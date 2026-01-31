"""
Main Streamlit Dashboard
Gaming Analytics Dashboard
"""
import sys
import os
from pathlib import Path

# CRITICAL: Add project root to Python path FIRST, before any other imports
# This ensures Streamlit Cloud can find the src and config modules
project_root = Path(__file__).parent.parent.resolve()
project_root_str = str(project_root)
if project_root_str not in sys.path:
    sys.path.insert(0, project_root_str)
# Also add current directory to path (for Streamlit Cloud)
current_dir = str(Path(__file__).parent.parent.resolve())
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Now import standard libraries
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from sqlalchemy import text

# Import project modules (after path is set)
from src.database.db_utils import db_manager
from src.analytics.aggregations import AnalyticsService
from src.ml.forecasting import ForecastingService
from src.ml.predictions import PredictionService

# IMPORTANT: set_page_config() MUST be called first, before any other Streamlit commands
st.set_page_config(
    page_title="Gaming Analytics Dashboard",
    page_icon="🎮",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/your-repo/issues',
        'Report a bug': 'https://github.com/your-repo/issues',
        'About': "# Gaming Analytics Dashboard\nReal-time gaming data analytics and predictions"
    }
)

# Import UI enhancements (after set_page_config)
try:
    from dashboard.components.ui_enhancements import (
        apply_custom_css, show_loading_spinner, empty_state,
        metric_card, section_header, success_badge, warning_badge, info_badge
    )
    from dashboard.components.data_export import create_export_buttons
except ImportError:
    # Fallback if components not available
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
    def create_export_buttons(df, filename):
        pass

# Apply custom CSS (after set_page_config)
apply_custom_css()

# Initialize services
analytics_service = AnalyticsService()
forecasting_service = ForecastingService()
prediction_service = PredictionService()
from src.analytics.game_specific import GameSpecificAnalytics
from src.analytics.comparison import ComparisonAnalytics
game_specific_analytics = GameSpecificAnalytics()
comparison_analytics = ComparisonAnalytics()

# Sidebar
st.sidebar.title("🎮 Gaming Analytics")
st.sidebar.markdown("---")

# Check which games have data
@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_available_games():
    """Get list of games that have data in database"""
    session = db_manager.get_session()
    try:
        result = session.execute(text("SELECT DISTINCT game_id FROM matches"))
        games_with_data = [row[0] for row in result]
        
        game_names = {
            "dota2": "Dota 2",
            "csgo": "CS:GO",
            "valorant": "Valorant",
            "gta5": "GTA 5",
            "pubg": "PUBG",
            "cod": "Call of Duty",
        }
        
        available = ["All Games"]
        for game_id in games_with_data:
            if game_id in game_names:
                available.append(game_names[game_id])
        
        return available
    except Exception as e:
        return ["All Games", "Dota 2"]
    finally:
        session.close()

available_games = get_available_games()

# Game selection - only show games with data
games = available_games if available_games else ["All Games", "Dota 2"]
selected_game = st.sidebar.selectbox("Select Game", games)

game_id_map = {
    "All Games": None,
    "Dota 2": "dota2",
    "CS:GO": "csgo",
    "Valorant": "valorant",
    "GTA 5": "gta5",
    "PUBG": "pubg",
    "Call of Duty": "cod",
    "COD": "cod",  # Alias for backward compatibility
}

selected_game_id = game_id_map.get(selected_game, None)

# Time period
time_period = st.sidebar.selectbox("Time Period", ["Last 7 days", "Last 30 days", "Last 90 days"])
days_map = {"Last 7 days": 7, "Last 30 days": 30, "Last 90 days": 90}
selected_days = days_map[time_period]

# Auto-refresh setup
if 'last_refresh' not in st.session_state:
    st.session_state.last_refresh = datetime.now()
    st.session_state.refresh_count = 0

# Check if 2 minutes have passed
time_since_refresh = (datetime.now() - st.session_state.last_refresh).total_seconds()
if time_since_refresh >= 120:  # 2 minutes
    st.session_state.last_refresh = datetime.now()
    st.session_state.refresh_count += 1
    st.rerun()

# Main content
st.title("🎮 Gaming Analytics Dashboard")
col_title, col_refresh, col_export = st.columns([3, 1, 1])
with col_title:
    st.markdown("### Real-time gaming data analytics and predictions")
