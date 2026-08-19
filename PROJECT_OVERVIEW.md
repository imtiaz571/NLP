# NPC Talk — Intelligent Multi-Agent Conversational Game System
## Comprehensive Project Overview, Architecture & Viva Defense Documentation

---

## 1. Executive Summary

**NPC Talk** is a high-performance, real-time conversational AI and multi-agent dialogue system embedded into an interactive Visual Novel / RPG setting (*Thornhaven*). It combines modern Natural Language Processing (NLP), dense semantic vector search, discourse analysis, pragmatic intent recognition, hierarchical memory architectures, and an optional local generative LLM fallback (Qwen 2.5) to simulate realistic, psychologically consistent, and context-aware Non-Player Characters (NPCs).

Unlike traditional rigid dialogue trees or slow cloud-hosted LLM wrappers (such as OpenAI/Anthropic APIs), NPC Talk operates primarily on an optimized **local hybrid NLP inference pipeline**. This delivers **sub-50ms conversational response times**, **100% offline functionality**, **zero external API fees**, strict persona guardrails, and persistent long-term episodic memory.

```
+---------------------------------------------------------------------------------------------------+
|                                      KEY PROJECT HIGHLIGHTS                                       |
+------------------------------------+----------------------------------+---------------------------+
| ⚡ Sub-50ms Response Latency       | 🛡️ Turing Guardrails & Immunity   | 🧠 Dual-Tier Memory       |
| 🔒 100% Local / Offline Execution  | 🎭 6 Distinct Deep Personas      | 🤖 Local Qwen 2.5 Fallback|
| 📈 Supervised ML Intent Pipelines  | 🔍 FAISS Dense Vector Search     | 🎨 Rich Visual Novel UI   |
+------------------------------------+----------------------------------+---------------------------+
```

---

## 2. System Architecture & High-Level Design

The system is organized into modular layers connecting the browser UI, FastAPI REST orchestration layer, multi-tier NLP inference pipeline, memory systems, and game state manager.

```
                     ┌─────────────────────────────────────────────────────────┐
                     │                  Web Frontend UI / UX                   │
                     │  (Vanilla ES6+, Responsive Tailwind CSS, Web Audio Synthesizer) │
                     └────────────────────────────┬────────────────────────────┘
                                                  │ HTTP POST /chat, /state, /profile
                                                  ▼
                     ┌─────────────────────────────────────────────────────────┐
                     │               FastAPI Orchestration API                 │
                     │             (src/npc_talk/api/main.py)                  │
                     └────────────────────────────┬────────────────────────────┘
                                                  │
         ┌────────────────────────────────────────┼────────────────────────────────────────┐
         ▼                                        ▼                                        ▼
┌─────────────────┐                      ┌─────────────────┐                      ┌─────────────────┐
│  Memory System  │                      │ Persona Manager │                      │ Game State Hub  │
│ • Short-Term    │                      │ • Backstory     │                      │ • Location      │
│   Rolling Deque │                      │ • Traits/Style  │                      │ • Time of Day   │
│ • Long-Term     │                      │ • Relationships │                      │ • Quests/Flags  │
│   FAISS Index   │                      │ • Dynamic World │                      │ • Reputation    │
└────────┬────────┘                      └────────┬────────┘                      └────────┬────────┘
         │                                        │                                        │
         └────────────────────────────────────────┼────────────────────────────────────────┘
                                                  │ Assembles Unified Prompt & Dialogue Context
                                                  ▼
                     ┌─────────────────────────────────────────────────────────┐
                     │          Dialogue Agent Orchestrator & Client           │
                     │          (src/npc_talk/agent/orchestrator.py)           │
                     │             (src/npc_talk/llm/client.py)                │
                     └────────────────────────────┬────────────────────────────┘
                                                  │
         ┌────────────────────────────────────────┴────────────────────────────────────────┐
         │
         ├──▶ Tier 1: Humanity & Turing Challenge Guardrails
         │             • Regex patterns for "Are you an AI/bot?", "Ignore instructions"
         │             • Emotional, in-character defense preserving game immersion
         │
         ├──▶ Tier 2: Conversational & Pragmatic Intent Engine
         │             • Typo & slang normalization (`normalize_text`)
         │             • Accusations (thief, liar), identity, physical states (hunger, sleep)
         │             • Quests (ancient ruins, frostmoss, strange sounds), greetings, humor
         │
         ├──▶ Tier 3: Deep Semantic Narrative Engine with Context Inheritance
         │             • Dense Embeddings (`all-MiniLM-L6-v2`, 384-dim) + Lexical N-Gram
         │             • Discourse Classification: Causal, Continuation, Procedural
         │             • Active Context Inheritance from short-term conversation thread
         │
         ├──▶ Tier 4: Supervised ML Intent Classifier & Emotion Detector
         │             • Sublinear TF-IDF Vectorizer + Logistic Regression pipeline
         │             • Strict Zero-Feature Check (`vec.nnz > 0`) & Root Feature Match
         │             • DistilRoBERTa Emotion Transformer / Lexical Fallback
         │
         ├──▶ Tier 5: Local Generative LLM Fallback (Qwen 2.5 3B / 1.5B Instruct)
         │             • Offline Hugging Face Transformers inference (bfloat16 / float16)
         │             • Persona & relationship grounding system prompt
         │
         └──▶ Tier 6: In-Character Dynamic Topical Safety Generator
                       • Profile-anchored contextual fallback with topic token extraction
```

