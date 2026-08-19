"""NPC Talk — Interactive Quickstart & Character Dialogue Tester."""
import sys
from pathlib import Path

# Ensure src is in Python path
ROOT_DIR = Path(__file__).resolve().parent
SRC_DIR = ROOT_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from npc_talk.llm.client import _generate_response
from npc_talk.nlp.models import warmup


def main():
    print("=" * 60)
    print("  NPC Talk — Character Dialogue & NLP Engine Quickstart")
    print("=" * 60)
    warmup()

    ctx = {
        "player_name": "Alex",
        "player_occupation": "adventurer",
        "player_age_group": "adult",
        "player_gender": "male",
        "location": "village_square",
        "time_of_day": "day",
    }

    sample_tests = [
        ("pip", "do you like sports"),
        ("pip", "what is your favorite food"),
        ("finn", "do you like sports"),
        ("sam", "is there a safe path into the ancient ruins?"),
        ("ash", "tell me about yourself"),
    ]

    print("\n--- Running Character Dialogue Tests ---")
    for npc, query in sample_tests:
        res = _generate_response(query, npc, ctx, [])
        print(f"\n[{npc.upper()}] Player: \"{query}\"")
        print(f"[{npc.upper()}] Reply: {res['dialogue']}")
        print(f"[{npc.upper()}] Emotion: {res.get('emotion', 'neutral')} | Action: {res.get('action', 'none')}")

    print("\n" + "=" * 60)
    print("  To launch the Web Server & Interactive UI, run: python run.py")
    print("  and navigate to: http://127.0.0.1:8000")
    print("=" * 60)


if __name__ == "__main__":
    main()
