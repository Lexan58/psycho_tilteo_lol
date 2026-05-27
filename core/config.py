import os

# =========================
# DATABASE
# =========================

DB_PATH = os.path.join("data", "tilteo.db")


# =========================
# MENTAL THRESHOLDS
# =========================

MENTAL_THRESHOLDS = {
    "low": {
        "low": 2.5,
        "medium": 4.5
    },

    "medium": {
        "low": 3.0,
        "medium": 6.0
    },

    "high": {
        "low": 4.0,
        "medium": 7.0
    }
}


# =========================
# GAME SETTINGS
# =========================

RECENT_MATCHES_ANALYZED = 5

DEFAULT_STRESS_CHAMPIONS = [
    "Yasuo",
    "Draven",
    "Riven"
]


# =========================
# STREAMLIT
# =========================

DASHBOARD_TITLE = "🧠 Psycho Tilt LoL"


# =========================
# RIOT API
# =========================

RIOT_API_KEY = ""
REGION = "la2"