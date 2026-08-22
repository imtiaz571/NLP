# NPC Talk

NPC Talk is a FastAPI backend and browser-based visual-novel chat UI for six
context-aware game characters. Each character has a stable persona, short-term
conversation history, semantic long-term memory, and dialogue that adapts to the
current location, time, quests, player profile, and reputation.

## Characters

- Ash — information broker
- Finn — apprentice scout
- Eva — apothecary and herbalist
- Sam — veteran blacksmith
- Tabitha — village lorekeeper
- Pip — curious village child

## How dialogue is generated

The backend uses a hybrid local pipeline:

1. Persona, game state, recent turns, and player-specific memories are assembled.
2. Deterministic intent and narrative rules handle known topics quickly.
3. The intent layer supports Naive Bayes, logistic regression, random forest,
   linear SVC, KNN, decision tree, XGBoost, soft voting, and AdaBoost. Auto mode
   selects a probability-stable model per NPC; logistic regression separately
   classifies response emotion.
4. A local Qwen 2.5 1.5B model is the optional fallback for open-ended prompts.
5. If the generative model is unavailable, the application still returns a safe
   in-character fallback.

Long-term memory uses `sentence-transformers` and FAISS. No cloud LLM API key is
required. The embedding and Qwen models may be downloaded on first use if they
are not already cached.

## Project layout

```text
agent/                 Dialogue orchestration and narrative retrieval
api/main.py            FastAPI models, endpoints, and static-file serving
data/                  Training data and optional dataset processing
frontend/              Visual-novel web interface and assets
memory/                 Short- and long-term memory implementations
personas/               Six JSON character cards
state/game_state.py     Player profile and game-state management
tools/validate_data.py  Persona/data integrity audit
config.py               Paths and memory/game defaults
llm_client.py           Hybrid local dialogue engine
ml_models.py            Intent and emotion classifiers
run.py                  Development launcher
test_offline.py         Network-free regression suite
```

## Setup

Python 3.10 or newer is required. Virtual environments contain absolute paths,
so an environment copied from another computer will not work. Create a fresh
one on the current machine:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

On macOS or Linux, activate it with:

```bash
source .venv/bin/activate
```

Kaggle credentials are optional. The public external datasets can normally be
downloaded without credentials; Kaggle may require you to accept a dataset's
terms on its web page before downloading it through the API.

## External training data

Eight Kaggle sources are supported: DailyDialog, GoEmotions, Small Talk Intent,
ViGGO, Fallout: New Vegas, Bitext, Chatbot Intent Classification, and MELD. To
download missing sources and rebuild the normalized corpora:

```powershell
python data/download_external_data.py
python data/build_external_corpora.py
```

The normalized files and a count report are written under `data/processed/`.
Every record retains its source, license, original label, and train/validation/
test split. The live classifiers use only the training split.

External labels are not assumed to mean the same thing as NPC intents. The live
intent model uses only conservative mappings for identity, advice, and Pip's
greetings. Customer-service labels remain available for experiments but are not
fed into the NPC model. ViGGO is stored as game-dialogue reference material, and
Fallout text is marked non-trainable because the underlying dialogue is
copyrighted. Only MELD's 1 MB text CSV is downloaded; its 4.5 GB media bundle is
not needed by this text classifier.

## Run

```powershell
python run.py
```

Open <http://127.0.0.1:8000>. To run without automatically opening a browser:

```powershell
python -m uvicorn api.main:app --host 127.0.0.1 --port 8000
```

## Verify

The offline suite uses deterministic test embeddings, so it does not download
models or require a GPU:

```powershell
python test_offline.py
python tools/validate_data.py
python tools/benchmark_models.py
python tools/benchmark_emotions.py
```

The intent benchmark evaluates all nine models in two profiles. Its enforced
90% gate measures in-distribution phrasing-template coverage for every model and
every NPC. A separate leakage-resistant profile holds out entire raw trigger
terms and reports the much harder unseen-synonym diagnostic. Keeping both scores
prevents the high coverage number from being misrepresented as real-world
generalization. Configure the live selector through `INTENT_CLASSIFIER` in
`config.py`; `auto` is the default. The emotion benchmark evaluates only
untouched external test splits.

## Why this project uses ML

Classical ML is not responsible for writing NPC dialogue. It handles two small,
bounded classification problems:

- Intent classification catches paraphrases that the exact rule matcher misses.
- Emotion classification maps generated dialogue to portrait/UI states.

These classifiers are local, fast, inexpensive, and deterministic compared with
calling a generative model for every routing decision. They sit behind the
high-precision rules and use a confidence threshold; uncertain predictions fall
through to the local language model.

All nine intent models exceed 90% in the template-coverage regression gate. The
original NPC trigger dataset is nevertheless too small and lexically narrow for
strong unseen-synonym generalization: most examples are isolated keywords, not
utterances. The benchmark therefore preserves a second raw-trigger diagnostic,
which remains low and must not be described as 90% accurate. External human-
labelled data gives the emotion model broader language coverage, while safely
mapped small-talk examples improve a few shared intents. NPC-specific quests,
lore, rumors, locations, and relationships still need human-written labels to
raise the leakage-resistant score.

To improve that harder score, generate the fixed human-annotation queue:

```powershell
python tools/create_intent_annotation_queue.py
```

Write a genuinely different player utterance in each row without copying the
seed terms, then mark it `approved`. The preassigned splits provide 20 training,
5 validation, and 5 untouched test messages per NPC intent.

## API

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/health` | Service health check |
| `GET` | `/npcs` | List characters |
| `GET` | `/npcs/{npc_id}` | Read one character card |
| `POST` | `/chat` | Generate a character response |
| `GET`, `POST` | `/state` | Read or update world/player state |
| `GET`, `POST` | `/profile` | Read or update a player profile |
| `GET`, `DELETE` | `/history` | Read or clear short-term history |

Chat example:

```bash
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"player_id":"player_1","npc_id":"tabitha","message":"Tell me about the ancient prophecy."}'
```

State example:

```bash
curl -X POST http://127.0.0.1:8000/state \
  -H "Content-Type: application/json" \
  -d '{"player_id":"player_1","npc_id":"ash","time_of_day":"night","location":"forest"}'
```

Supported locations are `village_square`, `forest`, `tavern`, `dungeon`,
`castle_ruins`, `apothecary`, `blacksmith_forge`, and `market_stalls`.
Supported times are `dawn`, `day`, `dusk`, and `night`.

## Persistence

Long-term memories are persisted under `memory/store`. Short-term history,
profiles, reputation, quests, location, and time are currently held in process
memory and reset when the server restarts.
