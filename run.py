import sys
import time
import webbrowser
import threading
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
SRC_DIR = PROJECT_ROOT / "src"

# Add src/ to path so `npc_talk` package is importable
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

import uvicorn

def open_browser():
    time.sleep(2.0)
    url = 'http://localhost:8000'
    print(f'\n[INFO] Opening browser at {url}...', flush=True)
    try:
        webbrowser.open(url)
    except Exception as e:
        print(f'[WARN] Could not automatically open browser: {e}')

def warmup_in_background():
    """Train ML models in a background thread — server stays responsive."""
    try:
        from npc_talk.nlp.models import warmup as _ml_warmup
        print('[INFO] ML model warmup starting in background (this may take a few minutes)...', flush=True)
        _ml_warmup()
        print('[INFO] ML models ready!', flush=True)
    except Exception as _e:
        print(f'[WARN] ML model warmup skipped: {_e}', flush=True)

if __name__ == '__main__':
    print('=' * 60)
    print('  NPC Talk — Dialogue Engine & Visual Novel UI')
    print('  URL: http://localhost:8000')
    print('  Press Ctrl+C to stop the server.')
    print('=' * 60, flush=True)

    # Start warmup and browser opener as background threads
    # Uvicorn starts immediately — frontend is accessible right away
    threading.Thread(target=warmup_in_background, daemon=True).start()
    threading.Thread(target=open_browser, daemon=True).start()

    uvicorn.run('npc_talk.api.main:app', host='127.0.0.1', port=8000, reload=False)

