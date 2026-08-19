"""NPC Talk — Dialogue Generation Client with Qwen 2.5 3B Generative Fallback."""
import json
import logging
import os
import random
import re
from pathlib import Path
from typing import Optional, Tuple
from npc_talk import config
from npc_talk.nlp.models import predict_emotion, predict_intent

logger = logging.getLogger(__name__)

# Canonical name aliases
NAME_TO_ID = {
    "ash": "ash", "shadow vex": "ash", "shadow_vex": "ash",
    "finn": "finn", "eva": "eva", "mara cole": "eva", "mara_cole": "eva",
    "sam": "sam", "tabitha": "tabitha", "elder ruth": "tabitha", "ruth": "tabitha",
    "pip": "pip",
}

AI_CHALLENGE_PATTERNS = [
    r"\b(are you|you are|you're)\s+(an?\s+)?(ai|bot|robot|npc|language model|program|computer|machine|synthetic|fake)\b",
    r"\b(are you|you are|you're)\s+(real|human|alive|mortal)\b",
    r"\b(not human|not a human|fake person|inhuman|robot|bot|ai)\b",
    r"\b(prove.*human|why.*scary|look.*robot)\b",
]

HUMAN_DEFENSES = {
    "sam": "Not human?! What kind of tavern madness is that? Feel this beating pulse and my callused hands! I sweat over twelve-hundred-degree coals every morning and bled in the border wars. I am flesh and blood, soldier!",
    "finn": "What?! Look at my scraped knees and messy hair — I'm a real human kid! I run until my lungs burn and get starving hungry every two hours! What made you think I was some kind of machine?!",
    "eva": "Not human? What a strange and feverish thought. I breathe the same air, feel exhaustion after tending the mountain roots, and bleed if pricked by thorns. I am flesh and mortal spirit, traveler.",
    "ash": "Not human? Haha! That's the wildest rumor yet. A machine wouldn't need to pay for tavern mutton, dodge guard patrols, or enjoy fine vintage wine. Beneath this cloak is flesh, bone, and sharp wits.",
    "tabitha": "To look upon an elder and question her humanity is a curious blindness. I have lived seventy-four winters, wept over the graves of kin, and felt the chill in my joints. I am as human as the stone of Thornhaven.",
    "pip": "I'm NOT a robot! Look at my scraped knees, and my tummy rumbles when Mom makes stew! Machines don't eat berry pies or lose baby teeth! I'm eight years old and completely human!",
}

# Lazy-loaded Generative LLM state
_qwen_model = None
_qwen_tokenizer = None


def _get_qwen_engine():
    """Lazily loads local Qwen 2.5 model and tokenizer without external API."""
    global _qwen_model, _qwen_tokenizer
    if not getattr(config, "ENABLE_GENERATIVE_LLM", True):
        return None, None
    if os.getenv("USE_MOCK_LLM", "").strip().lower() in {"1", "true", "yes", "on"}:
        return None, None

    if _qwen_model is None:
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer
        device = "cuda" if torch.cuda.is_available() else "cpu"
        if device == "cpu":
            dtype = torch.float32
            try:
                torch.set_num_threads(min(8, os.cpu_count() or 4))
            except Exception:
                pass
        else:
            dtype = torch.bfloat16 if (torch.cuda.is_available() and torch.cuda.is_bf16_supported()) else torch.float16

        candidates = [
            getattr(config, "GENERATIVE_LLM_MODEL", "Qwen/Qwen2.5-3B-Instruct"),
            "Qwen/Qwen2.5-3B-Instruct",
            "Qwen/Qwen2.5-1.5B-Instruct"
        ]

        for model_name in candidates:
            # Try offline local cache first for instant load
            for local_only in [True, False]:
                try:
                    logger.info("Initializing Local Generative LLM (%s, local_only=%s)...", model_name, local_only)
                    _qwen_tokenizer = AutoTokenizer.from_pretrained(
                        model_name,
                        trust_remote_code=True,
                        local_files_only=local_only
                    )
                    _qwen_model = AutoModelForCausalLM.from_pretrained(
                        model_name,
                        dtype=dtype,
                        low_cpu_mem_usage=True,
                        trust_remote_code=True,
                        local_files_only=local_only
                    ).to(device)
                    _qwen_model.eval()
                    logger.info("Successfully loaded Local LLM %s on %s (%s).", model_name, device, dtype)
                    break
                except Exception as e:
                    _qwen_model = None
                    _qwen_tokenizer = None
            if _qwen_model is not None:
                break

        if _qwen_model is None:
            _qwen_model = False
            _qwen_tokenizer = False

    return (_qwen_model if _qwen_model is not False else None), (_qwen_tokenizer if _qwen_tokenizer is not False else None)


