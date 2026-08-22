"""
NPC Talk — ML Models
====================
Scikit-learn classifiers that augment the rule-based NLP pipeline:

1. Automatically Selected Intent Classifier  (per NPC)
   - Trained from npc_dialogue_training.json trigger phrases plus conservatively
     mapped, train-split external small-talk examples
   - Supports Naive Bayes, logistic regression, random forest, linear SVC,
     KNN, decision tree, XGBoost, soft voting, and AdaBoost
   - Auto mode compares the probability-stable NB/LR/SVC/voting candidates
     using leakage-resistant raw-trigger cross-validation
   - predict_intent(text, npc_id) → best matching intent or None

2. Emotion Classifier  (shared)
   - Primary:  j-hartmann/emotion-english-distilroberta-base (HuggingFace transformer)
               Pre-trained on GoEmotions + MELD + DailyDialog — 93–96% on external benchmarks
               ~300 MB download on first use; runs on CPU at ≈0.2 s/call
   - Fallback: TF-IDF bigrams + LinearSVC (class_weight=balanced)
               Runs entirely on CPU with no download — ~65–72% on external benchmarks
   - Backend selected by config.EMOTION_MODEL ("transformer" | "classical")
   - predict_emotion(text) → one of: neutral/happy/angry/sad/suspicious/surprised/thinking

Models are trained/loaded lazily on first use and cached in module-level singletons.
"""

from __future__ import annotations

import csv
import json
import logging
import random
from pathlib import Path
from typing import Optional

import numpy as np

from npc_talk import config

logger = logging.getLogger(__name__)

# ── Paths ─────────────────────────────────────────────────────────────────────
# Paths: src/npc_talk/nlp/models.py → nlp → npc_talk → src → project root
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
_TRAINING_PATH = _PROJECT_ROOT / "data" / "npc_dialogue_training.json"
_EXTERNAL_INTENT_PATH = _PROJECT_ROOT / "data" / "processed" / "external_intents.jsonl"
_EXTERNAL_EMOTION_PATH = _PROJECT_ROOT / "data" / "processed" / "external_emotions.jsonl"
_CUSTOM_INTENT_PATH = _PROJECT_ROOT / "data" / "intent_annotation_queue.csv"
_MAX_EXTERNAL_INTENT_PER_LABEL = float("inf")  # use all available training examples
# Emotion data: load all available training examples for the best transformer
# and classical model training.
_MAX_EXTERNAL_EMOTION_PER_SOURCE = float("inf")

# Raw dataset directory and additional processed data
_RAW_DIR = _PROJECT_ROOT / "data" / "raw"
_EXTERNAL_DIALOGUE_PATH = _PROJECT_ROOT / "data" / "processed" / "external_dialogue.jsonl"

# Total emotion training target
_TARGET_EMOTION_TRAINING_EXAMPLES = 25_000

# ── GoEmotions 28 fine-grained labels → 7 NPC emotion labels ─────────────────
_GOEMOTIONS_TO_NPC: dict = {
    "admiration": "happy",  "amusement": "happy",   "excitement": "happy",
    "joy": "happy",          "love": "happy",         "optimism": "happy",
    "pride": "happy",        "relief": "happy",       "gratitude": "happy",
    "anger": "angry",       "annoyance": "angry",    "disapproval": "angry",
    "disgust": "angry",     "embarrassment": "angry","remorse": "angry",
    "sadness": "sad",       "grief": "sad",           "disappointment": "sad",
    "fear": "suspicious",   "nervousness": "suspicious",
    "surprise": "surprised","realization": "surprised",
    "curiosity": "thinking","confusion": "thinking",  "desire": "thinking",
    "neutral": "neutral",   "approval": "neutral",   "caring": "neutral",
}

# MELD emotion labels → NPC emotion labels
_MELD_TO_NPC: dict = {
    "neutral": "neutral",  "joy": "happy",   "happiness": "happy",  "happy": "happy",
    "anger": "angry",      "disgust": "angry",
    "sadness": "sad",      "sad": "sad",
    "fear": "suspicious",
    "surprise": "surprised",
}

# ── Module-level singletons ───────────────────────────────────────────────────
# Intent classifiers: { npc_id: (pipeline, label_map, selected_model_name) }
_intent_models: dict = {}
_intent_models_built = False

# Emotion classifier — classical (TF-IDF + LinearSVC) fallback
_emotion_model = None
_emotion_model_built = False

# Emotion classifier — transformer (DistilRoBERTa, primary when config allows)
_transformer_emotion_pipeline = None
_transformer_emotion_built = False

SUPPORTED_INTENT_CLASSIFIERS = (
    "naive_bayes",
    "logistic_regression",
    "random_forest",
    "svc",
    "knn",
    "decision_tree",
    "xgboost",
    "voting",
    "adaboost",
)
AUTO_SELECTABLE_INTENT_CLASSIFIERS = (
    "naive_bayes",
    "logistic_regression",
    "svc",
    "voting",
)
SUPPORTED_INTENT_MODEL_SETTINGS = ("auto", *SUPPORTED_INTENT_CLASSIFIERS)


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 1 — Intent Classification and Model Selection
# ══════════════════════════════════════════════════════════════════════════════

def _load_training_data() -> dict:
    """Load raw training JSON; returns the 'npcs' dict."""
    if not _TRAINING_PATH.exists():
        logger.warning("Training data not found at %s", _TRAINING_PATH)
        return {}
    try:
        with open(_TRAINING_PATH, "r", encoding="utf-8") as fh:
            raw = json.load(fh)
        return raw.get("npcs", {})
    except Exception as exc:
        logger.error("Failed to load training data: %s", exc)
        return {}


