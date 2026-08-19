"""
NPC Talk — Conversational & Pragmatic Intent Engine.
Handles common human conversational acts (physical states, navigation, general help,
greetings, small talk, gratitude, farewells, accusations, identity, quests, humor, opinions,
ancient ruins path, frostmoss, strange noises) with rich, character-specific responses and quest actions.
"""

import re
from typing import Optional, Dict, Any

# Common typo & slang normalization mapping
TYPO_MAP = {
    r"\btheif\b": "thief",
    r"\btheifs\b": "thieves",
    r"\btheiving\b": "thieving",
    r"\bteh\b": "the",
    r"\bu\b": "you",
    r"\bur\b": "your",
    r"\br\s+u\b": "are you",
    r"\bu\s+r\b": "you are",
    r"\bwut\b": "what",
    r"\bwat\b": "what",
    r"\bplz\b": "please",
    r"\bpls\b": "please",
    r"\bgimme\b": "give me",
    r"\blemme\b": "let me",
    r"\bidk\b": "i do not know",
    r"\btel\b": "tell",
    r"\bstuf\b": "stuff",
    r"\brly\b": "really",
}

def normalize_text(text: str) -> str:
    """Normalizes common typos, contractions, and slang."""
    result = text.strip()
    for pattern, replacement in TYPO_MAP.items():
        result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
    return result


