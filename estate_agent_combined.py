"""
╔══════════════════════════════════════════════════════════════════════╗
║     ESTATE AGENT — EMAIL SCRAPER + FULL WEBSITE AUDIT TOOL          ║
║                                                                      ║
║  Phase 1 (Playwright): Email scraping via headless Chromium          ║
║  Phase 2 (Requests):   Full website audit — CTAs · Meta/Schema       ║
║                        Robots · Accessibility · Content              ║
║                        Localisation · Trust · Tracking · Services    ║
╚══════════════════════════════════════════════════════════════════════╝

Install dependencies:
    pip install playwright beautifulsoup4 lxml requests textstat langdetect
    playwright install chromium

Optional (for PageSpeed scores):
    Set PAGESPEED_API_KEY below (free from Google Cloud Console)
    https://developers.google.com/speed/docs/insights/v5/get-started
"""

# ── Standard library ──────────────────────────────────────────────────
import re
import json
import time
import sys
import csv
import asyncio
from collections import Counter
from datetime import datetime
from urllib.parse import urljoin, urlparse

# ── Third-party ───────────────────────────────────────────────────────
import requests
from bs4 import BeautifulSoup

try:
    import textstat
    HAS_TEXTSTAT = True
except ImportError:
    HAS_TEXTSTAT = False
    print("[WARN] textstat not installed — readability checks skipped. pip install textstat\n")

try:
    from langdetect import detect as langdetect_detect
    HAS_LANGDETECT = True
except ImportError:
    HAS_LANGDETECT = False
    print("[WARN] langdetect not installed — language detection skipped. pip install langdetect\n")

try:
    from playwright.async_api import async_playwright
    HAS_PLAYWRIGHT = True
except ImportError:
    HAS_PLAYWRIGHT = False
    print("[WARN] playwright not installed — email scraping phase will be skipped. pip install playwright && playwright install chromium\n")


# ══════════════════════════════════════════════════════════════════════
#  CONFIGURATION
# ══════════════════════════════════════════════════════════════════════

PAGESPEED_API_KEY = "AIzaSyDWMhnoy2AsqyXQNoA1f32vE5QOwHp_3gM"          # Optional — leave blank to skip
REQUEST_TIMEOUT   = 20
REQUEST_DELAY     = 1.5

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-GB,en;q=0.9",
}

# ── Target URLs ───────────────────────────────────────────────────────
URLS = [
    "https://www.kings-estates.co.uk/property-valuation/",
    "https://www.knightfrank.co.uk/offices/tunbridge-wells-estate-agents",
    "http://maddisonsresidential.co.uk/",
    "https://www.andrewsonline.co.uk/about/offices/tunbridge-wells",
    "https://www.your-move.co.uk/estate-agent/tunbridge-wells",
]

# ── Email scraper config ──────────────────────────────────────────────
EMAIL_REGEX    = re.compile(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}")
IGNORE_DOMAINS = {"example.com", "sentry.io", "w3.org", "schema.org", "wixpress.com"}
IGNORE_TLDS    = {"png", "jpg", "gif", "svg", "js", "css", "html", "webp"}

# ── UK Property signals (always checked) ─────────────────────────────
UK_PROPERTY_SIGNALS = [
    "£", "stamp duty", "freehold", "leasehold", "conveyancing",
    "solicitor", "epc", "rightmove", "zoopla", "on the market",
    "naea", "arla", "propertymark", "rics", "ombudsman", "tpos",
    "united kingdom", "england", "scotland", "wales", "northern ireland",
]

# ── UK Counties & Regions ─────────────────────────────────────────────
UK_COUNTIES = [
    # English counties
    "bedfordshire", "berkshire", "bristol", "buckinghamshire", "cambridgeshire",
    "cheshire", "city of london", "cornwall", "cumbria", "derbyshire",
    "devon", "dorset", "durham", "east riding of yorkshire", "east sussex",
    "essex", "gloucestershire", "greater london", "greater manchester",
    "hampshire", "herefordshire", "hertfordshire", "isle of wight",
    "kent", "lancashire", "leicestershire", "lincolnshire", "merseyside",
    "norfolk", "north yorkshire", "northamptonshire", "northumberland",
    "nottinghamshire", "oxfordshire", "rutland", "shropshire", "somerset",
    "south yorkshire", "staffordshire", "suffolk", "surrey", "tyne and wear",
    "warwickshire", "west midlands", "west sussex", "west yorkshire",
    "wiltshire", "worcestershire",
    # Welsh counties
    "anglesey", "blaenau gwent", "bridgend", "caerphilly", "cardiff",
    "carmarthenshire", "ceredigion", "conwy", "denbighshire", "flintshire",
    "gwynedd", "merthyr tydfil", "monmouthshire", "neath port talbot",
    "newport", "pembrokeshire", "powys", "rhondda cynon taf", "swansea",
    "torfaen", "vale of glamorgan", "wrexham",
    # Scottish regions
    "aberdeen", "aberdeenshire", "angus", "argyll and bute", "clackmannanshire",
    "dumfries and galloway", "dundee", "east ayrshire", "east dunbartonshire",
    "east lothian", "east renfrewshire", "edinburgh", "eilean siar",
    "falkirk", "fife", "glasgow", "highland", "inverclyde", "midlothian",
    "moray", "north ayrshire", "north lanarkshire", "orkney", "perth and kinross",
    "renfrewshire", "scottish borders", "shetland", "south ayrshire",
    "south lanarkshire", "stirling", "west dunbartonshire", "west lothian",
    # Northern Ireland
    "antrim", "armagh", "belfast", "causeway coast", "derry", "fermanagh",
    "lisburn", "mid and east antrim", "mid ulster", "newry", "north down",
    "strabane",
    # Regions / areas
    "south east", "south west", "east midlands", "west midlands",
    "east of england", "north east", "north west", "yorkshire",
    "home counties", "the cotswolds", "the weald", "high weald",
    "peak district", "lake district", "new forest", "chilterns",
]

