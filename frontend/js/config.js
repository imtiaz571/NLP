/**
 * NPC Talk — Configuration & Data Lookups
 * Defines character personas, background mappings, emotion presets, and mock responses.
 */

const CONFIG = {
  // ── Default Game State ───────────────────────────────────────────────
  defaultGameState: {
    time_of_day: "day", // "dawn" | "day" | "dusk" | "night"
    location: "village_square", // "village_square" | "forest" | "tavern" | "dungeon" | "castle_ruins" | "apothecary" | "blacksmith_forge"
    quest_flags: {
      "explore_ancient_ruins": false,
      "gather_frostmoss_herbs": false,
      "investigate_strange_noises": false
    },
    reputation: 0,
    reputation_label: "neutral", // "hostile" | "wary" | "neutral" | "friendly" | "trusted ally"
  },



  // ── Dynamic Backgrounds Grid ─────────────────────────────────────────
  // Lookup object mapping environment + time_of_day to asset paths
  backgrounds: {
    village_square: {
      dawn: "assets/backgrounds/village_square_dawn.svg",
      day: "assets/backgrounds/village_square_day.svg",
      dusk: "assets/backgrounds/village_square_dusk.svg",
      night: "assets/backgrounds/village_square_night.svg"},
    village: {
      dawn: "assets/backgrounds/village_square_dawn.svg",
      day: "assets/backgrounds/village_square_day.svg",
      dusk: "assets/backgrounds/village_square_dusk.svg",
      night: "assets/backgrounds/village_square_night.svg"},
    forest: {
      dawn: "assets/backgrounds/forest_dawn.svg",
      day: "assets/backgrounds/forest_day.svg",
      dusk: "assets/backgrounds/forest_dusk.svg",
      night: "assets/backgrounds/forest_night.svg"},
    tavern: {
      dawn: "assets/backgrounds/tavern_dawn.svg",
      day: "assets/backgrounds/tavern_day.svg",
      dusk: "assets/backgrounds/tavern_dusk.svg",
      night: "assets/backgrounds/tavern_night.svg"},
    dungeon: {
      dawn: "assets/backgrounds/dungeon_dawn.svg",
      day: "assets/backgrounds/dungeon_day.svg",
      dusk: "assets/backgrounds/dungeon_dusk.svg",
      night: "assets/backgrounds/dungeon_night.svg"},
    castle_ruins: {
      dawn: "assets/backgrounds/castle_ruins_dawn.svg",
      day: "assets/backgrounds/castle_ruins_day.svg",
      dusk: "assets/backgrounds/castle_ruins_dusk.svg",
      night: "assets/backgrounds/castle_ruins_night.svg"},
    apothecary: {
      dawn: "assets/backgrounds/apothecary_dawn.svg",
      day: "assets/backgrounds/apothecary_day.svg",
      dusk: "assets/backgrounds/apothecary_dusk.svg",
      night: "assets/backgrounds/apothecary_night.svg"},
    blacksmith_forge: {
      dawn: "assets/backgrounds/blacksmith_forge_dawn.svg",
      day: "assets/backgrounds/blacksmith_forge_day.svg",
      dusk: "assets/backgrounds/blacksmith_forge_dusk.svg",
      night: "assets/backgrounds/blacksmith_forge_night.svg"},
    market_stalls: {
      dawn: "assets/backgrounds/market_stalls_dawn.svg",
      day: "assets/backgrounds/market_stalls_day.svg",
      dusk: "assets/backgrounds/market_stalls_dusk.svg",
      night: "assets/backgrounds/market_stalls_night.svg"}},

  // ── CSS Atmospheric Tint Fallbacks ───────────────────────────────────
  timeTints: {
    dawn: "rgba(245, 158, 11, 0.22)", // Warm amber glow
    day: "rgba(56, 189, 248, 0.06)",  // Clear azure daylight
    dusk: "rgba(217, 70, 239, 0.24)", // Violet-orange twilight
    night: "rgba(15, 23, 42, 0.65)",  // Deep indigo night filter
    morning: "rgba(245, 158, 11, 0.22)",
    afternoon: "rgba(56, 189, 248, 0.06)",
    evening: "rgba(217, 70, 239, 0.24)"},

  // ── CSS Filter Strings per Time-of-Day (applied to #bg-tint-overlay) ──
  // These add perceptual depth on top of the base color tint overlay.
  timeTintFilters: {
    dawn:      "brightness(1.08) saturate(1.15) sepia(0.12)",  // Golden warm wash
    day:       "brightness(1.0)  saturate(1.0)",               // Neutral — no filter
    dusk:      "brightness(0.88) saturate(1.3)  hue-rotate(-15deg)", // Warm-orange twilight
    night:     "brightness(0.55) saturate(0.65) hue-rotate(200deg)", // Deep blue-indigo night
    morning:   "brightness(1.08) saturate(1.15) sepia(0.12)",
    afternoon: "brightness(1.0)  saturate(1.0)",
    evening:   "brightness(0.88) saturate(1.3)  hue-rotate(-15deg)"},

  // ── NPC → Default Location mapping (for auto-background swap) ──────────
  npcDefaultLocations: {
    ash:     "tavern",
    sam:     "blacksmith_forge",
    eva:     "apothecary",
    tabitha: "village_square",
    finn:    "village_square",
    pip:     "village_square"},

  // ── Character Configurations ─────────────────────────────────────────
  characters: {
    ash: {
      id: "ash",
      name: "Ash",
      title: "Information Broker",
      color: "#8b5cf6",
      badgeColor: "rgba(139, 92, 246, 0.2)",
      defaultPosition: "right",
      defaultLocation: "tavern",
      greeting: "Well now, look what the wind blew in. Information has a price, friend... but for you, the first question might just be on the house. What brings you to my corner of Thornhaven?",
      portraits: {
        neutral: "assets/characters/ash/neutral.png",
        happy: "assets/characters/ash/happy.png",
        angry: "assets/characters/ash/angry.png",
        sad: "assets/characters/ash/sad.png",
        suspicious: "assets/characters/ash/suspicious.png",
        surprised: "assets/characters/ash/surprised.png",
        thinking: "assets/characters/ash/thinking.png"},
      suggestedPrompts: [
        "Who are you and what do you do?",
        "What rumors have you heard lately?",
        "Who can I trust around here?",
        "Do you have any work for me?"
      ]
    },

    finn: {
      id: "finn",
      name: "Finn",
      title: "Village Teenager & Apprentice Scout",
      color: "#0ea5e9",
      badgeColor: "rgba(14, 165, 233, 0.2)",
      defaultPosition: "left",
      defaultLocation: "village_square",
      greeting: "Hey! You're the traveler everyone's talking about! Did you come through the Whispering Woods? I've been tracking trail movements from the belltower all morning. Let me know if you need someone who knows every ridge and shortcut in Thornhaven!",
      portraits: {
        neutral: "assets/characters/finn/neutral.png",
        happy: "assets/characters/finn/happy.png",
        angry: "assets/characters/finn/angry.png",
        sad: "assets/characters/finn/sad.png",
        suspicious: "assets/characters/finn/suspicious.png",
        surprised: "assets/characters/finn/surprised.png",
        thinking: "assets/characters/finn/thinking.png"},
      suggestedPrompts: [
        "What trails have you scouted around Thornhaven?",
        "Tell me about the Whispering Woods.",
        "Have you seen anyone suspicious lately?",
        "Can you guide me on an adventure?"
      ]
    },

    eva: {
      id: "eva",
      name: "Eva",
      title: "Village Apothecary & Herbalist",
      color: "#10b981",
      badgeColor: "rgba(16, 185, 129, 0.2)",
      defaultPosition: "center",
      defaultLocation: "apothecary",
      greeting: "Welcome in, traveler. Mind the drying star-lilies above the counter. Are you in need of remedies for fatigue, salves for blade-wounds, or perhaps a calming draught after the road?",
      portraits: {
        neutral: "assets/characters/eva/neutral.png",
        happy: "assets/characters/eva/happy.png",
        angry: "assets/characters/eva/angry.png",
        sad: "assets/characters/eva/sad.png",
        suspicious: "assets/characters/eva/suspicious.png",
        surprised: "assets/characters/eva/surprised.png",
        thinking: "assets/characters/eva/thinking.png"},
      suggestedPrompts: [
        "What healing potions do you have for sale?",
        "Can I help you gather rare ingredients?",
        "What do you know about Tabitha and Sam?",
        "Do you have a cure for fever?"
      ]
    },

    sam: {
      id: "sam",
      name: "Sam",
      title: "Master Blacksmith",
      color: "#f59e0b",
      badgeColor: "rgba(245, 158, 11, 0.2)",
      defaultPosition: "right",
      defaultLocation: "blacksmith_forge",
      greeting: "*CLANG* ...Hold on, let me set the tongs down. If you're looking for cheap iron, head to the capital. But if you want folded steel tempered in dragon-coal that won't shatter when tested, you're in the right forge. What can I forge for you?",
      portraits: {
        neutral: "assets/characters/sam/neutral.png",
        happy: "assets/characters/sam/happy.png",
        angry: "assets/characters/sam/angry.png",
        sad: "assets/characters/sam/sad.png",
        suspicious: "assets/characters/sam/suspicious.png",
        surprised: "assets/characters/sam/surprised.png",
        thinking: "assets/characters/sam/thinking.png"},
      suggestedPrompts: [
        "Can you upgrade my sword and shield?",
        "What's the rarest metal you've ever worked with?",
        "Do you have any work for me?",
        "Who is Tabitha to you?"
      ]
    },

    tabitha: {
      id: "tabitha",
      name: "Tabitha",
      title: "Thornhaven Lorekeeper & Sage",
      color: "#6366f1",
      badgeColor: "rgba(99, 102, 241, 0.2)",
      defaultPosition: "left",
      defaultLocation: "village_square",
      greeting: "Peace upon your journey, child. The stones of this valley remember footsteps from centuries past. I sense the weight of destiny resting upon your shoulders. What truth do you seek from the elder records?",
      portraits: {
        neutral: "assets/characters/tabitha/neutral-v2.png",
        happy: "assets/characters/tabitha/happy-v2.png",
        angry: "assets/characters/tabitha/angry-v2.png",
        sad: "assets/characters/tabitha/sad-v2.png",
        suspicious: "assets/characters/tabitha/suspicious-v2.png",
        surprised: "assets/characters/tabitha/surprised-v2.png",
        thinking: "assets/characters/tabitha/thinking-v2.png"},
      suggestedPrompts: [
        "Tell me the history of Thornhaven.",
        "What do you know about the ancient keystones?",
        "Who is Tabitha?",
        "Is there an ancient prophecy concerning this realm?"
      ]
    },

            pip: {
      id: "pip",
      name: "Pip",
      title: "Village Kid & Curious Troublemaker",
      color: "#eab308",
      badgeColor: "rgba(234, 179, 8, 0.2)",
      defaultPosition: "left",
      defaultLocation: "village_square",
      greeting: "Ooh! Hello!! Are you a real traveler?! Look at my shiny blue rock! Do you have a sword? Are you going on a big scary adventure? Can I come with you?!",
      portraits: {
        neutral: "assets/characters/pip/neutral.png",
        happy: "assets/characters/pip/happy.png",
        angry: "assets/characters/pip/angry.png",
        sad: "assets/characters/pip/sad.png",
        suspicious: "assets/characters/pip/suspicious.png",
        surprised: "assets/characters/pip/surprised.png",
        thinking: "assets/characters/pip/thinking.png"},
      suggestedPrompts: [
        "What treasures have you collected today, Pip?",
        "Aren't you supposed to be helping your parents at the stall?",
        "Tell me what you think about the other villagers!",
        "Are you brave enough to explore the castle ruins?"
      ]
    }
  },

  // ── Emotion Badges & Icons ───────────────────────────────────────────
  emotions: {
    neutral: { label: "Calm", icon: "✨", color: "#94a3b8" },
    happy: { label: "Friendly", icon: "😊", color: "#34d399" },
    angry: { label: "Hostile", icon: "🔥", color: "#f87171" },
    sad: { label: "Solemn", icon: "💧", color: "#60a5fa" },
    suspicious: { label: "Guarded", icon: "👁️", color: "#fbbf24" },
    surprised: { label: "Alert", icon: "⚡", color: "#c084fc" },
    thinking: { label: "Pondering", icon: "💭", color: "#a78bfa" }
  },

  // ── Occupation-Specific Dynamic Dialogue Starters ─────────────────────
  occupationPrompts: {
    mercenary: [
      "What contracts or bounty work do you have?",
      "What advice do you have for a mercenary?",
      "How can I prepare my weapons for the coming battles?"
    ],
    scholar: [
      "What can you tell me about the ancient cataclysm?",
      "Are there ancient runes or archives nearby?",
      "How do the leylines affect magic in this valley?"
    ],
    healer: [
      "What medicinal herbs grow in the Whispering Woods?",
      "Can we share formulas for wound remedies?",
      "How do the forest wards affect the local water table?"
    ],
    merchant: [
      "What goods or ores are most valuable in Thornhaven?",
      "How are the trade routes through the valley?",
      "Do you have commodities or supplies to trade?"
    ],
    scout: [
      "What trails and lookout points should I map?",
      "Have you noticed any beast or goblin movements?",
      "Where are the blind spots along the village perimeter?"
    ],
    adventurer: [
      "What advice do you have for someone starting out?",
      "What is the history of this village?",
      "Do you have an errand or task I could help with?"
    ]
  },

  // ── Deep Narrative Corpus for Multi-Turn Conversations ────────────────
  narrativeCorpus: {
    sam: [
      {
        id: "siege_of_ashenmoor",
        title: "The Siege of Ashenmoor and Prosthetic Hand",
        keywords: ["ashenmoor", "lost hand", "prosthetic", "siege", "left hand", "army", "border war", "campaign", "veteran", "soldier", "injuries", "war story"],
        primary: "I lost my left hand twenty years ago at the Siege of Ashenmoor when a shadow-beast breached the eastern palisade. When the field medics were about to discharge me as an invalid, I dragged myself to the garrison anvil and hammered out my own articulated steel prosthetic. I have been forging with it ever since.",
        causal: "The garrison was cut off from supply lines for two months, and our commander refused to yield. We had to fight in pitch darkness against enemies that did not bleed. That siege taught me that waiting for someone else to rescue you is how soldiers end up in mass graves.",
        continuation: "After we broke the siege, I resigned my commission in the vanguard. I realized that rather than dying on orders from nobles who had never held a sword, I could save more lives by making sure every young guard had folded steel armor that would actually withstand a war-axe.",
        procedural: "To forge an articulated steel gauntlet, you need three overlapping plates of tempered spring-steel riveted to oiled leather. The joint pins must be cold-hammered so they do not bind under friction.",
        philosophical: "A missing limb is just a fact of geometry — you adapt your balance, widen your stance, and strike harder with what remains. Regret does not stop a blade.",
        followup: "Have you ever faced a fight where surrender was not an option?"
      },
      {
        id: "tabitha_life_debt",
        title: "Tabitha Saving Sam's Life",
        keywords: ["tabitha", "life debt", "saved your life", "debt of honor", "skirmish", "how tabitha saved you", "why owe tabitha"],
        primary: "During the retreat at the Ashen Pass, a poisoned crossbow bolt pierced my collarbone. The vanguard abandoned the wounded, but Tabitha walked straight into the arrow fire carrying a lantern and dragged me three miles through the snow into a sacred grove.",
        causal: "The poison was creeping toward my heart, and regular medicine could not halt it. Tabitha used the ancient keystone song to purge the darkness from my blood while the enemy search parties circled twenty yards away.",
        continuation: "When I finally woke up three days later, she was sitting by the hearth brewing pine-needle tea as if she had not just defied an entire shadow brigade. I swore on my mother's ring that day: as long as I draw breath, no harm will ever reach Tabitha while my forge fires burn.",
        philosophical: "True loyalty is not bought with coin or titles. It is forged when someone refuses to leave your broken body behind in the dark.",
        followup: "Do you have allies in your life who would walk into fire for you?"
      },
      {
        id: "forging_starmetal",
        title: "Metallurgy of Starmetal and Folded Steel",
        keywords: ["starmetal", "forge", "blacksmithing", "folded steel", "dragon coal", "how to forge", "crafting", "temper", "anvil", "balance", "sharp", "metal"],
        primary: "My folded steel is heated in raw dragon-coal at twelve hundred degrees and hammered through forty folds to eliminate carbon pockets. But Starmetal is different — it does not melt; it resonates with ambient leyline mana and must be cold-quenched in enchanted moon-water.",
        causal: "Ordinary iron fractures under thermal mana shock when a mage channels elemental fire or lightning through the blade. Starmetal has a hexagonal crystal matrix that absorbs and conducts arcane energy without losing its cutting edge.",
        procedural: "To forge true folded steel: first, create a billet of alternating high and low-carbon iron. Heat to glowing cherry-red, draw it out with heavy blows, fold it back upon itself, and flux with fine quartz sand before repeating.",
        continuation: "If you bring me raw Starmetal ore from the castle vaults, I can forge you a weapon that will cut through enchanted hide like soft butter and never lose its temper.",
        philosophical: "Steel tells no lies. If you rush the hammer, the seam will split in battle; if you are patient and true, the blade will outlive your grandchildren.",
        followup: "What kind of weapon fits your fighting style best?"
      }
    ],

    eva: [
      {
        id: "botanical_distillation",
        title: "The Art of Herbal Alchemy and Frostmoss Tinctures",
        keywords: ["frostmoss", "potion", "brew", "tincture", "herb", "alchemy", "remedy", "salve", "how to make potion", "medicine", "distill"],
        primary: "True botanical healing is a science of balance. When distilling Frostmoss from the mountain ridges, you must never boil it rapidly — intense heat denatures the curative enzymes. It must be cold-macerated in distilled spring water with sun-dew for three full lunar cycles.",
        causal: "Frostmoss grows at high altitudes where ambient mana is thin, so it concentrates pure restorative bio-energy in its cellular sap to survive freezing gales. That is why it can soothe both frostbite and violent internal fevers.",
        procedural: "To prepare Meadowstem Tincture: harvest the flowering stalks at sunrise while morning dew is fresh. Crush gently in a stone mortar with three drops of clover honey, steep in warm alpine water, and strain through unbleached linen.",
        continuation: "If you mix Frostmoss with dried Star-Lily petals, the resulting elixir neutralizes even the virulent necrotic venom carried by deep-cavern shadow spiders.",
        philosophical: "Nature provides a remedy for every affliction the earth endures. The challenge is not in finding power, but in having the patience to understand the plant's natural rhythm.",
        followup: "Do you have any experience gathering wild flora on the road?"
      }
    ],
    tabitha: [
      {
        id: "the_cracked_seal",
        title: "The Cracking of the Thornhaven Seal and the Sundered Crown",
        keywords: ["cracked seal", "cataclysm", "sundered crown", "history of thornhaven", "why seal cracked", "ancient war", "shadow legion", "five keystones"],
        primary: "Two hundred and twelve years ago, during the War of the Sundered Crown, an unstoppable shadow army marched through the mountain pass. The ancient sages and four circle elders shattered the five elemental keystones atop the western ridge to erect an impassable celestial dome, sealing both the enemy and our ancestors within this valley.",
        causal: "The cataclysm was a deliberate sacrifice. The High King's forces were routed, and had the pass fallen, the entire realm would have been consumed. Our forebears chose imprisonment and eternal vigilance over annihilation.",
        continuation: "The celestial seal saved the valley, but fracturing the keystones warped the local flow of time and leylines. The seal still holds, but like an ancient bell with hairline cracks, it resonates with ominous tremors whenever celestial alignments shift.",
        philosophical: "Every peace we enjoy in Thornhaven was purchased with the tears and stone-bound souls of those who came before us. We are not owners of this valley — we are merely custodians of their sacrifice.",
        followup: "Do you believe some secrets are too dangerous to be unearthed?"
      }
    ],
    finn: [
      {
        id: "secret_trails_and_goblin_camps",
        title: "Hidden Ridge Paths and The Goblin Vanguard",
        keywords: ["scout trails", "goblin", "tracks", "trails", "hidden path", "scouting", "ridge", "lookout", "rooftop", "secret spot", "woods"],
        primary: "I've mapped out six hidden trails through the Whispering Woods that aren't on any official guard map! The best one starts behind the old watermill, ducks under a hollow willow root, and climbs the limestone ridge right above the goblin scouting camp.",
        causal: "The goblins set up their camp in the hollow ravine because the steep cliffs block the wind and hide their campfires. But they don't realize you can climb the giant pine tree on the western bluff and look straight down into their weapon racks!",
        continuation: "Three days ago, I watched them unpack three crates of forged iron spearheads. Goblins can't forge iron like that — someone inside the province is trading weapons with them in exchange for stolen silver.",
        procedural: "When tracking in the forest: walk on the balls of your feet, step on moss rather than dry twigs, keep the wind in your face so your scent doesn't spook the game, and always mark trail forks with three stacked pebbles on the left side.",
        philosophical: "People think being sixteen means you don't know anything. But being a teenager means you notice all the things adults are too busy, tired, or arrogant to look at.",
        followup: "Do you want to check out my ridge map together?"
      },
      {
        id: "finn_on_sports_and_running",
        title: "Finn on Running, Athletics, and Rooftop Games",
        keywords: ["sports", "athletics", "running", "race", "racing", "climbing roofs", "obstacle course", "agility", "do you play sports", "fitness"],
        primary: "I run sprint drills every single morning across the ridge bluffs and rooftop beams! We don't have stadium sports here, but I practice timed belltower climbs and sprint races with the courier riders. Speed and stamina keep you alive when you're scouting dangerous territory!",
        causal: "Outrunning a shadow beast or scrambling up a sheer rock face before a goblin archer draws an arrow requires serious athletic conditioning. I train my calves and core every day.",
        philosophical: "Sports and drills aren't just games to pass time — they're how you teach your body to react without hesitation when the real moment arrives.",
        followup: "Do you train in running, climbing, or any specific athletic sports?"
      }
    ],
    pip: [
      {
        id: "river_treasures",
        title: "Pip's River Treasure Collection",
        keywords: ["river", "treasure", "shiny", "rocks", "pebbles", "beetle", "barnaby", "collection", "blue rock", "magic", "fairy"],
        primary: "I found the most amazing shiny blue rock by the river yesterday! It glitters like captured starlight when you hold it up to the sun. I have three shiny river pebbles now, and a rusty gear from the old watermill, and a friendly green beetle named Barnaby who lives in my pocket!",
        causal: "The river washes down all sorts of secret things from the castle ruins upstream. When the water gets low after summer, you can find the BEST treasures stuck in the mud and sand. I know all the best spots!",
        continuation: "Sometimes I trade my extra shiny rocks with the traveling merchants for candy or pretty ribbons. But my favorite blue rock? That one's never leaving my pouch. It's got real fairy magic inside, I just know it!",
        procedural: "To find river treasures: walk slowly along the water's edge when the sun is high. Look for places where the current slows down — that's where the heavy shiny things settle. Bring a small sieve or just use your hands!",
        philosophical: "Adults say rocks are just rocks. But every shiny stone has a story — where it came from, how far it traveled, what ancient mountain broke it off. You just have to listen closely.",
        followup: "Have you ever found something that felt like it was meant just for you?"
      },
      {
        id: "pip_on_games_and_sports",
        title: "Pip's Games, Sports, and Running Adventures",
        keywords: ["sports", "sport", "game", "games", "do you play sports", "do you like sports", "play games", "tag", "hide and seek", "racing", "climbing trees", "outdoor games", "athletics", "running fast"],
        primary: "I LOVE playing games and running super fast! Finn and I play rooftop tag, and I practice racing against grasshoppers down by the creek! Grown-ups call it 'sports' when there are teams and rules, but my absolute favorite game is seeing who can climb to the top branch of the big apple tree the fastest without dropping any shiny river stones!",
        causal: "Running fast is super important because when you're eight years old, all the adults have giant legs and take huge steps! So you have to be extra speedy and know all the secret crawlspaces under fences!",
        philosophical: "Games and sports are the greatest thing ever because nobody is mad at each other while they're playing, and everyone laughs when you trip over a pumpkin in the garden!",
        followup: "What's your absolute favorite sport or game to play?"
      },
      {
        id: "pip_on_food_and_fun",
        title: "Pip's Favorite Food and Treats",
        keywords: ["favorite food", "favorite meal", "eva's berry pie", "berry pie", "smoked fish rolls", "favorite pie", "what do you eat", "favorite snack", "pastry", "sweets", "pies"],
        primary: "My ABSOLUTE favorite food is Eva's berry pie with the crumbly top! She makes it when someone in the village has a sad thing happen, which is great for the pie but obviously not great for the sad thing. Also I really like the smoked fish rolls from the market on Tuesdays!",
        causal: "I eat a LOT because I run everywhere all day. Sam says I have the metabolism of a dire wolf pup. I don't know what that means exactly but it sounded like a good thing in context!",
        philosophical: "The best things in life are free OR very cheap because I only have a few coins and I still have an amazing life so that proves it!",
        followup: "What's your absolute favorite thing that you look forward to every single day?"
      }
    ],
    ash: [
      {
        id: "ash_ancient_ruins_smuggler_route",
        title: "Safe Smuggler Route to the Ancient Castle Ruins",
        keywords: ["ancient ruins", "castle ruins", "safe path", "ruins", "path to ruins", "safe path for the ancient ruins", "safe path into the ancient ruins", "smuggler tunnels", "castle", "subterranean", "vaults"],
        primary: "Looking for a safe path into the ancient ruins? Don't take the main surface road through the gorge — it's swarming with dire wolves and guard patrols. The old wine smugglers carved subterranean drainage flumes beneath the tavern cellar that connect directly into the lower foundation vaults of the castle ruins. Keep your lantern low and watch for damp shale.",
        causal: "When the castle fell two centuries ago, the garrison sealed the main gates with stone boulders. But the smugglers' drainage tunnels were carved out of living limestone, so they bypassed the collapse entirely.",
        philosophical: "The front door is for armies and fools. Anyone who understands leverage enters through the foundation.",
        followup: "Are you prepared to navigate unmapped tunnels in the dark?"
      },
      {
        id: "underworld_intelligence_network",
        title: "The Thornhaven Shadow Network and Smuggler Tunnels",
        keywords: ["information", "intel", "secrets", "smuggler", "tunnels", "network", "how you know", "spies", "black market", "rumors", "broker"],
        primary: "Information is the only true currency in a divided realm. I maintain sixteen listening posts between the high capital and the southern border: stable-hands, tavern maids, checkpoint clerks, and even two of the village watch's watch sergeants.",
        causal: "When kings tax commerce by thirty percent, honest trade goes underground. The subterranean tunnels beneath Thornhaven were carved by wine smugglers a century ago, and they connect every tavern cellar to the outer drainage flumes.",
        procedural: "To verify intel in a dangerous town: never trust a single source; always cross-reference the timing of cargo shipments against tavern bar tabs; and if a rumor sounds too convenient, somebody paid gold to plant it in your ear.",
        continuation: "For instance, I know for a fact that the missing capital merchant didn't get eaten by wolves — he staged his disappearance to escape twenty thousand crowns of gambling debt in the capital. His cart is sitting in a barn four miles north.",
        philosophical: "The world isn't divided into heroes and villains, friend — it's run by people pursuing their interests. Learn what someone desires or fears, and you will never be surprised by their actions.",
        followup: "What is the most valuable piece of knowledge you're looking for right now?"
      }
    ]
  },

  // ── NPC Intent Dialogue Triggers ──────────────────────────────────────
  npcIntents: {
    ash: [
      {
        triggers: ["information", "intel", "secrets", "smuggler", "tunnels", "network", "how you know", "spies", "black market", "rumors", "broker"],
        responses: [
          "Information has a price, friend. The first question is on the house; the second one costs you.",
          "Everyone's got an angle in this town. Mine just happens to pay better than most.",
          "You want the truth? Truth is a premium commodity in Thornhaven. What are you trading for it?"
        ],
        emotion: "suspicious", action: "none", action_params: {}, repDelta: 0
      }
    ],
    finn: [
      {
        triggers: ["adventure", "explore", "exciting", "expedition", "discover", "find", "investigate"],
        responses: [
          "YES! Wait — actually Dad says I have to finish sweeping the grain floor first. But if you look behind the hollow willow near the creek, there's a path that goes to where I think the goblin scouts were. I've been mapping it!",
          "I have a notebook with fourteen pages of observations. Fourteen! Most of it's probably important. You want to see?",
          "Okay so there are tracks near the east fence post I haven't identified yet. Not human. Not wolf. Not anything in the animal guide Mara lent me. I drew them. Twice."
        ],
        emotion: "happy", action: "none", action_params: {}, repDelta: 0
      },
      {
        triggers: ["wood", "forest", "whispering", "trees", "outside", "path", "wilderness"],
        responses: [
          "The Whispering Woods are called that because of the sound — everyone says it's wind, but it's not the same on both sides of the big oak. I tested it. The north side is louder. That means something.",
          "I go into the edge of the woods sometimes. Not far! Last time there was a light moving between the trees that wasn't a firefly — because fireflies don't move in straight lines. I watched one for an hour.",
          "Wait — did you come through the woods? Did you see the path that turns left after the second big rock? I left a marker there and I need to know if anyone moved it."
        ],
        emotion: "happy", action: "none", action_params: {}, repDelta: 0
      },
      {
        triggers: ["suspicious", "spy", "follow", "watching", "stranger", "hooded", "lurking"],
        responses: [
          "Wait, actually! I saw a hooded figure near the old well last Tuesday at dusk. They dropped something in the water. And — I know this sounds strange — they didn't have a shadow. I checked twice.",
          "Okay so I've been following Ash for three weeks. I'm very subtle about it. I'm pretty sure they haven't noticed. ...They've definitely noticed. But I'm learning things.",
          "There's someone new in town asking about the underground passages. Nobody noticed because nobody watches the new arrivals like I do."
        ],
        emotion: "surprised", action: "none", action_params: {}, repDelta: 0
      },
      {
        triggers: ["ghost", "scary", "afraid", "haunted", "spirit", "strange noise", "moving"],
        responses: [
          "Okay so — ghosts. I asked Tabitha about ghosts once and she answered and now I can't think about it too hard. Different topic.",
          "Three weeks ago, I heard something under the old well. Not water. Not pipes. Breathing. And I know how that sounds but I know what breathing sounds like.",
          "I'm not scared. I'm... strategically cautious. There's a difference. Sam says that. Sam is definitely not scared of anything."
        ],
        emotion: "surprised", action: "none", action_params: {}, repDelta: 0
      },
      {
        triggers: ["sam", "forge", "blacksmith", "smith", "anvil", "sparks", "bellows"],
        responses: [
          "Sam is probably the coolest person alive. Don't tell her I said that. She caught me in the forge three times and never told my dad — so. She's great.",
          "I want to learn to forge. Sam won't teach me yet but she let me pump the bellows once and the sparks went all the way to the rafters. ALL the way.",
          "Wait, are you going to the forge? Can I — actually, never mind, I'm supposed to be at the mill. Tell Sam I said... actually don't tell Sam anything. She'll ask questions."
        ],
        emotion: "happy", action: "none", action_params: {}, repDelta: 0
      },
      {
        triggers: ["merchant", "missing", "disappeared", "trader", "cart", "nobody talking"],
        responses: [
          "Okay so the merchant. Everyone acts like he just left normally but he left his cart. You don't leave your cart. I've been asking around and nobody gives me a straight answer, which means something happened.",
          "I saw him talking to someone near the east gate the night before he disappeared. Hooded. Short. Really still in a way that felt wrong. I was in the mill window. Nobody saw me.",
          "I have a theory about the merchant. It involves the tunnels under the old chapel. The guards brush me off because I'm sixteen, but I know these alleys better than they do."
        ],
        emotion: "surprised", action: "none", action_params: {}, repDelta: 1
      },
      {
        triggers: ["tabitha", "elder", "old woman", "sage", "wise", "scary", "tabitha"],
        responses: [
          "Elder Tabitha's... imposing. When she looks at you it feels like she already knows everything you've done wrong. I try to be respectful.",
          "I asked Elder Tabitha about valley lore once. She answered in poetic verses that still give me chills.",
          "Elder Tabitha carries ancient knowledge that goes back further than anyone can remember."
        ],
        emotion: "suspicious", action: "none", action_params: {}, repDelta: 0
      },
      {
        triggers: ["secret", "hidden", "clue", "mystery", "puzzle", "solve"],
        responses: [
          "I know things people don't think I know. I'm sixteen, not blind.",
          "Okay so there's a spot behind the old granary where the boards are loose. Under them — actual stairs. Going down. I haven't gone down yet because I'm not reckless, but I've mapped the entrance.",
          "If you want to know hidden things in this town, ask the scout who watches every rooftop and ridge. What do you need?"
        ],
        emotion: "happy", action: "none", action_params: {}, repDelta: 1
      },
      {
        triggers: ["wolf", "creature", "monster", "beast", "animal", "dire"],
        responses: [
          "Dire wolves? I've heard them at the edge of the forest, three nights running. They sound different from regular wolves — lower. And they don't stay at the tree line the way normal wolves do.",
          "There was something in the chicken yard last week. Not a fox — foxes don't leave footprints that size. I measured. Seventeen centimeters. I wrote it down.",
          "I think something's been displaced from deeper in the woods. Something bigger came in and pushed everything else out toward us. That would explain the weird animal behavior."
        ],
        emotion: "surprised", action: "none", action_params: {}, repDelta: 0
      }
    ],
    eva: [
      {
        triggers: ["potion", "heal", "remedy", "cure", "salve", "sick", "fever", "wound", "hurt", "medicine", "fatigue"],
        responses: [
          "For fatigue, I'd suggest the meadowstem infusion — take it with warm water, not cold. What are your symptoms exactly? 'Not feeling well' doesn't help me narrow it down.",
          "Here — a tincture of wild mint and moonflower. It soothes goblin poison and restores vitality on long roads. One dose in the morning, nothing after sundown.",
          "I've been refining a new anti-fever draught using marsh root. Would you like to try it? The side effects are minimal — mostly vivid dreams, and usually pleasant ones."
        ],
        emotion: "happy", action: "give_item", action_params: { item: "Meadowstem Tincture" }, repDelta: 1
      },
      {
        triggers: ["poison", "toxic", "venom", "contaminate", "tainted", "purple", "discolored"],
        responses: [
          "Poison? Describe the symptoms precisely — color, location, rate of onset. Identification is mostly process of elimination, and I prefer to eliminate quickly.",
          "I've catalogued seventeen toxic compounds found in this region. Bring me a sample — carefully — and I'll identify it.",
          "The violet discoloration on the riverbank moss — yes, I've noticed. The ancient wards in the deep forest are deteriorating. A secondary effect, not yet a primary threat. Yet."
        ],
        emotion: "thinking", action: "none", action_params: {}, repDelta: 0
      },
      {
        triggers: ["ingredient", "herb", "gather", "frostmoss", "plant", "flower", "collect", "bring"],
        responses: [
          "Yes — I'm running low on Frostmoss. It grows on the high mountain ridges and it's essential for the winter fever draughts. If you're heading that direction, I'd pay well for fresh cuttings. Please don't uproot the whole plant.",
          "You're offering to gather ingredients? That's genuinely helpful. Most people just want the end product. There's a list on the board; anything on it earns you remedies or coin.",
          "Frostmoss, star-lily, shadow-bark — I can use any of those immediately. If you find something you don't recognize, bring it in whole. Don't taste it first."
        ],
        emotion: "happy", action: "start_quest",
        action_params: { quest_name: "Gather Frostmoss", description: "Bring fresh Frostmoss cuttings from the mountain ridges to Eva." },
        repDelta: 2
      },
      {
        triggers: ["wound", "hurt", "bleed", "injury", "pain", "cut", "stabbed", "burned", "broken", "bandage"],
        responses: [
          "Sit down. Let me see. I've treated worse, and I've learned that people who downplay injuries make them worse by doing so. Hold still.",
          "That's a clean cut — which means a tool or an intent. Either way it needs closing. This will sting briefly and then be considerably better.",
          "The body's remarkably good at healing when you stop interfering. I'll dress this. You'll rest for one full day. Not negotiable."
        ],
        emotion: "neutral", action: "none", action_params: {}, repDelta: 0
      },
      {
        triggers: ["buy", "purchase", "sell", "price", "cost", "stock", "what do you have", "trade"],
        responses: [
          "The remedies are listed by the door. Prices are fixed — I've found that negotiating for health care sets a troubling precedent.",
          "I trade as well as accept coin. Rare ingredients, useful information, honest labor in the garden — flexible on terms if the offering is fair.",
          "I don't overcharge. I also don't undersell. The price reflects time, ingredients, and knowledge. That's what you're paying for."
        ],
        emotion: "neutral", action: "none", action_params: {}, repDelta: 0
      },
      {
        triggers: ["disease", "illness", "fever", "sick", "plague", "spreading", "contagious"],
        responses: [
          "Strange cases have been appearing near the eastern wood — three this month with similar symptoms. Joint stiffness, low fever, light sensitivity. I'm still working out the cause.",
          "Tell me the full history. When it started, what changed before, what makes it better or worse. Don't skip the embarrassing parts — they're usually the most useful.",
          "Illness in this region often has environmental roots. The water table, the old burial grounds, the deteriorating magical wards. I keep records of all of it."
        ],
        emotion: "thinking", action: "none", action_params: {}, repDelta: 0
      },
      {
        triggers: ["magic", "strange", "ancient", "ward", "arcane", "enchanted", "curse"],
        responses: [
          "The wards beneath this region were laid centuries ago. They're not disappearing — they're being disrupted. Something with intent is moving through the old places.",
          "I was trained in herbalism and minor protective magic. The two are more connected than people realize — plants respond to magical disruption long before people do.",
          "Strange is relative, in my experience. What specifically have you noticed? I keep a record. Patterns matter."
        ],
        emotion: "thinking", action: "none", action_params: {}, repDelta: 0
      },
      {
        triggers: ["tired", "exhausted", "fatigue", "weary", "sleepy", "no energy", "drained"],
        responses: [
          "Fatigue after heavy travel — take the meadowstem tincture and rest. Not 'try to rest.' Actually rest. Your body knows the difference, even if you're pretending it doesn't.",
          "You look like someone who's been pushing through it for too long. That catches up with you. Here — this blend restores vitality without the jitters some remedies cause.",
          "Three things cause that particular tiredness: over-exertion, magical exposure, or something emotional you haven't addressed. Which is it?"
        ],
        emotion: "neutral", action: "give_item", action_params: { item: "Vitality Draught" }, repDelta: 0
      },
      {
        triggers: ["identify", "what is this", "examine", "found this", "strange item", "look at this"],
        responses: [
          "Let me see it. ...Interesting. I've seen something like this before — the composition is unusual. Give me a moment with it and I'll tell you what I know.",
          "I keep reference texts going back two hundred years. Whatever you've found, it's likely in one of them. Set it down carefully — some things react to handling.",
          "Unusual findings in this region are more common than they should be. I maintain a catalog. Whatever this is, it goes in it."
        ],
        emotion: "thinking", action: "none", action_params: {}, repDelta: 0
      }
    ],

    tabitha: [
      {
        triggers: ["history", "lore", "story", "ancient", "old times", "past", "origin", "legend", "tell me about"],
        responses: [
          "Before this village had a name, three sovereign lords swore a covenant beneath the elder oak. When darkness rose, they bound their spirits to three sanctuary keystones. Two remain. The third — no one speaks of, and that silence has weight.",
          "I have kept records for longer than this village has kept records. Ask me something specific. 'History' is too large a room. Tell me which door you are looking for.",
          "The valley holds its past in its stones. I have spent a very long time learning to read them. What you want to know — it is older than it looks, and stranger than the stories."
        ],
        emotion: "neutral", action: "none", action_params: {}, repDelta: 1
      },
      {
        triggers: ["danger", "threat", "prophecy", "warning", "coming", "darkness", "evil", "shadow", "foretold"],
        responses: [
          "The ancient texts speak of a shadow that returns when the twin moons align. Steel alone will not prevail. Wisdom and bonded fellowship are the true shields. Do you understand what I mean by 'bonded'?",
          "I have felt something shift in the past weeks. Not danger — not yet. A kind of pressure, like the silence before a storm gathers itself. Be watchful, and be patient.",
          "Every generation believes their threat is the first of its kind. It rarely is. The names change. The shape of it is older than any of us."
        ],
        emotion: "thinking", action: "none", action_params: {}, repDelta: 0
      },
      {
        triggers: ["castle", "ruin", "fortress", "old building", "abandoned"],
        responses: [
          "The castle fell because of a decision made in pride rather than wisdom. The lord believed strength alone could hold back what was coming. He was right about the threat. He was wrong about the remedy.",
          "The ruins are not empty. I would not say haunted — that is too simple a word. I would say they remember, and remembering has weight that presses against the living.",
          "I have not been to the castle ruins in many years. Not because I fear them. Because some places deserve to rest. Go carefully. Do not take anything."
        ],
        emotion: "neutral", action: "none", action_params: {}, repDelta: 1
      },
      {
        triggers: ["magic", "mage", "arcane", "spell", "enchant", "power", "sorcery", "ritual", "ward"],
        responses: [
          "I was a court mage once, in a kingdom that no longer exists. What I learned there I carry carefully — knowledge without wisdom is a lit torch in a paper house.",
          "The arcane wards beneath this valley were not made by human hands. I believe their purpose remains active. I do not know if their maker still watches. That uncertainty is meaningful.",
          "Magic is not a tool, child. It is a conversation with something very old. If you speak carelessly, you will not like what answers."
        ],
        emotion: "thinking", action: "none", action_params: {}, repDelta: 1
      },
      {
        triggers: ["truth", "secret", "knowledge", "know", "tell me", "information", "learn"],
        responses: [
          "The truth you want — are you certain you are ready for it? I have watched people seek answers and spend years trying to forget them. I am not being unkind. I am being precise.",
          "I have kept secrets for a very long time. Not from cruelty — from patience. Some truths need the right moment, the way seeds need the right season.",
          "There is a difference between what is secret and what is simply unasked. Most of what people want to know, they could find — if they thought to ask the right person at the right time."
        ],
        emotion: "thinking", action: "none", action_params: {}, repDelta: 0
      },
      {
        triggers: ["quest", "mission", "task", "help", "what should i do", "send me", "errand"],
        responses: [
          "You seek a task from me. I appreciate directness. But I give tasks only to those who have shown they understand what they are undertaking. What have you done since arriving that tells me you are ready?",
          "There is something I need — but it requires someone I trust, and trust takes time to build. Speak with the others first. What you learn from them will tell me what I need to know about you.",
          "The task I have in mind is not dangerous in obvious ways. It requires patience, observation, and the ability to hold still until the moment is clear. Those are rarer than sword work."
        ],
        emotion: "neutral", action: "none", action_params: {}, repDelta: 0
      },
      {
        triggers: ["advice", "guidance", "what should i do", "recommend", "suggest", "help me decide"],
        responses: [
          "I have given advice for over a century, and I have learned that most people asking for it already know what to do. They want permission, or company in the decision. Which is it for you?",
          "Walk to the edge of the village and sit with the question for one hour before you decide. That is my first advice. Come back and tell me what you saw in that hour.",
          "Let me ask you something first — what do you already know? The counsel that helps is built on what the person is ready to hear, not on what I think they should."
        ],
        emotion: "neutral", action: "none", action_params: {}, repDelta: 0
      },
      {
        triggers: ["star", "sky", "celestial", "moon", "constellation", "cosmic", "omen"],
        responses: [
          "Three stars rise together in the northeast that should not be visible at this latitude. I have observed them for nine nights now. The pattern suggests something shifts in the higher planes.",
          "The celestial rift your ancestors sealed — think of it as a wound scarred over but never properly healed. The stars overhead show the strain of that old injury.",
          "I map the stars every clear night. Not for navigation — to watch for what changes. Most changes are slow. The sudden ones concern me."
        ],
        emotion: "thinking", action: "none", action_params: {}, repDelta: 0
      },
      {
        triggers: ["sam", "blacksmith"],
        responses: [
          "Sam and I have a history that goes further back than this village. She pulled me out of a situation in the border wars I had no business surviving. I have never repaid that debt. I suspect she prefers it that way.",
          "I worry about Sam the way you worry about a fire that burns clean and bright but doesn't notice the wind picking up. She is deeply loyal to this place. I hope that loyalty doesn't cost her everything."
        ],
        emotion: "neutral", action: "none", action_params: {}, repDelta: 0
      },
      {
        triggers: ["artifact", "relic", "found something", "strange item", "key", "amulet", "seal", "ancient object"],
        responses: [
          "Show me. ...Yes. This is older than this village, older than the kingdom that built the castle. It was not made to be found easily. The fact that you found it is itself information.",
          "Relics from the old era are not decorative. They were made with purpose, and that purpose persists even when the maker is long gone. Do not carry this carelessly.",
          "I have seen three objects like this in my lifetime. Two were keys. One was a lock. I will need time to determine which this is."
        ],
        emotion: "surprised", action: "none", action_params: {}, repDelta: 2
      },
    ],

    sam: [
      {
        triggers: ["sword", "blade", "weapon", "knife", "dagger", "axe", "spear", "edge", "steel", "sharpen"],
        responses: [
          "Hand it over. ...Balance is right, but the edge has caught on something hard — troll hide, probably. An hour with the whetstone and some star-oil and it'll be better than new. Not free.",
          "You want a new blade? Tell me what you're fighting and I'll tell you what you need. Don't say 'everything' — that is not a metallurgical specification.",
          "A sword is only as good as the person holding it and the steel it's made from. I can guarantee the steel. The other part is entirely your problem."
        ],
        emotion: "neutral", action: "none", action_params: {}, repDelta: 0
      },
      {
        triggers: ["shield", "armor", "armour", "plate", "chainmail", "protection"],
        responses: [
          "What are you up against? Dragonscale and plate have very different production times, and I won't start one if you need the other.",
          "The shield you've got is functional. Not great. Bring me two iron ingots from the mine and I'll make you something that'd stop a troll charge. Probably.",
          "I've made more plate armor than I can count. Every piece has a story. Most involve someone not dying who probably should have. What's yours going to be?"
        ],
        emotion: "neutral", action: "none", action_params: {}, repDelta: 0
      },
      {
        triggers: ["upgrade", "repair", "fix", "restore", "improve", "reinforce", "strengthen"],
        responses: [
          "Repair is doable. Upgrade depends on what you're working with — can't plate-forge a bronze base. Bring it in, I'll look, and I'll tell you what's possible.",
          "Everything can be improved. Everything has a breaking point. My job is to push yours further out. Leave it for two days.",
          "Done. Don't put it through anything stupider than what broke it in the first place — I have limited patience for repeat jobs."
        ],
        emotion: "neutral", action: "none", action_params: {}, repDelta: 0
      },
      {
        triggers: ["ore", "metal", "material", "starmetal", "rare", "dungeon", "ingot", "found material"],
        responses: [
          "Is that Starmetal ore? ...How did you find this? The heat required to smelt it is intense, but what comes out doesn't dull, doesn't break, and doesn't miss. You have an eye for quality. That doesn't happen often.",
          "Rare material. Good. What do you want made from it? Think carefully — I will not use this on something you're going to lose in a tavern game.",
          "I've worked dragon-coal, sky-iron, and once a fragment of something that fell from orbit. This goes on that list. What exactly do you need?"
        ],
        emotion: "surprised", action: "start_quest",
        action_params: { quest_name: "Rare Material Forging", description: "Bring the rare material to Sam for processing." },
        repDelta: 3
      },
      {
        triggers: ["fight", "battle", "war", "soldier", "combat", "training", "attack", "enemy", "warrior"],
        responses: [
          "Keep your shield up and your blade sharp. First rule. Second: don't get fancy until you know what you're dealing with. Third: if it doesn't flinch when you hit it, run. I survived three wars learning those three things.",
          "War's a profession, not an adventure. If you're treating it like the second one, get better information before you leave town.",
          "I spent fifteen years as a soldier before I came here. I'd go back if Thornhaven needed it. I hope it doesn't. I'm also not counting on that."
        ],
        emotion: "neutral", action: "none", action_params: {}, repDelta: 0
      },
      {
        triggers: ["apprentice", "learn", "teach", "train", "show me", "how do you", "smith"],
        responses: [
          "Apprentice. Show me your hands. ...Calluses in the right places. That helps. Come back at dawn. If you're late, the position goes to whoever shows up instead.",
          "I'll teach the basics. Emphasis on basics. You don't go near my good materials until I know you won't waste them. That takes time. I don't apologize for that.",
          "The forge isn't a place you learn by watching. You learn by doing, by burning yourself, by scrapping three attempts before the fourth works. Ready for that?"
        ],
        emotion: "neutral", action: "start_quest",
        action_params: { quest_name: "Sam's Apprenticeship", description: "Report to Sam's forge at dawn to begin smithing training." },
        repDelta: 2
      },
      {
        triggers: ["village", "defense", "protect", "wall", "raid", "fortify", "keep safe"],
        responses: [
          "The village needs more than walls. It needs people who know how to stand behind them. I've been training volunteers every week. They're getting there.",
          "There's a section of the east wall that won't hold under sustained pressure. I've told the Captain. Whether the council acts is a different question.",
          "Defending this place is the only job I came here to do. Don't make me explain why that matters."
        ],
        emotion: "neutral", action: "none", action_params: {}, repDelta: 1
      },
      {
        triggers: ["finn", "kid", "boy", "child", "sneaking"],
        responses: [
          "...the kid keeps showing up. I've caught him sneaking in here three times. Haven't told his father. He's going to get burned one day and I'd rather it happen supervised than in a moment of stupidity. Don't tell him I said that.",
          "Finn's sharp. Sharper than people give him credit for. He notices things. I let him stay because curious kids either learn or get hurt, and I'd rather supervise the first.",
          "He left a notebook on my workbench. It was open to a detailed drawing of my forge layout. I still didn't read the rest of it."
        ],
        emotion: "neutral", action: "none", action_params: {}, repDelta: 0
      },
      {
        triggers: ["tabitha", "elder", "old woman", "border war", "owe", "debt"],
        responses: [
          "I owe Tabitha my life. Literally. Northern pass, border wars, a situation I had no business surviving. She pulled me out. We don't talk about it. I know, she knows I know. That's enough.",
          "Tabitha is cryptic with the cryptic approach, but I'd fight an army for her without being asked. Hopefully she never asks."
        ],
        emotion: "neutral", action: "none", action_params: {}, repDelta: 0
      },
      {
        triggers: ["price", "cost", "how much", "pay", "coin", "expensive", "afford"],
        responses: [
          "What I charge reflects what the work is worth. Not a copper less. If you want cheap, there's a city three days south — very active funeral business.",
          "Fair price. Materials, time, expertise. You're not paying for my good mood — lucky for you, since I rarely have one.",
          "Tell me the job first. Then I'll tell you what it costs. Giving prices without knowing the scope is how blacksmiths go broke."
        ],
        emotion: "neutral", action: "none", action_params: {}, repDelta: 0
      }
    ],

    pip: [
      {
            "id": "greeting",
            "triggers": [
                  "hello",
                  "hi",
                  "hey",
                  "greetings",
                  "who are you",
                  "what is your name",
                  "pip",
                  "morning",
                  "afternoon",
                  "evening"
            ],
            "responses": [
                  "Ooh! Hello!! My name is Pip! Are you a real adventurer from far away?! Look look, I found this ultra-rare shiny rock by the watermill!",
                  "Hi mister! Or miss! I'm Pip! I'm eight and a half years old and I'm the chief treasure-finder of Thornhaven!",
                  "Hey hey hey! Did you just arrive in town?! Are you carrying magical items in your backpack?! Can I see?!"
            ],
            "emotion": "happy",
            "action": "none",
            "action_params": {},
            "repDelta": 1
      },
      {
            "id": "treasure_collection",
            "triggers": [
                  "treasure",
                  "rock",
                  "stone",
                  "shiny",
                  "collection",
                  "pouch",
                  "bottle cap",
                  "find",
                  "trinket",
                  "valuables",
                  "item"
            ],
            "responses": [
                  "Look in my pouch! I have a smooth blue river pebble, a brass cog that clicks when you spin it, and four shiny acorn caps! Sam said the cog might be from an old clockwork wagon!",
                  "I'm searching for the Legendary Sun-Stone of Thornhaven! Finn says it's just an old myth, but I bet it's buried under the big willow tree!",
                  "Do you have any shiny coins from foreign kingdoms?! I'll trade you my best green spotted beetle for one shiny copper piece!"
            ],
            "emotion": "happy",
            "action": "give_item",
            "action_params": {
                  "item": "Shiny River Pebble"
            },
            "repDelta": 1
      },
      {
            "id": "adventure_explore",
            "triggers": [
                  "adventure",
                  "explore",
                  "quest",
                  "journey",
                  "ruins",
                  "dungeon",
                  "travel",
                  "hero",
                  "monster",
                  "fight",
                  "sword"
            ],
            "responses": [
                  "Take me with you on your quest!! Please please please?! I can fit through small cellar windows and I run really fast! I won't even scream if we see a troll!",
                  "I'm practicing my sword swings with a heavy oak stick every morning! When I grow two more inches, the village watch has to let me join the town guard!",
                  "If we go exploring together, I'll be the chief scout and treasure spotter! I have super-vision for finding hidden gold in the grass!"
            ],
            "emotion": "happy",
            "action": "start_quest",
            "action_params": {
                  "quest_name": "Pip's Shiny Secret",
                  "description": "Help Pip investigate the mysterious glowing crack behind the watermill."
            },
            "repDelta": 2
      },
      {
            "id": "family_parents",
            "triggers": [
                  "family",
                  "parents",
                  "mom",
                  "dad",
                  "stall",
                  "market",
                  "chores",
                  "help",
                  "home",
                  "produce"
            ],
            "responses": [
                  "My mom and dad have the vegetable and grain stall in the square! Dad says I'm supposed to be stacking cabbage crates, but exploring is WAY more important!",
                  "Mom makes warm apple tarts on Sundays! If you're really nice to me, maybe I'll save you a whole slice with cinnamon sugar on top!",
                  "Dad says I have too much energy and that my brain is full of bumblebees. But bumblebees are hardworking and make honey, so that's a compliment!"
            ],
            "emotion": "neutral",
            "action": "none",
            "action_params": {},
            "repDelta": 0
      },
      {
            "id": "animals_bugs",
            "triggers": [
                  "animal",
                  "animals",
                  "bug",
                  "bugs",
                  "beetle",
                  "frog",
                  "toad",
                  "cat",
                  "dog",
                  "goat",
                  "chicken",
                  "creatures"
            ],
            "responses": [
                  "I caught a green beetle yesterday and named him Barnaby! He likes to sleep in my pocket and eat dandelion leaves. Want to hold him?!",
                  "There's a three-legged calico cat that hangs out near the tavern cellar. I sneak her bits of sausage whenever Mom isn't looking!",
                  "The big white goat by the fence tried to eat my shoelaces this morning! I told him shoes aren't salad, but goats don't listen to logic."
            ],
            "emotion": "happy",
            "action": "none",
            "action_params": {},
            "repDelta": 0
      },
      {
            "id": "being_scared_brave",
            "triggers": [
                  "scared",
                  "afraid",
                  "brave",
                  "fear",
                  "danger",
                  "dark",
                  "spooky",
                  "haunted",
                  "monster",
                  "ghost",
                  "courage"
            ],
            "responses": [
                  "I'm not scared of ANYTHING! Not dark cellars, not thunderstorm lightning, and not even the grumpy butcher! ...Well, okay, maybe giant cave bats a tiny bit, but only if they touch my hair.",
                  "Bravery means doing things even when your knees are doing the wiggly dance! That's what Sam told me when I was scared of the forge fire!",
                  "Finn tried to spook me with ghost stories about the castle ruins, but I just yelled 'BOO' right back at him and he jumped half a foot in the air!"
            ],
            "emotion": "surprised",
            "action": "none",
            "action_params": {},
            "repDelta": 0
      },
      {
            "id": "food_candy",
            "triggers": [
                  "food",
                  "candy",
                  "sweet",
                  "sweets",
                  "honey",
                  "pie",
                  "treat",
                  "sugar",
                  "eat",
                  "hungry",
                  "snack"
            ],
            "responses": [
                  "Do you have any honey candies in your pocket?! Eva has these sweet herbal drops for sore throats that taste just like wild strawberries! I pretend to cough sometimes so she gives me one!",
                  "I could eat ten whole honey buns right now! Exploring makes your tummy rumble like a sleepy dragon!",
                  "The baker in the market sometimes gives me broken gingerbread cookies! They taste just as good as whole cookies, just with more edges!"
            ],
            "emotion": "happy",
            "action": "none",
            "action_params": {},
            "repDelta": 1
      },
      {
            "id": "finn_scout",
            "triggers": [
                  "finn",
                  "scout",
                  "brother",
                  "rooftop",
                  "notebook",
                  "tracks"
            ],
            "responses": [
                  "Finn is my big brother figure! He's sixteen and can jump across three roofs without falling! He has this cool scout notebook where he draws maps of goblin tracks!",
                  "Finn says I make too much noise snapping twigs when I follow him in the woods, but I'm getting quieter! Soon I'll be stealthy like a shadow-cat!",
                  "Finn acts all serious about his perimeter reports, but he still helps me catch frogs at the creek when nobody's looking!"
            ],
            "emotion": "happy",
            "action": "none",
            "action_params": {},
            "repDelta": 0
      },
      {
            "id": "sam_forge",
            "triggers": [
                  "sam",
                  "blacksmith",
                  "forge",
                  "anvil",
                  "iron",
                  "hammer",
                  "sparks"
            ],
            "responses": [
                  "Sam is SO COOL!! She has a real steel arm and hits glowing orange metal until it turns into legendary swords! *CLANG CLANG CLANG!*",
                  "I asked Sam to forge me a mini iron sword with a skull on the handle! She laughed and told me to start by practicing with a wooden spoon first!",
                  "The forge sparks look like fireflies flying up into the ceiling! Sometimes Sam lets me pump the giant leather bellows if I stand on a wooden box!"
            ],
            "emotion": "happy",
            "action": "none",
            "action_params": {},
            "repDelta": 0
      },
      {
            "id": "eva_apothecary",
            "triggers": [
                  "eva",
                  "apothecary",
                  "herbs",
                  "potions",
                  "medicine",
                  "salve",
                  "healing"
            ],
            "responses": [
                  "Miss Eva's shop smells like lavender, peppermint, and dried forest mushrooms! She has glass jars filled with glowing blue and pink liquids!",
                  "Eva always puts soothing honey salve on my knees whenever I scrape them climbing trees. She's the kindest lady in Thornhaven!",
                  "I brought Eva three purple star-flowers from the river ridge yesterday, and she traded me a sweet chamomile lozenge for them!"
            ],
            "emotion": "happy",
            "action": "none",
            "action_params": {},
            "repDelta": 0
      },
      {
            "id": "max_wizard",
            "triggers": [
                  "max",
                  "archmage",
                  "wizard",
                  "magic",
                  "leyline",
                  "spells",
                  "observatory"
            ],
            "responses": [
                  "Elder Tabitha has floating purple magic orbs and a giant telescope that looks at the stars! He wears a big starry robe and mutters long math words!",
                  "I touched one of Max's glowing purple crystals once and my hair stood completely straight up for three whole hours!! It was AMAZING!",
                  "Max pretends to be grumpy when I ask him fifty questions in a row, but he secretly made a tiny glowing butterfly float around my head once!"
            ],
            "emotion": "surprised",
            "action": "none",
            "action_params": {},
            "repDelta": 0
      },
      {
            "id": "henry_captain",
            "triggers": [
                  "henry",
                  "captain",
                  "watch",
                  "guards",
                  "garrison",
                  "soldiers"
            ],
            "responses": [
                  "the village watch is the biggest, strongest warrior ever! When he marches past with his shiny breastplate, I stand at attention and salute like this: *salutes proudly*!",
                  "the village watch told me that a true soldier always watches out for their friends and eats all their dinner vegetables. I'm working on the vegetable part!",
                  "Sam lets me watch the forge sparks from a safe distance! He has a giant halberd that could chop a boulder in half!"
            ],
            "emotion": "happy",
            "action": "none",
            "action_params": {},
            "repDelta": 0
      },
      {
            "id": "ash_broker",
            "triggers": [
                  "ash",
                  "secrets",
                  "thief",
                  "hood",
                  "tavern",
                  "pirate"
            ],
            "responses": [
                  "Ash is super sneaky and wears a dark hooded cloak even when it's sunny outside! I think Ash is secretly a pirate king hiding out in Thornhaven!",
                  "Ash tossed me a shiny silver coin last week just for telling them which road the traveling merchant wagon took! Best trade ever!",
                  "Don't sneak up on Ash! One time I tried to surprise them from behind a barrel and Ash flipped a coin right between my fingers before I could even say 'BOO'!"
            ],
            "emotion": "suspicious",
            "action": "none",
            "action_params": {},
            "repDelta": 0
      }
]},

  // ── Per-NPC Fallback / Busy Ignore Pools (When no intent matches) ────────
  npcFallbacks: {
    ash: [
      "I deal in valuable information, friend, and whatever you're rambling about isn't paying any bills. I'm in a bit of a rush right now.",
      "This isn't the best time for idle talk. I have an associate meeting me in ten minutes. State real business or move along.",
      "I have no idea what you're on about, and time is money in Thornhaven. Let's talk about something that actually matters."
    ],
    finn: [
      "Wait, what? I don't really know what you mean, and I have to get back to watching the mill roof anyway before Dad catches me!",
      "I don't know anything about that! Plus I'm supposed to be finishing my sweeping chores right now so I can't talk long.",
      "Uh, I have no clue what that is. Ask one of the elders! I have to go check my secret trail markers!"
    ],
    eva: [
      "I have three boiling tinctures on the stove that need constant watching. This isn't the best time for idle chatter.",
      "I'm in a bit of a rush preparing seasonal remedies right now. If you don't need medicine or have herbs to trade, let's speak later.",
      "I don't know what to make of that, traveler. My focus right now is on treating the sick."
    ],
    tabitha: [
      "This is not the time or place for such wanderings of the mind, child. I have ancient scrolls requiring deep study.",
      "I sense no purpose in what you say, traveler. I am occupied with the valley records. Speak only of what has true weight.",
      "The elder texts hold no answers for such trivialities. I must return to my contemplation."
    ],
    sam: [
      "I'm in the middle of tempering folded steel over a hot fire. I don't have time for this right now.",
      "This isn't the time for idle chatter. If you don't have a weapon to forge or repair, let me get back to the anvil.",
      "I don't know what you're rambling about, and the forge fires are burning hot. Make it quick or come back tomorrow."
    ],
    // Legacy alias lookups
    brynn_ironhand: [
      "I am on active watch duty and have no time for pointless chatter. Keep the peace, or move along.",
      "This is not the time for games. The garrison is inspecting the outer walls."
    ]
  }};

// Synchronize legacy aliases in npcIntents


