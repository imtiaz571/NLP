import logging
import os
import sys
from pathlib import Path
from typing import Dict, Literal, Optional

# HuggingFace/Transformers online access allowed (will download models on first run if not cached)
# To force offline mode, set HF_HUB_OFFLINE=1 and TRANSFORMERS_OFFLINE=1 in environment

# Ensure src/ is in sys.path so npc_talk package is importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent / "src"))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

import npc_talk.config as config
from npc_talk.personas.load_persona import list_personas, load_persona
from npc_talk.memory.short_term import ShortTermMemory
from npc_talk.memory.long_term import LongTermMemory, _get_model
from npc_talk.state.game_state import GameState
from npc_talk.agent.orchestrator import NPCOrchestrator

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger('npc_talk.api')

# Warmup embedding model at startup for instant runtime retrieval
try:
    _get_model()
except Exception as e:
    logger.warning('Could not warm up embedding model: %s', e)

short_term_mem = ShortTermMemory(max_turns=config.SHORT_TERM_BUFFER_SIZE)
long_term_mem = LongTermMemory(store_dir=config.MEMORY_STORE_DIR)
game_state = GameState()

try:
    long_term_mem.seed_from_file(config.SEED_MEMORIES_FILE)
except Exception as e:
    logger.warning('Could not seed long-term memory: %s', e)

orchestrator = NPCOrchestrator(
    short_term=short_term_mem,
    long_term=long_term_mem,
    game_state=game_state
)

app = FastAPI(
    title='NPC Talk API',
    description='Context-Aware NLP Dialogue Agent for Game NCPs',
    version='2.0.0'
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=False,
    allow_methods=['*'],
    allow_headers=['*'],
)


class PlayerProfileFields(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=80)
    gender: Optional[str] = Field(default=None, min_length=1, max_length=40)
    age: Optional[int] = Field(default=None, ge=1, le=120)
    age_category: Optional[Literal['child', 'teenager', 'adult', 'elder']] = None
    age_group: Optional[Literal['child', 'teenager', 'adult', 'elder']] = None
    occupation: Optional[str] = Field(default=None, min_length=1, max_length=80)


class ChatRequest(BaseModel):
    player_id: str = Field(default='player_1', min_length=1, max_length=80)
    npc_id: str = Field(..., min_length=1, max_length=80, pattern=r'^[a-z0-9_-]+$')
    message: str = Field(..., min_length=1, max_length=4000)
    player_profile: Optional[PlayerProfileFields] = None


class ReputationUpdateRequest(BaseModel):
    player_id: str = Field(..., min_length=1, max_length=80)
    npc_id: str = Field(..., min_length=1, max_length=80, pattern=r'^[a-z0-9_-]+$')
    value: int = Field(default=0, ge=-100, le=100)


class StateUpdateRequest(BaseModel):
    player_id: str = Field(default='player_1', min_length=1, max_length=80)
    npc_id: str = Field(default='ash', min_length=1, max_length=80, pattern=r'^[a-z0-9_-]+$')
    time_of_day: Optional[Literal['dawn', 'day', 'dusk', 'night']] = None
    location: Optional[Literal[
        'village_square', 'forest', 'tavern', 'dungeon', 'castle_ruins',
        'apothecary', 'blacksmith_forge', 'market_stalls'
    ]] = None
    quest_flags: Optional[Dict[str, bool]] = None
    reputation: Optional[ReputationUpdateRequest] = None


class ProfileUpdateRequest(PlayerProfileFields):
    player_id: str = Field(default='player_1', min_length=1, max_length=80)


@app.get('/health')
def health_check():
    return {'status': 'ok', 'service': 'NPC Talk NLP Dialogue Server'}


@app.get('/npcs')
def get_npcs():
    return list_personas()


@app.get('/npcs/{npc_id}')
def get_npc_detail(npc_id: str):
    try:
        return load_persona(npc_id)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f'NPC {npc_id} not found')


@app.post('/chat')
def chat_with_npc(req: ChatRequest):
    if not req.message or not req.message.strip():
        raise HTTPException(status_code=400, detail='Message cannot be empty')

    try:
        response = orchestrator.generate_npc_response(
            player_input=req.message.strip(),
            npc_id=req.npc_id,
            player_id=req.player_id,
            player_profile=(
                req.player_profile.model_dump(exclude_none=True)
                if req.player_profile else None
            )
        )
        return response
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error('Error generating dialogue: %s', e, exc_info=True)
        raise HTTPException(status_code=500, detail='Dialogue generation failed')


@app.get('/profile')
def get_profile(player_id: str = 'player_1'):
    return game_state.get_player_profile(player_id)


@app.post('/profile')
def update_profile(req: ProfileUpdateRequest):
    data = {k: v for k, v in req.model_dump().items() if v is not None and k != 'player_id'}
    return game_state.set_player_profile(req.player_id, data)


@app.get('/state')
def get_current_state(player_id: str = 'player_1', npc_id: str = 'ash'):
    return game_state.get_state(player_id=player_id, npc_id=npc_id)


@app.post('/state')
def update_current_state(req: StateUpdateRequest):
    updates = {}
    if req.time_of_day is not None:
        updates['time_of_day'] = req.time_of_day
    if req.location is not None:
        updates['location'] = req.location
    if req.quest_flags is not None:
        updates['quest_flags'] = req.quest_flags
    if req.reputation is not None:
        updates['reputation'] = req.reputation.model_dump()

    game_state.update(updates)
    updated_state = game_state.get_state(req.player_id, req.npc_id)
    return {'status': 'updated', 'game_state': updated_state}


@app.get('/history')
def get_chat_history(player_id: str = 'player_1', npc_id: str = 'ash'):
    return short_term_mem.get_recent_turns(npc_id=npc_id, player_id=player_id)


@app.delete('/history')
def clear_chat_history(player_id: str = 'player_1', npc_id: str = 'ash'):
    short_term_mem.clear(npc_id=npc_id, player_id=player_id)
    return {'status': 'cleared'}


frontend_dir = Path(config.FRONTEND_DIR)
if frontend_dir.exists():
    app.mount('/', StaticFiles(directory=str(frontend_dir), html=True), name='frontend')
