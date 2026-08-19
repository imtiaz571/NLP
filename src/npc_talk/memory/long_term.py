"""NPC Talk — Long-Term Memory (FAISS Vector Store)."""
import json
import logging
import os
import threading
from datetime import datetime
from pathlib import Path
import numpy as np
from npc_talk import config

logger = logging.getLogger(__name__)

_model = None
_faiss = None
_EMBED_CACHE: dict[str, np.ndarray] = {}


def _get_model():
    """Lazy-load sentence-transformer embedding model."""
    global _model
    if _model is None:
        import torch
        torch.set_num_threads(1)
        from sentence_transformers import SentenceTransformer
        try:
            _model = SentenceTransformer(config.EMBEDDING_MODEL, local_files_only=True, device="cpu")
        except Exception:
            _model = SentenceTransformer(config.EMBEDDING_MODEL, device="cpu")
    return _model


def _get_faiss():
    """Lazy-import faiss."""
    global _faiss
    if _faiss is None:
        import faiss
        _faiss = faiss
    return _faiss


class LongTermMemory:
    """FAISS-backed vector store for semantic memory retrieval."""

    def __init__(self, store_dir: str | Path = config.MEMORY_STORE_DIR):
        self.store_dir = Path(store_dir)
        self.store_dir.mkdir(parents=True, exist_ok=True)
        self.index_path = self.store_dir / "faiss.index"
        self.meta_path = self.store_dir / "metadata.json"
        self._lock = threading.RLock()
        self.entries: list[dict] = []
        self.index = None
        self._load_or_create()

    def _load_or_create(self):
        faiss = _get_faiss()
        if self.index_path.exists() and self.meta_path.exists():
            try:
                self.index = faiss.read_index(str(self.index_path))
                with open(self.meta_path, "r", encoding="utf-8") as f:
                    self.entries = json.load(f)
                if isinstance(self.entries, list) and self.index.ntotal == len(self.entries):
                    return
            except Exception as e:
                logger.warning("Failed to load existing memory index: %s", e)

        self.index = faiss.IndexFlatIP(config.EMBEDDING_DIM)
        self.entries = []

    def _save(self):
        faiss = _get_faiss()
        faiss.write_index(self.index, str(self.index_path))
        with open(self.meta_path, "w", encoding="utf-8") as f:
            json.dump(self.entries, f, indent=2, ensure_ascii=False)

    def _embed(self, texts: list[str]) -> np.ndarray:
        uncached = [t for t in texts if t not in _EMBED_CACHE]
        if uncached:
            model = _get_model()
            embeddings = model.encode(uncached, normalize_embeddings=True, show_progress_bar=False, convert_to_numpy=True)
            for t, emb in zip(uncached, embeddings):
                _EMBED_CACHE[t] = np.array(emb, dtype="float32")
        return np.array([_EMBED_CACHE[t] for t in texts], dtype="float32")

    def add_memory(self, text: str, npc_id: str, player_id: str = "unknown", timestamp: str | None = None) -> None:
        timestamp = timestamp or datetime.now().isoformat()
        emb = self._embed([text])
        with self._lock:
            self.index.add(emb)
            self.entries.append({"text": text, "npc_id": npc_id, "player_id": player_id, "timestamp": timestamp})
            self._save()

    def retrieve(self, query: str, npc_id: str, top_k: int = config.LONG_TERM_TOP_K, player_id: str | None = None) -> list[str]:
        if top_k <= 0 or not self.entries:
            return []
        query_emb = self._embed([query])
        with self._lock:
            if self.index is None or self.index.ntotal == 0:
                return []
            _, indices = self.index.search(query_emb, self.index.ntotal)
            results = []
            for idx in indices[0]:
                if 0 <= idx < len(self.entries):
                    e = self.entries[idx]
                    if e.get("npc_id") == npc_id and (player_id is None or e.get("player_id") in (player_id, "seed")):
                        results.append(e["text"])
                        if len(results) >= top_k:
                            break
            return results

    def seed_from_file(self, path: str | Path | None = None) -> int:
        path = Path(path or config.SEED_MEMORIES_FILE)
        if not path.exists():
            return 0
        with self._lock:
            if any(e.get("player_id") == "seed" for e in self.entries):
                return 0
            with open(path, "r", encoding="utf-8") as f:
                seeds = json.load(f)
            if not seeds:
                return 0
            embeddings = self._embed([s["text"] for s in seeds])
            self.index.add(embeddings)
            self.entries.extend(seeds)
            self._save()
            return len(seeds)

    def format_for_prompt(self, memories: list[str]) -> str:
        if not memories:
            return ""
        lines = ["## Relevant Memories from Past Interactions"]
        lines.extend(f"{i}. {m}" for i, m in enumerate(memories, 1))
        lines.append("Use these memories naturally when relevant to show conversational continuity.")
        return "\n".join(lines)