def _generate_with_qwen(user_text: str, npc_id: str, ctx: dict, messages: list[dict]) -> Optional[dict]:
    """Generates dialogue using Qwen 2.5 3B-Instruct with full character grounding."""
    model, tokenizer = _get_qwen_engine()
    if model is None or tokenizer is None:
        return None

    try:
        from npc_talk.personas.load_persona import load_persona, load_all_characters_summary
        persona = load_persona(npc_id)
        p_name = ctx.get("player_name", "Traveler")
        p_age = ctx.get("player_age", 22)
        p_gender = ctx.get("player_gender", "male")
        p_occupation = ctx.get("player_occupation", "adventurer")
        location = ctx.get("location", "village_square").replace("_", " ")
        time_of_day = ctx.get("time_of_day", "day")
        rep = ctx.get("reputation", 0)

        # Build specific character relationships
        relationships_dict = persona.get("relationships", {})
        rel_text = "\n".join(f"- {target.capitalize()}: {desc}" for target, desc in relationships_dict.items()) if relationships_dict else "None noted."
        all_chars_summary = load_all_characters_summary()

        # Extract memories and active quests from system message if present
        system_text = messages[0]["content"] if messages and messages[0].get("role") == "system" else ""
        mem_match = re.search(r"## Relevant Memories\n(.*?)(?=\n##|\Z)", system_text, re.DOTALL)
        memories_text = mem_match.group(1).strip() if mem_match else ""

        quest_match = re.search(r"Active quests:\s*([^\.\n]+)", system_text, re.IGNORECASE)
        active_quests = quest_match.group(1).strip() if quest_match else "None"

        rep_label = "trusted ally" if rep >= 5 else "friendly" if rep >= 2 else "neutral" if rep >= 0 else "wary" if rep >= -2 else "hostile"

        system_instruction = (
            f"You are {persona['name']}, {persona.get('title', 'a resident of Thornhaven')}.\n\n"
            f"=== YOUR PROFILE ===\n"
            f"Backstory: {persona.get('backstory', '')}\n"
            f"Personality: {', '.join(persona.get('personality_traits', []))}\n"
            f"Speech Style: {persona.get('speech_style', '')}\n"
            f"Goals: {'; '.join(persona.get('goals', []))}\n\n"
            f"=== YOUR RELATIONSHIPS WITH OTHER CHARACTERS ===\n"
            f"{rel_text}\n\n"
            f"=== WORLD CONTEXT: ALL CHARACTERS IN THORNHAVEN ===\n"
            f"{all_chars_summary}\n\n"
            f"=== SETTING & GAME STATE ===\n"
            f"Location: {location} | Time of Day: {time_of_day}\n"
            f"Speaking to: {p_name} (a {p_age}-year-old {p_gender} {p_occupation})\n"
            f"Player Reputation: {rep_label} ({rep:+d})\n"
            f"Active Quests: {active_quests}\n"
        )
        if memories_text and memories_text != "None":
            system_instruction += f"\n=== RELEVANT MEMORIES ===\n{memories_text}\n"

        system_instruction += (
            "\n=== INSTRUCTIONS ===\n"
            "1. Answer directly and precisely based on what the player just asked or said.\n"
            "2. Stay strictly in-character as a fantasy NPC in the world of Thornhaven.\n"
            "3. If the player asks about another character (Sam, Ash, Eva, Tabitha, Finn, Pip), use your authentic relationships and knowledge of them.\n"
            "4. If asked about modern, out-of-world, or unfamiliar concepts (technology, science, pop culture, crypto, etc.), react authentically in-character with curiosity, skepticism, confusion, or fantasy reasoning in your distinct voice.\n"
            "5. Respond naturally in 1 to 3 spoken sentences in your distinct voice. Do NOT include action tags like *smiles* or character name prefixes like 'Ash:'."
        )

        chat_history = [{"role": "system", "content": system_instruction}]

        # Include recent conversational context
        for m in messages[-4:]:
            if m.get("role") in ("user", "assistant") and m.get("content"):
                chat_history.append({"role": m["role"], "content": m["content"]})

        if not chat_history or chat_history[-1].get("content") != user_text:
            chat_history.append({"role": "user", "content": user_text})

        text_input = tokenizer.apply_chat_template(
            chat_history,
            tokenize=False,
            add_generation_prompt=True
        )

        import torch
        device = next(model.parameters()).device
        model_inputs = tokenizer([text_input], return_tensors="pt").to(device)

        max_tokens = min(getattr(config, "GENERATIVE_MAX_NEW_TOKENS", 50), 50)
        temp = getattr(config, "GENERATIVE_TEMPERATURE", 0.7)
        top_p = getattr(config, "GENERATIVE_TOP_P", 0.9)

        with torch.no_grad():
            generated_ids = model.generate(
                **model_inputs,
                max_new_tokens=max_tokens,
                temperature=temp,
                top_p=top_p,
                repetition_penalty=1.1,
                do_sample=True,
                pad_token_id=tokenizer.eos_token_id
            )

        input_len = model_inputs.input_ids.shape[1]
        output_ids = generated_ids[0][input_len:]
        dialogue = tokenizer.decode(output_ids, skip_special_tokens=True).strip()

        # Clean dialogue
        dialogue = re.sub(r'^(Ash|Sam|Eva|Tabitha|Finn|Pip):\s*', '', dialogue, flags=re.IGNORECASE).strip()
        dialogue = dialogue.strip('"\'')

        if dialogue:
            emotion = predict_emotion(dialogue) or "neutral"
            return {
                "dialogue": dialogue,
                "emotion": emotion,
                "action": "none",
                "action_params": {},
                "model_source": "qwen2.5-3b-instruct",
                "tier": 5,
                "routing_reason": "qwen2.5-3b-instruct"
            }
    except Exception as e:
        logger.warning("Qwen generation error: %s", e)

    return None