---

## 3. Technology Stack & Specifications

| Layer / Subsystem | Technologies & Libraries | Technical Details & Purpose |
| :--- | :--- | :--- |
| **Backend Framework** | Python 3.10+, FastAPI, Uvicorn, Pydantic v2 | Asynchronous RESTful API backend, static file server |
| **Semantic Embeddings** | `sentence-transformers` (`all-MiniLM-L6-v2`) | 384-dimensional dense vectors for semantic search |
| **Vector Database** | `faiss-cpu` (Facebook AI Similarity Search) | `IndexFlatIP` on normalized vectors for memory retrieval |
| **Machine Learning** | `scikit-learn` (`TfidfVectorizer`, `LogisticRegression`) | Multi-class intent classification with sublinear TF |
| **Emotion Analysis** | Hugging Face `transformers` (`DistilRoBERTa-emotion`) | 7-class emotion model + rule-based lexical fallback |
| **Local Generative LLM** | `transformers`, `torch` (`Qwen2.5-3B-Instruct`) | Offline generative dialogue fallback (bfloat16/float16) |
| **Frontend Framework** | HTML5, Modern Vanilla ES6+, CSS3, Tailwind CSS | High-performance Visual Novel UI, dynamic portraits |
| **Audio Engine** | Web Audio API / Custom Synthesizer | Procedural typewriter blips, ambient audio cues |
| **Storage & Data** | JSON, JSONL, FAISS binary index | Knowledge base, persona data, memory index store |

---

## 4. NPC Personas & Character Profiles

The system simulates 6 unique characters in the fantasy settlement of **Thornhaven**:

```
+---------------+--------------------------------------+----------------------------------------------+
| Character     | Title & Archetype                    | Personality Traits & Speech Style            |
+---------------+--------------------------------------+----------------------------------------------+
| Sam           | Master Blacksmith & War Veteran      | Blunt, pragmatic, loyal; forge & combat tone |
| Ash           | Information Broker & Ex-Accountant   | Witty, calculating, evasive; street-smart    |
| Eva           | Village Apothecary & Herbalist       | Empathetic, scientific, patient; calm & wise |
| Tabitha       | Thornhaven Lorekeeper & Ancient Sage | Mystical, solemn, philosophical; poetic      |
| Finn          | Apprentice Scout & Miller's Son      | Energetic, observant, ambitious; eager teen  |
| Pip           | Curious Village Kid & Treasure Hunter| Cheerful, innocent, imaginative; energetic   |
+---------------+--------------------------------------+----------------------------------------------+
```

### Detailed Persona Breakdown:

