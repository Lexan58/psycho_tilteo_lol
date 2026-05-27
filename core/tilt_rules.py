import sqlite3
from datetime import datetime
from core.player_profile import PLAYER_PROFILE
from core.config import MENTAL_THRESHOLDS

def hour_risk_factor(hour):
    if hour >= 0 and hour <= 6:
        return 2      # alto riesgo
    elif hour >= 22:
        return 1      # riesgo medio
    return 0          # riesgo bajo

# ===== AJUSTE 1: TOLERANCIA AL TILT =====
def tolerance_modifier(tolerance):
    if tolerance == "low":
        return 1.2
    elif tolerance == "high":
        return 0.8
    return 1.0


# Paso 1
"""def detect_tilt_state(avg_tilt, losses_in_row):
    if avg_tilt >= 7 and losses_in_row >= 2:
        return "high"
    elif avg_tilt >= 4:
        return "medium"
    return "low"""


# Paso 3 (datos)
def get_recent_tilt_data(last_n=5):
    conn = sqlite3.connect("data/tilteo.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT tilt_level, result
        FROM matches
        ORDER BY id DESC
        LIMIT ?
    """, (last_n,))

    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return None, None

    avg_tilt = sum(r[0] for r in rows) / len(rows)

    losses = 0
    for r in rows:
        if r[1].upper() == "L":
            losses += 1
        else:
            break

    return avg_tilt, losses


# Paso 2
def anti_tilt_advice(tilt_state):
    if tilt_state == "high":
        return {
            "message": "Nivel alto de frustración detectado.",
            "action": "Pausa 10–15 min. Juega ARAM o cambia de juego.",
            "reason": "Reducir activación emocional evita decisiones impulsivas."
        }

    elif tilt_state == "medium":
        return {
            "message": "Atención: concentración inestable.",
            "action": "Evita ranked. Enfócate en un solo objetivo.",
            "reason": "Reducir carga cognitiva ayuda a recuperar control."
        }

    return {
        "message": "Estado mental estable.",
        "action": "Puedes seguir jugando.",
        "reason": "Buen equilibrio emocional."
    }

#Reglas anti tilteo

#Fatiga por volumen reciente
def fatigue_factor(matches_played_recent):
    if matches_played_recent >= 6:
        return 2
    elif matches_played_recent >= 4:
        return 1
    return 0

#Puntaje mental total

def mental_score(avg_tilt, losses, hour, matches_recent, champion=None):
    score = avg_tilt * 0.6
    score += losses * 1.2

    if matches_recent >= 3:
        score += 1

    if hour >= 23 or hour <= 4:
        score += 1

    # NUEVO: campeón como factor emocional
    if champion and champion in PLAYER_PROFILE["stress_champions"]:
        score += 1.5

    return score

#Interpretación del score
def mental_state_from_score(score, thresholds):
    if score < thresholds["low"]:
        return "low"
    elif score < thresholds["medium"]:
        return "medium"
    else:
        return "high"

#Consejos 
def advanced_anti_tilt_advice(state):
    if state == "critical":
        return {
            "message": "Estado crítico detectado.",
            "action": "Cierra ranked. Actividad física ligera o descanso.",
            "reason": "Alta carga emocional + fatiga reducen el juicio."
        }

    if state == "high":
        return {
            "message": "Frustración acumulada.",
            "action": "ARAM, modo normal o pausa corta.",
            "reason": "Reducir exigencia restaura control."
        }

    if state == "medium":
        return {
            "message": "Riesgo moderado.",
            "action": "Define un solo objetivo por partida.",
            "reason": "Menos variables = más foco."
        }

    return {
        "message": "Buen estado mental.",
        "action": "Juega normalmente.",
        "reason": "Equilibrio emocional adecuado."
    }

#Umbrales dinámicos
def get_dynamic_thresholds(tolerance):
    if tolerance == "low":
        return {"low": 3, "medium": 6}
    elif tolerance == "high":
        return {"low": 5, "medium": 8}
    return {"low": 4, "medium": 7}

def evaluate_mental_state(avg_tilt, losses, hour, matches_recent, last_champion):
    score = mental_score(avg_tilt, losses, hour, matches_recent, last_champion)

    thresholds = get_dynamic_thresholds(
        PLAYER_PROFILE["tilt_tolerance"]
    )

    state = mental_state_from_score(score, thresholds)

    advice = advanced_anti_tilt_advice(state)

    return score, state, advice


def ranked_access_decision(state):
    state = state.upper()

    if state == "HIGH":
        return {
            "allowed": False,
            "message": "🚫 Ranked bloqueado temporalmente.",
            "reason": "Estado emocional alto aumenta decisiones impulsivas.",
            "alternative": "ARAM, normales o pausa de 20–30 minutos."
        }

    if state == "MEDIUM":
        return {
            "allowed": True,
            "message": "⚠️ Ranked permitido con precaución.",
            "reason": "Riesgo moderado de frustración.",
            "alternative": "Define un solo objetivo por partida."
        }

    return {
        "allowed": True,
        "message": "✅ Ranked permitido.",
        "reason": "Estado mental estable.",
        "alternative": None
    }

