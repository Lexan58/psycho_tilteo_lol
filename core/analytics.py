import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

def tilt_by_result():
    conn = sqlite3.connect("data/tilteo.db")
    df = pd.read_sql("SELECT result, tilt_level FROM matches", conn)
    conn.close()

    if df.empty:
        print("❌ No hay datos aún.")
        return

def tilt_by_hour():
    conn = sqlite3.connect("data/tilteo.db")
    df = pd.read_sql("SELECT date, tilt_level FROM matches", conn)
    conn.close()

    if df.empty:
        print("❌ No hay datos aún.")
        return

# Convertir a datetime y extraer hora
    df["date"] = pd.to_datetime(df["date"])
    df["hour"] = df["date"].dt.hour

    grouped = df.groupby("hour")["tilt_level"].mean()

    grouped.plot(kind="line", marker="o")
    plt.title("Tilt promedio por hora del día")
    plt.xlabel("Hora del día")
    plt.ylabel("Tilt promedio")
    plt.xticks(range(0, 24))
    plt.grid(True)
    plt.show()

def winrate_vs_tilt():
    conn = sqlite3.connect("data/tilteo.db")
    df = pd.read_sql("SELECT tilt_level, result FROM matches", conn)
    conn.close()

    if df.empty:
        print("❌ No hay datos aún.")
        return

# Normalizar resultado
    df["win"] = df["result"].apply(lambda x: 1 if x.upper() == "W" else 0)

    grouped = df.groupby("tilt_level")["win"].mean() * 100

    grouped.plot(kind="bar")
    plt.title("Winrate según nivel de tilt")
    plt.xlabel("Nivel de tilt")
    plt.ylabel("Winrate (%)")
    plt.ylim(0, 100)
    plt.show()

# tilt por campeón
def tilt_by_champion():
    conn = sqlite3.connect("data/tilteo.db")
    df = pd.read_sql("SELECT champion, tilt_level FROM matches", conn)
    conn.close()

    if df.empty:
        print("❌ No hay datos aún.")
        return

    grouped = (
        df.groupby("champion")["tilt_level"]
        .mean()
        .sort_values(ascending=False)
    )

    grouped.plot(kind="bar")
    plt.title("Tilt promedio por campeón")
    plt.xlabel("Campeón")
    plt.ylabel("Tilt promedio")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.show()

def tilt_heatmap_by_hour():
    conn = sqlite3.connect("data/tilteo.db")
    df = pd.read_sql("SELECT date, tilt_level FROM matches", conn)
    conn.close()

    if df.empty:
        print("❌ No hay datos aún.")
        return

    # Procesar fecha y hora
    df["date"] = pd.to_datetime(df["date"])
    df["hour"] = df["date"].dt.hour

# Crear tabla para heatmap
    pivot = df.pivot_table(
        values="tilt_level",
        index="hour",
        aggfunc="mean"
    )

    plt.figure(figsize=(8, 6))
    plt.imshow(pivot, aspect="auto")
    plt.colorbar(label="Tilt promedio")

    plt.title("Heatmap de Tilt por Hora del Día")
    plt.xlabel("Tilt")
    plt.ylabel("Hora del día")
    plt.yticks(range(len(pivot.index)), pivot.index)

    plt.tight_layout()
    plt.show()

#Paso de evolución mental
import matplotlib.pyplot as plt
from datetime import datetime

def plot_mental_timeline(data):
    if not data:
        print("❌ No hay datos para graficar.")
        return

    timestamps = [datetime.fromisoformat(row[0]) for row in data]
    scores = [row[1] for row in data]

    plt.figure()
    plt.plot(timestamps, scores, marker='o')
    plt.xlabel("Tiempo")
    plt.ylabel("Score mental")
    plt.title("📈 Evolución del estado mental")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

#LÓGICA DE DETECCIÓN DE DETERIORO
def detect_mental_decline(states):
    if len(states) < 3:
        return None

    scores = [s[0] for s in states]
    scores.reverse()  # orden cronológico real

    worsening = all(
        scores[i] <= scores[i + 1]
        for i in range(len(scores) - 1)
    )

    if worsening:
        return {
            "level": "warning",
            "message": "🚨 Tendencia de deterioro mental detectada.",
            "action": "Pausa recomendada o modo relajado.",
            "reason": "El estado mental no se ha recuperado en sesiones recientes."
        }

    return None

