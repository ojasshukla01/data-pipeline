"""
Main ETL Pipeline Runner
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.etl.extract import DataExtractor
from src.etl.transform import DataTransformer
from src.etl.load import DataLoader
from src.ingestion.mock_data_generator import MockDataGenerator
from src.utils.logger import get_logger

logger = get_logger(__name__)


class ETLPipeline:
    """Complete ETL pipeline"""
    
    def __init__(self):
        self.extractor = DataExtractor()
        self.transformer = DataTransformer()
        self.loader = DataLoader()
        self.mock_generator = MockDataGenerator()
    
    def run(self, limit_per_game: int = 10):
        """Run the complete ETL pipeline"""
        logger.info("=" * 50)
        logger.info("Starting ETL Pipeline")
        logger.info("=" * 50)
        
        # Extract
        logger.info("Step 1: Extracting data...")
        raw_data = self.extractor.extract_all_games(limit_per_game=limit_per_game)
        
        # Transform and Load
        total_matches = 0
        total_stats = 0
        
        for game_id, matches in raw_data.items():
            if not matches:
                continue
            
            logger.info(f"\nProcessing {game_id}...")
            
            # Transform matches
            transformed_matches = self.transformer.transform_matches(matches, game_id)
            transformed_matches = self.transformer.deduplicate_matches(transformed_matches)
            
            # Load matches
            match_stats = self.loader.load_matches(transformed_matches)
            total_matches += match_stats["inserted"]
            
            # Generate and load player stats for each match - REAL DATA ONLY
            player_stats = []
            
            # For Dota 2, try to fetch real player stats from OpenDota
            if game_id == "dota2":
                try:
                    from src.ingestion.opendota_api import OpenDotaAPIConnector
                    opendota = OpenDotaAPIConnector()
                    
                    # Fetch player stats from first few matches
                    for match in transformed_matches[:5]:  # Limit to 5 matches
                        if match.get("source") == "opendota_api":
                            try:
                                match_id_clean = match["match_id"].replace("opendota_", "")
                                players = opendota.fetch_match_players(int(match_id_clean))
                                
                                if players and len(players) > 0:
                                    # Transform real player data
                                    for player in players[:10]:  # Limit to 10 players per match
                                        player_stat = {
                                            "stat_id": f"stat_{match['match_id']}_{player.get('account_id', player.get('player_slot', 0))}",
                                            "player_id": f"opendota_player_{player.get('account_id', player.get('player_slot', 0))}",
                                            "match_id": match["match_id"],
                                            "kills": player.get("kills", 0),
                                            "deaths": player.get("deaths", 0),
                                            "assists": player.get("assists", 0),
                                            "score": player.get("total_gold", 0),
                                            "rank": None,
                                            "additional_stats": {
                                                "hero_id": player.get("hero_id"),
                                                "gold_per_min": player.get("gold_per_min", 0),
                                                "xp_per_min": player.get("xp_per_min", 0),
                                                "last_hits": player.get("last_hits", 0),
                                                "denies": player.get("denies", 0),
                                                "net_worth": player.get("net_worth", 0),
                                                "hero_damage": player.get("hero_damage", 0),
                                                "tower_damage": player.get("tower_damage", 0),
                                            }
                                        }
                                        transformed_stat = self.transformer.transform_player_stats(
                                            player_stat, match["match_id"]
                                        )
                                        if transformed_stat:
                                            player_stats.append(transformed_stat)
                            except Exception as e:
                                logger.warning(f"Could not fetch real player stats for {match['match_id']}: {str(e)}")
                                continue
                except Exception as e:
                    logger.error(f"Error fetching Dota 2 player stats: {str(e)}")
            
            # For other games, skip player stats if no real API available
            # NO MOCK DATA - only real data
            
            if player_stats:
                stats_result = self.loader.load_player_stats(player_stats)
                total_stats += stats_result["inserted"]
                logger.info(f"Loaded {stats_result['inserted']} real player stats for {game_id}")
            else:
                logger.info(f"No real player stats available for {game_id} (skipping - no mock data)")
            
            # Skip game events - only use real event data from APIs
            # No mock events generated
            logger.info(f"Skipping game events for {game_id} - using only real API event data")
        
        logger.info("\n" + "=" * 50)
        logger.info("ETL Pipeline Complete!")
        logger.info(f"Total matches loaded: {total_matches}")
        logger.info(f"Total player stats loaded: {total_stats}")
        logger.info("=" * 50)
        
        return {
            "matches_loaded": total_matches,
            "stats_loaded": total_stats,
        }


if __name__ == "__main__":
    pipeline = ETLPipeline()
    pipeline.run(limit_per_game=10)
