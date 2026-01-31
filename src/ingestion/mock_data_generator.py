"""
Mock Data Generator
Generates realistic gaming data for PUBG, COD, and other games
when APIs are unavailable or for testing
"""
from typing import Dict, List, Any
from datetime import datetime, timedelta
import random
import uuid
from src.utils.logger import get_logger

logger = get_logger(__name__)


class MockDataGenerator:
    """Generate mock gaming data for various games"""
    
    GAMES = {
        "pubg": {
            "name": "PUBG",
            "maps": ["Erangel", "Miramar", "Sanhok", "Vikendi", "Karakin"],
            "modes": ["solo", "duo", "squad"],
        },
        "cod": {
            "name": "Call of Duty",
            "modes": ["warzone", "multiplayer", "zombies"],
            "maps": ["Verdansk", "Rebirth Island", "Caldera"],
        },
        "gta5": {
            "name": "Grand Theft Auto V",
            "modes": ["online", "heist", "race", "deathmatch"],
        },
    }
    
    def __init__(self):
        self.logger = logger
    
    def generate_match_data(self, game: str, count: int = 10) -> List[Dict[str, Any]]:
        """Generate mock match data for a game"""
        game_config = self.GAMES.get(game.lower())
        if not game_config:
            self.logger.warning(f"Unknown game: {game}, using default config")
            game_config = {"name": game.upper(), "modes": ["default"], "maps": ["default"]}
        
        results = []
        base_time = datetime.now()
        
        for i in range(count):
            match_id = f"mock_{game}_{uuid.uuid4().hex[:8]}"
            start_time = base_time - timedelta(minutes=i * 15)
            
            match_data = {
                "match_id": match_id,
                "game_id": game.lower(),
                "game_name": game_config["name"],
                "match_date": start_time.isoformat(),
                "duration_minutes": random.randint(15, 60),
                "match_type": random.choice(game_config.get("modes", ["default"])),
                "platform": "mock",
                "source": "mock_generator",
            }
            
            # Add game-specific fields
            if "maps" in game_config:
                match_data["map"] = random.choice(game_config["maps"])
            
            if game.lower() == "pubg":
                match_data.update({
                    "players_alive_start": random.randint(80, 100),
                    "players_alive_end": random.randint(1, 10),
                    "placement": random.randint(1, 100),
                })
            elif game.lower() == "cod":
                match_data.update({
                    "kills": random.randint(0, 30),
                    "deaths": random.randint(0, 20),
                    "assists": random.randint(0, 15),
                    "score": random.randint(1000, 10000),
                })
            elif game.lower() == "gta5":
                match_data.update({
                    "mission_type": random.choice(["heist", "race", "deathmatch", "freeroam"]),
                    "players_count": random.randint(2, 30),
                    "reward": random.randint(1000, 50000),
                })
            
            results.append(match_data)
        
        return results
    
    def generate_player_stats(self, game: str, player_id: str, match_id: str) -> Dict[str, Any]:
        """Generate mock player statistics"""
        base_stats = {
            "stat_id": f"stat_{uuid.uuid4().hex[:8]}",
            "player_id": player_id,
            "match_id": match_id,
            "kills": random.randint(0, 30),
            "deaths": random.randint(0, 20),
            "assists": random.randint(0, 20),
            "score": random.randint(100, 10000),
            "rank": random.randint(1, 100),
        }
        
        # Game-specific stats
        if game.lower() == "pubg":
            base_stats.update({
                "damage_dealt": random.randint(0, 5000),
                "survival_time": random.randint(0, 1800),
                "headshots": random.randint(0, 10),
            })
        elif game.lower() == "cod":
            base_stats.update({
                "accuracy": round(random.uniform(0.1, 0.8), 2),
                "headshots": random.randint(0, 15),
                "streak": random.randint(0, 10),
            })
        elif game.lower() == "dota2":
            base_stats.update({
                "hero": random.choice(["Pudge", "Invoker", "Juggernaut", "Phantom Assassin"]),
                "gold": random.randint(1000, 50000),
                "xp": random.randint(1000, 30000),
            })
        elif game.lower() == "valorant":
            base_stats.update({
                "agent": random.choice(["Jett", "Reyna", "Sage", "Cypher"]),
                "headshots": random.randint(0, 20),
                "first_bloods": random.randint(0, 5),
            })
        
        return base_stats
    
    def generate_realtime_events(self, game: str, count: int = 20) -> List[Dict[str, Any]]:
        """Generate real-time gaming events"""
        events = []
        base_time = datetime.now()
        event_types = ["kill", "death", "assist", "objective", "round_start", "round_end"]
        
        for i in range(count):
            event_time = base_time - timedelta(seconds=random.randint(0, 300))
            events.append({
                "event_id": f"event_{uuid.uuid4().hex[:8]}",
                "game_id": game.lower(),
                "match_id": f"match_{random.randint(1000, 9999)}",
                "event_type": random.choice(event_types),
                "event_timestamp": event_time.isoformat(),
                "event_data": {
                    "player_id": f"player_{random.randint(1, 100)}",
                    "value": random.randint(1, 100),
                    "location": f"location_{random.randint(1, 50)}",
                },
            })
        
        return events
    
    def generate_forecast_data(self, game: str, days: int = 7) -> List[Dict[str, Any]]:
        """Generate forecast/prediction data"""
        forecasts = []
        base_time = datetime.now()
        metrics = ["player_count", "match_count", "average_duration", "popularity_score"]
        
        for i in range(days):
            forecast_date = base_time + timedelta(days=i)
            for metric in metrics:
                base_value = random.randint(100, 10000)
                forecasts.append({
                    "forecast_id": f"forecast_{uuid.uuid4().hex[:8]}",
                    "game_id": game.lower(),
                    "forecast_date": forecast_date.isoformat(),
                    "predicted_metric": metric,
                    "predicted_value": base_value,
                    "confidence_interval_lower": int(base_value * 0.8),
                    "confidence_interval_upper": int(base_value * 1.2),
                    "model_version": "1.0",
                })
        
        return forecasts
