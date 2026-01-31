"""
Data Ingestion Module
"""
from src.ingestion.steam_api import SteamAPIConnector
from src.ingestion.opendota_api import OpenDotaAPIConnector
from src.ingestion.riot_api import RiotAPIConnector
from src.ingestion.mock_data_generator import MockDataGenerator
from src.ingestion.base_connector import BaseConnector

__all__ = [
    "SteamAPIConnector",
    "OpenDotaAPIConnector",
    "RiotAPIConnector",
    "MockDataGenerator",
    "BaseConnector",
]
