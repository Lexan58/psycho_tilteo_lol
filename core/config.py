import os
from dotenv import load_dotenv
load_dotenv()

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

RIOT_API_KEY = os.getenv("RIOT_API_KEY")
REGION = os.getenv("REGION", "la1")

# Validación defensiva (Buena práctica de ciberseguridad)
if not RIOT_API_KEY:
    print("⚠️ ADVERTENCIA: La variable RIOT_API_KEY no está configurada en el archivo .env")