"""Normalize external Kaggle datasets for NPC Talk.

Outputs are JSON Lines files under data/processed. Raw labels and provenance
are always retained. Only records with explicit ``npc_targets`` mappings are
eligible for the live intent classifier; domain-mismatched labels remain useful
for offline experiments but cannot silently contaminate NPC intent training.
"""

from __future__ import annotations

import ast
import csv
import hashlib
import json
import re
from collections import Counter
from pathlib import Path
from typing import Iterable, Iterator


ROOT = Path(__file__).resolve().parent.parent
EXTERNAL = ROOT / "data" / "external"
PROCESSED = ROOT / "data" / "processed"
MANIFEST = json.loads((ROOT / "data" / "external_sources.json").read_text(encoding="utf-8"))
LICENSES = {source["id"]: source["license"] for source in MANIFEST["sources"]}

EMOTION_OUTPUT = PROCESSED / "external_emotions.jsonl"
INTENT_OUTPUT = PROCESSED / "external_intents.jsonl"
DIALOGUE_OUTPUT = PROCESSED / "external_dialogue.jsonl"
REPORT_OUTPUT = PROCESSED / "external_data_report.json"

DAILY_EMOTIONS = {"0": "neutral", "1": "angry", "4": "happy", "5": "sad", "6": "surprised"}
DAILY_ACTS = {"1": "inform", "2": "question", "3": "directive", "4": "commissive"}
GO_EMOTION_MAP = {
    "admiration": "happy", "amusement": "happy", "approval": "happy",
    "caring": "happy", "excitement": "happy", "gratitude": "happy",
    "joy": "happy", "love": "happy", "optimism": "happy",
    "pride": "happy", "relief": "happy",
    "anger": "angry", "annoyance": "angry", "disapproval": "angry",
    "disgust": "angry", "disappointment": "sad", "grief": "sad",
    "remorse": "sad", "sadness": "sad", "surprise": "surprised",
    "confusion": "thinking", "curiosity": "thinking", "realization": "thinking",
    "neutral": "neutral",
}
MELD_EMOTIONS = {
    "angry": "angry", "happy": "happy", "neutral": "neutral",
    "sad": "sad", "surprise": "surprised",
}

IDENTITY_TARGETS = {
    "ash": "identity", "finn": "origin_story", "eva": "origin_story",
    "sam": "origin_story", "tabitha": "identity_age",
}
SMALLTALK_TARGETS = {
    "smalltalk_agent_acquaintance": IDENTITY_TARGETS,
    "smalltalk_agent_origin": IDENTITY_TARGETS,
    "smalltalk_agent_age": {"tabitha": "identity_age"},
    "smalltalk_agent_birth_date": {"tabitha": "identity_age"},
    "smalltalk_user_needs_advice": {"tabitha": "advice_guidance"},
    "smalltalk_greetings_hello": {"pip": "greeting"},
    "smalltalk_greetings_goodmorning": {"pip": "greeting"},
    "smalltalk_greetings_goodevening": {"pip": "greeting"},
    "smalltalk_greetings_how_are_you": {"pip": "greeting"},
    "smalltalk_greetings_nice_to_meet_you": {"pip": "greeting"},
    "smalltalk_greetings_nice_to_see_you": {"pip": "greeting"},
    "smalltalk_greetings_nice_to_talk_to_you": {"pip": "greeting"},
    "smalltalk_greetings_whatsup": {"pip": "greeting"},
}

_QUOTED_VALUE = re.compile(r"(['\"])((?:\\.|(?!\1).)*)\1", re.DOTALL)


def stable_split(source: str, key: str) -> str:
    bucket = int(hashlib.sha1(f"{source}\0{key}".encode("utf-8")).hexdigest()[:8], 16) % 10
    return "train" if bucket < 8 else "validation" if bucket == 8 else "test"


def clean_text(value: object) -> str:
    text = str(value or "").replace("\ufffd", "'")
    return re.sub(r"\s+", " ", text).strip()


def rows(path: Path, *, encoding: str = "utf-8-sig", delimiter: str = ",") -> Iterator[dict]:
    with path.open("r", encoding=encoding, errors="replace", newline="") as stream:
        yield from csv.DictReader(stream, delimiter=delimiter)


