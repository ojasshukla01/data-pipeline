"""
Tests for ETL pipeline
"""
import pytest
from src.etl.transform import DataTransformer
from datetime import datetime


def test_data_transformer():
    """Test data transformer"""
    transformer = DataTransformer()
    
    # Test match transformation
    raw_matches = [
        {
            "match_id": "test_123",
            "game_id": "dota2",
            "match_date": datetime.now().isoformat(),
            "duration_minutes": 45,
            "match_type": "ranked",
            "platform": "steam",
            "source": "test",
        }
    ]
    
    transformed = transformer.transform_matches(raw_matches, "dota2")
    assert len(transformed) == 1
    assert transformed[0]["match_id"] == "test_123"
    assert transformed[0]["game_id"] == "dota2"


def test_deduplicate_matches():
    """Test match deduplication"""
    transformer = DataTransformer()
    
    matches = [
        {"match_id": "1", "game_id": "dota2"},
        {"match_id": "2", "game_id": "dota2"},
        {"match_id": "1", "game_id": "dota2"},  # Duplicate
    ]
    
    unique = transformer.deduplicate_matches(matches)
    assert len(unique) == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
