# dashboard.py
import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime

from core.database import (
    create_table,
    create_mental_log_table,
    get_champion_mental_stats,
    get_recent_mental_states,
    get_mental_timeline,
    get_last_champion_played,
    get_recent_tilt_data,
    save_mental_state,
    get_matches_dataframe,
    update_match_tilt
)
from core.sync_service import sincronizar_historial_usuario
from core.analytics import (
    champion_emotional_profile,
    build_psychological_profile,
    personalized_advice_from_profile,
    adaptive_thresholds_from_history,
    detect_mental_decline
)
from core.tilt_rules import evaluate_mental_state, ranked_access_decision

# Inicializar Base de Datos al arrancar la UI
create_table()
create_mental_log_table()

st.set_page_config(page_title="Psycho Tilt LoL", layout="wide")

# Botón estructural en la barra lateral para resolver el problema de refresco de caché
with st.sidebar:
    st.title("⚙️ Panel de Control")
    if st.button("🔄 Forzar Sincronización Local / Limpiar Caché"):
        st.cache_data.clear()
        st.success("Caché restablecida.")
        st.rerun()
    st.info("Usa este botón si descargas nuevas partidas de Riot para actualizar los indicadores estadísticos.")

st.title("🧠🎮 Psycho Tilt LoL")
st.caption("Sistema inteligente de análisis mental y prevención de tilt para League of Legends")

# Carga de datos base de contingencia
states = get_recent_mental_states(15)
avg_tilt, losses = get_recent_tilt_data(5)
timeline = get_mental_timeline()

# DEFINICIÓN DE PESTAÑAS (FASE 4)
tab_mental, tab_champions, tab_sync, tab_history = st.tabs([
    "🧠 Estado Mental", 
    "🎮 Análisis de Campeones", 
    "🔄 Sincronizar Riot API", 
    "📈 Historial y Calificación"
])

# ==========================================
# PESTAÑA 1: ESTADO MENTAL
# ==========================================
with tab_mental:
    st.header("🧠 Pre-Match Predictor (IA)")
    st.write("Antes de entrar a la cola de emparejamiento, selecciona tus parámetros para evaluar el riesgo de tilt estimado por la IA.")

    # Inicializar predictor de Machine Learning
    from core.ml_predictor import TiltPredictorIO
    predictor = TiltPredictorIO()
    predictor.train_model() # Entrena el bosque aleatorio con tus 20 partidas guardadas

    col_sim1, col_sim2 = st.columns(2)
    with col_sim1:
        champ_input = st.selectbox("Campeón que planeas jugar:", ["Yasuo", "LeeSin", "Jinx", "Thresh", "Orianna", "Ahri", "Vayne"])
    with col_sim2:
        role_input = st.selectbox("Rol asignado:", ["TOP", "JUNGLE", "MIDDLE", "BOTTOM", "UTILITY"])

    if st.button("🔮 Calcular Probabilidad de Tilt"):
        prediction = predictor.predict_prematch_risk(champ_input, role_input)
        
        if prediction["success"]:
            prob = prediction["probability"]
            
            if prob >= 70:
                st.error(f"🚨 RIESGO CRÍTICO: {prob}% de probabilidad de tilt alto.")
            elif prob >= 40:
                st.warning(f"⚠️ RIESGO MODERADO: {prob}% de probabilidad de tilt.")
            else:
                st.success(f"✅ MENTAL ÓPTIMO: {prob}% de probabilidad de tilt. Estás enfocado.")
                
            if prediction["factors"]:
                st.write("**Factores determinantes analizados:**")
                for factor in prediction["factors"]:
                    st.write(factor)
            else:
                st.write("✨ No se detectaron anomalías ambientales ni de rendimiento latentes.")
        else:
            st.info(prediction["message"])

    st.markdown("---") # Línea divisoria
    st.header("🧠 Estado Mental Actual")
    
    if st.button("Evaluar mi estado emocional ahora"):
        hour = datetime.now().hour
        last_champion = get_last_champion_played()

        # 1. Evaluar el estado de alerta base
        score, state, advice = evaluate_mental_state(
            avg_tilt if avg_tilt is not None else 0,
            losses,
            hour,
            5,
            last_champion
        )
        
        # 2. Guardar en el log histórico de la DB
        save_mental_state(score, state)

        # 3. Calcular la decisión de acceso a ranked (Tu sistema original)
        decision = ranked_access_decision(state)

        st.markdown("### 📊 Veredicto de Estabilidad Emocional")
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Mental Score Target", f"{score:.2f}")
        with col2:
            st.metric("Estado de Alerta", state.upper())

        # 4. Desplegar caja de bloqueo/permiso de ranked
        if decision["allowed"]:
            if state == "medium":
                st.warning(f"**{decision['message']}**\n\n**Motivo:** {decision['reason']}")
            else:
                st.success(f"**{decision['message']}**\n\n**Motivo:** {decision['reason']}")
        else:
            st.error(f"**{decision['message']}**\n\n**Motivo:** {decision['reason']}\n\n👉 **Alternativa:** {decision['alternative']}")

        # 5. Desplegar los consejos psicológicos adicionales
        st.info(f"💡 **Consejo Anti-Tilt:** {advice['message']}\n\n🎯 **Acción recomendada:** {advice['action']}\n\n📌 **Causa:** {advice['reason']}")

    # Línea de tiempo evolutiva corregida para Modo Oscuro
    st.subheader("📈 Evolución de Estabilidad")
    if timeline:
        times = [datetime.fromisoformat(t[0]) for t in timeline]
        scores = [t[1] for t in timeline]
        
        plt.style.use('dark_background')
        fig, ax = plt.subplots(figsize=(10, 3.5))
        
        ax.plot(times, scores, marker="o", color="#00f2fe", mec="#7f00ff", mfc="#7f00ff", linewidth=2.5)
        fig.patch.set_facecolor('#0e1117') 
        ax.set_facecolor('#161b22')
        
        ax.set_ylabel("Mental Score", color="white")
        ax.set_xlabel("Tiempo", color="white")
        ax.tick_params(colors="white") 
        ax.grid(True, linestyle="--", alpha=0.3, color="gray")
        
        plt.xticks(rotation=15)
        plt.tight_layout()
        
        st.pyplot(fig)
        plt.close(fig)
        plt.style.use('default')
    else:
        st.info("No hay suficiente historial en el log mental. Evalúa tu estado un par de veces.")

