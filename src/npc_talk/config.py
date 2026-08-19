"""NPC Talk — Central Configuration."""
import os
from pathlib import Path

# Paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
PERSONAS_DIR = PROJECT_ROOT / "src" / "npc_talk" / "personas"
DATA_PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
MEMORY_STORE_DIR = PROJECT_ROOT / "src" / "npc_talk" / "memory" / "store"
SEED_MEMORIES_FILE = DATA_PROCESSED_DIR / "seed_memories.json"
TRAINING_FILE = PROJECT_ROOT / "data" / "npc_dialogue_training.json"
FRONTEND_DIR = PROJECT_ROOT / "frontend"

MODELS_DIR = PROJECT_ROOT / "models"
LOCAL_GENERATIVE_LLM = MODELS_DIR / "qwen2.5-3b-instruct"
LOCAL_EMBEDDING_MODEL = MODELS_DIR / "all-MiniLM-L6-v2"
LOCAL_EMOTION_MODEL = MODELS_DIR / "emotion-distilroberta"

# Memory settings
SHORT_TERM_BUFFER_SIZE = 10
LONG_TERM_TOP_K = 3
EMBEDDING_MODEL = str(LOCAL_EMBEDDING_MODEL) if LOCAL_EMBEDDING_MODEL.exists() else "all-MiniLM-L6-v2"
EMBEDDING_DIM = 384

# NLP / ML settings
INTENT_CLASSIFIER = "auto"
EMOTION_MODEL = "transformer"
EMOTION_MODEL_PATH = str(LOCAL_EMOTION_MODEL) if LOCAL_EMOTION_MODEL.exists() else "j-hartmann/emotion-english-distilroberta-base"
GENERATIVE_LLM_MODEL = str(LOCAL_GENERATIVE_LLM) if LOCAL_GENERATIVE_LLM.exists() else os.getenv("GENERATIVE_LLM_MODEL", "Qwen/Qwen2.5-3B-Instruct")
ENABLE_GENERATIVE_LLM = os.getenv("ENABLE_GENERATIVE_LLM", "true").lower() in ("true", "1", "yes")
GENERATIVE_MAX_NEW_TOKENS = int(os.getenv("GENERATIVE_MAX_NEW_TOKENS", "150"))
GENERATIVE_TEMPERATURE = float(os.getenv("GENERATIVE_TEMPERATURE", "0.7"))
GENERATIVE_TOP_P = float(os.getenv("GENERATIVE_TOP_P", "0.9"))

# Game-state defaults
DEFAULT_TIME_OF_DAY = "day"
DEFAULT_LOCATION = "village_square"
DEFAULT_REPUTATION = 0
