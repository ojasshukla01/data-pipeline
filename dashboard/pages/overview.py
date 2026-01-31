"""
Overview Page
Comprehensive dashboard overview and system status
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from sqlalchemy import text
import sys
from pathlib import Path

# Add project root to Python path for Streamlit Cloud compatibility
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# IMPORTANT: set_page_config() MUST be called first
st.set_page_config(
    page_title="Overview - Gaming Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Import UI enhancements
try:
    from dashboard.components.ui_enhancements import (
        apply_custom_css, show_loading_spinner, empty_state,
        metric_card, section_header, success_badge, warning_badge, info_badge
    )
except ImportError:
    def apply_custom_css():
        pass
    def show_loading_spinner(text=""):
        return st.spinner(text)
    def empty_state(message, icon="📊", action_text=None):
        st.info(message)
    def metric_card(label, value, delta=None, help_text=None):
        st.metric(label, value, delta=delta)
    def section_header(title, icon="📊", help_text=None):
        st.header(f"{icon} {title}")
    def success_badge(text):
        st.success(text)
    def warning_badge(text):
        st.warning(text)
    def info_badge(text):
        st.info(text)

# Apply custom CSS
apply_custom_css()

# Import services
from src.database.db_utils import db_manager
from src.analytics.aggregations import AnalyticsService
from src.analytics.comparison import ComparisonAnalytics
from config.api_config import APIConfig

# Initialize services
analytics_service = AnalyticsService()
comparison_analytics = ComparisonAnalytics()

# Page Header
st.title("📊 Dashboard Overview")
st.markdown("### Welcome to the Gaming Analytics Dashboard")
st.markdown("---")

# System Status Section
section_header("🔧 System Status", help_text="Current status of APIs, database, and data pipeline")

col1, col2, col3, col4 = st.columns(4)

# API Status
api_status = APIConfig.validate_config()
with col1:
    if api_status["opendota_configured"]:
        success_badge("OpenDota API")
    else:
        warning_badge("OpenDota API")

with col2:
    if api_status["steam_configured"]:
        success_badge("Steam API")
    else:
        warning_badge("Steam API")

with col3:
    if api_status["riot_configured"]:
        success_badge("Riot API")
    else:
        warning_badge("Riot API")

with col4:
    try:
        session = db_manager.get_session()
        session.execute(text("SELECT 1"))
        session.close()
        success_badge("Database")
    except Exception as e:
        warning_badge("Database")

st.markdown("---")

# Overall Statistics
section_header("📈 Overall Statistics", help_text="Aggregated metrics across all games and time periods")

try:
    session = db_manager.get_session()
    
    # Total matches
    total_matches = session.execute(text("SELECT COUNT(*) FROM matches")).scalar()
    
    # Total players
    total_players = session.execute(text("SELECT COUNT(DISTINCT player_id) FROM players")).scalar()
    
    # Total games
    total_games = session.execute(text("SELECT COUNT(DISTINCT game_id) FROM matches")).scalar()
    
    # Average duration
    avg_duration = session.execute(text("SELECT AVG(duration_minutes) FROM matches WHERE duration_minutes IS NOT NULL")).scalar()
    avg_duration = round(avg_duration, 2) if avg_duration else 0
    
    # Latest match date
    latest_match = session.execute(text("SELECT MAX(match_date) FROM matches")).scalar()
    
    # Oldest match date
    oldest_match = session.execute(text("SELECT MIN(match_date) FROM matches")).scalar()
    
    session.close()
    
    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        metric_card("Total Matches", f"{total_matches:,}", help_text="Total number of matches across all games")
    
    with col2:
        metric_card("Total Players", f"{total_players:,}", help_text="Unique players across all games")
    
    with col3:
        metric_card("Active Games", f"{total_games}", help_text="Number of games with data")
    
    with col4:
        metric_card("Avg Duration", f"{avg_duration} min", help_text="Average match duration in minutes")
    
    # Date range
    if latest_match and oldest_match:
        st.info(f"📅 **Data Range**: {oldest_match} to {latest_match}")
    
except Exception as e:
    st.error(f"Error loading statistics: {str(e)}")

st.markdown("---")

# Games Overview
section_header("🎮 Games Overview", help_text="Statistics for each game in the system")

try:
    session = db_manager.get_session()
    
    query = text("""
        SELECT 
            g.game_id,
            g.game_name,
            COUNT(DISTINCT m.match_id) as total_matches,
            COUNT(DISTINCT ps.player_id) as unique_players,
            AVG(m.duration_minutes) as avg_duration,
            MIN(m.match_date) as first_match,
            MAX(m.match_date) as last_match
        FROM games g
        LEFT JOIN matches m ON g.game_id = m.game_id
        LEFT JOIN player_stats ps ON m.match_id = ps.match_id
        GROUP BY g.game_id, g.game_name
        ORDER BY total_matches DESC
    """)
    
    df_games = pd.read_sql(query, session.bind)
    session.close()
    
    if not df_games.empty:
        # Format the dataframe
        df_games['avg_duration'] = df_games['avg_duration'].round(2)
        df_games = df_games.fillna(0)
        
        # Display table
        st.dataframe(
            df_games,
            use_container_width=True,
            hide_index=True
        )
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            if df_games['total_matches'].sum() > 0:
                fig_matches = px.bar(
                    df_games,
                    x='game_name',
                    y='total_matches',
                    title="Total Matches by Game",
                    labels={'total_matches': 'Total Matches', 'game_name': 'Game'},
                    color='total_matches',
                    color_continuous_scale='Blues',
                    hover_data={'game_name': True, 'total_matches': True, 'unique_players': True, 'avg_duration': True}
                )
                fig_matches.update_traces(
                    hovertemplate="<b>%{x}</b><br>Total Matches: %{y}<br>Unique Players: %{customdata[1]:.0f}<br>Avg Duration: %{customdata[2]:.2f} min<br><extra></extra>",
                    customdata=df_games[['total_matches', 'unique_players', 'avg_duration']].values
                )
                fig_matches.update_layout(showlegend=False, hovermode="x unified")
                st.plotly_chart(fig_matches, use_container_width=True)
        
        with col2:
            if df_games['unique_players'].sum() > 0:
                fig_players = px.bar(
                    df_games,
                    x='game_name',
                    y='unique_players',
                    title="Unique Players by Game",
                    labels={'unique_players': 'Unique Players', 'game_name': 'Game'},
                    color='unique_players',
                    color_continuous_scale='Greens',
                    hover_data={'game_name': True, 'unique_players': True, 'total_matches': True, 'avg_duration': True}
                )
                fig_players.update_traces(
                    hovertemplate="<b>%{x}</b><br>Unique Players: %{y}<br>Total Matches: %{customdata[1]:.0f}<br>Avg Duration: %{customdata[2]:.2f} min<br><extra></extra>",
                    customdata=df_games[['unique_players', 'total_matches', 'avg_duration']].values
                )
                fig_players.update_layout(showlegend=False, hovermode="x unified")
                st.plotly_chart(fig_players, use_container_width=True)
    else:
        empty_state("No game data available", "📊", "Run the ETL pipeline to populate data")
        
except Exception as e:
    st.error(f"Error loading games overview: {str(e)}")

st.markdown("---")

# Recent Activity
section_header("🕐 Recent Activity", help_text="Latest matches and data updates")

try:
    session = db_manager.get_session()
    
    query = text("""
        SELECT 
            m.match_id,
            g.game_name,
            m.match_date,
            m.duration_minutes,
            COUNT(DISTINCT ps.player_id) as player_count
        FROM matches m
        JOIN games g ON m.game_id = g.game_id
        LEFT JOIN player_stats ps ON m.match_id = ps.match_id
        GROUP BY m.match_id, g.game_name, m.match_date, m.duration_minutes
        ORDER BY m.match_date DESC
        LIMIT 10
    """)
    
    df_recent = pd.read_sql(query, session.bind)
    session.close()
    
    if not df_recent.empty:
        df_recent['match_date'] = pd.to_datetime(df_recent['match_date'])
        df_recent = df_recent.rename(columns={
            'game_name': 'Game',
            'match_date': 'Date',
            'duration_minutes': 'Duration (min)',
            'player_count': 'Players'
        })
        st.dataframe(df_recent[['Game', 'Date', 'Duration (min)', 'Players']], use_container_width=True, hide_index=True)
    else:
        empty_state("No recent matches", "🕐", "Run the ETL pipeline to see recent activity")
        
except Exception as e:
    st.error(f"Error loading recent activity: {str(e)}")

st.markdown("---")

# Quick Links & Information
section_header("🔗 Quick Links", help_text="Navigate to different sections of the dashboard")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    ### 📊 Main Dashboard
    - Game-specific analytics
    - Real-time metrics
    - Trends and forecasts
    """)
    if st.button("Go to Main Dashboard", use_container_width=True):
        st.info("Navigate to 'Gaming Analytics' in the sidebar to view the main dashboard")

