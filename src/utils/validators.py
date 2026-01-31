"""
Data validation utilities
"""
from typing import Any, Dict, List, Optional
from datetime import datetime
import pandas as pd
from pydantic import BaseModel, validator


class MatchData(BaseModel):
    """Match data validation schema"""
    match_id: str
    game_id: str
    match_date: datetime
    duration_minutes: int
    match_type: str
    
    @validator('duration_minutes')
    def validate_duration(cls, v):
        if v < 0 or v > 300:  # Max 5 hours
            raise ValueError('Duration must be between 0 and 300 minutes')
        return v


class PlayerStatData(BaseModel):
    """Player statistics validation schema"""
    stat_id: Optional[str] = None
    player_id: str
    match_id: str
    kills: int
    deaths: int
    assists: int
    score: int
    rank: Optional[int] = None
    
    @validator('kills', 'deaths', 'assists')
    def validate_non_negative(cls, v):
        if v < 0:
            raise ValueError('Stats must be non-negative')
        return v


def validate_match_data(data: Dict[str, Any]) -> bool:
    """Validate match data"""
    try:
        MatchData(**data)
        return True
    except Exception:
        return False


def validate_player_stat_data(data: Dict[str, Any]) -> bool:
    """Validate player statistics data"""
    try:
        PlayerStatData(**data)
        return True
    except Exception:
        return False


def validate_dataframe(df: pd.DataFrame, required_columns: List[str]) -> bool:
    """Validate DataFrame has required columns"""
    return all(col in df.columns for col in required_columns)


def clean_numeric_value(value: Any, default: float = 0.0) -> float:
    """Clean and convert numeric values"""
    try:
        if pd.isna(value) or value is None:
            return default
        return float(value)
    except (ValueError, TypeError):
        return default