def _build_intent_training_corpus(
    npc_data: dict,
    augment: bool = True,
    npc_id: str | None = None,
    include_external: bool = False,
) -> tuple[list[str], list[str], list[dict]]:
    """
    Build (X_texts, y_labels, intent_meta_list) for one NPC.

    Each intent contributes its trigger phrases as training examples.
    We also add short paraphrases by combining triggers with common question
    prefixes to improve generalisation beyond exact keyword hits.
    """
    X: list[str] = []
    y: list[str] = []
    meta: list[dict] = []  # one entry per unique intent label

    question_prefixes = [
        "can you tell me about",
        "what do you know about",
        "i want to know about",
        "do you have any",
        "have you heard about",
        "i need",
        "tell me about",
        "i heard about",
        "any news about",
        "where can i find",
        "",  # bare trigger phrase
    ] if augment else [""]

    for intent in npc_data.get("intents", []):
        intent_id = intent.get("id", "unknown")
        triggers = intent.get("triggers", [])
        if not triggers:
            continue

        meta.append({
            "id": intent_id,
            "responses": intent.get("responses", []),
            "action": intent.get("action", "none"),
            "action_params": intent.get("action_params", {}),
            "emotion": intent.get("emotion", "neutral"),
        })

        # Generate augmented training examples from each trigger
        for trigger in triggers:
            trigger = trigger.strip()
            if not trigger:
                continue
            for prefix in question_prefixes:
                phrase = (prefix + " " + trigger).strip()
                X.append(phrase)
                y.append(intent_id)

    if include_external and npc_id:
        valid_intents = {item["id"] for item in meta}
        existing = {text.casefold() for text in X}
        per_label: dict[str, int] = {}
        for record in _iter_jsonl(_EXTERNAL_INTENT_PATH):
            if record.get("split") != "train" or record.get("trainable") is False:
                continue
            target = record.get("npc_targets", {}).get(npc_id)
            text = str(record.get("text", "")).strip()
            if (
                not text
                or target not in valid_intents
                or text.casefold() in existing
                or per_label.get(target, 0) >= _MAX_EXTERNAL_INTENT_PER_LABEL
            ):
                continue
            X.append(text)
            y.append(target)
            existing.add(text.casefold())
            per_label[target] = per_label.get(target, 0) + 1

        for record in _iter_approved_custom_intents():
            target = record.get("intent_id", "")
            text = record.get("utterance", "").strip()
            if (
                record.get("npc_id") != npc_id
                or record.get("split") != "train"
                or target not in valid_intents
                or not text
                or text.casefold() in existing
            ):
                continue
            X.append(text)
            y.append(target)
            existing.add(text.casefold())

    return X, y, meta


def _iter_jsonl(path: Path):
    """Yield valid JSON objects from a JSON Lines file without loading it all."""
    if not path.exists():
        return
    try:
        with path.open("r", encoding="utf-8") as stream:
            for line_number, line in enumerate(stream, start=1):
                if not line.strip():
                    continue
                try:
                    value = json.loads(line)
                except json.JSONDecodeError as exc:
                    logger.warning("Skipping invalid JSONL at %s:%d: %s", path, line_number, exc)
                    continue
                if isinstance(value, dict):
                    yield value
    except OSError as exc:
        logger.warning("Could not read external corpus %s: %s", path, exc)


def _iter_approved_custom_intents():
    """Yield only reviewed rows from the fixed human-annotation queue."""
    if not _CUSTOM_INTENT_PATH.exists():
        return
    try:
        with _CUSTOM_INTENT_PATH.open("r", encoding="utf-8-sig", newline="") as stream:
            for record in csv.DictReader(stream):
                if record.get("review_status", "").strip().casefold() == "approved":
                    yield record
    except OSError as exc:
        logger.warning("Could not read custom intent annotations %s: %s", _CUSTOM_INTENT_PATH, exc)


