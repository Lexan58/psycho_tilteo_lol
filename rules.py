import sqlite3
import pandas as pd
from datetime import datetime

DB_PATH = "data/tilteo.db"

def check_anti_tilt_rules():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql("SELECT date, tilt_level, result FROM matches", conn)
    conn.close()

    if df.empty or len(df) < 5:
        return ["ℹ️ Aún no hay suficientes datos para evaluar reglas."]

    warnings = []

    # Procesar fechas
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date")

    current_hour = datetime.now().hour

    # 🔴 Regla 1: Hora peligrosa
    recent_hours = df[df["date"].dt.hour >= 22]
    if not recent_hours.empty and recent_hours["tilt_level"].mean() >= 4:
        warnings.append("❌ Riesgo alto: juegas muy tilteado después de las 22:00.")

    # 🟠 Regla 2: Últimas 3 partidas
    last_3 = df.tail(3)
    if (last_3["tilt_level"] >= 4).all():
        warnings.append("🟠 Las últimas 3 partidas fueron con tilt alto. Descansa.")

    # 🟡 Regla 3: Winrate con tilt alto
    high_tilt = df[df["tilt_level"] >= 4]
    if not high_tilt.empty:
        winrate = (high_tilt["result"] == "W").mean() * 100
        if winrate < 30:
            warnings.append(
                f"🟡 Con tilt alto tu winrate es {winrate:.1f}%. Evita ranked."
            )

    if not warnings:
        warnings.append("✅ No se detectan riesgos altos de tilt. Juega con cabeza.")

    return warnings
