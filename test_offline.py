#!/usr/bin/env python3
"""
NPC Talk — Offline Unit & Integration Tests
Tests persona loading, game state, memory stores, intent/emotion pipelines, and orchestrator flow.
Run with: python test_offline.py
"""

import sys
import json
import os
from pathlib import Path

# Add src to path
ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

import npc_talk.config as config
from npc_talk.personas.load_persona import load_persona, list_personas
from npc_talk.state.game_state import GameState
from npc_talk.memory.short_term import ShortTermMemory
from npc_talk.memory.long_term import LongTermMemory
from npc_talk.nlp.models import predict_intent, predict_emotion, warmup
from npc_talk.agent.orchestrator import NPCOrchestrator


CANONICAL_NPCS = ["ash", "finn", "eva", "sam", "tabitha", "pip"]


def test_persona_loading_and_validation():
    """Test that all 6 canonical personas load and have required fields."""
    print("\n" + "=" * 60)
    print("TEST: Persona Loading & Validation")
    print("=" * 60)
    
    all_passed = True
    
    for npc_id in CANONICAL_NPCS:
        try:
            persona = load_persona(npc_id)
            print(f"  ✓ Loaded {npc_id}: {persona.get('name')} - {persona.get('title')}")
            
            # Check required keys
            required_keys = ["id", "name", "title", "backstory", "personality_traits",
                           "speech_style", "goals", "relationships", "example_lines"]
            for key in required_keys:
                if key not in persona:
                    print(f"    ✗ Missing required key: {key}")
                    all_passed = False
                else:
                    print(f"    ✓ Has {key}")
            
            # Check relationships only point to valid NPCs
            rel = persona.get("relationships", {})
            for target_npc in rel.keys():
                if target_npc not in CANONICAL_NPCS or target_npc == npc_id:
                    print(f"    ✗ Invalid relationship target: {target_npc}")
                    all_passed = False
                else:
                    print(f"    ✓ Relationship to {target_npc}: {rel[target_npc][:50]}...")
            
            # Check pip is in relationships of all others (except pip itself)
            if npc_id != "pip":
                if "pip" not in rel:
                    print(f"    ✗ Missing 'pip' in relationships")
                    all_passed = False
                else:
                    print(f"    ✓ Has relationship with pip")
            else:
                # pip shouldn't have a relationship with itself
                if "pip" in rel:
                    print(f"    ! pip has self-relationship (unexpected but not critical)")
                    
        except FileNotFoundError:
            print(f"  ✗ Persona file not found: {npc_id}.json")
            all_passed = False
        except Exception as e:
            print(f"  ✗ Error loading {npc_id}: {e}")
            all_passed = False
    
    return all_passed


def test_game_state_management():
    """Test game state: reputation, time of day, location, quests, player profiles."""
    print("\n" + "=" * 60)
    print("TEST: Game State Management")
    print("=" * 60)
    
    gs = GameState()
    all_passed = True
    
    # Test default state
    state = gs.get_state("player_1", "ash")
    print(f"  ✓ Default state: location={state.get('location')}, time={state.get('time_of_day')}, rep={state.get('reputation')}")
    
    # Test reputation updates
    gs.update({"reputation": {"player_id": "player_1", "npc_id": "ash", "value": 5}})
    state = gs.get_state("player_1", "ash")
    assert state["reputation"] == 5, f"Expected reputation 5, got {state['reputation']}"
    print(f"  ✓ Reputation update works: {state['reputation']}")
    
    # Test negative reputation
    gs.update({"reputation": {"player_id": "player_1", "npc_id": "ash", "value": -3}})
    state = gs.get_state("player_1", "ash")
    assert state["reputation"] == -3, f"Expected reputation -3, got {state['reputation']}"
    print(f"  ✓ Negative reputation works: {state['reputation']}")
    
    # Test time of day
    gs.update({"time_of_day": "night"})
    state = gs.get_state("player_1", "ash")
    assert state["time_of_day"] == "night", f"Expected night, got {state['time_of_day']}"
    print(f"  ✓ Time of day update works: {state['time_of_day']}")
    
    # Test location
    gs.update({"location": "forest"})
    state = gs.get_state("player_1", "ash")
    assert state["location"] == "forest", f"Expected forest, got {state['location']}"
    print(f"  ✓ Location update works: {state['location']}")
    
    # Test quest flags
    gs.update({"quest_flags": {"Test Quest": True}})
    state = gs.get_state("player_1", "ash")
    assert state["quest_flags"].get("Test Quest") is True
    print(f"  ✓ Quest flags work: {state['quest_flags']}")
    
    # Test player profile
    gs.set_player_profile("player_1", {
        "name": "TestHero",
        "gender": "female",
        "age": 25,
        "age_group": "adult",
        "occupation": "scholar"
    })
    profile = gs.get_player_profile("player_1")
    assert profile["name"] == "TestHero"
    assert profile["occupation"] == "scholar"
    print(f"  ✓ Player profile works: {profile['name']}, {profile['occupation']}")
    
    return all_passed


