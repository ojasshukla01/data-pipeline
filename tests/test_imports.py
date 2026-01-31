"""
Test script to verify imports work correctly
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import pytest


def test_logger_import():
    """Test logger import"""
    from src.utils.logger import get_logger
    logger = get_logger("test")
    assert logger is not None


def test_config_import():
    """Test config import"""
    from config.database_config import DatabaseConfig
    assert DatabaseConfig is not None


def test_database_manager_import():
    """Test database manager import"""
    from src.database.db_utils import db_manager
    assert db_manager is not None


def test_mock_data_generator_import():
    """Test mock data generator import"""
    from src.ingestion.mock_data_generator import MockDataGenerator
    generator = MockDataGenerator()
    assert generator is not None