# ── Comprehensive UK Towns & Cities ───────────────────────────────────
# Major cities, towns, and commonly referenced places across all regions.
# This covers ~1,200 settlements; the dynamic extractor (below) catches the rest.
UK_TOWNS = [
    # A
    "aberdeen", "aberystwyth", "abingdon", "accrington", "acton",
    "aldeburgh", "alderley edge", "aldershot", "alfreton", "alton",
    "altrincham", "amersham", "amesbury", "andover", "arundel",
    "ascot", "ashbourne", "ashby de la zouch", "ashford", "ashington",
    "ashtead", "aylesbury", "aylesford",
    # B
    "banbury", "bangor", "barking", "barnet", "barnsley", "barnstaple",
    "barrow in furness", "basildon", "basingstoke", "bath", "battersea",
    "battle", "bedford", "belfast", "berkhamsted", "berwick upon tweed",
    "beverley", "bexhill", "bexley", "bicester", "bideford",
    "biggleswade", "billericay", "birkenhead", "birmingham", "bishop auckland",
    "bishop's stortford", "blackburn", "blackpool", "blandford forum",
    "blyth", "bodmin", "bognor regis", "bolton", "bordon", "boston",
    "bournemouth", "brackley", "bracknell", "bradford", "braintree",
    "brentford", "brentwood", "bridgend", "bridgnorth", "bridgwater",
    "bridlington", "bridport", "brighton", "bristol", "broadstairs",
    "bromley", "bromsgrove", "burnley", "burton upon trent", "bury",
    "bury st edmunds",
    # C
    "camberley", "cambridge", "cannock", "canterbury", "carlisle",
    "carmarthen", "chatham", "cheadle", "chelmsford", "cheltenham",
    "chertsey", "chester", "chester le street", "chesterfield",
    "chichester", "chippenham", "chipping norton", "chorley", "christchurch",
    "cirencester", "clacton on sea", "colchester", "congleton",
    "consett", "corby", "coventry", "crawley", "crewe", "croydon",
    "crowborough", "crowthorne",
    # D
    "darlington", "dartford", "dartmouth", "deal", "derby", "dereham",
    "devizes", "dewsbury", "didcot", "doncaster", "dorchester",
    "dover", "droitwich", "dronfield", "dudley", "dumfries", "dunstable",
    "durham",
    # E
    "eastbourne", "eastleigh", "edenbridge", "egham", "ely",
    "epsom", "esher", "evesham", "exeter", "exmouth",
    # F
    "faversham", "farnborough", "farnham", "felixstowe", "fleet",
    "fleetwood", "folkestone", "fordingbridge", "frodsham", "frome",
    # G
    "gateshead", "gillingham", "glastonbury", "gloucester", "godalming",
    "goole", "grantham", "gravesend", "great yarmouth", "grimsby",
    "guildford",
    # H
    "hailsham", "halifax", "harlow", "harrogate", "hartlepool",
    "hastings", "hatfield", "havant", "haverfordwest", "haywards heath",
    "hemel hempstead", "hereford", "hertford", "hexham", "high wycombe",
    "hucclecote", "huddersfield", "hull", "huntingdon", "hythe",
    # I
    "ilkeston", "ilkley", "ipswich", "irvine",
    # K
    "keighley", "kendal", "kettering", "kidderminster", "king's lynn",
    "kingston upon hull", "kingston upon thames", "knightsbridge",
    # L
    "lancaster", "leamington spa", "leeds", "leicester", "leominster",
    "lewes", "leyland", "lichfield", "lincoln", "lisburn", "liverpool",
    "llandudno", "llanelli", "london", "long eaton", "loughborough",
    "louth", "lowestoft", "ludlow", "luton", "lyme regis",
    # M
    "macclesfield", "maidenhead", "maidstone", "maldon", "malmesbury",
    "malvern", "manchester", "mansfield", "margate", "matlock",
    "medway", "middlesbrough", "milton keynes", "minehead", "mirfield",
    "morpeth",
    # N
    "nantwich", "neath", "newbury", "newcastle under lyme",
    "newcastle upon tyne", "newport", "northallerton", "northampton",
    "northwich", "norwich", "nottingham", "nuneaton",
    # O
    "oldbury", "oldham", "ormskirk", "oswestry", "oxford",
    # P
    "paignton", "penrith", "penzance", "perth", "peterborough",
    "petersfield", "plymouth", "pontefract", "poole", "portsmouth",
    "potters bar", "prescot", "preston",
    # R
    "ramsgate", "rawtenstall", "reading", "redcar", "redditch",
    "reigate", "richmond", "ripon", "rochdale", "rochester",
    "romsey", "rotherham", "rugby", "runcorn", "rushden",
    # S
    "st albans", "st austell", "st helens", "st ives", "salford",
    "salisbury", "sandbach", "scarborough", "scunthorpe", "seaford",
    "sevenoaks", "sheffield", "shepton mallet", "shrewsbury",
    "sittingbourne", "skegness", "skipton", "slough", "solihull",
    "southampton", "southend on sea", "southport", "stafford",
    "stamford", "stevenage", "stoke on trent", "stourbridge",
    "stratford upon avon", "stroud", "sunderland", "sutton coldfield",
    "swansea", "swindon",
    # T
    "tamworth", "taunton", "telford", "tenterden", "tewkesbury",
    "thetford", "thirsk", "tonbridge", "torquay", "totnes",
    "truro", "tunbridge wells", "twickenham",
    # U / V / W
    "uttoxeter", "wakefield", "walsall", "warrington", "warwick",
    "watford", "wellingborough", "wells", "welwyn garden city",
    "west bromwich", "weston super mare", "weymouth", "whitby",
    "whitehaven", "wigan", "winchester", "windsor", "wisbech",
    "woking", "wokingham", "wolverhampton", "worcester", "workington",
    "worksop", "worthing",
    # Y
    "yeovil", "york",
    # London areas & boroughs
    "aldgate", "battersea", "bermondsey", "bethnal green", "brixton",
    "camden", "canary wharf", "chelsea", "clapham", "dalston",
    "ealing", "elephant and castle", "finchley", "fulham", "greenwich",
    "hackney", "hammersmith", "hampstead", "highgate", "holborn",
    "holloway", "hoxton", "islington", "kennington", "kensington",
    "kilburn", "kingston", "lewisham", "mayfair", "notting hill",
    "paddington", "peckham", "pimlico", "poplar", "putney",
    "shepherd's bush", "shoreditch", "soho", "southwark", "stepney",
    "stoke newington", "stratford", "streatham", "tooting", "tower hamlets",
    "vauxhall", "wandsworth", "wapping", "westminster", "whitechapel",
    "wimbledon", "wood green",
    # Scottish cities & towns
    "dundee", "edinburgh", "falkirk", "glasgow", "inverness",
    "kirkcaldy", "livingston", "paisley", "perth", "stirling",
    # Welsh towns
    "aberystwyth", "bangor", "cardiff", "carmarthen", "llandudno",
    "llanelli", "newport", "neath", "swansea", "wrexham",
    # Northern Ireland
    "belfast", "derry", "lisburn", "londonderry", "newry",
    # Old Harlow / New Towns / less common but real
    "old harlow", "harlow", "hatfield", "hemel hempstead",
    "basildon", "corby", "crawley", "skelmersdale", "telford",
    "redditch", "runcorn", "peterlee", "washington", "cramlington",
    # Smaller / specialist towns frequently seen in estate agent URLs
    "aldeburgh", "alresford", "amersham", "arundel", "bakewell",
    "battle", "bembridge", "beaconsfield", "berkhamsted", "bexhill",
    "biggin hill", "bishops cleeve", "bordon", "brockenhurst",
    "bruton", "burford", "burnham on sea", "calne", "chalfont",
    "chipping campden", "cirencester", "cobham", "cowes",
    "cranbrook", "crowborough", "cuckfield", "dartmouth",
    "east grinstead", "east molesey", "esher", "epping",
    "faringdon", "farnham royal", "fordingbridge", "gerrards cross",
    "goudhurst", "hadleigh", "hailsham", "hawkhurst", "henley",
    "herstmonceux", "hertford", "hinckley", "horley", "horsforth",
    "horsham", "hungerford", "hurley", "hythe", "kings langley",
    "knaresborough", "lacock", "leatherhead", "ledbury",
    "lechlade", "limpsfield", "linton", "liphook", "liss",
    "long melford", "lymington", "lyndhurst", "maidenhead",
    "marlow", "midhurst", "nayland", "nailsworth", "newmarket",
    "northleach", "odiham", "oxted", "paddock wood", "petworth",
    "pewsey", "pulborough", "robertsbridge", "rolvenden",
    "ross on wye", "rye", "saffron walden", "sandwich",
    "sevenoaks", "shoreham", "sissinghurst", "southborough",
    "speldhurst", "steyning", "stow on the wold", "sudbury",
    "swanage", "tenterden", "tetbury", "tewkesbury", "thame",
    "tonbridge", "uckfield", "uckfield", "virginia water",
    "wadhurst", "wallingford", "wantage", "wareham", "watlington",
    "wendover", "west malling", "westbury", "westerham",
    "whitstable", "wilton", "winchelsea", "winchcombe",
    "wingham", "witney", "woodstock", "wye", "yateley",
]

# Build a fast lowercase lookup set
_UK_PLACE_SET = set(p.lower() for p in UK_TOWNS + UK_COUNTIES)

# ── Postcode area → region map (first 1-2 letters) ───────────────────
POSTCODE_AREA_REGIONS = {
    "AB": "Aberdeen", "AL": "St Albans", "B": "Birmingham",
    "BA": "Bath", "BB": "Blackburn", "BD": "Bradford",
    "BH": "Bournemouth", "BL": "Bolton", "BN": "Brighton",
    "BR": "Bromley", "BS": "Bristol", "CA": "Carlisle",
    "CB": "Cambridge", "CF": "Cardiff", "CH": "Chester",
    "CM": "Chelmsford", "CO": "Colchester", "CR": "Croydon",
    "CT": "Canterbury", "CV": "Coventry", "CW": "Crewe",
    "DA": "Dartford", "DD": "Dundee", "DE": "Derby",
    "DG": "Dumfries", "DH": "Durham", "DL": "Darlington",
    "DN": "Doncaster", "DT": "Dorchester", "DY": "Dudley",
    "E": "East London", "EC": "Central London", "EH": "Edinburgh",
    "EN": "Enfield", "EX": "Exeter", "FK": "Falkirk",
    "FY": "Blackpool", "G": "Glasgow", "GL": "Gloucester",
    "GU": "Guildford", "GY": "Guernsey", "HA": "Harrow",
    "HD": "Huddersfield", "HG": "Harrogate", "HP": "Hemel Hempstead",
    "HR": "Hereford", "HS": "Hebrides", "HU": "Hull",
    "HX": "Halifax", "IG": "Ilford", "IM": "Isle of Man",
    "IP": "Ipswich", "IV": "Inverness", "JE": "Jersey",
    "KA": "Kilmarnock", "KT": "Kingston", "KW": "Wick",
    "KY": "Kirkcaldy", "L": "Liverpool", "LA": "Lancaster",
    "LD": "Llandrindod Wells", "LE": "Leicester", "LL": "Llandudno",
    "LN": "Lincoln", "LS": "Leeds", "LU": "Luton",
    "M": "Manchester", "ME": "Medway", "MK": "Milton Keynes",
    "ML": "Motherwell", "N": "North London", "NE": "Newcastle",
    "NG": "Nottingham", "NN": "Northampton", "NP": "Newport",
    "NR": "Norwich", "NW": "North West London", "OL": "Oldham",
    "OX": "Oxford", "PA": "Paisley", "PE": "Peterborough",
    "PH": "Perth", "PL": "Plymouth", "PO": "Portsmouth",
    "PR": "Preston", "RG": "Reading", "RH": "Redhill",
    "RM": "Romford", "S": "Sheffield", "SA": "Swansea",
    "SE": "South East London", "SG": "Stevenage", "SK": "Stockport",
    "SL": "Slough", "SM": "Sutton", "SN": "Swindon",
    "SO": "Southampton", "SP": "Salisbury", "SR": "Sunderland",
    "SS": "Southend", "ST": "Stoke on Trent", "SW": "South West London",
    "SY": "Shrewsbury", "TA": "Taunton", "TD": "Galashiels",
    "TF": "Telford", "TN": "Tunbridge Wells", "TQ": "Torquay",
    "TR": "Truro", "TS": "Cleveland", "TW": "Twickenham",
    "UB": "Uxbridge", "W": "West London", "WA": "Warrington",
    "WC": "Central London", "WD": "Watford", "WF": "Wakefield",
    "WN": "Wigan", "WR": "Worcester", "WS": "Walsall",
    "WV": "Wolverhampton", "YO": "York", "ZE": "Shetland",
}

