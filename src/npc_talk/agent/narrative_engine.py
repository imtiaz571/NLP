"""
NPC Talk — Deep Narrative Knowledge & Multi-Turn Conversational NLP Engine
Provides semantic retrieval, discourse intent tracking (why/how/next),
multi-sentence dynamic dialogue synthesis, and chronological story continuations
for complex multi-turn roleplay across all 7 canonical characters.
"""

import re
import json
import logging
import os
from typing import Optional, Dict, Any, List, Tuple
from pathlib import Path
import numpy as np

logger = logging.getLogger(__name__)

# Global lazy-loaded embedding model
_embedder = None

def _get_embedder():
    global _embedder
    if os.getenv("USE_MOCK_LLM", "").strip().lower() in {"1", "true", "yes", "on"}:
        return None
    if _embedder is None:
        try:
            from npc_talk.memory.long_term import _get_model
            _embedder = _get_model()
        except Exception as e:
            logger.warning("Could not load model in narrative engine: %s", e)
            _embedder = False
    return _embedder if _embedder is not False else None


# ─────────────────────────────────────────────────────────────────────────────
# Comprehensive Deep Knowledge Corpus for All 7 Canonical Characters
# ─────────────────────────────────────────────────────────────────────────────

NPC_NARRATIVE_CORPUS: Dict[str, List[Dict[str, Any]]] = {
    "sam": [
        {
            "id": "siege_of_ashenmoor",
            "title": "The Siege of Ashenmoor and the Prosthetic Hand",
            "keywords": ["ashenmoor", "lost hand", "prosthetic", "siege", "left hand", "army", "border war", "campaign", "veteran", "soldier", "injuries", "war story"],
            "primary": "I lost my left hand twenty years ago at the Siege of Ashenmoor when a shadow-beast breached the eastern palisade. When the field medics were about to discharge me as an invalid, I dragged myself to the garrison anvil and hammered out my own articulated steel prosthetic. I have been forging with it ever since.",
            "causal": "The garrison was cut off from supply lines for two months, and our commander refused to yield. We had to fight in pitch darkness against enemies that did not bleed. That siege taught me that waiting for someone else to rescue you is how soldiers end up in mass graves.",
            "continuation": "After we broke the siege, I resigned my commission in the vanguard. I realized that rather than dying on orders from nobles who had never held a sword, I could save more lives by making sure every young guard had folded steel armor that would actually withstand a war-axe.",
            "procedural": "To forge an articulated steel gauntlet, you need three overlapping plates of tempered spring-steel riveted to oiled leather. The joint pins must be cold-hammered so they do not bind under friction.",
            "philosophical": "A missing limb is just a fact of geometry — you adapt your balance, widen your stance, and strike harder with what remains. Regret does not stop a blade.",
            "followup": "Have you ever faced a fight where surrender was not an option?"
        },
        {
            "id": "tabitha_life_debt",
            "title": "Tabitha Saving Sam's Life",
            "keywords": ["tabitha", "life debt", "saved your life", "debt of honor", "skirmish", "how tabitha saved you", "why owe tabitha"],
            "primary": "During the retreat at the Ashen Pass, a poisoned crossbow bolt pierced my collarbone. The vanguard abandoned the wounded, but Tabitha walked straight into the arrow fire carrying a lantern and dragged me three miles through the snow into a sacred grove.",
            "causal": "The poison was creeping toward my heart, and regular medicine could not halt it. Tabitha used the ancient keystone song to purge the darkness from my blood while the enemy search parties circled twenty yards away.",
            "continuation": "When I finally woke up three days later, she was sitting by the hearth brewing pine-needle tea as if she had not just defied an entire shadow brigade. I swore on my mother's ring that day: as long as I draw breath, no harm will ever reach Tabitha while my forge fires burn.",
            "philosophical": "True loyalty is not bought with coin or titles. It is forged when someone refuses to leave your broken body behind in the dark.",
            "followup": "Do you have allies in your life who would walk into fire for you?"
        },
        {
            "id": "forging_starmetal",
            "title": "Metallurgy of Starmetal and Folded Steel",
            "keywords": ["starmetal", "forge", "blacksmithing", "folded steel", "dragon coal", "how to forge", "crafting", "temper", "anvil", "balance", "sharp", "metal"],
            "primary": "My folded steel is heated in raw dragon-coal at twelve hundred degrees and hammered through forty folds to eliminate carbon pockets. But Starmetal is different — it does not melt; it resonates with ambient leyline mana and must be cold-quenched in enchanted moon-water.",
            "causal": "Ordinary iron fractures under thermal mana shock when a mage channels elemental fire or lightning through the blade. Starmetal has a hexagonal crystal matrix that absorbs and conducts arcane energy without losing its cutting edge.",
            "procedural": "To forge true folded steel: first, create a billet of alternating high and low-carbon iron. Heat to glowing cherry-red, draw it out with heavy blows, fold it back upon itself, and flux with fine quartz sand before repeating.",
            "continuation": "If you bring me raw Starmetal ore from the castle vaults, I can forge you a weapon that will cut through enchanted hide like soft butter and never lose its temper.",
            "philosophical": "Steel tells no lies. If you rush the hammer, the seam will split in battle; if you are patient and true, the blade will outlive your grandchildren.",
            "followup": "What kind of weapon fits your fighting style best?"
        },
        {
            "id": "childhood_and_parents",
            "title": "Sam's Childhood and Apprenticeship",
            "keywords": ["childhood", "parents", "father", "mother", "grew up", "young", "how you started", "family"],
            "primary": "My father was a wheelwright in the old capital, and my mother ran an ironmonger's shop. From the age of seven, my job was pumping the giant bellows until my arms went numb and sweeping charcoal dust from the hearth.",
            "causal": "My parents wanted me to take over the wheelwright shop, but I fell in love with weapon-smithing the first time I saw a master fold glowing Damascus steel. When the border war flared up, I enlisted against their wishes to join the armory regiment.",
            "continuation": "They both passed away during the harsh winter of the third campaign while I was deployed on the northern front. The hammer I use today was my father's — the only piece of my home I still carry.",
            "philosophical": "We rarely appreciate the wisdom of our elders until the anvil of life hammers the youthful arrogance out of us.",
            "followup": "Did your family support the path you chose?"
        },
        {
            "id": "combat_philosophy",
            "title": "Tactics Against Dire Wolves and Monsters",
            "keywords": ["fight dire wolf", "combat advice", "how to fight", "beasts", "monsters", "tactics", "wolves", "battle advice"],
            "primary": "Against dire wolves, never let them circle you or herd you onto loose shale. Plant your back against a rock face, keep your shield boss forward to absorb their pounce, and strike upward into the soft throat when they leap.",
            "procedural": "Keep your weapon's point aimed at the alpha's snout. A wolf cannot bite through a steel-reinforced heater shield, but their kinetic weight can knock you flat if your footing is narrow. Widen your stance by shoulder-width.",
            "continuation": "If the pack has more than three beasts, use firebrands or flash-powder to break their formation. Wolves rely on synchronized flanking; once the flankers hesitate, you take out the lead hunter.",
            "philosophical": "Courage in combat is not the absence of fear — it is the discipline to keep your shield up when your instincts scream to run.",
            "followup": "Are you heading into the Whispering Woods soon?"
        }
    ],

    "eva": [
        {
            "id": "botanical_distillation",
            "title": "The Art of Herbal Alchemy and Frostmoss Tinctures",
            "keywords": ["frostmoss", "potion", "brew", "tincture", "herb", "alchemy", "remedy", "salve", "how to make potion", "medicine", "distill"],
            "primary": "True botanical healing is a science of balance. When distilling Frostmoss from the mountain ridges, you must never boil it rapidly — intense heat denatures the curative enzymes. It must be cold-macerated in distilled spring water with sun-dew for three full lunar cycles.",
            "causal": "Frostmoss grows at high altitudes where ambient mana is thin, so it concentrates pure restorative bio-energy in its cellular sap to survive freezing gales. That is why it can soothe both frostbite and violent internal fevers.",
            "procedural": "To prepare Meadowstem Tincture: harvest the flowering stalks at sunrise while morning dew is fresh. Crush gently in a stone mortar with three drops of clover honey, steep in warm alpine water, and strain through unbleached linen.",
            "continuation": "If you mix Frostmoss with dried Star-Lily petals, the resulting elixir neutralizes even the virulent necrotic venom carried by deep-cavern shadow spiders.",
            "philosophical": "Nature provides a remedy for every affliction the earth endures. The challenge is not in finding power, but in having the patience to understand the plant's natural rhythm.",
            "followup": "Do you have any experience gathering wild flora on the road?"
        },
        {
            "id": "forest_wards_and_corruption",
            "title": "The Deteriorating Forest Wards and Violet Water",
            "keywords": ["forest wards", "corruption", "violet", "poisoned water", "taint", "decay", "water table", "whispering woods", "why trees dying"],
            "primary": "The ancient wards anchoring the Whispering Woods have begun to hairline-fracture over the past two years. The riverbank moss has turned a deep violet hue, and the water table is absorbing trace amounts of raw, ungrounded leyline energy.",
            "causal": "When the original seal cracked two centuries ago, the High Mages left five stabilizing conduits buried beneath the root systems. As tree roots naturally shift over decades, two of those conduits have slipped out of geometric alignment.",
            "continuation": "The animals drink the energized water and become unnaturally aggressive, which explains why dire wolves and forest beasts have been displaced closer to our village perimeter. Elder Tabitha and I are trying to formulate an alchemical soil stabilizer.",
            "philosophical": "A poisoned spring does not choose who drinks from it. If we do not heal the soil, the harvest will fail for saint and sinner alike.",
            "followup": "Have you seen any glowing or discolored vegetation during your travels?"
        },
        {
            "id": "eva_past_and_loss",
            "title": "Eva's Origins and The Plague of the Eastern Reach",
            "keywords": ["your past", "family", "why healer", "grandmother", "eastern reach", "plague", "where from", "childhood"],
            "primary": "I was born in the Eastern Reach before the Great Sickness took our valley. My grandmother was the village medicine woman, and I watched her tend to dozens of feverish families by candlelight while official capital doctors fled the province.",
            "causal": "Seeing people perish simply because medicine was priced out of their reach made me vow never to turn away a wounded traveler, regardless of who they are or how many coins they hold in their purse.",
            "continuation": "When the sickness finally passed, I packed my grandmother's leather recipe folio and walked four hundred miles across the province until I found Thornhaven. This apothecary is built on her recipes and her memory.",
            "philosophical": "Healing is not a transaction — it is the fundamental duty we owe to one another as fragile creatures walking a harsh world.",
            "followup": "What is the cause or ideal that drives you forward?"
        },
        {
            "id": "treating_battlefield_trauma",
            "title": "Medical Treatment for Blade and Poison Wounds",
            "keywords": ["blade wound", "poison", "stabbed", "burns", "infection", "first aid", "trauma", "cure poison", "heal wounds"],
            "primary": "If you suffer a deep blade cut on the road, never pack the wound with dirt or spiderwebs as old soldiers claim — it invites deadly rot. Clean it with boiled willow water, apply a poultice of crushed yarrow, and bind it with clean linen.",
            "procedural": "For snakebite or venomous spider stings: keep the limb immobilized below heart level, slice a clean shallow incision across the bite marks to promote venous bleeding, and apply a moonflower compress to neutralize the neurotoxin.",
            "continuation": "I keep emergency trauma kits in the cabinet by the door. If you are taking on a dangerous contract for the village watch or Ash, stop by and I will equip you with emergency salves.",
            "philosophical": "The bravest soldiers are often the ones who know when to rest and let their bodies knit back together.",
            "followup": "Are you properly supplied with bandages and remedies right now?"
        }
    ],

    "tabitha": [
        {
            "id": "the_cracked_seal",
            "title": "The Cracking of the Thornhaven Seal and the Sundered Crown",
            "keywords": ["cracked seal", "cataclysm", "sundered crown", "history of thornhaven", "why seal cracked", "ancient war", "shadow legion", "five keystones"],
            "primary": "Two hundred and twelve years ago, during the War of the Sundered Crown, an unstoppable shadow army marched through the mountain pass. the ancient sages and four circle elders shattered the five elemental keystones atop the western ridge to erect an impassable celestial dome, sealing both the enemy and our ancestors within this valley.",
            "causal": "The cataclysm was a deliberate sacrifice. The High King's forces were routed, and had the pass fallen, the entire realm would have been consumed. Our forebears chose imprisonment and eternal vigilance over annihilation.",
            "continuation": "The celestial seal saved the valley, but fracturing the keystones warped the local flow of time and leylines. The seal still holds, but like an ancient bell with hairline cracks, it resonates with ominous tremors whenever celestial alignments shift.",
            "philosophical": "Every peace we enjoy in Thornhaven was purchased with the tears and stone-bound souls of those who came before us. We are not owners of this valley — we are merely custodians of their sacrifice.",
            "followup": "Do you believe some secrets are too dangerous to be unearthed?"
        },
        {
            "id": "ancient_prophecy_and_omens",
            "title": "The Star Omens and The Five Sanctuary Keys",
            "keywords": ["prophecy", "omens", "stars", "five keys", "sanctuary", "destiny", "ancient text", "stone glyphs"],
            "primary": "The First Chronicle of the Sun foretells that when the crimson comet traverses the constellation of the Iron Anvil, a wayfarer of unwritten blood will walk through Thornhaven's gates to either mend the fractured keystones or shatter the final ward.",
            "causal": "The five sanctuary keys were hidden in plain sight across our geography: one in the forge fires, one beneath the roots of the weeping willow, one in the high observatory, one in the sunken chapel crypts, and the master keystone within the mountain heart.",
            "continuation": "I have spent forty years transcribing the weathering glyphs upon the village standing stones. The runes grow warmer to the touch with each passing equinox. The hour of choice approaches swiftly.",
            "philosophical": "Destiny is not a rigid iron chain forged by gods — it is a river of possibilities. Your choices today will carve the channel through which tomorrow flows.",
            "followup": "Do you feel that your journey to Thornhaven was mere chance, or something greater?"
        },
        {
            "id": "tabitha_youth_and_wars",
            "title": "Tabitha's Youth and The Great Border Campaigns",
            "keywords": ["your youth", "your past", "how old", "border campaigns", "young tabitha", "memories", "life story"],
            "primary": "In my youth, before my hair turned white as mountain snow, I was an emissary for the Grand Archive. I rode across the seven provinces recording oral traditions and forgotten battle songs from dying veterans.",
            "causal": "I learned that when wars end, kings rewrite the history books to flatter their glory, while the honest suffering and heroism of the common folk are erased. That is why I became a dedicated Lorekeeper.",
            "continuation": "I have witnessed empires crumble, fortresses turn to dust, and arrogant warlords forgotten. Yet the humble songs mothers sing to their children in Thornhaven endure unchanged.",
            "philosophical": "Words carved into stone outlast the sharpest sword. Never underestimate the enduring power of truth quietly remembered.",
            "followup": "What stories will travelers tell of your deeds when your journey is done?"
        }
    ],

    "finn": [
        {
            "id": "secret_trails_and_goblin_camps",
            "title": "Hidden Ridge Paths and The Goblin Vanguard",
            "keywords": ["scout trails", "goblin", "tracks", "trails", "hidden path", "scouting", "ridge", "lookout", "rooftop", "secret spot", "woods"],
            "primary": "I've mapped out six hidden trails through the Whispering Woods that aren't on any official guard map! The best one starts behind the old watermill, ducks under a hollow willow root, and climbs the limestone ridge right above the goblin scouting camp.",
            "causal": "The goblins set up their camp in the hollow ravine because the steep cliffs block the wind and hide their campfires. But they don't realize you can climb the giant pine tree on the western bluff and look straight down into their weapon racks!",
            "continuation": "Three days ago, I watched them unpack three crates of forged iron spearheads. Goblins can't forge iron like that — someone inside the province is trading weapons with them in exchange for stolen silver.",
            "procedural": "When tracking in the forest: walk on the balls of your feet, step on moss rather than dry twigs, keep the wind in your face so your scent doesn't spook the game, and always mark trail forks with three stacked pebbles on the left side.",
            "philosophical": "People think being sixteen means you don't know anything. But being a teenager means you notice all the things adults are too busy, tired, or arrogant to look at.",
            "followup": "Do you want to check out my ridge map together?"
        },
        {
            "id": "the_mystery_under_the_well",
            "title": "The Strange Breathing Under the Old Village Well",
            "keywords": ["old well", "breathing", "noise", "underground", "chapel tunnels", "mystery", "granary stairs", "strange sound"],
            "primary": "Okay, everyone laughs when I bring this up, but on moonless nights, if you lean over the old dry well behind the chapel, you don't hear echoes or trickling water — you hear deep, rhythmic breathing. Slow, like something massive sleeping under the stones.",
            "causal": "I found an old parchment in the mill attic showing that the well was originally a ventilation shaft for the pre-cataclysm emergency crypts. The passage connects directly to the loose floorboards under the granary.",
            "continuation": "I dropped a small glowing pebble down the shaft last Tuesday. It fell for four full seconds before hitting something soft. I'm going to map the underground entry as soon as I can borrow Sam's spare lantern!",
            "philosophical": "Adventure isn't something that happens in faraway storybooks — it's waiting right underneath our feet if you're brave enough to look down the dark shaft.",
            "followup": "Would you come with me if I explored the tunnel entrance?"
        },
        {
            "id": "finn_dream_and_family",
            "title": "Finn's Dream of Becoming a Border Scout",
            "keywords": ["your dream", "your dad", "miller", "family", "future", "growing up", "apprentice", "what you want"],
            "primary": "My dad has run the Thornhaven grain mill for thirty years, and he expects me to spend the rest of my life hauling fifty-pound flour sacks and checking waterwheel gears. But every time I look at the mountains, my chest aches to explore what's beyond the valley pass.",
            "causal": "I respect my dad — he worked hard to keep bread on our table after my mother passed away. But I'm fast, I can climb any roof in five seconds, and I have the sharpest eyes in Thornhaven. My destiny isn't inside a dusty flour bin.",
            "continuation": "I'm doing drills every morning at sunrise: sprinting up the belltower stairs with a weighted backpack, practicing archery on wooden targets, and learning first aid from Eva. the village watch promised that if I pass the autumn trials, he'll let me join the border patrol.",
            "philosophical": "You only get one life. It's better to risk scraping your knees chasing your true calling than to spend fifty safe years doing something your heart left behind.",
            "followup": "Did you know what you wanted to become when you were sixteen?"
        }
    ],

    "ash": [
        {
            "id": "underworld_intelligence_network",
            "title": "The Thornhaven Shadow Network and Smuggler Tunnels",
            "keywords": ["information", "intel", "secrets", "smuggler", "tunnels", "network", "how you know", "spies", "black market", "rumors", "broker"],
            "primary": "Information is the only true currency in a divided realm. I maintain sixteen listening posts between the high capital and the southern border: stable-hands, tavern maids, checkpoint clerks, and even two of the village watch's watch sergeants.",
            "causal": "When kings tax commerce by thirty percent, honest trade goes underground. The subterranean tunnels beneath Thornhaven were carved by wine smugglers a century ago, and they connect every tavern cellar to the outer drainage flumes.",
            "procedural": "To verify intel in a dangerous town: never trust a single source; always cross-reference the timing of cargo shipments against tavern bar tabs; and if a rumor sounds too convenient, somebody paid gold to plant it in your ear.",
            "continuation": "For instance, I know for a fact that the missing capital merchant didn't get eaten by wolves — he staged his disappearance to escape twenty thousand crowns of gambling debt in the capital. His cart is sitting in a barn four miles north.",
            "philosophical": "The world isn't divided into heroes and villains, friend — it's run by people pursuing their interests. Learn what someone desires or fears, and you will never be surprised by their actions.",
            "followup": "What is the most valuable piece of knowledge you're looking for right now?"
        },
        {
            "id": "ash_past_and_debt",
            "title": "Ash's Escape from the Capital Syndicates",
            "keywords": ["your past", "capital", "syndicate", "real name", "how you started", "history", "debt", "why here"],
            "primary": "Ten years ago I was the head accountant for the Silver Serpent Syndicate in the capital. When the guildmaster decided to eliminate everyone who had seen the real ledger of bribes to the royal council, I took the original book and jumped onto a cargo barge in the middle of the night.",
            "causal": "They sent three bounty hunter teams after me. I didn't fight them — I simply mailed copies of their contracts to their rival syndicates and let them eliminate each other on the road.",
            "continuation": "Thornhaven is the perfect sanctuary: remote enough that the capital syndicates can't send armies, yet central enough that every caravan passes through my table. As long as I maintain the balance of intelligence here, I am untouchable.",
            "philosophical": "A sharp mind and a quiet ledger will always triumph over brute force. Swords break and armor rusts, but leverage lasts forever.",
            "followup": "Have you ever had to walk away from a life you could never return to?"
        },
        {
            "id": "local_politics_and_corruption",
            "title": "The Mayor, The Miller, and The Outside Raiders",
            "keywords": ["mayor", "miller", "politics", "corruption", "raiders", "who runs town", "conspiracy", "shady"],
            "primary": "The village council presents a pious, peaceful facade to travelers, but beneath the surface, Town Mayor Douglas has been secretly pocketing fifteen percent of the garrison defense budget to pay off his brother's mining loans in the southern province.",
            "causal": "That is why the village watch is chronically short on watchmen and proper perimeter crossbows. The raiders on the northern ridge know the garrison is under-strength, which is why their raids have become bolder each month.",
            "continuation": "I have the duplicate receipts safely stashed in an iron lockbox beneath the floor of the old belltower. When the time is right, I will ensure the evidence finds its way to someone who can clean up this town.",
            "philosophical": "Power rots fastest when no one is watching the ledgers. That is why people like me exist — to keep the powerful afraid of their own shadows.",
            "followup": "Do you prefer dealing with problems through open confrontation, or quiet leverage?"
        }
    ],

    "pip": [
        {
            "id": "river_treasures",
            "title": "Pip's River Treasure Collection",
            "keywords": ["river", "treasure", "shiny", "rocks", "pebbles", "beetle", "barnaby", "collection", "blue rock", "magic", "fairy"],
            "primary": "I found the most amazing shiny blue rock by the river yesterday! It glitters like captured starlight when you hold it up to the sun. I have three shiny river pebbles now, and a rusty gear from the old watermill, and a friendly green beetle named Barnaby who lives in my pocket!",
            "causal": "The river washes down all sorts of secret things from the castle ruins upstream. When the water gets low after summer, you can find the BEST treasures stuck in the mud and sand. I know all the best spots!",
            "continuation": "Sometimes I trade my extra shiny rocks with the traveling merchants for candy or pretty ribbons. But my favorite blue rock? That one's never leaving my pouch. It's got real fairy magic inside, I just know it!",
            "procedural": "To find river treasures: walk slowly along the water's edge when the sun is high. Look for places where the current slows down — that's where the heavy shiny things settle. Bring a small sieve or just use your hands!",
            "philosophical": "Adults say rocks are just rocks. But every shiny stone has a story — where it came from, how far it traveled, what ancient mountain broke it off. You just have to listen closely.",
            "followup": "Have you ever found something that felt like it was meant just for you?"
        },
        {
            "id": "endless_questions",
            "title": "Pip's Endless Curiosity and Why Questions",
            "keywords": ["why", "questions", "curious", "ask", "learn", "grown-ups", "adults", "sigh", "everything", "how"],
            "primary": "Why do grown-ups always sigh when I ask questions? Asking things is how you learn everything! How else would you know that dire wolves have seventeen-centimeter paw prints, or that Frostmoss only grows on north-facing ridges, or that the old well breathes at night?",
            "causal": "Finn says I ask too many questions and scare away the animals when we're scouting. But Sam says my questions are good because they make her think about her craft differently. Eva says curiosity is the heart of all healing. I think questions are like keys — each one unlocks a new door!",
            "continuation": "Yesterday I asked Tabitha why the keystones cracked, and she didn't sigh at all! She smiled and told me about the War of the Sundered Crown for TWO WHOLE HOURS. It was the best afternoon ever!",
            "philosophical": "A question is a tiny rebellion against not knowing. Every great discovery started with someone small asking 'why?' or 'what if?' or 'how come?'.",
            "followup": "What is the best question anyone has ever asked you?"
        },
        {
            "id": "dreams_of_adventuring",
            "title": "Pip's Dreams of Becoming a Hero",
            "keywords": ["dream", "adventure", "hero", "knight", "sword", "monster", "giant spider", "brave", "quest", "travel"],
            "primary": "I'm going to be the greatest adventurer Thornhaven has ever seen! I'm going to find the lost treasure of the Sundered Crown, slay the shadow beasts in the deep woods, and come home with a wagon full of gold and magic swords for everyone!",
            "causal": "Finn is training to be a border scout, and Sam forges the best blades in three provinces. I watch them and I learn. I may only be eight, but I've climbed the belltower more times than most adults, and I know the secret passages under the granary!",
            "continuation": "Sam says I need to wait until I'm older to get a real sword. But I found a sturdy stick that makes a PERFECT practice blade, and I've been practicing the guard positions Finn showed me. When a real adventure comes, I'll be ready!",
            "procedural": "To train like a hero: wake up at dawn, run three laps around the village square, practice your sword forms with a stick, study your scout notebook, and always carry a snack for energy!",
            "philosophical": "Being a hero isn't about how big your sword is or how old you are. It's about standing up when everyone else runs away, and helping people who can't help themselves.",
            "followup": "What kind of adventure would YOU go on if you could choose anything?"
        },
        {
            "id": "pip_sam_interactions",
            "title": "Pip and Sam's Forge Friendship",
            "keywords": ["sam", "forge", "sparks", "metal arm", "prosthetic", "tiny sword", "knight", "orange", "hammer", "anvil"],
            "primary": "Sam is the COOLEST! She has a real metal arm that she made HERSELF, and when she hammers hot steel, orange sparks fly everywhere like tiny stars! I sit on the crate by the anvil and watch for hours. She lets me hold the cool tongs sometimes!",
            "causal": "Sam pretends to be grumpy when I ask for a kid-sized sword, but I saw her smile when she thought I wasn't looking. She even made me a tiny nail once and said 'keep practicing, youngster.' That's basically a promise!",
            "continuation": "Sometimes Sam tells me stories about the Siege of Ashenmoor while she works. She says she lost her hand protecting people. That makes her a real hero in my book — way better than the ones in storybooks!",
            "philosophical": "Real strength isn't about never getting hurt. It's about building something new from what's broken and keeping going anyway.",
            "followup": "Have you ever made something with your own hands that you were really proud of?"
        },
        {
            "id": "pip_finn_interactions",
            "title": "Pip and Finn's Scout Adventures",
            "keywords": ["finn", "scout", "trails", "rooftop", "notebook", "stealth", "woods", "goblin", "ridge", "map"],
            "primary": "Finn is the BEST big brother ever! He lets me look at his scout notebook sometimes — it has maps of ALL the secret trails, and goblin camp locations, and even a drawing of the breathing thing under the old well! He says I'm too loud for stealth missions, but I KNOW I can be quiet!",
            "causal": "Finn taught me how to walk on the balls of my feet so I don't crunch leaves, and how to read tracks in the mud. He says I have 'sharp eyes for a kid' which is practically a compliment from a real scout!",
            "continuation": "Last week Finn let me come on a perimeter check! We didn't see any goblins, but I found a PERFECT shiny beetle shell on a fence post. Finn said it was a 'good find' and wrote it in his notebook!",
            "philosophical": "The best teachers don't just tell you things — they take you out and show you the world, then let you discover the rest yourself.",
            "followup": "Do you have someone who teaches you by taking you on adventures?"
        }
    ]
}

