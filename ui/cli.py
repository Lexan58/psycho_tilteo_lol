# ui/cli.py
import sys
import os

# Añadir el directorio raíz al path para evitar problemas de importación modular
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.riot_api import RiotAPIGateway, RiotAPIError
from core.sync_service import extract_player_stats # El formateador que diseñamos en la respuesta anterior

def ejecutar_diagnostico_api():
    print("=" * 60)
    print(" PSYCHO TILT LOL - DIAGNÓSTICO DE INTEGRACIÓN (FASE 2) ")
    print("=" * 60)
    
    # 1. Inicializar el Gateway
    try:
        gateway = RiotAPIGateway()
        print("[✓] Configuración cargada y cliente de API inicializado.")
    except Exception as e:
        print(f"[X] Error de configuración: {e}")
        return

    # 2. Solicitar credenciales por consola
    print("\n--- Identificación del Jugador ---")
    game_name = input("Ingresa tu Riot ID (Nombre sin el #): ").strip()
    tag_line = input("Ingresa tu Tag (Ej: LAN, NA1, LAS): ").strip()

    if not game_name or not tag_line:
        print("[X] El Riot ID y el Tag son obligatorios.")
        return

    try:
        # 3. Obtener PUUID
        print(f"\n[Sincronizando] Buscando PUUID para {game_name}#{tag_line}...")
        puuid = gateway.get_puuid_by_riot_id(game_name, tag_line)
        print(f"[✓] PUUID obtenido con éxito: {puuid}")

        # 4. Obtener las últimas 3 partidas para validar la estructura
        print("\n[Sincronizando] Descargando IDs de las últimas 3 partidas...")
        match_ids = gateway.get_match_ids(puuid, start=0, count=3)
        
        if not match_ids:
            print("[!] No se encontraron partidas recientes en el historial de este jugador.")
            return
        
        print(f"[✓] IDs recuperados: {match_ids}")

        # 5. Obtener el detalle de la última partida y transformarla para el dataset
        ultima_partida_id = match_ids[0]
        print(f"\n[Sincronizando] Analizando JSON de la última partida ({ultima_partida_id})...")
        
        match_detail = gateway.get_match_details(ultima_partida_id)
        
        # Procesar con el extractor que alimentará a la base de datos e IA
        stats_limpias = extract_player_stats(match_detail, puuid)
        
        if stats_limpias:
            print("\n" + "=" * 40)
            print("  CONTRATO DE DATOS PARA BASE DE DATOS E IA  ")
            print("=" * 40)
            for clave, valor in stats_limpias.items():
                print(f"🔹 {clave:<12} : {valor}")
            print("=" * 40)
            print("\n[✓] ¡Diagnóstico completado con éxito! Estás listo para la FASE 3 (Automatización).")
        else:
            print("[X] No se pudieron extraer estadísticas del jugador en la partida analizada.")

    except RiotAPIError as e:
        print(f"\n[X] Error en la comunicación con Riot API: {e}")
    except Exception as e:
        print(f"\n[X] Error inesperado en el sistema: {e}")

if __name__ == "__main__":
    ejecutar_diagnostico_api()