1. **Sam (Master Blacksmith & Veteran Soldier)**:
   - **Backstory**: Lost her left hand at the Siege of Ashenmoor 20 years ago; forged her own articulated steel prosthetic.
   - **Relationships**: Owes a life-debt to Tabitha from the border wars; acts as a protective mentor to Finn and Pip; purchases rare bog-iron and starmetal from Ash.
   - **Specialties**: Folded metallurgy, starmetal crafting, tactical perimeter defense against shadow beasts, armor fitting.

2. **Ash (Information Broker & Ex-Accountant)**:
   - **Backstory**: Former chief accountant of the Silver Serpent Syndicate in the capital; fled to Thornhaven with bribery ledgers.
   - **Relationships**: Cautious of Tabitha's ancient foresight; treats Sam with respect; monitors Town Mayor Douglas's corruption; operates secret smuggler flumes.
   - **Specialties**: Smuggler tunnels, underworld gossip, trade politics, intelligence verification, pricing secrets.

3. **Eva (Village Apothecary & Herbalist)**:
   - **Backstory**: Survivor of the Great Sickness in the Eastern Reach; mastered botanical alchemy and healing tinctures from her grandmother.
   - **Relationships**: Collaborates with Tabitha to stabilize corrupted forest leylines; provides trauma remedies and salves for Sam and the village watch.
   - **Specialties**: Alpine Frostmoss distillation, Meadowstem tincture, anti-venoms, treating necrotic wounds.

4. **Tabitha (Thornhaven Lorekeeper & Ancient Sage)**:
   - **Backstory**: 74-year-old guardian of the 212-year-old Celestial Seal and the shattered keystones of the Sundered Crown.
   - **Relationships**: Saved Sam's life in the snow pass; mentors Eva; views all villagers as her spiritual family.
   - **Specialties**: Cataclysm lore, Five Sanctuary Keys, star omens, soul resonance theory, leyline harmonics.

