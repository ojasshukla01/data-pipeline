"""
Script to generate forecasts for all games
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.ml.forecasting import ForecastingService
from src.utils.logger import get_logger

logger = get_logger(__name__)


def generate_all_forecasts(days: int = 7):
    """Generate forecasts for all games"""
    service = ForecastingService()
    games = ["dota2", "csgo", "valorant", "gta5", "pubg", "cod"]
    
    logger.info(f"Generating forecasts for {len(games)} games (next {days} days)")
    
    all_forecasts = []
    
    for game_id in games:
        try:
            forecasts = service.generate_player_count_forecasts(game_id, days=days)
            all_forecasts.extend(forecasts)
            logger.info(f"Generated {len(forecasts)} forecasts for {game_id}")
        except Exception as e:
            logger.error(f"Error generating forecasts for {game_id}: {str(e)}")
    
    # Save to database
    if all_forecasts:
        service.save_forecasts(all_forecasts)
        logger.info(f"Saved {len(all_forecasts)} total forecasts")
    
    return all_forecasts


if __name__ == "__main__":
    generate_all_forecasts(days=7)
