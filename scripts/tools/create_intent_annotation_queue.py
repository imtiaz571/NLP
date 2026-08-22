"""Create a human-annotation queue for leakage-resistant intent evaluation.

The generated CSV deliberately contains blank utterances. A person should write
one natural player message per row and set ``review_status`` to ``approved``.
Train/validation/test assignments are fixed before annotation so test examples
cannot be moved into training after model results are inspected.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent.parent
TRAINING_PATH = ROOT / "data" / "npc_dialogue_training.json"
OUTPUT_PATH = ROOT / "data" / "intent_annotation_queue.csv"
EXAMPLES_PER_INTENT = 30


def main() -> int:
    data = json.loads(TRAINING_PATH.read_text(encoding="utf-8"))
    fields = (
        "npc_id", "intent_id", "example_number", "split", "utterance",
        "review_status", "seed_terms",
    )
    count = 0
    with OUTPUT_PATH.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        for npc_id, npc_data in data["npcs"].items():
            for intent in npc_data.get("intents", []):
                seeds = " | ".join(intent.get("triggers", []))
                for number in range(1, EXAMPLES_PER_INTENT + 1):
                    split = "train" if number <= 20 else "validation" if number <= 25 else "test"
                    writer.writerow({
                        "npc_id": npc_id,
                        "intent_id": intent["id"],
                        "example_number": number,
                        "split": split,
                        "utterance": "",
                        "review_status": "pending",
                        "seed_terms": seeds,
                    })
                    count += 1
    print(f"Wrote {count} annotation rows to {OUTPUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
