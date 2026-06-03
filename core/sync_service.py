# core/sync_service.py
from datetime import datetime
from typing import Dict, Any, Optional
from core.riot_api import RiotAPIGateway
from core.database import match_exists, save_match_to_db

def extract_player_stats(match_detail: Dict[str, Any], puuid: str) -> Optional[Dict[str, Any]]:
    """Filtra y extrae las métricas del jugador específico dentro del JSON de Riot."""
    info = match_detail.get("info", {})
    participants = info.get("participants", [])
    
    # Buscar al usuario por su PUUID
    player = next((p for p in participants if p["puuid"] == puuid), None)
    if not player:
        return None

    game_creation_ms = info.get("gameCreation", 0)
    date_obj = datetime.fromtimestamp(game_creation_ms / 1000.0)

    kills = player.get("kills", 0)
    deaths = player.get("deaths", 0)
    assists = player.get("assists", 0)
    
    # Formateamos el resultado para emparejarlo con tu lógica previa de la DB
    win_status = "Win" if player.get("win") else "Loss"
    
    return {
        "match_id": match_detail["metadata"]["matchId"],
        "date": date_obj.strftime("%Y-%m-%d %H:%M:%S"),
        "champion": player.get("championName", "Unknown"),
        "role": player.get("teamPosition", "UNKNOWN"),
        "kda": f"{kills}/{deaths}/{assists}",
        "kills": kills,
        "deaths": deaths,
        "assists": assists,
        "result": win_status
    }

def sincronizar_historial_usuario(game_name: str, tag_line: str, cantidad: int = 10) -> int:
    """
    Orquesta la descarga, filtrado y guardado automático.
    Retorna la cantidad de partidas nuevas que se agregaron a la DB.
    """
    api = RiotAPIGateway()
    partidas_guardadas = 0
    
    # 1. Obtener identificadores universales e historial
    puuid = api.get_puuid_by_riot_id(game_name, tag_line)
    match_ids = api.get_match_ids(puuid, start=0, count=cantidad)
    
    # 2. Procesar cada partida protegiendo la DB de duplicados
    for m_id in match_ids:
        if match_exists(m_id):
            continue  # Si ya existe, nos saltamos la llamada pesada a la API
            
        # Si es nueva para la DB local, descargamos el detalle completo
        detalle = api.get_match_details(m_id)
        stats = extract_player_stats(detalle, puuid)
        
        if stats:
            save_match_to_db(stats)
            partidas_guardadas += 1
            
    return partidas_guardadas