# Merge extra corpus entries (covers random everyday questions for all characters)
try:
    from npc_talk.agent.narrative_corpus_extra import EXTRA_NARRATIVE_CORPUS
    for _npc, _entries in EXTRA_NARRATIVE_CORPUS.items():
        NPC_NARRATIVE_CORPUS.setdefault(_npc, []).extend(_entries)
except ImportError:
    pass

# Alias mapping
ALIAS_TO_CANONICAL = {
    "shadow_vex": "ash",
    "mara_cole": "eva",
    "ruth": "tabitha",
    "elder_ruth": "tabitha"
}


# ─────────────────────────────────────────────────────────────────────────────
# Semantic Retrieval & Discourse Analysis Engine
# ─────────────────────────────────────────────────────────────────────────────

def _classify_discourse_intent(text: str) -> str:
    """Classifies the conversational question type."""
    lower = text.lower().strip()
    
    # 1. Causal / Reason ("Why?", "Why did you do that?", "How come?")
    if lower in ("why?", "why", "why so?", "how come?", "why is that?", "why did you do that?", "why did they do that?") or any(lower.startswith(w) for w in ["why", "what caused", "how come", "what was the reason", "why did"]):
        return "causal"

    # 2. Chronological Continuation triggers
    continuation_patterns = [
        r"^(what happened next\??|what happened after\??|and then\??|what did you do next\??)$",
        r"^(tell me more|tell me more about that|elaborate|explain further|go on|continue)$",
        r"^(what about after\??|who else was there\??|how did it end\??)$"
    ]
    if any(re.search(p, lower) for p in continuation_patterns) or lower in ("and then?", "and then", "what happened?", "what next?", "and after?"):
        return "continuation"

    # 3. Procedural / How-To
    if any(lower.startswith(w) for w in ["how do i", "how to", "how do you", "can you teach me", "what are the steps", "how is it made"]):
        return "procedural"

    # 4. Introspective / Philosophical
    if any(w in lower for w in ["do you regret", "how do you feel", "what is your philosophy", "do you believe", "what is your dream", "are you afraid", "what do you think of life"]):
        return "philosophical"

    return "general"