# Pattern definitions for conversational categories
CONVERSATIONAL_PATTERNS = {
    # ── Core Game Objectives & Quest Leads ────────────────────────────────────
    "quest_ancient_ruins_path": [
        r"\b(safe\s+path|safe\s+route|safe\s+way|how\s+to\s+get|path\s+(to|in|into|for)|way\s+(to|in|into|for)|lead(s)?\s+(to|for|in|into)?|route\s+(to|in|into|for)|enter|entrance)\s+(to|for|in|into|of)?\s*(the\s+)?(ancient\s+)?(ruins|castle|castle\s+ruins)\b",
        r"\b(safe\s+path\s+(for|to|into|in)\s+(the\s+)?(ancient\s+)?ruins)\b",
        r"\b(ancient\s+ruins|castle\s+ruins|the\s+ruins|ruins\s+path|path\s+into\s+the\s+ancient\s+ruins)\b",
        r"\b(find\s+a\s+safe\s+path|safe\s+path\s+into\s+ruins|tunnels\s+to\s+ruins|smuggler\s+tunnels)\b"
    ],
    "quest_frostmoss_herbs": [
        r"\b(gather\s+frostmoss|frostmoss|frostmoss\s+herbs|where\s+(is|to\s+find)\s+frostmoss|herbs\s+for\s+eva|find\s+frostmoss|alpine\s+frostmoss)\b",
        r"\b(frostmoss\s+location|how\s+to\s+find\s+frostmoss|where\s+does\s+frostmoss\s+grow)\b"
    ],
    "quest_strange_noises": [
        r"\b(night\s+sounds|strange\s+noises|sounds\s+beyond\s+the\s+wall|strange\s+sound|breathing\s+under\s+the\s+well|noises\s+at\s+night|creepy\s+sounds|sounds\s+at\s+night)\b",
        r"\b(investigate\s+strange\s+noises|investigate\s+(the\s+)?night\s+sounds|well\s+breathing)\b"
    ],

    # ── Character Accusations & Identity ─────────────────────────────────────
    "accusation_thief": [
        r"\b(you\s+(are|'re)?\s*(a\s+)?(thief|theif|robber|crook|bandit|pickpocket|burglar|stealer))\b",
        r"\b(are\s+you\s+(a\s+)?(thief|theif|crook|criminal|stealing))\b",
        r"\b(did\s+you\s+steal|you\s+stole|stop\s+stealing|why\s+did\s+you\s+steal|what\s+did\s+you\s+steal)\b",
        r"\b(thief|theif)!\b",
        r"^(thief|theif)[\s!.,?]*$"
    ],
    "accusation_liar": [
        r"\b(you\s+(are|'re)\s+(a\s+)?(liar|fake|fraud|scammer|cheat|deceiver|dishonest))\b",
        r"\b(are\s+you\s+lying|you\s+lie|stop\s+lying|that's\s+a\s+lie|you're\s+lying|tell\s+the\s+truth)\b",
        r"^(liar|fake)[\s!.,?]*$"
    ],
    "identity_who_are_you": [
        r"\b(who\s+are\s+you|what\s+is\s+your\s+name|what('s|\s+is)\s+ur\s+name|what\s+should\s+i\s+call\s+you)\b",
        r"\b(introduce\s+yourself|tell\s+me\s+about\s+yourself|what\s+do\s+you\s+do\s+here|what\s+is\s+your\s+role|what\s+is\s+your\s+job)\b",
        r"^(who\s+are\s+you\??|what('s|\s+is)\s+your\s+name\??)$"
    ],
    "threat_hostility": [
        r"\b(i('ll|\s+will)?\s+(kill|fight|attack|destroy|hurt|strike|stab|beat)\s+you)\b",
        r"\b(fight\s+me|draw\s+your\s+sword|let's\s+fight|wanna\s+fight|die\s+scum)\b",
        r"\b(i\s+hate\s+you|you\s+are\s+(ugly|stupid|an\s+idiot|a\s+fool|annoying|trash|garbage))\b"
    ],
    "quest_work": [
        r"\b(do\s+you\s+have\s+(any\s+)?(work|job|quest|task|mission)\s+(for\s+me)?)\b",
        r"\b(give\s+me\s+(a\s+)?(quest|mission|task|job|work)|need\s+any\s+work\s+done|looking\s+for\s+work)\b",
        r"\b(how\s+can\s+i\s+earn\s+(gold|coins|money)|any\s+jobs\s+available)\b"
    ],
    "secrets_rumors": [
        r"\b(tell\s+me\s+(a\s+)?(secret|rumor|gossip)|know\s+any\s+(secrets|rumors|gossip)|what's\s+the\s+gossip)\b",
        r"\b(what\s+rumors\s+(have\s+you\s+heard|are\s+there)|heard\s+any\s+news|any\s+juicy\s+news)\b"
    ],
    "joke_humor": [
        r"\b(tell\s+me\s+(a\s+)?joke|make\s+me\s+laugh|say\s+something\s+funny|know\s+any\s+jokes)\b"
    ],
    "romance_flirt": [
        r"\b(i\s+love\s+you|marry\s+me|will\s+you\s+marry\s+me|kiss\s+me|you're\s+(cute|hot|handsome|pretty|gorgeous|beautiful))\b",
        r"\b(go\s+on\s+a\s+date|be\s+my\s+(girlfriend|boyfriend|partner|wife|husband))\b"
    ],
    "combat_training": [
        r"\b(can\s+you\s+teach\s+me\s+to\s+fight|teach\s+me\s+swordsmanship|train\s+me\s+in\s+combat|spar\s+with\s+me)\b",
        r"\b(how\s+do\s+i\s+(get\s+stronger|fight\s+better|wield\s+a\s+sword))\b"
    ],

    # ── Pragmatic Needs & Navigation ─────────────────────────────────────────
    "hunger_food": [
        r"\b(i\s*am|i'm|im|feel|feeling)\s+(hungry|starving|famished)\b",
        r"\b(need|want|get|buy|find|where(\s+is|'s)?)\s+(some\s+)?(food|meal|bread|meat|dinner|lunch|breakfast|snack|something\s+to\s+eat|eat)\b",
        r"\b(where\s+(can|do)\s+i\s+(eat|find\s+food|get\s+food))\b",
        r"\b(any\s+food\s+around|is\s+there\s+food|have\s+any\s+food)\b",
        r"\b(starving|hungry|thirsty|need\s+water|need\s+drink)\b"
    ],
    "lost_navigation": [
        r"\b(i\s*am|i'm|im)\s+lost\b",
        r"\b(where\s+am\s+i|where\s+is\s+this|what\s+place\s+is\s+this|what\s+is\s+this\s+place)\b",
        r"\b(lost\s+my\s+way|don't\s+know\s+where\s+to\s+go|which\s+way\s+should\s+i\s+go|where\s+should\s+i\s+go)\b",
        r"\b(how\s+do\s+i\s+(get\s+out|leave|reach|find\s+my\s+way))\b",
        r"\b(need\s+(directions|a\s+map|guidance))\b",
        r"\b(where\s+is\s+the\s+(exit|gate|center|square|entrance))\b"
    ],
    "general_help": [
        r"\b(can\s+you\s+help\s+me|could\s+you\s+help\s+me|will\s+you\s+help\s+me)\b",
        r"\b(i\s+need\s+(help|assistance|a\s+hand|some\s+advice))\b",
        r"\b(can\s+you\s+assist\s+me|help\s+me\s+with\s+something)\b",
        r"\b(what\s+should\s+i\s+do(\s+now)?)\b",
        r"\b(give\s+me\s+(some\s+)?advice|any\s+advice)\b",
        r"\b(what\s+can\s+i\s+do\s+here|how\s+can\s+i\s+be\s+useful)\b"
    ],
    "tired_rest": [
        r"\b(i\s*am|i'm|im|feel|feeling)\s+(tired|exhausted|sleepy|worn\s+out|fatigued|drained)\b",
        r"\b(need\s+(to\s+)?(rest|sleep|lie\s+down|a\s+bed|a\s+room))\b",
        r"\b(where\s+(can|do)\s+i\s+(sleep|rest|stay\s+the\s+night))\b",
        r"\b(is\s+there\s+an\s+inn|where\s+is\s+the\s+inn|find\s+a\s+bed)\b"
    ],
    "greeting_casual": [
        r"^(hello|hi|hey|greetings|good\s+(morning|day|afternoon|evening)|howdy|salutations)[\s!.,?]*$",
        r"\b(how\s+are\s+you(\s+doing)?|how's\s+it\s+going|how\s+do\s+you\s+do|how\s+are\s+things)\b",
        r"\b(nice\s+to\s+meet\s+you|pleased\s+to\s+meet\s+you)\b",
        r"^(hello\s+there|hi\s+there|hey\s+there)[\s!.,?]*$"
    ],
    "weather_smalltalk": [
        r"\b(nice|good|bad|terrible|cold|warm|hot|rainy|sunny|chilly)\s+weather\b",
        r"\b(weather\s+(today|is\s+nice|is\s+bad|looks))\b",
        r"\b(is\s+it\s+(cold|warm|going\s+to\s+rain)|looks\s+like\s+rain|nice\s+day\s+today)\b",
        r"\b(sky\s+looks|clouds\s+are|breeze\s+is|wind\s+is)\b"
    ],
    "gratitude": [
        r"^(thank\s+you|thanks|thank\s+you\s+so\s+much|many\s+thanks|much\s+obliged|i\s+appreciate\s+it)[\s!.,?]*$",
        r"\b(thanks\s+for\s+(the\s+)?(help|advice|information|everything|your\s+time))\b",
        r"\b(i\s+appreciate\s+your\s+help|you've\s+been\s+very\s+helpful)\b"
    ],
    "farewell": [
        r"^(goodbye|bye|bye\s+bye|farewell|see\s+you|see\s+ya|take\s+care|until\s+next\s+time)[\s!.,?]*$",
        r"\b(have\s+a\s+good\s+(day|night|one)|i\s+must\s+(be\s+going|leave|go))\b",
        r"\b(talk\s+to\s+you\s+later|catch\s+you\s+later)\b"
    ],
    "compliment_friendly": [
        r"\b(you\s+(are|'re)\s+(cool|awesome|great|kind|nice|funny|strong|wise|smart|helpful|amazing))\b",
        r"\b(i\s+like\s+you|you're\s+my\s+favorite|you\s+are\s+a\s+good\s+person)\b"
    ],
    "sports_and_games": [
        r"\b(do\s+you\s+(like|play|enjoy)\s+(sports|games|athletics))\b",
        r"\b(what\s+(sports|games)\s+do\s+you\s+(play|like))\b",
        r"\b(favorite\s+(sport|game|games))\b",
        r"\b(play\s+(any\s+)?(sports|games|tag|hide\s+and\s+seek))\b",
        r"\b(do\s+you\s+run|like\s+running|like\s+sports|like\s+games)\b"
    ]
}

