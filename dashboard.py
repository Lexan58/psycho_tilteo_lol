import streamlit as st
from datetime import datetime
import matplotlib.pyplot as plt

# --- IMPORTS DE TUS MÓDULOS ---
from tilt_rules import get_recent_tilt_data, evaluate_mental_state
from database import (
    get_recent_mental_states,
    get_mental_timeline,
    get_last_champion_played
)
from analytics import (
    build_psychological_profile,
    personalized_advice_from_profile,
    adaptive_thresholds_from_history,
    detect_mental_decline
)

# --- CACHE ---
@st.cache_data(show_spinner=False)
def cached_recent_tilt(last_n):
    return get_recent_tilt_data(last_n)

@st.cache_data(show_spinner=False)
def cached_recent_states(limit):
    return get_recent_mental_states(limit)

@st.cache_data(show_spinner=False)
def cached_mental_timeline():
    return get_mental_timeline()

@st.cache_data(show_spinner=False)
def cached_profile(states):
    return build_psychological_profile(states)

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Tilteo Coach", layout="wide")
st.title("🧠🎮 Tilteo Coach")

# --- CARGA DE DATOS INICIAL ---
states_history = cached_recent_states(15)
avg_tilt, losses = cached_recent_tilt(5)

# --- 1. ESTADO MENTAL ACTUAL ---
st.header("🧠 Estado mental actual")

if avg_tilt is None:
    st.warning("No hay suficientes datos de partidas para realizar un análisis.")
else:
    if st.button("🧠 Evaluar estado mental actual"):
        hour = datetime.now().hour
        last_champion = get_last_champion_played()
        
        score, state, advice = evaluate_mental_state(
            avg_tilt, losses, hour, 5, last_champion
        )

        col1, col2 = st.columns(2)
        col1.metric("Score mental", f"{score:.2f}")
        col2.metric("Estado", state.upper())

        st.info(f"**Análisis:** {advice['message']}")
        st.success(f"**Acción recomendada:** {advice['action']}")

# --- 2. EVOLUCIÓN GRÁFICA ---
st.header("📈 Evolución mental")
timeline = cached_mental_timeline()

if timeline:
    times = [datetime.fromisoformat(t[0]) for t in timeline]
    scores = [t[1] for t in timeline]

    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(times, scores, marker="o", color="#1f77b4")
    ax.set_ylabel("Score mental")
    st.pyplot(fig)
else:
    st.info("Aún no hay historial suficiente para mostrar la gráfica.")

# --- 3. PERFIL Y UMBRALES ---
st.header("🧬 Análisis Avanzado")

if not states_history or len(states_history) < 3:
    st.warning("Se necesitan al menos 3 registros mentales en el historial para generar el perfil psicológico.")
else:
    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("🧬 Perfil psicológico")
        profile = cached_profile(states_history)
        st.write(profile["summary"])
        
        advice_profile = personalized_advice_from_profile(profile)
        st.info(f"🎯 **Consejo:** {advice_profile['message']}")

    with col_right:
        st.subheader("⚙️ Umbrales adaptativos")
        thresholds = adaptive_thresholds_from_history(states_history)
        st.write(thresholds["note"])
        st.code(f"Bajo < {thresholds['low']} | Medio < {thresholds['medium']} | Alto >= {thresholds['high']}")

    # Alerta de deterioros
    alert = detect_mental_decline(states_history)
    if alert:
        st.error(f"🚨 {alert['message']}")
        st.write(f"👉 **Acción:** {alert['action']}")