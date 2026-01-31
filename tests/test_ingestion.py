"""
Tests for data ingestion
"""
import pytest
from src.ingestion import MockDataGenerator, SteamAPIConnector


def test_mock_data_generator():
    """Test mock data generator"""
    generator = MockDataGenerator()
    
    # Test match data generation
    matches = generator.generate_match_data("pubg", count=5)
    assert len(matches) == 5
    assert all("match_id" in match for match in matches)
    assert all("game_id" in match for match in matches)


def test_steam_connector():
    """Test Steam API connector"""
    connector = SteamAPIConnector()
    assert connector.get_game_name() == "steam_games"
    
    # Test data fetching (will use mock if no API key)
    data = connector.fetch_data(game="dota2", limit=5)
    assert isinstance(data, list)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
