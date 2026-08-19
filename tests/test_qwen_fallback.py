"""
Test suite verifying Qwen 2.5 3B Generative LLM fallback integration and 6-tier routing.
"""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from npc_talk.llm.client import _generate_response
from npc_talk import config

CTX = {
    'player_name': 'Valen',
    'player_occupation': 'adventurer',
    'player_age': 25,
    'player_age_group': 'adult',
    'player_gender': 'male',
    'reputation': 0,
}


def test_indomain_queries_skip_llm():
    """Verify in-domain narrative, intent, and conversational queries resolve in Tiers 1-4 without invoking Tier 5."""
    # Tier 1: Turing / Humanity challenge
    res_turing = _generate_response("are you a robot or an ai?", "ash", CTX, [])
    assert res_turing.get("tier") == 1, f"Turing challenge failed to route to Tier 1: {res_turing}"
    print("[PASS] Tier 1: Turing challenge guardrail resolved deterministically.")

    # Tier 2: Conversational / Pragmatic intent (accusation)
    res_thief = _generate_response("you are a thief", "ash", CTX, [])
    assert res_thief.get("tier") == 2, f"Thief accusation failed to route to Tier 2: {res_thief}"
    assert "conversational_intent" in res_thief or "relocated" in res_thief.get("dialogue", "").lower()
    print("[PASS] Tier 2: Thief accusation resolved via pragmatic engine.")

    # Tier 2: Quest lead
    res_ruins = _generate_response("I want a safe path for the ancient ruins", "ash", CTX, [])
    assert res_ruins.get("tier") == 2, f"Ruins safe path failed to route to Tier 2: {res_ruins}"
    assert res_ruins.get("action") == "start_quest"
    print("[PASS] Tier 2: Ruins safe path resolved via quest engine.")

    # Tier 3: Narrative Concept Retrieval (Sam Ashenmoor siege)
    res_lore = _generate_response("Tell me about the Siege of Ashenmoor and your lost hand", "sam", CTX, [])
    assert res_lore.get("tier") == 3, f"Lore query failed to route to Tier 3: {res_lore}"
    assert "ashenmoor" in res_lore.get("dialogue", "").lower()
    print("[PASS] Tier 3: Narrative concept retrieval resolved via dense embeddings/keywords.")

    # Tier 4: Content-verified ML Intent Classifier (Sam blade repair)
    res_repair = _generate_response("Can you inspect and sharpen my steel blade?", "sam", CTX, [])
    assert res_repair.get("tier") == 4, f"Blade repair query failed to route to Tier 4: {res_repair}"
    print("[PASS] Tier 4: Blade repair query resolved via ML intent classifier.")


def test_outofdomain_queries_route_to_tier5():
    """Verify novel/out-of-domain questions across all 6 personas route to Tier 5 Qwen 2.5 3B."""
    novel_queries = [
        ("sam", "What do you think about quantum physics and time machines?"),
        ("ash", "Can you explain how a smartphone works?"),
        ("pip", "What is an airplane?"),
        ("eva", "Do you know any music by modern pop singers?"),
        ("tabitha", "What would you do with a million cryptocurrency tokens?"),
        ("finn", "What do you think of space exploration and rocket ships?"),
    ]

    for npc, query in novel_queries:
        messages = [{"role": "system", "content": f"You are {npc}"}, {"role": "user", "content": query}]
        res = _generate_response(query, npc, CTX, messages)
        tier = res.get("tier")
        diag = res.get("dialogue", "")
        emotion = res.get("emotion", "")
        model_source = res.get("model_source")

        assert tier == 5, f"[{npc.upper()}] Expected Tier 5 fallback, got Tier {tier} (routing_reason={res.get('routing_reason')}): '{diag}'"
        assert model_source == "qwen2.5-3b-instruct", f"[{npc.upper()}] Expected model_source='qwen2.5-3b-instruct', got {model_source}"
        assert len(diag) > 10, f"[{npc.upper()}] Dialogue too short for novel query: {query}"
        assert emotion in ("neutral", "happy", "angry", "sad", "suspicious", "surprised", "thinking")
        print(f"[PASS] [{npc.upper()}] Novel Query: '{query}' -> Handled by Tier 5 ({model_source}, len={len(diag)}, emotion={emotion})")


def test_safety_fallback_tier6_when_llm_disabled():
    """Verify Tier 6 safety fallback activates if Tier 5 is disabled."""
    os.environ["USE_MOCK_LLM"] = "1"
    try:
        res = _generate_response("What is an alien spacecraft from another galaxy?", "sam", CTX, [])
        assert res.get("tier") == 6, f"Expected Tier 6 safety fallback when LLM disabled, got Tier {res.get('tier')}"
        assert len(res.get("dialogue", "")) > 10
        print("[PASS] Tier 6 safety fallback activates correctly when Generative LLM is disabled.")
    finally:
        os.environ.pop("USE_MOCK_LLM", None)


if __name__ == "__main__":
    print("=== Testing Qwen Fallback & NLP Routing ===")
    test_indomain_queries_skip_llm()
    test_safety_fallback_tier6_when_llm_disabled()
    test_outofdomain_queries_route_to_tier5()
    print("\nALL QWEN FALLBACK AND ROUTING TESTS PASSED!")