#Perfil Psicológico
def build_psychological_profile(states):
    if len(states) < 5:
        return {
            "summary": "Perfil insuficiente",
            "details": "Se requieren más sesiones para análisis psicológico."
        }

    scores = [s[0] for s in states]

    avg_score = sum(scores) / len(scores)
    variability = max(scores) - min(scores)
    high_count = sum(1 for s in scores if s >= 5)

    if avg_score < 3:
        tolerance = "alta"
    elif avg_score < 4.5:
        tolerance = "media"
    else:
        tolerance = "baja"

    if variability < 1:
        stability = "muy estable"
    elif variability < 2:
        stability = "estable"
    else:
        stability = "volátil"

    if high_count >= len(scores) // 2:
        risk = "alto"
    elif high_count >= 2:
        risk = "moderado"
    else:
        risk = "bajo"

    summary = f"Jugador con tolerancia {tolerance} al tilt y perfil {stability}."
    details = (
        f"Promedio mental: {avg_score:.2f}\n"
        f"Variabilidad: {variability:.2f}\n"
        f"Riesgo emocional: {risk}"
    )

    return {
        "summary": summary,
        "details": details
    }

#Consejos personalizados
def personalized_advice_from_profile(profile):
    summary = profile["summary"].lower()
    details = profile["details"].lower()

    if "tolerancia baja" in summary and "volátil" in summary:
        return {
            "message": "Perfil sensible al tilt detectado.",
            "recommendation": (
                "• Máximo 2 ranked por sesión\n"
                "• Evitar campeones mecánicamente exigentes\n"
                "• Pausa obligatoria tras derrota\n"
                "• Priorizar ARAM o normales si hay frustración"
            ),
            "reason": "Alta reactividad emocional y baja estabilidad."
        }

    if "tolerancia media" in summary:
        return {
            "message": "Perfil con control moderado.",
            "recommendation": (
                "• Limitar sesiones largas\n"
                "• Definir objetivo por partida\n"
                "• Alternar ranked y normales"
            ),
            "reason": "Buen control con riesgo en acumulación."
        }

    if "tolerancia alta" in summary and "estable" in summary:
        return {
            "message": "Perfil mental sólido.",
            "recommendation": (
                "• Puedes jugar ranked continuo\n"
                "• Mantén rutinas de descanso\n"
                "• Usa este perfil para climb largo"
            ),
            "reason": "Alta tolerancia y estabilidad emocional."
        }

    return {
        "message": "Perfil mixto.",
        "recommendation": "Juega con atención a señales tempranas de frustración.",
        "reason": "Patrón no claramente dominante."
    }

#Perfil adaptativo
def adaptive_thresholds_from_history(states):
    scores = [s[0] for s in states]

    if len(scores) < 5:
        return {
            "low": 3.0,
            "medium": 4.5,
            "high": 6.0,
            "note": "Umbrales estándar (datos insuficientes)"
        }

    avg = sum(scores) / len(scores)
    variability = max(scores) - min(scores)

    # Ajuste por sensibilidad
    if variability > 4:
        high = 5.2
        medium = 4.0
    else:
        high = 6.0
        medium = 4.5

    # Ajuste por promedio alto
    if avg > 4.5:
        medium -= 0.3
        high -= 0.4

    return {
        "low": 3.0,
        "medium": round(medium, 2),
        "high": round(high, 2),
        "note": "Umbrales adaptados al comportamiento del jugador"
    }

def champion_emotional_profile(data):

    if not data:
        return None

    sorted_data = sorted(data, key=lambda x: x[1], reverse=True)

    worst = sorted_data[0]
    best = sorted_data[-1]

    return {
        "worst_champion": worst[0],
        "worst_score": round(worst[1], 2),

        "best_champion": best[0],
        "best_score": round(best[1], 2),

        "details": sorted_data
    }