# ==========================================
# PESTAÑA 2: ANALISIS DE CAMPEONES
# ==========================================
with tab_champions:
    st.header("🎮 Perfil Emocional por Campeón")
    
    champion_data = get_champion_mental_stats()
    if champion_data:
        profile = champion_emotional_profile(champion_data)
        if profile:
            col1, col2 = st.columns(2)
            with col1:
                st.error(f"🚨 **Más Peligroso:** {profile['worst_champion']} (Tilt avg: {profile['worst_score']})")
            with col2:
                st.success(f"🛡️ **Más Estable:** {profile['best_champion']} (Tilt avg: {profile['best_score']})")
            
            champions = [x[0] for x in profile["details"]]
            scores = [x[1] for x in profile["details"]]
            
            fig, ax = plt.subplots(figsize=(10, 4))
            ax.bar(champions, scores, color="#ff7300")
            ax.set_ylabel("Tilt Promedio Registrado")
            st.pyplot(fig)
    else:
        st.info("Para ver estadísticas por campeón, necesitas calificar tus partidas en la pestaña de Historial.")

# ==========================================
# PESTAÑA 3: SINCRONIZAR RIOT API
# ==========================================
with tab_sync:
    st.header("🔄 Importación Automatizada desde Riot")
    st.write("Descarga de forma asíncrona tus últimas partidas para eliminar el registro manual de KDA y resultados.")
    
    with st.form("riot_sync_form"):
        col1, col2 = st.columns(2)
        with col1:
            riot_name = st.text_input("Riot ID (Nombre sin #)", placeholder="Ej: Faker")
        with col2:
            riot_tag = st.text_input("Tagline", placeholder="Ej: KR1")
            
        cantidad = st.slider("Partidas a comprobar", min_value=1, max_value=20, value=5)
        submit_btn = st.form_submit_button("Sincronizar Historial")
        
        if submit_btn:
            if riot_name and riot_tag:
                with st.spinner("Conectando con servidores de Riot Games..."):
                    nuevas = sincronizar_historial_usuario(riot_name, riot_tag, cantidad=cantidad)
                    if nuevas > 0:
                        st.success(f"¡Éxito! Se han importado {nuevas} nuevas partidas a tu registro local.")
                        st.cache_data.clear() 
                    else:
                        st.info("Tu historial local ya está completamente actualizado. No se detectaron partidas duplicadas.")
            else:
                st.error("Por favor, rellena ambos campos para proceder.")

# ==========================================
# PESTAÑA 4: HISTORIAL Y CALIFICACIÓN MANUAL
# ==========================================
with tab_history:
    st.header("📈 Historial de Partidas y Control Emocional")
    
    df_matches = get_matches_dataframe()
    
    if not df_matches.empty:
        partidas_pendientes = df_matches[df_matches['tilt_level'] == 0]
        
        if not partidas_pendientes.empty:
            st.subheader("⚠️ Notas Emocionales Pendientes")
            st.write("Riot API ha descargado estas partidas automáticamente. Por favor, asígnales el nivel de tilt real que experimentaste:")
            
            partida_a_calificar = partidas_pendientes.iloc[0]
            
            with st.form("calificar_tilt_form"):
                st.write(f"**Partida con:** {partida_a_calificar['champion']} | **Rol:** {partida_a_calificar['role']} | **KDA:** {partida_a_calificar['kda']} | **Resultado:** {partida_a_calificar['result']}")
                nuevo_tilt = st.slider("¿Qué nivel de TILT sentiste en esta partida?", min_value=1, max_value=10, value=5)
                nota_emocional = st.text_input("Nota mental / ¿Qué disparó tu frustración?", placeholder="Ej: Mi jungla me tiró surrender temprano.")
                
                if st.form_submit_button("Guardar Registro Psicológico"):
                    update_match_tilt(partida_a_calificar['match_id'], nuevo_tilt, nota_emocional)
                    st.success("Nota guardada correctamente.")
                    st.cache_data.clear()
                    st.rerun()
        else:
            st.success("✨ ¡Buen trabajo! Tienes todas tus partidas del historial calificadas emocionalmente.")
            
        st.subheader("📋 Registro Completo de Datos")
        st.dataframe(
            df_matches[['date', 'champion', 'role', 'kda', 'result', 'tilt_level', 'note']],
            width="stretch"
        )
    else:
        st.info("No hay partidas guardadas en la base de datos. Ve a la pestaña de Sincronización para descargar tus primeros datos de Riot Games.")