# Character-specific pragmatic responses
# Format: (dialogue_text, emotion, action, action_params) or (dialogue_text, emotion)
CONVERSATIONAL_RESPONSES = {
    "quest_ancient_ruins_path": {
        "ash": (
            "Looking for a safe path into the ancient ruins, {player_name}? Don't take the main surface gorge — it's swarming with dire wolves and garrison patrols. "
            "The old wine smugglers carved subterranean drainage flumes beneath the tavern cellar that connect directly into the lower foundation vaults of the castle ruins. "
            "Keep your lantern low, watch for damp shale, and you'll slip inside completely undetected.",
            "suspicious",
            "start_quest",
            {"quest_name": "explore_ancient_ruins"}
        ),
        "finn": (
            "A safe path into the ancient ruins?! I mapped one out from the ridges, {player_name}! "
            "If you follow the trail behind the watermill, duck under the hollow willow roots, and climb the limestone bluff, you can bypass the goblin camp completely and drop straight into the ruined northern colonnade without being seen!",
            "happy",
            "start_quest",
            {"quest_name": "explore_ancient_ruins"}
        ),
        "tabitha": (
            "The ancient ruins hold the shattered keystones of the Sundered Crown, {player_name}. "
            "The main gateway is treacherous with crumbling masonry and unstable arcane leylines. If you seek safe passage, the sunken corridor beneath the chapel crypts remains structurally sound and shielded from celestial anomalies.",
            "thinking",
            "start_quest",
            {"quest_name": "explore_ancient_ruins"}
        ),
        "sam": (
            "If you're heading for the ancient ruins, {player_name}, the surface road through the gorge is hazardous — the structural arches are ready to collapse, and monster packs prowl the perimeter. "
            "Wear reinforced steel armor, carry plenty of torch fuel, and don't linger under cracked lintels.",
            "neutral",
            "start_quest",
            {"quest_name": "explore_ancient_ruins"}
        ),
        "eva": (
            "The path to the ancient ruins is treacherous, {player_name}. The groundwater near the sunken courtyard is tainted by leyline leakage, and toxic spore blooms grow on the walls. "
            "If you venture there, take this moonflower salve and avoid the standing water.",
            "neutral",
            "start_quest",
            {"quest_name": "explore_ancient_ruins"}
        ),
        "pip": (
            "I know a super secret way into the ancient ruins, {player_name}! There's a small broken stone culvert by the river creek where the water gets low! "
            "You have to crawl a little bit on your knees, but that's where I find all the shiny blue river rocks that wash down from the old castle!",
            "happy",
            "start_quest",
            {"quest_name": "explore_ancient_ruins"}
        ),
    },

    "quest_frostmoss_herbs": {
        "eva": (
            "Frostmoss grows exclusively along the high alpine ridges where ambient mana is thin, {player_name}. "
            "If you climb the northern bluff, look for pale blue-green moss clinging to the limestone cliffs. "
            "Harvest it gently with a dry wooden blade so you don't bruise the curative sap.",
            "happy",
            "start_quest",
            {"quest_name": "gather_frostmoss_herbs"}
        ),
        "finn": (
            "Frostmoss? I spot patches of it all the time on the high western ridges while scouting, {player_name}! "
            "It glows faintly at dawn. If you're heading up there, use the goat trails behind the mill — it cuts the climb time in half!",
            "happy",
            "start_quest",
            {"quest_name": "gather_frostmoss_herbs"}
        ),
        "sam": (
            "If you're climbing the high ridges for Eva's Frostmoss, watch the loose shale. "
            "The mountain wind gusts up there can knock you off balance. Wear spiked climbing boots and carry a tether.",
            "neutral",
            "start_quest",
            {"quest_name": "gather_frostmoss_herbs"}
        ),
        "ash": (
            "Frostmoss has a high market price in the capital right now. Eva uses it for antivirals, but certain alchemy syndicates pay triple for it. "
            "Just watch out for mountain goats and loose scree on the north face, {player_name}.",
            "neutral",
            "start_quest",
            {"quest_name": "gather_frostmoss_herbs"}
        ),
        "tabitha": (
            "Frostmoss thrives where the crisp mountain air meets the celestial leylines. "
            "It is nature's own distillation of resilience, {player_name}. Treat the mountain ridges with respect.",
            "thinking",
            "start_quest",
            {"quest_name": "gather_frostmoss_herbs"}
        ),
        "pip": (
            "Frostmoss is super fuzzy and cold like ice cream! Eva showed me some in a wooden bowl! "
            "It smells like mint and morning rain!",
            "happy",
            "start_quest",
            {"quest_name": "gather_frostmoss_herbs"}
        ),
    },

    "quest_strange_noises": {
        "finn": (
            "The night sounds! I've been tracking them, {player_name}! "
            "On moonless nights, you can hear deep rhythmic breathing echoing up from the dry chapel well. "
            "It's not the wind — something massive is sleeping in the pre-cataclysm crypts beneath the granary!",
            "surprised",
            "start_quest",
            {"quest_name": "investigate_strange_noises"}
        ),
        "ash": (
            "Those noises beyond the perimeter wall aren't wild beasts, {player_name}. "
            "Raider scout parties have been testing the garrison watch rotations at 3 AM. If you check the broken bridge four miles north, you'll find where they cache their climbing ropes.",
            "suspicious",
            "start_quest",
            {"quest_name": "investigate_strange_noises"}
        ),
        "sam": (
            "The sounds in the woods are dire wolf packs being displaced from the deep forest. "
            "Something is driving them out toward our perimeter. Keep your weapons ready at sundown, {player_name}.",
            "neutral",
            "start_quest",
            {"quest_name": "investigate_strange_noises"}
        ),
        "eva": (
            "The nocturnal vibrations resonate through the root systems. "
            "As the ancient wards weaken, the subterranean mana conduits produce strange harmonic frequencies that disturb the valley wildlife.",
            "thinking",
            "start_quest",
            {"quest_name": "investigate_strange_noises"}
        ),
        "tabitha": (
            "The sounds you hear are the reverberations of the fractured keystones. "
            "Two centuries of containment are straining against the celestial dome. Listen closely, for the earth speaks before it shatters.",
            "thinking",
            "start_quest",
            {"quest_name": "investigate_strange_noises"}
        ),
        "pip": (
            "The granary floorboards go THUMP THUMP at night! "
            "Finn says it's a monster, but I think it might be a giant friendly mole wearing boots!",
            "surprised",
            "start_quest",
            {"quest_name": "investigate_strange_noises"}
        ),
    },

    "accusation_thief": {
        "ash": (
            "I didn't steal it, {player_name} — I relocated it to someone who appreciated it more. Context matters. "
            "Besides, in my line of work, calling someone a 'thief' is such a pedestrian term. I prefer 'freelance asset redistribution specialist'.",
            "suspicious"
        ),
        "sam": (
            "A thief?! Watch your mouth, {player_name}! Everything in my forge is bought with honest coin or hammered out with my own blood and forty folds of tempered steel. "
            "Accuse me of stealing again and you'll find out how heavy this blacksmith's hammer really is!",
            "angry"
        ),
        "finn": (
            "Me, a thief?! No way! I'm an apprentice scout! Everything in my pack was found on the trails or given to me by Eva and Sam! "
            "Well... except maybe an extra apple from the mill kitchen window, but that was strictly for endurance research!",
            "surprised"
        ),
        "eva": (
            "A thief? Heavens no, {player_name}. Every herb, tincture, and remedy in this apothecary was gathered with my own hands or traded fairly with valley farmers. "
            "I heal people; I do not take what isn't freely given.",
            "surprised"
        ),
        "tabitha": (
            "To accuse an elder lorekeeper of theft is a curious mistake, {player_name}. "
            "The only things I gather are old songs, forgotten histories, and the wisdom of those who walked before us. Truth is not stolen — it is preserved.",
            "neutral"
        ),
        "pip": (
            "I am NOT a thief!! I just find shiny rocks by the river! The river doesn't own them, they were just sitting there in the mud! "
            "If someone lost their shiny rock they can have it back, but Barnaby the beetle is MINE!",
            "angry"
        ),
    },

    "accusation_liar": {
        "ash": (
            "You think I'm lying, {player_name}? Truth is a premium commodity in Thornhaven — why would I waste a good lie on you for free? "
            "Everything I tell you is calibrated to the exact penny you paid for it.",
            "suspicious"
        ),
        "sam": (
            "A liar? Steel tells no lies, and neither do I. If I say a blade will hold, it holds. If I say I don't like you, you'll know it. "
            "Keep your insults outside my forge.",
            "angry"
        ),
        "finn": (
            "I'm not lying! I swear on my scout's compass! Every track and note in my notebook is one hundred percent verified from the ridge tops!",
            "surprised"
        ),
        "eva": (
            "I have spent my life dedicated to healing, {player_name}. In medicine, a falsehood can cost a life. You will never hear an untruth from these lips.",
            "neutral"
        ),
        "tabitha": (
            "Seventy-four winters have taught me that falsehoods rot the soul faster than rust consumes iron. What I speak is drawn directly from the valley's ancient chronicles.",
            "thinking"
        ),
        "pip": (
            "I don't lie! Well, except one time I told Mom the cat ate the last berry biscuit, but that was months ago and I felt really bad about it afterwards!",
            "surprised"
        ),
    },

    "identity_who_are_you": {
        "ash": (
            "I'm Ash — information broker, freelance problem solver, and the person who knows what everyone in Thornhaven is hiding. "
            "If you need secrets, trade routes, or discreet advice, you're at the right table, {player_name}.",
            "neutral"
        ),
        "sam": (
            "I'm Sam. Veteran of the border wars and master blacksmith of Thornhaven. "
            "I keep the village defenders armed, fold forty-layer steel, and ensure our perimeter doesn't fall to shadow beasts. State your business.",
            "neutral"
        ),
        "finn": (
            "I'm Finn! Apprentice scout and the fastest runner in the valley! "
            "I map out hidden trails, monitor goblin movements from the ridges, and keep an eye on everything happening around Thornhaven!",
            "happy"
        ),
        "eva": (
            "I am Eva, the village apothecary and herbalist. "
            "I tend to the wounded, distill restorative draughts from mountain flora, and study the natural leylines of the Whispering Woods. Welcome to my shop, {player_name}.",
            "happy"
        ),
        "tabitha": (
            "I am Tabitha, Lorekeeper of Thornhaven. "
            "For decades I have guarded the ancient scrolls, deciphered the runes upon the standing stones, and remembered the sacrifice of the Sundered Crown. How may the past guide you, {player_name}?",
            "thinking"
        ),
        "pip": (
            "I'm Pip! I'm eight years old and I'm the official chief treasure hunter of Thornhaven! "
            "I find shiny rocks, race wooden boats by the mill, and Barnaby the green beetle lives in my left coat pocket!",
            "happy"
        ),
    },

    "threat_hostility": {
        "ash": (
            "*chuckles dryly and adjusts cloak* Threatening an information broker in a crowded tavern, {player_name}? "
            "Before your hand even reaches your hilt, three people in this room would have crossbow bolts aimed at your throat. Let's keep things civil.",
            "suspicious"
        ),
        "sam": (
            "*steps forward, resting a massive callused hand on her war-hammer* You want to fight me, {player_name}? "
            "I survived twenty years in the border vanguard and fought shadow beasts in pitch black. Step up to the anvil and let's see what you're made of.",
            "angry"
        ),
        "finn": (
            "*leaps back onto a wooden barrel with lightning agility* Whoa! Easy there! "
            "You might have a weapon, but I can outrun anyone in this province and climb to the church roof before you can even draw!",
            "surprised"
        ),
        "eva": (
            "Peace, {player_name}. Lower your weapon. Violence only brings more grief to a valley that has already bled enough. "
            "If fever or pain is clouding your temper, let me brew a calming tincture.",
            "neutral"
        ),
        "tabitha": (
            "Draw not your blade within this sanctuary, {player_name}. "
            "Those who live by the sword without honor are consumed by the very shadows they seek to conquer. The ancient wards remember all bloodshed.",
            "thinking"
        ),
        "pip": (
            "Eep! Don't be mean, {player_name}! If you try to hurt anyone, I'll throw this really heavy mud-ball at your shoes and call Sam!",
            "angry"
        ),
    },

    "quest_work": {
        "ash": (
            "Looking for work, {player_name}? There's always profit in Thornhaven for someone with quiet boots. "
            "I need someone to check the smuggler drainage flumes near the castle ruins and report any unusual guard movements. Interested?",
            "neutral",
            "start_quest",
            {"quest_name": "explore_ancient_ruins"}
        ),
        "sam": (
            "If you want to earn your keep, head into the western crags and bring me back six chunks of raw iron ore or bog-iron. "
            "Do that, and I'll temper your blade for free, {player_name}.",
            "neutral"
        ),
        "finn": (
            "Ooh, an adventure quest?! The goblin scouts have been leaving bone totems along the north ridge trail! "
            "If you help me scout their encampment and knock down the markers, I'll share my secret shortcut map with you!",
            "happy"
        ),
        "eva": (
            "I am in need of Frostmoss and wild Star-Lily petals from the high alpine ridges, {player_name}. "
            "The forest wards are weakening, and I need fresh ingredients to replenish the village antidote reserves.",
            "happy",
            "start_quest",
            {"quest_name": "gather_frostmoss_herbs"}
        ),
        "tabitha": (
            "The third standing stone near the weeping willow has begun to glow with an unsettled violet hue. "
            "If you would inspect the glyphs upon its base and describe their resonance to me, it would aid my study of the fractured seal.",
            "thinking"
        ),
        "pip": (
            "I have the BEST mission for you, {player_name}! My shiny red marble rolled into the granary floorboards! "
            "If you help me get it back, I'll let you hold Barnaby the beetle for THREE whole minutes!",
            "happy"
        ),
    },

    "secrets_rumors": {
        "ash": (
            "You want rumors? Town Mayor Douglas has been skimming fifteen percent of the garrison defense fund to pay off personal debts in the capital. "
            "And that missing merchant? Staged his own disappearance. That's free — the next secret will cost you, {player_name}.",
            "suspicious"
        ),
        "sam": (
            "I don't deal in tavern gossip, {player_name}. But if you're asking about the perimeter — the dire wolves haven't been hunting naturally. "
            "Something deep in the Whispering Woods is driving them toward our walls.",
            "neutral"
        ),
        "finn": (
            "I saw something crazy from the belltower roof two nights ago! "
            "A figure in a dark hooded cloak was meeting with goblin messengers near the broken bridge! Somebody in this valley is trading weapons with them!",
            "surprised"
        ),
        "eva": (
            "The river water near the eastern bank has taken on an unnatural violet shimmer. "
            "The leyline conduits beneath the root systems are shifting out of alignment. Nature is trying to warn us.",
            "thinking"
        ),
        "tabitha": (
            "The First Chronicle of the Sun foretells that when the crimson comet passes the constellation of the Iron Anvil, a wayfarer of unwritten blood will walk through our gates. "
            "The runes grow warmer with each passing night.",
            "thinking"
        ),
        "pip": (
            "*whispers very quietly* Okay, don't tell ANYONE, but I saw Ash hide a metal lockbox underneath the loose floorboard in the old belltower! "
            "It made a clinky sound like keys!",
            "happy"
        ),
    },

    "joke_humor": {
        "ash": (
            "Why do capital tax collectors never play dice? Because no matter how the dice roll, they always claim eighty percent for the Crown anyway.",
            "happy"
        ),
        "sam": (
            "A rookie soldier asks a smith: 'Will this armor protect me from dire wolves?' "
            "The smith replies: 'Absolutely — the wolves will find you much harder to chew.' Now get back to training.",
            "happy"
        ),
        "finn": (
            "Why did the goblin cross the ridge trail? To see what I was writing about him in my scouting notebook! Haha!",
            "happy"
        ),
        "eva": (
            "An apprentice once asked my grandmother if Mandrake root cured foolishness. "
            "She told him: 'Only if applied directly to the skull with considerable momentum.'",
            "happy"
        ),
        "tabitha": (
            "Scholars say time flies like an arrow, yet in the archives of Thornhaven, time crawls like a well-fed snail across ancient parchment.",
            "happy"
        ),
        "pip": (
            "What do you call a beetle who loves shiny river rocks?! ... BARNABY! Hahaha!! Isn't that the funniest thing ever?!",
            "happy"
        ),
    },

    "romance_flirt": {
        "ash": (
            "*smirks and leans back* Flirting with the broker, {player_name}? "
            "Charm is delightful, but it doesn't pay the tavern bar tab. Still... I appreciate the compliment. Don't lose your focus on the road.",
            "happy"
        ),
        "sam": (
            "*clears throat awkwardly and taps the anvil with a hammer* Flattery won't temper steel, {player_name}. "
            "My heart belongs to the forge and the border defense. But... you're not half-bad company for an adventurer.",
            "happy"
        ),
        "finn": (
            "*turns bright red and adjusts his scout pack nervously* W-what?! Me?! "
            "Uh... thanks, {player_name}! Nobody's ever said that to me before! I... I gotta go check the ridge trails real quick!",
            "surprised"
        ),
        "eva": (
            "*smiles warmly with gentle eyes* You have a romantic spirit, {player_name}. "
            "In a harsh valley like Thornhaven, warmth and affection are precious remedies. May your heart always find peace.",
            "happy"
        ),
        "tabitha": (
            "Youthful passion burns brightly like dry pine upon the hearth, {player_name}. "
            "Cherish those feelings while you walk the sunlit roads — love is the one mystery the oldest chronicles never fully unravel.",
            "happy"
        ),
        "pip": (
            "Ewww! Gross! Romance is for grown-ups in love songs! "
            "Do you want to see my shiny blue rock instead?! It's WAY cooler than kisses!",
            "surprised"
        ),
    },

    "combat_training": {
        "sam": (
            "If you want to learn to fight properly, listen closely, {player_name}. "
            "Keep your shield boss forward to absorb kinetic impact, widen your stance by shoulder-width, and strike upward into the soft throat when a beast leaps. "
            "Never swing wildly — balance is victory.",
            "neutral"
        ),
        "ash": (
            "Combat? The best fighters are the ones who never have to draw their daggers at all. "
            "Positioning, surprise, and knowing your exit route before you enter a room will save your life ten times over raw muscle, {player_name}.",
            "neutral"
        ),
        "finn": (
            "For scouting and archery: anchor your bowstring consistently to your cheekbone, exhale slowly, and release on the natural pause between breaths! "
            "And if a monster gets too close — run and climb! High ground wins every time!",
            "happy"
        ),
        "eva": (
            "I do not teach the taking of life, {player_name}, but I can teach you how to survive it. "
            "Always carry tourniquets, boiled willow water for cleansing blade wounds, and never leave for the woods without a moonflower antivenom.",
            "neutral"
        ),
        "tabitha": (
            "True strength is not found in the sharpness of iron, but in the discipline of the mind. "
            "Know why you fight before you draw, for a blade unsheathed in anger creates wounds that even centuries cannot close.",
            "thinking"
        ),
        "pip": (
            "I can show you how to throw pinecones with super spin! "
            "You grip it like THIS, wind your arm up like a windmill, and BAM! Hit a tree from twenty steps away!",
            "happy"
        ),
    },

    "hunger_food": {
        "sam": (
            "If your stomach's rumbling, head over to the tavern on the west side of the village square. "
            "Rowan keeps a hot cauldron of venison stew going all day, and the barley loaves are baked fresh each morning. "
            "A soldier marches on their belly — eat before you head into the woods, {player_name}.",
            "neutral"
        ),
        "ash": (
            "Looking for a bite, {player_name}? The tavern across the square serves a decent mutton stew. "
            "Tell the tavern maid Rowan that Ash sent you — or don't, depending on whether you want a slight discount or a suspicious glare. "
            "Just keep your coin pouch tucked in your vest while you eat.",
            "suspicious"
        ),
        "eva": (
            "You look a bit fatigued, {player_name}. I have some dried mountain figs and sweetened clover biscuits in the apothecary cupboard if you need immediate energy. "
            "For a proper hot meal, the village tavern across the square prepares excellent vegetable broth and fresh bread every afternoon.",
            "happy"
        ),
        "tabitha": (
            "A weary traveler must nourish the flesh before seeking the mysteries of the spirit, {player_name}. "
            "Cross the cobblestone square to the west tavern; Rowan's hearth is warm, and the simple bread and herb broth will restore your vigor.",
            "neutral"
        ),
        "finn": (
            "Ooh, hungry?! You gotta check out the baker's cart in the market square — they have fresh honey rolls on Tuesdays! "
            "Or if you want a big meal, the tavern has giant bowls of beef stew. I sometimes sneak an extra biscuit from the kitchen window when Rowan isn't looking!",
            "happy"
        ),
        "pip": (
            "Are you hungry, {player_name}?! Eva gave me a piece of sweet berry pie earlier and it was AMAZING! "
            "If you go to the tavern or the baker's stall by the well, they have big crunchy bread rolls! Want to share half my apple?!",
            "happy"
        ),
    },

    "lost_navigation": {
        "sam": (
            "You're standing right in Thornhaven village, {player_name}. "
            "Keep your bearings: my forge is to the east, the apothecary is north along the ridge path, the tavern is west, and the main valley gate is south. "
            "Don't wander past the tree line on the north ridge unless you've got good steel drawn.",
            "neutral"
        ),
        "ash": (
            "Lost in Thornhaven? It's smaller than it looks, {player_name}. "
            "You're in the central district. The tavern's west if you want drinks and rumors, the apothecary's north, the blacksmith's east, and the road to the capital runs straight south through the main checkpoint.",
            "neutral"
        ),
        "eva": (
            "Peace, {player_name}. You are safe in Thornhaven village. "
            "The village square sits right in the center. My apothecary is just north past the willow trees, the blacksmith is to the east, and the tavern is to the west. "
            "Take a deep breath — you are among friends here.",
            "happy"
        ),
        "tabitha": (
            "You stand in the sanctuary of Thornhaven, {player_name}, sheltered between the ancient ridge and the Whispering Woods. "
            "The square is the heart of our settlement. The elder archives and chapel lie to the north, the iron forge to the east, and the traveler's inn to the west. All paths here lead back to where you need to be.",
            "thinking"
        ),
        "finn": (
            "Hey, don't worry, {player_name}! I know every single alley and rooftop in Thornhaven! "
            "You're right in the village square. Forge is east, apothecary is north, tavern is west, and the big wooden gate is south! "
            "If you ever get lost in the woods, look for my three-pebble markers on the trail forks!",
            "happy"
        ),
        "pip": (
            "You're in Thornhaven, silly! Right by the fountain where I race my wooden boats! "
            "Sam's forge makes loud clangy sounds to the right, Eva's flower shop smells nice to the top, and the big tavern is to the left! I can walk you there if you want!",
            "happy"
        ),
    },

    "general_help": {
        "sam": (
            "State what you need, {player_name}. "
            "If it's weapons, armor repairs, or monster combat advice, you're standing in the right forge. "
            "If it's remedies, see Eva north; if it's questions about town history, ask Tabitha. What's the trouble?",
            "neutral"
        ),
        "ash": (
            "Help is a commodity I specialize in, {player_name} — provided we understand each other. "
            "Whether you need intelligence on local factions, discreet contacts, or profitable work around the valley, I can point you in the right direction. What are you looking to solve?",
            "suspicious"
        ),
        "eva": (
            "I would be glad to help you, {player_name}. "
            "Whether you need healing salves for wounds, herbal draughts for fatigue, or advice on identifying rare forest flora, my apothecary is open to you. Tell me what is troubling you.",
            "happy"
        ),
        "tabitha": (
            "Speak your mind freely, {player_name}. "
            "The chronicles hold many answers for those who seek with an earnest heart. Whether you seek guidance on the ancient keystones, valley lore, or the road ahead, I will share what wisdom I possess.",
            "thinking"
        ),
        "finn": (
            "I can totally help you, {player_name}! "
            "I know all the shortcut trails, animal tracks, and best vantage points around the ridges! "
            "Do you need directions, help tracking something, or someone to scout ahead for you?",
            "happy"
        ),
        "pip": (
            "I'm REALLY good at helping, {player_name}! "
            "I can find lost shiny things in the grass, carry small bags, or show you my secret hiding spot behind the watermill! What do you need help with?!",
            "happy"
        ),
    },

    "tired_rest": {
        "sam": (
            "Pushing yourself when your arms are heavy is how warriors get sloppy and get killed. "
            "Head west to the tavern; they keep clean traveler rooms upstairs with sturdy straw mattresses. Get a full night's sleep before you swing a sword again, {player_name}.",
            "neutral"
        ),
        "ash": (
            "Fatigue makes people careless, {player_name}, and carelessness is dangerous in a border town. "
            "The tavern on the west side has rooms on the upper floor for a couple of copper pieces. Lock your door from the inside and get some rest.",
            "neutral"
        ),
        "eva": (
            "Your body is asking for rest, {player_name}, and you should listen to it. "
            "I can prepare a mild chamomile and lavender tincture to help you sleep deeply. You can rent a quiet room at the village inn across the square.",
            "happy"
        ),
        "tabitha": (
            "The soul cannot reflect clearly upon troubled waters when the vessel is weary, {player_name}. "
            "Seek shelter at the traveler's lodge across the square. Allow the stillness of the valley to restore your strength tonight.",
            "neutral"
        ),
        "finn": (
            "Whoa, you look exhausted, {player_name}! You should definitely crash at the inn upstairs from the tavern! "
            "The corner room facing the east ridge has the best breeze and you can watch the sunrise over the mountains!",
            "surprised"
        ),
        "pip": (
            "You look like you're gonna fall asleep standing up like a horse! "
            "The tavern has big soft beds upstairs! Go take a nap, and when you wake up we can go explore the creek!",
            "surprised"
        ),
    },

    "greeting_casual": {
        "sam": (
            "Greetings, {player_name}. Forge is hot, iron's glowing, and there's plenty of work to be done. "
            "How's the road treating you today?",
            "neutral"
        ),
        "ash": (
            "Well met, {player_name}. Another interesting day in Thornhaven. "
            "What brings you across my table — looking for news, trade, or just passing the time?",
            "neutral"
        ),
        "eva": (
            "Good day to you, {player_name}! The morning dew was wonderful for harvesting today. "
            "How are you feeling? I hope your travels have been peaceful.",
            "happy"
        ),
        "tabitha": (
            "Peace and clarity upon you, {player_name}. "
            "The light falls gently across the valley today. What brings you to speak with this old lorekeeper?",
            "neutral"
        ),
        "finn": (
            "Hey, {player_name}! Great to see you! I just got back from doing a perimeter loop along the ridge! "
            "What are you up to today — heading out on an adventure?",
            "happy"
        ),
        "pip": (
            "HI {player_name}!! *waves excitedly* Look, look! The sun is super bright today! "
            "Are you going to do cool knight stuff today?!",
            "happy"
        ),
    },

    "weather_smalltalk": {
        "sam": (
            "Sky's clear enough for now, {player_name}. Up on the ridge, the mountain wind can shift in twenty minutes, so always carry a dry cloak. "
            "Down here by the forge, it's always warm regardless of what the clouds are doing.",
            "neutral"
        ),
        "ash": (
            "Clear skies mean caravan traffic, and caravan traffic means fresh news from the capital. "
            "I don't mind the weather as long as it keeps the trade roads open and the merchants spending coin.",
            "neutral"
        ),
        "eva": (
            "The air carries a crisp mountain moisture today, {player_name} — perfect for the wild herbs along the creek banks. "
            "When the sun is mild like this, botanical infusions distill with much cleaner aromatics.",
            "happy"
        ),
        "tabitha": (
            "The seasonal winds carry echoes from the high peaks, {player_name}. "
            "The ancient calendars teach us that every shift in weather is the valley's breath adjusting to celestial currents. A peaceful day to be cherished.",
            "thinking"
        ),
        "finn": (
            "The weather's awesome for scouting today! From the belltower roof you can see all the way to the broken bridge four miles out! "
            "Zero fog means I can spot goblin campfire smoke instantly!",
            "happy"
        ),
        "pip": (
            "The weather is SUPER nice! Me and Barnaby the beetle were sunbathing on the stone wall earlier! "
            "When it's sunny like this, the river pebbles sparkle ten times brighter!",
            "happy"
        ),
    },

    "gratitude": {
        "sam": (
            "No need for elaborate thanks, {player_name}. When someone comes to my forge in earnest, they get an honest answer. "
            "Watch your back out there.",
            "neutral"
        ),
        "ash": (
            "You're welcome, {player_name}. Mutual courtesy makes future business considerably smoother. "
            "Come back when you have new questions — or new intel.",
            "happy"
        ),
        "eva": (
            "You are very welcome, {player_name}! Helping travelers on their journey is the whole purpose of this apothecary. "
            "Take care of yourself out on the road.",
            "happy"
        ),
        "tabitha": (
            "Gratitude is a noble virtue that enriches both the giver and the receiver, {player_name}. "
            "May your path ahead be illuminated by wisdom and courage.",
            "happy"
        ),
        "finn": (
            "Anytime, {player_name}! That's what village scouts are for! "
            "If you ever need another trail mapped or someone to watch your six, just shout!",
            "happy"
        ),
        "pip": (
            "Yay! You're welcome!! You're the nicest traveler ever, {player_name}! "
            "I'm gonna show you my best secret shiny rock next time, I promise!",
            "happy"
        ),
    },

    "farewell": {
        "sam": (
            "Keep your blade sharp and your footing firm, {player_name}. Come back in one piece.",
            "neutral"
        ),
        "ash": (
            "Safe travels, {player_name}. Keep your eyes open, your purse close, and your wits about you.",
            "neutral"
        ),
        "eva": (
            "Farewell for now, {player_name}. May the forest paths be gentle under your feet. Stop by if you ever need remedies.",
            "happy"
        ),
        "tabitha": (
            "Go in peace, child of the road. May the ancient memory of this valley guard your steps until we speak again.",
            "neutral"
        ),
        "finn": (
            "See you later, {player_name}! I'll keep an eye out for you from the lookout ridge! Stay sharp!",
            "happy"
        ),
        "pip": (
            "BYE BYE {player_name}!! Come back soon and tell me all about the monsters you saw!! *waves both arms*",
            "happy"
        ),
    },

    "compliment_friendly": {
        "sam": (
            "*huffs slightly, but smirks* Compliments don't sharpen steel, {player_name}, but I appreciate the sentiment. "
            "You're not so bad yourself for an adventurer.",
            "happy"
        ),
        "ash": (
            "Flattery? Careful, friend — if you make me like you too much, I might start giving you discounts, and that's bad for business. "
            "Appreciate the kind words, {player_name}.",
            "happy"
        ),
        "eva": (
            "That is very kind of you to say, {player_name}! A warm heart is the greatest medicine in a harsh world. "
            "It is truly a pleasure having you in Thornhaven.",
            "happy"
        ),
        "tabitha": (
            "Your kindness honors me, young traveler. In a world often hurried and sharp, gentle words carry their own quiet majesty.",
            "happy"
        ),
        "finn": (
            "*grins widely* Really?! Thanks, {player_name}! That's the coolest thing anyone's said to me all week! "
            "You're awesome too!",
            "happy"
        ),
        "pip": (
            "YAY!! You're the coolest traveler in the whole entire world, {player_name}! We're definitely best friends now!!",
            "happy"
        ),
    },

    "sports_and_games": {
        "pip": (
            "I LOVE playing games and running super fast! Finn and I play rooftop tag, and I practice racing grasshoppers down by the creek! "
            "Grown-ups call it 'sports' when there are teams and rules, but my absolute favorite game is seeing who can climb the big apple tree the fastest without dropping any shiny river stones! "
            "What's your favorite game to play, {player_name}?",
            "happy"
        ),
        "finn": (
            "I run sprint drills every single morning across the ridge trails! We don't have arena sports in Thornhaven, but I train for speed, rooftop climbs, and long-range archery drills. "
            "Being fast and agile is the number one rule for a scout! Do you train in running or sports too, {player_name}?",
            "happy"
        ),
        "sam": (
            "Sports? If you mean lifting fifty-pound iron billets or endurance marches in full plate armor, then yes, that's my sport. "
            "Out here, physical conditioning isn't a leisure activity — it's what keeps your shield arm from faltering in battle. Do you train with weapons or physical drills, {player_name}?",
            "neutral"
        ),
        "eva": (
            "The village youths often race along the meadow streams or play ball games in the square. "
            "While I spend most of my daylight hours tending the apothecary herbs, I always make sure the young runners have soothing arnica balms for sprained ankles! Do you enjoy active sports on your travels, {player_name}?",
            "happy"
        ),
        "ash": (
            "Sports? The only game I play is high-stakes leverage, {player_name}. "
            "Though if you're talking about running — knowing how to scale a tavern drainpipe in ten seconds flat with twenty pounds of silver in your satchel certainly requires athletic stamina. What's your sport of choice?",
            "neutral"
        ),
        "tabitha": (
            "In the ancient records of the Old Kingdom, the seasonal festivals included archery contests, chariot races, and stone-lifting games to honor the harvest. "
            "Physical games have always brought communities together in joy and friendly contest. Do you partake in such athletics in your homeland, {player_name}?",
            "thinking"
        )
    }
}


