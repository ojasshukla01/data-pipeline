"""
All Games Comparison Analytics
Shows comparison between all games
"""
from typing import Dict, List, Any
from datetime import datetime, timedelta
from sqlalchemy import text
from src.database.db_utils import db_manager
from src.utils.logger import get_logger

logger = get_logger(__name__)


class ComparisonAnalytics:
    """Analytics for comparing all games"""
    
    def get_all_games_comparison(self, days: int = 7) -> Dict[str, Any]:
        """Get comparison statistics for all games"""
        session = db_manager.get_session()
        
        try:
            start_date = datetime.now() - timedelta(days=days)
            start_date_str = start_date.strftime("%Y-%m-%d %H:%M:%S")
            
            # Get stats for all games
            query = text("""
                SELECT 
                    m.game_id,
                    COUNT(DISTINCT m.match_id) as total_matches,
                    COUNT(DISTINCT ps.player_id) as unique_players,
                    AVG(m.duration_minutes) as avg_duration,
                    AVG(ps.kills) as avg_kills,
                    AVG(ps.deaths) as avg_deaths,
                    AVG(ps.assists) as avg_assists,
                    AVG(ps.score) as avg_score,
                    MIN(m.match_date) as first_match,
                    MAX(m.match_date) as last_match
                FROM matches m
                LEFT JOIN player_stats ps ON m.match_id = ps.match_id
                WHERE m.match_date >= :start_date
                GROUP BY m.game_id
                ORDER BY total_matches DESC
            """)
            
            result = session.execute(query, {"start_date": start_date_str})
            
            games_data = []
            for row in result:
                games_data.append({
                    "game_id": row[0],
                    "game_name": self._get_game_name(row[0]),
                    "total_matches": row[1],
                    "unique_players": row[2] if row[2] else 0,
                    "avg_duration": float(row[3]) if row[3] else 0,
                    "avg_kills": float(row[4]) if row[4] else 0,
                    "avg_deaths": float(row[5]) if row[5] else 0,
                    "avg_assists": float(row[6]) if row[6] else 0,
                    "avg_score": float(row[7]) if row[7] else 0,
                    "first_match": str(row[8]) if row[8] else None,
                    "last_match": str(row[9]) if row[9] else None,
                })
            
            # Get game names
            game_names_query = text("SELECT game_id, game_name FROM games")
            game_names = {row[0]: row[1] for row in session.execute(game_names_query)}
            
            # Update game names
            for game in games_data:
                if game["game_id"] in game_names:
                    game["game_name"] = game_names[game["game_id"]]
            
            return {
                "period_days": days,
                "games": games_data,
                "total_games": len(games_data),
                "summary": {
                    "total_matches_all": sum(g["total_matches"] for g in games_data),
                    "total_players_all": sum(g["unique_players"] for g in games_data),
                    "avg_duration_all": sum(g["avg_duration"] for g in games_data) / len(games_data) if games_data else 0,
                }
            }
        
        except Exception as e:
            logger.error(f"Error getting all games comparison: {str(e)}")
            return {}
        finally:
            session.close()
    
    def get_game_trends_comparison(self, days: int = 30) -> Dict[str, Any]:
        """Get daily trends comparison for all games"""
        session = db_manager.get_session()
        
        try:
            start_date = datetime.now() - timedelta(days=days)
            start_date_str = start_date.strftime("%Y-%m-%d %H:%M:%S")
            
            query = text("""
                SELECT 
                    date(m.match_date) as date,
                    m.game_id,
                    COUNT(DISTINCT m.match_id) as match_count,
                    COUNT(DISTINCT ps.player_id) as player_count
                FROM matches m
                LEFT JOIN player_stats ps ON m.match_id = ps.match_id
                WHERE m.match_date >= :start_date
                GROUP BY date(m.match_date), m.game_id
                ORDER BY date, m.game_id
            """)
            
            result = session.execute(query, {"start_date": start_date_str})
            
            trends_by_game = {}
            for row in result:
                date_str = str(row[0])
                game_id = row[1]
                
                if game_id not in trends_by_game:
                    trends_by_game[game_id] = []
                
                trends_by_game[game_id].append({
                    "date": date_str,
                    "match_count": row[2],
                    "player_count": row[3] if row[3] else 0,
                })
            
            return trends_by_game
        
        except Exception as e:
            logger.error(f"Error getting game trends comparison: {str(e)}")
            return {}
        finally:
            session.close()
    
    def _get_game_name(self, game_id: str) -> str:
        """Get game name from game_id"""
        game_names = {
            "dota2": "Dota 2",
            "csgo": "CS:GO",
            "valorant": "Valorant",
            "gta5": "GTA 5",
            "pubg": "PUBG",
            "cod": "Call of Duty",
        }
        return game_names.get(game_id, game_id.upper())
