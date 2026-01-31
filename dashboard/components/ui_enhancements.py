"""
UI Enhancement Components
Better styling, loading states, and user experience
"""
import streamlit as st
from typing import Optional, Dict, Any
import time

def apply_custom_css():
    """Apply custom CSS for better UI/UX"""
    st.markdown("""
    <style>
    /* Main container styling */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* Metric cards styling */
    [data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: bold;
    }
    
    [data-testid="stMetricLabel"] {
        font-size: 0.9rem;
        color: #666;
    }
    
    /* Sidebar styling - Ensure all text is visible on white background */
    [data-testid="stSidebar"] {
        background-color: #ffffff !important;
    }
    
    /* Force dark text color for ALL sidebar elements */
    [data-testid="stSidebar"] * {
        color: #1f1f1f !important;
    }
    
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] h4,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] div,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] .stMarkdown,
    [data-testid="stSidebar"] .stMarkdown * {
        color: #1f1f1f !important;
    }
    
    /* Selectbox styling */
    [data-testid="stSidebar"] .stSelectbox label {
        color: #1f1f1f !important;
    }
    
    [data-testid="stSidebar"] .stSelectbox > div > div {
        background-color: #ffffff !important;
        color: #1f1f1f !important;
    }
    
    /* Button styling */
    [data-testid="stSidebar"] .stButton > button {
        color: #ffffff !important;
        background-color: #1f77b4 !important;
    }
    
    /* Info boxes */
    .stInfo {
        background-color: #e7f3ff;
        border-left: 4px solid #1f77b4;
        color: #1f1f1f;
    }
    
    .stSuccess {
        background-color: #d4edda;
        border-left: 4px solid #28a745;
        color: #155724;
    }
    
    .stWarning {
        background-color: #fff3cd;
        border-left: 4px solid #ffc107;
        color: #856404;
    }
    
    .stError {
        background-color: #f8d7da;
        border-left: 4px solid #dc3545;
        color: #721c24;
    }
    
    /* Chart containers */
    .js-plotly-plot {
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    /* Dataframe styling */
    .dataframe {
        border-radius: 8px;
    }
    
    /* Header styling */
    h1 {
        color: #1f77b4;
        border-bottom: 3px solid #1f77b4;
        padding-bottom: 0.5rem;
    }
    
    h2 {
        color: #2c3e50;
        margin-top: 2rem;
    }
    
    h3 {
        color: #34495e;
    }
    
    /* Loading spinner */
    .loading-spinner {
        display: inline-block;
        width: 20px;
        height: 20px;
        border: 3px solid rgba(31, 119, 180, 0.3);
        border-radius: 50%;
        border-top-color: #1f77b4;
        animation: spin 1s ease-in-out infinite;
    }
    
    @keyframes spin {
        to { transform: rotate(360deg); }
    }
    
    /* Tooltip styling */
    [title] {
        cursor: help;
    }
    
    /* Section dividers */
    hr {
        margin: 2rem 0;
        border: none;
        border-top: 2px solid #e0e0e0;
    }
    </style>
    """, unsafe_allow_html=True)

def show_loading_spinner(text: str = "Loading..."):
    """Show loading spinner"""
    return st.spinner(text)

def empty_state(message: str, icon: str = "📊", action_text: Optional[str] = None):
    """Show empty state with message"""
    st.markdown(f"""
    <div style="text-align: center; padding: 3rem; color: #666;">
        <div style="font-size: 4rem; margin-bottom: 1rem;">{icon}</div>
        <h3 style="color: #999;">{message}</h3>
        {f'<p style="color: #999;">{action_text}</p>' if action_text else ''}
    </div>
    """, unsafe_allow_html=True)

def metric_card(label: str, value: Any, delta: Optional[str] = None, help_text: Optional[str] = None):
    """Enhanced metric card with help text"""
    col1, col2 = st.columns([10, 1])
    with col1:
        st.metric(label, value, delta=delta)
    if help_text:
        with col2:
            st.markdown(f'<span title="{help_text}">ℹ️</span>', unsafe_allow_html=True)

def section_header(title: str, icon: str = "📊", help_text: Optional[str] = None):
    """Create a styled section header"""
    if help_text:
        col1, col2 = st.columns([10, 1])
        with col1:
            st.markdown(f"### {icon} {title}")
        with col2:
            st.markdown(f'<div style="margin-top: 20px;"><span title="{help_text}">ℹ️</span></div>', unsafe_allow_html=True)
    else:
        st.markdown(f"### {icon} {title}")

def success_badge(text: str):
    """Show success badge"""
    st.markdown(f'<span style="background-color: #d4edda; color: #155724; padding: 0.25rem 0.5rem; border-radius: 4px; font-size: 0.875rem;">✅ {text}</span>', unsafe_allow_html=True)

def warning_badge(text: str):
    """Show warning badge"""
    st.markdown(f'<span style="background-color: #fff3cd; color: #856404; padding: 0.25rem 0.5rem; border-radius: 4px; font-size: 0.875rem;">⚠️ {text}</span>', unsafe_allow_html=True)

def info_badge(text: str):
    """Show info badge"""
    st.markdown(f'<span style="background-color: #d1ecf1; color: #0c5460; padding: 0.25rem 0.5rem; border-radius: 4px; font-size: 0.875rem;">ℹ️ {text}</span>', unsafe_allow_html=True)
