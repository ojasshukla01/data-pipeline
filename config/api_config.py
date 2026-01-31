"""
API Configuration for Gaming Data Sources
All APIs are free to use (with rate limits)
"""
import os
from typing import Dict, Optional
from dotenv import load_dotenv

load_dotenv()


class APIConfig:
    """Configuration for all gaming APIs"""
    
    # Steam API (Free - requires API key from https://steamcommunity.com/dev/apikey)
    STEAM_API_KEY: Optional[str] = os.getenv("STEAM_API_KEY")
    STEAM_API_BASE_URL: str = os.getenv("STEAM_API_BASE_URL", "https://api.steampowered.com")
    STEAM_RATE_LIMIT: int = 100000  # requests per day (free tier)
    
    # OpenDota API (Free - no key required, but rate limited)
    OPENDOTA_API_BASE_URL: str = os.getenv("OPENDOTA_API_BASE_URL", "https://api.opendota.com/api")
    OPENDOTA_RATE_LIMIT: int = 60  # requests per minute
    
    # Riot Games API (Free tier - requires API key)
    RIOT_API_KEY: Optional[str] = os.getenv("RIOT_API_KEY")
    RIOT_API_BASE_URL: str = os.getenv("RIOT_API_BASE_URL", "https://americas.api.riotgames.com")
    RIOT_RATE_LIMIT: int = 100  # requests per 2 minutes (free tier)
    
    # Mock Data Generator (Custom - no limits)
    # Set to false to disable mock data (recommended - use real APIs only)
    MOCK_DATA_ENABLED: bool = os.getenv("MOCK_DATA_ENABLED", "false").lower() == "true"
    
    @classmethod
    def get_steam_endpoints(cls) -> Dict[str, str]:
        """Steam API endpoints"""
        return {
            "player_stats": f"{cls.STEAM_API_BASE_URL}/ISteamUserStats/GetUserStatsForGame/v0002/",
            "player_summary": f"{cls.STEAM_API_BASE_URL}/ISteamUser/GetPlayerSummaries/v0002/",
            "recent_games": f"{cls.STEAM_API_BASE_URL}/IPlayerService/GetRecentlyPlayedGames/v0001/",
            "game_info": f"{cls.STEAM_API_BASE_URL}/ISteamApps/GetAppList/v2/",
        }
    
    @classmethod
    def get_opendota_endpoints(cls) -> Dict[str, str]:
        """OpenDota API endpoints"""
        return {
            "matches": f"{cls.OPENDOTA_API_BASE_URL}/matches",
            "players": f"{cls.OPENDOTA_API_BASE_URL}/players",
            "heroes": f"{cls.OPENDOTA_API_BASE_URL}/heroes",
            "pro_matches": f"{cls.OPENDOTA_API_BASE_URL}/proMatches",
            "public_matches": f"{cls.OPENDOTA_API_BASE_URL}/publicMatches",
        }
    
    @classmethod
    def get_riot_endpoints(cls) -> Dict[str, str]:
        """Riot Games API endpoints"""
        return {
            "match": f"{cls.RIOT_API_BASE_URL}/val/match/v1/matches/",
            "match_history": f"{cls.RIOT_API_BASE_URL}/val/match/v1/matchlists/by-puuid/",
            "ranked": f"{cls.RIOT_API_BASE_URL}/val/ranked/v1/leaderboards/by-act/",
        }
    
    @classmethod
    def validate_config(cls) -> Dict[str, bool]:
        """Validate API configuration"""
        return {
            "steam_configured": cls.STEAM_API_KEY is not None,
            "opendota_configured": True,  # No key needed
            "riot_configured": cls.RIOT_API_KEY is not None,
            "mock_data_enabled": cls.MOCK_DATA_ENABLED,
        }
