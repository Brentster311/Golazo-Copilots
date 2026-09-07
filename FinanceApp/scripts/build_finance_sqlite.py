#!/usr/bin/env python3
import csv
import hashlib
import re
import sqlite3
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from statistics import mean

from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "analysis" / "finance.db"
REPORT_PATH = ROOT / "analysis" / "summary_report.md"

FIRSTTECH_CSV = ROOT / "Finances" / "FirstTech" / "ExportedTransactions.csv"
FIDELITY_CSV = ROOT / "Finances" / "fidelity" / "Credit Card - 1860_01-01-2026_06-11-2026.csv"
CHASE_DIR = ROOT / "Finances" / "chase"
PAYPAL_DIR = ROOT / "Finances" / "paypal"
AMAZON_DETAIL_DIR = ROOT / "Finances" / "amazon detail" / "Your Orders"
AMAZON_RETURN_REQUESTS = AMAZON_DETAIL_DIR / "Your Returns & Refunds" / "Return Requests.csv"
AMAZON_REFUND_DETAILS = AMAZON_DETAIL_DIR / "Your Returns & Refunds" / "Refund Details.csv"
AMAZON_REPLACEMENT_ORDERS = AMAZON_DETAIL_DIR / "Your Returns & Refunds" / "Replacement Orders.csv"
AMAZON_DIGITAL_RETURNS = AMAZON_DETAIL_DIR / "Your Amazon Orders" / "Digital Returns.csv"
AMAZON_PURCHASE_DIR = ROOT / "Finances" / "amazon detail" / "Your Amazon Orders"
AMAZON_PURCHASE_DIR_LEGACY = AMAZON_DETAIL_DIR / "Your Amazon Orders"
AMAZON_ORDER_HISTORY = AMAZON_PURCHASE_DIR / "Order History.csv"
AMAZON_DIGITAL_CONTENT_ORDERS = AMAZON_PURCHASE_DIR / "Digital Content Orders.csv"
AMAZON_ORDER_HISTORY_LEGACY = AMAZON_PURCHASE_DIR_LEGACY / "Order History.csv"
AMAZON_DIGITAL_CONTENT_ORDERS_LEGACY = AMAZON_PURCHASE_DIR_LEGACY / "Digital Content Orders.csv"


CATEGORY_RULES = [
    ("Subscriptions", ["DISNEY PLUS", "SPOTIFY", "CHATGPT", "GOOGLE ONE", "GOOGLE NEST", "DUOLINGO", "FUNIMATION", "PEACOCK", "HALLMARK PLUS", "USER PAYMENT: GOOGLE"]),
    ("Subscription Groceries", ["HELLOFRESH", "COFFEE", "SUBSCRIBE", "SAVE", "DAILY HARVEST", "HUNGRYROOT"]),
    ("Groceries", ["SAFEWAY", "ALBERTSONS", "QFC", "FRED-MEYER", "FRED MEYER", "COSTCO", "WHATNOT", "TARGET"]),
    ("Dining", ["DOORDASH", "DOMINO", "MCDONALD", "ARBYS", "HABIT BURGER", "STARBUCKS", "TYPHOON", "CAFE", "FIVE GUYS", "PIZZA HUT", "PAPA MURPHY", "PAPA JOHN", "DOUGH ZONE", "JIMMY JOHNS", "RED ROBIN", "OLIVE GARDEN", "SUMO SUSHI", "SUSHI", "FRYING FISH", "MENCHIE", "7-ELEVEN", "MARKET@92", "SIDE HUSTLE TAPROO", "THAT CHICKEN PLACE", "MOD PIZZA", "BIG SPOON EVENTS", "YOFORIT", "PANDA EXPRESS", "DAIRY QUEEN", "WENDYS", "SUBWAY", "TACO BELL", "MR GYROS", "MAMI TRAN", "J&Y MOBILE CREPERI", "DANDY DOGS", "SHOOBY DOO CATERIN", "ARTISANS PNW", "LOFT BAKESHOP", "SECRET SAUSAGE", "RIDGE COMMONS", "JUST POKE", "CM FOODHALL", "CM NE DOTE", "STANWOOD CONCESSIO", "BIG BOYS FOOD TRUC", "ITALIANO FOODTRU"]),
    ("Entertainment", ["PRIME VIDEO", "GOFANTIX", "YMCA", "STUBHUB", "FAMILY FUN CENTER", "GIRL SCOUT", "GIRLSCOUT", "LWSD ATHLETIC TICKETS", "NINTENDO"]),
    ("Transport", ["SHELL OIL", "ARCO", "CHEVRON", "GOOD TO GO", "WSDOT", "LAZ PARKING"]),
    ("Utilities", ["ZIPLY", "T-MOBILE", "TMOBILE", "PUGET SOUND ENER", "RECOLOGY", "ALDERWOOD WATER", "KING COUNTY"]),
    ("Insurance", ["USAA", "TRANSAMERICA"]),
    ("Health", ["PSYCH", "VITAMIN", "SUPPLEMENT", "PROTEIN", "PROBIOTICS", "WHEY", "CVS PHARMACY", "SPORT CLIPS"]),
    ("Education", ["NORTHSHORE SCHOOL", "NORTHSHORE SD"]),
    ("Home", ["WINDOW & GUTTER", "HOMEDEPOT", "HOME DEPOT", "CHAMBRAY PLACE"]),
    ("Fees", ["INTEREST CHARGE", "LATE FEE", "BACKGROUND CHECK"]),
    ("Cigarettes", ["SUPERIOR SMOKE", "SMOKE N CIGAR"]),
    ("Home", ["AMAZON", "WOOT"]),
    ("Shipping", ["UPS"]),
    ("Income", ["EDIPAYMENT", "ACH DEPOSIT", "DEPOSIT"]),
]


AMAZON_ITEM_CATEGORY_RULES = [
    ("Automotive", [
        "AUTOMOTIVE", "AUTO", "CAR", "TRUCK", "SUV", "MOTOR", "ENGINE", "TIRE",
        "BRAKE", "BATTERY", "DASH CAM", "DASHCAM", "OBD", "WINDSHIELD", "WIPER",
        "GARAGE", "JUMPER CABLE", "CHAIN OIL", "OIL FILTER", "CAR WASH", "FLOOR MAT",
        "SEAT COVER", "LICENSE PLATE", "AIR FRESHENER", "BIKE", "PUMP", "SPRAYMAX",
    ]),
    ("Health", [
        "VITAMIN", "SUPPLEMENT", "PROTEIN", "WHEY", "COLLAGEN", "MAGNESIUM", "OMEGA",
        "CREATINE", "MEDICINE", "THERMOMETER", "BLOOD PRESSURE", "FIRST AID", "BANDAGE",
        "DIAPER", "INCONTINENCE", "SHAMPOO", "CONDITIONER", "SOAP", "TOOTHPASTE", "DEODORANT",
        "ALKA-SELTZER", "ALKA SELTZER", "ALKA-SELZTER", "ALLERGY", "THERAFLU",
    ]),
    ("Clothing", [
        "SHIRT", "SHIRTS", "T-SHIRT", "TOPS", "TUNIC", "BLOUSE",
        "DRESS", "DRESSES", "SKIRT", "PANTS", "SHORTS", "LEGGINGS", "SWEATER",
        "CARDIGAN", "JACKET", "COAT", "HOODIE", "SLEEPWEAR", "PAJAMA", "SOCKS",
        "UNDERWEAR", "SHOES", "SNEAKERS", "BOOTS", "SANDALS", "SWIMSUIT",
    ]),
    ("Home", [
        "KITCHEN", "BEDROOM", "BATHROOM", "SHELF", "ORGANIZER", "STORAGE", "RACK", "DESK",
        "TABLE", "CHAIR", "CURTAIN", "PILLOW", "MATTRESS", "BLANKET", "TOWEL", "LAMP",
        "VACUUM", "MOP", "BROOM", "TRASH", "CLEANER", "DETERGENT", "DISH", "LAUNDRY",
        "PAPER TOWEL", "TOILET PAPER", "PLATES", "CUTLERY", "COOKWARE", "BAKING", "GARDEN",
        "OFFICE", "HANGERS", "WALL", "HAMMER", "TOOL", "DRILL", "SCREW", "POOL",
        "OUTDOOR", "LITTER", "MULTI-CAT", "CLUMP", "ODOR", "SEWING KIT", "SEWING", "GOO GONE",
    ]),
    ("Groceries", [
        "SNACK", "COFFEE", "TEA", "CHOCOLATE", "CANDY", "PROTEIN BAR", "ENERGY DRINK",
        "BOTTLED WATER", "SPARKLING WATER", "SODA", "JUICE", "FOOD", "SAUCE", "SPICE", "SEASONING", "PASTA",
        "RICE", "CEREAL", "OATMEAL", "NUTS", "JERKY", "PET FOOD", "CAT FOOD", "DOG FOOD",
    ]),
    ("Entertainment", [
        "LEGO", "NINTENDO", "PLAYSTATION", "XBOX", "GAME", "PUZZLE", "BOARD GAME", "TOY",
        "BOOK", "KINDLE", "AUDIOBOOK", "DVD", "BLU-RAY", "STREAMING", "DUNE",
    ]),
    ("Transport", [
        "MOTOR OIL", "CAR WASH", "TIRE", "AUTO", "AUTOMOTIVE", "WINDSHIELD", "WIPER",
        "CAR COVER", "DASH CAM", "OBD", "GARAGE", "JUMPER CABLE", "BRAKE", "CHAIN OIL",
    ]),
    ("Subscriptions", [
        "AUDIBLE", "SUBSCRIPTION", "MEMBERSHIP", "PRIME VIDEO", "KINDLE UNLIMITED",
    ]),
]


