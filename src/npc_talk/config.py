"""
NPC Talk — Central Configuration
All tunable parameters in one place.
"""

import os
from pathlib import Path

# HuggingFace/Transformers online access allowed (will download models on first run if not cached)
# To force offline mode, set HF_HUB_OFFLINE=1 and TRANSFORMERS_OFFLINE=1 in environment

# src/npc_talk/config.py → src/npc_talk → src → project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

# ── Memory ─────────────────────────────────────────────────────────
SHORT_TERM_BUFFER_SIZE = 10          # turns kept per (npc, player)
LONG_TERM_TOP_K = 3                  # memories retrieved per query
EMBEDDING_MODEL = "all-MiniLM-L6-v2" # local sentence-transformers model
EMBEDDING_DIM = 384                  # output dim for MiniLM-L6-v2

# Intent classifier: "auto", "naive_bayes", "logistic_regression",
# "random_forest", "svc", "knn", "decision_tree", "xgboost", "voting", or
# "adaboost". Auto cross-validates the probability-stable NB/LR/SVC/voting
# candidates; every model remains selectable explicitly and benchmarked.
# LinearSVC scored highest (97.02%) in benchmarks — pinned for consistency.
INTENT_CLASSIFIER = "svc"

# Emotion classifier backend:
# "transformer" — use j-hartmann/emotion-english-distilroberta-base (pre-trained,
#                  ~300 MB download on first use, 93–96% on external benchmarks)
# "classical"   — use TF-IDF + LinearSVC (fast, CPU-only, ~65–72% on external benchmarks)
EMOTION_MODEL = "transformer"

# ── Paths ──────────────────────────────────────────────────────────
PERSONAS_DIR = PROJECT_ROOT / "src" / "npc_talk" / "personas"
DATA_PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
MEMORY_STORE_DIR = PROJECT_ROOT / "src" / "npc_talk" / "memory" / "store"
SEED_MEMORIES_FILE = DATA_PROCESSED_DIR / "seed_memories.json"
FRONTEND_DIR = PROJECT_ROOT / "frontend"

# ── Game-state defaults ────────────────────────────────────────────
DEFAULT_TIME_OF_DAY = "day"
DEFAULT_LOCATION = "village_square"
DEFAULT_REPUTATION = 0               # neutral
