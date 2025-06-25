import os
import streamlit as st
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Configuration for API keys and services"""
    HF_TOKEN = os.getenv("HF_TOKEN")
    PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
    PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT", "gcp-starter")
    SERPAPI_KEY = os.getenv("SERPAPI_KEY")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    
    EMBEDDING_MODEL = "sentence-transformers/all-mpnet-base-v2"  # Higher quality than MiniLM
    VECTOR_DB_INDEX = "healthclaims"
    VECTOR_DIMENSION = 768  # MPNet embedding dimension
    
    TRUSTED_DOMAINS = [
        "nih.gov", "cdc.gov", "who.int", "mayoclinic.org", "harvard.edu", 
        "hopkinsmedicine.org", "clevelandclinic.org", "healthline.com",
        "webmd.com", "health.harvard.edu", "medlineplus.gov", "ncbi.nlm.nih.gov"
    ]
    
    @classmethod
    def validate_config(cls):
        """Validate if all required credentials are available"""
        missing_keys = []
        
        if not cls.HF_TOKEN:
            missing_keys.append("HF_TOKEN")
        if not cls.PINECONE_API_KEY:
            missing_keys.append("PINECONE_API_KEY")
        if not cls.SERPAPI_KEY:
            missing_keys.append("SERPAPI_KEY")
        
        if missing_keys:
            st.sidebar.error(f"Missing API keys: {', '.join(missing_keys)}")
            return False
        return True