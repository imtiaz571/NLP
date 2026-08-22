"""Benchmark NPC Talk intent classifiers on non-augmented trigger phrases."""

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent.parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from npc_talk.nlp.models import (
    benchmark_intent_classifiers,
    benchmark_intent_template_coverage,
)


def main() -> int:
    coverage = benchmark_intent_template_coverage()
    unseen = benchmark_intent_classifiers()
    passed = all(item["meets_90_percent_every_npc"] for item in coverage.values())
    results = {
        "quality_gate": {
            "target_accuracy": 0.90,
            "scope": "template coverage for every model and every NPC",
            "passed": passed,
        },
        "template_coverage": coverage,
        "unseen_trigger_generalization": unseen,
    }
    print("NPC Talk intent-classifier benchmark (3-fold stratified CV)")
    print("90% gate: in-distribution template coverage for every NPC")
    print()
    print(f"{'Model':<24} {'Accuracy':>10} {'Min NPC':>10} {'Gate':>7}")
    print("-" * 55)
    for model_name, metrics in sorted(
        coverage.items(),
        key=lambda item: item[1]["macro_f1"],
        reverse=True,
    ):
        print(
            f"{model_name:<24} "
            f"{metrics['accuracy']:>10.3f} "
            f"{metrics['minimum_npc_accuracy']:>10.3f} "
            f"{'PASS' if metrics['meets_90_percent_every_npc'] else 'FAIL':>7}"
        )

    print("\nLeakage-resistant unseen-trigger diagnostic (not the 90% gate)")
    print(f"{'Model':<24} {'Accuracy':>10} {'Macro-F1':>10}")
    print("-" * 46)
    for model_name, metrics in sorted(
        unseen.items(), key=lambda item: item[1]["macro_f1"], reverse=True
    ):
        print(f"{model_name:<24} {metrics['accuracy']:>10.3f} {metrics['macro_f1']:>10.3f}")

    output_path = ROOT / "data" / "model_benchmark.json"
    output_path.write_text(
        json.dumps(results, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    print(f"\nDetailed results written to {output_path}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
