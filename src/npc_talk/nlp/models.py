"""NPC Talk — Intent and Emotion NLP Classifiers."""
import json
import logging
import re
from pathlib import Path
from typing import Optional
import numpy as np
from npc_talk import config

logger = logging.getLogger(__name__)

_intent_models: dict[str, tuple] = {}
_transformer_pipeline = None

# Emotion label mappings
TRANSFORMER_TO_NPC = {
    "anger": "angry", "disgust": "angry", "fear": "suspicious",
    "joy": "happy", "neutral": "neutral", "sadness": "sad", "surprise": "surprised"
}
THINKING_KEYWORDS = {
    "ponder", "consider", "ancient", "chronicle", "chronicles", "records",
    "formula", "recipe", "leylines", "leyline", "cataclysm", "archives", "study"
}


INTENT_STOPWORDS = {
    "a", "an", "the", "and", "or", "but", "if", "in", "on", "at", "to", "for",
    "with", "about", "against", "between", "into", "through", "during", "before",
    "after", "above", "below", "from", "up", "down", "out", "off", "over",
    "under", "again", "further", "then", "once", "here", "there", "when", "where",
    "why", "how", "all", "any", "both", "each", "few", "more", "most", "other",
    "some", "such", "no", "nor", "not", "only", "own", "same", "so", "than",
    "too", "very", "can", "will", "just", "don", "should", "now", "i", "me",
    "my", "myself", "we", "our", "ours", "ourselves", "you", "your", "yours",
    "yourself", "yourselves", "he", "him", "his", "himself", "she", "her",
    "hers", "herself", "it", "its", "itself", "they", "them", "their", "theirs",
    "themselves", "what", "which", "who", "whom", "this", "that", "these",
    "those", "am", "is", "are", "was", "were", "be", "been", "being", "have",
    "has", "had", "having", "do", "does", "did", "doing", "would", "could",
    "tell", "think", "know", "say", "talk", "like", "look", "want", "give",
    "make", "thing", "things"
}


def _load_training_data() -> dict:
    if not config.TRAINING_FILE.exists():
        return {}
    try:
        with open(config.TRAINING_FILE, "r", encoding="utf-8") as f:
            return json.load(f).get("npcs", {})
    except Exception as e:
        logger.warning("Could not load training file: %s", e)
        return {}


def _build_intent_models():
    global _intent_models
    if _intent_models:
        return
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.linear_model import LogisticRegression
        from sklearn.pipeline import Pipeline
    except ImportError:
        logger.warning("scikit-learn not installed")
        return

    npcs = _load_training_data()
    prefixes = ["", "can you tell me about", "what about", "do you have", "tell me about", "i need", "where is", "how do i"]

    for npc_id, data in npcs.items():
        X, y, meta_map = [], [], {}
        for intent in data.get("intents", []):
            iid = intent.get("id")
            triggers = intent.get("triggers", [])
            if not iid or not triggers:
                continue
            meta_map[iid] = {
                "id": iid,
                "triggers": [tr.lower().strip() for tr in triggers if tr.strip()],
                "responses": intent.get("responses", []),
                "action": intent.get("action", "none"),
                "action_params": intent.get("action_params", {}),
                "emotion": intent.get("emotion", "neutral"),
            }
            for trig in triggers:
                t = trig.strip().lower()
                if not t:
                    continue
                for p in prefixes:
                    phrase = f"{p} {t}".strip()
                    X.append(phrase)
                    y.append(iid)

        if len(set(y)) >= 2:
            clf = Pipeline([
                ("tfidf", TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True, strip_accents="unicode", stop_words="english")),
                ("lr", LogisticRegression(C=10.0, max_iter=500, random_state=42))
            ])
            clf.fit(X, y)
            _intent_models[npc_id] = (clf, meta_map)


