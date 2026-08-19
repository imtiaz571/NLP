import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["OMP_NUM_THREADS"] = "1"
import logging
from pathlib import Path
from typing import Any, Dict, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

import npc_talk.config as config
from npc_talk.agent.orchestrator import NPCOrchestrator
from npc_talk.memory.long_term import LongTermMemory
from npc_talk.memory.short_term import ShortTermMemory
from npc_talk.personas.load_persona import list_personas, load_persona
from npc_talk.state.game_state import GameState

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("npc_talk.api")

short_term_mem = ShortTermMemory(max_turns=config.SHORT_TERM_BUFFER_SIZE)
long_term_mem = LongTermMemory(store_dir=config.MEMORY_STORE_DIR)
game_state = GameState()

try:
    long_term_mem.seed_from_file(config.SEED_MEMORIES_FILE)
except Exception as e:
    logger.warning("Could not seed long-term memory: %s", e)

orchestrator = NPCOrchestrator(short_term=short_term_mem, long_term=long_term_mem, game_state=game_state)

# Pre-warm local LLM engine in background for instant first-query response
def _warmup_llm():
    try:
        from npc_talk.llm.client import _get_qwen_engine
        _get_qwen_engine()
    except Exception as e:
        logger.warning("LLM warmup encountered: %s", e)

import threading
threading.Thread(target=_warmup_llm, daemon=True).start()

app = FastAPI(title="NPC Talk API", version="2.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=False, allow_methods=["*"], allow_headers=["*"])


class ChatRequest(BaseModel):
    player_id: str = "player_1"
    npc_id: str
    message: str
    player_profile: Optional[Dict[str, Any]] = None


class ProfileUpdateRequest(BaseModel):
    player_id: str = "player_1"
    name: Optional[str] = None
    gender: Optional[str] = None
    age: Optional[int] = None
    age_category: Optional[str] = None
    age_group: Optional[str] = None
    occupation: Optional[str] = None


class StateUpdateRequest(BaseModel):
    player_id: str = "player_1"
    npc_id: str = "ash"
    time_of_day: Optional[str] = None
    location: Optional[str] = None
    quest_flags: Optional[Dict[str, bool]] = None
    reputation: Optional[Dict[str, Any]] = None


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "NPC Talk NLP Dialogue Server"}


@app.get("/npcs")
def get_npcs():
    return list_personas()


@app.get("/npcs/{npc_id}")
def get_npc_detail(npc_id: str):
    try:
        return load_persona(npc_id)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"NPC {npc_id} not found")


@app.post("/chat")
def chat_with_npc(req: ChatRequest):
    if not req.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    try:
        return orchestrator.generate_npc_response(
            player_input=req.message.strip(),
            npc_id=req.npc_id,
            player_id=req.player_id,
            player_profile=req.player_profile,
        )
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error("Error generating dialogue: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="Dialogue generation failed")


@app.get("/profile")
def get_profile(player_id: str = "player_1"):
    return game_state.get_player_profile(player_id)


@app.post("/profile")
def update_profile(req: ProfileUpdateRequest):
    data = {k: v for k, v in req.model_dump().items() if v is not None and k != "player_id"}
    return game_state.set_player_profile(req.player_id, data)


@app.get("/state")
def get_current_state(player_id: str = "player_1", npc_id: str = "ash"):
    return game_state.get_state(player_id=player_id, npc_id=npc_id)


@app.post("/state")
def update_current_state(req: StateUpdateRequest):
    updates = {k: v for k, v in req.model_dump().items() if v is not None and k not in ("player_id", "npc_id")}
    game_state.update(updates)
    return {"status": "updated", "game_state": game_state.get_state(req.player_id, req.npc_id)}


@app.get("/history")
def get_chat_history(player_id: str = "player_1", npc_id: str = "ash"):
    return short_term_mem.get_recent_turns(npc_id=npc_id, player_id=player_id)


@app.get("/download-overview")
def download_overview():
    from fastapi.responses import FileResponse
    overview_path = config.PROJECT_ROOT / "PROJECT_OVERVIEW.md"
    if not overview_path.exists():
        raise HTTPException(status_code=404, detail="PROJECT_OVERVIEW.md not found")
    return FileResponse(
        path=str(overview_path),
        filename="PROJECT_OVERVIEW.md",
        media_type="text/markdown"
    )


if config.FRONTEND_DIR.exists():
    app.mount("/", StaticFiles(directory=str(config.FRONTEND_DIR), html=True), name="frontend")


if __name__ == "__main__":
    import uvicorn
    print("=" * 60)
    print("  NPC Talk — Starting Server on http://127.0.0.1:8000")
    print("=" * 60)
    uvicorn.run("npc_talk.api.main:app", host="127.0.0.1", port=8000, reload=True, app_dir=str(config.PROJECT_ROOT / "src"))

