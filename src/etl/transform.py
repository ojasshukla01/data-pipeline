"""
ETL Transform Module
Transforms and cleans extracted data
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
import pandas as pd
from src.utils.validators import (
    validate_match_data,
    validate_player_stat_data,
    clean_numeric_value,
)
from src.utils.data_validator import DataValidator
from src.utils.logger import get_logger

logger = get_logger(__name__)


class DataTransformer:
    """Transform and clean data"""
    
    def __init__(self):
        self.logger = logger
    
    def transform_matches(self, raw_matches: List[Dict[str, Any]], game_id: str) -> List[Dict[str, Any]]:
        """Transform match data with API validation"""
        transformed = []
        source = raw_matches[0].get("source", "unknown") if raw_matches else "unknown"
        
        for match in raw_matches:
            try:
                # Validate and transform using DataValidator
                validated = DataValidator.validate_match_data(match, game_id, source)
                
                # Parse match date
                match_date = self._parse_datetime(match.get("match_date") or validated.get("match_date"))
                if not match_date:
                    self.logger.warning(f"Invalid match_date for match {match.get('match_id')}, skipping")
                    continue
                
                # Extract additional data (game-specific fields)
                additional_data = {}
                for key, value in match.items():
                    if key not in ["match_id", "game_id", "match_date", "duration_minutes", 
                                  "match_type", "platform", "source"]:
                        additional_data[key] = value
                
                # Merge validated fields
                transformed_match = {
                    "match_id": str(match.get("match_id", "")),
                    "game_id": game_id,
                    "match_date": match_date,
                    "duration_minutes": clean_numeric_value(validated.get("duration_minutes") or match.get("duration_minutes"), 0),
                    "match_type": str(validated.get("match_type") or match.get("match_type", "unknown")),
                    "platform": str(match.get("platform", "unknown")),
                    "source": str(match.get("source", "unknown")),
                    "additional_data": additional_data if additional_data else None,
                }
                
                # Validate
                if validate_match_data(transformed_match):
                    transformed.append(transformed_match)
                else:
                    self.logger.warning(f"Invalid match data for {match.get('match_id')}, skipping")
            
            except Exception as e:
                self.logger.error(f"Error transforming match {match.get('match_id')}: {str(e)}")
                continue
        
        self.logger.info(f"Transformed {len(transformed)}/{len(raw_matches)} matches for {game_id} (validated with API mapping)")
        return transformed
    
    def transform_player_stats(self, raw_stats: Dict[str, Any], match_id: str) -> Optional[Dict[str, Any]]:
        """Transform player statistics"""
        try:
            transformed = {
                "stat_id": str(raw_stats.get("stat_id", "")),
                "player_id": str(raw_stats.get("player_id", "")),
                "match_id": match_id,
                "kills": int(clean_numeric_value(raw_stats.get("kills"), 0)),
                "deaths": int(clean_numeric_value(raw_stats.get("deaths"), 0)),
                "assists": int(clean_numeric_value(raw_stats.get("assists"), 0)),
                "score": int(clean_numeric_value(raw_stats.get("score"), 0)),
                "rank": int(clean_numeric_value(raw_stats.get("rank"))) if raw_stats.get("rank") else None,
            }
            
            # Extract additional stats
            additional_stats = {}
            for key, value in raw_stats.items():
                if key not in ["stat_id", "player_id", "match_id", "kills", "deaths", 
                              "assists", "score", "rank"]:
                    additional_stats[key] = value
            
            if additional_stats:
                transformed["additional_stats"] = additional_stats
            
            if validate_player_stat_data(transformed):
                return transformed
            else:
                self.logger.warning(f"Invalid player stats for {raw_stats.get('stat_id')}")
                return None
        
        except Exception as e:
            self.logger.error(f"Error transforming player stats: {str(e)}")
            return None
    
    def transform_game_events(self, raw_events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Transform game events"""
        transformed = []
        
        for event in raw_events:
            try:
                event_timestamp = self._parse_datetime(event.get("event_timestamp"))
                if not event_timestamp:
                    continue
                
                transformed_event = {
                    "event_id": str(event.get("event_id", "")),
                    "match_id": str(event.get("match_id", "")),
                    "game_id": str(event.get("game_id", "")),
                    "event_type": str(event.get("event_type", "unknown")),
                    "event_timestamp": event_timestamp,
                    "event_data": event.get("event_data", {}),
                }
                
                transformed.append(transformed_event)
            
            except Exception as e:
                self.logger.error(f"Error transforming event {event.get('event_id')}: {str(e)}")
                continue
        
        return transformed
    
    def _parse_datetime(self, value: Any) -> Optional[datetime]:
        """Parse datetime from various formats"""
        if value is None:
            return None
        
        if isinstance(value, datetime):
            return value
        
        if isinstance(value, (int, float)):
            # Unix timestamp
            try:
                return datetime.fromtimestamp(value)
            except (ValueError, OSError):
                return None
        
        if isinstance(value, str):
            # ISO format or other string formats
            try:
                # Try ISO format
                return datetime.fromisoformat(value.replace('Z', '+00:00'))
            except ValueError:
                try:
                    # Try common formats
                    for fmt in ["%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d"]:
                        try:
                            return datetime.strptime(value, fmt)
                        except ValueError:
                            continue
                except Exception:
                    pass
        
        return None
    
    def deduplicate_matches(self, matches: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate matches based on match_id"""
        seen = set()
        unique_matches = []
        
        for match in matches:
            match_id = match.get("match_id")
            if match_id and match_id not in seen:
                seen.add(match_id)
                unique_matches.append(match)
        
        removed = len(matches) - len(unique_matches)
        if removed > 0:
            self.logger.info(f"Removed {removed} duplicate matches")
        
        return unique_matches
    
    def aggregate_daily_stats(self, matches: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Aggregate daily statistics from matches"""
        if not matches:
            return {}
        
        df = pd.DataFrame(matches)
        df['match_date'] = pd.to_datetime(df['match_date'])
        df['date'] = df['match_date'].dt.date
        
        daily_stats = df.groupby('date').agg({
            'match_id': 'count',
            'duration_minutes': 'mean',
        }).rename(columns={
            'match_id': 'match_count',
            'duration_minutes': 'avg_duration',
        }).to_dict('index')
        
        return daily_stats