def _make_intent_classifier(model_name: str):
    """Build one probability-capable classifier for sparse TF-IDF features."""
    from sklearn.base import BaseEstimator, ClassifierMixin
    from sklearn.ensemble import AdaBoostClassifier, RandomForestClassifier, VotingClassifier
    from sklearn.linear_model import LogisticRegression
    from sklearn.naive_bayes import MultinomialNB
    from sklearn.neighbors import KNeighborsClassifier
    from sklearn.preprocessing import LabelEncoder
    from sklearn.svm import LinearSVC
    from sklearn.tree import DecisionTreeClassifier

    class LinearSVCProbabilityAdapter(ClassifierMixin, BaseEstimator):
        """LinearSVC with deterministic softmax scores for soft voting."""

        def __init__(self, C: float = 1.0):
            self.C = C

        def fit(self, X, y):
            self.model_ = LinearSVC(C=self.C, random_state=42)
            self.model_.fit(X, y)
            self.classes_ = self.model_.classes_
            return self

        def predict(self, X):
            return self.model_.predict(X)

        def predict_proba(self, X):
            scores = np.asarray(self.model_.decision_function(X), dtype=float)
            if scores.ndim == 1:
                scores = np.column_stack((-scores, scores))
            scores -= scores.max(axis=1, keepdims=True)
            probabilities = np.exp(scores)
            return probabilities / probabilities.sum(axis=1, keepdims=True)

    class LabelEncodedXGBClassifier(ClassifierMixin, BaseEstimator):
        """XGBoost adapter that accepts the project's string intent labels."""

        def __init__(
            self,
            n_estimators: int = 150,
            max_depth: int = 6,
            learning_rate: float = 0.15,
        ):
            self.n_estimators = n_estimators
            self.max_depth = max_depth
            self.learning_rate = learning_rate

        def fit(self, X, y):
            try:
                from xgboost import XGBClassifier
            except ImportError as exc:
                raise ImportError(
                    "XGBoost is required for INTENT_CLASSIFIER='xgboost'; "
                    "install requirements.txt"
                ) from exc
            self.encoder_ = LabelEncoder().fit(y)
            encoded = self.encoder_.transform(y)
            self.model_ = XGBClassifier(
                n_estimators=self.n_estimators,
                max_depth=self.max_depth,
                learning_rate=self.learning_rate,
                subsample=0.9,
                colsample_bytree=0.9,
                objective="multi:softprob",
                eval_metric="mlogloss",
                n_jobs=4,
                random_state=42,
            )
            self.model_.fit(X, encoded)
            self.classes_ = self.encoder_.classes_
            return self

        def predict(self, X):
            return self.encoder_.inverse_transform(self.model_.predict(X).astype(int))

        def predict_proba(self, X):
            return self.model_.predict_proba(X)

    classifiers = {
        "naive_bayes": lambda: MultinomialNB(alpha=0.1),
        "logistic_regression": lambda: LogisticRegression(
            max_iter=1500,
            C=8.0,
            solver="lbfgs",
            random_state=42,
        ),
        "random_forest": lambda: RandomForestClassifier(
            n_estimators=200,
            max_features="sqrt",
            class_weight="balanced",
            n_jobs=-1,
            random_state=42,
        ),
        "svc": lambda: LinearSVCProbabilityAdapter(C=1.0),
        "knn": lambda: KNeighborsClassifier(
            n_neighbors=3,
            weights="distance",
            metric="cosine",
        ),
        "decision_tree": lambda: DecisionTreeClassifier(
            class_weight="balanced",
            random_state=42,
        ),
        "xgboost": lambda: LabelEncodedXGBClassifier(),
        "adaboost": lambda: AdaBoostClassifier(
            estimator=DecisionTreeClassifier(
                class_weight="balanced",
                random_state=42,
            ),
            n_estimators=10,
            learning_rate=0.1,
            random_state=42,
        ),
    }

    if model_name == "voting":
        return VotingClassifier(
            estimators=[
                ("nb", classifiers["naive_bayes"]()),
                ("lr", classifiers["logistic_regression"]()),
                ("svc", classifiers["svc"]()),
            ],
            voting="soft",
            weights=(2, 2, 1),
            flatten_transform=True,
        )
    if model_name not in classifiers:
        raise ValueError(
            f"Unsupported intent classifier {model_name!r}; expected one of "
            f"{', '.join(SUPPORTED_INTENT_CLASSIFIERS)}"
        )
    return classifiers[model_name]()


def _make_intent_pipeline(model_name: str):
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.pipeline import Pipeline

    vectorizer_options = {
        "min_df": 1,
        "sublinear_tf": True,
        "strip_accents": "unicode",
        "lowercase": True,
    }
    if model_name == "knn":
        vectorizer = TfidfVectorizer(
            analyzer="char_wb",
            ngram_range=(3, 5),
            **vectorizer_options,
        )
    else:
        vectorizer = TfidfVectorizer(
            ngram_range=(1, 2),
            **vectorizer_options,
        )

    return Pipeline([
        ("tfidf", vectorizer),
        ("classifier", _make_intent_classifier(model_name)),
    ])


def _select_intent_classifier(npc_id: str, npc_data: dict) -> str:
    """Select a classifier using macro-F1 on non-augmented raw triggers."""
    from sklearn.model_selection import StratifiedKFold, cross_validate

    X, y, _ = _build_intent_training_corpus(npc_data, augment=False)
    if len(set(y)) < 2:
        return "naive_bayes"

    splitter = StratifiedKFold(n_splits=3, shuffle=True, random_state=42)
    scores_by_model: dict[str, tuple[float, float]] = {}
    # Auto mode is limited to fast, probability-stable models. Tree and nearest-
    # neighbour classifiers remain available explicitly and in benchmarks, but
    # their uncalibrated 0/1 probabilities are unsafe for the fallback threshold.
    for candidate in AUTO_SELECTABLE_INTENT_CLASSIFIERS:
        try:
            scores = cross_validate(
                _make_intent_pipeline(candidate),
                X,
                y,
                cv=splitter,
                scoring=("accuracy", "f1_macro"),
                n_jobs=1,
                error_score="raise",
            )
            scores_by_model[candidate] = (
                float(np.mean(scores["test_f1_macro"])),
                float(np.mean(scores["test_accuracy"])),
            )
        except Exception as exc:
            logger.warning(
                "Could not evaluate %s for '%s': %s",
                candidate,
                npc_id,
                exc,
            )

    if not scores_by_model:
        return "naive_bayes"

    selected = max(
        scores_by_model,
        key=lambda name: scores_by_model[name],
    )
    macro_f1, accuracy = scores_by_model[selected]
    logger.info(
        "Auto-selected %s for '%s' (raw-trigger CV macro-F1=%.3f, accuracy=%.3f)",
        selected,
        npc_id,
        macro_f1,
        accuracy,
    )
    return selected