AMAZON_ITEM_OVERRIDE_RULES = [
    # Add internet-verified, one-by-one mappings here as (title clue, category).
    # These rules run before generic keyword rules.
    ("VISA GIFT CARD", "Transfers"),
    ("VISA $200 GIFT CARD", "Transfers"),
    ("VISA $100 GIFT CARD", "Transfers"),
    ("VISA $50 GIFT CARD", "Transfers"),
    ("$100 VISA® GIFT CARD (PLUS $5.95 PURCHASE FEE)", "Transfers"),
    ("$50 VISA® GIFT CARD (PLUS $4.95 PURCHASE FEE)", "Transfers"),
    ("MASTERCARD GIFT CARD", "Transfers"),
    ("MASTERCARD $200 GIFT CARD", "Transfers"),
    ("AMAZON RELOAD", "Transfers"),
    ("GOOGLE PLAY GIFT CODE", "Transfers"),
    ("AMAZON.COM $10 GIFT CARD IN A GREETING CARD", "Transfers"),
    ("AMAZON.COM $25 GIFT CARD", "Transfers"),
    ("AMAZON.COM $100 GIFT CARD", "Transfers"),
    ("AMAZON PHYSICAL GIFT CARD", "Transfers"),
    ("AMAZON EGIFT CARD", "Transfers"),
    ("AMAZON.COM GIFT CARD BALANCE RELOAD", "Transfers"),
    ("AMAZON.COM GIFT CARD IN A FLOWER POT REVEAL", "Transfers"),
    ("UBER GIFT CARD", "Transport"),

    ("STRENGTHS BASED LEADERSHIP", "Education"),
    ("STRENGTHS-BASED LEADERSHIP HANDBOOK", "Education"),
    ("SMARTGUARD 4-YEAR LAPTOP ACCIDENTAL PROTECTION PLAN", "Insurance"),
    ("HANDBOOK OF STATISTICAL DISTRIBUTIONS WITH APPLICATIONS", "Education"),
    ("BETTY CROCKER COOKBOOK: EVERYTHING YOU NEED TO KNOW TO COOK TODAY", "Education"),
    ("JOSEY BAKER BREAD: GET BAKING", "Education"),
    ("DANISH COOKING AND BAKING TRADITIONS", "Education"),
    ("SMITHSONIAN HANDBOOKS: ROCKS & MINERALS", "Education"),
    ("CODING FOR KIDS: PYTHON: LEARN TO CODE WITH 50 AWESOME GAMES AND ACTIVITIES", "Education"),
    ("FABER PIANO ADVENTURES PRIMER LEVEL LEARNING LIBRARY PACK", "Education"),
    ("FABER PIANO ADVENTURES LEVEL 1 LEARNING LIBRARY PACK", "Education"),
    ("THE ART OF FAILURE: AN ESSAY ON THE PAIN OF PLAYING VIDEO GAMES", "Education"),
    ("THE HUNGER GAMES", "Education"),
    ("STRATEGIES AND GAMES: THEORY AND PRACTICE", "Education"),
    ("STRENGTHSFINDER 2.0", "Education"),
    ("INTRODUCTION TO DATA MINING", "Education"),
    ("BUSINESS PROCESS MODELING, SIMULATION AND DESIGN", "Education"),
    ("[OLD VERSION] TURBOTAX DELUXE 2020 DESKTOP TAX SOFTWARE", "Education"),
    ("TEXAS INSTRUMENTS TI84", "Education"),
    ("SPLASH: THE ART OF THE SWIMMING POOL", "Education"),
    ("PRACTICAL SPREADSHEET RISK MODELING FOR MANAGEMENT", "Education"),
    ("TURBOTAX 2017 DELUXE FEDERAL TAX SOFTWARE CD", "Education"),

    ("SPERTI FIJI SUN HOME TANNING LAMP", "Health"),
    ("FOLDING TREADMILL", "Health"),
    ("SPEEDIANCE GYM MONSTER", "Health"),
    ("ROWING MACHINES FOR HOME USE", "Health"),
    ("ELLIPTICAL MINI STEPPER TRAINER", "Health"),
    ("23ANDME ANCESTRY + TRAITS SERVICE", "Health"),
    ("SOURCE NATURALS L-TRYPTOPHAN", "Health"),
    ("DERMAHEALER UVB LIGHT THERAPY", "Health"),
    ("PROACTIV 3 STEP ACNE TREATMENT", "Health"),
    ("GALAXY WATCH 4 CLASSIC", "Health"),
    ("LOVE YOUR TEETH WHITENING DEVICE KIT", "Health"),
    ("AQUA-MYCIN 250MG ERYTHROMYCIN ANTIBIOTIC", "Health"),
    ("NATURE'S BOUNTY MELATONIN", "Health"),
    ("NATURES BOUNTY MELATONIN", "Health"),
    ("NATURE MADE MELATONIN", "Health"),
    ("NUTRISYSTEM® 14 DAY EVERYDAY KIT", "Health"),
    ("SUNNY HEALTH & FITNESS FULLY ASSEMBLED MAGNETIC UNDER DESK ELLIPTICAL PEDDLER", "Health"),
    ("PREMIUM LARGE YOGA MAT", "Health"),
    ("ZYPPAH - STOP SNORING HYBRID ORAL APPLIANCE", "Health"),
    ("PORTABLE STEAM SAUNA SPA", "Health"),
    ("IHEALTH COVID-19 ANTIGEN RAPID TEST", "Health"),
    ("POWER GUIDANCE BATTLE ROPE", "Health"),
    ("OPI PROSPA NAIL & CUTICLE OIL", "Health"),
    ("FACIAL MOISTURIZING LOTION SPF 30 BY OLAY TOTAL EFFECTS", "Health"),
    ("OLAY TOTAL EFFECTS WHIP LIGHT FACE MOISTURIZER CREAM SPF 25", "Health"),
    ("OLAY TOTAL WHIP, 1.7 OZ", "Health"),
    ("DARK SPOT CORRECTOR BY OLAY", "Health"),
    ("GREENWICH BAY ROSEWATER JASMINE, FOAMING MILK BATH", "Health"),
    ("SALONITURE PROFESSIONAL PORTABLE FOLDING MASSAGE TABLE", "Health"),
    ("XMARK COMMERCIAL RATED HEAVY BAG WALL MOUNT", "Health"),
    ("BIKE", "Health"),
    ("BICYCLE", "Health"),
    ("BIKE HELMET", "Health"),
    ("BOAT", "Health"),

    ("BAKING SODA (1 GALLON)", "Groceries"),
    ("EARTHBORN ELEMENTS BAKING SODA", "Groceries"),
    ("TOILET PAPER", "Groceries"),
    ("PAPER TOWEL", "Groceries"),
    ("KEURIG SINGLE-SERVE K-CUP PODS", "Groceries"),
    ("CLOROX ULTRA CLEAN TOILET TABLETS BLEACH", "Groceries"),

    ("AQUARIUM", "Home"),
    ("FISH TANK", "Home"),
    ("AQUATICS", "Home"),
    ("FISH FEEDER", "Home"),
    ("AQUARIUM WATER CONDITIONER", "Home"),

    ("CRICUT EXPLORE AIR 2", "Entertainment"),
    ("HP 15-INCH FHD LAPTOP", "Entertainment"),
    ("SAMSUNG GALAXY S20 FE 5G", "Entertainment"),
    ("MAGIC: THE GATHERING", "Entertainment"),
    ("VIEWSONIC", "Entertainment"),
    ("DAS KEYBOARD", "Entertainment"),
    ("RAZER HEROIC BUNDLE", "Entertainment"),
    ("RAZER BLACKWIDOW", "Entertainment"),
    ("LEGO ICONS TRANQUIL GARDEN", "Entertainment"),
    ("LEGO BOTANICALS JAPANESE RED MAPLE BONSAI TREE BUILDING KIT", "Entertainment"),
    ("KIDS ART SET | 27-PIECE ACRYLIC PAINT SET", "Entertainment"),
    ("POLYMER CLAY, DEECOO 70 COLORS", "Entertainment"),
    ("SCULPTING TOOLS- 11 DOUBLE-SIDED PIECES WITH 21 TOOLS", "Entertainment"),
    ("WII SPORTS CLUB - WII U", "Entertainment"),
    ("MIGHTY VIBE SPOTIFY AND AMAZON MUSIC PLAYER", "Entertainment"),
    ("CREATIVE LABS RHOMBA 128 MB MP3/WMA PLAYER", "Entertainment"),
    ("MP3 PLAYER 8GB BLUETOOTH KLANTOP DIGITAL CLIP MUSIC PLAYER", "Entertainment"),
    ("SOUNDCORE BY ANKER Q20I HYBRID ACTIVE NOISE CANCELLING HEADPHONES", "Entertainment"),
    ("EA SPORTS ACTIVE 2", "Entertainment"),
    ("TICKET TO RIDE - PLAY WITH ALEXA", "Entertainment"),
    ("GOSPORTS SHUFFLEBOARD AND CURLING 2 IN 1 TABLE TOP BOARD GAME", "Entertainment"),
    ("SKLZ HIT-A-WAY PORTABLE BASEBALL TRAINER", "Entertainment"),
    ("GORICH [2019 NEW BEACH TENT", "Entertainment"),
    ("ALVANTOR WINTER SCREEN HOUSE ROOM CAMPING TENT CANOPY GAZEBOS", "Entertainment"),
    ("BACK BAY PLAY KID'S PREMIUM SAND AND WATER CONVERTIBLE PICNIC TABLE", "Entertainment"),
    ("MICHIGAN PEAT 2750 LEISURE TIME PLAY SAND", "Entertainment"),
    ("COSCO FUNSPORT PLAY YARD", "Entertainment"),
    ("PRINCESS CASTLE PLAY TENT HOUSE FOR GIRLS", "Entertainment"),
    ("HEXAGON RUG PAD MAT  FOR KIDS PLAYHOUSE PLAY TENT", "Entertainment"),
    ("VR HEADSET FOR IPHONE & ANDROID PHONE - UNIVERSAL VIRTUAL REALITY GOGGLES", "Entertainment"),
    ("HC GAMERLIFE XBOX1 NO SWEAT CLOSE THUMB STICK GRIPS", "Entertainment"),
    ("HASBRO GAMES TRIVIAL PURSUIT FAMILY EDITION", "Entertainment"),
    ("CZECH GAMES PICTOMANIA", "Entertainment"),
    ("YORKSGAMEPIECES PINK WOOD REPLACEMENT PIECES FOR SETTLERS OF CATAN", "Entertainment"),
    ("YORKSGAMEPIECES PURPLE WOOD REPLACEMENT PIECES FOR SETTLERS OF CATAN", "Entertainment"),
    ("BOCCE BALL SET- OUTDOOR FAMILY BOCCE GAME", "Entertainment"),
    ("TABLE TOP TENNIS GAME SET, GLOW IN THE DARK", "Entertainment"),
    ("INTEX POOL VOLLEYBALL GAME", "Entertainment"),
    ("INTEX METAL FRAME POOL SET", "Entertainment"),
    ("BESTWAY 56498 DELUXE SPLASH", "Entertainment"),
    ("KIDKRAFT BACKYARD SANDBOX", "Entertainment"),
    ("RAWLINGS CS10-14 YOUNG ADULT CATCHER'S GEAR SET", "Entertainment"),
    ("MOVTOTOP INDOOR TRAMPOLINE", "Entertainment"),
    ("14' ROUND DELUXE BLUE TRAMPOLINE SAFETY PAD", "Entertainment"),

    ("UBER EATS GIFT CARD $50", "Dining"),
    ("DANIEL'S BROILER GIFT CARD - $100", "Dining"),
    ("RUTH'S CHRIS STEAK HOUSE $100 GIFT CARD", "Dining"),
    ("PANERA BREAD GIFT CARDS, MULTIPACK OF 3 - $10", "Dining"),
    ("PANERA BREAD HOLIDAY GIFT CARD $25", "Dining"),
    ("OMAHA STEAKS GIFT CARD $25", "Dining"),

    ("AMC THEATRE GIFT CARD $25", "Entertainment"),
    ("FANDANGO GIFT CARD $25", "Entertainment"),
    ("MICHAELS GIFT CARD $25 TO $500", "Entertainment"),

    ("NEST LEARNING THERMOSTAT", "Utilities"),
    ("GAME 72000-BB", "Utilities"),
    ("RAIN BIRD 32HE", "Utilities"),
    ("TP-LINK TRI-BAND BE9300 WIFI 7 ROUTER", "Utilities"),
    ("16 PORT 2.5G", "Utilities"),
    ("MOKERLINK 5 PORT 2.5 GIGABIT POE SWITCH", "Utilities"),
    ("TP-LINK 16 PORT GIGABIT ETHERNET NETWORK SWITCH", "Utilities"),
    ("TP-LINK TL-SG108", "Utilities"),
    ("LINKSYS AC1900 GIGABIT RANGE EXTENDER", "Utilities"),
    ("PHILIPS HUE SINGLE PREMIUM SMART BULB DOWNLIGHT", "Utilities"),

    ("TONER CARTRIDGE REPLACEMENT FOR HP 206A 206X", "Utilities"),
    ("206X 206A TONER CARTRIDGES 4 PACK HIGH YIELD", "Utilities"),
    ("VALUETONER REMANUFACTURED INK CARTRIDGE", "Utilities"),
    ("TIMINK 950XL 951XL INK CARTRIDGES", "Utilities"),
    ("HAMMERMILL PRINTER PAPER", "Utilities"),

    ("SAMSONITE COLOMBIAN LEATHER FLAP-OVER MESSENGER BAG", "Clothing"),
    ("EDDIE BAUER MEN'S MAINSTAY 2.0 INSULATED TRENCH", "Clothing"),
    ("ISOTONER MEN'S OPEN BACK SLIPPER", "Clothing"),
    ("ISOTONER WOMENS SATIN BALLERINA SLIPPERS", "Clothing"),
    ("COMFORTVIEW WOMEN'S WIDE WIDTH THE MILAN WIDE CALF BOOT", "Clothing"),
    ("COMFORTVIEW WOMEN'S WIDE WIDTH THE ORLY SANDAL", "Clothing"),
    ("SOLO NEW YORK LUDLOW UNIVERSAL TABLET SLING BAG", "Clothing"),
    ("WOMAN'S SUNGLASSES TWO CHIC FANCY LADY SUNNIES", "Clothing"),
    ("SKECHERS SPORT WOMEN'S AIR STREAMER SLIP-ON MULE", "Clothing"),
    ("SALIA GIRL GIRLS TRANING BRA SOILD COTTON WIREFREE SPORTS BRA", "Clothing"),
    ("WATCHBAND FOR XIAOMI MI BAND", "Clothing"),
    ("BROOKS ADRENALINE GTS 21", "Clothing"),
    ("WOMENS LIGHTWEIGHT WARM WINTER PUFFER DOWN JACKETS", "Clothing"),
    ("UGG MEN'S ASCOT SLIPPER", "Clothing"),
    ("SKECHERS USA MEN'S EXPECTED AVILLO RELAXED-FIT SLIP-ON LOAFER", "Clothing"),
    ("ADIDAS ADIZERO AFTERBURNER 3 E CLEAT", "Clothing"),
    ("EDDIE BAUER WOMEN'S CIRRUSLITE 2.0 DOWN PARKA", "Clothing"),
    ("VINTAGE FOUNDRY CO. WOMEN'S LOUISA SLIDE SLIP-ON WOVEN HEELED SANDAL", "Clothing"),
    ("AMAZONBASICS PREMIUM HARDSIDE SPINNER LUGGAGE", "Clothing"),
    ("LAPTOP TRAVEL BACKPACK, LARGE CAPACITY COMPUTER BACK PACK", "Clothing"),
    ("COLLEGE BACKPACK, EXTRA LARGE BACKPACKS WITH USB CHARGING PORT", "Clothing"),
    ("YOREPEK 18.4 LAPTOP LARGE BACKPACKS", "Clothing"),
    ("YOREPEK TRAVEL BACKPACK, EXTRA LARGE 50L LAPTOP BACKPACKS", "Clothing"),
    ("MENS MESSENGER BAG 15.6 INCH WATERPROOF VINTAGE GENUINE LEATHER", "Clothing"),
    ("RAINSMORE MENS MESSENGER BAG 17 INCH", "Clothing"),
    ("TANTO TRAVEL BAGS FOR WOMEN WEEKENDER BAG", "Clothing"),
    ("AQUA CIRCLE LINK REINFORCED AND WATER RESISTANT PADDED LAPTOP SCHOOL BACKPACK", "Clothing"),
    ("NUOKU WOMEN SMALL CROSSBODY BAG CELLPHONE PURSE WALLET", "Clothing"),
    ("S-ZONE PU LEATHER RFID BLOCKING CROSSBODY CELL PHONE BAG", "Clothing"),
    ("S-ZONE PU LEATHER RFID BLOCKING CROSSBODY PHONE BAG", "Clothing"),
    ("MANGOTREE LARGE BEACH TOTE BAG", "Clothing"),
    ("SLIM RUNNING BELT FANNY PACK", "Clothing"),
    ("WATERFLY SLIM SOFT POLYESTER WATER RESISTANT WAIST BAG PACK", "Clothing"),
    ("AIKELIDA RUNNING BELT / FANNY PACK / FITNESS BELT", "Clothing"),
    ("REEHUT RUNNING BELT WAIST PACK", "Clothing"),
    ("HOLYLUCK RUNNING WAIST PACK", "Clothing"),
    ("CICY BELL WOMENS CASUAL JACKETS OPEN FRONT LONG SLEEVE", "Clothing"),

    ("FOR SUBARU LEGACY CLEAR CHROME HEADLIGHTS", "Automotive"),

    ("PANASONIC MINIDV CAMCORDER BUNDLE", "Entertainment"),
    ("INTEX EXCURSION 5 PERSON INFLATABLE BOAT", "Entertainment"),
    ("SAMSUNG GALAXY TAB A9+", "Entertainment"),
    ("FENDER SQUIER DEBUT SERIES STRATOCASTER ELECTRIC GUITAR", "Entertainment"),
    ("HAUPPAUGE WINTV-PVR 250", "Entertainment"),
    ("BOSEBUILD SPEAKER CUBE", "Entertainment"),
    ("POWERNET DLX PRO BUNDLE", "Entertainment"),
    ("KIDS HEADPHONES, HD30 VOLUME LIMITING KIDS HEADSET", "Entertainment"),
    ("FUJIFILM INSTAX MINI 9 CAMERA", "Entertainment"),
    ("DIGITAL CAMERA, LECRAN FHD 1080P", "Entertainment"),
    ("MINI DIGITAL CAMERA, 1080P 20MP HD VIDEO CAMERA", "Entertainment"),
    ("BESTISAN BLUETOOTH BOOKSHELF SPEAKERS", "Entertainment"),
    ("CLEARSTREAM MAX-V INDOOR OUTDOOR TV ANTENNA", "Entertainment"),
    ("THERMALTAKE V200 TEMPERED GLASS RGB EDITION", "Entertainment"),
    ("CORSAIR HYDRO SERIES H60", "Entertainment"),
    ("SHURE WH20XLR DYNAMIC HEADSET MICROPHONE", "Entertainment"),
    ("BEST NOISE CANCELLING IN-EAR HEADPHONES", "Entertainment"),
    ("REFERENCE S4I PREMIUM IN-EAR NOISE-ISOLATING HEADPHONES", "Entertainment"),
    ("ONEODIO WIRED OVER EAR HEADPHONES", "Entertainment"),
    ("MONSTER BEATS BY DR DRE IBEATS IN EAR HEADPHONES", "Entertainment"),
    ("SADES SA902 GAMING HEADSET", "Entertainment"),
    ("AILIHEN C8 HEADPHONES WITH MICROPHONE", "Entertainment"),
    ("AILIHEN C8 GIRLS HEADPHONES", "Entertainment"),
    ("LORELEI X6 OVER-EAR HEADPHONES", "Entertainment"),
    ("TOZO A1 MINI WIRELESS EARBUDS", "Entertainment"),
    ("ONEODIO KIDS SAFE HEADPHONES", "Entertainment"),
    ("2 PACK JOWAY STEREO EARPHONES/EARBUDS/HEADPHONES", "Entertainment"),
    ("MUVEACOUSTICS DRIVE WIRED IN-EAR EARBUD HEADPHONES", "Entertainment"),
    ("BLUETOOTH BEANIE HAT HEADPHONES", "Entertainment"),
    ("CREATIVE PEBBLE 2.0 USB-POWERED DESKTOP SPEAKERS", "Entertainment"),
    ("VICTSING SHOWER SPEAKER", "Entertainment"),
    ("TBS®2510 A2DP BLUETOOTH 2.1 + EDR WIRELESS PORTABLE SPEAKER", "Entertainment"),
    ("NEWEST 62\" PHONE TRIPOD", "Entertainment"),
    ("CARRYING & PROTECTIVE CASE FOR DIGITAL CAMERA", "Entertainment"),
    ("PROFESSIONAL HEADPHONE REPLACEMENT EAR PADS FOR BOSE QUIETCOMFORT", "Entertainment"),
    ("OFC REPLACEMENT INLINE REMOTE AND MIC EXTENSION AUDIO CABLE CORD FOR MONSTER BEATS", "Entertainment"),
    ("ARTIX HEADPHONES WITH MICROPHONE", "Entertainment"),
    ("PARTS EXPRESS MINI STEREO LIGHTWEIGHT HEADPHONES", "Entertainment"),
    ("AQUARIUS BEETLEJUICE PLAYING CARDS", "Entertainment"),
    ("2 PACK OUTDOOR BLUETOOTH SPEAKERS, PORTABLE LED FLAME SPEAKER", "Entertainment"),
    ("ARTRESIN - EPOXY RESIN - CLEAR - NON-TOXIC", "Entertainment"),

    ("350W SPACE HEATER, WALL OUTLET ELECTRIC SPACE HEATER", "Utilities"),
    ("HUNTER 59222 SYMPHONY CEILING FAN", "Utilities"),
    ("HOLMES 4 IN 1 STAND FAN", "Utilities"),
    ("BEST COMFORT 20\" BOX FAN", "Utilities"),
    ("FANTASEA PORTABLE TOWEL STEAMER FSC-87", "Utilities"),
    ("PHILIPS HUE PLAY WHITE & COLOR SMART LIGHT", "Utilities"),
    ("SANDISK 1TB EXTREME PRO PORTABLE SSD - UP TO 2000MB/S", "Utilities"),
    ("7-PORT USB 3.0 HUB, IVETTO DATA USB HUB SPLITTER", "Utilities"),
    ("KENSINGTON MAGPRO ELITE MAGNETIC PRIVACY SCREEN FOR SURFACE LAPTOP STUDIO", "Utilities"),
    ("LENOVO ACTIVE CAPACITY PENS FOR TOUCHSCREEN LAPTOP", "Utilities"),
    ("GOOGLE, T5001SF, NEST TEMPERATURE SENSOR", "Utilities"),
    ("PHILIPS HUE WHITE AND COLOR AMBIANCE LED SMART LIGHT BULB STARTER KIT", "Utilities"),
    ("IMBZBK [3+3 PACK] UV FOR SAMSUNG GALAXY S23 ULTRA PRIVACY SCREEN PROTECTOR", "Utilities"),
    ("IMBZBK [3+3 PACK UV FOR SAMSUNG GALAXY S23 ULTRA PRIVACY SCREEN PROTECTOR", "Utilities"),
    ("BUTAIGA FOR SAMSUNG GALAXY S25 ULTRA CASE WITH STAND", "Utilities"),
    ("HOLICFUN 360° ADJUSTABLE INDOOR/OUTDOOR SECURITY CAMERA WALL MOUNT", "Utilities"),
    ("LONG RANGE USB BLUETOOTH 5.3 ADAPTER FOR DESKTOP PC", "Utilities"),
    ("65W 45W CHARGER FIT FOR LENOVO IDEAPAD FLEX", "Utilities"),
    ("COWOOGMZ 65W USB C LAPTOP CHARGER", "Utilities"),
    ("MOSISO LAPTOP SLEEVE", "Utilities"),
    ("100W USB C UNIVERSAL LAPTOP CHARGER", "Utilities"),
    ("SR MINI KEYBOARD WIRED THIN LIGHT 78 KEYS USB MULTIMEDIA", "Utilities"),
    ("EDUP USB WIFI 6 ADAPTER AX600M FOR PC", "Utilities"),
    ("5V 2A AC ADAPTER, SOULBAY 10WATT", "Utilities"),
    ("USB FAST CHARGER, MULTI-PORT 100W-6 PORT USB FAST CHARGING STATION", "Utilities"),
    ("FAST WIRELESS CHARGER,NANAMI QI CERTIFIED WIRELESS CHARGING STAND", "Utilities"),
    ("INKOTIMES CHARGING STATION WITH 5-PORT USB CHARGER", "Utilities"),
    ("SUPER FAST CHARGER 25 WATT PD 3.0 USB C TYPE C CHARGER CABLE", "Utilities"),
    ("MULTIPLE USB CHARGER, OVERTIME 3.1A 3-PORT DESKTOP CHARGER", "Utilities"),
    ("NTONPOWER 4-OUTLET ELECTRICAL SURGE PROTECTOR", "Utilities"),
    ("BESTTEN USB OUTLET SURGE PROTECTOR", "Utilities"),
    ("BESTTEN MULTI OUTLET WALL MOUNT ADAPTER SURGE PROTECTOR", "Utilities"),
    ("INIU WIRELESS CHARGER, 15W FAST QI-CERTIFIED WIRELESS CHARGING STATION", "Utilities"),
    ("SOKE GALAXY TAB S6 LITE 10.4 CASE", "Utilities"),
    ("SHELLBOX COMPATIBLE FOR SAMSUNG GALAXY NOTE 9 WATERPROOF CASE", "Utilities"),
    ("ENCASED MAGNETIC CASE AND GRIP - DESIGNED FOR SAMSUNG GALAXY S23 ULTRA", "Utilities"),
    ("ANNGELAS MAGNETIC PHONE CASE COMPATIBLE WITH SAMSUNG GALAXY S23 ULTRA", "Utilities"),
    ("AMUVEC MULTI USB CHARGING CABLE 3A, 4 IN1 FAST CHARGER CORD", "Utilities"),
    ("SOLIOM BF08- SMART BIRD FEEDER CAMERA", "Utilities"),

    ("TRAVELPRO LUGGAGE MAXLITE 5", "Clothing"),
    ("NIKE $100 GIFT CARD", "Clothing"),

    ("TORCHBEAM T2 H13/9008 LED BULBS KIT", "Automotive"),

    ("PRESTO! 2-PLY ULTRA-SOFT TOILET PAPER", "Groceries"),
    ("PRESTO! 308-SHEET MEGA ROLL TOILET PAPER", "Groceries"),
    ("BOUNTY QUICK-SIZE PAPER TOWELS", "Groceries"),
    ("BRAWNY", "Groceries"),
    ("BRAWNY TEAR-A-SQUARE PAPER TOWELS", "Groceries"),

    ("TIDY CATS", "Groceries"),
    ("CLUMP & SEAL", "Groceries"),

    ("NOT APPLICABLE", "Unclassified"),
]