with col2:
    st.markdown("""
    ### 📈 Analytics
    - Player statistics
    - Match analysis
    - Performance metrics
    """)
    st.info("Available in Main Dashboard")

with col3:
    st.markdown("""
    ### 🔮 Predictions
    - ML forecasts
    - Player predictions
    - Trend analysis
    """)
    st.info("Available in Main Dashboard")

st.markdown("---")

# Data Sources Information
section_header("📡 Data Sources", help_text="Information about API integrations and data sources")

st.markdown("""
### Available APIs

**OpenDota API (Dota 2)**
- ✅ No API key required
- Real-time match data
- Player statistics
- Match history

**Steam API**
- ⚠️ API key required
- CS:GO player data
- GTA 5 statistics
- Game ownership data

**Riot Games API**
- ⚠️ API key required
- Valorant match data
- Player statistics
- Rank information
""")

st.info("💡 **Tip**: Run `python setup_api_keys.py` to configure API keys for Steam and Riot APIs")

st.markdown("---")

# Footer
st.markdown("""
<div style="text-align: center; padding: 2rem; color: #666;">
    <p>🎮 Gaming Analytics Dashboard</p>
    <p>Real-time gaming data analytics and predictions</p>
    <p><small>Last updated: {}</small></p>
</div>
""".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")), unsafe_allow_html=True)
