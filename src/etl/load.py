"""
ETL Load Module
Loads transformed data into the database
"""
from typing import List, Dict, Any, Optional
from sqlalchemy.exc import IntegrityError
from sqlalchemy import text
from src.database.db_utils import db_manager
from src.database.models import Match, PlayerStat, GameEvent, Player
from src.utils.logger import get_logger

logger = get_logger(__name__)


class DataLoader:
    """Load data into the database"""
    
    def __init__(self):
        self.db = db_manager
        self.logger = logger
    
    def load_matches(self, matches: List[Dict[str, Any]], batch_size: int = 100) -> Dict[str, int]:
        """Load matches into database"""
        session = self.db.get_session()
        stats = {"inserted": 0, "updated": 0, "errors": 0}
        
        try:
            for i in range(0, len(matches), batch_size):
                batch = matches[i:i + batch_size]
                
                for match_data in batch:
                    try:
                        # Check if match exists
                        existing = session.query(Match).filter(
                            Match.match_id == match_data["match_id"]
                        ).first()
                        
                        if existing:
                            # Update existing match
                            for key, value in match_data.items():
                                if key != "match_id":
                                    setattr(existing, key, value)
                            stats["updated"] += 1
                        else:
                            # Insert new match
                            match = Match(**match_data)
                            session.add(match)
                            stats["inserted"] += 1
                    
                    except IntegrityError as e:
                        session.rollback()
                        self.logger.warning(f"Integrity error for match {match_data.get('match_id')}: {str(e)}")
                        stats["errors"] += 1
                        continue
                    except Exception as e:
                        session.rollback()
                        self.logger.error(f"Error loading match {match_data.get('match_id')}: {str(e)}")
                        stats["errors"] += 1
                        continue
                
                # Commit batch
                try:
                    session.commit()
                    self.logger.info(f"Loaded batch {i//batch_size + 1}: {len(batch)} matches")
                except Exception as e:
                    session.rollback()
                    self.logger.error(f"Error committing batch: {str(e)}")
                    stats["errors"] += len(batch)
        
        except Exception as e:
            session.rollback()
            self.logger.error(f"Error loading matches: {str(e)}")
            raise
        finally:
            session.close()
        
        self.logger.info(f"Match loading complete: {stats}")
        return stats
    
    def load_player_stats(self, stats: List[Dict[str, Any]], batch_size: int = 100) -> Dict[str, int]:
        """Load player statistics into database"""
        session = self.db.get_session()
        result_stats = {"inserted": 0, "updated": 0, "errors": 0}
        
        try:
            for i in range(0, len(stats), batch_size):
                batch = stats[i:i + batch_size]
                
                for stat_data in batch:
                    try:
                        # Check if stat exists
                        existing = session.query(PlayerStat).filter(
                            PlayerStat.stat_id == stat_data["stat_id"]
                        ).first()
                        
                        if existing:
                            # Update existing stat
                            for key, value in stat_data.items():
                                if key != "stat_id":
                                    setattr(existing, key, value)
                            result_stats["updated"] += 1
                        else:
                            # Insert new stat
                            stat = PlayerStat(**stat_data)
                            session.add(stat)
                            result_stats["inserted"] += 1
                    
                    except IntegrityError as e:
                        session.rollback()
                        self.logger.warning(f"Integrity error for stat {stat_data.get('stat_id')}: {str(e)}")
                        result_stats["errors"] += 1
                        continue
                    except Exception as e:
                        session.rollback()
                        self.logger.error(f"Error loading stat {stat_data.get('stat_id')}: {str(e)}")
                        result_stats["errors"] += 1
                        continue
                
                # Commit batch
                try:
                    session.commit()
                except Exception as e:
                    session.rollback()
                    self.logger.error(f"Error committing stats batch: {str(e)}")
                    result_stats["errors"] += len(batch)
        
        except Exception as e:
            session.rollback()
            self.logger.error(f"Error loading player stats: {str(e)}")
            raise
        finally:
            session.close()
        
        self.logger.info(f"Player stats loading complete: {result_stats}")
        return result_stats
    
    def load_game_events(self, events: List[Dict[str, Any]], batch_size: int = 100) -> Dict[str, int]:
        """Load game events into database"""
        session = self.db.get_session()
        stats = {"inserted": 0, "errors": 0}
        
        try:
            for i in range(0, len(events), batch_size):
                batch = events[i:i + batch_size]
                
                for event_data in batch:
                    try:
                        event = GameEvent(**event_data)
                        session.add(event)
                        stats["inserted"] += 1
                    except Exception as e:
                        self.logger.error(f"Error loading event {event_data.get('event_id')}: {str(e)}")
                        stats["errors"] += 1
                        continue
                
                try:
                    session.commit()
                except Exception as e:
                    session.rollback()
                    self.logger.error(f"Error committing events batch: {str(e)}")
                    stats["errors"] += len(batch)
        
        except Exception as e:
            session.rollback()
            self.logger.error(f"Error loading game events: {str(e)}")
            raise
        finally:
            session.close()
        
        self.logger.info(f"Game events loading complete: {stats}")
        return stats
    
    def upsert_player(self, player_data: Dict[str, Any]) -> bool:
        """Insert or update player"""
        session = self.db.get_session()
        
        try:
            existing = session.query(Player).filter(
                Player.player_id == player_data["player_id"]
            ).first()
            
            if existing:
                for key, value in player_data.items():
                    if key != "player_id":
                        setattr(existing, key, value)
            else:
                player = Player(**player_data)
                session.add(player)
            
            session.commit()
            return True
        
        except Exception as e:
            session.rollback()
            self.logger.error(f"Error upserting player: {str(e)}")
            return False
        finally:
            session.close()