def _detect_npc_id(system_prompt: str) -> str:
    m = re.search(r"You are ([^,\.\n]+)", system_prompt, re.IGNORECASE)
    if m:
        name = m.group(1).strip().lower()
        if name in NAME_TO_ID:
            return NAME_TO_ID[name]
        for k, v in NAME_TO_ID.items():
            if k in name:
                return v
    for k, v in NAME_TO_ID.items():
        if k in system_prompt.lower():
            return v
    return "ash"


def _extract_context(system_prompt: str) -> dict:
    ctx = {
        "time_of_day": "day", "location": "village_square", "reputation": 0,
        "player_name": "Traveler", "player_gender": "male", "player_age": 22,
        "player_age_group": "adult", "player_occupation": "adventurer",
    }
    for tod in ["dawn", "morning", "day", "dusk", "evening", "night"]:
        if tod in system_prompt.lower():
            ctx["time_of_day"] = tod
            break

    loc_m = re.search(r"You are in the ([^\.\n]+)", system_prompt, re.IGNORECASE)
    if loc_m:
        ctx["location"] = loc_m.group(1).strip().lower().replace(" ", "_")

    rep_m = re.search(r"reputation[^:]*:\s*[^\(]*\(([+-]?\d+)\)", system_prompt, re.IGNORECASE)
    if rep_m:
        ctx["reputation"] = int(rep_m.group(1))

    prof_m = re.search(r"The player is ([^,]+),\s*a (\d+)-year-old (\w+)\s+([^\(\n\.]+)", system_prompt, re.IGNORECASE)
    if prof_m:
        ctx["player_name"] = prof_m.group(1).strip()
        ctx["player_age"] = int(prof_m.group(2))
        ctx["player_gender"] = prof_m.group(3).strip().lower()
        ctx["player_occupation"] = prof_m.group(4).strip().lower()

    return ctx