_POSTCODE_RE = re.compile(
    r"\b([A-Z]{1,2})(\d{1,2}[A-Z]?)\s*\d[A-Z]{2}\b"
)


def extract_locations_from_page(text: str, html: str) -> dict:
    """
    Dynamically extracts UK location signals from a page using three methods:
      1. Known place name matching against comprehensive built-in list
      2. Postcode detection → mapped to region/city
      3. Schema.org JSON-LD address fields
    Returns a dict with all findings.
    """
    text_lower = text.lower()

    # Method 1: match known place names
    matched_places = []
    for place in _UK_PLACE_SET:
        # Use word-boundary aware check to avoid partial matches
        pattern = r'\b' + re.escape(place) + r'\b'
        if re.search(pattern, text_lower):
            matched_places.append(place.title())

    # Method 2: postcode extraction → region lookup
    postcode_regions = []
    raw_postcodes    = []
    for m in _POSTCODE_RE.finditer(text):
        area = m.group(1)
        raw_postcodes.append(m.group(0))
        region = POSTCODE_AREA_REGIONS.get(area)
        if region and region not in postcode_regions:
            postcode_regions.append(region)

    # Method 3: Schema.org addressLocality / addressRegion
    schema_locations = []
    soup = BeautifulSoup(html, "lxml")
    for script in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(script.string or "")
            for field in ["addressLocality", "addressRegion", "addressCountry",
                          "streetAddress", "postalCode"]:
                val = (data.get("address", {}) or {}).get(field, "")
                if val and isinstance(val, str) and val.strip():
                    schema_locations.append(val.strip())
        except Exception:
            pass

    # UK property signals
    property_signals = [kw for kw in UK_PROPERTY_SIGNALS if kw.lower() in text_lower]

    return {
        "matched_places":    sorted(set(matched_places)),
        "postcode_regions":  postcode_regions,
        "raw_postcodes":     list(set(raw_postcodes))[:10],
        "schema_locations":  schema_locations,
        "property_signals":  property_signals,
        # Combined unique signal count for scoring
        "total_signals":     len(set(matched_places)) + len(postcode_regions)
                             + len(schema_locations) + len(property_signals),
    }


# Legacy alias so existing call sites still work without changes
LOCAL_KEYWORDS = UK_PROPERTY_SIGNALS  # used only as fallback in scoring

# ── Service keyword map ───────────────────────────────────────────────
SERVICE_KEYWORDS = {
    "Sales": [
        "property for sale", "homes for sale", "buy a home", "buying",
        "sales", "sell your home", "sell your property", "house sales",
        "residential sales", "for sale"
    ],
    "Lettings / Rentals": [
        "lettings", "to let", "rental", "rent a property", "renting",
        "landlord", "tenant", "let your property", "property to rent",
        "managed let", "let only"
    ],
    "New Homes": [
        "new homes", "new build", "new development", "off-plan",
        "newly built", "new properties", "show home", "plot"
    ],
    "Auctions": [
        "auction", "property auction", "unconditional", "conditional auction",
        "bid", "lot number", "guide price", "reserve price"
    ],
    "Valuations": [
        "free valuation", "book a valuation", "property valuation",
        "market appraisal", "instant valuation", "online valuation",
        "how much is my home worth"
    ],
    "Property Management": [
        "property management", "managed service", "full management",
        "maintenance", "repair", "rent collection", "block management"
    ],
    "Commercial": [
        "commercial property", "office space", "retail", "industrial",
        "commercial lettings", "commercial sales", "business premises"
    ],
    "Land & Development": [
        "land", "development site", "planning permission",
        "development opportunity", "land for sale"
    ],
    "Mortgages / Financial": [
        "mortgage", "financial advice", "conveyancing", "solicitor",
        "stamp duty", "mortgage broker", "financial services"
    ],
    "International": [
        "international", "overseas property", "foreign investment",
        "global", "abroad"
    ],
    "Surveys": [
        "survey", "homebuyer report", "structural survey",
        "rics survey", "valuation survey"
    ],
    "Short Lets / Holidays": [
        "short let", "holiday let", "airbnb", "serviced apartment",
        "temporary accommodation"
    ],
}

SERVICE_URL_PATTERNS = {
    "Sales":               ["/sales", "/buy", "/for-sale", "/residential-sales"],
    "Lettings / Rentals":  ["/lettings", "/rent", "/to-let", "/rental"],
    "New Homes":           ["/new-homes", "/new-builds", "/developments"],
    "Auctions":            ["/auction", "/auctions"],
    "Valuations":          ["/valuation", "/appraisal", "/value-my-home"],
    "Commercial":          ["/commercial"],
    "Land & Development":  ["/land", "/development"],
    "Mortgages":           ["/mortgages", "/financial", "/conveyancing"],
    "Surveys":             ["/surveys", "/survey"],
    "Property Management": ["/management", "/property-management"],
}

CTA_KEYWORDS = [
    "book a valuation", "book valuation", "get a valuation",
    "contact us", "get in touch", "enquire now", "enquire",
    "register", "register interest", "sign up",
    "request a callback", "call us", "book a viewing",
    "arrange a viewing", "find a property", "search properties",
    "instant valuation", "online valuation", "free valuation",
    "sell your home", "let your property", "list your property",
    "download", "get started", "learn more", "view properties",
    "book now", "apply now"
]

TRACKING_PATTERNS = {
    "Google Analytics 4":   [r"gtag\(", r"G-[A-Z0-9]{6,12}", r"google-analytics\.com/g/"],
    "Google Analytics UA":  [r"UA-\d{5,10}-\d", r"ga\("],
    "Google Tag Manager":   [r"GTM-[A-Z0-9]{5,8}", r"googletagmanager\.com"],
    "Meta / Facebook Pixel":[r"fbq\(", r"facebook\.net/en_US/fbevents"],
    "Hotjar":               [r"hotjar\.com", r"hj\(window"],
    "HubSpot":              [r"hubspot\.com", r"hs-scripts\.com"],
    "Intercom":             [r"intercom\.io", r"intercomSettings"],
    "Drift":                [r"drift\.com", r"driftt\.com"],
    "Clarity (Microsoft)":  [r"clarity\.ms"],
    "LinkedIn Insight":     [r"snap\.licdn\.com", r"linkedin insight"],
    "Tiktok Pixel":         [r"tiktok\.com/i18n/pixel"],
}

TRUST_SIGNALS = {
    "Reviews":      ["reviews", "rated", "stars", "trustpilot", "google reviews", "feefo",
                     "allagents", "5 star", "five star", "review"],
    "Awards":       ["award", "winner", "accredited", "recognised", "best agent",
                     "award-winning", "gold", "silver", "shortlisted"],
    "Testimonials": ["testimonial", "what our clients say", "customer stories",
                     "what our customers say", "client feedback", "hear from"],
    "Memberships":  ["rics", "naea", "arla", "propertymark", "ombudsman",
                     "tpos", "nals", "safeagent", "client money protect"],
    "Guarantees":   ["no sale no fee", "money back", "guarantee", "promise",
                     "no let no fee", "fixed fee"],
    "Social Proof": ["follow us", "facebook", "instagram", "linkedin", "twitter",
                     "youtube", "social media"],
}

REVIEW_PLATFORMS = {
    "Trustpilot":     "trustpilot.com",
    "Google Reviews": "maps.googleapis.com",
    "Feefo":          "feefo.com",
    "AllAgents":      "allagents.co.uk",
    "Bark":           "bark.com",
    "Reviews.io":     "reviews.io",
}

