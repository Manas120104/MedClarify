"""
UI components for the health claim verification feature.
"""

import json
import streamlit as st
from config.settings import Config

def show_claim_verification(assistant):
    """
    Display and handle the health claim verification UI.
    
    Args:
        assistant: MedVerifyAssistant instance to process claims
    """
    st.title("Health Claim Verification")
    st.markdown(
        "Enter a health claim to verify its validity against our comprehensive database "
        "and trusted medical sources on the web."
    )
    
    # Health claim input
    claim = st.text_area(
        "Enter a health claim for verification:", 
        height=100, 
        placeholder="e.g., 'Vitamin C prevents the common cold' or 'Regular exercise reduces the risk of heart disease'"
    )
    
    col1, col2 = st.columns(2)
    with col1:
        search_k = st.slider("Number of reference sources:", 1, 7, 3)
    
    # Process button
    if st.button("Verify Claim", key="verify_claim"):
        if not claim:
            st.warning("Please enter a health claim to verify.")
        elif not Config.validate_config():
            st.error("Please set up your API credentials to continue.")
        else:
            with st.spinner("Analyzing claim... this may take a moment as I search my database and trusted medical sources..."):
                # Process the claim
                response, results, new_content_added = assistant.verify_claim(claim, top_k=search_k)
                
                # Display results
                st.subheader("Analysis Results")
                st.markdown(response)
                
                # Display references
                if results:
                    st.subheader("Reference Sources")
                    for i, ref in enumerate(results):
                        with st.expander(f"Reference {i+1}: {ref.get('claim', 'Unknown Claim')}"):
                            st.markdown(f"**Evidence Level**: {ref.get('evidence_level', 'Not specified')}")
                            st.markdown(f"**Explanation**: {ref.get('explanation', 'Not available')}")

                            # Add source display that works for both web content and database content
                            sources = ref.get('sources', [])
                            
                            # Standardize source format
                            if isinstance(sources, str):
                                try:
                                    sources = json.loads(sources)
                                except json.JSONDecodeError:
                                    sources = []
                            
                            if sources:
                                st.markdown("**Sources:**")
                                for source in sources:
                                    if isinstance(source, dict):
                                        name = source.get('name', '')
                                        url = source.get('url', '')
                                        if name and url:
                                            st.markdown(f"- [{name}]({url})")
                                        elif name:
                                            st.markdown(f"- {name}")
                                        elif url:
                                            st.markdown(f"- [{url}]({url})")
                                    elif isinstance(source, str):
                                        st.markdown(f"- {source}")

                            # Show badge if new content was added
                            if new_content_added:
                                st.success("✨ New information was found and added to our database!")