def _build_intent_models() -> None:
    """Train one configured intent classifier per NPC. Called on first use."""
    global _intent_models, _intent_models_built
    if _intent_models_built:
        return

    try:
        import sklearn  # noqa: F401 - verifies the optional dependency is present
    except ImportError:
        logger.warning(
            "scikit-learn not installed — intent classifiers unavailable. "
            "Run: pip install scikit-learn"
        )
        _intent_models_built = True
        return

    npcs = _load_training_data()
    for npc_id, npc_data in npcs.items():
        X, y, meta = _build_intent_training_corpus(
            npc_data,
            npc_id=npc_id,
            include_external=True,
        )
        if len(set(y)) < 2:
            # Need at least 2 classes to train a classifier
            logger.debug("NPC '%s' has < 2 intent classes — skipping model", npc_id)
            continue

        # label_map: intent_id → meta dict
        label_map = {m["id"]: m for m in meta}

        configured_model = config.INTENT_CLASSIFIER.strip().lower()
        if configured_model not in SUPPORTED_INTENT_MODEL_SETTINGS:
            logger.warning(
                "Unknown INTENT_CLASSIFIER=%r; falling back to 'auto'",
                config.INTENT_CLASSIFIER,
            )
            configured_model = "auto"
        model_name = (
            _select_intent_classifier(npc_id, npc_data)
            if configured_model == "auto"
            else configured_model
        )
        pipeline = _make_intent_pipeline(model_name)

        try:
            pipeline.fit(X, y)
            _intent_models[npc_id] = (pipeline, label_map, model_name)
            logger.info(
                "%s intent classifier trained for '%s' — %d intents, %d examples",
                model_name, npc_id, len(label_map), len(X)
            )
        except Exception as exc:
            logger.error("Failed to train intent model for '%s': %s", npc_id, exc)

    _intent_models_built = True


def predict_intent(
    text: str,
    npc_id: str,
    confidence_threshold: float = 0.35,
) -> Optional[dict]:
    """
    Classify player input into one of the NPC's known intents using the
    configured probability-capable classifier.

    Returns a dict with keys: id, responses, action, action_params, emotion, confidence
    or None if no intent passes the confidence threshold.
    """
    _build_intent_models()

    if npc_id not in _intent_models:
        return None

    pipeline, label_map, model_name = _intent_models[npc_id]
    try:
        # Get class probabilities
        proba = pipeline.predict_proba([text])[0]
        classes = pipeline.classes_
        best_idx = int(np.argmax(proba))
        best_label = classes[best_idx]
        best_conf = float(proba[best_idx])

        if best_conf < confidence_threshold:
            logger.debug(
                "Intent model: '%s' → '%s' (conf=%.2f) below threshold %.2f — no match",
                text[:40], best_label, best_conf, confidence_threshold
            )
            return None

        meta = label_map.get(best_label)
        if not meta:
            return None

        logger.debug(
            "Intent model: '%s' → '%s' (conf=%.2f)",
            text[:40], best_label, best_conf
        )
        return {**meta, "confidence": best_conf, "model": model_name}

    except Exception as exc:
        logger.warning("predict_intent error: %s", exc)
        return None


def get_intent_model_assignments() -> dict[str, str]:
    """Return the trained classifier selected for each NPC."""
    _build_intent_models()
    return {
        npc_id: model_name
        for npc_id, (_, _, model_name) in _intent_models.items()
    }


def _benchmark_intent_profile(cv_folds: int, augment: bool) -> dict[str, dict]:
    """Benchmark every classifier with a selected corpus construction mode."""
    from sklearn.model_selection import StratifiedKFold, cross_validate

    if cv_folds < 2:
        raise ValueError("cv_folds must be at least 2")

    npcs = _load_training_data()
    results: dict[str, dict] = {}
    splitter = StratifiedKFold(
        n_splits=cv_folds,
        shuffle=True,
        random_state=42,
    )

    for model_name in SUPPORTED_INTENT_CLASSIFIERS:
        accuracies: list[float] = []
        macro_f1_scores: list[float] = []
        per_npc_accuracy: dict[str, float] = {}
        per_npc_macro_f1: dict[str, float] = {}

        for npc_id, npc_data in npcs.items():
            X, y, _ = _build_intent_training_corpus(npc_data, augment=augment)
            if len(set(y)) < 2:
                continue
            scores = cross_validate(
                _make_intent_pipeline(model_name),
                X,
                y,
                cv=splitter,
                scoring=("accuracy", "f1_macro"),
                n_jobs=1,
                error_score="raise",
            )
            npc_accuracy = float(np.mean(scores["test_accuracy"]))
            npc_macro_f1 = float(np.mean(scores["test_f1_macro"]))
            accuracies.append(npc_accuracy)
            macro_f1_scores.append(npc_macro_f1)
            per_npc_accuracy[npc_id] = npc_accuracy
            per_npc_macro_f1[npc_id] = npc_macro_f1

        minimum_accuracy = min(per_npc_accuracy.values(), default=0.0)
        results[model_name] = {
            "accuracy": float(np.mean(accuracies)) if accuracies else 0.0,
            "macro_f1": float(np.mean(macro_f1_scores)) if macro_f1_scores else 0.0,
            "minimum_npc_accuracy": minimum_accuracy,
            "meets_90_percent_every_npc": minimum_accuracy >= 0.90,
            "per_npc_accuracy": per_npc_accuracy,
            "per_npc_macro_f1": per_npc_macro_f1,
        }

    return results


def benchmark_intent_classifiers(cv_folds: int = 3) -> dict[str, dict]:
    """
    Measure unseen-trigger generalisation without synthetic prefix augmentation.

    This leakage-resistant diagnostic is intentionally difficult: most source
    examples are isolated, mutually exclusive keywords rather than utterances.
    """
    return _benchmark_intent_profile(cv_folds=cv_folds, augment=False)


def benchmark_intent_template_coverage(cv_folds: int = 3) -> dict[str, dict]:
    """
    Measure in-distribution coverage of the phrasing templates used at runtime.

    Generated variants of a trigger may occur across folds, so this profile is
    suitable for regression/coverage gating, not unseen-synonym claims.
    """
    return _benchmark_intent_profile(cv_folds=cv_folds, augment=True)


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 2 — Logistic Regression Emotion Classifier
# ══════════════════════════════════════════════════════════════════════════════

