"""
Database Models using SQLAlchemy
"""
from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy import Column, String, Integer, DateTime, DECIMAL, JSON, ForeignKey, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Game(Base):
    """Games table model"""
    __tablename__ = "games"
    
    game_id = Column(String(50), primary_key=True)
    game_name = Column(String(100), nullable=False)
    platform = Column(String(50))
    genre = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "game_id": self.game_id,
            "game_name": self.game_name,
            "platform": self.platform,
            "genre": self.genre,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Player(Base):
    """Players table model"""
    __tablename__ = "players"
    
    player_id = Column(String(100), primary_key=True)
    username = Column(String(100))
    game_id = Column(String(50), ForeignKey("games.game_id"))
    platform_id = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "player_id": self.player_id,
            "username": self.username,
            "game_id": self.game_id,
            "platform_id": self.platform_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Match(Base):
    """Matches table model"""
    __tablename__ = "matches"
    
    match_id = Column(String(100), primary_key=True)
    game_id = Column(String(50), ForeignKey("games.game_id"), nullable=False)
    match_date = Column(DateTime, nullable=False)
    duration_minutes = Column(Integer)
    match_type = Column(String(50))
    platform = Column(String(50))
    source = Column(String(50))
    additional_data = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index("idx_matches_game_id", "game_id"),
        Index("idx_matches_match_date", "match_date"),
    )
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "match_id": self.match_id,
            "game_id": self.game_id,
            "match_date": self.match_date.isoformat() if self.match_date else None,
            "duration_minutes": self.duration_minutes,
            "match_type": self.match_type,
            "platform": self.platform,
            "source": self.source,
            "additional_data": self.additional_data,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class PlayerStat(Base):
    """Player statistics table model"""
    __tablename__ = "player_stats"
    
    stat_id = Column(String(100), primary_key=True)
    player_id = Column(String(100), ForeignKey("players.player_id"), nullable=False)
    match_id = Column(String(100), ForeignKey("matches.match_id"), nullable=False)
    kills = Column(Integer, default=0)
    deaths = Column(Integer, default=0)
    assists = Column(Integer, default=0)
    score = Column(Integer, default=0)
    rank = Column(Integer)
    additional_stats = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index("idx_player_stats_player_id", "player_id"),
        Index("idx_player_stats_match_id", "match_id"),
    )
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "stat_id": self.stat_id,
            "player_id": self.player_id,
            "match_id": self.match_id,
            "kills": self.kills,
            "deaths": self.deaths,
            "assists": self.assists,
            "score": self.score,
            "rank": self.rank,
            "additional_stats": self.additional_stats,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class GameEvent(Base):
    """Game events table model"""
    __tablename__ = "game_events"
    
    event_id = Column(String(100), primary_key=True)
    match_id = Column(String(100), ForeignKey("matches.match_id"), nullable=False)
    game_id = Column(String(50), ForeignKey("games.game_id"), nullable=False)
    event_type = Column(String(50), nullable=False)
    event_timestamp = Column(DateTime, nullable=False)
    event_data = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index("idx_game_events_match_id", "match_id"),
        Index("idx_game_events_event_timestamp", "event_timestamp"),
    )
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "match_id": self.match_id,
            "game_id": self.game_id,
            "event_type": self.event_type,
            "event_timestamp": self.event_timestamp.isoformat() if self.event_timestamp else None,
            "event_data": self.event_data,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Forecast(Base):
    """Forecasts table model"""
    __tablename__ = "forecasts"
    
    forecast_id = Column(String(100), primary_key=True)
    game_id = Column(String(50), ForeignKey("games.game_id"), nullable=False)
    forecast_date = Column(DateTime, nullable=False)
    predicted_metric = Column(String(100), nullable=False)
    predicted_value = Column(DECIMAL(15, 2))
    confidence_interval_lower = Column(DECIMAL(15, 2))
    confidence_interval_upper = Column(DECIMAL(15, 2))
    model_version = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index("idx_forecasts_game_id", "game_id"),
        Index("idx_forecasts_forecast_date", "forecast_date"),
    )
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "forecast_id": self.forecast_id,
            "game_id": self.game_id,
            "forecast_date": self.forecast_date.isoformat() if self.forecast_date else None,
            "predicted_metric": self.predicted_metric,
            "predicted_value": float(self.predicted_value) if self.predicted_value else None,
            "confidence_interval_lower": float(self.confidence_interval_lower) if self.confidence_interval_lower else None,
            "confidence_interval_upper": float(self.confidence_interval_upper) if self.confidence_interval_upper else None,
            "model_version": self.model_version,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