def array_strings(value: str) -> list[str]:
    result = []
    for match in _QUOTED_VALUE.finditer(value):
        try:
            result.append(clean_text(ast.literal_eval(match.group(0))))
        except (SyntaxError, ValueError):
            result.append(clean_text(match.group(2)))
    return result


def array_numbers(value: str) -> list[str]:
    return re.findall(r"\d+", value or "")


def base_record(text: str, source: str, split: str, original_label: str | None = None) -> dict:
    record = {"text": clean_text(text), "source": source, "split": split, "license": LICENSES[source]}
    if original_label is not None:
        record["original_label"] = original_label
    return record


def dailydialog_records() -> Iterator[tuple[str, dict]]:
    for path in sorted((EXTERNAL / "dailydialog").glob("*.csv")):
        split = "validation" if path.stem == "validation" else path.stem
        for row in rows(path):
            utterances = array_strings(row.get("dialog", ""))
            acts = array_numbers(row.get("act", ""))
            emotions = array_numbers(row.get("emotion", ""))
            for index, text in enumerate(utterances):
                if not text:
                    continue
                common = base_record(text, "dailydialog", split)
                common["turn_index"] = index
                yield "dialogue", {**common, "training_use": "natural_dialogue"}
                if index < len(acts) and acts[index] in DAILY_ACTS:
                    act = DAILY_ACTS[acts[index]]
                    yield "intent", {**common, "label": f"dialogue_act_{act}", "original_label": acts[index]}
                if index < len(emotions) and emotions[index] in DAILY_EMOTIONS:
                    label = DAILY_EMOTIONS[emotions[index]]
                    yield "emotion", {**common, "label": label, "original_label": emotions[index]}


def goemotion_records() -> Iterator[tuple[str, dict]]:
    path = EXTERNAL / "goemotions" / "go_emotions_dataset.csv"
    for row in rows(path):
        text = clean_text(row.get("text"))
        if not text or str(row.get("example_very_unclear", "")).lower() == "true":
            continue
        mapped = {GO_EMOTION_MAP[name] for name in GO_EMOTION_MAP if row.get(name) == "1"}
        if len(mapped) != 1:
            continue
        label = mapped.pop()
        originals = sorted(name for name in GO_EMOTION_MAP if row.get(name) == "1")
        record = base_record(text, "goemotions", stable_split("goemotions", row.get("id", text)), ",".join(originals))
        yield "emotion", {**record, "label": label}


def smalltalk_records() -> Iterator[tuple[str, dict]]:
    path = EXTERNAL / "smalltalk" / "Small_talk_Intent.csv"
    for index, row in enumerate(rows(path)):
        text, label = clean_text(row.get("Utterances")), clean_text(row.get("Intent"))
        if text and label:
            record = base_record(text, "smalltalk", stable_split("smalltalk", f"{index}:{text}"), label)
            yield "intent", {**record, "label": label, "npc_targets": SMALLTALK_TARGETS.get(label, {})}


def viggo_records() -> Iterator[tuple[str, dict]]:
    for path in sorted((EXTERNAL / "viggo").glob("*.csv")):
        # challenge_train_*.csv files are training-split challenge subsets — include them
        if path.stem.startswith("challenge_"):
            split = "train"
        else:
            split = "validation" if path.stem == "validation" else path.stem
        for row in rows(path):
            text = clean_text(row.get("target"))
            mr = clean_text(row.get("meaning_representation"))
            if not text:
                continue
            act = mr.split("(", 1)[0].strip() or "unknown"
            # Use a distinct source id for challenge records so they can be traced
            source = "viggo_challenge" if split == "train" and path.stem.startswith("challenge_") else "viggo"
            common = base_record(text, source, split, act)
            yield "dialogue", {**common, "meaning_representation": mr, "training_use": "game_dialogue"}
            yield "intent", {**common, "label": f"viggo_{act}"}


def fallout_records() -> Iterator[tuple[str, dict]]:
    path = EXTERNAL / "fallout" / "fallout_new_vegas_dataset.csv"
    for index, row in enumerate(rows(path, encoding="latin-1", delimiter=";")):
        text = clean_text(row.get("text_content"))
        if len(text) < 3:
            continue
        yield "dialogue", {
            **base_record(text, "fallout_new_vegas", stable_split("fallout_new_vegas", str(index))),
            "speaker": clean_text(row.get("speaker")),
            "topic": clean_text(row.get("topic")),
            "quest": clean_text(row.get("quest")),
            "training_use": "research_reference_only",
            "trainable": False,
        }


