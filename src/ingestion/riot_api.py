"""
Riot Games API Connector
Fetches Valorant match data
"""
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import random
from src.ingestion.base_connector import BaseConnector
from config.api_config import APIConfig
from src.utils.logger import get_logger

logger = get_logger(__name__)


class RiotAPIConnector(BaseConnector):
    """Riot Games API connector for Valorant data"""
    
    def __init__(self):
        super().__init__(
            base_url=APIConfig.RIOT_API_BASE_URL,
            rate_limit=APIConfig.RIOT_RATE_LIMIT
        )
        self.api_key = APIConfig.RIOT_API_KEY
        self.endpoints = APIConfig.get_riot_endpoints()
    
    def get_game_name(self) -> str:
        return "valorant"
    
    def fetch_data(self, limit: int = 10, **kwargs) -> List[Dict[str, Any]]:
        """Fetch Valorant match data from Riot API - REAL DATA ONLY"""
        logger.info(f"Fetching Riot/Valorant data (limit: {limit})")
        
        # If no API key, return empty - no mock data
        if not self.api_key:
            logger.warning("Riot API key not configured - returning empty (no mock data)")
            return []
        
        # Riot API requires PUUID (player unique ID) to fetch matches
        # This is a limitation - we need player PUUIDs to get match history
        logger.warning("Riot API requires player PUUIDs to fetch match data")
        logger.info("Note: To get real Valorant data, you need player PUUIDs")
        
        # For now, return empty - no mock data
        # In production, you would:
        # 1. Get PUUID from player name/region
        # 2. Fetch match history using PUUID
        # 3. Fetch match details for each match ID
        return []
    
    def fetch_match_history(self, puuid: str) -> List[Dict]:
        """Fetch match history for a player"""
        if not self.api_key:
            logger.warning("Riot API key not configured, using mock data")
            return self._generate_mock_match_history(puuid)
        
        endpoint = f"{self.endpoints['match_history']}{puuid}"
        headers = {"X-Riot-Token": self.api_key}
        
        data = self._make_request(
            endpoint.replace(APIConfig.RIOT_API_BASE_URL, ""),
            headers=headers
        )
        
        if not data:
            return self._generate_mock_match_history(puuid)
        
        return data.get("history", [])
    
    def _generate_mock_valorant_matches(self, limit: int) -> List[Dict[str, Any]]:
        """Generate mock Valorant match data"""
        results = []
        base_time = datetime.now()
        maps = ["Bind", "Haven", "Split", "Ascent", "Icebox", "Breeze", "Fracture"]
        agents = ["Jett", "Reyna", "Sage", "Cypher", "Omen", "Phoenix", "Brimstone"]
        
        for i in range(limit):
            match_id = f"riot_valorant_{random.randint(1000000000, 9999999999)}"
            start_time = base_time - timedelta(hours=i * 2)
            
            results.append({
                "match_id": match_id,
                "game_id": "valorant",
                "game_name": "Valorant",
                "match_date": start_time.isoformat(),
                "duration_minutes": random.randint(20, 50),
                "match_type": random.choice(["competitive", "unrated", "spike_rush"]),
                "map": random.choice(maps),
                "score_team1": random.randint(0, 13),
                "score_team2": random.randint(0, 13),
                "most_played_agent": random.choice(agents),
                "platform": "riot",
                "source": "riot_api",
            })
        
        return results
    
    def _generate_mock_match_history(self, puuid: str) -> List[Dict]:
        """Generate mock match history"""
        matches = []
        base_time = datetime.now()
        
        for i in range(10):
            matches.append({
                "matchId": f"riot_valorant_{random.randint(1000000000, 9999999999)}",
                "gameStartTimeMillis": int((base_time - timedelta(hours=i)).timestamp() * 1000),
                "queueId": random.choice(["competitive", "unrated"]),
            })
        
        return matches
