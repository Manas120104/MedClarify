import streamlit as st
from config.settings import Config
from services.vector_db import VectorDatabaseClient
from services.web_search import WebSearchService
from services.claim_processor import HealthClaimProcessor
from services.medical_assistant import MedVerifyAssistant
from services.report_analyzer import MedicalReportAnalyzer
from ui.sidebar import setup_sidebar
from ui.claim_verification import show_claim_verification
from ui.report_analysis import show_report_analysis
from utils.logging_setup import setup_logger,get_default_log_path
import logging

def main():
    # Set up logging
    logger = setup_logger(
    name="medclarify",
    level=logging.INFO,
    log_file=get_default_log_path()
)

    
    # Set page configuration
    st.set_page_config(
        page_title="MedClarify",
        page_icon="🩺",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Validate configuration
    config_valid = Config.validate_config()
    
    # Initialize services if configuration is valid
    services = {}
    if config_valid:
        # Initialize components
        services["vector_db"] = VectorDatabaseClient()
        services["web_search"] = WebSearchService()
        services["claim_processor"] = HealthClaimProcessor()
        services["assistant"] = MedVerifyAssistant(
            services["vector_db"], 
            services["web_search"], 
            services["claim_processor"]
        )
        services["report_analyzer"] = MedicalReportAnalyzer()
    
    # Setup sidebar
    setup_sidebar(services.get("vector_db"))

    st.title("MedClarify")
    st.markdown("### 🩺 Health Claim Verifier & Report Explainer")
    
    # Create tabs for different functionalities
    tab1, tab2 = st.tabs(["Verify Health Claims", "Analyze Medical Reports"])
    
    # Tab 1: Health Claim Verification
    with tab1:
        show_claim_verification(services.get("assistant"))
    
    # Tab 2: Medical Report Analysis
    with tab2:
        show_report_analysis(services.get("report_analyzer"))

if __name__ == "__main__":
    main()