"""
Lingexa Across - British vs American English
"""

import os, sys, json, random, asyncio, subprocess, urllib.request
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

load_dotenv()
POLLINATIONS_API_KEY = os.getenv("POLLINATIONS_API_KEY")
AI_MODEL = os.getenv("AI_MODEL")
if not AI_MODEL:
    raise ValueError("AI_MODEL not set!")

BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / "output"
VIDEO_DIR = OUTPUT_DIR / "video"
HISTORY_DIR = OUTPUT_DIR / "history"
for d in [OUTPUT_DIR, VIDEO_DIR, HISTORY_DIR]:
    d.mkdir(exist_ok=True)

VIDEO_WIDTH = 1080
VIDEO_HEIGHT = 1920
FPS = 30
BRITISH_VOICE = "en-GB-RyanNeural"
AMERICAN_VOICE = "en-US-GuyNeural"
CHANNEL_NAME = "Lingexa Across"
WORDS_PER_VIDEO = 3
PAIR_HISTORY_FILE = HISTORY_DIR / "all_generated_pairs.json"
FONTS_DIR = Path(__file__).parent / "fonts"
FLAGS_DIR = FONTS_DIR / "flags"

def ensure_flags():
    FLAGS_DIR.mkdir(parents=True, exist_ok=True)
    flags = {
        "uk.png": "https://flagcdn.com/48x36/gb.png",
        "us.png": "https://flagcdn.com/48x36/us.png",
    }
    for name, url in flags.items():
        path = FLAGS_DIR / name
        if not path.exists() or path.stat().st_size < 100:
            try:
                print(f"[flag] Downloading {name}...")
                urllib.request.urlretrieve(url, str(path))
                if path.exists() and path.stat().st_size > 100:
                    print(f"[flag] Downloaded {name}")
            except Exception as e:
                print(f"[flag] Failed to download {name}: {e}")
    return FLAGS_DIR

def load_pair_history():
    if PAIR_HISTORY_FILE.exists():
        with open(PAIR_HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"pairs": [], "last_updated": None}

