"""
NPC Talk — Short-Term Memory
Rolling buffer of the last N turns per (npc_id, player_id) pair.
"""

from collections import defaultdict, deque
import threading

from npc_talk import config


class ShortTermMemory:
    """In-memory rolling buffer of recent conversation turns."""

    def __init__(self, max_turns: int = config.SHORT_TERM_BUFFER_SIZE):
        if max_turns <= 0:
            raise ValueError("max_turns must be greater than zero")
        self.max_turns = max_turns
        self._lock = threading.RLock()
        # Key: (npc_id, player_id) → deque of {"role": ..., "content": ...}
        self._buffers: dict[tuple[str, str], deque] = defaultdict(
            lambda: deque(maxlen=max_turns)
        )

    def add_turn(
        self, npc_id: str, player_id: str, role: str, content: str
    ) -> None:
        """
        Add a turn to the buffer.
        role: "player" or "npc"
        """
        key = (npc_id, player_id)
        with self._lock:
            self._buffers[key].append({"role": role, "content": content})

    def get_recent_turns(
        self, npc_id: str, player_id: str
    ) -> list[dict]:
        """Return the recent turns as a list (oldest first)."""
        key = (npc_id, player_id)
        with self._lock:
            return list(self._buffers[key])

    def format_for_prompt(
        self, npc_id: str, player_id: str, npc_name: str = "NPC"
    ) -> list[dict]:
        """
        Format recent turns as OpenAI-style message dicts
        for injection into the prompt.
        """
        turns = self.get_recent_turns(npc_id, player_id)
        messages = []
        for turn in turns:
            if turn["role"] == "player":
                messages.append({"role": "user", "content": turn["content"]})
            else:
                messages.append({"role": "assistant", "content": turn["content"]})
        return messages

    def clear(self, npc_id: str, player_id: str) -> None:
        """Clear the buffer for a specific NPC-player pair."""
        key = (npc_id, player_id)
        with self._lock:
            self._buffers.pop(key, None)