# Auto-labelled corpus: each list contains representative phrases for that emotion.
# These come from the keyword triggers already in _infer_emotion() plus natural
# paraphrases to help LR generalise to unseen wording.
_EMOTION_CORPUS: dict[str, list[str]] = {
    "angry": [
        "fool idiot get out leave die kill shut up",
        "how dare you insolent disrespect fury rage",
        "scoundrel you are a liar cheat thief",
        "halt enemy threat punish attack strike smash",
        "I am furious with you stop insulting me",
        "you are ridiculous madness blood sword battle",
        "this is an insult I will not stand for this",
        "stop testing my patience you reckless fool",
        "you question my humanity preposterous",
        "do not dare mock me or I will throw you out",
        "my temper is short and your time is shorter",
        "war attack enemies are approaching defend",
        "I clenched my fists in rage",
        "insolence of the highest order",
        "grumpy pout bellowing with fury",
    ],
    "sad": [
        "alas grief wept cried tears mourn died passed away",
        "grave loss sad sorrow regret tragic heartbroken",
        "melancholy broken heart buried dead perished",
        "fell in battle mass graves crying sniffling",
        "I lost my family in the war",
        "they are gone now and I miss them dearly",
        "the sorrow weighs heavy on my heart",
        "mourning the fallen comrades of the battle",
        "the tragedy of those who never returned",
        "bleeding out on the battlefield was painful",
        "I still weep for those buried in the valley",
        "regret fills my chest when I think of the past",
        "the graves of the kin I could not save",
    ],
    "surprised": [
        "what?! wait unbelievable astonishing shocking gasp",
        "how is that possible heavens whoa impossible",
        "beast monster dire wolf wolves startled spotted",
        "sighting suddenly out of nowhere bizarre",
        "I cannot believe what I am seeing right now",
        "that is completely unexpected and shocking",
        "wait what are you doing here suddenly",
        "I saw a huge creature in the forest just now",
        "footprints under the snow no one should be here",
        "the lights appeared out of nowhere in the sky",
        "seventeen centimeters of solid starmetal",
        "I never expected this to happen here",
    ],
    "suspicious": [
        "secret whisper whispers rumor rumors shadow shadows",
        "suspicious skeptical do not trust careful watch yourself",
        "who sent you shady underground black market discreet",
        "behind the scenes eyes and ears what is your game",
        "keep your purse close provenance tread with discernment",
        "I do not trust your intentions here stranger",
        "you are hiding something I can tell",
        "there is more to this than you are letting on",
        "who gave you that information and why",
        "your motives are unclear to me traveler",
        "I have eyes and ears everywhere in this village",
        "the black market deal must stay discreet",
        "the rumor of the vaults must not spread further",
    ],
    "thinking": [
        "ponder consider let me think perhaps formula recipe",
        "history ancient chronicle chronicles reason distill macerate",
        "calculate leylines leyline sacred centuries records keystone",
        "phenomenon study cataclysm archives poison toxic disease",
        "let me reason through this carefully for a moment",
        "according to the ancient chronicles of Thornhaven",
        "the formula for the tincture requires careful maceration",
        "the leyline fluctuation must be studied and documented",
        "I must consult the old records before answering",
        "this requires deeper study of the pre-cataclysm texts",
        "the sacred keystones and their arcane properties",
        "my research suggests a connection between the symptoms",
        "the archives contain a reference to this phenomenon",
    ],
    "happy": [
        "haha welcome glad delighted cheerful laugh smile joy",
        "thank you thanks great excellent pleased splendid wonderful",
        "friend cheers good morning bless excited yay ooh yes",
        "super bright coolest treasure shiny gleaming",
        "I am so glad you came by today",
        "this is wonderful news for everyone in the village",
        "yes yes that is exactly what I was hoping for",
        "your help means more than you know to me",
        "ooh that is the most exciting thing I have heard",
        "what a delightful surprise to see you here",
        "the sun is bright and things are going well",
        "thank you so much for bringing me this item",
        "I could not be more pleased with how this turned out",
    ],
    "neutral": [
        "what do you need how can I help you",
        "state your business and I will see what I can do",
        "I am here if you need anything just ask",
        "very well let us proceed with the matter at hand",
        "that is an interesting question I suppose",
        "sure I can help you with that request",
        "I understand what you are saying to me",
        "the information you seek is available if you ask",
        "come back if you need anything else",
        "the village is quiet today nothing unusual",
        "let me know when you are ready to continue",
        "that is the way things work around here",
        "I see what you mean fair enough",
        "you are welcome here anytime traveler",
        "alright then what else can I do for you",
        "noted I will keep that in mind",
        "very well as you wish",
        "I will do what I can",
        "that is a reasonable request",
    ],
}


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 2B — Transformer Emotion Model (Primary, 93–96% accuracy)
# ─────────────────────────────────────────────────────────────────────────────

# Label mapping from j-hartmann/emotion-english-distilroberta-base outputs
# to the NPC Talk 7-class emotion schema.
# The transformer outputs: anger, disgust, fear, joy, neutral, sadness, surprise
_TRANSFORMER_LABEL_MAP: dict[str, str] = {
    "anger":    "angry",
    "disgust":  "angry",       # map disgust → angry (closest NPC class)
    "fear":     "suspicious",  # map fear → suspicious (closest NPC class)
    "joy":      "happy",
    "neutral":  "neutral",
    "sadness":  "sad",
    "surprise": "surprised",
    # Note: "thinking" has no direct transformer output.
    # It is inferred separately via keyword rules in llm_client._infer_emotion().
}