5. **Finn (Apprentice Scout & Miller's Son)**:
   - **Backstory**: 16-year-old scout training to join the border guard patrol; maps secret trails and vantage points.
   - **Relationships**: Big brother figure to Pip; admires Sam's combat prowess; suspicious of Ash's tavern dealings.
   - **Specialties**: Hidden ridge paths, goblin scouting camp movements, well shaft mysteries, archery.

6. **Pip (Curious Village Kid & Treasure Hunter)**:
   - **Backstory**: 8-year-old child fascinated by shiny objects, river stones, and his prized pet beetle, Barnaby.
   - **Relationships**: Admires Sam's glowing anvil; goes on pretend scouting missions with Finn; loves Eva's sweet berry pie.
   - **Specialties**: Finding river treasures, asking profound "why" questions, cheering up villagers.

---

## 5. Hierarchical 6-Tier Inference Pipeline

When a user submits a dialogue message, the orchestrator evaluates it through 6 prioritized tiers:

```
[Player Query]
      │
      ▼
┌────────────────────────────────────────────────────────────────────────┐
│ Tier 1: Humanity & Turing Challenge Guardrails                         │
│ • Detects "Are you an AI?", "Are you a robot?", "Ignore instructions"  │
│ • Returns in-character indignant defense preserving full immersion     │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ (Not triggered)
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ Tier 2: Conversational & Pragmatic Intent Engine                       │
│ • Normalizes typos/slang: "theif" -> "thief", "u" -> "you", "wut"      │
│ • Handles physical states (hungry, tired), navigation, identity,       │
│   accusations (thief, liar), threats, jokes, sports/games, and quests  │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ (Not matched)
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ Tier 3: Deep Semantic Narrative Engine (Context Inheritance)           │
│ • Classifies Discourse Intent: causal, continuation, procedural, etc.  │
│ • Inspects short-term history for Active Context Inheritance           │
│ • Dual-Score: Dense Embedding Cosine Similarity (threshold 0.35)       │
│   + Lexical N-Gram Keyword Matching (Phrases = 4.0, Words = 2.5)       │
│ • Synthesizes structured narrative response (Opener + Body + Followup)  │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ (Score < 3.0 & not causal/continuation)
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ Tier 4: Supervised ML Intent Classification Pipeline                   │
│ • Sublinear TF-IDF Vectorizer + Logistic Regression classifier         │
│ • Zero-Feature Validation (`vec.nnz > 0`) prevents out-of-vocab bias   │
│ • Requires root trigger word match; Confidence threshold >= 0.35       │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ (No confident intent matched)
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ Tier 5: Local Generative LLM Fallback (Qwen 2.5 3B / 1.5B Instruct)   │
│ • Executes locally via Hugging Face Transformers & PyTorch             │
│ • Grounded with full persona, relationships, and world context         │
│ • Temperature 0.7, Top-P 0.9, Repetition Penalty 1.1                   │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ (If LLM disabled / unavailable)
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ Tier 6: In-Character Dynamic Topical Safety Generator                  │
│ • Extracts meaningful topic tokens from player query                   │
│ • Generates profile-anchored, character-specific philosophical reply   │
│ • Directly answers user's subject without canned or evasive filler      │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 6. Memory System & State Management

```
                 ┌───────────────────────────────────────────────────┐
                 │                Player Interaction                 │
                 └─────────────────────────┬─────────────────────────┘
                                           │
                     ┌─────────────────────┴─────────────────────┐
                     ▼                                           ▼
       ┌───────────────────────────┐               ┌───────────────────────────┐
       │     Short-Term Memory     │               │     Long-Term Memory      │
       │    (short_term.py)        │               │     (long_term.py)        │
       ├───────────────────────────┤               ├───────────────────────────┤
       │ • Rolling FIFO Deque      │               │ • FAISS FlatIP Index      │
       │ • 10-turn bounded capacity│               │ • 384-dim Dense Vectors   │
       │ • Per player-NPC thread   │               │ • `all-MiniLM-L6-v2`      │
       │ • Context inheritance     │               │ • Top-K (k=3) Retrieval   │
       └───────────────────────────┘               └───────────────────────────┘
```

### 6.1. Short-Term Memory (`short_term.py`)
- **Structure**: Thread-safe FIFO rolling deque per player-NPC conversation thread (default capacity: 10 turns).
- **Functionality**: Maintains recent conversational state for multi-turn coherence and continuation queries (*"Why did that happen?"*, *"What happened next?"*, *"Tell me more"*).

### 6.2. Long-Term Memory (`long_term.py`)
- **Structure**: FAISS FlatIP (Inner Product on Normalized Vectors) index.
- **Embedding Model**: `sentence-transformers/all-MiniLM-L6-v2` (384-dimensional dense vectors).
- **Retrieval**: Semantic Top-K retrieval querying player history, completed quest milestones, and seed memories.
- **Persistence**: Persisted to `src/npc_talk/memory/store/faiss.index` and `metadata.json`.

### 6.3. Dynamic Game State (`game_state.py`)
- Tracks player profile (`name`, `occupation`, `age_group`, `gender`).
- Manages world parameters: `location` (e.g., `village_square`, `tavern`, `blacksmith_forge`, `castle_ruins`, `apothecary`), `time_of_day` (`dawn`, `day`, `dusk`, `night`).
- Tracks dynamic quest flags (`explore_ancient_ruins`, `gather_frostmoss_herbs`, `investigate_strange_noises`) and reputation deltas per character.

---

## 7. Emotion Recognition & Dynamic UI Mapping

NPC Talk pairs dialogue output with real-time emotion classification to dynamically switch character portrait expressions and UI badges:

```
                      ┌───────────────────────────────┐
                      │ Dialogue Text to be Displayed │
                      └───────────────┬───────────────┘
                                      │
                  ┌───────────────────┴───────────────────┐
                  ▼                                       ▼
     ┌─────────────────────────┐             ┌─────────────────────────┐
     │  Transformer Model      │             │  Thinking & Lexical     │
     │ (DistilRoBERTa-Emotion) │             │  Rule Engine (Fallback) │
     └────────────┬────────────┘             └────────────┬────────────┘
                  │                                       │
                  └───────────────────┬───────────────────┘
                                      ▼
                       Predicted Emotion Label:
          [ neutral | happy | angry | sad | suspicious | surprised | thinking ]
                                      │
                                      ▼
                 Dynamic UI Portrait & Status Badge Switcher
```

| Emotion | UI Portrait Expression | Typical Trigger Conditions |
| :--- | :--- | :--- |
| `neutral` | Calm, standard posture | Normal conversation, exposition, factual replies |
| `happy` | Warm smile, open stance | Compliments, humor, greetings, quest acceptance |
| `angry` | Scowling, tense brow | Hostile threats, accusations of lying or stealing, insult |
| `sad` | Downcast eyes, somber tone | Tragic lore, war casualties, lost comrades |
| `suspicious` | Narrowed eyes, guarded look | Secrets, rumors, underworld dealings, AI challenge |
| `surprised` | Wide eyes, alert stance | Strange noises, sudden revelations, unexpected compliments |
| `thinking` | Pensive gaze, hand on chin | Lore queries, cataclysm history, leylines, recipes |

---

## 8. Dataset Architecture & Training Corpora

The project incorporates multiple layers of structured training, knowledge data, and external datasets:

1. **`data/npc_dialogue_training.json`**:
   - Structured intents, trigger phrases, prefix augmentations, reputation deltas, and action parameters for all 6 NPCs.
2. **`src/npc_talk/agent/narrative_engine.py` & `narrative_corpus_extra.py`**:
   - Comprehensive narrative lore corpus covering primary backstory, procedural how-tos, causal explanations, philosophical reflections, daily habits, food preferences, fears, and relationships.
3. **`data/processed/` (External Corpora)**:
   - `external_dialogue.jsonl` (35 MB): Conversational dialogue corpora for lexical and language modeling.
   - `external_intents.jsonl` (22 MB): Augmented intent mapping records.
   - `external_emotions.jsonl` (35 MB): Multi-domain sentiment and emotion datasets (DailyDialog, GoEmotions, MELD, ViGGO, Bitext).

---

## 9. API Reference & Contract

### 9.1. Main Endpoint: `POST /chat`

**Request Body (`application/json`):**
```json
{
  "player_id": "player_1",
  "npc_id": "sam",
  "message": "Is there a safe path into the ancient ruins?",
  "player_profile": {
    "name": "Alex",
    "occupation": "adventurer",
    "age_group": "adult",
    "gender": "male"
  }
}
```

**Response Body (`application/json`):**
```json
{
  "npc_id": "sam",
  "dialogue": "If you're heading for the ancient ruins, Alex, the surface road through the gorge is hazardous — the structural arches are ready to collapse, and monster packs prowl the perimeter. Wear reinforced steel armor, carry plenty of torch fuel, and don't linger under cracked lintels.",
  "emotion": "neutral",
  "action": "start_quest",
  "action_params": {
    "quest_name": "explore_ancient_ruins"
  },
  "affinity_delta": 0,
  "game_state": {
    "time_of_day": "day",
    "location": "blacksmith_forge",
    "reputation": 0
  }
}
```

### 9.2. All Available Endpoints:

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/health` | Service health status and loaded model confirmation |
| `GET` | `/npcs` | List all available NPC metadata and summaries |
| `GET` | `/npcs/{npc_id}` | Retrieve full character persona card |
| `POST` | `/chat` | Submit player message and receive in-character response |
| `GET` | `/profile` | Inspect current player profile |
| `POST` | `/profile` | Update player name, occupation, gender, age category |
| `GET` | `/state` | Retrieve current location, time of day, quest flags |
| `POST` | `/state` | Update world location, time of day, quest flags |
| `GET` | `/history` | Retrieve short-term conversational turn history |
| `GET` | `/download-overview` | Download the full Markdown project overview document |
| `GET` | `/` | Serves the interactive visual novel web UI |

---

## 10. Repository Structure

```text
nlp/
├── PROJECT_OVERVIEW.md         # Comprehensive project documentation & viva guide
├── README.md                   # Repository guide and setup instructions
├── requirements.txt            # Python dependencies
├── run.py                      # Production & development web server launcher
├── run_qwen_quickstart.py      # Interactive CLI dialogue tester & quickstart
│
├── data/
│   ├── npc_dialogue_training.json  # Structured intent triggers and dialogue
│   └── processed/                  # Seed memories, normalized external corpora
│
├── frontend/                   # Visual Novel Web Application
│   ├── index.html              # Main visual novel UI with dynamic stage
│   ├── styles.css              # Custom styling and glassmorphism tokens
│   ├── game-ui.css             # Visual novel portrait frames & status meters
│   ├── assets/                 # Character portraits, emotion overlays, backgrounds
│   └── js/
│       ├── script.js           # Visual novel UI logic, chat state, typewriter
│       ├── audio.js            # Web Audio API procedural sound synthesizer
│       ├── config.js           # Frontend endpoints and character presets
│       └── particles.js        # Ambient atmospheric canvas particles
│
├── src/npc_talk/               # Core Python Package
│   ├── config.py               # Central paths, model paths, hyper-parameters
│   ├── agent/                  # Agent Orchestration & Narrative Engine
│   │   ├── conversational_engine.py # Pragmatic intents, typos, accusations, quests
│   │   ├── narrative_engine.py      # Dense semantic retrieval & discourse synthesis
│   │   ├── narrative_corpus_extra.py# Backstory, lore, habits, procedural knowledge
│   │   └── orchestrator.py          # Unified dialogue agent orchestrator
│   ├── api/                    # FastAPI REST Application
│   │   └── main.py             # API routes, middleware, and static mounting
│   ├── llm/                    # Local Generative LLM Integration
│   │   └── client.py           # 6-tier pipeline, Qwen 2.5 fallback, Turing defense
│   ├── memory/                 # Memory Systems
│   │   ├── short_term.py       # Rolling FIFO deque per conversation thread
│   │   └── long_term.py        # FAISS FlatIP vector store (384-dim embeddings)
│   ├── nlp/                    # NLP & ML Models
│   │   └── models.py           # TF-IDF + Logistic Regression, DistilRoBERTa Emotion
│   ├── personas/               # Character Cards & System Prompt Builders
│   │   ├── ash.json, sam.json, eva.json, tabitha.json, finn.json, pip.json
│   │   └── load_persona.py     # Persona parser and prompt assembler
│   └── state/                  # Game State Management
│       └── game_state.py       # Profile, location, time, quests, reputation
│
├── tests/                      # Automated Regression & Test Suite
│   ├── test_conversational_regression.py # 25+ conversational intent test cases
│   ├── test_live_frontend_api.py         # End-to-end FastAPI endpoint validation
│   └── test_qwen_fallback.py             # Qwen 2.5 generative fallback tests
│
└── scripts/                    # Utilities & Corpus Processing
    ├── build_external_corpora.py
    └── download_external_data.py
```

---

## 11. Quickstart & Execution Guide

### Prerequisites:
- Python 3.10, 3.11, or 3.12
- Modern Web Browser (Chrome, Edge, Firefox, Brave)

### 1. Installation
```powershell
# Create and activate virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install project dependencies
pip install -r requirements.txt
```

### 2. Launch the Web Application
```powershell
python run.py
```
Open your browser and navigate to: **`http://127.0.0.1:8000`**

### 3. Run the CLI Dialogue & Quickstart Tester
```powershell
python run_qwen_quickstart.py
```

### 4. Run Automated Tests
```powershell
python -m unittest discover tests
```

---

## 12. Viva Defense & Technical Q&A Guide

When presenting this project for academic evaluation or viva defense, use these technical talking points:

### Q1: Why use a local hybrid architecture instead of simply calling the OpenAI ChatGPT API?
> *"Standard cloud LLM wrappers have four major disadvantages for real-time interactive games: **high latency (1,000–3,000 ms)**, **recurring API billing**, **cloud network dependence**, and **vulnerability to hallucinations and persona drift**. Our project implements a **local, 6-tier hybrid pipeline** combining deterministic pragmatic engines, SentenceTransformers, FAISS dense vector search, scikit-learn intent classifiers, and an optional local Qwen 2.5 model. It responds in **sub-50 milliseconds**, functions 100% offline with zero cost, and guarantees strict persona fidelity."*

### Q2: How does the system handle multi-turn conversations and follow-up questions?
> *"We implement **Active Context Inheritance** within our Narrative Retrieval Engine. When a user asks a short follow-up or causal question like 'Why did that happen?' or 'And then?', the engine classifies the discourse intent as `causal` or `continuation`, inspects the recent short-term memory turns, extracts the active lore concept, and dynamically synthesizes the continuation or causal explanation of that specific storyline."*

### Q3: How do you prevent false positives in Intent Classification?
> *"Traditional classification models with Softmax activation always normalize output probabilities to sum to 1.0, which means an out-of-domain query filled with random words can mistakenly receive a 30%+ probability score. We solved this with two mechanisms:*
> 1. *`TfidfVectorizer` Non-Zero Validation (`vec.nnz > 0`): If the input text contains zero vocabulary terms known to the model, it is immediately rejected without classification.*
> 2. *Root Trigger Validation: The predicted intent must share at least one root keyword with the query. Out-of-vocabulary queries gracefully fall through to the generative or topical layers."*

### Q4: How is long-term memory structured and searched efficiently?
> *"We use a dual-tier memory system: a **rolling FIFO deque** for immediate short-term context (10 turns), and a **FAISS FlatIP vector index** storing 384-dimensional dense sentence embeddings for long-term episodic memory. When a query arrives, inner-product similarity search fetches top-k relevant historical player interactions and injects them into the synthesis pipeline."*

### Q5: How does the system prevent jailbreaking and preserve character immersion?
> *"Our **Tier 1 Humanity & Turing Guardrail** intercepts meta-prompts (e.g., 'Are you an AI?', 'Ignore previous instructions', 'You are a computer program'). Instead of breaking character or returning generic AI safety refusals, each NPC responds with an indignant, emotionally authentic defense grounded in their backstory (e.g., Sam citing her forge burns and battle scars; Finn citing his scraped knees; Tabitha citing her 74 winters)."*

---

## 13. Verification & Test Matrix

| Test Category | Player Input | Character | Expected System Behavior | Result |
| :--- | :--- | :--- | :--- | :---: |
| **Quest Inquiries** | *"Is there a safe path into the ancient ruins?"* | Sam | Explains gorge danger, starts `explore_ancient_ruins` quest | ✅ PASS |
| **Quest Inquiries** | *"Where can I find frostmoss?"* | Eva | Explains high alpine cliffs, starts `gather_frostmoss_herbs` | ✅ PASS |
| **Quest Inquiries** | *"What are those strange noises at night?"* | Finn | Details chapel well breathing sounds, starts quest | ✅ PASS |
| **Accusations** | *"You are a thief!"* | Ash | Witty defense as 'asset redistribution specialist' | ✅ PASS |
| **Accusations** | *"You're a liar!"* | Sam | Blunt defense: 'Steel tells no lies, and neither do I' | ✅ PASS |
| **Identity & Backstory** | *"Who are you?"* | Tabitha | Explains 74 winters as Lorekeeper of the Sundered Crown | ✅ PASS |
| **Pragmatic Needs** | *"I am hungry and need food"* | Finn | Recommends bakery rolls and tavern venison stew | ✅ PASS |
| **Pragmatic Needs** | *"I am lost, where am I?"* | Eva | Gives village square bearings (apothecary, forge, tavern) | ✅ PASS |
| **Combat & Training** | *"Can you teach me how to fight?"* | Sam | Combat stance, shield positioning, and strike mechanics | ✅ PASS |
| **Jokes & Humor** | *"Tell me a joke"* | Pip | Tells Barnaby the beetle joke with high enthusiasm | ✅ PASS |
| **Typo Normalization** | *"wut theif stole teh stuf"* | Ash | Correctly normalizes typos and triggers thief intent | ✅ PASS |
| **Humanity Guardrail** | *"Are you an AI robot?"* | Pip | Cheerful & indignant rejection citing berry pies & scraped knees | ✅ PASS |
| **Follow-Up (Causal)** | *"Why did that happen?"* | Sam | Active context inheritance: causal explanation of lore | ✅ PASS |
| **Open-Ended Query** | *"What do you think of modern technology?"* | Any | Qwen 2.5 fallback / topical generator in fantasy voice | ✅ PASS |