AI_CRAWLERS = [
    "GPTBot", "ChatGPT-User", "ClaudeBot", "Claude-Web",
    "CCBot", "Googlebot", "Bingbot", "anthropic-ai",
    "PerplexityBot", "YouBot"
]

WCAG_HEADING_ORDER = ["h1", "h2", "h3", "h4", "h5", "h6"]


# ══════════════════════════════════════════════════════════════════════
#  PHASE 1 — EMAIL SCRAPER (Playwright / headless Chromium)
# ══════════════════════════════════════════════════════════════════════

def _email_clean(email: str) -> str:
    return email.rstrip(".,;:\"'")

def _email_valid(email: str) -> bool:
    e = email.lower()
    if any(e.endswith(f"@{d}") for d in IGNORE_DOMAINS):
        return False
    tld = e.rsplit(".", 1)[-1]
    return tld not in IGNORE_TLDS

def _email_extract(text: str) -> set:
    return {_email_clean(m).lower()
            for m in EMAIL_REGEX.findall(text)
            if _email_valid(_email_clean(m))}


async def _scrape_emails_for_url(url: str, page) -> dict:
    result = {"url": url, "emails": set(), "status": ""}
    try:
        await page.goto(url, wait_until="networkidle", timeout=30_000)
        await asyncio.sleep(2)
        html = await page.content()
        result["status"] = "OK"
    except Exception as exc:
        result["status"] = f"ERROR: {exc}"
        return result

    soup = BeautifulSoup(html, "html.parser")

    for a in soup.find_all("a", href=True):
        href = a["href"]
        if href.startswith("mailto:"):
            email = _email_clean(href[7:].split("?")[0].strip())
            if email and _email_valid(email):
                result["emails"].add(email.lower())

    result["emails"].update(_email_extract(soup.get_text(" ")))
    result["emails"].update(_email_extract(html))
    return result


async def run_email_scraper(urls: list) -> dict:
    """
    Returns: {domain: [email, ...], ...}  and also prints a summary.
    """
    print("\n" + "═" * 62)
    print("  PHASE 1 — EMAIL SCRAPER  (headless Chromium / Playwright)")
    print("═" * 62)

    all_emails: dict[str, list] = {}

    if not HAS_PLAYWRIGHT:
        print("  ⚠️  Playwright not available — skipping email phase.\n")
        return all_emails

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
            locale="en-GB",
        )
        page = await context.new_page()

        for url in urls:
            domain = urlparse(url).netloc
            print(f"\n  🔍  {domain}")
            result = await _scrape_emails_for_url(url, page)
            print(f"      Status: {result['status']}")
            if result["emails"]:
                for email in sorted(result["emails"]):
                    print(f"      ✉   {email}")
                    all_emails.setdefault(email, []).append(domain)
            else:
                print("      — no emails found")

        await browser.close()

    print("\n" + "─" * 62)
    print("  EMAIL SUMMARY — unique addresses found")
    print("─" * 62)
    if all_emails:
        for email, sources in sorted(all_emails.items()):
            print(f"  {email}  [{', '.join(sources)}]")
    else:
        print("  None found.")

    return all_emails


# ══════════════════════════════════════════════════════════════════════
#  PHASE 2 — FULL AUDIT HELPERS
# ══════════════════════════════════════════════════════════════════════

def print_section(title):
    print(f"\n  {'─'*54}")
    print(f"  {title}")
    print(f"  {'─'*54}")


def print_check(label, status, detail=""):
    icon = "✅" if status == "pass" else "⚠️ " if status == "warn" else "❌"
    detail_str = f"  → {detail}" if detail else ""
    print(f"    {icon}  {label:<40}{detail_str}")


def fetch_page(url):
    try:
        start   = time.time()
        resp    = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        elapsed = round((time.time() - start) * 1000)
        return resp.text, resp.status_code, elapsed, resp.headers
    except Exception:
        return None, 0, 0, {}


def get_base_url(url):
    parsed = urlparse(url)
    return f"{parsed.scheme}://{parsed.netloc}"


def extract_zones(html):
    soup = BeautifulSoup(html, "lxml")
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    def zone_text(tags):
        return " ".join(t.get_text(" ", strip=True) for t in tags)

    return {
        "navigation": zone_text(
            soup.find_all(["nav", "header"]) +
            soup.find_all(class_=re.compile(r"nav|menu|header", re.I))
        ),
        "footer":   zone_text(
            soup.find_all("footer") +
            soup.find_all(class_=re.compile(r"footer", re.I))
        ),
        "headings": zone_text(soup.find_all(["h1", "h2", "h3"])),
        "body":     soup.get_text(" ", strip=True),
    }


def get_all_nav_links(html, base_url):
    soup  = BeautifulSoup(html, "lxml")
    links = []
    for a in soup.find_all("a", href=True):
        text = a.get_text(strip=True).lower()
        href = a["href"].lower()
        if len(text) < 60 and text:
            links.append({
                "text":     text,
                "href":     href,
                "full_url": urljoin(base_url, a["href"])
            })
    return links


# ── Module 1 — Meta & Schema ──────────────────────────────────────────

def audit_meta(html, url):
    soup    = BeautifulSoup(html, "lxml")
    results = {}

    title_tag = soup.find("title")
    title     = title_tag.get_text(strip=True) if title_tag else ""
    results["title"]        = title
    results["title_length"] = len(title)
    results["title_ok"]     = 10 <= len(title) <= 70

    desc_tag = soup.find("meta", attrs={"name": re.compile("description", re.I)})
    desc     = desc_tag.get("content", "").strip() if desc_tag else ""
    results["meta_description"]        = desc
    results["meta_description_length"] = len(desc)
    results["meta_description_ok"]     = 50 <= len(desc) <= 160

    og = {}
    for tag in soup.find_all("meta", attrs={"property": re.compile("^og:", re.I)}):
        og[tag.get("property")] = tag.get("content", "")
    results["open_graph"] = og

    tc = {}
    for tag in soup.find_all("meta", attrs={"name": re.compile("^twitter:", re.I)}):
        tc[tag.get("name")] = tag.get("content", "")
    results["twitter_card"] = tc

    canonical = soup.find("link", rel="canonical")
    results["canonical"] = canonical["href"] if canonical else ""

    schemas = []
    for script in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(script.string or "")
            schemas.append({
                "type":    data.get("@type", "Unknown"),
                "rating":  data.get("ratingValue") or
                           data.get("aggregateRating", {}).get("ratingValue"),
                "reviews": data.get("reviewCount") or
                           data.get("aggregateRating", {}).get("reviewCount"),
            })
        except Exception:
            pass
    results["schema_types"] = [s["type"] for s in schemas]
    results["schema_data"]  = schemas

    h1s = soup.find_all("h1")
    results["h1_count"] = len(h1s)
    results["h1_text"]  = [h.get_text(strip=True) for h in h1s]
    return results


def print_meta_audit(data):
    print_section("META DATA & SCHEMA")
    tl = data["title_length"]
    print_check("Page Title",
                "pass" if data["title_ok"] else "warn",
                f'"{data["title"][:60]}" ({tl} chars)')
    dl = data["meta_description_length"]
    print_check("Meta Description",
                "pass" if data["meta_description_ok"] else "warn",
                f"{dl} chars {'✓' if data['meta_description_ok'] else '(ideal: 50-160)'}")
    print_check("Open Graph Tags",
                "pass" if data["open_graph"] else "fail",
                f"{len(data['open_graph'])} tags found")
    print_check("Twitter Card",
                "pass" if data["twitter_card"] else "warn",
                f"{len(data['twitter_card'])} tags found")
    print_check("Canonical URL",
                "pass" if data["canonical"] else "warn",
                data["canonical"][:60] if data["canonical"] else "Missing")
    print_check("Schema / JSON-LD",
                "pass" if data["schema_types"] else "warn",
                ", ".join(data["schema_types"]) if data["schema_types"] else "None found")
    h1c = data["h1_count"]
    print_check("H1 Tag",
                "pass" if h1c == 1 else "warn",
                f'{h1c} found — "{data["h1_text"][0][:50]}"' if data["h1_text"] else f"{h1c} found")


# ── Module 2 — Robots.txt ─────────────────────────────────────────────

