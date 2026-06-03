# core/analytics.py
import pandas as pd
import matplotlib.pyplot as plt
from core.database import get_matches_dataframe

def tilt_by_result():
    """Calcula y despliega el tilt promedio según victorias o derrotas."""
    df = get_matches_dataframe()
    if df.empty:
        print("❌ No hay datos suficientes en la base de datos.")
        return None

    # Agrupación estadística
    grouped = df.groupby("result")["tilt_level"].mean()

    # Construcción orientada a objetos (Segura para CLI y Streamlit)
    fig, ax = plt.subplots(figsize=(6, 4))
    grouped.plot(kind="bar", color=["#e74c3c", "#2ecc71"], ax=ax)
    ax.set_title("Nivel de Tilt Promedio por Resultado")
    ax.set_xlabel("Resultado de la Partida")
    ax.set_ylabel("Tilt Promedio (1-10)")
    ax.grid(axis='y', linestyle="--", alpha=0.7)
    
    # Si se ejecuta desde la consola (CLI), mostramos el plot. 
    # Si viene desde Streamlit, la UI capturará el objeto 'fig' devuelto.
    return fig

def tilt_by_hour():
    """Analiza la correlación entre la hora de juego y el nivel de frustración."""
    df = get_matches_dataframe()
    if df.empty:
        print("❌ No hay datos aún.")
        return None

    # Mapeo y formateo seguro del tiempo
    df["date"] = pd.to_datetime(df["date"])
    df["hour"] = df["date"].dt.hour

    grouped = df.groupby("hour")["tilt_level"].mean()

    fig, ax = plt.subplots(figsize=(10, 4))
    grouped.plot(kind="line", marker="o", color="#9b59b6", linewidth=2, ax=ax)
    ax.set_title("Tilt Promedio por Hora del Día")
    ax.set_xlabel("Hora del Día (0-23)")
    ax.set_ylabel("Tilt Promedio")
    ax.set_xticks(range(0, 24))
    ax.grid(True, linestyle="--", alpha=0.5)
    
    return fig

def winrate_vs_tilt():
    """Calcula el porcentaje de victorias agrupado por la severidad del tilt."""
    df = get_matches_dataframe()
    if df.empty:
        print("❌ No hay datos suficientes.")
        return None

    # Convertimos los estados de texto a binarios para promediar el Winrate
    df["win_binary"] = df["result"].apply(lambda x: 1 if x == "Win" else 0)
    
    # Agrupamos por el nivel de tilt para ver el impacto real en el rendimiento
    grouped = df.groupby("tilt_level")["win_binary"].mean() * 100

    fig, ax = plt.subplots(figsize=(8, 4))
    grouped.plot(kind="line", marker="s", color="#3498db", linewidth=2, ax=ax)
    ax.set_title("Impacto del Tilt en el Winrate")
    ax.set_xlabel("Nivel de Tilt Experimentado")
    ax.set_ylabel("Winrate (%)")
    ax.grid(True, linestyle="--", alpha=0.5)
    
    return fig

def tilt_by_champion():
    """Muestra qué campeones disparan mayor carga de estrés emocional."""
    df = get_matches_dataframe()
    if df.empty:
        print("❌ No hay datos.")
        return None

    grouped = df.groupby("champion")["tilt_level"].mean().sort_values(ascending=False)

    fig, ax = plt.subplots(figsize=(10, 4))
    grouped.plot(kind="bar", color="#e67e22", ax=ax)
    ax.set_title("Índice de Toxicidad Mental por Campeón")
    ax.set_xlabel("Campeón")
    ax.set_ylabel("Tilt Promedio")
    ax.grid(axis='y', linestyle="--", alpha=0.5)
    
    return fig

def tilt_heatmap_by_hour():
    """Genera una matriz cruzada para identificar horas y días críticos de tilt."""
    df = get_matches_dataframe()
    if df.empty:
        print("❌ Datos insuficientes.")
        return None

    df["date"] = pd.to_datetime(df["date"])
    df["hour"] = df["date"].dt.hour
    df["day_name"] = df["date"].dt.day_name()

    # Matriz pivotada para el mapa de calor estadístico
    pivot_table = df.pivot_table(
        index="day_name", 
        columns="hour", 
        values="tilt_level", 
        aggfunc="mean"
    ).fillna(0)

    fig, ax = plt.subplots(figsize=(12, 5))
    cax = ax.matshow(pivot_table, cmap="YlOrRd")
    fig.colorbar(cax, label="Nivel de Tilt")
    
    ax.set_title("Mapa de Calor Semanal: Puntos Críticos de Frustración\n", fontsize=14)
    ax.set_xticks(range(len(pivot_table.columns)))
    ax.set_xticklabels(pivot_table.columns)
    ax.set_yticks(range(len(pivot_table.index)))
    ax.set_yticklabels(pivot_table.index)
    
    return fig

# =========================================================
# LÓGICA DE NEGOCIO PSICOLÓGICA (Tus funciones dinámicas intactas)
# =========================================================

def build_psychological_profile(states):
    if not states:
        return {
            "summary": "Sin datos.",
            "details": "Evalúa tu estado mental para generar un diagnóstico."
        }
    scores = [s[0] for s in states]
    avg_score = sum(scores) / len(scores)
    
    if avg_score < 4:
        return {
            "summary": "Mente de Hierro (Estable)",
            "details": "Baja reactividad ante las derrotas. Control emocional óptimo."
        }
    elif avg_score < 6.5:
        return {
            "summary": "Reactivo (Riesgo Moderado)",
            "details": "Sensibilidad notable a malas rachas o compañeros tóxicos."
        }
    else:
        return {
            "summary": "Tilt Crónico (Inestable)",
            "details": "Alta propensión a jugar de manera impulsiva o por venganza."
        }

def personalized_advice_from_profile(profile):
    if "Hierro" in profile["summary"]:
        return {"message": "Sigue así. Tu enfoque analítico mitiga la varianza.", "action": "Continuar en ranked."}
    return {"message": "Detectamos fatiga competitiva latente.", "action": "Tomar un descanso de 20 minutos o jugar un ARAM."}

def adaptive_thresholds_from_history(states):
    scores = [s[0] for s in states]
    if len(scores) < 5:
        return {"low": 3.0, "medium": 4.5, "high": 6.0, "note": "Umbrales estándar"}
    
    avg = sum(scores) / len(scores)
    return {
        "low": 3.0,
        "medium": round(avg, 2),
        "high": round(avg + 1.5, 2),
        "note": "Umbrales adaptados estadísticamente"
    }

def champion_emotional_profile(champion_data):
    if not champion_data:
        return {}
    
    # Estructura limpia para mapear el rendimiento psicológico de campeones
    sorted_champs = sorted(champion_data, key=lambda x: x[1])
    return {
        "best_champion": sorted_champs[0][0],
        "best_score": round(sorted_champs[0][1], 2),
        "worst_champion": sorted_champs[-1][0],
        "worst_score": round(sorted_champs[-1][1], 2),
        "details": sorted_champs
    }

def detect_mental_decline(states):
    if len(states) < 3:
        return False
    scores = [s[0] for s in states[:3]]
    return scores[0] > scores[1] > scores[2]