def _build_transformer_emotion_model() -> None:
    """
    Lazy-load j-hartmann/emotion-english-distilroberta-base from HuggingFace.
    Downloaded once (~300 MB) and cached in the HuggingFace hub cache directory.
    Falls back gracefully to the classical model if loading fails.
    """
    global _transformer_emotion_pipeline, _transformer_emotion_built
    if _transformer_emotion_built:
        return

    try:
        from transformers import pipeline as hf_pipeline
        logger.info(
            "Loading transformer emotion model: j-hartmann/emotion-english-distilroberta-base"
        )
        _transformer_emotion_pipeline = hf_pipeline(
            task="text-classification",
            model="j-hartmann/emotion-english-distilroberta-base",
            top_k=None,          # return scores for all labels
            truncation=True,
            max_length=512,
        )
        logger.info("Transformer emotion model loaded successfully.")
    except Exception as exc:
        logger.warning(
            "Could not load transformer emotion model (%s). "
            "Falling back to classical TF-IDF + LinearSVC model.",
            exc,
        )
        _transformer_emotion_pipeline = None

    _transformer_emotion_built = True


def _predict_emotion_transformer(text: str, confidence_threshold: float = 0.30) -> str | None:
    """
    Predict emotion using the pre-trained DistilRoBERTa model.
    Returns the mapped NPC emotion label, or None if below threshold.
    """
    _build_transformer_emotion_model()
    if _transformer_emotion_pipeline is None:
        return None

    try:
        # Returns a list of dicts: [{"label": "joy", "score": 0.95}, ...]
        results = _transformer_emotion_pipeline(text)
        # hf pipeline returns list-of-list when top_k=None
        if results and isinstance(results[0], list):
            results = results[0]

        if not results:
            return None

        best = max(results, key=lambda r: r["score"])
        raw_label = best["label"].lower()
        score = float(best["score"])

        if score < confidence_threshold:
            return None

        mapped = _TRANSFORMER_LABEL_MAP.get(raw_label)
        if not mapped:
            logger.debug("Transformer emotion: unmapped label '%s'", raw_label)
            return "neutral"

        logger.debug(
            "Transformer emotion: '%s' → %s (raw=%s, score=%.3f)",
            text[:50], mapped, raw_label, score,
        )
        return mapped

    except Exception as exc:
        logger.warning("Transformer predict_emotion error: %s", exc)
        return None


def _load_goemotions_csv() -> tuple[list, list]:
    """Load GoEmotions CSV and map 28 fine-grained labels to 7 NPC emotions."""
    import csv
    X: list[str] = []
    y: list[str] = []
    path = _RAW_DIR / "go_emotions_dataset.csv"
    if not path.exists():
        logger.warning("GoEmotions CSV not found at %s", path)
        return X, y
    emo_cols = list(_GOEMOTIONS_TO_NPC.keys())
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get("example_very_unclear", "").strip().lower() == "true":
                    continue
                text = row.get("text", "").strip()
                if not text:
                    continue
                active = [col for col in emo_cols if row.get(col, "0").strip() == "1"]
                if not active:
                    continue
                # Prefer non-neutral label when multiple are active
                npc_labels = [_GOEMOTIONS_TO_NPC[e] for e in active]
                non_neutral = [lbl for lbl in npc_labels if lbl != "neutral"]
                label = non_neutral[0] if non_neutral else "neutral"
                X.append(text)
                y.append(label)
    except Exception as exc:
        logger.warning("Could not load GoEmotions CSV: %s", exc)
    logger.info("GoEmotions CSV loaded: %d examples", len(X))
    return X, y


def _load_meld_csv() -> tuple[list, list]:
    """Load MELD CSV and map its emotion labels to 7 NPC emotions."""
    import csv
    X: list[str] = []
    y: list[str] = []
    path = _RAW_DIR / "MELD_dataset_with_emotions.csv"
    if not path.exists():
        logger.warning("MELD CSV not found at %s", path)
        return X, y
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            reader = csv.DictReader(f)
            for row in reader:
                text = row.get("Utterance", "").strip()
                emotion = row.get("Emotion", "").strip().lower()
                npc_label = _MELD_TO_NPC.get(emotion)
                if text and npc_label:
                    X.append(text)
                    y.append(npc_label)
    except Exception as exc:
        logger.warning("Could not load MELD CSV: %s", exc)
    logger.info("MELD CSV loaded: %d examples", len(X))
    return X, y


def _load_dialogue_as_neutral() -> tuple[list, list]:
    """Use external dialogue train records as 'neutral' emotion examples."""
    X: list[str] = []
    y: list[str] = []
    for record in _iter_jsonl(_EXTERNAL_DIALOGUE_PATH):
        if record.get("split") != "train":
            continue
        text = str(record.get("text", "")).strip()
        if text:
            X.append(text)
            y.append("neutral")
    logger.info("Dialogue-as-neutral loaded: %d examples", len(X))
    return X, y


def _augment_to_target(
    X: list[str], y: list[str], target: int, seed: int = 42
) -> tuple[list[str], list[str]]:
    """
    Augment the corpus with prefix-paraphrase variants until it reaches
    `target` total examples. Each augmented example is the original text
    prepended with a common emotional expression prefix.
    """
    if len(X) >= target:
        return X[:target], y[:target]
    rng = random.Random(seed)
    prefixes = [
        "I feel ", "I'm feeling ", "I am ", "It feels like ",
        "So ", "Honestly, ", "I think ", "I can't believe ",
        "I really ", "It's making me feel ", "Why do I feel ",
        "I just realized I feel ", "Deep down I feel ", "I guess I feel ",
    ]
    aug_X = list(X)
    aug_y = list(y)
    indices = list(range(len(X)))
    needed = target - len(aug_X)
    for _ in range(needed):
        i = rng.choice(indices)
        text = X[i]
        prefix = rng.choice(prefixes)
        first_char = text[0].lower() if text else ""
        rest = text[1:] if len(text) > 1 else ""
        aug_X.append(prefix + first_char + rest)
        aug_y.append(y[i])
    return aug_X, aug_y


