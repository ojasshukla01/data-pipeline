"""
Data Validation and Transformation
Ensures API data matches database and dashboard displays correctly
"""
from typing import Dict, List, Any, Optional
from datetime import datetime
from src.utils.logger import get_logger

logger = get_logger(__name__)


class DataValidator:
    """Validates and transforms data to ensure accuracy"""
    
    # API attribute mappings to database fields
    API_FIELD_MAPPINGS = {
        "dota2": {
            "opendota": {
                "match_id": "match_id",
                "start_time": "match_date",
                "duration": "duration_minutes",
                "lobby_type": "match_type",
                "radiant_win": "radiant_win",
                "game_mode": "game_mode",
                "radiant_score": "radiant_score",
                "dire_score": "dire_score",
                "cluster": "cluster",
                "region": "region",
                "skill": "skill",
            },
            "player_fields": {
                "account_id": "player_id",
                "kills": "kills",
                "deaths": "deaths",
                "assists": "assists",
                "total_gold": "score",
                "hero_id": "hero_id",
                "gold_per_min": "gold_per_min",
                "xp_per_min": "xp_per_min",
                "last_hits": "last_hits",
                "denies": "denies",
                "net_worth": "net_worth",
                "hero_damage": "hero_damage",
                "tower_damage": "tower_damage",
            }
        },
        "csgo": {
            "steam": {
                "match_id": "match_id",
                "duration": "duration_minutes",
                "match_type": "match_type",
            }
        },
        "valorant": {
            "riot": {
                "match_id": "match_id",
                "game_start_time": "match_date",
                "match_info": "match_type",
                "teams": "score_data",
            }
        }
    }
    
    @staticmethod
    def validate_match_data(match_data: Dict, game_id: str, source: str) -> Dict[str, Any]:
        """Validate and transform match data from API"""
        mapping = DataValidator.API_FIELD_MAPPINGS.get(game_id, {}).get(source, {})
        
        validated = {}
        errors = []
        
        # Required fields
        required_fields = ["match_id", "game_id", "match_date"]
        
        for field in required_fields:
            if field not in match_data:
                errors.append(f"Missing required field: {field}")
        
        # Transform fields according to mapping
        for api_field, db_field in mapping.items():
            if api_field in match_data:
                validated[db_field] = match_data[api_field]
        
        # Validate data types
        if "match_date" in validated:
            if isinstance(validated["match_date"], (int, float)):
                validated["match_date"] = datetime.fromtimestamp(validated["match_date"])
            elif isinstance(validated["match_date"], str):
                try:
                    validated["match_date"] = datetime.fromisoformat(validated["match_date"])
                except:
                    errors.append(f"Invalid date format: {validated['match_date']}")
        
        if "duration_minutes" in validated:
            if isinstance(validated["duration_minutes"], (int, float)):
                validated["duration_minutes"] = int(validated["duration_minutes"] / 60) if validated["duration_minutes"] > 60 else int(validated["duration_minutes"])
        
        if errors:
            logger.warning(f"Validation errors for {game_id} match: {errors}")
        
        return validated
    
    @staticmethod
    def validate_player_stats(player_data: Dict, game_id: str) -> Dict[str, Any]:
        """Validate and transform player stats from API"""
        mapping = DataValidator.API_FIELD_MAPPINGS.get(game_id, {}).get("player_fields", {})
        
        validated = {}
        
        for api_field, db_field in mapping.items():
            if api_field in player_data:
                validated[db_field] = player_data[api_field]
        
        # Ensure numeric fields are numbers
        numeric_fields = ["kills", "deaths", "assists", "score"]
        for field in numeric_fields:
            if field in validated:
                try:
                    validated[field] = float(validated[field]) if validated[field] is not None else 0
                except (ValueError, TypeError):
                    validated[field] = 0
        
        return validated
    
    @staticmethod
    def compare_api_vs_database(api_data: Dict, db_data: Dict, game_id: str) -> Dict[str, Any]:
        """Compare API data with database to ensure accuracy"""
        differences = []
        matches = []
        
        # Compare key fields
        key_fields = ["match_id", "duration_minutes", "match_type"]
        
        for field in key_fields:
            api_value = api_data.get(field)
            db_value = db_data.get(field)
            
            if api_value != db_value:
                differences.append({
                    "field": field,
                    "api_value": api_value,
                    "db_value": db_value
                })
            else:
                matches.append(field)
        
        return {
            "matches": matches,
            "differences": differences,
            "accuracy": len(matches) / len(key_fields) * 100 if key_fields else 0
        }
    
    @staticmethod
    def get_validation_summary(game_id: str, source: str) -> Dict[str, Any]:
        """Get validation summary for a game"""
        mapping = DataValidator.API_FIELD_MAPPINGS.get(game_id, {}).get(source, {})
        
        return {
            "game_id": game_id,
            "source": source,
            "mapped_fields": list(mapping.keys()),
            "total_fields": len(mapping),
        }
