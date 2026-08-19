"""
Extra narrative corpus entries — covering random everyday/personality questions.
These are merged into NPC_NARRATIVE_CORPUS in narrative_engine.py at module load.
"""

EXTRA_NARRATIVE_CORPUS = {
    "sam": [
        {
            "id": "sam_favorite_things",
            "title": "Sam's Preferences — Food, Rest, and Leisure",
            "keywords": ["favorite food", "favorite drink", "what do you eat", "what do you drink",
                         "mushroom stew", "black tea", "favorite meal", "relax after work", "forge food"],
            "primary": "After a twelve-hour shift at the forge I want nothing more than a bowl of Eva's thick mushroom stew and a mug of strong black tea. No wine, no spirits — I need my hands steady in the morning. On rare days off I sharpen old blades and listen to Tabitha tell stories.",
            "causal": "Forge work demands absolute precision. A trembling hand turns a masterwork blade into scrap metal. So I made peace with simple food and early nights a long time ago.",
            "philosophical": "Joy doesn't have to be grand. Sometimes it's just the silence after the last hammer blow, the cooling tick of good steel, and the knowledge that today's work was honest.",
            "followup": "What do you do to recover after a hard day on the road?"
        },
        {
            "id": "sam_on_magic",
            "title": "Sam's Views on Magic and Mages",
            "keywords": ["magic", "mage", "spell", "arcane", "sorcery", "wizard", "enchantment", "leyline",
                         "supernatural", "mystic", "opinion on magic", "believe magic"],
            "primary": "Magic is a tool, same as a hammer. I have no quarrel with it as long as the person wielding it has sense. What I distrust is mages who think raw power replaces skill, discipline, and the patience to learn their craft properly.",
            "causal": "I have forged enchanted blades for mages who later snapped them channeling more power than the steel could handle. You can infuse a blade with leyline energy all day long — if the underlying metalwork is sloppy, it will still shatter under pressure.",
            "philosophical": "Magic and metallurgy are not so different. Both require you to understand your materials deeply, respect their limits, and never force what the metal — or the world — isn't ready to give.",
            "followup": "Have you ever seen magic used in a way that genuinely impressed you?"
        },
        {
            "id": "sam_fears_and_weakness",
            "title": "Sam's Fears and Vulnerabilities",
            "keywords": ["afraid", "fear", "scared", "weakness", "vulnerable", "worry", "nightmare", "regret",
                         "doubt", "insecurity", "dying in bed", "substandard gear", "fear of failure"],
            "primary": "I don't talk about fear much. But if you're asking honestly — I'm afraid of dying in a bed with unfinished work on the anvil. I'm afraid of the village watch having sub-standard gear when the next real threat comes through that pass.",
            "causal": "You spend enough winters in active combat and you stop fearing death itself. What you start fearing is meaningless death — dying before you've built something worth leaving behind.",
            "philosophical": "Fear is the whetstone. It keeps your attention sharp and your instincts honest. The day you stop being afraid of anything is the day you've stopped caring about the outcome.",
            "followup": "What keeps you moving forward when things get difficult?"
        },
        {
            "id": "sam_on_friendship",
            "title": "Sam's Views on Friends and Trust",
            "keywords": ["friends", "friendship", "who do you trust", "closest friends", "comrades", "life debt", "bonds of loyalty"],
            "primary": "I have three real friends in this world: Eva, who mends what the forge breaks; Tabitha, to whom I owe a life debt I will never fully repay; and Pip, who reminds me that the forge is warm enough for laughter too.",
            "causal": "In the border wars, the soldiers I trusted most weren't the decorated officers — they were the ones who shared their rations when supplies ran short and stood the night watch without being ordered.",
            "philosophical": "Friendship forged in hardship is like folded steel — tested, layered, and nearly impossible to break. Friendship built only in comfort is closer to brittle iron.",
            "followup": "Who do you rely on most when things go badly?"
        },
        {
            "id": "sam_on_thornhaven",
            "title": "Sam's Feelings About Living in Thornhaven",
            "keywords": ["thornhaven", "village life", "why live here", "why stay in thornhaven", "opinion thornhaven", "defending thornhaven"],
            "primary": "I came to Thornhaven because it needed a real forge and a real smith. I stayed because the people here didn't ask too many questions and didn't run when the shadow beasts tested the perimeter walls. That earns respect in my ledger.",
            "causal": "After decades of traveling with armies and working capital forges, I needed a place where my hammer could do some actual good. Thornhaven needed better protection. I provide it.",
            "philosophical": "Home is not the place where you were born. Home is the place where the people around you are worth protecting.",
            "followup": "Do you feel like you belong here, or are you still searching for where you belong?"
        },
    ],

    "eva": [
        {
            "id": "eva_on_magic_healing",
            "title": "Eva's Views on Magic Versus Natural Healing",
            "keywords": ["magic healing", "mana healing", "arcane medicine", "magic vs herbs", "supernatural healing",
                         "opinion magic", "believe in magic", "leyline healing"],
            "primary": "Magic can accelerate healing, yes — but it cannot replace the underlying process. I have seen mages use arcane restoration spells on shattered bones only to have the patient's body reject the accelerated growth three weeks later. Natural healing takes time because the body must rebuild properly.",
            "causal": "The leyline energy that flows through this valley does interact with botanical compounds. My grandmother theorized that Frostmoss is so potent precisely because it grows near leyline convergence points.",
            "philosophical": "Magic and nature are not opposed — they are partners. The wisest healers learn to work with both, using each where it is strongest.",
            "followup": "Have you ever been treated by magical means, or only by traditional medicine?"
        },
        {
            "id": "eva_favorite_things",
            "title": "Eva's Daily Life, Preferences, and Routines",
            "keywords": ["sage tea", "favorite tea", "morning routine", "apothecary routine", "drying herbs", "quiet hour", "favorite herbal drink"],
            "primary": "My mornings begin before sunrise. I light the hearth, brew a cup of alpine sage tea, and spend an hour in silence tending the drying herbs on the rafters. It is my favorite hour of the entire day — quiet, purposeful, and mine alone.",
            "causal": "A healer who doesn't care for herself cannot properly care for others. I learned that lesson painfully during the plague years when I worked twenty-hour stretches and eventually collapsed.",
            "philosophical": "Peace is not a luxury. It is a medicine — one that costs nothing but discipline to take every day.",
            "followup": "Do you have a routine that keeps you centered and well?"
        },
        {
            "id": "eva_on_fear_and_sadness",
            "title": "Eva's Fears and What Keeps Her Going",
            "keywords": ["afraid", "great sickness", "plague", "fear of plague", "losing patients", "grief", "mourning", "loss of family"],
            "primary": "My greatest fear is a return of the Great Sickness — watching people suffer while I stand helpless with inadequate medicines. I keep a comprehensive stock of antivirals for that reason. Preparedness is the only antidote to that particular terror.",
            "causal": "Grief is familiar to me. I lost my grandmother, my village, and most of my childhood friends to the plague. I don't avoid those memories — I carry them carefully, like fragile glass vials.",
            "philosophical": "Sorrow is not weakness. It is the price of loving people who are mortal. I would rather feel this grief than live without the love that caused it.",
            "followup": "How do you process difficult emotions when they become overwhelming?"
        },
        {
            "id": "eva_on_animals",
            "title": "Eva's Knowledge of Forest Animals and Creatures",
            "keywords": ["forest animals", "creatures", "beasts", "wolves", "deer behavior", "forest wildlife", "wild animals", "fauna"],
            "primary": "The forest animals have been behaving strangely for two seasons now. The deer avoid the eastern riverbank entirely, the songbirds have shifted their nesting sites northward, and the wolves have pushed their territory closer to the village perimeter. Animals sense environmental changes long before humans notice them.",
            "causal": "I believe the corrupted leyline water is altering their behavior at a neurological level. Animals drinking from the violet-tinted stream become erratic and aggressive within days.",
            "philosophical": "Every creature in this forest is a living indicator of the forest's health. When they suffer, it is nature's way of telling us the balance has been broken.",
            "followup": "Have you noticed any unusual animal behavior on your travels recently?"
        },
        {
            "id": "eva_on_thornhaven",
            "title": "Eva's Role and Feelings About Thornhaven",
            "keywords": ["thornhaven apothecary", "why live in thornhaven", "settled in thornhaven", "healer's purpose", "apothecary history"],
            "primary": "Thornhaven chose me as much as I chose it. When I arrived, exhausted and nearly penniless, the apothecary shop was derelict and the previous healer had left without a replacement. I saw people who needed care and a space that needed purpose.",
            "philosophical": "A healer belongs wherever there are people who need healing. It is not about the place — it is about the purpose. Thornhaven gave me purpose, and in return I give it everything I know.",
            "followup": "Have you ever found a place that felt like it was waiting for you specifically?"
        },
    ],

    "tabitha": [
        {
            "id": "tabitha_on_magic",
            "title": "Tabitha's Deep Knowledge of Arcane Arts and Leylines",
            "keywords": ["arcane leylines", "leyline resonance", "arcane arts", "mana flows", "ancient rituals", "standing stones magic", "sundered crown keystones"],
            "primary": "The leylines beneath Thornhaven are not mere channels of raw power — they are the memory of the earth itself. Each leyline carries an imprint of every significant event that occurred along its path since the valley was first settled.",
            "causal": "When the keystones shattered during the War of the Sundered Crown, the leyline network fractured into unstable resonance loops. This is why certain areas of the valley produce inexplicable phenomena: objects moving without wind, voices heard in sealed chambers.",
            "philosophical": "Magic is not a gift granted to the worthy. It is a responsibility that requires complete understanding of consequence. Power without wisdom is merely destruction with a longer fuse.",
            "followup": "Have you felt any unusual sensations near the standing stones or the valley's edge?"
        },
        {
            "id": "tabitha_on_death_and_afterlife",
            "title": "Tabitha's Views on Death, the Afterlife, and Ancestors",
            "keywords": ["afterlife", "what happens after death", "ancestral spirits", "departed souls", "leyline memory", "immortality"],
            "primary": "The ancient texts describe the soul as a resonance pattern — a unique vibration that persists after the physical form dissolves. The departed do not vanish. They become part of the valley's accumulated memory, woven into the leyline record like verses added to an endless song.",
            "causal": "This is why the standing stones grow warmer near significant anniversaries. The leylines pulse with the accumulated energy of remembered grief, love, and sacrifice.",
            "philosophical": "We fear death because we imagine it as an ending. But an ending is only a failure of imagination. Everything that was truly essential about a person leaves a permanent mark on the world they touched.",
            "followup": "Is there someone from your past whose memory still guides your choices today?"
        },
        {
            "id": "tabitha_on_wisdom",
            "title": "Tabitha's Philosophy on Knowledge, Learning, and Wisdom",
            "keywords": ["wisdom vs knowledge", "grand archive", "scholarship", "philosophy of wisdom", "ancient learning", "lessons of history"],
            "primary": "In seventy-four years I have learned that wisdom and knowledge are entirely different things. Knowledge is accumulated facts — it fills a mind the way water fills a vessel. Wisdom is knowing which facts matter, when to act on them, and when to remain still.",
            "causal": "The Grand Archive taught me everything about recorded history but nothing about human nature. That education came from sitting with dying soldiers, listening to grieving mothers.",
            "philosophical": "The greatest scholars I have known were not those who read the most books — they were those who could sit with an unanswered question without demanding it resolve itself before they were ready.",
            "followup": "What is the most important thing you have learned not from a book but from lived experience?"
        },
        {
            "id": "tabitha_on_fear",
            "title": "Tabitha's Fears and What She Protects",
            "keywords": ["seal failing", "shadow remnants", "celestial ward fracture", "ancient threat", "cataclysm fear"],
            "primary": "My deepest fear is not death — I have made peace with that old companion long ago. What I fear is the seal failing while Thornhaven is unprepared. A fractured ward releasing the shadow remnants that have been imprisoned beneath this valley for over two centuries.",
            "causal": "I have read the original accounts of the War of the Sundered Crown. The shadow army was not defeated — it was contained. The distinction matters enormously. Containment requires constant vigilance.",
            "philosophical": "A guardian's truest fear is not the threat itself, but the moment she is no longer strong enough to stand between the threat and what she loves.",
            "followup": "What do you feel most compelled to protect in your own life?"
        },
        {
            "id": "tabitha_on_relationships",
            "title": "Tabitha's Relationships with the Villagers",
            "keywords": ["villagers", "opinions on villagers", "family in thornhaven", "care for villagers", "sam eva finn pip"],
            "primary": "Sam carries the fire of a warrior's devotion — I have never doubted her protection. Eva brings the quiet compassion of a healer who has truly suffered and chosen kindness anyway. Young Finn burns with potential he has not yet fully understood. And little Pip — Pip is pure wonder, uncorrupted by disappointment. They are my family.",
            "philosophical": "Family is not merely blood or legal bond. It is the collection of souls who have seen your worst days and chosen to remain anyway. That choice, repeated daily, is love in its most honest form.",
            "followup": "Who in your life has chosen to stay when staying was not easy?"
        },
        {
            "id": "tabitha_on_food_and_daily",
            "title": "Tabitha's Daily Life and Simple Pleasures",
            "keywords": ["pine needle tea", "archive manuscripts", "standing stones inspection", "tabitha morning routine"],
            "primary": "I begin each day before sunrise with pine-needle tea and an hour reading the oldest manuscripts in the archive. By midmorning I tend the standing stones, checking the runes for temperature changes. The afternoon I reserve for visitors — young Pip especially, who brings more questions per minute than most scholars manage in a week.",
            "causal": "At my age, the body needs simple, consistent things. Clear water, warm food, regular sleep, and the sense that today's work mattered. Everything else is decoration.",
            "philosophical": "The grand tapestry of history is woven from the humblest daily choices — what we eat, how we speak to one another, whether we choose patience over irritation in small moments.",
            "followup": "What small daily habit do you believe shapes who you are more than any grand decision?"
        },
    ],

    "finn": [
        {
            "id": "finn_on_magic",
            "title": "Finn's Thoughts on Magic and Mysterious Events",
            "keywords": ["standing stones glowing", "breathing well", "weird valley phenomena", "scout notebook mysteries", "unexplained occurrences"],
            "primary": "Okay so I used to think magic was just Tabitha stories to keep kids in bed at night. Then I saw the standing stones glow orange at midnight during the last equinox and I completely changed my position on that.",
            "causal": "There are things in this valley that don't follow normal rules. The well breathing. The stones glowing. The path that seems shorter going north than south even though it's the same distance on the map. I document everything in my notebook.",
            "philosophical": "Adults dismiss weird stuff because admitting they don't understand something feels dangerous to them. But not understanding something is exactly the right reason to start paying attention.",
            "followup": "Have you ever seen something that you couldn't explain with ordinary logic?"
        },
        {
            "id": "finn_on_friends",
            "title": "Finn's Friendships and How He Sees People",
            "keywords": ["sam and eva", "fellow villagers", "scout companions", "who finn looks up to", "mentor"],
            "primary": "Sam pretends to hate having me around the forge but she always has a spare crate near the anvil where I sit. Eva teaches me herb names and gives me honey drops when I help carry her supply crates. Tabitha knows everything I'm going to say before I say it, which is honestly terrifying. And Pip — Pip just makes everything louder and more exciting.",
            "philosophical": "The adults in this village act like they have everything figured out. They don't. But the good ones are honest about that and help you figure things out anyway. Those are the ones worth following.",
            "followup": "Who is the person in your life who made the biggest difference?"
        },
        {
            "id": "finn_on_fear_courage",
            "title": "Finn on Fear, Bravery, and Real Courage",
            "keywords": ["whispering woods fear", "facing fear", "scout bravery", "scary ridge", "courage definition"],
            "primary": "I'm not going to pretend I've never been scared. The first time I went past the stone markers into the Whispering Woods alone, I ran back twice before I actually made it through. Being brave doesn't mean not being scared. It means going anyway.",
            "causal": "My mom used to say the bravest thing she ever did was get out of bed the morning after my dad said she might be sick. Not fighting dragons — just getting up when everything felt impossible. That always stuck with me.",
            "philosophical": "Courage isn't a thing you have permanently. You have to find it fresh every time the fear comes back. That's actually what makes it worth having.",
            "followup": "What's the scariest thing you've ever had to do anyway?"
        },
        {
            "id": "finn_on_food_and_life",
            "title": "Finn's Everyday Life, Hobbies, and Preferences",
            "keywords": ["barley bread", "smoked fish meals", "scouting routine", "belltower star watching", "daily scout life"],
            "primary": "After morning drills I usually eat whatever the mill kitchen has going — barley bread and smoked fish mostly. Then I check my observation posts, update my notebook, and spend the afternoon on the ridges. Eva sometimes sends fresh fruit with Pip. It is a really good system.",
            "causal": "I don't have much time for relaxing exactly — there's always something to document or scout. But sometimes on long nights when the weather is clear I sit on the belltower roof and watch the stars. That's probably my version of rest.",
            "philosophical": "The best days are the ones where you go to bed knowing more than you did when you woke up. Even if what you learned is just that the north path is two minutes shorter than you calculated.",
            "followup": "What does a perfect day look like to you?"
        },
        {
            "id": "finn_on_weapons_training",
            "title": "Finn's Archery Training and Combat Skills",
            "keywords": ["archery training", "bow and arrow", "scout speed", "climbing speed", "target practice", "scout combat"],
            "primary": "I'm not the strongest person in Thornhaven — that's obviously Sam — but I'm the fastest. I can climb the belltower in forty seconds flat, outrun any of the village watch over a quarter mile, and my archery accuracy at fifty yards has improved to about seventy percent center-mass.",
            "causal": "Speed and perception are the scout's real weapons. A scout who gets into a brawl has already failed — the job is to see, report, and get out without being seen. So I train for distance running, climbing, and long-range accuracy.",
            "procedural": "For archery: anchor consistently, breathe out slowly, release on the natural pause between breaths. At distance you aim slightly above target to compensate for arrow drop. Wind compensation comes with practice.",
            "philosophical": "The best weapon is the one that means you never had to use your second-best weapon. Preparation is its own kind of armor.",
            "followup": "What skills have you worked hardest to develop on your own?"
        },
        {
            "id": "finn_on_sports_and_running",
            "title": "Finn on Running, Athletics, and Rooftop Games",
            "keywords": ["sports", "athletics", "running", "race", "racing", "climbing roofs", "obstacle course", "agility", "do you play sports", "fitness"],
            "primary": "I run sprint drills every single morning across the ridge bluffs and rooftop beams! We don't have stadium sports here, but I practice timed belltower climbs and sprint races with the courier riders. Speed and stamina keep you alive when you're scouting dangerous territory!",
            "causal": "Outrunning a shadow beast or scrambling up a sheer rock face before a goblin archer draws an arrow requires serious athletic conditioning. I train my calves and core every day.",
            "philosophical": "Sports and drills aren't just games to pass time — they're how you teach your body to react without hesitation when the real moment arrives.",
            "followup": "Do you train in running, climbing, or any specific athletic sports?"
        }
    ],

    "ash": [
        {
            "id": "ash_ancient_ruins_smuggler_route",
            "title": "Safe Smuggler Route to the Ancient Castle Ruins",
            "keywords": ["ancient ruins route", "castle ruins path", "safe smuggler route", "drainage flumes route", "subterranean ruins access"],
            "primary": "Looking for a safe path into the ancient ruins? Don't take the main surface road through the gorge — it's swarming with dire wolves and guard patrols. The old wine smugglers carved subterranean drainage flumes beneath the tavern cellar that connect directly into the lower foundation vaults of the castle ruins. Keep your lantern low and watch for damp shale.",
            "causal": "When the castle fell two centuries ago, the garrison sealed the main gates with stone boulders. But the smugglers' drainage tunnels were carved out of living limestone, so they bypassed the collapse entirely.",
            "philosophical": "The front door is for armies and fools. Anyone who understands leverage enters through the foundation.",
            "followup": "Are you prepared to navigate unmapped tunnels in the dark?"
        },
        {
            "id": "ash_on_trust_and_loyalty",
            "title": "Ash's Philosophy on Trust, Loyalty, and Betrayal",
            "keywords": ["trust and betrayal", "philosophy on loyalty", "syndicate contracts", "reliable contacts", "brokers code"],
            "primary": "Trust is a contract, not a feeling. I trust Sam to forge steel that won't shatter. I trust Eva to ask no questions when I show up with a knife wound. I trust Tabitha to see through everything I say — which is actually useful, because it keeps me honest when nothing else does.",
            "causal": "Every betrayal I have experienced came from someone who had more to gain from the betrayal than from the loyalty. Understanding that isn't cynicism — it's calibration.",
            "philosophical": "Loyalty without self-interest is rare and therefore extremely valuable. When you find it, protect it fiercely. But never mistake affection for loyalty — they often travel together but they are not the same thing.",
            "followup": "Has anyone ever surprised you by being more loyal than you expected?"
        },
        {
            "id": "ash_on_magic",
            "title": "Ash's Views on Magic and Power",
            "keywords": ["magic as leverage", "leyline keys", "arcane politics", "magical contraband", "power brokering"],
            "primary": "Magic is the same as any other form of leverage — whoever controls it has the upper hand. I am less interested in the arcane theory and more interested in who currently holds the leyline access keys and what they intend to do with them.",
            "causal": "The seal fractures are not just a mystical problem — they are a political one. Every faction in the valley has an opinion on how the keystones should be handled. Tabitha wants restoration. The village council wants containment.",
            "philosophical": "Raw power without information about how to deploy it is just noise. Real power is knowing who else knows, who wants what, and what they will trade to get it.",
            "followup": "If you could have one advantage — strength, speed, magic, or information — which would you choose?"
        },
        {
            "id": "ash_fears_and_vulnerabilities",
            "title": "Ash's Fears and Private Vulnerabilities",
            "keywords": ["silver serpent syndicate", "fear of irrelevance", "syndicate retribution", "losing control", "hidden vulnerabilities"],
            "primary": "What frightens me most? Fine — being found by the Silver Serpent Syndicate is the obvious answer. But the quiet fear, the one I don't examine too closely, is becoming irrelevant. Losing the information edge. Becoming just another person that events happen to instead of someone who shapes them.",
            "causal": "Control is the armor I wear. When I controlled the ledgers at the Syndicate, I was untouchable. The night I fled with only the clothes on my back and a stolen book, I understood for the first time what it felt like to be powerless.",
            "philosophical": "Every person has a wound they protect with a particular kind of armor. Mine is information. The question worth asking is whether the armor is protecting you or imprisoning you.",
            "followup": "What are you protecting that you pretend not to care about?"
        },
        {
            "id": "ash_on_money_and_work",
            "title": "Ash's Philosophy on Money, Trade, and Work",
            "keywords": ["money and power", "information price", "broker economics", "debt and leverage", "trade philosophy"],
            "primary": "Everything has a price — that's not cynicism, that's clarity. Once you accept that, negotiation becomes honest. I charge fairly, deliver what I promise, and never misrepresent the quality of my information. In a world full of cheats, reliable service is actually the rarest commodity.",
            "causal": "The Syndicate taught me how power flows through money. Who holds the debt controls the debtor. Who holds the information controls the narrative. I prefer information — it doesn't depreciate.",
            "philosophical": "The problem with purely chasing money is that you eventually acquire enough to realize it was never the actual goal. What people are really buying is security, respect, or freedom. I sell all three.",
            "followup": "What would you spend real money on, if you had more than you needed?"
        },
        {
            "id": "ash_daily_life",
            "title": "Ash's Daily Routine, Preferences, and Habits",
            "keywords": ["dead drops review", "tavern intelligence", "broker schedule", "black coffee routine", "listening posts check"],
            "primary": "I wake before anyone else is moving, check my dead-drops around the village, and spend an hour reviewing the previous day's intelligence over black coffee and yesterday's bread. The afternoon is for appointments. Evenings I spend in the tavern where everyone is relaxed enough to say things they shouldn't.",
            "causal": "The best intelligence comes from people who aren't being careful. Morning is when they're guarded. Evening, after a few drinks, is when they're not. I structure my entire day around exploiting that window.",
            "philosophical": "Pattern recognition is the core of this work. Once you know someone's habits, their lies become obvious and their fears become legible. I don't read people's minds — I read their schedules.",
            "followup": "What patterns have you noticed about people on the road that others seem to miss?"
        },
    ],

    "pip": [
        {
            "id": "pip_on_magic_and_mystery",
            "title": "Pip's Experience with Magic and Mysterious Things",
            "keywords": ["glowing blue rock", "standing stones humming", "magic stones", "fairy rock", "magic belief", "pip magic"],
            "primary": "I DEFINITELY believe in magic! The blue rock I found glows a little bit at night — just a tiny bit, like a firefly! And I once saw the old standing stones make a humming sound that I could feel in my chest but not hear with my ears. Tabitha says that's totally normal. I think that means it's totally magic!",
            "causal": "Grown-ups say lots of magical things are just tricks of the light or the wind. But the wind doesn't make a sound you feel in your bones. And tricks of the light don't make warm stones on a cold night. I keep a list of ALL the things that can't be explained!",
            "philosophical": "Magic isn't just for wizards and ancient scrolls. Magic is when something happens that shouldn't be possible but happens anyway. That's everywhere if you look!",
            "followup": "What's the most magical thing you've ever seen or felt?"
        },
        {
            "id": "pip_on_scary_things",
            "title": "Pip's Fears and Brave Moments",
            "keywords": ["chapel basement", "dripping sound", "scary monsters", "pip fears", "dark basement fear", "bravery"],
            "primary": "I'm NOT scared of the dark! Well... I AM a little scared of the dark in the chapel basement because it makes a specific kind of dripping sound that I do not like. But everything else I'm totally fine with! Mostly!",
            "causal": "Finn says being scared and being brave are actually the same feeling — the brave feeling just has better shoes and keeps walking anyway. I wrote that in my notebook because it's the best thing I've heard this week.",
            "philosophical": "Grown-ups pretend they're never scared. But you can tell when they are because their hands do the thing where they're very still when normally they're moving. I notice that.",
            "followup": "What makes you feel brave when you're scared?"
        },
        {
            "id": "pip_on_food_and_fun",
            "title": "Pip's Favorite Food and Treats",
            "keywords": ["favorite food", "favorite meal", "eva's berry pie", "berry pie", "smoked fish rolls", "favorite pie",
                         "what do you eat", "what is your favorite food", "favorite snack", "pastry", "sweets", "pies"],
            "primary": "My ABSOLUTE favorite food is Eva's berry pie with the crumbly top! She makes it when someone in the village has a sad thing happen, which is great for the pie but obviously not great for the sad thing. Also I really like the smoked fish rolls from the market on Tuesdays!",
            "causal": "I eat a LOT because I run everywhere all day. Sam says I have the metabolism of a dire wolf pup. I don't know what that means exactly but it sounded like a good thing in context!",
            "philosophical": "The best things in life are free OR very cheap because I only have a few coins and I still have an amazing life so that proves it!",
            "followup": "What's your absolute favorite thing that you look forward to every single day?"
        },
        {
            "id": "pip_on_games_and_sports",
            "title": "Pip's Games, Sports, and Running Adventures",
            "keywords": ["sports", "sport", "game", "games", "do you play sports", "do you like sports", "play games",
                         "tag", "hide and seek", "racing", "climbing trees", "outdoor games", "athletics", "running fast"],
            "primary": "I LOVE playing games and running super fast! Finn and I play rooftop tag, and I practice racing against grasshoppers down by the creek! Grown-ups call it 'sports' when there are teams and rules, but my absolute favorite game is seeing who can climb to the top branch of the big apple tree the fastest without dropping any shiny river stones!",
            "causal": "Running fast is super important because when you're eight years old, all the adults have giant legs and take huge steps! So you have to be extra speedy and know all the secret crawlspaces under fences!",
            "philosophical": "Games and sports are the greatest thing ever because nobody is mad at each other while they're playing, and everyone laughs when you trip over a pumpkin in the garden!",
            "followup": "What's your absolute favorite sport or game to play?"
        },
    ],
}