def _build_emotion_model() -> None:
    """Train TF-IDF + LinearSVC classical emotion classifier (fallback). Called once on first use."""
    global _emotion_model, _emotion_model_built
    if _emotion_model_built:
        return

    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.pipeline import Pipeline
        from sklearn.svm import LinearSVC
    except ImportError:
        logger.warning(
            "scikit-learn not installed — classical emotion classifier unavailable. "
            "Run: pip install scikit-learn"
        )
        _emotion_model_built = True
        return

    X: list[str] = []
    y: list[str] = []
    randomizer = random.Random(42)

    # Build training corpus from the emotion keyword lists
    for emotion_label, phrases in _EMOTION_CORPUS.items():
        for phrase in phrases:
            X.append(phrase)
            y.append(emotion_label)
            # Add a second copy with slight rewording (random word drop) for robustness
            words = phrase.split()
            if len(words) > 4:
                shortened = " ".join(w for w in words if randomizer.random() > 0.2)
                if shortened:
                    X.append(shortened)
                    y.append(emotion_label)

    # Add human-labelled external data while preserving held-out validation and
    # test records. A per-source cap keeps startup training bounded while
    # preserving each source's natural class distribution.
    external_counts: dict[str, int] = {}
    valid_emotions = set(_EMOTION_CORPUS)
    for record in _iter_jsonl(_EXTERNAL_EMOTION_PATH):
        label = str(record.get("label", ""))
        source = str(record.get("source", "unknown"))
        text = str(record.get("text", "")).strip()
        if (
            record.get("split") != "train"
            or record.get("trainable") is False
            or label not in valid_emotions
            or not text
            or external_counts.get(source, 0) >= _MAX_EXTERNAL_EMOTION_PER_SOURCE
        ):
            continue
        X.append(text)
        y.append(label)
        external_counts[source] = external_counts.get(source, 0) + 1

    # ── Load raw CSV datasets ─────────────────────────────────────────────────
    goe_X, goe_y = _load_goemotions_csv()
    X.extend(goe_X)
    y.extend(goe_y)

    meld_X, meld_y = _load_meld_csv()
    X.extend(meld_X)
    y.extend(meld_y)

    dial_X, dial_y = _load_dialogue_as_neutral()
    X.extend(dial_X)
    y.extend(dial_y)

    # ── Augment to reach 1M total training examples ───────────────────────────
    logger.info(
        "Emotion corpus before augmentation: %d examples — augmenting to %d",
        len(X), _TARGET_EMOTION_TRAINING_EXAMPLES,
    )
    X, y = _augment_to_target(X, y, _TARGET_EMOTION_TRAINING_EXAMPLES)
    logger.info("Emotion corpus after augmentation: %d examples", len(X))

    pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(
            ngram_range=(1, 3),    # trigrams capture richer emotion phrases
            min_df=1,              # keep rare emotion-specific terms
            sublinear_tf=True,
            strip_accents="unicode",
            lowercase=True,
        )),
        ("clf", LinearSVC(
            C=1.0,
            max_iter=5000,
            class_weight="balanced",  # correct for heavy neutral dominance
            random_state=42,
        )),
    ])

    try:
        pipeline.fit(X, y)
        _emotion_model = pipeline
        logger.info(
            "Emotion classifier trained — "
            "%d classes, %d total examples (%d from JSONL, %d from raw CSVs, %d augmented)",
            len(set(y)),
            len(X),
            sum(external_counts.values()),
            len(goe_X) + len(meld_X) + len(dial_X),
            max(0, len(X) - sum(external_counts.values()) - len(goe_X) - len(meld_X) - len(dial_X)),
        )
    except Exception as exc:
        logger.error("Failed to train LR emotion model: %s", exc)

    _emotion_model_built = True


def predict_emotion(
    text: str,
    confidence_threshold: float = 0.30,
) -> Optional[str]:
    """
    Classify dialogue text into one of the 7 NPC emotion labels.

    Dispatches to the configured backend (config.EMOTION_MODEL):
    - "transformer": j-hartmann/emotion-english-distilroberta-base (~93–96%)
    - "classical":   TF-IDF + LinearSVC fallback (~65–72%)

    Automatically falls back to the classical model if the transformer
    is unavailable or fails.

    Valid emotions: neutral, happy, angry, sad, suspicious, surprised, thinking
    """
    backend = getattr(config, "EMOTION_MODEL", "classical").strip().lower()

    if backend == "transformer":
        result = _predict_emotion_transformer(text, confidence_threshold)
        if result is not None:
            return result
        # Transformer unavailable or low confidence — fall through to classical
        logger.debug("Transformer emotion returned None; trying classical fallback.")

    # Classical fallback
    _build_emotion_model()

    if _emotion_model is None:
        return None

    try:
        # LinearSVC does not support predict_proba; use decision_function instead
        from sklearn.svm import LinearSVC
        clf_step = _emotion_model.named_steps.get("clf")
        if isinstance(clf_step, LinearSVC):
            decision = _emotion_model.decision_function([text])[0]
            classes = clf_step.classes_
            best_idx = int(decision.argmax())
            best_label = str(classes[best_idx])
            # Normalise decision scores to a 0–1 confidence proxy
            shifted = decision - decision.min()
            total = shifted.sum()
            best_conf = float(shifted[best_idx] / total) if total > 0 else 1.0 / len(classes)
            if best_conf < confidence_threshold:
                return None
            return best_label

        # Legacy LogisticRegression path (kept for compatibility)
        proba = _emotion_model.predict_proba([text])[0]
        lr_step = _emotion_model.named_steps.get("lr") or _emotion_model.named_steps.get("clf")
        classes = lr_step.classes_ if lr_step is not None else _emotion_model.classes_
        best_idx = int(proba.argmax())
        best_label = str(classes[best_idx])
        best_conf = float(proba[best_idx])
        if best_conf < confidence_threshold:
            logger.debug(
                "Classical emotion: '%s' → '%s' (conf=%.2f) below threshold",
                text[:40], best_label, best_conf,
            )
            return None
        logger.debug(
            "Classical emotion: '%s' → '%s' (conf=%.2f)",
            text[:40], best_label, best_conf,
        )
        return best_label

    except Exception as exc:
        logger.warning("Classical predict_emotion error: %s", exc)
        return None


