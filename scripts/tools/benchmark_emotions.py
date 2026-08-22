"""Evaluate emotion models on untouched external test splits.

Benchmarks both the transformer model (primary) and the classical
TF-IDF + LinearSVC model (fallback), as well as a seed-only baseline.
"""

from __future__ import annotations

import json
import random
import sys
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent.parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from npc_talk import config
import npc_talk.nlp.models as ml_models


def _get_classical_classes(model) -> set:
    """Extract class labels from a sklearn Pipeline with a 'clf' step."""
    clf_step = model.named_steps.get("clf") or model.named_steps.get("lr")
    if clf_step is not None and hasattr(clf_step, "classes_"):
        return set(clf_step.classes_)
    # Fallback: try the pipeline directly
    if hasattr(model, "classes_"):
        return set(model.classes_)
    return set(ml_models._EMOTION_CORPUS.keys())


def main() -> int:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import accuracy_score, f1_score
    from sklearn.pipeline import Pipeline

    # ── 1. Build classical model ──────────────────────────────────────────────
    ml_models._build_emotion_model()
    classical_model = ml_models._emotion_model

    # ── 2. Determine valid labels from classical model ────────────────────────
    valid_labels = _get_classical_classes(classical_model) if classical_model else set(
        ml_models._EMOTION_CORPUS.keys()
    )

    # ── 3. Load external test split ───────────────────────────────────────────
    texts: list[str] = []
    labels: list[str] = []
    for record in ml_models._iter_jsonl(ml_models._EXTERNAL_EMOTION_PATH):
        if record.get("split") == "test" and record.get("label") in valid_labels:
            texts.append(record["text"])
            labels.append(record["label"])

    if not texts:
        print("ERROR: No test examples found in external_emotions.jsonl")
        return 1

    # ── 4. Seed-only baseline (LR trained on seed phrases only) ──────────────
    baseline_texts: list[str] = []
    baseline_labels: list[str] = []
    randomizer = random.Random(42)
    for label, phrases in ml_models._EMOTION_CORPUS.items():
        for phrase in phrases:
            baseline_texts.append(phrase)
            baseline_labels.append(label)
            words = phrase.split()
            if len(words) > 4:
                shortened = " ".join(word for word in words if randomizer.random() > 0.2)
                if shortened:
                    baseline_texts.append(shortened)
                    baseline_labels.append(label)

    baseline = Pipeline([
        ("tfidf", TfidfVectorizer(
            ngram_range=(1, 2), min_df=1, sublinear_tf=True,
            strip_accents="unicode", lowercase=True,
        )),
        ("lr", LogisticRegression(max_iter=1000, C=1.0, solver="lbfgs")),
    ])
    baseline.fit(baseline_texts, baseline_labels)
    baseline_predictions = baseline.predict(texts)
    baseline_accuracy = float(accuracy_score(labels, baseline_predictions))
    baseline_macro_f1 = float(
        f1_score(labels, baseline_predictions, average="macro", zero_division=0)
    )

    # ── 5. Classical model (TF-IDF + LinearSVC) ───────────────────────────────
    classical_accuracy: float | None = None
    classical_macro_f1: float | None = None
    if classical_model is not None:
        classical_predictions = classical_model.predict(texts)
        classical_accuracy = float(accuracy_score(labels, classical_predictions))
        classical_macro_f1 = float(
            f1_score(labels, classical_predictions, average="macro", zero_division=0)
        )

    # ── 6. Transformer model (primary, if configured) ─────────────────────────
    transformer_accuracy: float | None = None
    transformer_macro_f1: float | None = None
    transformer_available = False
    if getattr(config, "EMOTION_MODEL", "classical") == "transformer":
        print("Loading transformer model (this may take a moment on first run)...")
        ml_models._build_transformer_emotion_model()
        if ml_models._transformer_emotion_pipeline is not None:
            transformer_available = True
            transformer_predictions = [
                ml_models._predict_emotion_transformer(t, confidence_threshold=0.0) or "neutral"
                for t in texts
            ]
            transformer_accuracy = float(accuracy_score(labels, transformer_predictions))
            transformer_macro_f1 = float(
                f1_score(labels, transformer_predictions, average="macro", zero_division=0)
            )

    # ── 7. Build report ───────────────────────────────────────────────────────
    primary_accuracy = transformer_accuracy if transformer_available else classical_accuracy
    primary_macro_f1 = transformer_macro_f1 if transformer_available else classical_macro_f1

    report: dict = {
        "evaluation": "external test splits only",
        "examples": len(labels),
        "emotion_model_backend": getattr(config, "EMOTION_MODEL", "classical"),
        "baseline_seed_only": {
            "accuracy": baseline_accuracy,
            "macro_f1": baseline_macro_f1,
        },
        "with_external_training": {
            "accuracy": primary_accuracy,
            "macro_f1": primary_macro_f1,
        },
        "accuracy_improvement": (primary_accuracy - baseline_accuracy) if primary_accuracy is not None else None,
        "macro_f1_improvement": (primary_macro_f1 - baseline_macro_f1) if primary_macro_f1 is not None else None,
        "class_counts": dict(sorted(Counter(labels).items())),
    }

    if transformer_available and classical_accuracy is not None:
        report["classical_fallback"] = {
            "accuracy": classical_accuracy,
            "macro_f1": classical_macro_f1,
        }

    output = ROOT / "data" / "emotion_benchmark.json"
    output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    print(f"\nWritten to {output}")

    # ── 8. Print summary table ────────────────────────────────────────────────
    print("\n--- Emotion Accuracy Summary ---")
    print(f"  Seed-only baseline   : {baseline_accuracy:.2%}")
    if classical_accuracy is not None:
        print(f"  Classical (LinearSVC): {classical_accuracy:.2%}")
    if transformer_available and transformer_accuracy is not None:
        print(f"  Transformer (primary): {transformer_accuracy:.2%}  ← active model")
    print(f"  90%+ gate            : {'PASS' if (primary_accuracy or 0) >= 0.90 else 'FAIL'}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
