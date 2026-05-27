import streamlit as st
import matplotlib.pyplot as plt
from core.database import get_champion_mental_stats
from core.analytics import champion_emotional_profile
from core.config import DASHBOARD_TITLE

from datetime import datetime

from core.database import (
    get_recent_mental_states,
    get_mental_timeline,
    get_last_champion_played
)

from core.tilt_rules import (
    get_recent_tilt_data,
    evaluate_mental_state
)

from core.analytics import (
    build_psychological_profile,
    personalized_advice_from_profile,
    adaptive_thresholds_from_history,
    detect_mental_decline
)

# =========================
# CONFIG
# =========================

st.set_page_config(
    page_title="Tilteo Coach",
    layout="wide"
)

st.title("🧠🎮 Tilteo Coach")
st.caption("Sistema inteligente de análisis mental para League of Legends")

# =========================
# CACHE
# =========================

@st.cache_data(show_spinner=False)
def cached_recent_tilt(last_n):
    return get_recent_tilt_data(last_n)

@st.cache_data(show_spinner=False)
def cached_recent_states(limit):
    return get_recent_mental_states(limit)

@st.cache_data(show_spinner=False)
def cached_timeline():
    return get_mental_timeline()

@st.cache_data(show_spinner=False)
def cached_profile(states):
    return build_psychological_profile(states)

# =========================
# LOAD DATA
# =========================

with st.spinner("Analizando estado mental..."):
    avg_tilt, losses = cached_recent_tilt(5)
    states = cached_recent_states(15)
    timeline = cached_timeline()

# =========================
# VALIDATION
# =========================

if not states or len(states) < 3:
    st.warning("⚠️ No hay suficientes datos mentales aún.")
    st.stop()

# =========================
# CURRENT STATE
# =========================

st.header("🧠 Estado mental actual")

if st.button("Evaluar estado mental"):

    hour = datetime.now().hour
    last_champion = get_last_champion_played()

    score, state, advice = evaluate_mental_state(
        avg_tilt,
        losses,
        hour,
        5,
        last_champion
    )

    col1, col2 = st.columns(2)

    with col1:
        st.metric("Mental Score", round(score, 2))

    with col2:
        st.metric("Estado", state.upper())

    if state == "high":
        st.error(advice["message"])
    elif state == "medium":
        st.warning(advice["message"])
    else:
        st.success(advice["message"])

    st.write("👉", advice["action"])
    st.caption(advice["reason"])

# =========================
# PROFILE
# =========================

with st.expander("🧬 Perfil psicológico", expanded=False):

    profile = cached_profile(states)

    st.subheader("Resumen")

    st.write(profile["summary"])

    st.text(profile["details"])

    advice_profile = personalized_advice_from_profile(profile)

    st.subheader("🎯 Recomendación personalizada")

    st.write(advice_profile["message"])

    st.caption(advice_profile["recommendation"])

# =========================
# ADAPTIVE THRESHOLDS
# =========================

with st.expander("⚙️ Umbrales adaptativos", expanded=False):

    thresholds = adaptive_thresholds_from_history(states)

    st.write(thresholds["note"])

    st.code(
        f"""
LOW < {thresholds['low']}
MEDIUM < {thresholds['medium']}
HIGH ≥ {thresholds['medium']}
"""
    )

# =========================
# DECLINE ALERT
# =========================

alert = detect_mental_decline(states)

if alert:
    st.error(alert["message"])
    st.write("👉", alert["action"])

# =========================
# MENTAL TIMELINE
# =========================

with st.expander("📈 Evolución mental", expanded=True):

    if timeline:

        times = [datetime.fromisoformat(t[0]) for t in timeline]
        scores = [t[1] for t in timeline]

        fig, ax = plt.subplots(figsize=(10, 4))

        ax.plot(times, scores, marker="o")

        ax.set_title("Mental Score Timeline")

        ax.set_xlabel("Tiempo")

        ax.set_ylabel("Score")

        st.pyplot(fig)

    else:
        st.info("No hay historial suficiente.")

# =========================
# CHAMPION ANALYSIS
# =========================

with st.expander("🎮 Perfil emocional por campeón", expanded=True):

    champion_data = get_champion_mental_stats()

    profile = champion_emotional_profile(champion_data)

    if profile:

        st.subheader("🚨 Campeón más peligroso")

        st.error(
            f"{profile['worst_champion']} "
            f"(Tilt promedio: {profile['worst_score']})"
        )

        st.subheader("🛡️ Campeón más estable")

        st.success(
            f"{profile['best_champion']} "
            f"(Tilt promedio: {profile['best_score']})"
        )

        st.subheader("📊 Comparación completa")

        champions = [x[0] for x in profile["details"]]
        scores = [x[1] for x in profile["details"]]

        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(figsize=(10, 4))

        ax.bar(champions, scores)

        ax.set_ylabel("Tilt promedio")

        ax.set_title("Carga emocional por campeón")

        st.pyplot(fig)

    else:
        st.info("No hay suficientes datos.")