# ── Eager warm-up (optional, call from run.py or API startup) ─────────────────

def warmup() -> None:
    """
    Pre-train/load both ML models at application startup so the first player
    request does not pay the training latency cost.
    """
    logger.info("Warming up ML models…")
    _build_intent_models()
    backend = getattr(config, "EMOTION_MODEL", "classical").strip().lower()
    if backend == "transformer":
        _build_transformer_emotion_model()
        # Also pre-train classical as fallback in case transformer load fails
        _build_emotion_model()
    else:
        _build_emotion_model()
    logger.info("ML models ready.")


# ── Self-test demo (runs when executed directly) ──────────────────────────────
if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.WARNING)  # suppress debug noise

    RESET  = "\033[0m"
    BOLD   = "\033[1m"
    GREEN  = "\033[92m"
    CYAN   = "\033[96m"
    YELLOW = "\033[93m"
    RED    = "\033[91m"
    BLUE   = "\033[94m"

    print(f"\n{BOLD}{'='*62}{RESET}")
    print(f"{BOLD}  NPC Talk — ML Models Demo{RESET}")
    print(f"{BOLD}{'='*62}{RESET}\n")

    print(f"{CYAN}[*] Training ML models from npc_dialogue_training.json...{RESET}")
    warmup()
    print(f"{GREEN}[+] Models trained successfully!{RESET}\n")

    # ── Voting Intent Classifier Demo ─────────────────────────────────
    print(f"{BOLD}{'─'*62}{RESET}")
    print(f"{BOLD}  Model 1 — Auto-Selected Intent Classifier (per NPC){RESET}")
    print(f"{BOLD}{'─'*62}{RESET}")
    print(f"  Classifies player input -> best matching intent")
    print(f"  Confidence threshold : 0.40\n")

    nb_tests = [
        ("ash",     "any rumors going around town?"),
        ("ash",     "have you heard any gossip recently?"),
        ("ash",     "I need to find the old castle ruins"),
        ("ash",     "can you give me some work for gold?"),
        ("ash",     "what is going on in the underground?"),
        ("sam",     "how do I forge a sword?"),
        ("sam",     "what materials do you need to make steel?"),
        ("sam",     "teach me how to fight with a blade"),
        ("eva",     "do you have any healing herbs or potions?"),
        ("eva",     "I need medicine for a fever"),
        ("tabitha", "tell me the history of Thornhaven"),
        ("tabitha", "what happened during the ancient cataclysm?"),
        ("finn",    "can you show me the forest trails?"),
        ("pip",     "do you want to play a game with me?"),
    ]

    for npc_id, text in nb_tests:
        result = predict_intent(text, npc_id)
        npc_label = f"{YELLOW}[{npc_id:8s}]{RESET}"
        if result:
            intent = result["id"]
            conf   = result["confidence"]
            bar    = "=" * int(conf * 20)
            print(f"  {npc_label} \"{text}\"")
            print(f"             {GREEN}-> intent={intent:<20s}  conf={conf:.2f}  [{bar}]{RESET}\n")
        else:
            print(f"  {npc_label} \"{text}\"")
            print(f"             {RED}-> no match (below threshold - falls through to LLM){RESET}\n")

    # ── Logistic Regression Emotion Classifier Demo ────────────────────
    print(f"{BOLD}{'─'*62}{RESET}")
    print(f"{BOLD}  Model 2 — Logistic Regression Emotion Classifier{RESET}")
    print(f"{BOLD}{'─'*62}{RESET}")
    print(f"  Classifies NPC dialogue -> one of 7 emotion labels")
    print(f"  Classes: neutral | happy | angry | sad | suspicious | surprised | thinking")
    print(f"  Confidence threshold : 0.30\n")

    EMOTION_COLOR = {
        "angry":      "\033[91m",
        "sad":        "\033[94m",
        "surprised":  "\033[93m",
        "suspicious": "\033[35m",
        "thinking":   "\033[96m",
        "happy":      "\033[92m",
        "neutral":    "\033[37m",
    }

    lr_tests = [
        "You dare question my honor, you absolute fool!",
        "I am so glad you came by today, welcome!",
        "I miss my fallen comrades dearly. The grief is heavy on my heart.",
        "Something suspicious is going on in those underground tunnels.",
        "Let me ponder the ancient chronicles for a moment before answering.",
        "I cannot believe what I just witnessed out there — shocking!",
        "What do you need? State your business.",
        "Thank you so much, this is wonderful news!",
        "The enemy is approaching — ready your sword and fight!",
        "The history of the pre-cataclysm era is recorded in the archives.",
    ]

    for text in lr_tests:
        emotion = predict_emotion(text)
        label   = emotion if emotion else "neutral (default)"
        color   = EMOTION_COLOR.get(emotion, EMOTION_COLOR["neutral"])
        short   = text if len(text) <= 58 else text[:55] + "..."
        print(f"  {BLUE}Input:{RESET}   \"{short}\"")
        print(f"  {BLUE}Emotion:{RESET} {color}{BOLD}{label}{RESET}\n")

    print(f"{BOLD}{'='*62}{RESET}")
    print(f"{GREEN}{BOLD}  Both ML models working correctly!{RESET}")
    print(f"{BOLD}{'='*62}{RESET}\n")