@dataclass
class Txn:
    source_institution: str
    source_account: str
    source_file: str
    source_transaction_id: str
    txn_date: str
    posted_date: str
    effective_date: str
    amount: float
    direction: str
    currency: str
    raw_merchant: str
    normalized_merchant: str
    raw_description: str
    memo: str
    reference_id: str
    account_type: str
    provider_category: str
    normalized_category: str
    is_transfer: int
    transfer_group_id: str


def parse_date(value: str):
    value = (value or "").strip()
    if not value:
        return None
    for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%m/%d/%y"):
        try:
            return datetime.strptime(value, fmt).date().isoformat()
        except ValueError:
            pass
    return None


def parse_date_with_year_fallback(mmdd: str, open_date: str, close_date: str):
    if not mmdd:
        return None

    try:
        month, day = [int(x) for x in mmdd.split("/")]
    except ValueError:
        return None

    open_dt = parse_date(open_date)
    close_dt = parse_date(close_date)
    if not open_dt or not close_dt:
        return None

    open_obj = datetime.strptime(open_dt, "%Y-%m-%d")
    close_obj = datetime.strptime(close_dt, "%Y-%m-%d")

    year = close_obj.year
    if open_obj.year != close_obj.year:
        year = open_obj.year if month >= open_obj.month else close_obj.year

    try:
        return datetime(year, month, day).date().isoformat()
    except ValueError:
        return None


