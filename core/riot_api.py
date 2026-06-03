# core/riot_api.py
import requests
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class RiotAPIError(Exception):
    """Excepción base para errores de la Riot API."""
    pass

class RiotAPIGateway:
    def __init__(self):
        from core.config import RIOT_API_KEY, REGION
        if not RIOT_API_KEY:
            raise RiotAPIError("RIOT_API_KEY no configurada en config.py")
        
        self.headers = {
            "X-Riot-Token": RIOT_API_KEY
        }
        self.regional_url = f"https://{self._get_regional_routing(REGION)}.api.riotgames.com"
        self.platform_url = f"https://{REGION}.api.riotgames.com"

    def _get_regional_routing(self, region: str) -> str:
        region_map = {
            "la1": "americas", "la2": "americas", "na1": "americas", "br1": "americas",
            "euw1": "europe", "eun1": "europe", "tr1": "europe", "ru": "europe",
            "kr": "asia", "jp1": "asia"
        }
        return region_map.get(region.lower(), "americas")

    def _request(self, url: str) -> Dict[str, Any]:
        try:
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 429:
                raise RiotAPIError("Rate limit exceeded. Por favor, espera antes de reintentar.")
            elif response.status_code == 403:
                raise RiotAPIError("API Key inválida o expirada (403).")
            elif response.status_code == 404:
                raise RiotAPIError("Recurso no encontrado (404).")
            
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise RiotAPIError(f"Error de conexión: {e}")

    def get_puuid_by_riot_id(self, game_name: str, tag_line: str) -> str:
        url = f"{self.regional_url}/riot/account/v1/accounts/by-riot-id/{game_name}/{tag_line}"
        data = self._request(url)
        return data["puuid"]

    def get_match_ids(self, puuid: str, start: int = 0, count: int = 20) -> List[str]:
        url = f"{self.regional_url}/lol/match/v5/matches/by-puuid/{puuid}/ids?start={start}&count={count}"
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise RiotAPIError(f"Error al obtener historial de partidas: {e}")

    def get_match_details(self, match_id: str) -> Dict[str, Any]:
        url = f"{self.regional_url}/lol/match/v5/matches/{match_id}"
        return self._request(url)