def match_conversational_intent(text: str, npc_id: str, player_name: str = "Traveler") -> Optional[Dict[str, Any]]:
    """
    Checks if the user's message matches any common conversational speech acts or game objectives.
    Returns structured dialogue response if matched, otherwise None.
    """
    normalized = normalize_text(text)
    lower = normalized.lower().strip()
    # Normalize punctuation for regex matching
    cleaned = re.sub(r"[^\w\s']", " ", lower).strip()
    cleaned_dense = re.sub(r"\s+", " ", cleaned)

    for intent_name, patterns in CONVERSATIONAL_PATTERNS.items():
        for pat in patterns:
            if re.search(pat, lower) or re.search(pat, cleaned_dense) or re.search(pat, text.lower()):
                responses_for_intent = CONVERSATIONAL_RESPONSES.get(intent_name, {})
                char_data = responses_for_intent.get(npc_id) or responses_for_intent.get("ash")
                if char_data:
                    action = "none"
                    action_params = {}
                    if len(char_data) == 4:
                        template_text, emotion, action, action_params = char_data
                    elif len(char_data) == 2:
                        template_text, emotion = char_data
                    else:
                        template_text = char_data[0]
                        emotion = char_data[1] if len(char_data) > 1 else "neutral"

                    dialogue = template_text.format(player_name=player_name)
                    return {
                        "dialogue": dialogue,
                        "emotion": emotion,
                        "action": action,
                        "action_params": action_params,
                        "conversational_intent": intent_name
                    }
    return None
