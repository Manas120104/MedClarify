"""
UI components for the medical report analysis feature.
"""

import streamlit as st
from config.settings import Config

def show_report_analysis(report_analyzer):
    """
    Display and handle the medical report analysis UI.
    
    Args:
        report_analyzer: MedicalReportAnalyzer instance to process reports
    """
    st.title("Medical Report Analyzer")
    st.markdown(
        "Upload a medical report (PDF) and get a patient-friendly explanation of the terminology, "
        "findings, and implications."
    )
    
    # File uploader
    uploaded_file = st.file_uploader("Upload a medical report (PDF)", type="pdf")
    
    if uploaded_file is not None:
        # Display file details
        file_details = {"Filename": uploaded_file.name, "File size": f"{uploaded_file.size / 1024:.2f} KB"}
        st.write(file_details)
        
        # Process button
        if st.button("Analyze Report", key="analyze_report"):
            if not Config.validate_config():
                st.error("Please set up your API credentials to continue.")
            else:
                with st.spinner("Analyzing medical report... this may take a moment..."):
                    # Process the report
                    analysis = report_analyzer.analyze_medical_report(uploaded_file)
                    
                    if analysis:
                        # Display sections with appropriate formatting
                        if "MEDICAL TERMS EXPLAINED" in analysis:
                            st.subheader("Medical Terms Explained")
                            st.markdown(analysis["MEDICAL TERMS EXPLAINED"])
                        
                        if "REPORT SUMMARY FOR PATIENT" in analysis:
                            st.subheader("Report Summary")
                            st.markdown(analysis["REPORT SUMMARY FOR PATIENT"])
                        
                        if "KEY FINDINGS" in analysis:
                            st.subheader("Key Findings")
                            st.markdown(analysis["KEY FINDINGS"])
                        
                        if "RECOMMENDED QUESTIONS FOR DOCTOR" in analysis:
                            st.subheader("Recommended Questions for Your Doctor")
                            st.markdown(analysis["RECOMMENDED QUESTIONS FOR DOCTOR"])
                    else:
                        st.error("An error occurred while analyzing the report. Please try again.")