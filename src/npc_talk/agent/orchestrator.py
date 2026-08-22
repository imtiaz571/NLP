"""
NPC Talk — Agent Orchestrator
Central pipeline: assembles persona + memory + state into a prompt,
calls the LLM, parses the response, and updates state/memory.
"""

import json
import logging
import re
from datetime import datetime
from typing import Optional, Dict, Any

from npc_talk.llm import client as llm_client
from npc_talk.personas.load_persona import load_persona, format_system_prompt
from npc_talk.memory.short_term import ShortTermMemory
from npc_talk.memory.long_term import LongTermMemory
from npc_talk.state.game_state import GameState

logger = logging.getLogger(__name__)


class NPCOrchestrator:
    """
    Orchestrates NPC dialogue generation.
    One instance per application — holds references to shared memory and state.
    """

    def __init__(
        self,
        short_term: ShortTermMemory,
        long_term: LongTermMemory,
        game_state: GameState,
    ):
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
        """
        Full pipeline:
        1. Set / update player profile if provided
        2. Load persona → system prompt
        3. Retrieve relevant memories
        4. Get game state context with player profile
        5. Build combined messages
        6. Call LLM / Local NLP Engine
        7. Parse structured response
        8. Update memory & state
        """
        if player_profile:
            self.game_state.set_player_profile(player_id, player_profile)

        # ── 1. Load persona ────────────────────────────────────────
        persona = load_persona(npc_id)
        system_prompt = format_system_prompt(persona)

        # ── 2. Retrieve long-term memories ─────────────────────────
        try:
            memories = self.long_term.retrieve(
                player_input,
                npc_id,
                player_id=player_id,
            )
        except Exception as exc:
            logger.warning("Long-term memory retrieval unavailable: %s", exc)
            memories = []
        memory_context = self.long_term.format_for_prompt(memories)

        # ── 3. Get game state ──────────────────────────────────────
        state_context = self.game_state.format_for_prompt(player_id, npc_id)

        # ── 4. Build messages ──────────────────────────────────────
        # System message: persona + memory + state
        full_system = system_prompt
        if memory_context:
            full_system += "\n\n" + memory_context
        full_system += "\n\n" + state_context

        messages = [{"role": "system", "content": full_system}]

        # Add conversation history (short-term buffer)
        history = self.short_term.format_for_prompt(
            npc_id, player_id, persona.get("name", "NPC")
        )
        messages.extend(history)

        # Add current player message
        messages.append({"role": "user", "content": player_input})

        # ── 5. Call LLM ────────────────────────────────────────────
        raw_response = llm_client.generate(messages)

        # ── 6. Parse response ──────────────────────────────────────
        parsed = self._parse_response(raw_response)

        # ── 7. Update short-term memory ────────────────────────────
        self.short_term.add_turn(npc_id, player_id, "player", player_input)
        self.short_term.add_turn(
            npc_id, player_id, "npc", parsed["dialogue"]
        )

        # ── 8. Handle actions & long-term memory ───────────────────
        self._handle_action(parsed, npc_id, player_id, player_input)

        # ── 9. Return response with current state ──────────────────
        parsed["game_state"] = self.game_state.get_state(player_id, npc_id)
        return parsed

    def _parse_response(self, raw: str) -> dict:
        """
        Parse the LLM's response as JSON.
        Robust: handles markdown code fences, partial JSON, and plain text fallback.
        """
        # Strip markdown code fences if present
        cleaned = raw.strip()
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
        cleaned = re.sub(r"\s*```$", "", cleaned)
        cleaned = cleaned.strip()

        try:
            normalized = self._normalize_response(json.loads(cleaned))
            if normalized is not None:
                return normalized
        except (json.JSONDecodeError, TypeError):
            pass

        # Try each object start so prose-wrapped JSON and nested action_params
        # are handled without a fragile regular expression.
        decoder = json.JSONDecoder()
        for match in re.finditer(r"\{", cleaned):
            try:
                candidate, _ = decoder.raw_decode(cleaned[match.start():])
            except json.JSONDecodeError:
                continue
            normalized = self._normalize_response(candidate)
            if normalized is not None:
                return normalized

        # Fallback: treat entire response as dialogue
        logger.warning("Could not parse LLM response as JSON, using fallback")
        return {
            "dialogue": cleaned,
            "action": "none",
            "action_params": {},
            "emotion": "neutral",
        }

    @staticmethod
    def _normalize_response(candidate: Any) -> Optional[dict]:
        """Validate untrusted model output before it reaches state handlers."""
        if not isinstance(candidate, dict):
            return None

        dialogue = candidate.get("dialogue")
        if not isinstance(dialogue, str) or not dialogue.strip():
            return None

        allowed_actions = {
            "none", "start_quest", "give_item", "update_reputation"
        }
        action = candidate.get("action", "none")
        if action not in allowed_actions:
            action = "none"

        params = candidate.get("action_params", {})
        if not isinstance(params, dict):
            params = {}

        if action == "update_reputation":
            change = params.get("change", 1)
            if isinstance(change, bool) or not isinstance(change, int):
                change = 1
            params = {**params, "change": max(-10, min(10, change))}
        elif action == "start_quest":
            quest_name = params.get("quest_name", "Unknown Quest")
            if not isinstance(quest_name, str) or not quest_name.strip():
                quest_name = "Unknown Quest"
            params = {**params, "quest_name": quest_name.strip()[:120]}
        elif action == "give_item":
            item = params.get("item", "an item")
            if not isinstance(item, str) or not item.strip():
                item = "an item"
            params = {**params, "item": item.strip()[:120]}

        allowed_emotions = {
            "neutral", "happy", "angry", "sad", "suspicious",
            "surprised", "thinking"
        }
        emotion = candidate.get("emotion", "neutral")
        if emotion not in allowed_emotions:
            emotion = "neutral"

        return {
            "dialogue": dialogue.strip(),
            "emotion": emotion,
            "action": action,
            "action_params": params,
        }

    def _handle_action(
        self,
        parsed: dict,
        npc_id: str,
        player_id: str,
        player_input: str,
    ) -> None:
        """Handle NPC actions and write significant events to long-term memory."""
        action = parsed.get("action", "none")
        params = parsed.get("action_params", {})

        if action == "none":
            return

        timestamp = datetime.now().isoformat()

        if action == "start_quest":
            quest_name = params.get("quest_name", "Unknown Quest")
            self.game_state.set_quest_status(quest_name, True)
            memory_text = (
                f"I gave the player the quest '{quest_name}'. "
                f"They seemed interested when they said: '{player_input[:80]}'"
            )
            self._remember_event(memory_text, npc_id, player_id, timestamp)
            logger.info("Quest started: %s", quest_name)

        elif action == "give_item":
            item = params.get("item", "an item")
            memory_text = (
                f"I gave the player {item}. "
                f"Context: '{player_input[:80]}'"
            )
            self._remember_event(memory_text, npc_id, player_id, timestamp)
            logger.info("Item given: %s", item)

        elif action == "update_reputation":
            change = params.get("change", 1)
            new_rep = self.game_state.change_reputation(
                player_id, npc_id, change
            )
            memory_text = (
                f"My opinion of the player changed ({'improved' if change > 0 else 'worsened'}). "
                f"Reputation is now {new_rep}. "
                f"Reason: '{player_input[:80]}'"
            )
            self._remember_event(memory_text, npc_id, player_id, timestamp)
            logger.info("Reputation updated: %+d → %d", change, new_rep)

    def _remember_event(
        self,
        text: str,
        npc_id: str,
        player_id: str,
        timestamp: str,
    ) -> None:
        """Keep optional vector-memory failures from breaking core dialogue."""
        try:
            self.long_term.add_memory(text, npc_id, player_id, timestamp)
        except Exception as exc:
            logger.warning("Could not persist long-term memory: %s", exc)
