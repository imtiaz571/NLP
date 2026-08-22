"""
NPC Talk — Dataset Loader
Downloads the Cornell Movie-Dialogs Corpus from Kaggle, cleans it,
and extracts per-character dialogue lines for NPC persona seeding.

Usage:
    python data/load_dataset.py
"""

import json
import os
import re
import sys
from pathlib import Path
from collections import defaultdict

# ── Paths ──────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

# Characters we want to map to our 3 NPC archetypes.
# Each entry: (target NPC id, list of candidate movie-character names)
# We pick the first candidate that has ≥20 lines in the corpus.
NPC_MAPPING = {
    "tabitha": {
        "archetype": "wise elder",
        "candidates": ["GANDALF", "DUMBLEDORE", "MORPHEUS", "ODIN", "ELDER"],
        "fallback_keywords": ["wisdom", "destiny", "ancient", "prophecy", "journey"],
    },
    "sam": {
        "archetype": "blunt warrior",
        "candidates": ["GIMLI", "DRAX", "CONAN", "MAXIMUS", "WOLVERINE"],
        "fallback_keywords": ["fight", "sword", "battle", "strength", "war"],
    },
    "ash": {
        "archetype": "witty rogue",
        "candidates": ["HAN", "JACK SPARROW", "LOKI", "FLYNN", "ROCKET"],
        "fallback_keywords": ["steal", "trick", "shadow", "deal", "coin"],
    },
}

# ── Fallback dialogue (used when Kaggle download fails) ────────────
FALLBACK_LINES = {
    "tabitha": [
        "The path ahead is shrouded, traveler. Not all who seek answers are prepared for the truth.",
        "I have watched empires crumble and forests reclaim stone. What is your hurry?",
        "Listen to the wind. It carries the memories of those who walked before you.",
        "You remind me of someone I knew long ago. They too were full of questions.",
        "The stars have shifted. Something stirs in the old places.",
        "Patience is not the absence of action — it is the mastery of timing.",
        "Every choice you make ripples outward, like a stone cast into still water.",
        "Do not mistake my silence for ignorance. I have seen more than you can imagine.",
    ],
    "sam": [
        "You want something forged? Then bring me proper materials, not this rubbish.",
        "I've seen soldiers twice your size crumble at the first sign of trouble.",
        "Talk is cheap. Steel isn't. What do you need?",
        "This blade has taken more lives than you've had hot meals. Treat it with respect.",
        "I didn't survive three wars by being polite. State your business.",
        "You want my help? Fine. But you'd better pull your own weight.",
        "The forge doesn't care about your feelings. Neither do I.",
        "Every scar tells a story. Most of mine say 'don't be stupid.'",
    ],
    "ash": [
        "You didn't see me, and I was never here. We clear on that?",
        "Everyone's got secrets. I just happen to collect them professionally.",
        "Trust? That's a luxury. I deal in information and coin.",
        "I could tell you, but then you'd owe me a favor. And my favors aren't cheap.",
        "The shadows have ears, friend. Best watch what you say out loud.",
        "I know every alley, every locked door, and every guard's schedule. Interested?",
        "Funny thing about honesty — it's the best disguise nobody expects.",
        "Let's just say I have a flexible relationship with the concept of ownership.",
    ],
}


def _parse_movie_lines(dataset_path: str) -> dict[str, list[str]]:
    """
    Parse movie_lines.txt or movie_lines.tsv and return
    {CHARACTER_NAME: [line, line, ...]}.

    Supports two formats:
    - Original (.txt): fields separated by ` +++$+++ `
    - Kaggle TSV (.tsv): tab-separated fields
    Fields: lineID, characterID, movieID, character name, text
    """
    lines_file = None
    for name in ("movie_lines.tsv", "movie_lines.txt"):
        candidate = os.path.join(dataset_path, name)
        if os.path.exists(candidate):
            lines_file = candidate
            break

    # Also search subdirectories (kagglehub sometimes nests)
    if lines_file is None:
        for root, _dirs, files in os.walk(dataset_path):
            for f in files:
                if f in ("movie_lines.tsv", "movie_lines.txt"):
                    lines_file = os.path.join(root, f)
                    break
            if lines_file:
                break

    if lines_file is None:
        print(f"  [!] movie_lines.txt/tsv not found under {dataset_path}")
        return {}

    # Auto-detect separator based on file extension and content
    is_tsv = lines_file.endswith(".tsv")
    print(f"  [i] Parsing {lines_file} ({'TSV' if is_tsv else 'TXT'} format)")

    char_lines: dict[str, list[str]] = defaultdict(list)

    with open(lines_file, "r", encoding="utf-8", errors="replace") as fh:
        for raw in fh:
            if is_tsv:
                parts = raw.strip().split("\t")
            else:
                parts = raw.strip().split(" +++$+++ ")

            if len(parts) < 5:
                continue
            char_name = parts[3].strip().upper()
            text = parts[4].strip()
            # Basic cleaning
            if not text or len(text) < 10:
                continue
            # Remove stage directions like (sighs), [laughing]
            text = re.sub(r"[\(\[][^)\]]*[\)\]]", "", text).strip()
            if not text or len(text) < 10:
                continue
            char_lines[char_name].append(text)

    return dict(char_lines)


