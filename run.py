"""NPC Talk — Development Launcher."""
import sys
from pathlib import Path
import uvicorn

# Ensure src is in Python path
ROOT_DIR = Path(__file__).resolve().parent
SRC_DIR = ROOT_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

if __name__ == "__main__":
    print("=" * 60)
    print("  NPC Talk — Starting Server on http://127.0.0.1:8000")
    print("=" * 60)
    uvicorn.run(
        "npc_talk.api.main:app",
        host="127.0.0.1",
        port=8000,
        reload=False,
        app_dir=str(SRC_DIR),
    )
