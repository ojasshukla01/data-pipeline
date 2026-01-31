"""
Game-Specific Analytics
Different metrics and calculations for each game
"""
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy import text
from src.database.db_utils import db_manager
from src.utils.logger import get_logger

logger = get_logger(__name__)


class GameSpecificAnalytics:
    """Game-specific analytics and metrics"""
    
    def get_dota2_metrics(self, days: int = 7) -> Dict[str, Any]:
        """Dota 2 specific metrics"""
        session = db_manager.get_session()
        
        try:
            start_date = datetime.now() - timedelta(days=days)
            start_date_str = start_date.strftime("%Y-%m-%d %H:%M:%S")
            
            # Match type distribution (simplified for SQLite compatibility)
            match_type_query = text("""
                SELECT 
                    match_type,
                    COUNT(*) as count,
                    AVG(duration_minutes) as avg_duration,
                    SUM(CASE WHEN additional_data LIKE '%"radiant_win": true%' THEN 1 ELSE 0 END) as radiant_wins
                FROM matches
                WHERE game_id = 'dota2'
                    AND match_date >= :start_date
                    AND source = 'opendota_api'
                GROUP BY match_type
            """)
            
            match_type_result = session.execute(match_type_query, {"start_date": start_date_str})
            
            # Get radiant win rate
            win_rate_query = text("""
                SELECT 
                    COUNT(*) as total_matches,
                    SUM(CASE WHEN additional_data LIKE '%"radiant_win": true%' THEN 1 ELSE 0 END) as radiant_wins
                FROM matches
                WHERE game_id = 'dota2'
                    AND match_date >= :start_date
                    AND source = 'opendota_api'
            """)
            win_rate_result = session.execute(win_rate_query, {"start_date": start_date_str}).fetchone()
            
            metrics = {
                "game_id": "dota2",
                "game_name": "Dota 2",
                "match_types": [
                    {
                        "type": row[0] or "unknown",
                        "count": row[1],
                        "avg_duration": float(row[2]) if row[2] else 0,
                        "radiant_wins": row[3] if row[3] else 0,
                    }
                    for row in match_type_result
                ],
                "win_rate": {
                    "total_matches": win_rate_result[0] if win_rate_result else 0,
                    "radiant_wins": win_rate_result[1] if win_rate_result else 0,
                    "radiant_win_rate": (win_rate_result[1] / win_rate_result[0] * 100) if win_rate_result and win_rate_result[0] > 0 else 0,
                } if win_rate_result else {},
            }
            
            return metrics
        
        except Exception as e:
            logger.error(f"Error getting Dota 2 metrics: {str(e)}")
            return {}
        finally:
            session.close()
    
    def get_csgo_metrics(self, days: int = 7) -> Dict[str, Any]:
        """CS:GO specific metrics"""
        session = db_manager.get_session()
        
        try:
            start_date = datetime.now() - timedelta(days=days)
            start_date_str = start_date.strftime("%Y-%m-%d %H:%M:%S")
            
            # CS:GO specific stats
            query = text("""
                SELECT 
                    match_type,
                    COUNT(*) as match_count,
                    AVG(duration_minutes) as avg_duration,
                    AVG(ps.kills) as avg_kills,
                    AVG(ps.deaths) as avg_deaths,
                    AVG(ps.assists) as avg_assists,
                    AVG(ps.score) as avg_score
                FROM matches m
                LEFT JOIN player_stats ps ON m.match_id = ps.match_id
                WHERE m.game_id = 'csgo'
                    AND m.match_date >= :start_date
                GROUP BY match_type
            """)
            
            result = session.execute(query, {"start_date": start_date_str})
            
            metrics = {
                "game_id": "csgo",
                "game_name": "CS:GO",
                "match_types": [
                    {
                        "type": row[0] or "unknown",
                        "match_count": row[1],
                        "avg_duration": float(row[2]) if row[2] else 0,
                        "avg_kills": float(row[3]) if row[3] else 0,
                        "avg_deaths": float(row[4]) if row[4] else 0,
                        "avg_assists": float(row[5]) if row[5] else 0,
                        "avg_score": float(row[6]) if row[6] else 0,
                    }
                    for row in result
                ],
            }
            
            return metrics
        
        except Exception as e:
            logger.error(f"Error getting CS:GO metrics: {str(e)}")
            return {}
        finally:
            session.close()
    
    def get_valorant_metrics(self, days: int = 7) -> Dict[str, Any]:
        """Valorant specific metrics"""
        session = db_manager.get_session()
        
        try:
            start_date = datetime.now() - timedelta(days=days)
            start_date_str = start_date.strftime("%Y-%m-%d %H:%M:%S")
            
            # Valorant specific stats (simplified for SQLite)
            query = text("""
                SELECT 
                    match_type,
                    COUNT(*) as match_count,
                    AVG(duration_minutes) as avg_duration
                FROM matches
                WHERE game_id = 'valorant'
                    AND match_date >= :start_date
                GROUP BY match_type
            """)
            
            result = session.execute(query, {"start_date": start_date_str})
            
            metrics = {
                "game_id": "valorant",
                "game_name": "Valorant",
                "match_types": [
                    {
                        "type": row[0] or "unknown",
                        "match_count": row[1],
                        "avg_duration": float(row[2]) if row[2] else 0,
                    }
                    for row in result
                ],
            }
            
            return metrics
        
        except Exception as e:
            logger.error(f"Error getting Valorant metrics: {str(e)}")
            return {}
        finally:
            session.close()
    
    def get_pubg_metrics(self, days: int = 7) -> Dict[str, Any]:
        """PUBG specific metrics"""
        session = db_manager.get_session()
        
        try:
            start_date = datetime.now() - timedelta(days=days)
            start_date_str = start_date.strftime("%Y-%m-%d %H:%M:%S")
            
            query = text("""
                SELECT 
                    match_type,
                    COUNT(*) as match_count,
                    AVG(duration_minutes) as avg_duration
                FROM matches
                WHERE game_id = 'pubg'
                    AND match_date >= :start_date
                GROUP BY match_type
            """)
            
            result = session.execute(query, {"start_date": start_date_str})
            
            metrics = {
                "game_id": "pubg",
                "game_name": "PUBG",
                "match_types": [
                    {
                        "type": row[0] or "unknown",
                        "match_count": row[1],
                        "avg_duration": float(row[2]) if row[2] else 0,
                    }
                    for row in result
                ],
            }
            
            return metrics
        
        except Exception as e:
            logger.error(f"Error getting PUBG metrics: {str(e)}")
            return {}
        finally:
            session.close()
    
    def get_game_specific_metrics(self, game_id: str, days: int = 7) -> Dict[str, Any]:
        """Get game-specific metrics based on game ID"""
        game_analytics = {
            "dota2": self.get_dota2_metrics,
            "csgo": self.get_csgo_metrics,
            "valorant": self.get_valorant_metrics,
            "pubg": self.get_pubg_metrics,
        }
        
        analytics_func = game_analytics.get(game_id)
        if analytics_func:
            return analytics_func(days)
        
        # Default metrics for other games
        return {
            "game_id": game_id,
            "message": "Game-specific analytics not yet implemented",
        }