def save_pair_history(data):
    data["last_updated"] = datetime.now().isoformat()
    with open(PAIR_HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def is_pair_used(brit_word, us_word, history=None, recent_window=80):
    if history is None:
        history = load_pair_history()
    bw = brit_word.lower().strip()
    uw = us_word.lower().strip()
    pairs = history.get("pairs", [])
    # Check against recent window (default last 80 pairs = ~5 days of 5x daily uploads)
    # This prevents duplicates in the short term while allowing healthy vocabulary rotation.
    recent_pairs = pairs[-recent_window:] if recent_window and len(pairs) > recent_window else pairs
    for p in recent_pairs:
        pb = p.get("british", "").lower().strip()
        pu = p.get("american", "").lower().strip()
        if (pb == bw and pu == uw) or (pb == uw and pu == bw):
            return True
        # Prevent headword repetition within the most recent 25 pairs (~1.5 days)
        if len(recent_pairs) >= 25 and p in recent_pairs[-25:]:
            if pb == bw or pu == uw:
                return True
    return False

def add_pairs_to_history(pairs):
    history = load_pair_history()
    for p in pairs:
        history["pairs"].append({
            "british": p["british"],
            "american": p["american"],
            "category": p.get("category", ""),
            "generated_at": datetime.now().isoformat()
        })
    save_pair_history(history)

# Curated library of authentic British vs American vocabulary differences
CURATED_UNSEEN_PAIRS = [
    # Baby and Parenting
    {"british": "pram", "american": "baby carriage", "part_of_speech": "noun", "definition": "four-wheeled carriage for infants", "british_example": "She pushed the baby in a pram.", "american_example": "A vintage baby carriage.", "category": "baby and parenting"},
    {"british": "pushchair", "american": "stroller", "part_of_speech": "noun", "definition": "folding wheeled chair for toddlers", "british_example": "Fold the pushchair before boarding.", "american_example": "Keep the baby in the stroller.", "category": "baby and parenting"},
    {"british": "dummy", "american": "pacifier", "part_of_speech": "noun", "definition": "soothing rubber teat for babies", "british_example": "The baby calmed down with a dummy.", "american_example": "Don't drop the pacifier.", "category": "baby and parenting"},
    {"british": "nappy", "american": "diaper", "part_of_speech": "noun", "definition": "absorbent garment worn by infants", "british_example": "Change the baby's wet nappy.", "american_example": "Buy a box of disposable diapers.", "category": "baby and parenting"},
    {"british": "cot", "american": "crib", "part_of_speech": "noun", "definition": "slatted high-sided bed for infant", "british_example": "The baby slept soundly in the cot.", "american_example": "Place the newborn in the crib.", "category": "baby and parenting"},

    # Clothing and Styling
    {"british": "waistcoat", "american": "vest", "part_of_speech": "noun", "definition": "sleeveless buttoned garment over shirt", "british_example": "He wore a silk waistcoat with his suit.", "american_example": "A three-piece suit includes a vest.", "category": "clothing and styling"},
    {"british": "braces", "american": "suspenders", "part_of_speech": "noun", "definition": "shoulder straps supporting trousers", "british_example": "He fastened leather braces to his trousers.", "american_example": "Elastic suspenders keep pants up.", "category": "clothing and styling"},
    {"british": "suspenders", "american": "garter belt", "part_of_speech": "noun", "definition": "fasteners holding up stockings", "british_example": "Vintage silk suspenders.", "american_example": "A lace garter belt.", "category": "clothing and styling"},
    {"british": "plimsolls", "american": "gym shoes", "part_of_speech": "noun", "definition": "light canvas rubber-soled sports shoes", "british_example": "Pupils wear plimsolls in PE class.", "american_example": "Lace up your gym shoes.", "category": "clothing and styling"},
    {"british": "wellingtons", "american": "rubber boots", "part_of_speech": "noun", "definition": "waterproof knee-high rubber rain boots", "british_example": "Put on wellingtons for the muddy walk.", "american_example": "Stomp through puddles in rubber boots.", "category": "clothing and styling"},
    {"british": "mackintosh", "american": "raincoat", "part_of_speech": "noun", "definition": "waterproof coat protecting from rain", "british_example": "Button up your mackintosh in the drizzle.", "american_example": "She wore a yellow raincoat.", "category": "clothing and styling"},
    {"british": "pinafore dress", "american": "jumper dress", "part_of_speech": "noun", "definition": "sleeveless dress worn over blouse", "british_example": "A grey school pinafore dress.", "american_example": "Corduroy jumper dress with a turtleneck.", "category": "clothing and styling"},
    {"british": "polo neck", "american": "turtleneck", "part_of_speech": "noun", "definition": "high turned-over close-fitting collar", "british_example": "A warm black woollen polo neck.", "american_example": "Layer a turtleneck under the jacket.", "category": "clothing and styling"},
    {"british": "dressing gown", "american": "bathrobe", "part_of_speech": "noun", "definition": "warm robe worn around the house", "british_example": "Tie the belt of your dressing gown.", "american_example": "Soft cotton bathrobe after shower.", "category": "clothing and styling"},
    {"british": "swimming costume", "american": "swimsuit", "part_of_speech": "noun", "definition": "garment worn for swimming in water", "british_example": "Pack a swimming costume for holiday.", "american_example": "She put on a red swimsuit.", "category": "clothing and styling"},
    {"british": "kirby grip", "american": "bobby pin", "part_of_speech": "noun", "definition": "small flat metal wire hairpin", "british_example": "Pin your curls with a kirby grip.", "american_example": "Slide a bobby pin into hair.", "category": "clothing and styling"},
    {"british": "hair bobble", "american": "hair tie", "part_of_speech": "noun", "definition": "elastic band holding ponytail hair", "british_example": "Fasten your braid with a hair bobble.", "american_example": "She needed an elastic hair tie.", "category": "clothing and styling"},
    {"british": "bootlace", "american": "shoelace", "part_of_speech": "noun", "definition": "cord used to tie footwear securely", "british_example": "Tie your muddy bootlace tightly.", "american_example": "He broke his black shoelace.", "category": "clothing and styling"},
    {"british": "bumbag", "american": "fanny pack", "part_of_speech": "noun", "definition": "small waist pouch for essentials", "british_example": "Wear a bumbag on long walks.", "american_example": "Tourist wearing a neon fanny pack.", "category": "clothing and styling"},

    # Stationery and Office
    {"british": "full stop", "american": "period", "part_of_speech": "noun", "definition": "punctuation mark ending declarative sentence", "british_example": "Always end sentences with a full stop.", "american_example": "Don't forget the period at the end.", "category": "stationery and office"},
    {"british": "inverted commas", "american": "quotation marks", "part_of_speech": "noun", "definition": "punctuation marks enclosing dialogue", "british_example": "Put the quote in inverted commas.", "american_example": "Surround the title with quotation marks.", "category": "stationery and office"},
    {"british": "rubber", "american": "eraser", "part_of_speech": "noun", "definition": "rubber block erasing pencil marks", "british_example": "Rub out the mistake with a rubber.", "american_example": "Use a pencil eraser to fix it.", "category": "stationery and office"},
    {"british": "tipex", "american": "white-out", "part_of_speech": "noun", "definition": "correction fluid covering pen mistakes", "british_example": "Dab Tipp-Ex over the typo.", "american_example": "Cover ink errors with White-Out.", "category": "stationery and office"},
    {"british": "pencil case", "american": "pencil pouch", "part_of_speech": "noun", "definition": "zippered case holding pens and pencils", "british_example": "Zip your pencil case before class.", "american_example": "A canvas pencil pouch for school.", "category": "stationery and office"},
    {"british": "geometry set", "american": "math set", "part_of_speech": "noun", "definition": "case with compass ruler protractor", "british_example": "Bring your geometry set to exam.", "american_example": "A student math set with ruler.", "category": "stationery and office"},
    {"british": "drawing pin", "american": "thumbtack", "part_of_speech": "noun", "definition": "short flat-headed pin for corkboards", "british_example": "Fasten the poster with a drawing pin.", "american_example": "Stick a thumbtack into the board.", "category": "stationery and office"},
    {"british": "sellotape", "american": "scotch tape", "part_of_speech": "noun", "definition": "clear sticky adhesive cellophane tape", "british_example": "Wrap Christmas presents with Sellotape.", "american_example": "Fasten the note with Scotch tape.", "category": "stationery and office"},
    {"british": "pritt stick", "american": "glue stick", "part_of_speech": "noun", "definition": "solid adhesive stick for craft paper", "british_example": "Stick pictures with a Pritt Stick.", "american_example": "School children using glue sticks.", "category": "stationery and office"},
    {"british": "rubber band", "american": "elastic band", "part_of_speech": "noun", "definition": "stretchable looped rubber cord fastener", "british_example": "Bundle letters with a rubber band.", "american_example": "Wrap an elastic band around cables.", "category": "stationery and office"},
    {"british": "hole punch", "american": "hole puncher", "part_of_speech": "noun", "definition": "tool punching holes in document sheets", "british_example": "Use a metal hole punch on reports.", "american_example": "Desktop two-hole puncher.", "category": "stationery and office"},

    # Sports and Games
    {"british": "table tennis", "american": "ping pong", "part_of_speech": "noun", "definition": "indoor table game with paddles", "british_example": "Play table tennis at the youth club.", "american_example": "A lively game of ping pong in garage.", "category": "sports and games"},
    {"british": "skipping rope", "american": "jump rope", "part_of_speech": "noun", "definition": "cord swung around while jumping", "british_example": "Children chanting with a skipping rope.", "american_example": "Boxers training with a jump rope.", "category": "sports and games"},
    {"british": "noughts and crosses", "american": "tic-tac-toe", "part_of_speech": "noun", "definition": "game of three-in-a-row marks", "british_example": "Play noughts and crosses on scrap paper.", "american_example": "Draw a tic-tac-toe grid.", "category": "sports and games"},
    {"british": "pitch", "american": "sports field", "part_of_speech": "noun", "definition": "marked grass surface for ball games", "british_example": "Run onto the football pitch.", "american_example": "The grass on the sports field.", "category": "sports and games"},
    {"british": "touchline", "american": "sideline", "part_of_speech": "noun", "definition": "side boundary line of pitch", "british_example": "The manager shouted from the touchline.", "american_example": "Cheer from the sideline.", "category": "sports and games"},

    # Medical and Pharmacy
    {"british": "chemist", "american": "pharmacy", "part_of_speech": "noun", "definition": "shop dispensing medicinal prescriptions", "british_example": "Pick up prescription pills at chemist.", "american_example": "Visit the 24-hour pharmacy.", "category": "medical and pharmacy"},
    {"british": "paracetamol", "american": "acetaminophen", "part_of_speech": "noun", "definition": "common fever-reducing painkiller drug", "british_example": "Take two paracetamol for headache.", "american_example": "Acetaminophen helps lower fever.", "category": "medical and pharmacy"},
    {"british": "casualty", "american": "emergency room", "part_of_speech": "noun", "definition": "hospital emergency trauma ward", "british_example": "He rushed his broken wrist to casualty.", "american_example": "Wait in the emergency room lobby.", "category": "medical and pharmacy"},
    {"british": "surgical spirit", "american": "rubbing alcohol", "part_of_speech": "noun", "definition": "antiseptic alcohol for skin disinfection", "british_example": "Clean the cut with surgical spirit.", "american_example": "Swab the skin with rubbing alcohol.", "category": "medical and pharmacy"},
    {"british": "cotton bud", "american": "q-tip", "part_of_speech": "noun", "definition": "small swab stick with cotton ends", "british_example": "Clean small edges with a cotton bud.", "american_example": "Dab ointment using a Q-tip.", "category": "medical and pharmacy"},
    {"british": "cotton wool", "american": "cotton balls", "part_of_speech": "noun", "definition": "soft raw fluffy cotton for wounds", "british_example": "Clean the scratch with cotton wool.", "american_example": "Dab makeup remover with cotton balls.", "category": "medical and pharmacy"},
    {"british": "sticking plaster", "american": "adhesive strip", "part_of_speech": "noun", "definition": "small adhesive bandage strip dressing", "british_example": "Put a sticking plaster on your finger.", "american_example": "Cover blisters with an adhesive strip.", "category": "medical and pharmacy"},

    # Household Objects and DIY
    {"british": "kitchen roll", "american": "paper towels", "part_of_speech": "noun", "definition": "absorbent paper sheets for spills", "british_example": "Clean the spill with kitchen roll.", "american_example": "Grab a sheet of paper towels.", "category": "household objects"},
    {"british": "cling film", "american": "plastic wrap", "part_of_speech": "noun", "definition": "thin clear food wrap film", "british_example": "Wrap the sandwiches in cling film.", "american_example": "Cover the salad with plastic wrap.", "category": "household objects"},
    {"british": "washing-up liquid", "american": "dish soap", "part_of_speech": "noun", "definition": "liquid soap for washing dishes", "british_example": "Pour washing-up liquid into the sink.", "american_example": "Use mild dish soap on pans.", "category": "household objects"},
    {"british": "tea towel", "american": "dish towel", "part_of_speech": "noun", "definition": "cloth for drying washed dishes", "british_example": "Dry wine glasses with a tea towel.", "american_example": "Hang the wet dish towel.", "category": "household objects"},
    {"british": "rubbish bin", "american": "trash can", "part_of_speech": "noun", "definition": "receptacle for household waste", "british_example": "Throw wrappers in the rubbish bin.", "american_example": "Empty the bedroom trash can.", "category": "household objects"},
    {"british": "wheelie bin", "american": "trash cart", "part_of_speech": "noun", "definition": "large plastic bin on wheels", "british_example": "Wheel the wheelie bin outside.", "american_example": "Roll the trash cart to curb.", "category": "household objects"},
    {"british": "clothes peg", "american": "clothespin", "part_of_speech": "noun", "definition": "clip holding wet laundry on line", "british_example": "Hang shirts with a clothes peg.", "american_example": "Wooden clothespins on the clothesline.", "category": "household objects"},
    {"british": "baking tin", "american": "baking pan", "part_of_speech": "noun", "definition": "metal container for baking in oven", "british_example": "Grease the loaf baking tin.", "american_example": "Pour cake batter into baking pan.", "category": "household objects"},
    {"british": "face cloth", "american": "washcloth", "part_of_speech": "noun", "definition": "small square towel for washing face", "british_example": "Wet the soft face cloth.", "american_example": "Warm washcloth over the forehead.", "category": "household objects"},
    {"british": "cooker hood", "american": "range hood", "part_of_speech": "noun", "definition": "exhaust fan canopy above stove", "british_example": "Turn on the cooker hood fan.", "american_example": "Stainless steel range hood.", "category": "household objects"},
    {"british": "skip", "american": "dumpster", "part_of_speech": "noun", "definition": "large open container for rubbish", "british_example": "Throw renovation rubble in the skip.", "american_example": "Toss bags into the dumpster.", "category": "household objects"},
    {"british": "white spirit", "american": "mineral spirits", "part_of_speech": "noun", "definition": "solvent for cleaning paint brushes", "british_example": "Clean brushes with white spirit.", "american_example": "Thin paint with mineral spirits.", "category": "household objects"},

    # Transport, Roads and Driving
    {"british": "sleeping policeman", "american": "speed bump", "part_of_speech": "noun", "definition": "raised ridge to slow cars", "british_example": "Drive slowly over the sleeping policeman.", "american_example": "Slow down for the speed bump.", "category": "roads and driving"},
    {"british": "estate car", "american": "station wagon", "part_of_speech": "noun", "definition": "car with large rear cargo space", "british_example": "They loaded luggage in the estate car.", "american_example": "The old family station wagon.", "category": "roads and driving"},
    {"british": "driving licence", "american": "driver's license", "part_of_speech": "noun", "definition": "official permit to drive motor vehicles", "british_example": "Show your valid driving licence.", "american_example": "Keep your driver's license in wallet.", "category": "roads and driving"},
    {"british": "number plate", "american": "license plate", "part_of_speech": "noun", "definition": "vehicle identification tag board", "british_example": "Read the rear number plate.", "american_example": "The front license plate was missing.", "category": "roads and driving"},
    {"british": "tailback", "american": "traffic jam", "part_of_speech": "noun", "definition": "long queue of stalled vehicles", "british_example": "A ten-mile tailback on the motorway.", "american_example": "Stuck in a heavy traffic jam.", "category": "roads and driving"},
    {"british": "hire car", "american": "rental car", "part_of_speech": "noun", "definition": "vehicle rented for short time", "british_example": "Pick up your hire car at Heathrow.", "american_example": "Book an economy rental car.", "category": "roads and driving"},
    {"british": "level crossing", "american": "grade crossing", "part_of_speech": "noun", "definition": "intersection where railway tracks cross road", "british_example": "The train passed the level crossing.", "american_example": "Red lights flashed at grade crossing.", "category": "roads and driving"},
    {"british": "dual carriageway", "american": "divided highway", "part_of_speech": "noun", "definition": "road separated by central barrier", "british_example": "Follow the dual carriageway north.", "american_example": "Merge onto the divided highway.", "category": "roads and driving"},
    {"british": "hard shoulder", "american": "road shoulder", "part_of_speech": "noun", "definition": "emergency stop lane alongside motorway", "british_example": "Pull over onto the hard shoulder.", "american_example": "Park on the road shoulder.", "category": "roads and driving"},
    {"british": "slip road", "american": "on-ramp", "part_of_speech": "noun", "definition": "access ramp onto high speed motorway", "british_example": "Speed up on the slip road.", "american_example": "Yield when entering the on-ramp.", "category": "roads and driving"},
    {"british": "flyover", "american": "overpass", "part_of_speech": "noun", "definition": "elevated bridge road above highway", "british_example": "Drive over the motorway flyover.", "american_example": "Traffic slowed beneath the overpass.", "category": "roads and driving"},

    # Food and Sweets
    {"british": "candy floss", "american": "cotton candy", "part_of_speech": "noun", "definition": "spun sugar confection on stick", "british_example": "She bought candy floss at the fair.", "american_example": "They ate pink cotton candy.", "category": "food and sweets"},
    {"british": "jacket potato", "american": "baked potato", "part_of_speech": "noun", "definition": "potato baked whole in skin", "british_example": "Jacket potato topped with cheese.", "american_example": "Steak served with baked potato.", "category": "food and sweets"},
    {"british": "icing sugar", "american": "powdered sugar", "part_of_speech": "noun", "definition": "finely ground white confectioner sugar", "british_example": "Dust the sponge with icing sugar.", "american_example": "Sprinkle powdered sugar on waffles.", "category": "food and sweets"},
    {"british": "ice lolly", "american": "popsicle", "part_of_speech": "noun", "definition": "frozen flavored ice confection on stick", "british_example": "Cool down with an orange ice lolly.", "american_example": "Summer treat of cherry popsicles.", "category": "food and sweets"},
    {"british": "sultana", "american": "golden raisin", "part_of_speech": "noun", "definition": "pale dried seedless white grape", "british_example": "Bake scones with sweet sultanas.", "american_example": "Toss golden raisins in oatmeal.", "category": "food and sweets"},

    # City, Society and Shopping
    {"british": "high street", "american": "main street", "part_of_speech": "noun", "definition": "primary retail shopping thoroughfare in town", "british_example": "Shops along the busy high street.", "american_example": "The town parade walked down Main Street.", "category": "city and navigation"},
    {"british": "dustbin lorry", "american": "garbage truck", "part_of_speech": "noun", "definition": "large vehicle collecting refuse", "british_example": "The dustbin lorry comes on Friday.", "american_example": "The early morning garbage truck.", "category": "city and navigation"},
    {"british": "lost property", "american": "lost and found", "part_of_speech": "noun", "definition": "office keeping mislaid items", "british_example": "Inquire at the lost property desk.", "american_example": "Hand the wallet to lost and found.", "category": "city and navigation"},
    {"british": "post code", "american": "zip code", "part_of_speech": "noun", "definition": "postal geographical delivery code", "british_example": "Include your correct post code.", "american_example": "Enter the five-digit zip code.", "category": "city and navigation"},
    {"british": "car boot sale", "american": "swap meet", "part_of_speech": "noun", "definition": "outdoor market selling secondhand goods", "british_example": "Bargains at Sunday car boot sale.", "american_example": "Browse antiques at the swap meet.", "category": "shopping and stores"},
    {"british": "off-licence", "american": "liquor store", "part_of_speech": "noun", "definition": "shop licensed to sell alcoholic drinks", "british_example": "Buy cold beer at the off-licence.", "american_example": "Stop by the local liquor store.", "category": "shopping and stores"},
    {"british": "greengrocer", "american": "produce store", "part_of_speech": "noun", "definition": "merchant selling fresh fruit and vegetables", "british_example": "Fresh strawberries from the greengrocer.", "american_example": "Organic neighborhood produce store.", "category": "shopping and stores"},
    {"british": "ironmonger", "american": "hardware store", "part_of_speech": "noun", "definition": "retail store selling tools and screws", "british_example": "Buy brass hinges at the ironmonger.", "american_example": "Find power tools at hardware store.", "category": "shopping and stores"},
    {"british": "fishmonger", "american": "fish market", "part_of_speech": "noun", "definition": "merchant selling fresh caught fish", "british_example": "Whole sea bass at the fishmonger.", "american_example": "Bustling harbor fish market.", "category": "shopping and stores"},
    {"british": "sweet shop", "american": "candy store", "part_of_speech": "noun", "definition": "retailer selling sugary confections", "british_example": "Jars of toffee in the sweet shop.", "american_example": "Vintage downtown candy store.", "category": "shopping and stores"},
    {"british": "primary school", "american": "elementary school", "part_of_speech": "noun", "definition": "school for children under eleven", "british_example": "Pupils start primary school at five.", "american_example": "She teaches at the elementary school.", "category": "school and learning"},
    {"british": "secondary school", "american": "high school", "part_of_speech": "noun", "definition": "school for teenagers aged eleven plus", "british_example": "He attends the local secondary school.", "american_example": "Senior year in American high school.", "category": "school and learning"},
    {"british": "public school", "american": "private school", "part_of_speech": "noun", "definition": "fee-paying independent boarding school", "british_example": "Eton is a famous public school.", "american_example": "They enrolled him in private school.", "category": "school and learning"},
    {"british": "tuck shop", "american": "snack bar", "part_of_speech": "noun", "definition": "school shop selling snacks and sweets", "british_example": "Buy crisps at morning tuck shop.", "american_example": "Campus cafeteria snack bar.", "category": "school and learning"},
    {"british": "dinner lady", "american": "lunch lady", "part_of_speech": "noun", "definition": "school cafeteria worker serving meals", "british_example": "The dinner lady served hot stew.", "american_example": "The cheerful school lunch lady.", "category": "school and learning"},
    {"british": "solicitor", "american": "attorney", "part_of_speech": "noun", "definition": "legal practitioner giving professional counsel", "british_example": "Consult a solicitor for contracts.", "american_example": "Represented by a skilled attorney.", "category": "work and business"},
    {"british": "barrister", "american": "trial lawyer", "part_of_speech": "noun", "definition": "advocate pleading cases in court", "british_example": "The barrister argued before the judge.", "american_example": "Cross-examination by trial lawyer.", "category": "work and business"},
    {"british": "current account", "american": "checking account", "part_of_speech": "noun", "definition": "standard everyday bank account for payments", "british_example": "Pay rent from your current account.", "american_example": "Deposit paychecks in checking account.", "category": "money and banking"},
]

def generate_pair_data(num_pairs=WORDS_PER_VIDEO):
    max_attempts = 15
    categories = [
        "kitchen and cooking", "driving, roads and transport", "street navigation and city life",
        "stationery and desk items", "household tools and DIY", "baby and parenting",
        "bathroom and toiletries", "clothing and accessories", "food and sweets",
        "leisure and hobbies", "money, shopping and banking", "school and university",
        "gardening and outdoors", "medical and pharmacy", "everyday household objects",
        "entertainment and pop culture", "buildings and architecture", "sports and games",
        "travel, train and holiday", "workplace and business"
    ]
    random.shuffle(categories)
    collected = []
    history = load_pair_history()
    recent_pairs = history.get("pairs", [])[-25:]
    recent_str = ", ".join([f"{p.get('british','')}/{p.get('american','')}" for p in recent_pairs]) if recent_pairs else "(none)"

    import requests, time
    for attempt in range(max_attempts):
        try:
            cat = categories[attempt % len(categories)]
            remaining = num_pairs - len(collected)
            print(f"[api] Attempt {attempt + 1}: {cat} (need {remaining} more)")

            prompt = f"""Generate exactly 6 unique British vs American English vocabulary differences from the category: {cat}.

CRITICAL RULES:
- Terms must have DIFFERENT words on each side (British vs American)
- NEVER generate standard clichéd pairs like chips/fries, flat/apartment, lift/elevator, biscuit/cookie, boot/trunk, holiday/vacation, autumn/fall, rubbish/trash.
- Avoid recently used pairs: {recent_str}
- Terms can be 1 or 2 words (e.g. compound nouns like candy floss/cotton candy, sleeping policeman/speed bump, zebra crossing/crosswalk, kitchen roll/paper towels, drawing pin/thumbtack). Max 2 words per side.
- Both words must be widely used everyday real-world terms.
- KEEP SHORT: definition max 8 words

Return JSON array. Each item:
[{{"british":"kitchen roll","american":"paper towels","part_of_speech":"noun","definition":"absorbent paper sheets for spills","british_example":"Wipe the spill with kitchen roll.","american_example":"Grab a roll of paper towels."}}]

Return ONLY the JSON array. No explanations."""
            payload = {
                "model": AI_MODEL or "gemini-fast",
                "messages": [
                    {"role": "system", "content": "Return ONLY valid JSON arrays."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 1.0
            }

            # Support primary gen.pollinations.ai and fallback text.pollinations.ai/openai
            endpoints = []
            if POLLINATIONS_API_KEY:
                endpoints.append(("https://gen.pollinations.ai/v1/chat/completions", {"Authorization": f"Bearer {POLLINATIONS_API_KEY}", "Content-Type": "application/json"}))
            endpoints.append(("https://text.pollinations.ai/openai", {"Content-Type": "application/json"}))
            if not POLLINATIONS_API_KEY:
                endpoints.append(("https://gen.pollinations.ai/v1/chat/completions", {"Content-Type": "application/json"}))

            raw_data = None
            for url, headers in endpoints:
                try:
                    resp = requests.post(url, headers=headers, json=payload, timeout=25)
                    if resp.status_code == 200:
                        content = resp.json()["choices"][0]["message"]["content"].strip()
                        if "```json" in content:
                            content = content.split("```json")[1].split("```")[0].strip()
                        elif "```" in content:
                            content = content.split("```")[1].split("```")[0].strip()
                        raw_data = json.loads(content)
                        break
                    elif resp.status_code in (401, 402, 429):
                        continue
                except Exception:
                    continue

            if not raw_data:
                time.sleep(1)
                continue

            # Normalize data structure (handle lists, nested lists, or dicts)
            pairs = []
            if isinstance(raw_data, dict):
                for k in ["pairs", "differences", "items", "data", "vocabulary"]:
                    if k in raw_data and isinstance(raw_data[k], list):
                        raw_data = raw_data[k]
                        break
                else:
                    for val in raw_data.values():
                        if isinstance(val, list):
                            raw_data = val
                            break

            if isinstance(raw_data, list):
                for item in raw_data:
                    if isinstance(item, list):
                        pairs.extend([x for x in item if isinstance(x, dict)])
                    elif isinstance(item, dict):
                        pairs.append(item)

            fresh = []
            already_collected = {c["british"].lower().strip() for c in collected} | {c["american"].lower().strip() for c in collected}
            for p in pairs:
                b = p.get("british", "").strip()
                u = p.get("american", "").strip()
                if not b or not u:
                    continue
                if len(b.split()) > 2 or len(u.split()) > 2:
                    continue
                if b.lower() == u.lower():
                    continue
                if is_pair_used(b, u, history=history, recent_window=80):
                    continue
                if b.lower() in already_collected or u.lower() in already_collected:
                    continue
                p["category"] = cat
                fresh.append(p)
                already_collected.add(b.lower())
                already_collected.add(u.lower())
                if len(collected) + len(fresh) >= num_pairs:
                    break
            collected.extend(fresh)
            if len(collected) >= num_pairs:
                add_pairs_to_history(collected[:num_pairs])
                return collected[:num_pairs]
        except Exception as e:
            print(f"[api] Attempt {attempt + 1} notice: {e}")
            time.sleep(1)

    # 1. Fallback to curated high-quality vocabulary pool
    if len(collected) < num_pairs:
        print("[fallback] Drawing from curated high-quality vocabulary pool...")
        used_now = {c["british"].lower().strip() for c in collected} | {c["american"].lower().strip() for c in collected}
        for cp in CURATED_UNSEEN_PAIRS:
            if len(collected) >= num_pairs:
                break
            cb = cp["british"].strip()
            cu = cp["american"].strip()
            if not is_pair_used(cb, cu, history=history, recent_window=80):
                if cb.lower() not in used_now and cu.lower() not in used_now:
                    cp_copy = dict(cp)
                    collected.append(cp_copy)
                    used_now.add(cb.lower())
                    used_now.add(cu.lower())

    # 2. Safety net: Least Recently Used (LRU) fallback from historical pool (rotation)
    if len(collected) < num_pairs:
        print("[fallback] Drawing from least recently used historical pairs...")
        existing = history.get("pairs", [])
        used_now = {c["british"].lower().strip() for c in collected} | {c["american"].lower().strip() for c in collected}
        recent_set = {p.get("british", "").lower().strip() for p in existing[-80:]} | {p.get("american", "").lower().strip() for p in existing[-80:]}
        candidates = [
            p for p in existing
            if p.get("british", "").lower().strip() not in recent_set
            and p.get("american", "").lower().strip() not in recent_set
            and p.get("british", "").lower().strip() not in used_now
            and p.get("american", "").lower().strip() not in used_now
            and p.get("british", "").strip()
            and p.get("american", "").strip()
        ]
        random.shuffle(candidates)
        for cand in candidates:
            if len(collected) >= num_pairs:
                break
            b_word = cand["british"].strip()
            u_word = cand["american"].strip()
            cp = {
                "british": b_word,
                "american": u_word,
                "part_of_speech": cand.get("part_of_speech", "noun"),
                "definition": cand.get("definition", "British vs American vocabulary difference"),
                "british_example": cand.get("british_example", f"In British English, they say {b_word}."),
                "american_example": cand.get("american_example", f"In American English, they say {u_word}."),
                "category": cand.get("category", "everyday vocabulary")
            }
            collected.append(cp)
            used_now.add(b_word.lower())
            used_now.add(u_word.lower())

    # 3. Ultimate fallback: Any curated pair not currently in collected batch
    if len(collected) < num_pairs:
        used_now = {c["british"].lower().strip() for c in collected} | {c["american"].lower().strip() for c in collected}
        for cp in CURATED_UNSEEN_PAIRS:
            if len(collected) >= num_pairs:
                break
            cb = cp["british"].lower().strip()
            cu = cp["american"].lower().strip()
            if cb not in used_now and cu not in used_now:
                collected.append(dict(cp))
                used_now.add(cb)
                used_now.add(cu)

    if collected:
        add_pairs_to_history(collected[:num_pairs])
        return collected[:num_pairs]

    raise RuntimeError("API failed all attempts and no pairs available")

def create_background():
    from PIL import Image, ImageDraw
    img = Image.new('RGB', (VIDEO_WIDTH, VIDEO_HEIGHT))
    draw = ImageDraw.Draw(img)
    for y in range(VIDEO_HEIGHT):
        ratio = y / VIDEO_HEIGHT
        if ratio < 0.5:
            r, g, b = 248, 248, 252
        else:
            r = int(248 + (242 - 248) * ((ratio - 0.5) * 2))
            g = int(248 + (242 - 248) * ((ratio - 0.5) * 2))
            b = int(252 + (248 - 252) * ((ratio - 0.5) * 2))
        draw.rectangle([(0, y), (VIDEO_WIDTH, y + 1)], fill=(r, g, b))
    return img

async def gen_audio(text, voice, path):
    try:
        import edge_tts
        await edge_tts.Communicate(text, voice).save(path)
        return True
    except:
        return False

async def gen_audio_retry(text, voice, path, retries=3):
    for a in range(1, retries + 1):
        ok = await gen_audio(text, voice, path)
        if ok and Path(path).exists() and Path(path).stat().st_size > 100:
            return True
        await asyncio.sleep(2 * a)
    return False

def get_audio_duration(file):
    if not Path(file).exists():
        return 2.0
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", file], capture_output=True, text=True)
    try:
        return float(r.stdout.strip())
    except:
        return 2.0

def generate_all_audio(pairs, out_dir):
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    audio_files = []
    total = 0.0
    for i, p in enumerate(pairs):
        bf = out_dir / f"b_{i}.mp3"
        uf = out_dir / f"u_{i}.mp3"
        cf = out_dir / f"p_{i}.mp3"
        bt = f"British: {p['british']}. {p['definition']}. Example: {p.get('british_example', '')}."
        ut = f"American: {p['american']}. Example: {p.get('american_example', '')}."
        ff = p.get("fun_fact", "")
        if ff:
            bt += f" {ff}"
        asyncio.run(gen_audio_retry(bt, BRITISH_VOICE, str(bf)))
        asyncio.run(gen_audio_retry(ut, AMERICAN_VOICE, str(uf)))
        for f in [bf, uf]:
            if not (f.exists() and f.stat().st_size > 100):
                subprocess.run(["ffmpeg", "-y", "-f", "lavfi", "-i", "anullsrc=r=24000:cl=mono", "-t", "3", str(f)], capture_output=True)
        cl = out_dir / f"cl_{i}.txt"
        with open(cl, "w") as f:
            f.write(f"file '{bf.as_posix()}'\nfile '{uf.as_posix()}'\n")
        subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(cl), "-c:a", "libmp3lame", str(cf)], capture_output=True)
        if cl.exists():
            cl.unlink()
        dur = get_audio_duration(str(cf))
        audio_files.append({"file": str(cf), "duration": dur})
        total += dur + 0.3
    print(f"[audio] {len(audio_files)} pairs, {total:.1f}s")
    return audio_files, total

def create_final_audio(audio_files, out_file):
    od = Path(out_file).parent
    parts = []
    for i, af in enumerate(audio_files):
        p = od / f"pd_{i}.mp3"
        subprocess.run(["ffmpeg", "-y", "-i", str(af["file"]), "-af", "apad=pad_dur=0.3", "-ar", "24000", "-ac", "1", "-c:a", "libmp3lame", str(p)], capture_output=True)
        parts.append(p)
    cl = od / "cl.txt"
    with open(cl, "w") as f:
        for part in parts:
            f.write(f"file '{str(part.resolve()).replace(chr(92), chr(47))}'\n")
    subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(cl), "-c:a", "libmp3lame", str(out_file)], capture_output=True)
    for p in parts:
        if p.exists(): p.unlink()
    if cl.exists(): cl.unlink()
    return Path(out_file).exists() and Path(out_file).stat().st_size > 100

