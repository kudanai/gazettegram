from api.gazette_types import GazetteType
from dotenv import dotenv_values

# init dotenv
env = dotenv_values(".env")

# The types of gazette to scrape
TARGET_GAZETTE_TYPE = [
    GazetteType.MASAKKAIY,
    GazetteType.GANNAN_BEYNUNVAA,
    GazetteType.VAZEEFAA,
    GazetteType.THAMREENU,
    GazetteType.BEELAN
]

# Base URL for the gazette website
BASE_URL = "https://gazette.gov.mv"

# Path to the SQLite database
DATABASE_PATH = "gazette.db"

# Concurrency settings
MAX_CONCURRENT_REQUESTS = 5  # Number of parallel requests to the server
REQUEST_DELAY = 4  # Delay in seconds between batches of requests to avoid overloading the server

# Set a maximum number of index pages to fetch. Set to None for no limit.
MAX_INDEX_PAGES = 10

# keyword score cutoff for the classifier
KEYWORD_SCORE_CUTOFF = 12

# Telegram bot configuration
TG_TOKEN = env["TG_BOT_TOKEN"]
TG_CHAT_ID = env["TG_CHAT_ID"]
TG_ADMIN_CHATID = env["TG_ADMIN_CHATID"]
TG_URL_SEND = f"https://api.telegram.org/{TG_TOKEN}/sendMessage"

# keyword score map for the classifier
KEYWORD_MAP = {

    # --- ICT & Tech Specific Terms (Contextual Keywords) ---
    "TECH_HARDWARE": {
        "weight": 3,
        "terms": ["ކޮމްޕިއުޓަރ", "ލެޕްޓޮޕް", "ސާވަރ", "ނެޓްވޯކް", "ޕްރިންޓަރ", "ސްވިޗް"]
    },
    "TECH_SOFTWARE": {
        "weight": 4, # Higher weight as it's a very strong signal
        "terms": ["ސޮފްޓްވެއަރ", "ވެބްސައިޓް", "އެޕްލިކޭޝަން", "ސިސްޓަމް", "ޑޭޓާބޭސް", "ޑިވެލޮޕްމަންޓް", "ޑިސައިން"]
    },
    "TECH_ROLES": {
        "weight": 4,
        "terms": ["ޑިވެލޮޕަރ", "ޕްރޮގްރާމަރ", "އެޑްމިނިސްޓްރޭޓަރ", "އިންޖިނިއަރ", "ޓެކްނީޝަން"]
    },
    "TECH_FIELD": {
        "weight": 3,
        "terms": ["އިންފޮމޭޝަން ޓެކްނޮލޮޖީ", "އައިޓީ", "ކޮމްޕިއުޓަރ ސައިންސް", "ސައިބަރ ސެކިއުރިޓީ"]
    },

    # --- Negative Keywords (To reduce false positives) ---
    "NEGATIVE_CONTEXT": {
        "weight": -5,
        "terms": [
            "ޢިމާރާތް", "ކޮންސްޓްރަކްޝަން", "ވެހިކަލް",
            "މެޑިކަލް", "ފަރުނީޗަރ"
        ]
    }
}
