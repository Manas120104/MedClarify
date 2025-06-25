"""
Sidebar components for MedClarify application.
"""

import streamlit as st
from config.settings import Config

def setup_sidebar(vector_db=None):
    """
    Setup the sidebar with application information and status indicators.
    
    Args:
        vector_db: Vector database instance to display stats
    """
    # Application title and info
    st.sidebar.title("About MedClarify")
    st.sidebar.info(
        "MedClarify uses a vector database with web search capabilities to verify health claims "
        "and explain medical reports in patient-friendly language."
    )
    
    # System status indicators
    st.sidebar.subheader("System Status")
    status_col1, status_col2 = st.sidebar.columns(2)
    
    # Vector DB Status
    if vector_db and vector_db.index:
        try:
            stats = vector_db.index.describe_index_stats()
            status_col1.success("Vector DB: ✅")
            st.sidebar.success(f"Connected to vector database with {stats.get('total_vector_count', 0)} health claims")
        except Exception as e:
            status_col1.warning("Vector DB: ⚠️")
            st.sidebar.warning(f"Connected to vector database but couldn't get stats: {str(e)}")
    else:
        status_col1.error("Vector DB: ❌")
        st.sidebar.warning("Failed to connect to vector database")
    
    # API Status
    if Config.HF_TOKEN and Config.SERPAPI_KEY:
        status_col2.success("APIs: ✅")
    else:
        status_col2.error("APIs: ❌")
        st.sidebar.error("Missing API keys. Some features may not work.")