"""
OpenDota API Connector
Fetches detailed Dota 2 match data
"""
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import random
from src.ingestion.base_connector import BaseConnector
from config.api_config import APIConfig
from src.utils.logger import get_logger

logger = get_logger(__name__)


class OpenDotaAPIConnector(BaseConnector):
    """OpenDota API connector for Dota 2 data"""
    
    def __init__(self):
        super().__init__(
            base_url=APIConfig.OPENDOTA_API_BASE_URL,
            rate_limit=APIConfig.OPENDOTA_RATE_LIMIT
        )
        self.endpoints = APIConfig.get_opendota_endpoints()
    
    def get_game_name(self) -> str:
        return "dota2"
    
    def fetch_data(self, limit: int = 10, **kwargs) -> List[Dict[str, Any]]:
        """Fetch Dota 2 match data from OpenDota - REAL DATA ONLY"""
        logger.info(f"Fetching OpenDota data (limit: {limit})")
        
        # Always try to fetch real data - no mock fallback
        try:
            endpoint = self.endpoints["public_matches"].replace(APIConfig.OPENDOTA_API_BASE_URL, "")
            # Fetch more to ensure we get enough valid matches
            data = self._make_request(endpoint, params={"limit": min(limit * 2, 100)})
            
            if data and isinstance(data, list) and len(data) > 0:
                transformed = self._transform_opendota_matches(data)
                logger.info(f"Successfully fetched {len(transformed)} real matches from OpenDota!")
                return transformed[:limit]  # Return requested limit
            else:
                logger.warning("OpenDota API returned empty data - will retry")
                # Retry once
                data = self._make_request(endpoint, params={"limit": limit})
                if data and isinstance(data, list) and len(data) > 0:
                    transformed = self._transform_opendota_matches(data)
                    logger.info(f"Retry successful: fetched {len(transformed)} real matches")
                    return transformed
        except Exception as e:
            logger.error(f"Error fetching from OpenDota API: {str(e)}")
        
        # Only return empty list if API fails - no mock data
        logger.warning("OpenDota API unavailable - returning empty list (no mock data)")
        return []
    
    def fetch_match_details(self, match_id: int) -> Optional[Dict]:
        """Fetch detailed match information - REAL DATA ONLY"""
        # Remove 'opendota_' prefix if present
        clean_match_id = str(match_id).replace("opendota_", "")
        
        try:
            endpoint = f"{self.endpoints['matches']}/{clean_match_id}"
            data = self._make_request(endpoint.replace(APIConfig.OPENDOTA_API_BASE_URL, ""))
            
            if data:
                logger.info(f"Fetched real match details for {clean_match_id}")
                return data
            else:
                logger.warning(f"Could not fetch match details for {clean_match_id}")
                return None
        except Exception as e:
            logger.error(f"Error fetching match details: {str(e)}")
            return None
    
    def fetch_heroes(self) -> List[Dict]:
        """Fetch Dota 2 heroes list - REAL DATA ONLY"""
        try:
            data = self._make_request(
                self.endpoints["heroes"].replace(APIConfig.OPENDOTA_API_BASE_URL, "")
            )
            
            if data and isinstance(data, list) and len(data) > 0:
                logger.info(f"Fetched {len(data)} real heroes from OpenDota")
                return data
            else:
                logger.warning("OpenDota heroes API returned empty data")
                return []
        except Exception as e:
            logger.error(f"Error fetching heroes: {str(e)}")
            return []
    
    def fetch_pro_matches(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Fetch professional Dota 2 matches - REAL DATA"""
        try:
            endpoint = self.endpoints["pro_matches"].replace(APIConfig.OPENDOTA_API_BASE_URL, "")
            data = self._make_request(endpoint, params={"limit": limit})
            
            if data and isinstance(data, list) and len(data) > 0:
                logger.info(f"Fetched {len(data)} real pro matches from OpenDota")
                return self._transform_opendota_matches(data)
            return []
        except Exception as e:
            logger.error(f"Error fetching pro matches: {str(e)}")
            return []
    
    def fetch_match_players(self, match_id: int) -> List[Dict]:
        """Fetch player data from a specific match - REAL DATA"""
        clean_match_id = str(match_id).replace("opendota_", "")
        
        try:
            # Fetch match details which includes player data
            match_details = self.fetch_match_details(int(clean_match_id))
            if match_details and "players" in match_details:
                players = match_details["players"]
                logger.info(f"Fetched {len(players)} real players from match {clean_match_id}")
                return players
            return []
        except Exception as e:
            logger.error(f"Error fetching match players: {str(e)}")
            return []
    
    def _transform_opendota_matches(self, matches: List[Dict]) -> List[Dict[str, Any]]:
        """Transform OpenDota match format to our schema"""
        results = []
        
        for match in matches:
            try:
                # Extract match data
                match_id = match.get('match_id', 0)
                start_time = match.get("start_time", 0)
                
                # Convert timestamp to datetime
                if start_time:
                    match_date = datetime.fromtimestamp(start_time)
                else:
                    match_date = datetime.now()
                
                duration_seconds = match.get("duration", 0)
                duration_minutes = duration_seconds // 60 if duration_seconds else 0
                
                # Determine match type from lobby_type
                lobby_type = match.get("lobby_type", 0)
                match_type_map = {
                    0: "public",
                    1: "practice",
                    2: "tournament",
                    3: "tutorial",
                    4: "coop_bot",
                    5: "team_match",
                    6: "solo_queue",
                    7: "ranked",
                }
                match_type = match_type_map.get(lobby_type, "public")
                
                results.append({
                    "match_id": f"opendota_{match_id}",
                    "game_id": "dota2",
                    "game_name": "Dota 2",
                    "match_date": match_date.isoformat(),
                    "duration_minutes": duration_minutes,
                    "match_type": match_type,
                    "lobby_type": lobby_type,
                    "radiant_win": match.get("radiant_win", False),
                    "platform": "opendota",
                    "source": "opendota_api",
                    # Additional OpenDota-specific data
                    "additional_data": {
                        "game_mode": match.get("game_mode", 0),
                        "radiant_score": match.get("radiant_score", 0),
                        "dire_score": match.get("dire_score", 0),
                        "leagueid": match.get("leagueid"),
                        "series_id": match.get("series_id"),
                        "series_type": match.get("series_type"),
                        "cluster": match.get("cluster"),
                        "region": match.get("region"),
                        "skill": match.get("skill"),
                    }
                })
            except Exception as e:
                logger.warning(f"Error transforming match {match.get('match_id', 'unknown')}: {str(e)}")
                continue
        
        return results
    
    def _generate_mock_dota_matches(self, limit: int) -> List[Dict[str, Any]]:
        """Generate mock Dota 2 match data"""
        results = []
        base_time = datetime.now()
        heroes = ["Pudge", "Invoker", "Crystal Maiden", "Juggernaut", "Phantom Assassin"]
        
        for i in range(limit):
            match_id = f"opendota_{random.randint(700000000, 799999999)}"
            duration = random.randint(20, 60)
            start_time = base_time - timedelta(hours=i)
            
            results.append({
                "match_id": match_id,
                "game_id": "dota2",
                "game_name": "Dota 2",
                "match_date": start_time.isoformat(),
                "duration_minutes": duration,
                "match_type": random.choice(["ranked", "public", "turbo"]),
                "lobby_type": random.randint(0, 7),
                "radiant_win": random.choice([True, False]),
                "most_picked_hero": random.choice(heroes),
                "platform": "opendota",
                "source": "opendota_api",
            })
        
        return results
    
    def _generate_mock_match_details(self, match_id: int) -> Dict:
        """Generate mock match details"""
        return {
            "match_id": match_id,
            "radiant_win": random.choice([True, False]),
            "duration": random.randint(1200, 3600),
            "lobby_type": random.randint(0, 7),
            "game_mode": random.randint(0, 23),
            "players": [
                {
                    "hero_id": random.randint(1, 120),
                    "kills": random.randint(0, 30),
                    "deaths": random.randint(0, 20),
                    "assists": random.randint(0, 30),
                }
                for _ in range(10)
            ]
        }
    
    def _generate_mock_heroes(self) -> List[Dict]:
        """Generate mock heroes list"""
        return [
            {"id": 1, "name": "npc_dota_hero_antimage", "localized_name": "Anti-Mage"},
            {"id": 2, "name": "npc_dota_hero_axe", "localized_name": "Axe"},
            {"id": 3, "name": "npc_dota_hero_bane", "localized_name": "Bane"},
        ]
