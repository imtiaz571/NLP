"""
NPC Talk — Long-Term Memory
Vector store using sentence-transformers + FAISS for semantic retrieval
of past interactions and seeded knowledge.
"""

import json
import os
import logging
import threading
from datetime import datetime
from pathlib import Path

import numpy as np

from npc_talk import config

logger = logging.getLogger(__name__)

# Lazy-loaded globals
_model = None
_faiss = None
_EMBED_CACHE: dict = {}


def _get_model():
    """Lazy-load the sentence-transformer model from offline local cache."""
    global _model
    if _model is None:
        os.environ.setdefault("HF_HUB_OFFLINE", "1")
        os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
        from sentence_transformers import SentenceTransformer
        logger.info("Loading embedding model: %s", config.EMBEDDING_MODEL)
        try:
            _model = SentenceTransformer(config.EMBEDDING_MODEL, local_files_only=True)
        except Exception:
            _model = SentenceTransformer(config.EMBEDDING_MODEL)
    return _model


def _get_faiss():
    """Lazy-import faiss."""
    global _faiss
    if _faiss is None:
        import faiss as _f
        _faiss = _f
    return _faiss


class LongTermMemory:
    """
    FAISS-backed vector store for long-term NPC memory.
    Stores text entries with metadata and retrieves by semantic similarity.
    """

    def __init__(self, store_dir: str = config.MEMORY_STORE_DIR):
        self.store_dir = Path(store_dir)
        self.store_dir.mkdir(parents=True, exist_ok=True)
        self._lock = threading.RLock()

        self.index_path = self.store_dir / "faiss.index"
        self.meta_path = self.store_dir / "metadata.json"

        # Metadata: list of dicts parallel to FAISS index rows
        self.entries: list[dict] = []
        self.index = None

        self._load_or_create()

    def _load_or_create(self):
        """Load existing index from disk, or create a new empty one."""
        faiss = _get_faiss()

        if self.index_path.exists() and self.meta_path.exists():
            try:
                self.index = faiss.read_index(str(self.index_path))
                with open(self.meta_path, "r", encoding="utf-8") as fh:
                    self.entries = json.load(fh)
                if not isinstance(self.entries, list):
                    raise ValueError("Memory metadata must contain a JSON list")
                if self.index.d != config.EMBEDDING_DIM:
                    raise ValueError(
                        f"Index dimension {self.index.d} does not match configured "
                        f"dimension {config.EMBEDDING_DIM}"
                    )
                if self.index.ntotal != len(self.entries):
                    raise ValueError(
                        f"Index contains {self.index.ntotal} vectors but metadata "
                        f"contains {len(self.entries)} entries"
                    )
                logger.info(
                    "Loaded long-term memory: %d entries", len(self.entries)
                )
                return
            except Exception as exc:
                logger.warning("Failed to load index, creating new: %s", exc)

        # Create fresh index (Inner Product on normalized vectors = cosine sim)
        self.index = faiss.IndexFlatIP(config.EMBEDDING_DIM)
        self.entries = []

    def _save(self):
        """Persist index and metadata to disk."""
        faiss = _get_faiss()
        faiss.write_index(self.index, str(self.index_path))
        with open(self.meta_path, "w", encoding="utf-8") as fh:
            json.dump(self.entries, fh, indent=2, ensure_ascii=False)

    def _embed(self, texts: list[str]) -> np.ndarray:
        """Encode texts into normalized float32 embeddings with in-memory caching."""
        model = _get_model()
        uncached = [t for t in texts if t not in _EMBED_CACHE]
        if uncached:
            try:
                embeddings = model.encode(uncached, normalize_embeddings=True, show_progress_bar=False)
            except TypeError:
                embeddings = model.encode(uncached, normalize_embeddings=True)
            for t, emb in zip(uncached, embeddings):
                _EMBED_CACHE[t] = np.array(emb, dtype="float32")
        return np.array([_EMBED_CACHE[t] for t in texts], dtype="float32")

    def add_memory(
        self,
        text: str,
        npc_id: str,
        player_id: str = "unknown",
        timestamp: str | None = None,
    ) -> None:
        """Add a single memory entry."""
        if timestamp is None:
            timestamp = datetime.now().isoformat()

        embedding = self._embed([text])
        with self._lock:
            self.index.add(embedding)
            self.entries.append({
                "text": text,
                "npc_id": npc_id,
                "player_id": player_id,
                "timestamp": timestamp,
            })
            self._save()

    def retrieve(
        self,
        query: str,
        npc_id: str,
        top_k: int = config.LONG_TERM_TOP_K,
        player_id: str | None = None,
    ) -> list[str]:
        """
        Retrieve the top-k most relevant memories for a given NPC.
        Filters results to the specified NPC and, when supplied, the current
        player. Seed memories are shared world knowledge and remain visible to
        every player.
        """
        if top_k <= 0:
            return []

        with self._lock:
            if self.index is None or self.index.ntotal == 0:
                return []

        query_emb = self._embed([query])
        with self._lock:
            if self.index is None or self.index.ntotal == 0:
                return []

            # Search the full index because a fixed oversampling factor can miss
            # a player's memories when the store contains many other players.
            _, indices = self.index.search(query_emb, self.index.ntotal)

            results = []
            for idx in indices[0]:
                if idx < 0 or idx >= len(self.entries):
                    continue
                entry = self.entries[idx]
                if entry.get("npc_id") != npc_id:
                    continue
                entry_player = entry.get("player_id")
                if player_id is not None and entry_player not in (player_id, "seed"):
                    continue
                results.append(entry["text"])
                if len(results) >= top_k:
                    break

        return results

    def seed_from_file(self, path: str | None = None) -> int:
        """
        Load seed memories from a JSON file.
        Returns the number of entries added.
        """
        if path is None:
            path = config.SEED_MEMORIES_FILE

        if not os.path.exists(path):
            logger.info("No seed file found at %s, skipping", path)
            return 0

        # Do not duplicate seed entries in an existing player-memory store.
        with self._lock:
            if any(entry.get("player_id") == "seed" for entry in self.entries):
                logger.info("Memory already contains seed entries, skipping")
                return 0

        with open(path, "r", encoding="utf-8") as fh:
            seeds = json.load(fh)

        if not seeds:
            return 0

        texts = [s["text"] for s in seeds]
        embeddings = self._embed(texts)
        with self._lock:
            self.index.add(embeddings)
            self.entries.extend(seeds)
            self._save()
        logger.info("Seeded long-term memory with %d entries", len(seeds))
        return len(seeds)

    def format_for_prompt(self, memories: list[str]) -> str:
        """Format retrieved memories as a prompt section."""
        if not memories:
            return ""

        lines = ["## Relevant Memories from Past Interactions"]
        for i, mem in enumerate(memories, 1):
            lines.append(f"{i}. {mem}")
        lines.append("")
        lines.append(
            "Use these memories naturally in conversation when relevant. "
            "Reference past events to show continuity, but don't force it."
        )
        return "\n".join(lines)
