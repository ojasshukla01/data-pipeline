"""
Data Export Components
Export functionality for dashboard data
"""
import streamlit as st
import pandas as pd
import json
from typing import Dict, List, Any
from io import BytesIO

def export_dataframe_to_csv(df: pd.DataFrame, filename: str = "data.csv") -> BytesIO:
    """Export dataframe to CSV"""
    output = BytesIO()
    df.to_csv(output, index=False)
    output.seek(0)
    return output

def export_dataframe_to_excel(df: pd.DataFrame, filename: str = "data.xlsx") -> BytesIO:
    """Export dataframe to Excel"""
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Data')
    output.seek(0)
    return output

def export_dataframe_to_json(df: pd.DataFrame) -> str:
    """Export dataframe to JSON"""
    return df.to_json(orient='records', indent=2)

def create_export_buttons(df: pd.DataFrame, base_filename: str = "gaming_data"):
    """Create export buttons for dataframe"""
    col1, col2, col3 = st.columns(3)
    
    with col1:
        csv = export_dataframe_to_csv(df, f"{base_filename}.csv")
        st.download_button(
            label="📥 Download CSV",
            data=csv,
            file_name=f"{base_filename}.csv",
            mime="text/csv"
        )
    
    with col2:
        try:
            excel = export_dataframe_to_excel(df, f"{base_filename}.xlsx")
            st.download_button(
                label="📥 Download Excel",
                data=excel,
                file_name=f"{base_filename}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        except ImportError:
            st.info("Excel export requires openpyxl")
    
    with col3:
        json_str = export_dataframe_to_json(df)
        st.download_button(
            label="📥 Download JSON",
            data=json_str,
            file_name=f"{base_filename}.json",
            mime="application/json"
        )
