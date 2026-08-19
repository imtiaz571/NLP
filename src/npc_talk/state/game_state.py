"""NPC Talk — Game State Manager."""
from collections import defaultdict
import threading
from npc_talk import config


class GameState:
    """Thread-safe world condition, player profiles, and NPC reputation tracker."""

    def __init__(self):
        self._lock = threading.RLock()
        self.time_of_day: str = config.DEFAULT_TIME_OF_DAY
        self.location: str = config.DEFAULT_LOCATION
        self.quest_flags: dict[str, bool] = {}
        self._player_profiles: dict[str, dict] = defaultdict(
            lambda: {"name": "Traveler", "gender": "male", "age": 22, "age_category": "adult", "age_group": "adult", "occupation": "adventurer"}
        )
        self._reputation: dict[tuple[str, str], int] = defaultdict(lambda: config.DEFAULT_REPUTATION)

    def get_player_profile(self, player_id: str) -> dict:
        with self._lock:
            return dict(self._player_profiles[player_id])

    def set_player_profile(self, player_id: str, profile: dict) -> dict:
        with self._lock:
            curr = self._player_profiles[player_id]
            curr.update(profile)
            age = curr.get("age", 22)
            age_cat = profile.get("age_group") or profile.get("age_category") or (
                "child" if age <= 12 else "teenager" if age <= 19 else "adult" if age <= 49 else "elder"
            )
            curr["age_category"] = curr["age_group"] = age_cat
            return dict(curr)

    def get_reputation(self, player_id: str, npc_id: str) -> int:
        with self._lock:
            return self._reputation[(player_id, npc_id)]

    def set_reputation(self, player_id: str, npc_id: str, value: int) -> None:
        with self._lock:
            self._reputation[(player_id, npc_id)] = value

    def change_reputation(self, player_id: str, npc_id: str, delta: int) -> int:
        with self._lock:
            self._reputation[(player_id, npc_id)] += delta
            return self._reputation[(player_id, npc_id)]

    def set_quest_status(self, quest_name: str, active: bool) -> None:
        with self._lock:
            self.quest_flags[quest_name] = active

    def update(self, changes: dict) -> dict:
        with self._lock:
            if "time_of_day" in changes:
                self.time_of_day = changes["time_of_day"]
            if "location" in changes:
                self.location = changes["location"]
            if "quest_flags" in changes:
                self.quest_flags.update(changes["quest_flags"])
            if "reputation" in changes:
                rep = changes["reputation"]
                if isinstance(rep, dict) and "player_id" in rep and "npc_id" in rep:
                    self.set_reputation(rep["player_id"], rep["npc_id"], rep.get("value", 0))
            return self.get_full_state()

    def get_state(self, player_id: str, npc_id: str) -> dict:
        with self._lock:
            rep = self.get_reputation(player_id, npc_id)
            label = "trusted ally" if rep >= 5 else "friendly" if rep >= 2 else "neutral" if rep >= 0 else "wary" if rep >= -2 else "hostile"
            return {
                "time_of_day": self.time_of_day,
                "location": self.location,
                "quest_flags": dict(self.quest_flags),
                "reputation": rep,
                "reputation_label": label,
            }

    def get_full_state(self) -> dict:
        with self._lock:
            return {"time_of_day": self.time_of_day, "location": self.location, "quest_flags": dict(self.quest_flags)}

    def format_for_prompt(self, player_id: str, npc_id: str) -> str:
        state = self.get_state(player_id, npc_id)
        prof = self.get_player_profile(player_id)
        quests = [q for q, v in state["quest_flags"].items() if v]
        lines = [
            "## Current Game State",
            f"Time of Day: {state['time_of_day'].title()}.",
            f"You are in the {state['location'].replace('_', ' ').title()}.",
            f"The player's reputation with you is: {state['reputation_label']} ({state['reputation']:+d}).",
            f"Active quests: {', '.join(quests) if quests else 'None'}.",
            f"The player is {prof.get('name', 'Traveler')}, a {prof.get('age', 22)}-year-old {prof.get('gender', 'male')} {prof.get('occupation', 'adventurer')} ({prof.get('age_category', 'adult')}).",
        ]
        return "\n".join(lines)
