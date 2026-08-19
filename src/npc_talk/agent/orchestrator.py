"""NPC Talk — Dialogue Agent Orchestrator."""
import json
import logging
import re
from datetime import datetime
from typing import Optional
from npc_talk.llm import client as llm_client
from npc_talk.memory.long_term import LongTermMemory
from npc_talk.memory.short_term import ShortTermMemory
from npc_talk.personas.load_persona import format_system_prompt, load_persona
from npc_talk.state.game_state import GameState

logger = logging.getLogger(__name__)


class NPCOrchestrator:
    """Orchestrates persona formatting, memory retrieval, LLM generation, and game state updates."""

    def __init__(self, short_term: ShortTermMemory, long_term: LongTermMemory, game_state: GameState):
        self.short_term = short_term
        self.long_term = long_term
        self.game_state = game_state

    def generate_npc_response(
        self,
        player_input: str,
        npc_id: str,
        player_id: str = "player_1",
        player_profile: Optional[dict] = None,
    ) -> dict:
        if player_profile:
            self.game_state.set_player_profile(player_id, player_profile)

        # 1. Load persona & build system prompt
        persona = load_persona(npc_id)
        system_prompt = format_system_prompt(persona)

        # 2. Retrieve memories & state
        memories = self.long_term.retrieve(player_input, npc_id, player_id=player_id)
        mem_prompt = self.long_term.format_for_prompt(memories)
        state_prompt = self.game_state.format_for_prompt(player_id, npc_id)

        full_system = f"{system_prompt}\n\n{mem_prompt}\n\n{state_prompt}".strip()
        messages = [{"role": "system", "content": full_system}]
        messages.extend(self.short_term.format_for_prompt(npc_id, player_id, persona.get("name", "NPC")))
        messages.append({"role": "user", "content": player_input})

        # 3. Generate response
        raw = llm_client.generate(messages)
        parsed = self._parse_response(raw)

        # 4. Update memory & state
        self.short_term.add_turn(npc_id, player_id, "player", player_input)
        self.short_term.add_turn(npc_id, player_id, "npc", parsed["dialogue"])
        self._handle_action(parsed, npc_id, player_id, player_input)

        parsed["game_state"] = self.game_state.get_state(player_id, npc_id)
        return parsed

    def _parse_response(self, raw: str) -> dict:
        cleaned = re.sub(r"^```(?:json)?\s*", "", raw.strip())
        cleaned = re.sub(r"\s*```$", "", cleaned).strip()
        try:
            data = json.loads(cleaned)
            if isinstance(data, dict) and "dialogue" in data:
                return {
                    "dialogue": str(data["dialogue"]),
                    "emotion": data.get("emotion", "neutral"),
                    "action": data.get("action", "none"),
                    "action_params": data.get("action_params", {}),
                    "tier": data.get("tier"),
                    "model_source": data.get("model_source"),
                    "routing_reason": data.get("routing_reason"),
                    "conversational_intent": data.get("conversational_intent"),
                }
        except Exception:
            pass
        return {"dialogue": cleaned, "emotion": "neutral", "action": "none", "action_params": {}}

    def _handle_action(self, parsed: dict, npc_id: str, player_id: str, player_input: str):
        action = parsed.get("action", "none")
        params = parsed.get("action_params", {})
        ts = datetime.now().isoformat()

        if action == "start_quest":
            quest = params.get("quest_name", "New Quest")
            self.game_state.set_quest_status(quest, True)
            self.long_term.add_memory(f"Started quest: {quest}", npc_id, player_id, ts)
        elif action == "give_item":
            item = params.get("item", "an item")
            self.long_term.add_memory(f"Gave player item: {item}", npc_id, player_id, ts)
        elif action == "update_reputation":
            delta = params.get("change", 1)
            new_rep = self.game_state.change_reputation(player_id, npc_id, delta)
            self.long_term.add_memory(f"Reputation updated to {new_rep}", npc_id, player_id, ts)