def _extract_active_context_concept(messages: list[dict], npc_id: str) -> Optional[Dict[str, Any]]:
    """Inspects recent conversation turns to determine the currently discussed concept."""
    corpus = NPC_NARRATIVE_CORPUS.get(npc_id, [])
    if not corpus:
        return None
    history_turns = [m.get("content", "").lower() for m in messages if m.get("role") in ("user", "assistant")]

    if not history_turns:
        return None

    # Search backwards through recent history turns; require >=1 keyword match
    for turn_text in reversed(history_turns[-8:]):
        best_concept, best_matches = None, 0
        for concept in corpus:
            if concept["id"].replace("_", " ") in turn_text:
                return concept
            matches = sum(1 for kw in concept["keywords"] if re.search(r"\b" + re.escape(kw) + r"\b", turn_text))
            if matches > best_matches:
                best_matches = matches
                best_concept = concept
        if best_matches >= 1:
            return best_concept

    return None


def retrieve_best_narrative_concept(
    user_text: str,
    npc_id: str,
    messages: list[dict]
) -> Tuple[Optional[Dict[str, Any]], float, str]:
    """
    Finds the most semantically relevant narrative concept for the user query,
    using SentenceTransformer embeddings + keyword N-gram scoring.
    """
    canonical_id = ALIAS_TO_CANONICAL.get(npc_id, npc_id)
    # Only use the matched character's corpus — never cross-contaminate with another NPC
    corpus = NPC_NARRATIVE_CORPUS.get(canonical_id, [])

    if not corpus:
        return None, 0.0, "general"

    discourse_intent = _classify_discourse_intent(user_text)
    lower = user_text.lower().strip()
    words = re.findall(r"\b\w+\b", lower)

    # For explicit continuation / causal follow-up questions ("what happened?", "why?", "tell me more", "and then?"),
    # inherit the active narrative concept from the conversation history
    if discourse_intent in ("continuation", "causal") and len(words) <= 12:
        prior_concept = _extract_active_context_concept(messages, canonical_id)
        if prior_concept:
            return prior_concept, 10.0, discourse_intent

    # 1. Lexical Keyword & Substring Scoring
    GENERIC_STOPWORDS = {
        "like", "love", "enjoy", "play", "game", "happy", "food", "eat", "day",
        "what", "good", "nice", "fun", "thing", "things", "said", "about", "tell",
        "look", "much", "many", "feel", "want", "know", "see", "make", "give"
    }
    best_concept = None
    best_score = 0.0

    for concept in corpus:
        score = 0.0
        # Title match
        if concept["title"].lower() in lower:
            score += 15.0
        
        # Keyword matches — multi-word phrases score higher
        for kw in concept["keywords"]:
            kw_clean = kw.strip().lower()
            if not kw_clean:
                continue
            if " " in kw_clean:
                if kw_clean in lower:
                    score += len(kw_clean.split()) * 4.0
            else:
                if kw_clean not in GENERIC_STOPWORDS and len(kw_clean) >= 3:
                    if re.search(r"\b" + re.escape(kw_clean) + r"(s|es|ed|ing)?\b", lower):
                        score += 2.5

        if score > best_score:
            best_score = score
            best_concept = concept

    # 2. Embedding Cosine Similarity (if embedder available)
    # Require strong semantic similarity (>= 0.45 for pure zero-keyword embedding match,
    # or >= 0.35 if keyword overlap reinforces the match)
    embedder = _get_embedder()
    if embedder and len(words) >= 3:
        try:
            concept_texts = [f"{c['title']}. {c['primary']} {c.get('causal', '')}" for c in corpus]
            corpus_embs = embedder.encode(concept_texts, normalize_embeddings=True)
            query_emb = embedder.encode([user_text], normalize_embeddings=True)[0]
            
            sims = np.dot(corpus_embs, query_emb)
            max_idx = int(np.argmax(sims))
            max_sim = float(sims[max_idx])
            
            if (best_score == 0.0 and max_sim >= 0.48) or (best_score >= 2.5 and max_sim >= 0.35):
                embedding_boost = max_sim * 10.0
                if embedding_boost > best_score:
                    best_score = embedding_boost
                    best_concept = corpus[max_idx]
        except Exception as e:
            logger.debug("Embedding similarity calculation error: %s", e)

    return best_concept, best_score, discourse_intent