def bitext_records() -> Iterator[tuple[str, dict]]:
    import os as _os
    bitext_dir = EXTERNAL / "bitext"
    found: list[tuple[int, Path]] = []
    try:
        for root, _dirs, files in _os.walk(str(bitext_dir)):
            for fname in files:
                if fname.lower().endswith(".csv"):
                    try:
                        full = Path(root) / fname
                        size = full.stat().st_size
                        found.append((size, full))
                    except OSError:
                        continue
    except OSError:
        pass
    if not found:
        return
    # Pick the largest CSV (most comprehensive dataset)
    found.sort(key=lambda t: t[0], reverse=True)
    largest_path = found[0][1]
    for index, row in enumerate(rows(largest_path)):
        text, label = clean_text(row.get("utterance")), clean_text(row.get("intent"))
        if text and label:
            record = base_record(text, "bitext", stable_split("bitext", f"{index}:{text}"), label)
            yield "intent", {
                **record, "label": label, "category": clean_text(row.get("category")),
                "flags": clean_text(row.get("flags")), "npc_targets": {}, "trainable": False,
            }



def chatbot_intent_records() -> Iterator[tuple[str, dict]]:
    path = EXTERNAL / "chatbot_intent" / "chatbot_intent_classification.csv"
    for index, row in enumerate(rows(path)):
        text, label = clean_text(row.get("user_input")), clean_text(row.get("intent"))
        if text and label:
            record = base_record(text, "chatbot_intent", stable_split("chatbot_intent", f"{index}:{text}"), label)
            yield "intent", {**record, "label": label, "npc_targets": {}, "synthetic": True}


def meld_records() -> Iterator[tuple[str, dict]]:
    path = EXTERNAL / "meld_text" / "MELD_dataset_with_emotions.csv"
    for row in rows(path):
        text, original = clean_text(row.get("Utterance")), clean_text(row.get("Emotion")).lower()
        label = MELD_EMOTIONS.get(original)
        if text and label:
            key = clean_text(row.get("File_Name")) or text
            record = base_record(text, "meld_text", stable_split("meld_text", key), original)
            yield "emotion", {**record, "label": label}


BUILDERS = (
    dailydialog_records, goemotion_records, smalltalk_records, viggo_records,
    fallout_records, bitext_records, chatbot_intent_records, meld_records,
)


def write_jsonl(path: Path, records: Iterable[dict]) -> int:
    count = 0
    seen: set[tuple[str, str, str]] = set()
    with path.open("w", encoding="utf-8", newline="\n") as stream:
        for record in records:
            key = (record.get("source", ""), record.get("label", ""), record.get("text", "").lower())
            if not record.get("text") or key in seen:
                continue
            seen.add(key)
            stream.write(json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n")
            count += 1
    return count


def build() -> dict:
    PROCESSED.mkdir(parents=True, exist_ok=True)
    by_task: dict[str, list[dict]] = {"emotion": [], "intent": [], "dialogue": []}
    for builder in BUILDERS:
        for task, record in builder():
            by_task[task].append(record)

    counts = {
        "emotion": write_jsonl(EMOTION_OUTPUT, by_task["emotion"]),
        "intent": write_jsonl(INTENT_OUTPUT, by_task["intent"]),
        "dialogue": write_jsonl(DIALOGUE_OUTPUT, by_task["dialogue"]),
    }
    source_counts = Counter(record["source"] for records in by_task.values() for record in records)
    mapped_intents = sum(bool(record.get("npc_targets")) for record in by_task["intent"])
    report = {
        "version": 1,
        "counts": counts,
        "source_records_before_deduplication": dict(sorted(source_counts.items())),
        "live_mapped_intent_records_before_deduplication": mapped_intents,
        "outputs": {
            "emotion": str(EMOTION_OUTPUT.relative_to(ROOT)),
            "intent": str(INTENT_OUTPUT.relative_to(ROOT)),
            "dialogue": str(DIALOGUE_OUTPUT.relative_to(ROOT)),
        },
    }
    REPORT_OUTPUT.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report


def main() -> int:
    report = build()
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
