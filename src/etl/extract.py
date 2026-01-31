"""
ETL Extract Module
Extracts data from various gaming APIs
"""
from typing import List, Dict, Any
from src.ingestion import (
    SteamAPIConnector,
    OpenDotaAPIConnector,
    RiotAPIConnector,
    MockDataGenerator,
)
from config.api_config import APIConfig
from src.utils.logger import get_logger

logger = get_logger(__name__)


class DataExtractor:
    """Extract data from various sources"""
    
    def __init__(self):
        self.steam_connector = SteamAPIConnector()
        self.opendota_connector = OpenDotaAPIConnector()
        self.riot_connector = RiotAPIConnector()
        self.mock_generator = MockDataGenerator()
        self.config = APIConfig
    
    def extract_all_games(self, limit_per_game: int = 10) -> Dict[str, List[Dict[str, Any]]]:
        """Extract data from all game sources"""
        results = {}
        
        # Dota 2 - OpenDota
        try:
            logger.info("Extracting Dota 2 data from OpenDota...")
            results["dota2"] = self.opendota_connector.fetch_data(limit=limit_per_game)
            logger.info(f"Extracted {len(results['dota2'])} Dota 2 matches")
        except Exception as e:
            logger.error(f"Error extracting Dota 2 data: {str(e)}")
            results["dota2"] = []
        
        # Dota 2 - Steam (backup)
        try:
            logger.info("Extracting Dota 2 data from Steam...")
            steam_dota = self.steam_connector.fetch_data(game="dota2", limit=limit_per_game)
            if steam_dota:
                results["dota2"].extend(steam_dota)
        except Exception as e:
            logger.error(f"Error extracting Steam Dota 2 data: {str(e)}")
        
        # CS:GO - Steam
        try:
            logger.info("Extracting CS:GO data from Steam...")
            results["csgo"] = self.steam_connector.fetch_data(game="csgo", limit=limit_per_game)
            logger.info(f"Extracted {len(results['csgo'])} CS:GO matches")
        except Exception as e:
            logger.error(f"Error extracting CS:GO data: {str(e)}")
            results["csgo"] = []
        
        # Valorant - Riot
        try:
            logger.info("Extracting Valorant data from Riot...")
            results["valorant"] = self.riot_connector.fetch_data(limit=limit_per_game)
            logger.info(f"Extracted {len(results['valorant'])} Valorant matches")
        except Exception as e:
            logger.error(f"Error extracting Valorant data: {str(e)}")
            results["valorant"] = []
        
        # GTA 5 - Steam
        try:
            logger.info("Extracting GTA 5 data from Steam...")
            results["gta5"] = self.steam_connector.fetch_data(game="gta5", limit=limit_per_game)
            logger.info(f"Extracted {len(results['gta5'])} GTA 5 matches")
        except Exception as e:
            logger.error(f"Error extracting GTA 5 data: {str(e)}")
            results["gta5"] = []
        
        # PUBG - No free API available, skip (no mock data)
        logger.info("PUBG: No free API available - skipping (no mock data)")
        results["pubg"] = []
        
        # COD - No free API available, skip (no mock data)
        logger.info("COD: No free API available - skipping (no mock data)")
        results["cod"] = []
        
        total_matches = sum(len(matches) for matches in results.values())
        logger.info(f"Total extracted matches: {total_matches}")
        
        return results
    
    def extract_game_events(self, game: str, count: int = 20) -> List[Dict[str, Any]]:
        """Extract real-time game events - REAL DATA ONLY"""
        # Only extract real events from APIs, no mock data
        if game == "dota2":
            # Could fetch real events from OpenDota match details
            logger.info("Game events: Using only real API data (no mock)")
        return []
    
    def extract_player_stats(self, game: str, player_id: str, match_id: str) -> Dict[str, Any]:
        """Extract player statistics for a match - REAL DATA ONLY"""
        # This should only be called with real match IDs from APIs
        # No mock data generation
        logger.warning("extract_player_stats called - should use API-specific methods instead")
        return {}