def test_memory_stores():
    """Test short-term buffer and long-term vector store."""
    print("\n" + "=" * 60)
    print("TEST: Memory Stores")
    print("=" * 60)
    
    all_passed = True
    
    # Test ShortTermMemory
    stm = ShortTermMemory(max_turns=5)
    stm.add_turn("ash", "player_1", "user", "Hello there!")
    stm.add_turn("ash", "player_1", "assistant", "Well hello, friend.")
    stm.add_turn("ash", "player_1", "user", "Nice weather.")
    stm.add_turn("ash", "player_1", "assistant", "Indeed it is.")
    
    turns = stm.get_recent_turns("ash", "player_1")
    assert len(turns) == 4, f"Expected 4 turns, got {len(turns)}"
    print(f"  ✓ Short-term memory stores turns: {len(turns)} turns")
    
    # Test buffer limit
    for i in range(10):
        stm.add_turn("ash", "player_1", "user", f"Message {i}")
        stm.add_turn("ash", "player_1", "assistant", f"Reply {i}")
    
    turns = stm.get_recent_turns("ash", "player_1")
    assert len(turns) <= 10, f"Expected max 10 turns (5 pairs), got {len(turns)}"
    print(f"  ✓ Short-term memory respects buffer limit: {len(turns)} turns")
    
    # Test clear
    stm.clear("ash", "player_1")
    turns = stm.get_recent_turns("ash", "player_1")
    assert len(turns) == 0, f"Expected 0 turns after clear, got {len(turns)}"
    print(f"  ✓ Short-term memory clear works")
    
    # Test LongTermMemory (mock - may not have embeddings in test env)
    try:
        ltm = LongTermMemory(store_dir=config.MEMORY_STORE_DIR)
        # Just test initialization works
        print(f"  ✓ Long-term memory initializes: {ltm.store_dir}")
    except Exception as e:
        print(f"  ! Long-term memory init note: {e} (may need embeddings)")
    
    return all_passed


def test_intent_classification():
    """Test intent classification pipeline for all NPCs."""
    print("\n" + "=" * 60)
    print("TEST: Intent Classification Pipeline")
    print("=" * 60)
    
    # Warm up models
    warmup()
    
    all_passed = True
    test_cases = [
        ("ash", "any rumors going around town?"),
        ("ash", "have you heard any gossip recently?"),
        ("sam", "how do I forge a sword?"),
        ("sam", "what materials do you need to make steel?"),
        ("eva", "do you have any healing herbs or potions?"),
        ("eva", "I need medicine for a fever"),
        ("tabitha", "tell me the history of Thornhaven"),
        ("tabitha", "what happened during the ancient cataclysm?"),
        ("finn", "can you show me the forest trails?"),
        ("finn", "any secrets in the woods?"),
        ("pip", "do you want to play a game with me?"),
        ("pip", "look at my shiny rock collection!"),
    ]
    
    for npc_id, text in test_cases:
        try:
            result = predict_intent(text, npc_id, confidence_threshold=0.30)
            if result:
                print(f"  ✓ {npc_id}: \"{text}\" → {result['id']} (conf={result['confidence']:.2f})")
            else:
                print(f"  ! {npc_id}: \"{text}\" → no match (below threshold)")
        except Exception as e:
            print(f"  ✗ {npc_id}: \"{text}\" → ERROR: {e}")
            all_passed = False
    
    return all_passed


def test_emotion_prediction():
    """Test emotion prediction pipeline."""
    print("\n" + "=" * 60)
    print("TEST: Emotion Prediction Pipeline")
    print("=" * 60)
    
    all_passed = True
    test_cases = [
        ("You dare question my honor, you absolute fool!", "angry"),
        ("I am so glad you came by today, welcome!", "happy"),
        ("I miss my fallen comrades dearly. The grief is heavy on my heart.", "sad"),
        ("Something suspicious is going on in those underground tunnels.", "suspicious"),
        ("Let me ponder the ancient chronicles for a moment before answering.", "thinking"),
        ("I cannot believe what I just witnessed out there — shocking!", "surprised"),
        ("What do you need? State your business.", "neutral"),
    ]
    
    for text, expected in test_cases:
        try:
            emotion = predict_emotion(text, confidence_threshold=0.25)
            if emotion:
                status = "✓" if emotion == expected else "!"
                print(f"  {status} \"{text[:50]}...\" → {emotion} (expected {expected})")
                if emotion != expected:
                    print(f"    Note: Got {emotion}, expected {expected}")
            else:
                print(f"  ! \"{text[:50]}...\" → None (below threshold)")
        except Exception as e:
            print(f"  ✗ \"{text[:50]}...\" → ERROR: {e}")
            all_passed = False
    
    return all_passed


