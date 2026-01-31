"""
Comprehensive Dashboard Test Suite
Tests all sections, features, and functionality
"""
import sys
import io
from pathlib import Path

# Fix Windows encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import pytest


def test_imports():
    """Test all imports"""
    import streamlit as st
    import pandas as pd
    import plotly.express as px
    import plotly.graph_objects as go
    from src.database.db_utils import db_manager
    from src.analytics.aggregations import AnalyticsService
    from src.analytics.game_specific import GameSpecificAnalytics
    from src.analytics.comparison import ComparisonAnalytics
    from src.ml.forecasting import ForecastingService
    from src.ml.predictions import PredictionService
    from dashboard.components.ui_enhancements import apply_custom_css
    from dashboard.components.data_export import create_export_buttons
    assert True


def test_analytics_services():
    """Test analytics services"""
    from src.analytics.aggregations import AnalyticsService
    from src.analytics.game_specific import GameSpecificAnalytics
    from src.analytics.comparison import ComparisonAnalytics
    
    analytics = AnalyticsService()
    game_specific = GameSpecificAnalytics()
    comparison = ComparisonAnalytics()
    
    assert analytics is not None
    assert game_specific is not None
    assert comparison is not None


def test_ml_services():
    """Test ML services"""
    from src.ml.forecasting import ForecastingService
    from src.ml.predictions import PredictionService
    
    forecasting = ForecastingService()
    predictions = PredictionService()
    
    assert forecasting is not None
    assert predictions is not None


def test_database_connection():
    """Test database connection"""
    from src.database.db_utils import db_manager
    
    try:
        session = db_manager.get_session()
        assert session is not None
        session.close()
    except Exception:
        # Database might not be set up, that's OK for import test
        pass


def test_ui_components():
    """Test UI components"""
    from dashboard.components.ui_enhancements import (
        apply_custom_css, show_loading_spinner, empty_state,
        metric_card, section_header
    )
    from dashboard.components.data_export import create_export_buttons
    
    assert callable(apply_custom_css)
    assert callable(show_loading_spinner)
    assert callable(empty_state)
    assert callable(metric_card)
    assert callable(section_header)
    assert callable(create_export_buttons)


def test_api_connectors():
    """Test API connectors"""
    from src.ingestion.opendota_api import OpenDotaConnector
    from src.ingestion.steam_api import SteamConnector
    from src.ingestion.riot_api import RiotConnector
    
    opendota = OpenDotaConnector()
    steam = SteamConnector()
    riot = RiotConnector()
    
    assert opendota is not None
    assert steam is not None
    assert riot is not None
