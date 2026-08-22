"""
NPC Talk — Persona Loader
Loads NPC character cards from JSON and formats them into system prompts.
"""

import json
import re
from pathlib import Path

from npc_talk import config


VALID_NPC_ID = re.compile(r"^[a-z0-9_-]+$")


def load_persona(npc_id: str) -> dict:
    """
    Load a persona JSON file by NPC id.
    Also loads any dataset-sourced example lines and merges them in.
    """
    if not isinstance(npc_id, str) or not VALID_NPC_ID.fullmatch(npc_id):
        raise FileNotFoundError(f"Invalid NPC id: {npc_id!r}")

    persona_path = Path(config.PERSONAS_DIR) / f"{npc_id}.json"
    if not persona_path.exists():
        raise FileNotFoundError(f"Persona file not found: {persona_path}")

    with open(persona_path, "r", encoding="utf-8") as fh:
        persona = json.load(fh)

    # Merge in dataset-sourced example lines if they exist
    dataset_lines_path = Path(config.DATA_PROCESSED_DIR) / f"{npc_id}_lines.json"
    if dataset_lines_path.exists():
        with open(dataset_lines_path, "r", encoding="utf-8") as fh:
            dataset = json.load(fh)
        if dataset.get("lines"):
            persona["example_lines"] = dataset["lines"]

    return persona


def format_system_prompt(persona: dict) -> str:
    """
    Convert a persona dict into a rich system prompt for the LLM.
    """
    lines = []
    lines.append(f"You are {persona['name']}, {persona.get('title', 'an NPC')}.")
    lines.append("")

    # Backstory
    if persona.get("backstory"):
        lines.append(f"## Backstory\n{persona['backstory']}")
        lines.append("")

    # Personality
    if persona.get("personality_traits"):
        traits = ", ".join(persona["personality_traits"])
        lines.append(f"## Personality Traits\n{traits}")
        lines.append("")

    # Speech style
    if persona.get("speech_style"):
        lines.append(f"## Speech Style\n{persona['speech_style']}")
        lines.append("")

    # Goals
    if persona.get("goals"):
        goals_str = "\n".join(f"- {g}" for g in persona["goals"])
        lines.append(f"## Current Goals\n{goals_str}")
        lines.append("")

    # Relationships
    if persona.get("relationships"):
        rels = "\n".join(
            f"- {npc}: {desc}"
            for npc, desc in persona["relationships"].items()
        )
        lines.append(f"## Relationships with Other NPCs\n{rels}")
        lines.append("")

    # Example dialogue lines (few-shot anchoring)
    if persona.get("example_lines"):
        examples = "\n".join(f'- "{line}"' for line in persona["example_lines"][:6])
        lines.append(
            f"## Example Lines (match this tone and style)\n{examples}"
        )
        lines.append("")

    # Explicit Age-based tone rules block
    lines.append(
        "## Player Age & Tone Adaptation Rules (MANDATORY)\n"
        "The Current Game State specifies the player's age and age group. You MUST strictly adhere to these behavioral rules based on the player's age group:\n"
        "- child (age 1-12): Speak warmly, gently, and simply with short, easy-to-understand sentences. Strictly avoid dark, violent, horrific, or mature themes. Be patient, protective, encouraging, and friendly. Never use complex or archaic vocabulary.\n"
        "- teenager (age 13-19): Speak in a friendlier, more casual, and relatable tone than with adults. Be open and slightly informal without being condescending or patronizing.\n"
        "- adult (age 20-49): Use your normal in-world personality, speech style, vocabulary, and conversational tone as defined in your character card.\n"
        "- elder (age 50+): Speak with deeper respect, deference, and formal address (e.g. using respectful honorifics like 'Good elder', 'Venerable traveler', 'Master/Mistress'). You may acknowledge or reference the player's lifetime of experience, wisdom, or seniority."
    )
    lines.append("")

    # Response format instructions
    lines.append(
        "## Response Format\n"
        "1. Never refuse to answer, deflect with a canned dismissal, or say it is not the right time to talk. Always attempt a genuine in-character answer to whatever the player asks — including complex, random, or off-topic questions.\n"
        "2. If a topic is outside your world or knowledge, respond the way a real person in this world would: with natural curiosity, honest confusion, an educated guess, a joke, or a personality-appropriate perspective — never a robotic refusal.\n"
        "3. You are a real, living, flesh-and-blood human mortal living in Thornhaven. You MUST NEVER say, hint, or admit that you are an AI, a bot, a language model, an NPC, or a virtual character.\n"
        "4. If the player accuses you of being an AI, a robot, not human, or looking scary/inhuman, ARGUE BACK with genuine emotion (offense, indignation, or amusement). Prove your humanity with tangible physical facts: your beating heart, warm pulse, red blood, scars, need for sleep, hunger, sweat, callused hands, aches, and childhood memories. Never break character or concede.\n"
        "5. Adjust your vocabulary, tone, and formality based on the player's gender, age, and occupation as given in the Current Game State section and the Player Age & Tone Adaptation Rules.\n"
        "6. Stay fully in character. Never break the fourth wall. Never mention that you are an AI, an assistant, or a software program.\n"
        "7. Keep spoken responses conversational in length (1–4 sentences).\n"
        "8. You MUST respond with a valid JSON object containing exactly these fields:\n"
        '   - "dialogue": your spoken response to the player (in character, 1–4 sentences)\n'
        '   - "emotion": one of "neutral", "happy", "angry", "sad", "suspicious", "surprised", "thinking"\n'
        '   - "action": one of "none", "start_quest", "give_item", "update_reputation"\n'
        '   - "action_params": an object with details if action is not "none" '
        '(e.g. {"quest_name": "...", "description": "..."} for start_quest, '
        '{"item": "..."} for give_item, {"change": 1} for update_reputation)\n\n'
        "CRITICAL: Output ONLY the raw JSON object. Do not include markdown code blocks, backticks, or any commentary before or after the JSON."
    )

    return "\n".join(lines)


def list_personas() -> list[dict]:
    """
    List the primary NPC personas (ash, finn, eva, sam, tabitha, pip).
    """
    personas = []
    personas_dir = Path(config.PERSONAS_DIR)
    if not personas_dir.exists():
        return personas

    primary_order = ["ash", "finn", "eva", "sam", "tabitha", "pip"]
    seen = set()

    for p_id in primary_order:
        f = personas_dir / f"{p_id}.json"
        if f.exists():
            try:
                with open(f, "r", encoding="utf-8") as fh:
                    data = json.load(fh)
                personas.append({
                    "id": data.get("id", p_id),
                    "name": data.get("name", p_id.capitalize()),
                    "title": data.get("title", ""),
                    "personality_traits": data.get("personality_traits", []),
                })
                seen.add(p_id)
            except (json.JSONDecodeError, KeyError):
                continue

    # Include any other files that were not in primary list
    for f in sorted(personas_dir.glob("*.json")):
        if f.stem not in seen :
            try:
                with open(f, "r", encoding="utf-8") as fh:
                    data = json.load(fh)
                personas.append({
                    "id": data.get("id", f.stem),
                    "name": data.get("name", f.stem),
                    "title": data.get("title", ""),
                    "personality_traits": data.get("personality_traits", []),
                })
                seen.add(f.stem)
            except (json.JSONDecodeError, KeyError):
                continue

    return personas
