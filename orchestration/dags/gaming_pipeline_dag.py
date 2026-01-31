"""
Gaming Data Pipeline DAG
Using Prefect for orchestration (simpler and free)
"""
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from prefect import flow, task
from prefect.schedules import CronSchedule
from prefect.tasks import task_input_hash
from src.etl.run_pipeline import ETLPipeline
from src.ml.generate_forecasts import generate_all_forecasts
from src.utils.logger import get_logger

logger = get_logger(__name__)


@task(cache_key_fn=task_input_hash, cache_expiration=timedelta(minutes=15))
def run_etl_pipeline_task(limit_per_game: int = 10):
    """ETL pipeline task"""
    logger.info("Starting ETL pipeline task...")
    pipeline = ETLPipeline()
    result = pipeline.run(limit_per_game=limit_per_game)
    logger.info(f"ETL pipeline completed: {result}")
    return result


@task
def generate_forecasts_task(days: int = 7):
    """Generate forecasts task"""
    logger.info("Starting forecasts generation task...")
    forecasts = generate_all_forecasts(days=days)
    logger.info(f"Generated {len(forecasts)} forecasts")
    return forecasts


@flow(name="gaming_data_pipeline", log_prints=True)
def gaming_data_pipeline_flow(limit_per_game: int = 10, generate_forecasts: bool = True):
    """Main gaming data pipeline flow"""
    logger.info("=" * 50)
    logger.info("Starting Gaming Data Pipeline Flow")
    logger.info("=" * 50)
    
    # Run ETL pipeline
    etl_result = run_etl_pipeline_task(limit_per_game=limit_per_game)
    
    # Generate forecasts if enabled
    if generate_forecasts:
        forecast_result = generate_forecasts_task(days=7)
    else:
        forecast_result = None
    
    logger.info("=" * 50)
    logger.info("Gaming Data Pipeline Flow Completed")
    logger.info("=" * 50)
    
    return {
        "etl_result": etl_result,
        "forecast_result": forecast_result,
    }


# Schedule: Run every 15 minutes
schedule = CronSchedule(cron="*/15 * * * *", timezone="UTC")

# Create scheduled flow
if __name__ == "__main__":
    # Run manually for testing
    gaming_data_pipeline_flow(limit_per_game=10, generate_forecasts=True)