def norm_merchant(text: str):
    text = (text or "").upper().strip()
    text = re.sub(r"\s+", " ", text)
    text = text.replace("PAYPAL *", "")
    text = text.replace("AMAZON RETA*", "AMAZON")
    text = text.replace("AMAZON MKTPL*", "AMAZON")
    text = text.replace("AMAZON MKTPLACE PMTS", "AMAZON")
    text = text.replace("PRIME VIDEO *", "PRIME VIDEO ")

    prefixes = [
        "POS TRANSACTION: ",
        "ACH DEBIT: ",
        "ACH DEPOSIT: ",
        "DEPOSIT: ",
        "WITHDRAWAL: ",
        "CHECK: ",
    ]
    for p in prefixes:
        if text.startswith(p):
            text = text[len(p):]
            break

    text = re.split(r"\s{2,}|\s-\s", text)[0].strip()
    return text


def conservative_category(provider_category: str, raw: str, merchant: str, amount: float):
    probe = f"{merchant} {raw}".upper()

    if "PAYMENT THANK YOU" in probe or "PAYMENT MADE BY ACCOUNT ENDING IN" in probe:
        return "Transfers"

    if "MONEYLINE" in probe:
        return "Transfers"

    # Recology payments are utility bills.
    if "RECOLOGY" in probe:
        return "Utilities"

    # Puget Sound Energy payments are utility bills.
    if "PUGET SOUND ENER" in probe:
        return "Utilities"

    # Utility billers that may come through ACH bill-pay descriptors.
    if "ALDERWOOD WATER" in probe or "KING COUNTY WA" in probe:
        return "Utilities"

    # QFC is a grocery store even when provider categories are noisy.
    if "QFC" in probe:
        return "Groceries"

    # Employer ACH deposits from Microsoft are income.
    if "ACH DEPOSIT" in probe and "MICROSOFT" in probe:
        return "Income"

    # Snohomish County: the large annual charge is property tax; the rest are utilities.
    if "SNOHOMISH COUNTY" in probe:
        if abs(amount) >= 6000:
            return "Property Tax"
        return "Utilities"

    # Bill-pay withdrawals and check/ATM cash movements are transfers.
    if "ACH DEBIT" in probe and "BILL PAYMT" in probe:
        return "Transfers"
    if "US BANK/ELAN FIN" in probe:
        return "Transfers"
    if "ATM WITHDRAWAL" in probe or "CHECK #" in probe:
        return "Transfers"

    # Force known subscription meal service to avoid provider-side FOOD/SHOP reclassification.
    if "HELLOFRESH" in probe:
        return "Subscription Groceries"

    # Keep Disney Plus in subscriptions even if source provider category is noisy.
    if "DISNEY PLUS" in probe:
        return "Subscriptions"

    # Fuel purchases at Costco should be transport, not groceries.
    if "COSTCO GAS" in probe:
        return "Transport"

    # Small Shell Oil purchases are treated as cigarette purchases.
    if "SHELL OIL" in probe and abs(amount) <= 30:
        return "Cigarettes"

    # Medical provider charges should be categorized as Health.
    if "PACIFIC MEDICAL" in probe:
        return "Health"

    # YMCA mock trial and GOFANTIX should be treated as entertainment activities.
    if "YMCA" in probe or "GOFANTIX" in probe:
        return "Entertainment"

    # Doordash food delivery should be Dining even if provider category is Shopping.
    if "DOORDASH" in probe:
        return "Dining"

    # Microsoft subscriptions should be Dining, not Shopping.
    if "MICROSOFT" in probe:
        return "Dining"

    # Card bill payments should always be Transfers.
    if "ACH DEBIT CHASE MC & VISA" in probe:
        return "Transfers"

    # Streaming/security/membership/app charges should be Subscriptions.
    if "SPOTIFY" in probe or "AMAZON PRIME" in probe or "NORTON" in probe or "AARP" in probe:
        return "Subscriptions"

    # Android app purchases from Google should be subscriptions.
    if "GOOGLE GLORITY" in probe or "GOOGLE GEOCACHING" in probe:
        return "Subscriptions"

    # Costco warehouse purchases are groceries.
    if "COSTCO WHSE" in probe:
        return "Groceries"

    pcat = (provider_category or "").strip()
    if pcat:
        pcat_upper = pcat.upper()
        if "FOOD" in pcat_upper:
            return "Dining"
        if "HOME" in pcat_upper:
            return "Home"
        if "AUTO" in pcat_upper:
            return "Transport"
        if "ENTERTAIN" in pcat_upper:
            return "Entertainment"
        if "HEALTH" in pcat_upper:
            return "Health"
        if "SHOP" in pcat_upper:
            return "Home"
        if "BILLS" in pcat_upper or "UTIL" in pcat_upper:
            return "Utilities"
        if "TRANSFER" in pcat_upper:
            return "Transfers"

    for cat, keys in CATEGORY_RULES:
        for key in keys:
            if key in probe:
                return cat

    if amount > 0:
        return "Income"
    return "Unclassified"