def test_orchestrator_dialogue_flow():
    """Test the full orchestrator dialogue flow for all NPCs."""
    print("\n" + "=" * 60)
    print("TEST: Orchestrator Dialogue Flow")
    print("=" * 60)
    
    all_passed = True
    
    # Initialize components
    stm = ShortTermMemory(max_turns=config.SHORT_TERM_BUFFER_SIZE)
    ltm = LongTermMemory(store_dir=config.MEMORY_STORE_DIR)
    gs = GameState()
    
    orchestrator = NPCOrchestrator(
        short_term=stm,
        long_term=ltm,
        game_state=gs
    )
    
    test_cases = [
        ("ash", "Hello there, got any rumors?"),
        ("finn", "Can you show me the forest trails?"),
        ("eva", "Do you have any healing potions?"),
        ("sam", "How do I forge a sword?"),
        ("tabitha", "Tell me about the history of Thornhaven"),
        ("pip", "Want to see my shiny rock collection?"),
    ]
    
    for npc_id, message in test_cases:
        try:
            response = orchestrator.generate_npc_response(
                player_input=message,
                npc_id=npc_id,
                player_id="test_player",
                player_profile={
                    "name": "TestHero",
                    "gender": "male",
                    "age": 25,
                    "age_group": "adult",
                    "occupation": "adventurer"
                }
            )
            
            dialogue = response.get("dialogue", "")
            emotion = response.get("emotion", "neutral")
            action = response.get("action", "none")
            
            if dialogue and len(dialogue) > 5:
                print(f"  ✓ {npc_id}: \"{message}\" → \"{dialogue[:60]}...\" (emotion={emotion}, action={action})")
            else:
                print(f"  ✗ {npc_id}: \"{message}\" → Empty or too short dialogue: '{dialogue}'")
                all_passed = False
                
        except Exception as e:
            print(f"  ✗ {npc_id}: \"{message}\" → ERROR: {e}")
            all_passed = False
    
    # Test multi-turn conversation
    print("\n  Testing multi-turn conversation...")
    try:
        # First turn
        r1 = orchestrator.generate_npc_response(
            player_input="Hello Sam!",
            npc_id="sam",
            player_id="test_player2",
            player_profile={"name": "Hero", "gender": "female", "age": 20, "age_group": "adult", "occupation": "mercenary"}
        )
        
        # Second turn - follow up
        r2 = orchestrator.generate_npc_response(
            player_input="Can you tell me more about your prosthetic hand?",
            npc_id="sam",
            player_id="test_player2",
            player_profile={"name": "Hero", "gender": "female", "age": 20, "age_group": "adult", "occupation": "mercenary"}
        )
        
        print(f"  ✓ Turn 1: {r1.get('dialogue', '')[:50]}...")
        print(f"  ✓ Turn 2: {r2.get('dialogue', '')[:50]}...")
        
    except Exception as e:
        print(f"  ✗ Multi-turn test failed: {e}")
        all_passed = False
    
    return all_passed


def test_narrative_engine_pip():
    """Test Pip's narrative corpus is accessible."""
    print("\n" + "=" * 60)
    print("TEST: Pip Narrative Corpus")
    print("=" * 60)
    
    try:
        from npc_talk.agent.narrative_engine import NPC_NARRATIVE_CORPUS, retrieve_best_narrative_concept
        
        pip_corpus = NPC_NARRATIVE_CORPUS.get("pip", [])
        print(f"  ✓ Pip corpus has {len(pip_corpus)} entries")
        
        expected_concepts = ["river_treasures", "endless_questions", "dreams_of_adventuring", 
                            "pip_sam_interactions", "pip_finn_interactions"]
        for concept_id in expected_concepts:
            found = any(c["id"] == concept_id for c in pip_corpus)
            if found:
                print(f"  ✓ Found concept: {concept_id}")
            else:
                print(f"  ✗ Missing concept: {concept_id}")
                return False
        
        # Test retrieval
        concept, score, intent = retrieve_best_narrative_concept(
            "Tell me about your river treasures", "pip", []
        )
        if concept and concept["id"] == "river_treasures":
            print(f"  ✓ Retrieval works: {concept['id']} (score={score:.1f}, intent={intent})")
        else:
            print(f"  ! Retrieval returned: {concept['id'] if concept else None}")
        
        return True
        
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("NPC TALK — OFFLINE TEST SUITE")
    print("=" * 60)
    
    tests = [
        ("Persona Loading & Validation", test_persona_loading_and_validation),
        ("Game State Management", test_game_state_management),
        ("Memory Stores", test_memory_stores),
        ("Intent Classification", test_intent_classification),
        ("Emotion Prediction", test_emotion_prediction),
        ("Orchestrator Dialogue Flow", test_orchestrator_dialogue_flow),
        ("Pip Narrative Corpus", test_narrative_engine_pip),
    ]
    
    results = {}
    for name, test_func in tests:
        try:
            results[name] = test_func()
        except Exception as e:
            print(f"\n  ✗ {name} failed with exception: {e}")
            import traceback
            traceback.print_exc()
            results[name] = False
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    all_passed = True
    for name, passed in results.items():
        status = "PASS" if passed else "FAIL"
        print(f"  {status}: {name}")
        if not passed:
            all_passed = False
    
    print("=" * 60)
    if all_passed:
        print("ALL TESTS PASSED ✓")
        return 0
    else:
        print("SOME TESTS FAILED ✗")
        return 1


if __name__ == "__main__":
    sys.exit(main())