def audit_robots(base_url):
    robots_url = urljoin(base_url, "/robots.txt")
    results    = {"url": robots_url, "found": False, "crawlers": {}, "sitemap": ""}
    try:
        resp = requests.get(robots_url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        if resp.status_code == 200:
            results["found"]   = True
            results["content"] = resp.text
            text_lower         = resp.text.lower()
            for crawler in AI_CRAWLERS:
                cl = crawler.lower()
                if cl in text_lower:
                    pattern = rf"user-agent:\s*{re.escape(cl)}.*?(?:disallow:\s*(/[^\n]*)|allow:\s*(/[^\n]*))"
                    match   = re.search(pattern, text_lower, re.DOTALL)
                    if match:
                        disallowed = match.group(1)
                        results["crawlers"][crawler] = (
                            "BLOCKED" if disallowed and disallowed.strip() in ["/", "/*"]
                            else "PARTIALLY BLOCKED"
                        )
                    else:
                        results["crawlers"][crawler] = "MENTIONED"
                else:
                    results["crawlers"][crawler] = "NOT MENTIONED (allowed by default)"
            sm_match = re.search(r"sitemap:\s*(\S+)", resp.text, re.I)
            if sm_match:
                results["sitemap"] = sm_match.group(1)
    except Exception:
        pass
    return results


def print_robots_audit(data):
    print_section("ROBOTS.TXT & AI CRAWLER INDEXING")
    print_check("robots.txt found",
                "pass" if data["found"] else "fail",
                data["url"])
    print_check("Sitemap declared",
                "pass" if data["sitemap"] else "warn",
                data["sitemap"] or "Not found in robots.txt")
    if data["found"]:
        print(f"\n    AI Crawler Status:")
        for crawler, status in data["crawlers"].items():
            icon = "🔴" if "BLOCKED" in status else "🟢"
            print(f"      {icon}  {crawler:<20}  {status}")


# ── Module 3 — CTAs ───────────────────────────────────────────────────

def audit_ctas(html):
    soup    = BeautifulSoup(html, "lxml")
    results = {"buttons": [], "links": [], "forms": 0, "keywords_found": []}
    for btn in soup.find_all(["button", "input"]):
        text = btn.get_text(strip=True) or btn.get("value", "") or btn.get("placeholder", "")
        if text and len(text) < 80:
            results["buttons"].append(text)
    for a in soup.find_all("a", href=True):
        text = a.get_text(strip=True)
        if text and len(text) < 80:
            for kw in CTA_KEYWORDS:
                if kw.lower() in text.lower():
                    results["links"].append(text)
                    results["keywords_found"].append(kw)
                    break
    results["forms"] = len(soup.find_all("form"))
    page_text = html.lower()
    for kw in CTA_KEYWORDS:
        if kw.lower() in page_text and kw not in results["keywords_found"]:
            results["keywords_found"].append(kw)
    results["keywords_found"] = list(set(results["keywords_found"]))
    return results


def print_cta_audit(data):
    print_section("CALLS TO ACTION (CTAs)")
    kw_count = len(data["keywords_found"])
    print_check("CTA keywords found",
                "pass" if kw_count >= 3 else "warn",
                f"{kw_count} found: {', '.join(data['keywords_found'][:5])}")
    print_check("Forms on page",
                "pass" if data["forms"] > 0 else "warn",
                f"{data['forms']} form(s) found")
    print_check("CTA buttons/links",
                "pass" if data["links"] else "warn",
                f"{len(data['links'])} CTA link(s): {', '.join(data['links'][:3])}")


# ── Module 4 — Accessibility ──────────────────────────────────────────

def audit_accessibility(html):
    soup    = BeautifulSoup(html, "lxml")
    results = {}
    all_imgs    = soup.find_all("img")
    missing_alt = [img.get("src", "")[:60] for img in all_imgs
                   if not img.get("alt") and img.get("src")]
    results["total_images"] = len(all_imgs)
    results["missing_alt"]  = missing_alt
    results["alt_pass"]     = len(missing_alt) == 0

    inputs     = soup.find_all(["input", "select", "textarea"])
    inputs     = [i for i in inputs if i.get("type") not in ["hidden", "submit", "button"]]
    unlabelled = []
    for inp in inputs:
        inp_id    = inp.get("id")
        has_label = (
            (inp_id and soup.find("label", attrs={"for": inp_id})) or
            inp.find_parent("label") or inp.get("aria-label") or
            inp.get("aria-labelledby") or inp.get("placeholder")
        )
        if not has_label:
            unlabelled.append(inp.get("name") or inp.get("type") or "unknown")
    results["unlabelled_inputs"] = unlabelled
    results["form_labels_ok"]    = len(unlabelled) == 0

    headings = []
    for level in WCAG_HEADING_ORDER:
        for h in soup.find_all(level):
            headings.append((level, h.get_text(strip=True)[:60]))
    results["headings"]      = headings
    results["heading_count"] = len(headings)

    results["has_skip_nav"] = bool(
        soup.find("a", href="#main") or
        soup.find("a", href="#content") or
        soup.find("a", string=re.compile("skip", re.I))
    )
    html_tag = soup.find("html")
    results["lang_attr"]    = html_tag.get("lang", "") if html_tag else ""
    results["aria_main"]    = bool(soup.find(attrs={"role": "main"}) or soup.find("main"))
    results["aria_nav"]     = bool(soup.find(attrs={"role": "navigation"}) or soup.find("nav"))
    results["aria_banner"]  = bool(soup.find(attrs={"role": "banner"}) or soup.find("header"))
    return results


def print_accessibility_audit(data):
    print_section("ACCESSIBILITY (WCAG 2.1 AA)")
    missing = len(data["missing_alt"])
    total   = data["total_images"]
    print_check("Image alt tags",
                "pass" if data["alt_pass"] else "fail",
                f"{total - missing}/{total} images have alt text"
                + (f" — missing: {data['missing_alt'][0]}" if missing else ""))
    print_check("Form input labels",
                "pass" if data["form_labels_ok"] else "warn",
                "All inputs labelled" if data["form_labels_ok"]
                else f"Missing labels: {', '.join(data['unlabelled_inputs'][:3])}")
    print_check("HTML lang attribute",
                "pass" if data["lang_attr"] else "fail",
                data["lang_attr"] or "Missing — required for screen readers")
    print_check("ARIA main landmark",
                "pass" if data["aria_main"] else "warn",
                "Found" if data["aria_main"] else "Missing <main> or role=main")
    print_check("ARIA navigation",
                "pass" if data["aria_nav"] else "warn",
                "Found" if data["aria_nav"] else "Missing <nav> or role=navigation")
    print_check("Skip navigation link",
                "pass" if data["has_skip_nav"] else "warn",
                "Found" if data["has_skip_nav"] else "Not found (keyboard users affected)")
    print_check("Heading structure",
                "pass" if data["heading_count"] > 0 else "fail",
                f"{data['heading_count']} headings found")


# ── Module 5 — Tracking ───────────────────────────────────────────────

def audit_tracking(html):
    results = {}
    for tracker, patterns in TRACKING_PATTERNS.items():
        found = any(re.search(p, html, re.I) for p in patterns)
        if found:
            ids = []
            for p in patterns:
                matches = re.findall(p, html, re.I)
                ids.extend(m for m in matches if isinstance(m, str) and len(m) > 3)
            results[tracker] = {"found": True, "ids": list(set(ids))[:3]}
    return results


def print_tracking_audit(data):
    print_section("TRACKING & ANALYTICS SETUP")
    critical = ["Google Analytics 4", "Google Tag Manager", "Meta / Facebook Pixel"]
    for tracker in critical:
        info = data.get(tracker)
        print_check(tracker,
                    "pass" if info else "warn",
                    f"IDs: {', '.join(info['ids'])}" if info and info["ids"]
                    else ("Detected" if info else "Not found"))
    others = [t for t in data if t not in critical]
    if others:
        print(f"\n    Additional trackers found:")
        for t in others:
            print(f"      ➕  {t}")


# ── Module 6 — Content ────────────────────────────────────────────────

def audit_content(html):
    soup = BeautifulSoup(html, "lxml")
    for tag in soup(["script", "style"]):
        tag.decompose()
    text    = " ".join(soup.get_text(" ", strip=True).split())
    results = {}
    results["word_count"] = len(text.split())
    if HAS_TEXTSTAT:
        results["flesch_ease"]  = round(textstat.flesch_reading_ease(text), 1)
        results["flesch_grade"] = round(textstat.flesch_kincaid_grade(text), 1)
        results["fog_index"]    = round(textstat.gunning_fog(text), 1)
    else:
        results["flesch_ease"] = results["flesch_grade"] = results["fog_index"] = None
    if HAS_LANGDETECT and len(text) > 50:
        try:
            results["language"] = langdetect_detect(text[:2000])
        except Exception:
            results["language"] = "unknown"
    else:
        results["language"] = "unknown"

    # ── Dynamic UK location detection ────────────────────────────────
    loc = extract_locations_from_page(text, html)
    results["location_data"]  = loc
    results["local_keywords"] = loc["property_signals"]   # legacy compat
    results["has_gbp"]        = bool(re.search(r"£[\d,]", text))
    results["has_phone_uk"]   = bool(re.search(r"0\d{3,4}[\s\-]\d{6,7}", text))
    results["has_postcode"]   = bool(loc["raw_postcodes"])

    words               = re.findall(r"\b[a-z]{4,}\b", text.lower())
    freq                = Counter(words)
    results["top_keywords"] = freq.most_common(10)
    results["thin_content"] = results["word_count"] < 300
    return results


def print_content_audit(data):
    print_section("CONTENT QUALITY & LOCALISATION")
    wc = data["word_count"]
    print_check("Word count",
                "pass" if wc >= 300 else "warn",
                f"{wc} words {'⚠ Thin content' if data['thin_content'] else ''}")
    print_check("Language detected",
                "pass" if data["language"] == "en" else "warn",
                data["language"])

    loc = data.get("location_data", {})

    # Places detected
    places = loc.get("matched_places", [])
    print_check("UK places detected",
                "pass" if places else "warn",
                f"{len(places)} found: {', '.join(places[:6])}" if places else "None detected")

    # Postcode regions
    pc_regions = loc.get("postcode_regions", [])
    pc_raw     = loc.get("raw_postcodes", [])
    print_check("Postcodes / regions",
                "pass" if pc_raw else "warn",
                f"{len(pc_raw)} postcode(s) → {', '.join(pc_regions[:4])}"
                if pc_raw else "No postcodes found")

    # Schema address fields
    schema_locs = loc.get("schema_locations", [])
    print_check("Schema address fields",
                "pass" if schema_locs else "warn",
                ", ".join(schema_locs[:4]) if schema_locs else "None in JSON-LD")

    # Property signals
    prop_sigs = loc.get("property_signals", [])
    print_check("UK property signals",
                "pass" if len(prop_sigs) >= 3 else "warn",
                f"{len(prop_sigs)} found: {', '.join(prop_sigs[:5])}")

    print_check("UK phone number",
                "pass" if data["has_phone_uk"] else "warn",
                "Found" if data["has_phone_uk"] else "Not detected")
    print_check("UK postcode",
                "pass" if data["has_postcode"] else "warn",
                "Found" if data["has_postcode"] else "Not detected")
    print_check("GBP currency (£)",
                "pass" if data["has_gbp"] else "warn",
                "Found" if data["has_gbp"] else "Not detected")
    if data["flesch_ease"] is not None:
        fe          = data["flesch_ease"]
        readability = "Easy" if fe >= 70 else "Medium" if fe >= 50 else "Difficult"
        print_check("Readability (Flesch)",
                    "pass" if fe >= 50 else "warn",
                    f"{fe} — {readability} (Grade {data['flesch_grade']})")
    else:
        print_check("Readability", "warn", "Skipped (textstat not installed)")


# ── Module 7 — Trust ──────────────────────────────────────────────────

def audit_trust(html):
    soup    = BeautifulSoup(html, "lxml")
    text    = soup.get_text(" ", strip=True).lower()
    results = {"signals": {}, "review_platforms": [], "schema_ratings": [], "badge_images": []}
    for category, keywords in TRUST_SIGNALS.items():
        hits = [kw for kw in keywords if kw.lower() in text]
        results["signals"][category] = {"found": hits, "detected": len(hits) > 0}
    for platform, domain in REVIEW_PLATFORMS.items():
        if domain.lower() in html.lower():
            results["review_platforms"].append(platform)
    for script in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(script.string or "")
            if data.get("@type") in ["LocalBusiness", "RealEstateAgent",
                                      "Review", "AggregateRating"]:
                rating = (data.get("ratingValue") or
                          data.get("aggregateRating", {}).get("ratingValue"))
                count  = (data.get("reviewCount") or
                          data.get("aggregateRating", {}).get("reviewCount"))
                if rating:
                    results["schema_ratings"].append({
                        "type": data.get("@type"), "rating": rating, "count": count
                    })
        except Exception:
            pass
    badge_keywords = ["award", "badge", "accredited", "member", "logo", "certified",
                      "rics", "naea", "arla", "propertymark"]
    for img in soup.find_all("img"):
        alt = img.get("alt", "").lower()
        src = img.get("src", "").lower()
        if any(kw in alt or kw in src for kw in badge_keywords):
            results["badge_images"].append(alt or src.split("/")[-1])
    return results


def print_trust_audit(data):
    print_section("SOCIAL PROOF & TRUST SIGNALS")
    for category, info in data["signals"].items():
        print_check(category,
                    "pass" if info["detected"] else "warn",
                    f"Found: {', '.join(info['found'][:3])}" if info["found"] else "None detected")
    plat = data["review_platforms"]
    print_check("Review platform widgets",
                "pass" if plat else "warn",
                ", ".join(plat) if plat else "None detected")
    badges = data["badge_images"]
    print_check("Trust badge images",
                "pass" if badges else "warn",
                f"{len(badges)} found: {', '.join(badges[:3])}" if badges else "None detected")
    ratings = data["schema_ratings"]
    print_check("Schema rating markup",
                "pass" if ratings else "warn",
                (f"Rating: {ratings[0]['rating']}/5 ({ratings[0]['count']} reviews)"
                 if ratings else "Not found"))


# ── Module 8 — Services ───────────────────────────────────────────────

def audit_services(html, base_url):
    zones     = extract_zones(html)
    nav_links = get_all_nav_links(html, base_url)
    nav_text  = " ".join(f"{l['text']} {l['href']}" for l in nav_links)
    weighted  = [
        (zones["navigation"], 3),
        (zones["headings"],   2),
        (zones["footer"],     2),
        (zones["body"],       1),
    ]
    detected = {}
    for service, keywords in SERVICE_KEYWORDS.items():
        score   = 0
        matched = []
        for kw in keywords:
            kw_l = kw.lower()
            for text, weight in weighted:
                if kw_l in text.lower():
                    score += weight
                    if kw not in matched:
                        matched.append(kw)
            if kw_l in nav_text.lower():
                score += 4
                tag = f"[NAV] {kw}"
                if tag not in matched:
                    matched.append(tag)
        if score > 0:
            detected[service] = {
                "score":      score,
                "keywords":   matched[:5],
                "confidence": "High" if score >= 8 else "Medium" if score >= 4 else "Low"
            }
    service_pages = {}
    for service, patterns in SERVICE_URL_PATTERNS.items():
        matches = [
            l["full_url"] for l in nav_links
            if any(p in l["href"] for p in patterns)
        ]
        if matches:
            service_pages[service] = list(set(matches))[:2]
    return {
        "detected":      dict(sorted(detected.items(),
                                     key=lambda x: x[1]["score"], reverse=True)),
        "service_pages": service_pages
    }


def print_services_audit(data):
    print_section("SERVICES OFFERED")
    detected = data["detected"]
    if not detected:
        print("    ❌  No services detected")
        return
    for service, info in detected.items():
        if info["confidence"] in ["High", "Medium"]:
            bar  = "█" * min(info["score"], 15)
            tags = [k.replace("[NAV] ", "🔗 ") for k in info["keywords"][:3]]
            print(f"    ✅  {service:<28} [{info['confidence']:<6}]  {bar}")
            print(f"        Signals: {', '.join(tags)}")
    low = [s for s, i in detected.items() if i["confidence"] == "Low"]
    if low:
        print(f"\n    ⚠️   Low-confidence signals: {', '.join(low)}")
    if data["service_pages"]:
        print(f"\n    Dedicated service pages found:")
        for service, urls in data["service_pages"].items():
            print(f"      🔗  {service}: {urls[0]}")


# ── Module 9 — PageSpeed ──────────────────────────────────────────────

def audit_pagespeed(url):
    if not PAGESPEED_API_KEY:
        return None
    results = {}
    for strategy in ["mobile", "desktop"]:
        api_url = (
            f"https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
            f"?url={url}&strategy={strategy}&key={PAGESPEED_API_KEY}"
        )
        try:
            resp = requests.get(api_url, timeout=30)
            if resp.status_code == 200:
                data       = resp.json()
                cats       = data.get("lighthouseResult", {}).get("categories", {})
                audits     = data.get("lighthouseResult", {}).get("audits", {})
                results[strategy] = {
                    "performance":    round(cats.get("performance",    {}).get("score", 0) * 100),
                    "accessibility":  round(cats.get("accessibility",  {}).get("score", 0) * 100),
                    "seo":            round(cats.get("seo",            {}).get("score", 0) * 100),
                    "best_practices": round(cats.get("best-practices", {}).get("score", 0) * 100),
                    "fcp":  audits.get("first-contentful-paint",   {}).get("displayValue", ""),
                    "lcp":  audits.get("largest-contentful-paint", {}).get("displayValue", ""),
                    "cls":  audits.get("cumulative-layout-shift",  {}).get("displayValue", ""),
                    "tbt":  audits.get("total-blocking-time",      {}).get("displayValue", ""),
                }
        except Exception as e:
            results[strategy] = {"error": str(e)}
    return results


def print_pagespeed_audit(data):
    if data is None:
        print_section("PAGE SPEED (PageSpeed Insights)")
        print("    ⚠️   Skipped — set PAGESPEED_API_KEY to enable")
        return
    print_section("PAGE SPEED (PageSpeed Insights API)")
    for strategy, scores in data.items():
        if "error" in scores:
            print(f"    ❌  {strategy.capitalize()}: {scores['error']}")
            continue
        p = scores["performance"]
        a = scores["accessibility"]
        s = scores["seo"]
        print(f"\n    {'📱' if strategy == 'mobile' else '🖥 '} {strategy.capitalize()}:")
        print_check("Performance",
                    "pass" if p >= 70 else "warn" if p >= 50 else "fail", f"{p}/100")
        print_check("Accessibility",
                    "pass" if a >= 80 else "warn", f"{a}/100")
        print_check("SEO",
                    "pass" if s >= 80 else "warn", f"{s}/100")
        if scores.get("lcp"):
            print(f"        LCP: {scores['lcp']}  |  FCP: {scores['fcp']}  "
                  f"|  CLS: {scores['cls']}")


# ── Scoring ───────────────────────────────────────────────────────────

def calculate_score(meta, robots, ctas, access, tracking, content, trust, services):
    score = max_sc = 0

    def add(points, condition):
        nonlocal score, max_sc
        max_sc += points
        if condition:
            score += points

    add(5, meta["title_ok"])
    add(5, meta["meta_description_ok"])
    add(3, bool(meta["open_graph"]))
    add(3, bool(meta["schema_types"]))
    add(2, meta["h1_count"] == 1)
    add(3, robots["found"])
    add(3, bool(robots["sitemap"]))
    add(5, len(ctas["keywords_found"]) >= 3)
    add(3, ctas["forms"] > 0)
    add(5, access["alt_pass"])
    add(3, access["form_labels_ok"])
    add(3, bool(access["lang_attr"]))
    add(2, access["aria_main"])
    add(5, bool(tracking.get("Google Analytics 4")))
    add(3, bool(tracking.get("Google Tag Manager")))
    add(3, bool(tracking.get("Meta / Facebook Pixel")))
    add(5, not content["thin_content"])
    loc_signals = content.get("location_data", {}).get("total_signals", 0)
    add(3, loc_signals >= 5)   # richer threshold for dynamic detection
    add(2, content["has_gbp"])
    add(2, content["has_phone_uk"])
    trust_detected = sum(1 for _, i in trust["signals"].items() if i["detected"])
    add(5, trust_detected >= 3)
    add(3, bool(trust["review_platforms"]))
    confirmed = sum(1 for _, i in services["detected"].items()
                    if i["confidence"] in ["High", "Medium"])
    add(5, confirmed >= 3)

    pct = round((score / max_sc) * 100) if max_sc > 0 else 0
    return pct, score, max_sc


# ── Single site audit ─────────────────────────────────────────────────

def audit_site(url, emails_found=None):
    print(f"\n\n{'█'*62}")
    print(f"  AUDITING: {url}")
    print(f"{'█'*62}")

    html, status, load_ms, resp_headers = fetch_page(url)
    if not html:
        print(f"  ❌  Failed to fetch URL (status: {status})")
        return None

    print(f"  ⏱  Load time: {load_ms}ms  |  HTTP Status: {status}")

    # Show emails found for this domain (from Phase 1)
    if emails_found:
        domain = urlparse(url).netloc
        domain_emails = [e for e, srcs in emails_found.items() if domain in srcs]
        if domain_emails:
            print_section("EMAILS FOUND (Phase 1 Playwright scan)")
            for email in sorted(domain_emails):
                print(f"    ✉   {email}")

    base_url      = get_base_url(url)
    meta          = audit_meta(html, url)
    robots        = audit_robots(base_url)
    ctas          = audit_ctas(html)
    accessibility = audit_accessibility(html)
    tracking      = audit_tracking(html)
    content       = audit_content(html)
    trust         = audit_trust(html)
    services      = audit_services(html, base_url)
    pagespeed     = audit_pagespeed(url)

    print_meta_audit(meta)
    print_robots_audit(robots)
    print_cta_audit(ctas)
    print_accessibility_audit(accessibility)
    print_tracking_audit(tracking)
    print_content_audit(content)
    print_trust_audit(trust)
    print_services_audit(services)
    print_pagespeed_audit(pagespeed)

    score_pct, score, max_sc = calculate_score(
        meta, robots, ctas, accessibility, tracking, content, trust, services
    )
    grade = (
        "A" if score_pct >= 85 else "B" if score_pct >= 70 else
        "C" if score_pct >= 55 else "D" if score_pct >= 40 else "F"
    )
    print(f"\n  {'═'*54}")
    print(f"  OVERALL SCORE:  {score}/{max_sc}  ({score_pct}%)  Grade: {grade}")
    print(f"  {'═'*54}")

    return {
        "url": url, "status": status, "load_ms": load_ms,
        "score_pct": score_pct, "grade": grade,
        "emails": [e for e, srcs in (emails_found or {}).items()
                   if urlparse(url).netloc in srcs],
        "meta": meta, "robots": robots, "ctas": ctas,
        "accessibility": accessibility, "tracking": tracking,
        "content": content, "trust": trust,
        "services": services, "pagespeed": pagespeed,
    }


# ── Comparison report ─────────────────────────────────────────────────

def print_comparison(all_results):
    print(f"\n\n{'█'*62}")
    print(f"  COMPETITOR COMPARISON SUMMARY")
    print(f"{'█'*62}")
    print(f"\n  {'Agency':<30} {'Bar':<12} {'Score':>5} {'Grade':>5} "
          f"{'Load':>7} {'Svcs':>5} {'Tags':>5} {'Trust':>6} {'Emails':>7}")
    print(f"  {'─'*85}")

    for r in sorted(all_results, key=lambda x: x["score_pct"], reverse=True):
        name     = r["url"].split("/")[2].replace("www.", "")[:28]
        services = sum(1 for _, i in r["services"]["detected"].items()
                       if i["confidence"] in ["High", "Medium"])
        trackers = len(r["tracking"])
        trust    = sum(1 for _, i in r["trust"]["signals"].items() if i["detected"])
        emails   = len(r.get("emails", []))
        bar      = "▓" * (r["score_pct"] // 10) + "░" * (10 - r["score_pct"] // 10)
        print(f"  {name:<30} {bar}  {r['score_pct']:>3}%   {r['grade']:>2} "
              f"  {r['load_ms']:>5}ms  {services:>3}    {trackers:>2}    {trust:>2}/6  {emails:>4}✉")

    by_score    = sorted(all_results, key=lambda x: x["score_pct"], reverse=True)
    by_services = sorted(all_results,
                         key=lambda x: sum(1 for _, i in x["services"]["detected"].items()
                                           if i["confidence"] in ["High", "Medium"]),
                         reverse=True)
    by_speed    = sorted(all_results, key=lambda x: x["load_ms"])

    def name(r):
        return r["url"].split("/")[2].replace("www.", "")

    print(f"\n  🏆  Best overall score : {name(by_score[0])} ({by_score[0]['score_pct']}%)")
    print(f"  📋  Most services      : {name(by_services[0])}")
    print(f"  ⚡  Fastest load time  : {name(by_speed[0])} ({by_speed[0]['load_ms']}ms)")


# ── Exports ───────────────────────────────────────────────────────────

def export_csv(all_results, filename="audit_report.csv"):
    rows = []
    for r in all_results:
        trust_detected = sum(1 for _, i in r["trust"]["signals"].items() if i["detected"])
        services_confirmed = sum(1 for _, i in r["services"]["detected"].items()
                                 if i["confidence"] in ["High", "Medium"])
        services_list = ", ".join(
            s for s, i in r["services"]["detected"].items()
            if i["confidence"] in ["High", "Medium"]
        )
        trackers_list = ", ".join(r["tracking"].keys())
        row = {
            "URL":                      r["url"],
            "HTTP Status":              r["status"],
            "Load Time (ms)":           r["load_ms"],
            "Overall Score (%)":        r["score_pct"],
            "Grade":                    r["grade"],
            "Emails Found":             "; ".join(r.get("emails", [])),
            "Page Title":               r["meta"]["title"][:80],
            "Title Length":             r["meta"]["title_length"],
            "Title OK (10-70 chars)":   r["meta"]["title_ok"],
            "Meta Description":         r["meta"]["meta_description"][:120],
            "Meta Desc Length":         r["meta"]["meta_description_length"],
            "Meta Desc OK (50-160)":    r["meta"]["meta_description_ok"],
            "Open Graph Tags":          len(r["meta"]["open_graph"]),
            "Twitter Card Tags":        len(r["meta"]["twitter_card"]),
            "Canonical URL":            r["meta"]["canonical"][:80],
            "Schema Types":             ", ".join(r["meta"]["schema_types"]),
            "H1 Count":                 r["meta"]["h1_count"],
            "H1 Text":                  r["meta"]["h1_text"][0][:80] if r["meta"]["h1_text"] else "",
            "robots.txt Found":         r["robots"]["found"],
            "Sitemap in robots.txt":    r["robots"]["sitemap"][:100] if r["robots"]["sitemap"] else "",
            "GPTBot Status":            r["robots"]["crawlers"].get("GPTBot", ""),
            "ClaudeBot Status":         r["robots"]["crawlers"].get("ClaudeBot", ""),
            "Googlebot Status":         r["robots"]["crawlers"].get("Googlebot", ""),
            "CTA Keywords Found":       len(r["ctas"]["keywords_found"]),
            "CTA Keywords List":        ", ".join(r["ctas"]["keywords_found"][:8]),
            "Forms on Page":            r["ctas"]["forms"],
            "CTA Links Count":          len(r["ctas"]["links"]),
            "Total Images":             r["accessibility"]["total_images"],
            "Images Missing Alt":       len(r["accessibility"]["missing_alt"]),
            "Alt Tags OK":              r["accessibility"]["alt_pass"],
            "Unlabelled Inputs":        len(r["accessibility"]["unlabelled_inputs"]),
            "Form Labels OK":           r["accessibility"]["form_labels_ok"],
            "HTML Lang Attr":           r["accessibility"]["lang_attr"],
            "ARIA Main":                r["accessibility"]["aria_main"],
            "ARIA Nav":                 r["accessibility"]["aria_nav"],
            "Skip Nav Link":            r["accessibility"]["has_skip_nav"],
            "Heading Count":            r["accessibility"]["heading_count"],
            "GA4 Found":                bool(r["tracking"].get("Google Analytics 4")),
            "GTM Found":                bool(r["tracking"].get("Google Tag Manager")),
            "Meta Pixel Found":         bool(r["tracking"].get("Meta / Facebook Pixel")),
            "Hotjar Found":             bool(r["tracking"].get("Hotjar")),
            "All Trackers":             trackers_list,
            "Tracker Count":            len(r["tracking"]),
            "Word Count":               r["content"]["word_count"],
            "Thin Content (<300 words)":r["content"]["thin_content"],
            "Language Detected":        r["content"]["language"],
            "UK Places Detected":       len(r["content"].get("location_data", {}).get("matched_places", [])),
            "UK Places List":           ", ".join(r["content"].get("location_data", {}).get("matched_places", [])[:10]),
            "Postcode Regions":         ", ".join(r["content"].get("location_data", {}).get("postcode_regions", [])),
            "Raw Postcodes":            ", ".join(r["content"].get("location_data", {}).get("raw_postcodes", [])[:5]),
            "Schema Locations":         ", ".join(r["content"].get("location_data", {}).get("schema_locations", [])),
            "UK Property Signals":      len(r["content"].get("location_data", {}).get("property_signals", [])),
            "Property Signals List":    ", ".join(r["content"].get("location_data", {}).get("property_signals", [])[:8]),
            "Total Location Signals":   r["content"].get("location_data", {}).get("total_signals", 0),
            "Local Keywords Found":     len(r["content"]["local_keywords"]),
            "Local Keywords List":      ", ".join(r["content"]["local_keywords"][:8]),
            "Has GBP (£)":              r["content"]["has_gbp"],
            "Has UK Phone":             r["content"]["has_phone_uk"],
            "Has UK Postcode":          r["content"]["has_postcode"],
            "Flesch Reading Ease":      r["content"]["flesch_ease"] if r["content"]["flesch_ease"] is not None else "N/A",
            "Flesch Grade Level":       r["content"]["flesch_grade"] if r["content"]["flesch_grade"] is not None else "N/A",
            "Gunning Fog Index":        r["content"]["fog_index"] if r["content"]["fog_index"] is not None else "N/A",
            "Reviews Signals":          r["trust"]["signals"].get("Reviews", {}).get("detected", False),
            "Awards Signals":           r["trust"]["signals"].get("Awards", {}).get("detected", False),
            "Testimonials Signals":     r["trust"]["signals"].get("Testimonials", {}).get("detected", False),
            "Membership Signals":       r["trust"]["signals"].get("Memberships", {}).get("detected", False),
            "Guarantee Signals":        r["trust"]["signals"].get("Guarantees", {}).get("detected", False),
            "Social Proof Signals":     r["trust"]["signals"].get("Social Proof", {}).get("detected", False),
            "Trust Categories Found":   trust_detected,
            "Review Platforms":         ", ".join(r["trust"]["review_platforms"]),
            "Schema Ratings Found":     len(r["trust"]["schema_ratings"]),
            "Badge Images Found":       len(r["trust"]["badge_images"]),
            "Services Count":           services_confirmed,
            "Services List":            services_list,
            "Service Pages Found":      len(r["services"]["service_pages"]),
            "PS Mobile Performance":    r["pagespeed"]["mobile"]["performance"]   if r["pagespeed"] and "mobile"  in r["pagespeed"] and "error" not in r["pagespeed"]["mobile"]  else "N/A",
            "PS Mobile Accessibility":  r["pagespeed"]["mobile"]["accessibility"] if r["pagespeed"] and "mobile"  in r["pagespeed"] and "error" not in r["pagespeed"]["mobile"]  else "N/A",
            "PS Mobile SEO":            r["pagespeed"]["mobile"]["seo"]           if r["pagespeed"] and "mobile"  in r["pagespeed"] and "error" not in r["pagespeed"]["mobile"]  else "N/A",
            "PS Desktop Performance":   r["pagespeed"]["desktop"]["performance"]  if r["pagespeed"] and "desktop" in r["pagespeed"] and "error" not in r["pagespeed"]["desktop"] else "N/A",
            "PS Desktop SEO":           r["pagespeed"]["desktop"]["seo"]          if r["pagespeed"] and "desktop" in r["pagespeed"] and "error" not in r["pagespeed"]["desktop"] else "N/A",
            "PS LCP":                   r["pagespeed"]["mobile"]["lcp"]           if r["pagespeed"] and "mobile"  in r["pagespeed"] and "error" not in r["pagespeed"]["mobile"]  else "N/A",
            "Audit Timestamp":          datetime.now().strftime("%Y-%m-%d %H:%M"),
        }
        rows.append(row)

    if rows:
        with open(filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)
        print(f"  📊  CSV report saved to: {filename}")


def export_json(all_results, filename="audit_report.json"):
    def clean(obj):
        if isinstance(obj, dict):   return {k: clean(v) for k, v in obj.items()}
        if isinstance(obj, list):   return [clean(i) for i in obj]
        if isinstance(obj, tuple):  return list(obj)
        if isinstance(obj, set):    return list(obj)
        if isinstance(obj, (int, float, str, bool)) or obj is None: return obj
        return str(obj)

    report = {
        "generated":   datetime.now().isoformat(),
        "total_sites": len(all_results),
        "results":     clean(all_results)
    }
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    print(f"  💾  Full JSON report saved to: {filename}")


# ══════════════════════════════════════════════════════════════════════
#  MAIN — orchestrates both phases
# ══════════════════════════════════════════════════════════════════════

async def main_async(urls=None):
    target_urls = urls or URLS

    print("\n" + "█" * 62)
    print("  ESTATE AGENT — EMAIL SCRAPER + FULL AUDIT TOOL")
    print(f"  {datetime.now().strftime('%d %b %Y  %H:%M')}")
    print(f"  Auditing {len(target_urls)} site(s)")
    print("█" * 62)

    # ── Phase 1: Email scraping via Playwright ────────────────────────
    emails_found = await run_email_scraper(target_urls)

    # ── Phase 2: Full audit via requests ─────────────────────────────
    print("\n\n" + "═" * 62)
    print("  PHASE 2 — FULL WEBSITE AUDIT")
    print("═" * 62)

    all_results = []
    for i, url in enumerate(target_urls, 1):
        print(f"\n  [{i}/{len(target_urls)}]  {url}")
        result = audit_site(url, emails_found=emails_found)
        if result:
            all_results.append(result)
        if i < len(target_urls):
            time.sleep(REQUEST_DELAY)

    if all_results:
        print_comparison(all_results)
        export_json(all_results)
        export_csv(all_results)

    print(f"\n  ✅  Complete — {len(all_results)}/{len(target_urls)} sites audited.\n")


def main(urls=None):
    asyncio.run(main_async(urls))


if __name__ == "__main__":
    if len(sys.argv) > 1:
        main(sys.argv[1:])
    else:
        main()