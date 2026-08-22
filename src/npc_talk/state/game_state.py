"""
NPC Talk — Game State Manager
Tracks per-session world state (time, location, quests, reputation)
and formats it for prompt injection.
"""

from collections import defaultdict
import threading

from npc_talk import config


class GameState:
    """
    In-memory game state singleton.
    Tracks world conditions and per-player-NPC reputation.
    """

    def __init__(self):
        self._lock = threading.RLock()
        self.time_of_day: str = config.DEFAULT_TIME_OF_DAY
        self.location: str = config.DEFAULT_LOCATION
        self.quest_flags: dict[str, bool] = {}
        # player profile keyed by player_id → dict
        self._player_profiles: dict[str, dict] = defaultdict(
            lambda: {
                "name": "Traveler",
                "gender": "male",
                "age": 22,
                "age_category": "adult",
                "occupation": "adventurer"
            }
        )
        # reputation keyed by (player_id, npc_id) → int
        self._reputation: dict[tuple[str, str], int] = defaultdict(
            lambda: config.DEFAULT_REPUTATION
        )

    def get_player_profile(self, player_id: str) -> dict:
        with self._lock:
            return dict(self._player_profiles[player_id])

    def set_player_profile(self, player_id: str, profile: dict) -> dict:
        with self._lock:
            current = self._player_profiles[player_id]
            current.update(profile)
            if "age_group" in profile:
                current["age_category"] = profile["age_group"]
                current["age_group"] = profile["age_group"]
            elif "age_category" in profile:
                current["age_category"] = profile["age_category"]
                current["age_group"] = profile["age_category"]
            elif "age" in profile:
                age = profile["age"]
                if age <= 12:
                    cat = "child"
                elif age <= 19:
                    cat = "teenager"
                elif age <= 49:
                    cat = "adult"
                else:
                    cat = "elder"
                current["age_category"] = cat
                current["age_group"] = cat
            return dict(current)

    def get_reputation(self, player_id: str, npc_id: str) -> int:
        with self._lock:
            return self._reputation[(player_id, npc_id)]

    def set_reputation(self, player_id: str, npc_id: str, value: int) -> None:
        with self._lock:
            self._reputation[(player_id, npc_id)] = value

    def change_reputation(self, player_id: str, npc_id: str, delta: int) -> int:
        with self._lock:
            key = (player_id, npc_id)
            self._reputation[key] += delta
            return self._reputation[key]

    def set_quest_status(self, quest_name: str, active: bool) -> None:
        with self._lock:
            self.quest_flags[quest_name] = active

    def update(self, changes: dict) -> dict:
        """
        Apply partial updates to the game state.
        Accepted keys: time_of_day, location, quest_flags, reputation.
        Returns the full updated state (without player-specific rep).
        """
        with self._lock:
            if "time_of_day" in changes:
                self.time_of_day = changes["time_of_day"]
            if "location" in changes:
                self.location = changes["location"]
            if "quest_flags" in changes:
                self.quest_flags.update(changes["quest_flags"])
            if "reputation" in changes:
                # Expects: {"player_id": ..., "npc_id": ..., "value": int}
                rep = changes["reputation"]
                if isinstance(rep, dict) and "player_id" in rep and "npc_id" in rep:
                    self.set_reputation(
                        rep["player_id"], rep["npc_id"], rep.get("value", 0)
                    )

            return self.get_full_state()

    def get_state(self, player_id: str, npc_id: str) -> dict:
        """Get the full state snapshot for a specific player-NPC pair."""
        with self._lock:
            rep = self.get_reputation(player_id, npc_id)
            return {
                "time_of_day": self.time_of_day,
                "location": self.location,
                "quest_flags": dict(self.quest_flags),
                "reputation": rep,
                "reputation_label": self._reputation_label(rep),
            }

    def get_full_state(self) -> dict:
        """Get global state (without player-specific reputation)."""
        with self._lock:
            return {
                "time_of_day": self.time_of_day,
                "location": self.location,
                "quest_flags": dict(self.quest_flags),
            }

    @staticmethod
    def _reputation_label(rep: int) -> str:
        if rep >= 5:
            return "trusted ally"
        elif rep >= 2:
            return "friendly"
        elif rep >= 0:
            return "neutral"
        elif rep >= -2:
            return "wary"
        else:
            return "hostile"

    @staticmethod
    def _location_display(location: str) -> str:
        return location.replace("_", " ").title()

    def format_for_prompt(self, player_id: str, npc_id: str) -> str:
        """
        Format current game state as a natural-language prompt section.
        """
        state = self.get_state(player_id, npc_id)
        lines = ["## Current Game State"]

        # Time
        time_flavor = {
            "dawn": "The sun has just risen over Thornhaven. Morning light filters through the trees.",
            "morning": "The sun has just risen over Thornhaven. Morning light filters through the trees.",
            "day": "The sun hangs high over Thornhaven. The village bustles with activity.",
            "afternoon": "The afternoon sun hangs high. The village bustles with activity.",
            "dusk": "Dusk settles over Thornhaven. Lanterns are being lit along the streets.",
            "evening": "Dusk settles over Thornhaven. Lanterns are being lit along the streets.",
            "night": "Night has fallen. Shadows pool between the buildings. The village is quiet.",
        }
        lines.append(
            time_flavor.get(state["time_of_day"], f"It is {state['time_of_day']}.")
        )

        # Location
        lines.append(
            f"You are in the {self._location_display(state['location'])}."
        )

        # Reputation
        lines.append(
            f"The player's reputation with you is: {state['reputation_label']} "
            f"({state['reputation']:+d}). "
            "Adjust your warmth and willingness to help accordingly."
        )

        # Active quests
        active_quests = [q for q, v in state["quest_flags"].items() if v]
        if active_quests:
            lines.append(
                f"Active quests: {', '.join(active_quests)}. "
                "Reference these if relevant to the conversation."
            )

        # Player Profile
        profile = self.get_player_profile(player_id)
        lines.append(
            f"The player is {profile.get('name', 'Traveler')}, a {profile.get('age', 22)}-year-old {profile.get('gender', 'male')} {profile.get('occupation', 'adventurer')} ({profile.get('age_category', 'adult')}). "
            "Tailor your honorifics, address, advice, and conversation topics to match the player's gender, age, and occupation."
        )

        return "\n".join(lines)