def categorize_amazon_item(product_name: str, amount: float):
    probe = (product_name or "").upper()
    probe_tokens = set(re.findall(r"[A-Z0-9]+", probe))

    for clue, category in AMAZON_ITEM_OVERRIDE_RULES:
        if clue.upper() in probe:
            return "Home" if category == "Utilities" else category

    # Keep explicit medicine/allergy items in Health before broad home keyword matches.
    if "ALKA-SELTZER" in probe or "ALKA SELTZER" in probe or "ALKA-SELZTER" in probe or "ALLERGY" in probe or "THERAFLU" in probe:
        return "Health"

    for cat, keys in AMAZON_ITEM_CATEGORY_RULES:
        for key in keys:
            key_u = key.upper()
            if " " in key_u or "-" in key_u or "'" in key_u:
                matched = key_u in probe
            else:
                matched = key_u in probe_tokens
            if matched:
                return "Home" if cat == "Utilities" else cat

    ncat = conservative_category("", product_name, product_name, amount)
    if ncat == "Utilities":
        return "Home"
    if ncat == "Unclassified":
        return "Home"
    return ncat


def compute_hash_key(txn: Txn):
    raw = "|".join([
        txn.source_institution,
        txn.source_account,
        txn.txn_date or "",
        f"{txn.amount:.2f}",
        txn.normalized_merchant,
        txn.reference_id,
    ])
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:24]


def parse_firsttech(path: Path):
    txns = []
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            raw_desc = (row.get("Description") or "").strip()
            merchant = norm_merchant(raw_desc)
            amount = float(row.get("Amount") or 0)
            ncat = conservative_category(row.get("Transaction Category") or "", raw_desc, merchant, amount)

            is_transfer = 1 if ("XFER TO" in raw_desc.upper() or "TRANSFER" in (row.get("Transaction Category") or "").upper()) else 0
            txns.append(Txn(
                source_institution="FirstTech",
                source_account="Checking",
                source_file=str(path.relative_to(ROOT)).replace("\\", "/"),
                source_transaction_id=(row.get("Transaction ID") or "").strip(),
                txn_date=parse_date(row.get("Posting Date") or ""),
                posted_date=parse_date(row.get("Posting Date") or ""),
                effective_date=parse_date(row.get("Effective Date") or ""),
                amount=amount,
                direction="credit" if amount > 0 else "debit",
                currency="USD",
                raw_merchant=raw_desc,
                normalized_merchant=merchant,
                raw_description=raw_desc,
                memo=(row.get("Memo") or "").strip(),
                reference_id=(row.get("Reference Number") or "").strip(),
                account_type="bank",
                provider_category=(row.get("Transaction Category") or "").strip(),
                normalized_category=ncat,
                is_transfer=is_transfer,
                transfer_group_id="",
            ))
    return txns


def parse_fidelity(path: Path):
    txns = []
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            raw_name = (row.get("Name") or "").strip()
            raw_desc = raw_name
            memo = (row.get("Memo") or "").strip()
            merchant = norm_merchant(raw_name)
            amount = float(row.get("Amount") or 0)
            ncat = conservative_category("", raw_desc, merchant, amount)
            
            # Amazon charges on credit cards are transfers (to avoid double-counting with direct Amazon purchases)
            if "AMAZON" in raw_name.upper():
                ncat = "Transfers"

            is_transfer = 1 if "PAYMENT   THANK YOU" in raw_name.upper() else 0
            txns.append(Txn(
                source_institution="Fidelity",
                source_account="Credit Card 1860",
                source_file=str(path.relative_to(ROOT)).replace("\\", "/"),
                source_transaction_id="",
                txn_date=parse_date(row.get("Date") or ""),
                posted_date=parse_date(row.get("Date") or ""),
                effective_date=None,
                amount=amount,
                direction="credit" if amount > 0 else "debit",
                currency="USD",
                raw_merchant=raw_name,
                normalized_merchant=merchant,
                raw_description=raw_desc,
                memo=memo,
                reference_id=memo.split(";")[0].strip() if memo else "",
                account_type="credit_card",
                provider_category="",
                normalized_category=ncat,
                is_transfer=is_transfer,
                transfer_group_id="",
            ))
    return txns