with col_refresh:
    time_until_refresh = 120 - time_since_refresh
    info_badge(f"Refresh in {int(time_until_refresh)}s")
with col_export:
    if st.button("🔄 Manual Refresh"):
        st.cache_data.clear()
        st.rerun()

# Show current time period with better styling
st.markdown(f"""
<div style="background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); padding: 1rem; border-radius: 8px; color: white; margin: 1rem 0;">
    <strong>📅 Viewing:</strong> {time_period} | <strong>🎮 Game:</strong> {selected_game} | <strong>🕐 Last refresh:</strong> {st.session_state.last_refresh.strftime('%H:%M:%S')}
</div>
""", unsafe_allow_html=True)

# API Status Indicator
with st.sidebar:
    st.markdown("---")
    st.markdown("### 📡 API Status")
    from config.api_config import APIConfig
    api_status = APIConfig.validate_config()
    
    if api_status["opendota_configured"]:
        st.markdown('<div style="color: #155724; background-color: #d4edda; padding: 0.5rem; border-radius: 4px; margin: 0.25rem 0;">✅ OpenDota API (Dota 2) - Active</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div style="color: #721c24; background-color: #f8d7da; padding: 0.5rem; border-radius: 4px; margin: 0.25rem 0;">❌ OpenDota API - Not configured</div>', unsafe_allow_html=True)
    
    if api_status["steam_configured"]:
        st.markdown('<div style="color: #155724; background-color: #d4edda; padding: 0.5rem; border-radius: 4px; margin: 0.25rem 0;">✅ Steam API - Configured</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div style="color: #856404; background-color: #fff3cd; padding: 0.5rem; border-radius: 4px; margin: 0.25rem 0;">⚠️ Steam API - No key</div>', unsafe_allow_html=True)
    
    if api_status["riot_configured"]:
        st.markdown('<div style="color: #155724; background-color: #d4edda; padding: 0.5rem; border-radius: 4px; margin: 0.25rem 0;">✅ Riot API - Configured</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div style="color: #856404; background-color: #fff3cd; padding: 0.5rem; border-radius: 4px; margin: 0.25rem 0;">⚠️ Riot API - No key</div>', unsafe_allow_html=True)
    
    # Show data source info
    st.markdown("---")
    st.markdown("### 📊 Data Sources")
    st.markdown('<div style="color: #0c5460; background-color: #d1ecf1; padding: 0.5rem; border-radius: 4px; margin: 0.25rem 0;">ℹ️ OpenDota: Real Dota 2 data (no key needed)</div>', unsafe_allow_html=True)
    if not api_status["steam_configured"]:
        st.markdown('<div style="color: #856404; background-color: #fff3cd; padding: 0.5rem; border-radius: 4px; margin: 0.25rem 0;">⚠️ Steam: Get API key for CS:GO, GTA 5</div>', unsafe_allow_html=True)
    if not api_status["riot_configured"]:
        st.markdown('<div style="color: #856404; background-color: #fff3cd; padding: 0.5rem; border-radius: 4px; margin: 0.25rem 0;">⚠️ Riot: Get API key for Valorant</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    if st.button("🔑 Setup API Keys"):
        st.markdown('<div style="color: #0c5460; background-color: #d1ecf1; padding: 0.5rem; border-radius: 4px; margin: 0.25rem 0;">ℹ️ Run: python setup_api_keys.py</div>', unsafe_allow_html=True)

# Helper function for info tooltips
def info_tooltip(text: str):
    """Create an info icon with tooltip"""
    return st.markdown(f'<span title="{text}">ℹ️</span>', unsafe_allow_html=True)

# GAME-SPECIFIC OVERVIEW (First Section - Shows API Attributes)
if selected_game_id:
    section_header(
        f"{selected_game} - Game-Specific Overview & API Attributes",
        icon="🎮",
        help_text=f"Game-specific metrics and attributes from API. Shows real data from {selected_game} API with game-specific fields and statistics."
    )
    
    with show_loading_spinner("Loading game data..."):
        try:
            # Get game-specific metrics first (shows API attributes)
            game_metrics = game_specific_analytics.get_game_specific_metrics(selected_game_id, days=selected_days)
            stats = analytics_service.get_game_statistics(selected_game_id, days=selected_days)
            
            # Dota 2 Specific Display (OpenDota API Attributes)
            if selected_game_id == "dota2":
                if game_metrics and "win_rate" in game_metrics:
                    wr = game_metrics["win_rate"]
                    st.subheader("Dota 2 Match Statistics (OpenDota API Data)")
                    st.caption(f"📡 Source: OpenDota API | Period: {time_period}")
                    
                    col1, col2, col3, col4, col5 = st.columns(5)
                    with col1:
                        metric_card(
                            "Total Matches",
                            wr.get("total_matches", 0),
                            help_text=f"Total matches in {time_period}"
                        )
                        st.caption(f"{time_period}")
                    with col2:
                        metric_card(
                            "Radiant Wins",
                            wr.get("radiant_wins", 0),
                            help_text="Number of matches won by Radiant team"
                        )
                        st.caption("Radiant team")
                    with col3:
                        win_rate = wr.get("radiant_win_rate", 0)
                        delta_value = f"{win_rate-50:.1f}%" if win_rate != 50 else None
                        metric_card(
                            "Radiant Win Rate",
                            f"{win_rate:.1f}%",
                            delta=delta_value,
                            help_text="Percentage of matches won by Radiant team"
                        )
                        st.caption("Win percentage")
                    with col4:
                        dire_wins = wr.get("total_matches", 0) - wr.get("radiant_wins", 0)
                        metric_card(
                            "Dire Wins",
                            dire_wins,
                            help_text="Number of matches won by Dire team"
                        )
                        st.caption("Dire team")
                    with col5:
                        avg_dur = stats.get("matches", {}).get("avg_duration_minutes", 0)
                        metric_card(
                            "Avg Duration",
                            f"{avg_dur:.1f} min",
                            help_text="Average match duration in minutes"
                        )
                        st.caption("Per match")
                    
                    # Match Type Distribution (OpenDota API Attribute)
                    if "match_types" in game_metrics and game_metrics["match_types"]:
                        st.subheader("Match Type Distribution (OpenDota API Attribute)")
                        match_type_df = pd.DataFrame(game_metrics["match_types"])
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            fig = px.bar(
                                match_type_df,
                                x="type",
                                y="count",
                                title="Matches by Type (OpenDota Data)",
                                labels={"type": "Match Type", "count": "Number of Matches"},
                                color="count",
                                color_continuous_scale="viridis",
                                hover_data={"type": True, "count": True}
                            )
                            fig.update_traces(
                                hovertemplate="<b>%{x}</b><br>Matches: %{y}<br><extra></extra>"
                            )
                            fig.update_layout(hovermode="x unified")
                            st.plotly_chart(fig, use_container_width=True)
                        
                        with col2:
                            st.dataframe(match_type_df, use_container_width=True)
            
            # CS:GO Specific Display (Steam API Attributes)
            elif selected_game_id == "csgo":
                st.subheader("CS:GO Match Statistics (Steam API Data)")
                st.caption(f"📡 Source: Steam API | Period: {time_period}")
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Total Matches", stats.get("matches", {}).get("total", 0))
                    st.caption(f"{time_period}")
                with col2:
                    st.metric("Unique Players", stats.get("players", {}).get("unique_count", 0))
                    st.caption("Distinct players")
                with col3:
                    avg_kills = stats.get("players", {}).get("avg_kills", 0)
                    st.metric("Avg Kills", f"{avg_kills:.1f}")
                    st.caption("Per player")
                with col4:
                    avg_dur = stats.get("matches", {}).get("avg_duration_minutes", 0)
                    st.metric("Avg Duration", f"{avg_dur:.1f} min")
                    st.caption("Per match")
            
            # Other games
            else:
                st.subheader(f"{selected_game} Match Statistics")
                st.caption(f"Period: {time_period}")
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Total Matches", stats.get("matches", {}).get("total", 0))
                with col2:
                    st.metric("Unique Players", stats.get("players", {}).get("unique_count", 0))
                with col3:
                    avg_dur = stats.get("matches", {}).get("avg_duration_minutes", 0)
                    st.metric("Avg Duration", f"{avg_dur:.1f} min")
                with col4:
                    avg_kills = stats.get("players", {}).get("avg_kills", 0)
                    st.metric("Avg Kills", f"{avg_kills:.1f}")
        
        except Exception as e:
            st.error(f"❌ Error loading game data: {str(e)}")
            empty_state("Unable to load game data", icon="⚠️")

# ALL GAMES COMPARISON VIEW
if selected_game_id is None:
    section_header(
        "All Games Comparison",
        icon="📊",
        help_text="Compare statistics across all games. Shows total matches, players, and performance metrics for each game in the selected time period."
    )
    
    with show_loading_spinner("Loading comparison data..."):
        try:
            comparison = comparison_analytics.get_all_games_comparison(days=selected_days)
            
            if comparison and comparison.get("games"):
                # Summary metrics
                summary = comparison.get("summary", {})
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Total Matches (All)", summary.get("total_matches_all", 0))
                with col2:
                    st.metric("Total Players (All)", summary.get("total_players_all", 0))
                with col3:
                    st.metric("Avg Duration (All)", f"{summary.get('avg_duration_all', 0):.1f} min")
                with col4:
                    st.metric("Games with Data", comparison.get("total_games", 0))
                
                # Games comparison table
                st.subheader("Games Comparison Table")
                games_df = pd.DataFrame(comparison["games"])
                st.dataframe(games_df, use_container_width=True)
                
                # Comparison charts
                col1, col2 = st.columns(2)
                
                with col1:
                    fig_matches = px.bar(
                        games_df,
                        x="game_name",
                        y="total_matches",
                        title=f"Total Matches by Game ({time_period})",
                        labels={"game_name": "Game", "total_matches": "Matches"},
                        color="total_matches",
                        color_continuous_scale="viridis",
                        hover_data={"game_name": True, "total_matches": True, "unique_players": True, "avg_duration": True}
                    )
                    fig_matches.update_traces(
                        hovertemplate="<b>%{x}</b><br>Total Matches: %{y}<br>Unique Players: %{customdata[1]:.0f}<br>Avg Duration: %{customdata[2]:.2f} min<br><extra></extra>",
                        customdata=games_df[["total_matches", "unique_players", "avg_duration"]].values if "unique_players" in games_df.columns and "avg_duration" in games_df.columns else games_df[["total_matches"]].values
                    )
                    fig_matches.update_layout(hovermode="x unified")
                    st.plotly_chart(fig_matches, use_container_width=True)
                
                with col2:
                    fig_players = px.bar(
                        games_df,
                        x="game_name",
                        y="unique_players",
                        title=f"Unique Players by Game ({time_period})",
                        labels={"game_name": "Game", "unique_players": "Players"},
                        color="unique_players",
                        color_continuous_scale="plasma",
                        hover_data={"game_name": True, "unique_players": True, "total_matches": True, "avg_duration": True}
                    )
                    fig_players.update_traces(
                        hovertemplate="<b>%{x}</b><br>Unique Players: %{y}<br>Total Matches: %{customdata[1]:.0f}<br>Avg Duration: %{customdata[2]:.2f} min<br><extra></extra>",
                        customdata=games_df[["unique_players", "total_matches", "avg_duration"]].values if "total_matches" in games_df.columns and "avg_duration" in games_df.columns else games_df[["unique_players"]].values
                    )
                    fig_players.update_layout(hovermode="x unified")
                    st.plotly_chart(fig_players, use_container_width=True)
                
                # Export button
                st.markdown("---")
                st.subheader("📥 Export Comparison Data")
                create_export_buttons(games_df, f"all_games_comparison_{time_period.replace(' ', '_')}")
            else:
                empty_state(
                    "No comparison data available",
                    icon="📊",
                    action_text="Run the ETL pipeline to fetch data"
                )
        
        except Exception as e:
            st.error(f"❌ Error loading comparison: {str(e)}")
            empty_state("Unable to load comparison data", icon="⚠️")

# TRENDS SECTION
if selected_game_id:
    section_header(
        "📈 Daily Trends",
        icon="📈",
        help_text=f"Daily trends for {selected_game}. Shows match count, player count, and performance metrics over time for the selected period."
    )
    
    with show_loading_spinner("Loading trends..."):
        try:
            trends = analytics_service.get_daily_trends(selected_game_id, days=selected_days)
            
            if not trends:
                empty_state(
                    "No trend data available",
                    icon="📈",
                    action_text="Run the ETL pipeline to fetch data"
                )
            else:
                df_trends = pd.DataFrame(trends)
                df_trends["date"] = pd.to_datetime(df_trends["date"])
                
                col1, col2 = st.columns(2)
                
                with col1:
                    fig_matches = px.line(
                        df_trends,
                        x="date",
                        y="match_count",
                        title="Daily Match Count",
                        labels={"match_count": "Matches", "date": "Date"},
                        hover_data={"date": True, "match_count": True}
                    )
                    fig_matches.update_traces(
                        hovertemplate="<b>Date:</b> %{x|%Y-%m-%d}<br><b>Matches:</b> %{y}<br><extra></extra>",
                        mode="lines+markers"
                    )
                    fig_matches.update_layout(hovermode="x unified")
                    st.plotly_chart(fig_matches, use_container_width=True)
                
                with col2:
                    fig_players = px.line(
                        df_trends,
                        x="date",
                        y="player_count",
                        title="Daily Player Count",
                        labels={"player_count": "Players", "date": "Date"},
                        hover_data={"date": True, "player_count": True}
                    )
                    fig_players.update_traces(
                        hovertemplate="<b>Date:</b> %{x|%Y-%m-%d}<br><b>Players:</b> %{y}<br><extra></extra>",
                        mode="lines+markers"
                    )
                    fig_players.update_layout(hovermode="x unified")
                    st.plotly_chart(fig_players, use_container_width=True)
                
                # Performance metrics
                fig_performance = go.Figure()
                fig_performance.add_trace(go.Scatter(
                    x=df_trends["date"],
                    y=df_trends["avg_kills"],
                    name="Avg Kills",
                    line=dict(color="green", width=2),
                    hovertemplate="<b>Date:</b> %{x|%Y-%m-%d}<br><b>Avg Kills:</b> %{y:.2f}<br><extra></extra>",
                    mode="lines+markers"
                ))
                fig_performance.add_trace(go.Scatter(
                    x=df_trends["date"],
                    y=df_trends["avg_duration_minutes"],
                    name="Avg Duration (min)",
                    yaxis="y2",
                    line=dict(color="blue", width=2),
                    hovertemplate="<b>Date:</b> %{x|%Y-%m-%d}<br><b>Avg Duration:</b> %{y:.2f} min<br><extra></extra>",
                    mode="lines+markers"
                ))
                
                fig_performance.update_layout(
                    title="Performance Metrics Over Time",
                    xaxis_title="Date",
                    yaxis=dict(title="Avg Kills", side="left"),
                    yaxis2=dict(title="Avg Duration (min)", overlaying="y", side="right"),
                    hovermode="x unified",
                    hoverlabel=dict(bgcolor="white", font_size=12, font_family="Arial")
                )
                
                st.plotly_chart(fig_performance, use_container_width=True)
                
                # Export button for trends
                st.markdown("---")
                st.subheader("📥 Export Trends Data")
                create_export_buttons(df_trends, f"{selected_game}_trends_{time_period.replace(' ', '_')}")
        
        except Exception as e:
            st.error(f"❌ Error loading trends: {str(e)}")
            empty_state("Unable to load trend data", icon="⚠️")

# Additional Game-Specific Metrics (if not already shown)
if selected_game_id:
    section_header(
        "🎯 Additional Game-Specific Metrics",
        icon="🎯",
        help_text=f"Additional game-specific statistics and attributes for {selected_game}."
    )
    
    with show_loading_spinner("Loading additional metrics..."):
        try:
            game_metrics = game_specific_analytics.get_game_specific_metrics(selected_game_id, days=selected_days)
            
            if game_metrics and "message" not in game_metrics:
                # Dota 2 specific metrics
                if selected_game_id == "dota2":
                    if "win_rate" in game_metrics and game_metrics["win_rate"]:
                        wr = game_metrics["win_rate"]
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Total Matches", wr.get("total_matches", 0))
                        with col2:
                            st.metric("Radiant Wins", wr.get("radiant_wins", 0))
                        with col3:
                            st.metric("Radiant Win Rate", f"{wr.get('radiant_win_rate', 0):.1f}%")
                    
                    if "match_types" in game_metrics and game_metrics["match_types"]:
                        st.subheader("Match Type Distribution")
                        match_type_df = pd.DataFrame(game_metrics["match_types"])
                        if not match_type_df.empty:
                            fig = px.bar(
                                match_type_df,
                                x="type",
                                y="count",
                                title="Matches by Type (Real Dota 2 Data)",
                                labels={"type": "Match Type", "count": "Number of Matches"},
                                color="count",
                                color_continuous_scale="viridis",
                                hover_data={"type": True, "count": True}
                            )
                            fig.update_traces(
                                hovertemplate="<b>%{x}</b><br>Matches: %{y}<br><extra></extra>"
                            )
                            fig.update_layout(hovermode="x unified")
                            st.plotly_chart(fig, use_container_width=True)
                            
                            # Show detailed stats
                            st.subheader("Match Type Details")
                            st.dataframe(match_type_df, use_container_width=True)
            
                # CS:GO specific metrics
                elif selected_game_id == "csgo":
                    if "match_types" in game_metrics:
                        st.subheader("CS:GO Match Statistics")
                        csgo_df = pd.DataFrame(game_metrics["match_types"])
                        if not csgo_df.empty:
                            st.dataframe(csgo_df, use_container_width=True)
            
                # Valorant specific metrics
                elif selected_game_id == "valorant":
                    if "match_types" in game_metrics:
                        st.subheader("Valorant Match Statistics")
                        valorant_df = pd.DataFrame(game_metrics["match_types"])
                        if not valorant_df.empty:
                            fig = px.bar(
                                valorant_df,
                                x="type",
                                y="match_count",
                                title="Matches by Type",
                                labels={"type": "Match Type", "match_count": "Number of Matches"},
                                hover_data={"type": True, "match_count": True}
                            )
                            fig.update_traces(
                                hovertemplate="<b>%{x}</b><br>Matches: %{y}<br><extra></extra>"
                            )
                            fig.update_layout(hovermode="x unified")
                            st.plotly_chart(fig, use_container_width=True)
            
                # PUBG specific metrics
                elif selected_game_id == "pubg":
                    if "match_types" in game_metrics:
                        st.subheader("PUBG Match Statistics")
                        pubg_df = pd.DataFrame(game_metrics["match_types"])
                        if not pubg_df.empty:
                            st.dataframe(pubg_df, use_container_width=True)
            
                # COD specific metrics
                elif selected_game_id == "cod":
                    if "match_types" in game_metrics:
                        st.subheader("Call of Duty Match Statistics")
                        cod_df = pd.DataFrame(game_metrics["match_types"])
                        if not cod_df.empty:
                            st.dataframe(cod_df, use_container_width=True)
            
            else:
                empty_state(
                    "No additional metrics available",
                    icon="📊",
                    action_text="Run the ETL pipeline to fetch data"
                )
        
        except Exception as e:
            st.error(f"❌ Error loading additional metrics: {str(e)}")
            empty_state("Unable to load additional metrics", icon="⚠️")

# TOP PLAYERS SECTION
if selected_game_id:
    section_header(
        "🏆 Top Players",
        icon="🏆",
        help_text=f"Top performing players in {selected_game} based on kills, score, and other performance metrics for the selected period."
    )
    
    with show_loading_spinner("Loading top players..."):
        try:
            top_players = analytics_service.get_top_players(selected_game_id, days=selected_days, limit=10)
            
            if not top_players:
                empty_state(
                    "No player data available",
                    icon="👤",
                    action_text="Run the ETL pipeline to fetch data"
                )
            else:
                df_top = pd.DataFrame(top_players)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("Top Players by Kills")
                    fig = px.bar(
                        df_top,
                        x="player_name",
                        y="total_kills",
                        title="Top Players by Kills",
                        labels={"total_kills": "Total Kills", "player_name": "Player"},
                        color="total_kills",
                        color_continuous_scale="Reds",
                        hover_data={"player_name": True, "total_kills": True, "total_deaths": True, "total_assists": True}
                    )
                    fig.update_traces(
                        hovertemplate="<b>%{x}</b><br>Kills: %{y}<br>Deaths: %{customdata[1]:.0f}<br>Assists: %{customdata[2]:.0f}<br><extra></extra>",
                        customdata=df_top[["total_kills", "total_deaths", "total_assists"]].values
                    )
                    fig.update_layout(showlegend=False, hovermode="x unified")
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    st.subheader("Top Players by Average Score")
                    fig = px.bar(
                        df_top,
                        x="player_name",
                        y="avg_score",
                        title="Top Players by Average Score",
                        labels={"avg_score": "Average Score", "player_name": "Player"},
                        color="avg_score",
                        color_continuous_scale="Purples",
                        hover_data={"player_name": True, "avg_score": True, "total_matches": True}
                    )
                    fig.update_traces(
                        hovertemplate="<b>%{x}</b><br>Avg Score: %{y:.2f}<br>Matches: %{customdata[1]:.0f}<br><extra></extra>",
                        customdata=df_top[["avg_score", "total_matches"]].values
                    )
                    fig.update_layout(hovermode="x unified")
                    st.plotly_chart(fig, use_container_width=True)
                
                # Top players table
                st.subheader("Top Players Table")
                st.dataframe(df_top, use_container_width=True)
                
                # Export button
                st.markdown("---")
                st.subheader("📥 Export Top Players Data")
                create_export_buttons(df_top, f"{selected_game}_top_players_{time_period.replace(' ', '_')}")
        
        except Exception as e:
            st.error(f"❌ Error loading top players: {str(e)}")
            empty_state("Unable to load player data", icon="⚠️")

# FORECASTS SECTION
if selected_game_id:
    section_header(
        "🔮 Forecasts & Predictions",
        icon="🔮",
        help_text=f"ML-powered forecasts for {selected_game}. Predicts player count and match trends for the next 7 days based on historical data."
    )
    
    with show_loading_spinner("Generating forecasts..."):
        try:
            forecasts = forecasting_service.generate_player_count_forecasts(
                selected_game_id, days=7
            )
            
            if forecasts:
                df_forecasts = pd.DataFrame(forecasts)
                df_forecasts["forecast_date"] = pd.to_datetime(df_forecasts["forecast_date"])
                
                fig_forecast = go.Figure()
                
                # Predicted values
                fig_forecast.add_trace(go.Scatter(
                    x=df_forecasts["forecast_date"],
                    y=df_forecasts["predicted_value"],
                    name="Predicted",
                    line=dict(color="blue", width=2),
                    hovertemplate="<b>Date:</b> %{x|%Y-%m-%d}<br><b>Predicted:</b> %{y:.0f} players<br><extra></extra>",
                    mode="lines+markers"
                ))
                
                # Confidence interval
                fig_forecast.add_trace(go.Scatter(
                    x=df_forecasts["forecast_date"],
                    y=df_forecasts["confidence_interval_upper"],
                    name="Upper Bound",
                    line=dict(color="lightblue", width=1, dash="dash"),
                    hovertemplate="<b>Date:</b> %{x|%Y-%m-%d}<br><b>Upper Bound:</b> %{y:.0f}<br><extra></extra>",
                    showlegend=False
                ))
                
                fig_forecast.add_trace(go.Scatter(
                    x=df_forecasts["forecast_date"],
                    y=df_forecasts["confidence_interval_lower"],
                    name="Lower Bound",
                    line=dict(color="lightblue", width=1, dash="dash"),
                    hovertemplate="<b>Date:</b> %{x|%Y-%m-%d}<br><b>Lower Bound:</b> %{y:.0f}<br><extra></extra>",
                    fill="tonexty",
                    fillcolor="rgba(173, 216, 230, 0.2)",
                    showlegend=False
                ))
                
                fig_forecast.update_layout(
                    title=f"Player Count Forecast - Next 7 Days ({selected_game})",
                    xaxis_title="Date",
                    yaxis_title="Predicted Player Count",
                    hovermode="x unified",
                    hoverlabel=dict(bgcolor="white", font_size=12, font_family="Arial")
                )
                
                st.plotly_chart(fig_forecast, use_container_width=True)
                
                # Forecast table
                st.subheader("Forecast Details")
                forecast_display = df_forecasts[
                    ["forecast_date", "predicted_value", "confidence_interval_lower", "confidence_interval_upper"]
                ].copy()
                forecast_display.columns = ["Date", "Predicted", "Lower Bound", "Upper Bound"]
                st.dataframe(forecast_display, use_container_width=True)
                
                # Export button
                st.markdown("---")
                st.subheader("📥 Export Forecast Data")
                create_export_buttons(df_forecasts, f"{selected_game}_forecasts")
            else:
                empty_state(
                    "No forecast data available",
                    icon="🔮",
                    action_text="Insufficient historical data for forecasting"
                )
        
        except Exception as e:
            st.error(f"❌ Error generating forecasts: {str(e)}")
            empty_state("Unable to generate forecasts", icon="⚠️")