def wrap_text(draw, text, font, max_w):
    words = text.split()
    lines = []
    cur = []
    for w in words:
        t = ' '.join(cur + [w])
        if draw.textbbox((0, 0), t, font=font)[2] <= max_w or not cur:
            cur.append(w)
        else:
            lines.append(' '.join(cur))
            cur = [w]
    if cur:
        lines.append(' '.join(cur))
    return lines

def generate_pair_image(pair, bg_image, out_path):
    from PIL import Image, ImageDraw, ImageFont

    img = bg_image.copy().convert('RGBA')
    draw = ImageDraw.Draw(img)

    MX = 90
    CX = VIDEO_WIDTH // 2
    CW = VIDEO_WIDTH - MX * 2

    FONT_BOLD = [
        "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf","/usr/share/fonts/noto/NotoSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf","/usr/share/fonts/Liberation/LiberationSans-Bold.ttf",
        "C:/Windows/Fonts/arialbd.ttf","C:/Windows/Fonts/verdanab.ttf","C:/Windows/Fonts/segoeuib.ttf",
    ]
    FONT_REG = [
        "/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf","/usr/share/fonts/noto/NotoSans-Regular.ttf",
        "C:/Windows/Fonts/arial.ttf","C:/Windows/Fonts/verdana.ttf","C:/Windows/Fonts/segoeui.ttf",
    ]

    def lf(paths, sz):
        for p in paths:
            try:
                f = ImageFont.truetype(p, sz)
                if draw.textbbox((0, 0), "AW", font=f)[2] > sz * 0.5:
                    return f
            except:
                continue
        return ImageFont.load_default()

    f_head = lf(FONT_BOLD, 65)
    f_tag = lf(FONT_BOLD, 42)
    f_word = lf(FONT_BOLD, 80)
    f_flag = lf(FONT_BOLD, 36)
    f_vs = lf(FONT_BOLD, 44)
    f_pos = lf(FONT_BOLD, 50)
    f_dlab = lf(FONT_BOLD, 42)
    f_def = lf(FONT_REG, 60)
    f_exlab = lf(FONT_BOLD, 42)
    f_ex = lf(FONT_REG, 48)
    f_foot = lf(FONT_BOLD, 42)

    brit = pair.get("british", "").upper()
    us = pair.get("american", "").upper()
    definition = pair.get("definition", "a word difference between UK and US English")
    brit_ex = pair.get("british_example", "")
    us_ex = pair.get("american_example", "")
    pos = pair.get("part_of_speech", "")

    H = (45, 35, 65)
    W = (25, 20, 45)
    DB = (65, 50, 95)
    EB = (95, 80, 125)
    L = (80, 65, 105)

    draw.rectangle([(0, 0), (VIDEO_WIDTH, 150)], fill=H)
    draw.text((CX, 50), CHANNEL_NAME.upper(), fill=(255, 255, 255), font=f_head, anchor="mm")
    draw.text((CX, 120), "BRITISH ENGLISH  vs  AMERICAN ENGLISH", fill=(200, 195, 215), font=lf(FONT_REG, 34), anchor="mm")

    y = 340

    fl_dir = ensure_flags()
    try:
        fl_uk = Image.open(FLAGS_DIR / "uk.png").convert('RGBA').resize((48, 36), Image.LANCZOS)
    except:
        fl_uk = None
    try:
        fl_us = Image.open(FLAGS_DIR / "us.png").convert('RGBA').resize((48, 36), Image.LANCZOS)
    except:
        fl_us = None

    if fl_uk:
        img.paste(fl_uk, (CX - 90 - 24, y - 18), fl_uk)
    draw.text((CX + 40, y), "BRITISH", fill=(55, 65, 145), font=f_flag, anchor="mm")
    y += 55

    MAX_WW = CW
    wfs = 80
    wf = lf(FONT_BOLD, wfs)
    ww = draw.textbbox((0, 0), brit, font=wf)[2]
    while ww > MAX_WW and wfs > 30:
        wfs -= 5
        wf = lf(FONT_BOLD, wfs)
        ww = draw.textbbox((0, 0), brit, font=wf)[2]
    wh = draw.textbbox((0, 0), "Ay", font=wf)[3] - draw.textbbox((0, 0), "Ay", font=wf)[1]
    draw.text((CX, y + wh // 2), brit, fill=(40, 40, 100), font=wf, anchor="mm", stroke_width=2, stroke_fill=(210, 205, 220))
    y += wh + 70

    vs_y = y
    vs_b = draw.textbbox((0, 0), "VS", font=f_vs)
    vs_w = vs_b[2] - vs_b[0]
    vs_h = vs_b[3] - vs_b[1]
    draw.rounded_rectangle([(CX - vs_w // 2 - 20, vs_y - 12), (CX + vs_w // 2 + 20, vs_y + vs_h + 16)], radius=14, fill=(90, 80, 110))
    draw.text((CX, vs_y + vs_h // 2), "VS", fill=(255, 255, 255), font=f_vs, anchor="mm")
    y = vs_y + vs_h + 70

    # American label + word
    if fl_us:
        img.paste(fl_us, (CX - 90 - 24, y - 18), fl_us)
    draw.text((CX + 40, y), "AMERICAN", fill=(150, 35, 35), font=f_flag, anchor="mm")
    y += 50

    wfs2 = 80
    wf2 = lf(FONT_BOLD, wfs2)
    ww2 = draw.textbbox((0, 0), us, font=wf2)[2]
    while ww2 > MAX_WW and wfs2 > 30:
        wfs2 -= 5
        wf2 = lf(FONT_BOLD, wfs2)
        ww2 = draw.textbbox((0, 0), us, font=wf2)[2]
    wh2 = draw.textbbox((0, 0), "Ay", font=wf2)[3] - draw.textbbox((0, 0), "Ay", font=wf2)[1]
    draw.text((CX, y + wh2 // 2), us, fill=(140, 20, 20), font=wf2, anchor="mm", stroke_width=2, stroke_fill=(225, 200, 200))
    y += wh2 + 70

    # POS
    if pos:
        pb = draw.textbbox((0, 0), pos.upper(), font=f_pos)
        pw = pb[2] - pb[0]
        ph = pb[3] - pb[1]
        draw.rounded_rectangle([(CX - pw // 2 - 16, y), (CX + pw // 2 + 16, y + ph + 18)], radius=10, fill=(75, 55, 115))
        draw.text((CX, y + ph // 2 + 9), pos.upper(), fill=(255, 245, 140), font=f_pos, anchor="mm")
        y += ph + 70

    # MEANING
    draw.text((MX, y), "MEANING", fill=L, font=f_dlab, anchor="lm")
    y += 60

    dl = wrap_text(draw, definition, f_def, CW - 60)
    while len(dl) > 2 and f_def.size > 36:
        f_def = lf(FONT_REG, f_def.size - 4)
        dl = wrap_text(draw, definition, f_def, CW - 60)
    lh = draw.textbbox((0, 0), "A", font=f_def)[3] - draw.textbbox((0, 0), "A", font=f_def)[1]
    ls = int(lh * 1.5)
    th = (len(dl) - 1) * ls + lh
    pd = 40
    bh = th + pd * 2
    box = Image.new('RGBA', (CW, bh), DB + (255,))
    bd = ImageDraw.Draw(box)
    bd.rounded_rectangle([(0, 0), (CW, bh)], radius=16, fill=DB + (255,))
    for i, line in enumerate(dl):
        ly = pd + (i * ls) + (lh // 2)
        bd.text((CW // 2, ly), line, fill=(255, 255, 255), font=f_def, anchor="mm")
    img.paste(box, (MX, y), box)
    y += bh + 65

    # EXAMPLES
    if brit_ex or us_ex:
        draw.text((MX, y), "EXAMPLES", fill=L, font=f_exlab, anchor="lm")
        y += 60
        if brit_ex:
            ef = lf(FONT_REG, 42)
            el = wrap_text(draw, f"UK: {brit_ex}", ef, CW - 50)
            while len(el) > 2 and ef.size > 28:
                ef = lf(FONT_REG, ef.size - 4)
                el = wrap_text(draw, f"UK: {brit_ex}", ef, CW - 50)
            tlh = draw.textbbox((0, 0), "A", font=ef)[3] - draw.textbbox((0, 0), "A", font=ef)[1]
            tls = int(tlh * 2.0)
            tth = (len(el) - 1) * tls + tlh + 28
            ebox = Image.new('RGBA', (CW, tth), (220, 215, 230, 200))
            ed = ImageDraw.Draw(ebox)
            ed.rounded_rectangle([(0, 0), (CW, tth)], radius=12, fill=(220, 215, 230, 200))
            for i, line in enumerate(el):
                ed.text((20, 14 + (i * tls) + tlh // 2), line, fill=(40, 35, 70), font=ef, anchor="lm")
            img.paste(ebox, (MX, y), ebox)
            y += tth + 15
        if us_ex:
            ef2 = lf(FONT_REG, 42)
            el2 = wrap_text(draw, f"US: {us_ex}", ef2, CW - 50)
            while len(el2) > 2 and ef2.size > 28:
                ef2 = lf(FONT_REG, ef2.size - 4)
                el2 = wrap_text(draw, f"US: {us_ex}", ef2, CW - 50)
            tlh2 = draw.textbbox((0, 0), "A", font=ef2)[3] - draw.textbbox((0, 0), "A", font=ef2)[1]
            tls2 = int(tlh2 * 2.0)
            tth2 = (len(el2) - 1) * tls2 + tlh2 + 28
            ebox2 = Image.new('RGBA', (CW, tth2), (235, 210, 210, 200))
            ed2 = ImageDraw.Draw(ebox2)
            ed2.rounded_rectangle([(0, 0), (CW, tth2)], radius=12, fill=(235, 210, 210, 200))
            for i, line in enumerate(el2):
                ed2.text((20, 14 + (i * tls2) + tlh2 // 2), line, fill=(80, 20, 20), font=ef2, anchor="lm")
            img.paste(ebox2, (MX, y), ebox2)
            y += tth2 + 15

    draw.rectangle([(0, VIDEO_HEIGHT - 65), (VIDEO_WIDTH, VIDEO_HEIGHT)], fill=H)
    draw.text((CX, VIDEO_HEIGHT - 32), f"UK vs US Daily  |  {CHANNEL_NAME}", fill=(210, 200, 220), font=f_foot, anchor="mm")

    img = img.convert('RGB')
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    img.save(out_path, quality=96, optimize=True)
    print(f"[image] {Path(out_path).name}")
    return out_path

def create_video(image_files, audio_files, out_file):
    print(f"[video] {len(image_files)} images...")
    clips = []
    for i, (ip, ai) in enumerate(zip(image_files, audio_files)):
        tc = Path(out_file).parent / f"c_{i}.mp4"
        d = ai["duration"]
        subprocess.run(["ffmpeg", "-y", "-loop", "1", "-i", str(ip), "-i", str(ai["file"]),
            "-vf", f"scale={VIDEO_WIDTH}:{VIDEO_HEIGHT}:force_original_aspect_ratio=decrease,pad={VIDEO_WIDTH}:{VIDEO_HEIGHT}:(ow-iw)/2:(oh-ih)/2,fps={FPS}",
            "-c:v", "libx264", "-preset", "medium", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "128k",
            "-t", f"{d}", "-shortest", str(tc)], capture_output=True)
        ad = get_audio_duration(str(tc))
        print(f"  Clip {i+1}: {ad:.1f}s")
        clips.append(tc)
    if not clips:
        return False
    cf = Path(out_file).parent / "cl.txt"
    with open(cf, "w") as f:
        for c in clips:
            f.write(f"file '{str(c.resolve()).replace(chr(92), chr(47))}'\n")
    subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(cf), "-c", "copy", str(out_file)], capture_output=True)
    for c in clips:
        if c.exists(): c.unlink()
    if cf.exists(): cf.unlink()
    print(f"[video] {Path(out_file).name}")
    return True

def generate_reel():
    print(f"\n{'='*80}\n  {CHANNEL_NAME.upper()}\n{'='*80}\n")
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    rd = VIDEO_DIR / f"pairs_{ts}"
    rd.mkdir()
    print("[1/3] Generating word pairs...")
    pairs = generate_pair_data(WORDS_PER_VIDEO)
    for i, p in enumerate(pairs, 1):
        print(f"  {i}. {p['british']}  vs  {p['american']}")
    print("\n[2/3] Generating images...")
    bg = create_background()
    imgs = []
    for i, p in enumerate(pairs):
        ip = rd / f"p_{i}.jpg"
        generate_pair_image(p, bg, str(ip))
        imgs.append(str(ip))
    print("\n[3/3] Generating audio & video...")
    af, td = generate_all_audio(pairs, str(rd))
    fa = rd / "narration.mp3"
    create_final_audio(af, str(fa))
    ov = rd / "final_reel.mp4"
    create_video(imgs, af, str(ov))
    meta = {"channel": CHANNEL_NAME, "pairs": pairs, "timestamp": ts, "video": str(ov), "duration": td}
    with open(rd / "metadata.json", "w") as f:
        json.dump(meta, f, indent=2)
    print(f"\n{'='*80}\n  COMPLETE! {td:.1f}s\n{'='*80}\n")
    return meta

if __name__ == "__main__":
    print(f"\n{'='*80}\n  {CHANNEL_NAME.upper()}\n{'='*80}\n")
    generate_reel()