def _generate_response(user_text: str, npc_id: str, ctx: dict, messages: list[dict]) -> dict:
    from npc_talk.agent.conversational_engine import normalize_text, match_conversational_intent
    normalized_text = normalize_text(user_text)
    lower = normalized_text.lower().strip()
    p_name = ctx.get("player_name", "Traveler")

    # 1. Humanity / Turing challenge
    if any(re.search(p, lower) for p in AI_CHALLENGE_PATTERNS):
        logger.info("[Tier 1: Humanity Guardrails] Handled query for NPC '%s' (matched Turing challenge pattern)", npc_id)
        reply = HUMAN_DEFENSES.get(npc_id, HUMAN_DEFENSES["ash"])
        return {
            "dialogue": reply,
            "action": "none",
            "action_params": {},
            "emotion": "angry" if npc_id in ("sam", "pip") else "suspicious",
            "tier": 1,
            "routing_reason": "turing_challenge_match"
        }

    # 2. Conversational & Pragmatic Intent Engine (Accusations, identity, quests, physical needs, navigation, greetings, small talk)
    try:
        conv_res = match_conversational_intent(normalized_text, npc_id, player_name=p_name)
        if conv_res:
            logger.info("[Tier 2: Pragmatic Intent] Handled query for NPC '%s' (intent='%s')", npc_id, conv_res.get("conversational_intent"))
            conv_res["tier"] = 2
            conv_res["routing_reason"] = f"conversational_intent:{conv_res.get('conversational_intent')}"
            return conv_res
    except Exception as e:
        logger.warning("Conversational engine error: %s", e)

    # 3. Deep Semantic Narrative Engine Concept Match (Dense Embeddings + Keyword N-Gram)
    try:
        from npc_talk.agent.narrative_engine import retrieve_best_narrative_concept, synthesize_deep_dialogue_response
        concept, score, discourse_intent = retrieve_best_narrative_concept(normalized_text, npc_id, messages)
        if concept and score >= 3.0:
            logger.info("[Tier 3: Narrative Retrieval] Handled query for NPC '%s' (concept='%s', score=%.2f, discourse='%s')", npc_id, concept.get("id"), score, discourse_intent)
            narr_res = synthesize_deep_dialogue_response(concept, discourse_intent, npc_id, ctx, len(messages) >= 3)
            narr_res["tier"] = 3
            narr_res["routing_reason"] = f"narrative_concept:{concept.get('id')}(score={score:.2f})"
            return narr_res
        else:
            logger.debug("[Tier 3: Narrative Retrieval] Skipped (concept=%s, score=%.2f < 3.0)", concept.get("id") if concept else None, score)
    except Exception as e:
        logger.warning("Narrative engine check error: %s", e)

    # 4. ML Intent Classifier — content-verified triggers
    intent = predict_intent(normalized_text, npc_id, confidence_threshold=0.35)
    if intent and intent.get("responses"):
        logger.info("[Tier 4: ML Intent Classifier] Handled query for NPC '%s' (intent='%s', confidence=%.2f)", npc_id, intent.get("id"), intent.get("confidence", 0.0))
        resp_text = random.choice(intent["responses"])
        return {
            "dialogue": resp_text,
            "action": intent.get("action", "none"),
            "action_params": intent.get("action_params", {}),
            "emotion": intent.get("emotion") or predict_emotion(resp_text) or "neutral",
            "tier": 4,
            "routing_reason": f"ml_intent:{intent.get('id')}(conf={intent.get('confidence', 0.0):.2f})"
        }
    else:
        logger.debug("[Tier 4: ML Intent Classifier] Skipped (no intent passed confidence and trigger validation)")

    # 5. Generative LLM Fallback (Qwen 2.5 3B-Instruct) — triggers when question is not in narrative engine/intents
    logger.info("[Tier 5: Generative Fallback] Attempting Qwen 2.5 3B generative fallback for NPC '%s'", npc_id)
    qwen_response = _generate_with_qwen(normalized_text, npc_id, ctx, messages)
    if qwen_response:
        logger.info("[Tier 5: Generative Fallback] Successfully generated response with Qwen 2.5 3B for NPC '%s'", npc_id)
        return qwen_response
    else:
        logger.warning("[Tier 5: Generative Fallback] Qwen 2.5 3B unavailable or returned None; falling to Tier 6")

    # 6. In-character dynamic topical generator (Deterministic Safety Fallback)
    logger.info("[Tier 6: Topical Safety Fallback] Generating deterministic safety fallback for NPC '%s'", npc_id)
    topic_words = [w for w in re.findall(r"\b\w+\b", lower) if len(w) > 2 and w not in {
        "what", "tell", "about", "your", "have", "that", "with", "this", "from", "know",
        "does", "when", "where", "will", "would", "could", "should", "there", "then",
        "than", "they", "them", "their", "some", "like", "just", "much", "many", "think",
        "feel", "look", "come", "went", "into", "also", "very", "more", "most", "been",
        "are", "the", "and", "for", "you", "who", "why", "how", "can", "did", "was", "were",
        "please", "really", "thing", "things", "said", "says", "want", "give", "make"
    }]
    topic_hint = " ".join(topic_words[:2]) if topic_words else ""

    topic_responses = {
        "ash": (
            f"You're asking about {topic_hint}, {p_name}? Out here in Thornhaven, everything has a story and an angle. If there's valuable intelligence or profit in it, my network can look into it. What's your real angle here?" if topic_hint else
            f"Information is the only true currency in a divided realm. Keep your eyes sharp around Thornhaven, {p_name}."
        ),
        "finn": (
            f"Whoa, {topic_hint}?! I haven't spotted anything about that on my scouting ridge patrols yet, {p_name}! But I'm writing that down in my scouting notebook right now and I'll keep an eye out!" if topic_hint else
            f"I know every trail and rooftop in Thornhaven, {p_name}! Always keep your boots laced and watch the trees!"
        ),
        "eva": (
            f"That is a curious thought regarding {topic_hint}, {p_name}. While my grandmother's herbal folios don't specifically detail that, nature always has its own subtle wisdom. Let me know if you need any remedies or rest while you ponder it." if topic_hint else
            f"Nature provides a remedy for those who seek with patience, {p_name}. Be mindful of where you tread."
        ),
        "sam": (
            f"Asking about {topic_hint}, {p_name}? Down at the forge, I focus on practical things: folded steel, balanced hilts, and sturdy shields. If it helps defend this valley or forge honest iron, I'm listening." if topic_hint else
            f"Words mean nothing without honest steel behind them, {p_name}. Keep your blade sharp and your armor intact."
        ),
        "tabitha": (
            f"The mysteries of {topic_hint} reach far, {p_name}. In seventy-four winters of transcribing the ancient chronicles of Thornhaven, every inquiry reveals how much of the world remains to be understood. Walk thoughtfully on your journey." if topic_hint else
            f"The ancient chronicles remember all who walk this valley, {p_name}. Every question carries a history."
        ),
        "pip": (
            f"Ooh! {topic_hint.capitalize()}?! Is that something sparkly, or does it make a cool sound?! Tell me more, {p_name}, I love collecting new stories almost as much as shiny river stones!" if topic_hint else
            f"Ooh! That sounds super exciting, {p_name}! Look at this shiny rock I found by the river yesterday!"
        ),
    }
    dialogue = topic_responses.get(npc_id, f"Welcome to Thornhaven, {p_name}. How can I assist you today?")
    emotion = predict_emotion(dialogue) or "neutral"
    return {
        "dialogue": dialogue,
        "action": "none",
        "action_params": {},
        "emotion": emotion,
        "tier": 6,
        "routing_reason": "deterministic_topical_safety_fallback"
    }


def generate(messages: list[dict], **kwargs) -> str:
    system_text = ""
    user_text = ""
    for msg in messages:
        if msg.get("role") == "system":
            system_text = msg.get("content", "")
        elif msg.get("role") == "user":
            user_text = msg.get("content", "")

    npc_id = _detect_npc_id(system_text)
    ctx = _extract_context(system_text)
    resp = _generate_response(user_text, npc_id, ctx, messages)
    return json.dumps(resp)
