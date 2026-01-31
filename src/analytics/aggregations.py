"""
Analytics Aggregations
"""
from typing import Dict, List, Any
from datetime import datetime, timedelta
from sqlalchemy import text, func
from src.database.db_utils import db_manager
from src.utils.logger import get_logger

logger = get_logger(__name__)


class AnalyticsService:
    """Analytics and aggregation service"""
    
    def get_game_statistics(self, game_id: str, days: int = 7) -> Dict[str, Any]:
        """Get statistics for a game - properly filtered by time period"""
        session = db_manager.get_session()
        
        try:
            start_date = datetime.now() - timedelta(days=days)
            # Format for SQLite compatibility - use ISO format
            start_date_str = start_date.strftime("%Y-%m-%d %H:%M:%S")
            
            # Match statistics - SQLite stores dates as strings, compare directly
            match_query = text("""
                SELECT 
                    COUNT(*) as total_matches,
                    AVG(duration_minutes) as avg_duration,
                    MIN(match_date) as first_match,
                    MAX(match_date) as last_match
                FROM matches
                WHERE game_id = :game_id
                    AND match_date >= :start_date
            """)
            
            match_result = session.execute(match_query, {
                "game_id": game_id,
                "start_date": start_date_str
            }).fetchone()
            
            # Player statistics - properly filtered by time period
            player_query = text("""
                SELECT 
                    COUNT(DISTINCT ps.player_id) as unique_players,
                    AVG(ps.kills) as avg_kills,
                    AVG(ps.deaths) as avg_deaths,
                    AVG(ps.assists) as avg_assists,
                    AVG(ps.score) as avg_score
                FROM player_stats ps
                JOIN matches m ON ps.match_id = m.match_id
                WHERE m.game_id = :game_id
                    AND m.match_date >= :start_date
            """)
            
            player_result = session.execute(player_query, {
                "game_id": game_id,
                "start_date": start_date_str
            }).fetchone()
            
            # Helper function to safely convert dates
            def safe_date_format(date_value):
                if date_value is None:
                    return None
                if isinstance(date_value, str):
                    return date_value
                if hasattr(date_value, 'isoformat'):
                    return date_value.isoformat()
                return str(date_value)
            
            stats = {
                "game_id": game_id,
                "period_days": days,
                "matches": {
                    "total": match_result[0] if match_result else 0,
                    "avg_duration_minutes": float(match_result[1]) if match_result and match_result[1] else 0,
                    "first_match": safe_date_format(match_result[2]) if match_result else None,
                    "last_match": safe_date_format(match_result[3]) if match_result else None,
                },
                "players": {
                    "unique_count": player_result[0] if player_result else 0,
                    "avg_kills": float(player_result[1]) if player_result and player_result[1] else 0,
                    "avg_deaths": float(player_result[2]) if player_result and player_result[2] else 0,
                    "avg_assists": float(player_result[3]) if player_result and player_result[3] else 0,
                    "avg_score": float(player_result[4]) if player_result and player_result[4] else 0,
                }
            }
            
            return stats
        
        except Exception as e:
            logger.error(f"Error getting game statistics: {str(e)}")
            return {}
        finally:
            session.close()
    
    def get_daily_trends(self, game_id: str, days: int = 30) -> List[Dict[str, Any]]:
        """Get daily trends for a game - properly filtered by time period"""
        session = db_manager.get_session()
        
        try:
            start_date = datetime.now() - timedelta(days=days)
            start_date_str = start_date.strftime("%Y-%m-%d %H:%M:%S")
            
            # Use date() function for SQLite compatibility
            query = text("""
                SELECT 
                    date(m.match_date) as date,
                    COUNT(DISTINCT m.match_id) as match_count,
                    COUNT(DISTINCT ps.player_id) as player_count,
                    AVG(m.duration_minutes) as avg_duration,
                    AVG(ps.kills) as avg_kills
                FROM matches m
                LEFT JOIN player_stats ps ON m.match_id = ps.match_id
                WHERE m.game_id = :game_id
                    AND m.match_date >= :start_date
                GROUP BY date(m.match_date)
                ORDER BY date
            """)
            
            result = session.execute(query, {
                "game_id": game_id,
                "start_date": start_date_str
            })
            
            trends = []
            for row in result:
                # Handle date - SQLite returns strings, not datetime objects
                date_value = row[0]
                if isinstance(date_value, datetime):
                    date_str = date_value.isoformat()
                elif isinstance(date_value, str):
                    date_str = date_value
                else:
                    date_str = str(date_value)
                
                trends.append({
                    "date": date_str,
                    "match_count": row[1],
                    "player_count": row[2] if row[2] else 0,
                    "avg_duration_minutes": float(row[3]) if row[3] else 0,
                    "avg_kills": float(row[4]) if row[4] else 0,
                })
            
            return trends
        
        except Exception as e:
            logger.error(f"Error getting daily trends: {str(e)}")
            return []
        finally:
            session.close()
    
    def get_top_players(self, game_id: str, days: int = 30, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top players by score - filtered by time period"""
        session = db_manager.get_session()
        
        try:
            start_date = datetime.now() - timedelta(days=days)
            start_date_str = start_date.strftime("%Y-%m-%d %H:%M:%S")
            
            query = text("""
                SELECT 
                    ps.player_id,
                    COUNT(*) as match_count,
                    SUM(ps.kills) as total_kills,
                    SUM(ps.deaths) as total_deaths,
                    SUM(ps.assists) as total_assists,
                    AVG(ps.kills) as avg_kills,
                    AVG(ps.deaths) as avg_deaths,
                    AVG(ps.assists) as avg_assists,
                    AVG(ps.score) as avg_score,
                    MAX(ps.score) as max_score
                FROM player_stats ps
                JOIN matches m ON ps.match_id = m.match_id
                WHERE m.game_id = :game_id
                    AND m.match_date >= :start_date
                GROUP BY ps.player_id
                ORDER BY avg_score DESC
                LIMIT :limit
            """)
            
            result = session.execute(query, {
                "game_id": game_id,
                "start_date": start_date_str,
                "limit": limit
            })
            
            players = []
            for row in result:
                # Get player name if available
                player_name = f"Player {row[0]}"  # Default name
                try:
                    player_query = text("SELECT player_name FROM players WHERE player_id = :player_id")
                    player_result = session.execute(player_query, {"player_id": row[0]}).fetchone()
                    if player_result and player_result[0]:
                        player_name = player_result[0]
                except:
                    pass
                
                players.append({
                    "player_id": row[0],
                    "player_name": player_name,
                    "match_count": row[1],
                    "total_kills": int(row[2]) if row[2] else 0,
                    "total_deaths": int(row[3]) if row[3] else 0,
                    "total_assists": int(row[4]) if row[4] else 0,
                    "avg_kills": float(row[5]) if row[5] else 0,
                    "avg_deaths": float(row[6]) if row[6] else 0,
                    "avg_assists": float(row[7]) if row[7] else 0,
                    "avg_score": float(row[8]) if row[8] else 0,
                    "max_score": float(row[9]) if row[9] else 0,
                })
            
            return players
        
        except Exception as e:
            logger.error(f"Error getting top players: {str(e)}")
            return []
        finally:
            session.close()
