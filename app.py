from core.database import create_table, create_mental_log_table, show_mental_log
from ui.cli import add_match
from core.analytics import (
    tilt_by_result,
    tilt_by_hour,
    winrate_vs_tilt,
    tilt_by_champion,
    tilt_heatmap_by_hour
)
from core.database import get_recent_mental_states
from core.analytics import detect_mental_decline

from core.database import get_mental_timeline
from core.analytics import plot_mental_timeline

from core.rules import check_anti_tilt_rules
from core.tilt_rules import ranked_access_decision

from core.tilt_rules import (
    get_recent_tilt_data,
    evaluate_mental_state
)

from core.database import save_mental_state
from datetime import datetime
from core.database import get_last_champion_played
from core.analytics import build_psychological_profile
from core.analytics import personalized_advice_from_profile


def main():
    create_table()
    create_mental_log_table()

    while True:
        print("\n🎮 Tilteo LoL Tracker")
        print("1. Registrar partida")
        print("2. Tilt por resultado")
        print("3. Tilt por hora del día")
        print("4. Winrate vs nivel de tilt")
        print("5. Tilt por campeón")
        print("6. Heatmap de tilt")
        print("7. Evaluar reglas anti-tilt")
        print("8. Análisis anti-tilt (coach mental)")
        print("9. Mostrar el historial")
        print("10. Ver evolución mental")
        print("11. Perfil psicológico del jugador")
        print("12. Salir")

        choice = input("Selecciona una opción: ")

        if choice == "1":
            add_match()
        elif choice == "2":
            tilt_by_result()
        elif choice == "3":
            tilt_by_hour()
        elif choice == "4":
            winrate_vs_tilt()
        elif choice == "5":
            tilt_by_champion()
        elif choice == "6":
            tilt_heatmap_by_hour()
        elif choice == "7":
            alerts = check_anti_tilt_rules()
            print("\n🚨 Evaluación anti-tilt:")
            for alert in alerts:
                print(alert)
        elif choice == "8":
            last_champion = get_last_champion_played()
            avg_tilt, losses = get_recent_tilt_data(last_n=5)

            if avg_tilt is None:
                print("❌ No hay suficientes datos aún.")
            else:
                hour = datetime.now().hour
                matches_recent = 5

                # 1. Obtener datos para umbrales
                from core.database import get_recent_mental_states # Mover arriba si es posible
                from core.analytics import adaptive_thresholds_from_history, detect_mental_decline
                # Asegúrate de importar mental_state_from_score si existe
                
                recent_states = get_recent_mental_states(limit=10)
                thresholds = adaptive_thresholds_from_history(recent_states)

                # 2. Evaluación inicial
                score, state, advice = evaluate_mental_state(
                    avg_tilt, losses, hour, matches_recent, last_champion
                )

                # 3. RECALCULAR estado con umbrales adaptativos ANTES de guardar
                # state = mental_state_from_score(score, thresholds) 

                # 4. GUARDAR ahora que tenemos el estado final
                save_mental_state(score, state)

                # --- Visualización ---
                if last_champion:
                    from core.player_profile import PLAYER_PROFILE
                    print(f"🎮 Campeón reciente: {last_champion}")
                    if last_champion in PLAYER_PROFILE["stress_champions"]:
                        print("⚠️ Campeón de alta carga emocional detectado.")
                
                # Alerta de tendencia
                decline_alert = detect_mental_decline(get_recent_mental_states(limit=5))
                if decline_alert:
                    print(f"\n🚨 ALERTA: {decline_alert['message']}")

                print("\n🧠 ESTADO MENTAL AVANZADO")
                print(f"Score: {score:.2f} | Estado: {state.upper()}")
                print(f"👉 {advice['message']}\n📌 Acción: {advice['action']}")

                # Decisión de ranked
                decision = ranked_access_decision(state)
                print(f"\n🎯 ACCESO A RANKED: {decision['message']}")
                
                print("\n⚙️ UMBRALES ADAPTATIVOS")
                print(f"LOW < {thresholds['low']} | MEDIUM < {thresholds['medium']} | HIGH ≥ {thresholds['high']}")


        elif choice == "9":
            logs = show_mental_log()
            print("\n" + "="*40)
            print("📊 ÚLTIMOS REGISTROS MENTALES")
            print(f"{'FECHA Y HORA':<25} | {'SCORE':<7} | {'ESTADO'}")
            print("-" * 40)
            
            for row in logs:
                # Formateamos la fecha para que no se vea el T de ISO
                fecha = row[0].replace("T", " ")[:16]
                score = row[1]
                estado = row[2].upper()
                print(f"{fecha:<25} | {score:<7.2f} | {estado}")
            print("="*40)
        
        elif choice == "10":
            data = get_mental_timeline()
            plot_mental_timeline(data)

        elif choice == "11":
            from core.database import get_recent_mental_states
            states = get_recent_mental_states(limit=10)

            profile = build_psychological_profile(states)
            advice = personalized_advice_from_profile(profile)

            print("\n🧬 PERFIL PSICOLÓGICO DEL JUGADOR")
            print(profile["summary"])
            print(profile["details"])

            print("\n🎯 CONSEJO PERSONALIZADO")
            print(advice["message"])
            print(advice["recommendation"])
            print("📌 Motivo:", advice["reason"])
    
        elif choice == "12":
            print("👋 GG. Cuida tu mental.")
            break


if __name__ == "__main__":
    main()
