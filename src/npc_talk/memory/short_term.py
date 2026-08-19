"""NPC Talk — Short-Term Memory (Rolling Conversation Buffer)."""
from collections import defaultdict, deque
import threading
from npc_talk import config


class ShortTermMemory:
    """Thread-safe rolling buffer of recent conversation turns per (npc_id, player_id)."""

    def __init__(self, max_turns: int = config.SHORT_TERM_BUFFER_SIZE):
        if max_turns <= 0:
            raise ValueError("max_turns must be > 0")
        self.max_turns = max_turns
        self._lock = threading.RLock()
        self._buffers: dict[tuple[str, str], deque] = defaultdict(lambda: deque(maxlen=max_turns))

    def add_turn(self, npc_id: str, player_id: str, role: str, content: str) -> None:
        with self._lock:
            self._buffers[(npc_id, player_id)].append({"role": role, "content": content})

    def get_recent_turns(self, npc_id: str, player_id: str) -> list[dict]:
        with self._lock:
            return list(self._buffers[(npc_id, player_id)])

    def format_for_prompt(self, npc_id: str, player_id: str, npc_name: str = "NPC") -> list[dict]:
        role_map = {"player": "user", "user": "user", "npc": "assistant", "assistant": "assistant"}
        with self._lock:
            return [
                {"role": role_map.get(t["role"], "user"), "content": t["content"]}
                for t in self._buffers[(npc_id, player_id)]
            ]

    def clear(self, npc_id: str, player_id: str) -> None:
        with self._lock:
            self._buffers.pop((npc_id, player_id), None)