def _select_lines_for_npc(
    npc_id: str,
    mapping: dict,
    char_lines: dict[str, list[str]],
    max_lines: int = 8,
) -> list[str]:
    """
    Try to find a matching character for the NPC archetype.
    Fallback: scan all characters for keyword-matching lines.
    """
    # Strategy 1: exact character name match
    for candidate in mapping["candidates"]:
        if candidate in char_lines and len(char_lines[candidate]) >= 20:
            # Pick the most interesting lines (longer = more personality)
            selected = sorted(char_lines[candidate], key=len, reverse=True)
            # Take a mix of lengths
            result = selected[:max_lines // 2]
            mid = selected[len(selected) // 3 : len(selected) // 3 + max_lines // 2]
            result.extend(mid)
            return result[:max_lines]

    # Strategy 2: keyword scan across all characters
    print(f"  [i] No exact match for {npc_id}, falling back to keyword scan")
    keywords = mapping["fallback_keywords"]
    scored_lines: list[tuple[int, str]] = []
    for lines in char_lines.values():
        for line in lines:
            score = sum(1 for kw in keywords if kw.lower() in line.lower())
            if score > 0 and 20 < len(line) < 200:
                scored_lines.append((score, line))
    scored_lines.sort(key=lambda x: x[0], reverse=True)
    return [line for _, line in scored_lines[:max_lines]]


def _build_seed_memories(char_lines: dict[str, list[str]]) -> list[dict]:
    """
    Create seed long-term memory entries from dialogue pairs.
    These give the vector store something to demo on day one.
    """
    memories = []
    npc_memory_templates = {
        "tabitha": [
            "A traveler once asked about the ancient prophecy. I told them the truth would find them when they were ready.",
            "I remember warning a young adventurer about the dangers of the Dark Forest. They didn't listen.",
            "A merchant from the eastern lands brought news of strange lights in the sky. The old magic stirs.",
            "Last winter, a group of soldiers sought shelter in the village. I shared stories of the old wars.",
            "The player once asked me about the Lost Amulet. I hinted it lies beneath the old ruins.",
        ],
        "sam": [
            "I forged a special blade for a warrior who proved their worth in the arena.",
            "A fool tried to haggle the price of dragonscale armor. I threw them out of the shop.",
            "The player helped me gather rare ore from the abandoned mine. They earned my respect.",
            "I remember repairing the village gate after the goblin raid. Nobody else lifted a finger.",
            "Someone once asked me to teach them swordplay. I told them to survive a week first.",
        ],
        "ash": [
            "I once sold information about a noble's secret tunnels to a clever adventurer.",
            "The player caught me snooping around the tavern. I convinced them it was for a good cause.",
            "A rival thief tried to muscle in on my territory. They won't make that mistake again.",
            "I remember overhearing guards discussing a hidden treasure beneath the castle.",
            "The player asked me to find someone. I found them — for a price, of course.",
        ],
    }
    for npc_id, entries in npc_memory_templates.items():
        for entry in entries:
            memories.append({
                "text": entry,
                "npc_id": npc_id,
                "player_id": "seed",
                "timestamp": "2024-01-01T00:00:00",
            })
    return memories


def download_and_process():
    """Main entry point: download dataset, process, save outputs."""
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    # ── Try Kaggle download ────────────────────────────────────────
    char_lines: dict[str, list[str]] = {}
    try:
        import kagglehub
        print("[*] Downloading Cornell Movie-Dialogs Corpus via kagglehub…")
        dataset_path = kagglehub.dataset_download("Cornell-University/movie-dialog-corpus")
        print(f"  [✓] Downloaded to: {dataset_path}")
        char_lines = _parse_movie_lines(dataset_path)
        print(f"  [✓] Parsed {sum(len(v) for v in char_lines.values())} lines from {len(char_lines)} characters")
    except Exception as exc:
        print(f"  [!] Kaggle download failed: {exc}")
        print("  [i] Using fallback dialogue lines instead")

    # ── Extract per-NPC lines ──────────────────────────────────────
    for npc_id, mapping in NPC_MAPPING.items():
        if char_lines:
            lines = _select_lines_for_npc(npc_id, mapping, char_lines)
            if len(lines) < 4:
                print(f"  [i] Too few lines for {npc_id}, supplementing with fallback")
                lines.extend(FALLBACK_LINES[npc_id][: 8 - len(lines)])
        else:
            lines = FALLBACK_LINES[npc_id]

        output = {"character": npc_id, "archetype": mapping["archetype"], "lines": lines}
        out_path = PROCESSED_DIR / f"{npc_id}_lines.json"
        with open(out_path, "w", encoding="utf-8") as fh:
            json.dump(output, fh, indent=2, ensure_ascii=False)
        print(f"  [✓] Wrote {len(lines)} lines → {out_path}")

    # ── Seed memories ──────────────────────────────────────────────
    memories = _build_seed_memories(char_lines)
    mem_path = PROCESSED_DIR / "seed_memories.json"
    with open(mem_path, "w", encoding="utf-8") as fh:
        json.dump(memories, fh, indent=2, ensure_ascii=False)
    print(f"  [✓] Wrote {len(memories)} seed memories → {mem_path}")

    print("\n[✓] Dataset processing complete!")


if __name__ == "__main__":
    download_and_process()
