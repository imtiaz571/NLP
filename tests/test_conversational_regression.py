"""
Automated Regression Test Suite for NPC Talk Dialogue System.
Verifies topic relevance, pragmatic conversational handling, and context isolation.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from npc_talk.llm.client import _generate_response

CHARACTERS = ["sam", "ash", "eva", "tabitha", "finn", "pip"]
CTX = {'player_name': 'Alex', 'player_occupation': 'adventurer', 'player_age_group': 'adult', 'player_gender': 'male'}


def test_hunger_queries_all_characters():
    """Verify hunger queries route to food/tavern guidance, never unrelated topics."""
    queries = ["I am hungry", "I need food", "where can I eat something?"]
    food_keywords = ["stew", "bread", "tavern", "eat", "food", "cupboard", "figs", "biscuit", "meal", "baker", "rolls", "pie", "apple", "broth", "cook", "nourish"]
    
    for npc in CHARACTERS:
        for q in queries:
            messages = [{'role': 'system', 'content': f'You are {npc}'}]
            res = _generate_response(q, npc, CTX, messages)
            diag = res.get("dialogue", "").lower()
            assert any(kw in diag for kw in food_keywords), (
                f"[{npc.upper()}] Query '{q}' returned unrelated reply: '{diag}'"
            )


def test_lost_navigation_all_characters():
    """Verify lost/navigation queries route to directions/orientation."""
    queries = ["I am lost", "Where am I?", "lost my way"]
    nav_keywords = ["thornhaven", "village", "square", "forge", "apothecary", "tavern", "gate", "north", "east", "west", "south", "district", "center", "fountain"]
    
    for npc in CHARACTERS:
        for q in queries:
            messages = [{'role': 'system', 'content': f'You are {npc}'}]
            res = _generate_response(q, npc, CTX, messages)
            diag = res.get("dialogue", "").lower()
            assert any(kw in diag for kw in nav_keywords), (
                f"[{npc.upper()}] Query '{q}' returned unrelated reply: '{diag}'"
            )


def test_general_help_all_characters():
    """Verify general assistance queries return helpful character-grounded guidance."""
    queries = ["Can you help me with something?", "I need help", "What should I do?"]
    help_keywords = ["help", "need", "trouble", "solve", "remed", "forge", "advice", "guid", "scout", "assist", "point", "state", "weapons", "salve", "wisdom", "look"]
    
    for npc in CHARACTERS:
        for q in queries:
            messages = [{'role': 'system', 'content': f'You are {npc}'}]
            res = _generate_response(q, npc, CTX, messages)
            diag = res.get("dialogue", "").lower()
            assert any(kw in diag for kw in help_keywords), (
                f"[{npc.upper()}] Query '{q}' returned unrelated reply: '{diag}'"
            )


def test_tired_rest_queries():
    """Verify fatigue queries route to rest/tavern/inn rooms."""
    queries = ["I'm tired", "I am exhausted", "where can I sleep?"]
    rest_keywords = ["tavern", "rest", "sleep", "inn", "bed", "room", "tired", "straw", "exhaust", "chamomile", "lavender", "night"]
    
    for npc in ["sam", "ash", "eva", "tabitha", "finn"]:
        for q in queries:
            messages = [{'role': 'system', 'content': f'You are {npc}'}]
            res = _generate_response(q, npc, CTX, messages)
            diag = res.get("dialogue", "").lower()
            assert any(kw in diag for kw in rest_keywords), (
                f"[{npc.upper()}] Query '{q}' returned unrelated reply: '{diag}'"
            )


def test_weather_and_greetings():
    """Verify small talk and greetings return coherent in-character pleasantries."""
    for npc in CHARACTERS:
        # Greeting
        res_greet = _generate_response("Hello there", npc, CTX, [{'role': 'system', 'content': f'You are {npc}'}])
        diag_g = res_greet.get("dialogue", "").lower()
        assert len(diag_g) > 20, f"Greeting too short for {npc}"
        
        # Weather
        res_weather = _generate_response("Nice weather today", npc, CTX, [{'role': 'system', 'content': f'You are {npc}'}])
        diag_w = res_weather.get("dialogue", "").lower()
        assert any(kw in diag_w for kw in ["weather", "sky", "wind", "sun", "day", "mountain", "air", "clouds", "moisture", "clear"]), (
            f"[{npc.upper()}] Weather reply unrelated: '{diag_w}'"
        )


def test_context_isolation_after_lore_query():
    """
    Critical regression test:
    Verify that asking a lore question followed by 'I am hungry' does NOT
    pollute the hunger query with the lore topic!
    """
    messages = [
        {'role': 'system', 'content': 'You are sam'},
        {'role': 'user', 'content': 'Tell me about the siege of Ashenmoor'},
        {'role': 'assistant', 'content': 'I lost my left hand twenty years ago at the Siege of Ashenmoor when a shadow-beast breached the eastern palisade.'},
        {'role': 'user', 'content': 'I am hungry'}
    ]
    
    res = _generate_response("I am hungry", "sam", CTX, messages)
    diag = res.get("dialogue", "").lower()
    
    # Must be about food / tavern, NOT Ashenmoor or prosthetic arm!
    assert "ashenmoor" not in diag, f"Hunger query polluted by Ashenmoor lore: '{diag}'"
    assert any(kw in diag for kw in ["tavern", "stew", "bread", "cauldron", "eat", "food"]), (
        f"Hunger query did not return food response: '{diag}'"
    )


def test_explicit_continuation_still_works():
    """Verify that explicit follow-ups ('Why did that happen?') DO inherit context correctly."""
    messages = [
        {'role': 'system', 'content': 'You are sam'},
        {'role': 'user', 'content': 'Tell me about the siege of Ashenmoor'},
        {'role': 'assistant', 'content': 'I lost my left hand twenty years ago at the Siege of Ashenmoor when a shadow-beast breached the eastern palisade.'},
        {'role': 'user', 'content': 'Why did that happen?'}
    ]
    
    res = _generate_response("Why did that happen?", "sam", CTX, messages)
    diag = res.get("dialogue", "").lower()
    
    # Must explain the causal reason of the siege
    assert any(kw in diag for kw in ["garrison", "supply", "commander", "siege", "reason", "lines"]), (
        f"Continuation failed to inherit siege context: '{diag}'"
    )


def test_sports_and_games_queries():
    """Verify sports and games queries return relevant activity replies, NEVER food / berry pie."""
    sport_queries = ["do you like sports", "do you play sports", "what games do you like to play?"]
    for q in sport_queries:
        res = _generate_response(q, "pip", CTX, [])
        diag = res.get("dialogue", "").lower()
        emotion = res.get("emotion", "")
        # Must talk about games/running/tag/climbing, NOT berry pie or food
        assert "berry pie" not in diag, f"Pip replied about berry pie to sports query '{q}': {diag}"
        assert any(kw in diag for kw in ["game", "play", "run", "fast", "tag", "sport", "tree", "climb"]), (
            f"Pip sports reply missed game/sport keywords: '{diag}'"
        )
        assert emotion in ("happy", "neutral"), f"Pip gave hostile or non-happy emotion for sports: {emotion}"

    # Also test Finn and Sam
    res_finn = _generate_response("do you like sports", "finn", CTX, [])
    assert any(kw in res_finn["dialogue"].lower() for kw in ["run", "sprint", "drill", "scout", "agility", "speed"])
    assert res_finn.get("emotion") in ("happy", "neutral")


def test_emotion_no_false_hostile():
    """Verify that phrases containing words like 'forward', 'courage', 'skills', 'remedies' are never flagged hostile."""
    from npc_talk.nlp.models import predict_emotion
    safe_phrases = [
        "What's your absolute favorite thing that you look forward to every single day?",
        "Finn showed great courage on the ridge.",
        "Eva prepared soothing remedies for the injured traveler.",
        "Sam forged masterwork shields with exquisite skill.",
        "We are moving forward together as friends."
    ]
    for phrase in safe_phrases:
        emo = predict_emotion(phrase)
        assert emo != "angry", f"Phrase falsely classified as angry/hostile: '{phrase}' (got {emo})"


if __name__ == "__main__":
    print("Running conversational regression test suite...")
    test_hunger_queries_all_characters()
    print("[PASS] test_hunger_queries_all_characters")
    test_lost_navigation_all_characters()
    print("[PASS] test_lost_navigation_all_characters")
    test_general_help_all_characters()
    print("[PASS] test_general_help_all_characters")
    test_tired_rest_queries()
    print("[PASS] test_tired_rest_queries")
    test_weather_and_greetings()
    print("[PASS] test_weather_and_greetings")
    test_context_isolation_after_lore_query()
    print("[PASS] test_context_isolation_after_lore_query")
    test_explicit_continuation_still_works()
    print("[PASS] test_explicit_continuation_still_works")
    test_sports_and_games_queries()
    print("[PASS] test_sports_and_games_queries")
    test_emotion_no_false_hostile()
    print("[PASS] test_emotion_no_false_hostile")
    print("\nALL REGRESSION TESTS PASSED 100%!")
