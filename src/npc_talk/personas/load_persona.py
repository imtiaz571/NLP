"""NPC Talk — Persona Loader & System Prompt Formatter."""
import json
import re
from pathlib import Path
from npc_talk import config

VALID_NPC_ID = re.compile(r"^[a-z0-9_-]+$")
PRIMARY_ORDER = ["ash", "finn", "eva", "sam", "tabitha", "pip"]


def load_persona(npc_id: str) -> dict:
    if not isinstance(npc_id, str) or not VALID_NPC_ID.fullmatch(npc_id):
        raise FileNotFoundError(f"Invalid NPC id: {npc_id!r}")
    path = Path(config.PERSONAS_DIR) / f"{npc_id}.json"
    if not path.exists():
        raise FileNotFoundError(f"Persona file not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        persona = json.load(f)

    # Optional dataset lines
    lines_path = Path(config.DATA_PROCESSED_DIR) / f"{npc_id}_lines.json"
    if lines_path.exists():
        try:
            with open(lines_path, "r", encoding="utf-8") as f:
                lines_data = json.load(f)
            if lines_data.get("lines"):
                persona["example_lines"] = lines_data["lines"]
        except Exception:
            pass
    return persona


def format_system_prompt(persona: dict) -> str:
    traits = ", ".join(persona.get("personality_traits", []))
    goals = "\n".join(f"- {g}" for g in persona.get("goals", []))
    rels = "\n".join(f"- {k}: {v}" for k, v in persona.get("relationships", {}).items())
    examples = "\n".join(f'- "{ex}"' for ex in persona.get("example_lines", [])[:6])

    return f"""You are {persona['name']}, {persona.get('title', 'an NPC')}.

## Backstory
{persona.get('backstory', '')}

## Personality Traits
{traits}

## Speech Style
{persona.get('speech_style', '')}

## Goals
{goals}

## Relationships
{rels}

## Example Dialogue
{examples}

## Behavioral Rules
1. Respond in-character in conversational length (1–3 sentences).
2. Adapt tone to player age, gender, occupation, and reputation.
3. If asked about humanity or accused of being an AI, argue with emotional conviction.
4. Output a JSON object with:
   {{"dialogue": "...", "emotion": "neutral|happy|angry|sad|suspicious|surprised|thinking", "action": "none|start_quest|give_item|update_reputation", "action_params": {{}}}}"""


def list_personas() -> list[dict]:
    personas = []
    seen = set()
    dir_path = Path(config.PERSONAS_DIR)
    if not dir_path.exists():
        return personas

    for pid in PRIMARY_ORDER:
        f = dir_path / f"{pid}.json"
        if f.exists():
            try:
                with open(f, "r", encoding="utf-8") as fh:
                    data = json.load(fh)
                personas.append({
                    "id": data.get("id", pid),
                    "name": data.get("name", pid.capitalize()),
                    "title": data.get("title", ""),
                    "personality_traits": data.get("personality_traits", []),
                })
                seen.add(pid)
            except Exception:
                continue

    for f in sorted(dir_path.glob("*.json")):
        if f.stem not in seen:
            try:
                with open(f, "r", encoding="utf-8") as fh:
                    data = json.load(fh)
                personas.append({
                    "id": data.get("id", f.stem),
                    "name": data.get("name", f.stem.capitalize()),
                    "title": data.get("title", ""),
                    "personality_traits": data.get("personality_traits", []),
                })
            except Exception:
                continue
    return personas


def load_all_characters_summary() -> str:
    """Returns a structured summary of all 6 characters in Thornhaven for LLM context grounding."""
    summaries = [
        "1. Sam (Master Blacksmith & Veteran Soldier): Lost her left hand at the Siege of Ashenmoor 20 years ago; forged her own articulated steel prosthetic. Blunt, loyal, protective of the village. Owes a life-debt to Tabitha from the border wars.",
        "2. Ash (Information Broker & Ex-Accountant): Former head accountant for the Silver Serpent Syndicate who escaped with the bribery ledgers. Knows the secret smuggler tunnels and underworld gossip. Witty, calculating, street-smart.",
        "3. Eva (Village Apothecary & Herbalist): Expert in botanical alchemy, Frostmoss tinctures, and burn salves. Empathetic, calm, and scientific. Treats wounds with zero questions asked.",
        "4. Tabitha (Thornhaven Lorekeeper & Ancient Sage): 74-year-old guardian of the 212-year-old celestial seal and shattered keystones of the Sundered Crown. Mystical, solemn, and deeply wise.",
        "5. Finn (Apprentice Scout & Miller's Son): 16-year-old energetic scout who maps hidden ridge trails, tracks goblin camps, and watches rooftops. Suspicious of Ash, looks up to Sam.",
        "6. Pip (Curious Village Kid & Treasure Hunter): 8-year-old boy who finds shiny river rocks and keeps a friendly green beetle named Barnaby in his pocket. Cheerful, innocent, and imaginative."
    ]
    return "\n".join(summaries)