def predict_intent(text: str, npc_id: str, confidence_threshold: float = 0.35) -> Optional[dict]:
    _build_intent_models()
    if npc_id not in _intent_models or not text.strip():
        return None

    pipeline, meta_map = _intent_models[npc_id]
    try:
        lower = text.strip().lower()
        # Verify query matches at least one domain TF-IDF vocabulary term
        tfidf = pipeline.named_steps.get("tfidf")
        if tfidf is not None:
            vec = tfidf.transform([lower])
            if vec.nnz == 0:
                return None

        proba = pipeline.predict_proba([lower])[0]
        best_idx = int(np.argmax(proba))
        best_label = pipeline.classes_[best_idx]
        conf = float(proba[best_idx])
        if conf >= confidence_threshold and best_label in meta_map:
            intent_meta = meta_map[best_label]
            query_content_words = {
                w for w in re.findall(r"\b[a-z]{3,}\b", lower)
                if w not in INTENT_STOPWORDS
            }
            triggers = intent_meta.get("triggers", [])
            has_trigger_match = False
            for trig in triggers:
                t_clean = trig.strip().lower()
                if not t_clean:
                    continue
                # Full phrase match with word boundaries
                if " " in t_clean and re.search(r"\b" + re.escape(t_clean) + r"\b", lower):
                    has_trigger_match = True
                    break
                # Non-stopword token overlap with word boundaries/inflections
                trig_tokens = {
                    w for w in re.findall(r"\b[a-z]{3,}\b", t_clean)
                    if w not in INTENT_STOPWORDS
                }
                if trig_tokens and (query_content_words & trig_tokens or any(re.search(r"\b" + re.escape(tt) + r"(s|es|ed|ing)?\b", lower) for tt in trig_tokens)):
                    has_trigger_match = True
                    break

            if has_trigger_match:
                return {**intent_meta, "confidence": conf}
    except Exception as e:
        logger.debug("predict_intent error: %s", e)
    return None


def _get_transformer_emotion():
    global _transformer_pipeline
    if _transformer_pipeline is None:
        try:
            from transformers import pipeline
            model_ref = getattr(config, "EMOTION_MODEL_PATH", "j-hartmann/emotion-english-distilroberta-base")
            _transformer_pipeline = pipeline(
                "text-classification",
                model=model_ref,
                top_k=None,
                truncation=True,
                max_length=256
            )
        except Exception as e:
            logger.warning("Transformer emotion model unavailable: %s", e)
            _transformer_pipeline = False
    return _transformer_pipeline if _transformer_pipeline is not False else None


def predict_emotion(text: str, confidence_threshold: float = 0.25) -> Optional[str]:
    lower = text.lower().strip()
    # Direct thinking keyword check
    if any(k in lower for k in THINKING_KEYWORDS):
        return "thinking"

    model = _get_transformer_emotion()
    if model:
        try:
            res = model(text)
            if res and isinstance(res[0], list):
                res = res[0]
            if res:
                best = max(res, key=lambda x: x["score"])
                if best["score"] >= confidence_threshold:
                    return TRANSFORMER_TO_NPC.get(best["label"].lower(), "neutral")
        except Exception as e:
            logger.debug("Transformer emotion prediction failed: %s", e)

    # Heuristic fallback using word boundaries
    has_word = lambda word_list: any(re.search(r"\b" + re.escape(w) + r"\b", lower) for w in word_list)

    if has_word(["fool", "hate", "kill", "die", "rage", "angry", "insult", "dare you"]):
        return "angry"
    if has_word(["glad", "welcome", "happy", "joy", "thanks", "great", "yay", "wonderful"]):
        return "happy"
    if has_word(["grief", "loss", "sad", "mourn", "died", "tears", "tragedy"]):
        return "sad"
    if has_word(["secret", "whisper", "rumor", "shadow", "suspicious", "trust"]):
        return "suspicious"
    if any(k in lower for k in ["what?!", "wait!", "unbelievable", "shocking", "monster", "whoa"]):
        return "surprised"
    return "neutral"


def warmup():
    """Warm up intent and emotion models."""
    _build_intent_models()
    _get_transformer_emotion()