def parse_date_flexible(value: str):
    value = (value or "").strip()
    if not value:
        return None

    parsed = parse_date(value)
    if parsed:
        return parsed

    for fmt in ("%Y-%m-%dT%H:%M:%S.%fZ", "%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(value, fmt).date().isoformat()
        except ValueError:
            pass
    return None


def first_non_empty(row: dict, keys):
    for key in keys:
        value = (row.get(key) or "").strip()
        if value:
            return value
    return ""


def parse_money(value: str):
    text = (value or "").strip()
    if not text:
        return None
    text = text.replace("$", "").replace(",", "")
    if text.startswith("(") and text.endswith(")"):
        text = f"-{text[1:-1]}"
    try:
        return float(text)
    except ValueError:
        return None


def parse_amazon_item_purchases():
    txns = []

    def first_existing(*paths):
        for p in paths:
            if p.exists():
                return p
        return None

    def add_item_txn(source_file: Path, row: dict, *, order_id_keys, asin_keys, name_keys, date_keys, amount_keys, qty_keys):
        order_id = first_non_empty(row, order_id_keys)
        product_name = first_non_empty(row, name_keys)
        if not order_id or not product_name:
            return

        amount_value = None
        for key in amount_keys:
            amount_raw = first_non_empty(row, [key])
            if amount_raw.upper() in {"NOT APPLICABLE", "N/A"}:
                continue
            amount_value = parse_money(amount_raw)
            if amount_value is not None:
                break
        if amount_value is None or amount_value <= 0:
            return

        qty_text = first_non_empty(row, qty_keys)
        qty = parse_money(qty_text) if qty_text else 1.0
        if qty is None or qty <= 0:
            qty = 1.0

        per_item_amount = -(amount_value / qty)
        asin = first_non_empty(row, asin_keys)
        txn_date = parse_date_flexible(first_non_empty(row, date_keys))
        ncat = categorize_amazon_item(product_name, per_item_amount)

        item_count = int(round(qty))
        item_count = max(item_count, 1)

        for idx in range(item_count):
            reference_id = f"{order_id}:{asin or 'NOASIN'}:{idx+1}"
            txns.append(Txn(
                source_institution="Amazon Detail",
                source_account="Item Purchases",
                source_file=str(source_file.relative_to(ROOT)).replace("\\", "/"),
                source_transaction_id=reference_id,
                txn_date=txn_date,
                posted_date=txn_date,
                effective_date=None,
                amount=per_item_amount,
                direction="debit",
                currency="USD",
                raw_merchant=f"AMAZON ORDER {order_id}",
                normalized_merchant="AMAZON ITEM",
                raw_description=product_name,
                memo="",
                reference_id=reference_id,
                account_type="order_item",
                provider_category="",
                normalized_category=ncat,
                is_transfer=0,
                transfer_group_id="",
            ))

    order_history_path = first_existing(AMAZON_ORDER_HISTORY, AMAZON_ORDER_HISTORY_LEGACY)
    if order_history_path is not None:
        with order_history_path.open("r", encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                add_item_txn(
                    order_history_path,
                    row,
                    order_id_keys=["Order ID", "Order Id"],
                    asin_keys=["ASIN", "Asin"],
                    name_keys=["Product Name", "Product name", "Title"],
                    date_keys=["Order Date", "Order Date and Time", "Purchase Date"],
                    amount_keys=["Total Amount", "Shipment Item Subtotal", "Item Total", "Item Subtotal", "Item Price", "Price", "Unit Price"],
                    qty_keys=["Original Quantity", "Quantity", "Quantity Ordered", "Item Quantity"],
                )

    digital_orders_path = first_existing(AMAZON_DIGITAL_CONTENT_ORDERS, AMAZON_DIGITAL_CONTENT_ORDERS_LEGACY)
    if digital_orders_path is not None:
        with digital_orders_path.open("r", encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                component = (row.get("Component Type") or "").strip().upper()
                if component and component not in {"PRICE AMOUNT", "NOT APPLICABLE"}:
                    continue
                add_item_txn(
                    digital_orders_path,
                    row,
                    order_id_keys=["Order ID", "Order Id"],
                    asin_keys=["ASIN", "Asin"],
                    name_keys=["Product Name", "Title"],
                    date_keys=["Order Date", "Order Date and Time", "Purchase Date"],
                    amount_keys=["Transaction Amount", "Price", "List Price Amount", "Installment Our Price", "Amount", "Item Total"],
                    qty_keys=["Quantity", "Affected Item Quantity"],
                )

    return txns


def read_pdf_lines(path: Path):
    text = "\n".join((page.extract_text() or "") for page in PdfReader(str(path)).pages)
    return [line.strip() for line in text.splitlines() if line.strip()]


def parse_chase_pdfs(directory: Path):
    txns = []
    files = sorted(directory.glob("*.pdf"))

    period_re = re.compile(r"Opening/Closing Date\s+(\d{2}/\d{2}/\d{2})\s+-\s+(\d{2}/\d{2}/\d{2})")
    row_re = re.compile(r"^(\d{2}/\d{2})\s+(.*?)\s+(\d{1,3}(?:,\d{3})*\.\d{2})$")

    for path in files:
        lines = read_pdf_lines(path)
        full_text = "\n".join(lines)

        open_date = None
        close_date = None
        m_period = period_re.search(full_text)
        if m_period:
            open_date = parse_date(m_period.group(1))
            close_date = parse_date(m_period.group(2))

        fallback_year = None
        m_year = re.search(r"(20\d{2})", path.stem)
        if m_year:
            fallback_year = int(m_year.group(1))

        for line in lines:
            m = row_re.match(line)
            if not m:
                continue

            mmdd, desc, amount_str = m.groups()
            txn_date = None
            if open_date and close_date:
                txn_date = parse_date_with_year_fallback(mmdd, open_date, close_date)
            elif fallback_year is not None:
                try:
                    month, day = [int(x) for x in mmdd.split("/")]
                    txn_date = datetime(fallback_year, month, day).date().isoformat()
                except ValueError:
                    txn_date = None

            amount = -float(amount_str.replace(",", ""))
            raw_desc = desc.strip()
            merchant = norm_merchant(raw_desc)
            ncat = conservative_category("", raw_desc, merchant, amount)
            
            # Amazon charges on credit cards are transfers (to avoid double-counting with direct Amazon purchases)
            if "AMAZON" in raw_desc.upper():
                ncat = "Transfers"

            txns.append(Txn(
                source_institution="Chase",
                source_account="Credit Card 6773",
                source_file=str(path.relative_to(ROOT)).replace("\\", "/"),
                source_transaction_id="",
                txn_date=txn_date,
                posted_date=txn_date,
                effective_date=None,
                amount=amount,
                direction="debit",
                currency="USD",
                raw_merchant=raw_desc,
                normalized_merchant=merchant,
                raw_description=raw_desc,
                memo="",
                reference_id="",
                account_type="credit_card",
                provider_category="",
                normalized_category=ncat,
                is_transfer=0,
                transfer_group_id="",
            ))

    return txns


def parse_paypal_pdfs(directory: Path):
    txns = []
    files = sorted(directory.glob("*.pdf"))

    date_start_re = re.compile(r"^(\d{2}/\d{2}/\d{4})\s+(.+)$")
    usd_line_re = re.compile(r"^USD\s+(-?\d{1,3}(?:,\d{3})*\.\d{2})\s+(-?\d{1,3}(?:,\d{3})*\.\d{2})\s+(-?\d{1,3}(?:,\d{3})*\.\d{2})$")

    for path in files:
        lines = read_pdf_lines(path)
        idx = 0
        while idx < len(lines):
            line = lines[idx]
            m_start = date_start_re.match(line)
            if not m_start:
                idx += 1
                continue

            date_s = m_start.group(1)
            desc_parts = [m_start.group(2)]
            txn_id = ""
            ref_id = ""
            amount = None

            j = idx + 1
            while j < len(lines):
                current = lines[j]

                if date_start_re.match(current):
                    break

                if current.startswith("ID:"):
                    txn_id = current.replace("ID:", "").strip()
                    j += 1
                    continue

                if current.startswith("Ref ID:"):
                    ref_id = current.replace("Ref ID:", "").strip()
                    j += 1
                    continue

                m_usd = usd_line_re.match(current)
                if m_usd:
                    amount = float(m_usd.group(1).replace(",", ""))
                    j += 1
                    break

                if not current.startswith("ACCOUNT ") and not current.startswith("PAGE") and not current.startswith("Statement Period"):
                    desc_parts.append(current)
                j += 1

            if amount is not None:
                raw_desc = " ".join(desc_parts).strip()
                merchant = norm_merchant(raw_desc)

                is_transfer = 1 if "GENERAL CREDIT CARD DEPOSIT" in raw_desc.upper() else 0
                provider_category = "Transfer" if is_transfer else ""
                ncat = "Transfers" if is_transfer else conservative_category(provider_category, raw_desc, merchant, amount)

                txn_date = parse_date(date_s)

                txns.append(Txn(
                    source_institution="PayPal",
                    source_account="PayPal Account",
                    source_file=str(path.relative_to(ROOT)).replace("\\", "/"),
                    source_transaction_id=txn_id,
                    txn_date=txn_date,
                    posted_date=txn_date,
                    effective_date=None,
                    amount=amount,
                    direction="credit" if amount > 0 else "debit",
                    currency="USD",
                    raw_merchant=raw_desc,
                    normalized_merchant=merchant,
                    raw_description=raw_desc,
                    memo="",
                    reference_id=ref_id,
                    account_type="digital_wallet",
                    provider_category=provider_category,
                    normalized_category=ncat,
                    is_transfer=is_transfer,
                    transfer_group_id=ref_id,
                ))

            idx = j if j > idx else idx + 1

    return txns


def init_db(conn: sqlite3.Connection):
    conn.executescript(
        """
        PRAGMA journal_mode=WAL;

        DROP TABLE IF EXISTS transactions;
        DROP TABLE IF EXISTS recurring_candidates;
        DROP TABLE IF EXISTS amazon_orders;
        DROP TABLE IF EXISTS amazon_matches;
        DROP TABLE IF EXISTS merchant_map;
        DROP TABLE IF EXISTS deduped_transactions;
        DROP VIEW IF EXISTS amazon_item_monthly_metrics;

        CREATE TABLE transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            hash_id TEXT NOT NULL,
            source_institution TEXT NOT NULL,
            source_account TEXT NOT NULL,
            source_file TEXT NOT NULL,
            source_transaction_id TEXT,
            txn_date TEXT,
            posted_date TEXT,
            effective_date TEXT,
            amount REAL NOT NULL,
            direction TEXT NOT NULL,
            currency TEXT NOT NULL,
            raw_merchant TEXT,
            normalized_merchant TEXT,
            raw_description TEXT,
            memo TEXT,
            reference_id TEXT,
            account_type TEXT NOT NULL,
            provider_category TEXT,
            normalized_category TEXT NOT NULL,
            is_transfer INTEGER NOT NULL DEFAULT 0,
            transfer_group_id TEXT
        );

        CREATE INDEX idx_transactions_date ON transactions(txn_date);
        CREATE INDEX idx_transactions_merchant ON transactions(normalized_merchant);
        CREATE INDEX idx_transactions_category ON transactions(normalized_category);
        CREATE INDEX idx_transactions_hash ON transactions(hash_id);

        CREATE TABLE recurring_candidates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            normalized_merchant TEXT NOT NULL,
            normalized_category TEXT NOT NULL,
            txn_count INTEGER NOT NULL,
            avg_amount REAL NOT NULL,
            stddev_amount REAL NOT NULL,
            avg_day_gap REAL NOT NULL,
            cadence_guess TEXT NOT NULL,
            first_date TEXT,
            last_date TEXT,
            confidence REAL NOT NULL
        );

        CREATE TABLE amazon_orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id TEXT NOT NULL,
            asin TEXT,
            product_name TEXT,
            return_reason TEXT,
            source_file TEXT
        );

        CREATE TABLE amazon_matches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            txn_id TEXT,
            order_id TEXT,
            match_confidence REAL,
            match_type TEXT
        );

        CREATE TABLE merchant_map (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            raw_merchant TEXT NOT NULL,
            canonical_merchant TEXT NOT NULL
        );

        CREATE TABLE deduped_transactions AS
        SELECT * FROM transactions
        WHERE 1=0;

        CREATE VIEW amazon_item_monthly_metrics AS
        SELECT
            substr(txn_date, 1, 7) AS month,
            ROUND(SUM(CASE WHEN amount < 0 THEN -amount ELSE 0 END), 2) AS spend,
            SUM(CASE WHEN amount < 0 THEN 1 ELSE 0 END) AS transactions,
            ROUND(
                SUM(CASE WHEN amount < 0 THEN -amount ELSE 0 END) /
                NULLIF(SUM(CASE WHEN amount < 0 THEN 1 ELSE 0 END), 0),
                2
            ) AS avg_transaction
        FROM transactions
        WHERE source_institution = 'Amazon Detail'
          AND source_account = 'Item Purchases'
        GROUP BY substr(txn_date, 1, 7)
        ORDER BY month;
        """
    )


def insert_transactions(conn: sqlite3.Connection, txns):
    rows = []
    for t in txns:
        hash_id = compute_hash_key(t)
        rows.append((
            hash_id,
            t.source_institution,
            t.source_account,
            t.source_file,
            t.source_transaction_id,
            t.txn_date,
            t.posted_date,
            t.effective_date,
            t.amount,
            t.direction,
            t.currency,
            t.raw_merchant,
            t.normalized_merchant,
            t.raw_description,
            t.memo,
            t.reference_id,
            t.account_type,
            t.provider_category,
            t.normalized_category,
            t.is_transfer,
            t.transfer_group_id,
        ))

    conn.executemany(
        """
        INSERT INTO transactions (
            hash_id, source_institution, source_account, source_file, source_transaction_id,
            txn_date, posted_date, effective_date, amount, direction, currency,
            raw_merchant, normalized_merchant, raw_description, memo, reference_id,
            account_type, provider_category, normalized_category, is_transfer, transfer_group_id
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        rows,
    )


def amount_stddev(values):
    if not values:
        return 0.0
    m = mean(values)
    return (sum((v - m) ** 2 for v in values) / len(values)) ** 0.5


def load_amazon_orders(conn: sqlite3.Connection):
    rows = []

    def append_if_present(path: Path, builder):
        if not path.exists():
            return
        with path.open("r", encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            for record in reader:
                built = builder(record)
                if built and built[0]:
                    rows.append(built)

    append_if_present(
        AMAZON_RETURN_REQUESTS,
        lambda r: (
            (r.get("Order ID") or "").strip(),
            (r.get("ASIN") or "").strip(),
            (r.get("Product Name") or "").strip(),
            (r.get("Return Reason Code") or "").strip(),
            "Return Requests.csv",
        ),
    )

    append_if_present(
        AMAZON_REFUND_DETAILS,
        lambda r: (
            (r.get("Order ID") or "").strip(),
            "",
            "",
            (r.get("Reversal Reason") or r.get("Payment Status") or "").strip(),
            "Refund Details.csv",
        ),
    )

    append_if_present(
        AMAZON_REPLACEMENT_ORDERS,
        lambda r: (
            (r.get("Order ID") or "").strip(),
            "",
            "",
            "replacement_order",
            "Replacement Orders.csv",
        ),
    )

    append_if_present(
        AMAZON_DIGITAL_RETURNS,
        lambda r: (
            (r.get("Order ID") or "").strip(),
            (r.get("ASIN") or "").strip(),
            (r.get("Product Name") or "").strip(),
            (r.get("Reason Code") or "").strip(),
            "Digital Returns.csv",
        ),
    )

    if rows:
        conn.executemany(
            "INSERT INTO amazon_orders (order_id, asin, product_name, return_reason, source_file) VALUES (?, ?, ?, ?, ?)",
            rows,
        )


def match_amazon_orders(conn: sqlite3.Connection):
    if not conn.execute("SELECT COUNT(*) FROM amazon_orders").fetchone()[0]:
        return

    amz_orders = {}
    for order_id, asin, product_name, reason, _ in conn.execute(
        "SELECT order_id, asin, product_name, return_reason, source_file FROM amazon_orders"
    ).fetchall():
        amz_orders[order_id] = {"asin": asin, "product_name": product_name, "reason": reason}

    amazon_txns = conn.execute(
        "SELECT id, txn_date, amount, raw_description FROM transactions WHERE raw_description LIKE '%AMAZON%' OR normalized_merchant LIKE '%AMAZON%'"
    ).fetchall()

    matches = []
    order_id_pattern = re.compile(r"\b(\d{3}-\d{7}-\d{7})\b")
    
    for txn_id, txn_date, amount, raw_desc in amazon_txns:
        best_order = None
        best_conf = 0
        
        order_ids_in_desc = order_id_pattern.findall(raw_desc or "")
        if order_ids_in_desc:
            for found_order_id in order_ids_in_desc:
                if found_order_id in amz_orders:
                    best_order = found_order_id
                    best_conf = 0.95
                    break
        
        if best_conf >= 0.5:
            matches.append((txn_id, best_order, best_conf, "order_id_match"))

    if matches:
        conn.executemany(
            "INSERT INTO amazon_matches (txn_id, order_id, match_confidence, match_type) VALUES (?, ?, ?, ?)",
            matches,
        )


def build_merchant_map(conn: sqlite3.Connection):
    merchants = conn.execute("SELECT DISTINCT normalized_merchant FROM transactions ORDER BY normalized_merchant").fetchall()
    rows = []
    for (m,) in merchants:
        canonical = m
        if "PAYPAL" in m.upper() and "HELLOFRESH" in m.upper():
            canonical = "HELLOFRESH"
        elif "PAYPAL" in m.upper() and "DOORDASH" in m.upper():
            canonical = "DOORDASH"
        elif "PAYPAL" in m.upper() and "SPOTIFY" in m.upper():
            canonical = "SPOTIFY"
        elif "PAYPAL" in m.upper() and "DISNEY" in m.upper():
            canonical = "DISNEY PLUS"
        elif "POS TRANSACTION HELLOFRESH" in m.upper():
            canonical = "HELLOFRESH"
        elif "POS TRANSACTION DOORDASH" in m.upper():
            canonical = "DOORDASH"
        else:
            canonical = m
        rows.append((m, canonical))
    if rows:
        conn.executemany(
            "INSERT INTO merchant_map (raw_merchant, canonical_merchant) VALUES (?, ?)",
            rows,
        )


def build_deduped_view(conn: sqlite3.Connection):
    conn.execute("DELETE FROM deduped_transactions")
    conn.execute(
        """
        INSERT INTO deduped_transactions
        SELECT DISTINCT t.* FROM transactions t
        WHERE 1=1
          AND NOT (
              t.source_institution = 'PayPal'
              AND t.is_transfer = 1
              AND EXISTS (
                  SELECT 1 FROM transactions t2
                  WHERE t2.source_institution IN ('FirstTech', 'Fidelity', 'Chase')
                    AND ABS(t2.amount) >= 0.01
                    AND ABS(t2.amount + t.amount) < 0.01
                    AND ABS(CAST(substr(t2.txn_date, 6) AS FLOAT) - CAST(substr(t.txn_date, 6) AS FLOAT)) <= 2
              )
          )
        """
    )


def detect_recurring(conn: sqlite3.Connection):
    cur = conn.cursor()
    cur.execute(
        """
        SELECT normalized_merchant, normalized_category, txn_date, amount
        FROM transactions
        WHERE direction = 'debit'
          AND amount < 0
          AND normalized_category NOT IN ('Transfers', 'Unclassified')
          AND normalized_merchant <> ''
        ORDER BY normalized_merchant, txn_date
        """
    )

    grouped = {}
    for merchant, cat, date_s, amt in cur.fetchall():
        if not date_s:
            continue
        grouped.setdefault((merchant, cat), []).append((datetime.fromisoformat(date_s).date(), abs(amt)))

    rec_rows = []
    for (merchant, cat), items in grouped.items():
        if len(items) < 3:
            continue
        items.sort(key=lambda x: x[0])
        dates = [d for d, _ in items]
        amts = [a for _, a in items]
        gaps = [(dates[i] - dates[i - 1]).days for i in range(1, len(dates))]
        if not gaps:
            continue

        avg_gap = sum(gaps) / len(gaps)
        if 26 <= avg_gap <= 35:
            cadence = "monthly"
        elif 12 <= avg_gap <= 17:
            cadence = "biweekly"
        elif 6 <= avg_gap <= 8:
            cadence = "weekly"
        else:
            cadence = "irregular"

        std = amount_stddev(amts)
        avg_amt = sum(amts) / len(amts)
        stable_amount = std <= max(2.0, avg_amt * 0.08)
        cadence_score = 1.0 if cadence != "irregular" else 0.4
        amount_score = 1.0 if stable_amount else 0.5
        count_score = min(1.0, len(items) / 6.0)
        confidence = round(0.4 * cadence_score + 0.4 * amount_score + 0.2 * count_score, 3)

        if confidence >= 0.65:
            rec_rows.append((
                merchant,
                cat,
                len(items),
                round(avg_amt, 2),
                round(std, 2),
                round(avg_gap, 2),
                cadence,
                dates[0].isoformat(),
                dates[-1].isoformat(),
                confidence,
            ))

    conn.executemany(
        """
        INSERT INTO recurring_candidates (
            normalized_merchant, normalized_category, txn_count, avg_amount, stddev_amount,
            avg_day_gap, cadence_guess, first_date, last_date, confidence
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        rec_rows,
    )


def write_report(conn: sqlite3.Connection):
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM deduped_transactions")
    deduped_count = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM transactions")
    txn_count = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM transactions WHERE amount < 0")
    debit_count = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM transactions WHERE amount > 0")
    credit_count = cur.fetchone()[0]

    cur.execute(
        """
        SELECT normalized_category, ROUND(SUM(CASE WHEN amount < 0 THEN -amount ELSE 0 END), 2) AS spend
        FROM transactions
        GROUP BY normalized_category
        ORDER BY spend DESC
        LIMIT 15
        """
    )
    by_cat = cur.fetchall()

    cur.execute(
        """
        SELECT normalized_merchant, ROUND(SUM(CASE WHEN amount < 0 THEN -amount ELSE 0 END), 2) AS spend, COUNT(*)
        FROM transactions
        WHERE amount < 0
          AND normalized_category <> 'Transfers'
        GROUP BY normalized_merchant
        ORDER BY spend DESC
        LIMIT 20
        """
    )
    top_merchants = cur.fetchall()

    cur.execute(
        """
        SELECT substr(txn_date, 1, 7) AS ym,
               ROUND(SUM(CASE WHEN amount < 0 AND normalized_category <> 'Transfers' THEN -amount ELSE 0 END), 2) AS spend
        FROM transactions
        GROUP BY ym
        ORDER BY ym
        """
    )
    monthly = cur.fetchall()

    cur.execute(
        """
        SELECT normalized_merchant, normalized_category, txn_count, avg_amount, cadence_guess, confidence
        FROM recurring_candidates
        ORDER BY confidence DESC, txn_count DESC
        """
    )
    recurring = cur.fetchall()

    cur.execute(
        """
        SELECT COUNT(*)
        FROM transactions
        WHERE normalized_merchant LIKE 'AMAZON%'
           OR raw_description LIKE '%AMAZON%'
        """
    )
    amazon_count = cur.fetchone()[0]

    cur.execute(
        """
        SELECT source_institution, source_account, COUNT(*)
        FROM transactions
        GROUP BY source_institution, source_account
        ORDER BY source_institution, source_account
        """
    )
    source_coverage = cur.fetchall()

    cur.execute("SELECT COUNT(*) FROM amazon_matches WHERE match_confidence >= 0.3")
    amazon_matches = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM amazon_orders")
    amazon_order_records = cur.fetchone()[0]

    cur.execute(
        """
        SELECT COUNT(*), ROUND(SUM(CASE WHEN amount < 0 THEN -amount ELSE 0 END), 2)
        FROM transactions
        WHERE source_institution = 'Amazon Detail'
                    AND source_account = 'Item Purchases'
        """
    )
    amazon_purchase_feed_count, amazon_purchase_feed_spend = cur.fetchone()

    lines = []
    lines.append("# Finance Normalization Report")
    lines.append("")
    lines.append("## Snapshot")
    lines.append(f"- Total transactions: {txn_count}")
    lines.append(f"- Deduped transactions (excluding PayPal transfers): {deduped_count}")
    lines.append(f"- Debits: {debit_count}")
    lines.append(f"- Credits: {credit_count}")
    lines.append(f"- Amazon-labeled transactions found: {amazon_count}")
    lines.append(f"- Amazon detail records loaded: {amazon_order_records}")
    lines.append(f"- Amazon item feed records loaded: {amazon_purchase_feed_count}")
    lines.append(f"- Amazon item feed spend: ${float(amazon_purchase_feed_spend or 0):,.2f}")
    lines.append(f"- Amazon order matches: {amazon_matches}")
    lines.append("")

    lines.append("## Source Coverage")
    for source_institution, source_account, count in source_coverage:
        lines.append(f"- {source_institution} / {source_account}: {count} transactions")
    lines.append("")

    lines.append("## Spend by Category (Conservative)")
    lines.append("| Category | Spend |")
    lines.append("|---|---:|")
    for cat, spend in by_cat:
        lines.append(f"| {cat} | ${spend:,.2f} |")
    lines.append("")

    lines.append("## Top Merchants by Spend")
    lines.append("| Merchant | Spend | Count |")
    lines.append("|---|---:|---:|")
    for merchant, spend, cnt in top_merchants:
        display = merchant if merchant else "(blank)"
        lines.append(f"| {display} | ${spend:,.2f} | {cnt} |")
    lines.append("")

    lines.append("## Monthly Net Spend (Excluding Transfers)")
    lines.append("| Month | Spend |")
    lines.append("|---|---:|")
    for ym, spend in monthly:
        lines.append(f"| {ym} | ${spend:,.2f} |")
    lines.append("")

    lines.append("## Recurring Candidates")
    if recurring:
        lines.append("| Merchant | Category | Count | Avg Amount | Cadence | Confidence |")
        lines.append("|---|---|---:|---:|---|---:|")
        for merchant, cat, cnt, avg_amt, cadence, conf in recurring:
            lines.append(f"| {merchant} | {cat} | {cnt} | ${avg_amt:,.2f} | {cadence} | {conf:.2f} |")
    else:
        lines.append("No high-confidence recurring candidates detected with current conservative rules.")
    lines.append("")

    lines.append("## Subscription Food Services")
    sub_food = cur.execute(
        """SELECT normalized_merchant, ROUND(COUNT(*), 0) AS count, 
                  ROUND(AVG(ABS(amount)), 2) AS avg_amt,
                  ROUND(SUM(CASE WHEN amount < 0 THEN -amount ELSE 0 END), 2) AS total_spent
           FROM transactions
           WHERE normalized_category IN ('Subscription Groceries')
           GROUP BY normalized_merchant
           ORDER BY total_spent DESC"""
    ).fetchall()
    if sub_food:
        lines.append("Recurring subscription-based grocery and meal services:")
        lines.append("| Service | Transactions | Avg Amount | Total Spent |")
        lines.append("|---|---:|---:|---:|")
        for merchant, cnt, avg_amt, total in sub_food:
            lines.append(f"| {merchant} | {int(cnt)} | ${avg_amt:,.2f} | ${total:,.2f} |")
        # Calculate monthly projection
        total_sub_food = sum(row[3] for row in sub_food)
        months_covered = 6
        monthly_avg = total_sub_food / months_covered if months_covered > 0 else 0
        annual_projection = monthly_avg * 12
        lines.append(f"\n**Monthly average:** ${monthly_avg:,.2f} | **Annual projection:** ${annual_projection:,.2f}")
    else:
        lines.append("No subscription food services detected.")
    lines.append("")

    lines.append("## Amazon Order Matches")
    if amazon_matches:
        lines.append("Amazon orders successfully matched to card transactions:")
        matched_rows = cur.execute(
            "SELECT m.order_id, m.match_confidence, m.match_type, a.product_name FROM amazon_matches m JOIN amazon_orders a ON m.order_id = a.order_id WHERE m.match_confidence >= 0.5 LIMIT 20"
        ).fetchall()
        if matched_rows:
            for order_id, conf, match_type, product_name in matched_rows:
                lines.append(f"- {order_id} ({match_type}, confidence {conf:.2f}): {product_name[:60]}")
        else:
            lines.append("Note: Credit card descriptions do not contain Amazon order IDs for deterministic matching.")
            lines.append("Recommend obtaining Amazon order history export with transaction dates and amounts for reliable enrichment.")
    else:
        lines.append("Amazon order matching not possible - credit card merchant descriptors do not contain order IDs.")
        lines.append("To enable Amazon order-level analysis, please provide Amazon order history CSV with dates and amounts.")
    lines.append("")

    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main():
    txns = []
    if FIRSTTECH_CSV.exists():
        txns.extend(parse_firsttech(FIRSTTECH_CSV))
    if FIDELITY_CSV.exists():
        txns.extend(parse_fidelity(FIDELITY_CSV))
    txns.extend(parse_amazon_item_purchases())
    if CHASE_DIR.exists():
        txns.extend(parse_chase_pdfs(CHASE_DIR))
    if PAYPAL_DIR.exists():
        txns.extend(parse_paypal_pdfs(PAYPAL_DIR))

    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    try:
        init_db(conn)
        insert_transactions(conn, txns)
        load_amazon_orders(conn)
        match_amazon_orders(conn)
        build_merchant_map(conn)
        build_deduped_view(conn)
        detect_recurring(conn)
        write_report(conn)
        conn.commit()
    finally:
        conn.close()

    print(f"Wrote SQLite DB: {DB_PATH}")
    print(f"Wrote report: {REPORT_PATH}")


if __name__ == "__main__":
    main()
