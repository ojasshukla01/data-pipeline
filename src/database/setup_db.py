"""
Database setup script
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.database.db_utils import db_manager
from src.utils.logger import get_logger

logger = get_logger(__name__)


def setup_database():
    """Set up the database schema"""
    try:
        logger.info("Setting up database...")
        db_manager.create_tables()
        logger.info("Database setup completed successfully!")
    except Exception as e:
        logger.error(f"Database setup failed: {str(e)}")
        raise


if __name__ == "__main__":
    setup_database()