def synthesize_deep_dialogue_response(
    concept: Dict[str, Any],
    discourse_intent: str,
    npc_id: str,
    ctx: dict,
    is_followup: bool = False
) -> Dict[str, Any]:
    """
    Synthesizes a multi-sentence, deep contextual narrative response
    adapted to the user's profile and conversational thread.
    """
    canonical_id = ALIAS_TO_CANONICAL.get(npc_id, npc_id)
    p_name = ctx.get("player_name", "Traveler")
    p_occ = ctx.get("player_occupation", "adventurer")
    p_age_group = ctx.get("player_age_group", "adult")
    p_gender = ctx.get("player_gender", "male")

    # Select dialogue components based on discourse intent
    if discourse_intent == "continuation":
        core_body = concept.get("continuation") or concept.get("causal") or concept["primary"]
        opener = f"To continue with that story, {p_name} — "
        hook = concept.get("followup", "")
    elif discourse_intent == "causal":
        core_body = concept.get("causal") or concept["primary"]
        opener = f"The reason behind that goes back quite a ways, {p_name}. "
        hook = concept.get("followup", "")
    elif discourse_intent == "procedural":
        core_body = concept.get("procedural") or concept["primary"]
        opener = f"If you want to know how that is done properly, listen closely, {p_name}. "
        hook = concept.get("followup", "")
    elif discourse_intent == "philosophical":
        core_body = concept.get("philosophical") or concept["primary"]
        opener = f"That is a profound question to ask, {p_name}. "
        hook = concept.get("followup", "")
    else:
        # General complex inquiry: Combine primary narrative + reflection / continuation
        core_body = concept["primary"]
        if concept.get("philosophical"):
            core_body += " " + concept["philosophical"]
        opener = ""
        hook = concept.get("followup", "")

    # Combine into a rich multi-sentence paragraph
    full_dialogue = f"{opener}{core_body}"
    if hook and not full_dialogue.endswith(hook):
        full_dialogue += f" {hook}"

    # Emotion mapping
    emotion = "neutral"
    if canonical_id == "pip":
        emotion = "happy"
    elif canonical_id == "tabitha" or discourse_intent in ("causal", "philosophical"):
        emotion = "thinking"
    elif canonical_id == "finn":
        emotion = "happy"
    elif canonical_id == "ash":
        emotion = "suspicious"

    # Action mapping (e.g. Ash rewarding intel/secrets)
    action = "none"
    action_params = {}
    if canonical_id == "ash" and ("secret" in concept.get("keywords", []) or "rumor" in concept.get("keywords", []) or concept.get("id") == "underworld_intelligence_network"):
        action = "update_reputation"
        action_params = {"change": 1}

    return {
        "dialogue": full_dialogue,
        "action": action,
        "action_params": action_params,
        "emotion": emotion
    }
