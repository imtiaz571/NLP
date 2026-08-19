import urllib.request
import json

base_url = "http://127.0.0.1:8000"

def check_endpoint(path, method="GET", payload=None):
    url = base_url + path
    headers = {"Content-Type": "application/json"}
    data = json.dumps(payload).encode("utf-8") if payload else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            content = resp.read()
            status = resp.status
            print(f"[PASS] {method} {path} -> {status} ({len(content)} bytes)")
            if "application/json" in resp.headers.get("Content-Type", ""):
                try:
                    parsed = json.loads(content.decode())
                    if isinstance(parsed, list):
                        print(f"       Items returned: {len(parsed)}")
                    elif isinstance(parsed, dict):
                        for k, v in list(parsed.items())[:4]:
                            val_str = str(v)[:80] + ("..." if len(str(v)) > 80 else "")
                            print(f"       {k}: {val_str}")
                except Exception as ex:
                    print(f"       Could not format json: {ex}")
            return True
    except Exception as e:
        print(f"[FAIL] {method} {path} -> {e}")
        return False

def main():
    print("=== Testing Static Files & Frontend Assets ===")
    check_endpoint("/")
    check_endpoint("/game-ui.css")
    check_endpoint("/styles.css")
    check_endpoint("/js/config.js")
    check_endpoint("/js/audio.js")
    check_endpoint("/js/particles.js")
    check_endpoint("/js/script.js")

    print("\n=== Testing API Endpoints ===")
    check_endpoint("/health")
    check_endpoint("/npcs")

    print("\n=== Testing Live Chat Dialogue Generation (All 6 NPCs) ===")
    npc_prompts = {
        "ash": "What rumors have you heard lately?",
        "finn": "Have you seen any strange creatures in the forest?",
        "eva": "Can you prepare an antidote or remedy for me?",
        "sam": "Can you inspect and repair my blade?",
        "tabitha": "Tell me about the history of the ancient ruins.",
        "pip": "Hey Pip, what treasures did you find today?"
    }

    for npc_id, prompt in npc_prompts.items():
        print(f"\n--- NPC: {npc_id} (Prompt: \"{prompt}\") ---")
        msg = {"player_id": "player_1", "npc_id": npc_id, "message": prompt}
        check_endpoint("/chat", method="POST", payload=msg)

    print("\n=== Testing Game State & Profile & History Sync ===")
    check_endpoint("/profile?player_id=player_1")
    check_endpoint("/profile", method="POST", payload={"player_id": "player_1", "name": "Valen", "gender": "male", "age": 25, "occupation": "scout"})
    check_endpoint("/state?player_id=player_1&npc_id=ash")
    check_endpoint("/state", method="POST", payload={"player_id": "player_1", "npc_id": "ash", "location": "tavern", "time_of_day": "night"})
    check_endpoint("/history?player_id=player_1&npc_id=ash")

if __name__ == "__main__":
    main()
