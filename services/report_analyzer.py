import os
import re
import tempfile
import PyPDF2
import requests
import logging
import streamlit as st
from config.settings import Config

logger = logging.getLogger(__name__)

class MedicalReportAnalyzer:
    """Analyze and explain medical reports"""
    def __init__(self):
        self.ner_model_url = "https://api-inference.huggingface.co/models/Helios9/BioMed_NER"
        self.llm_url = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.3"
        self.headers = {"Authorization": f"Bearer {Config.HF_TOKEN}"}
    
    def analyze_medical_report(self, pdf_file):
        """Analyze a medical report PDF and provide patient-friendly explanations"""
        try:
            # Extract text from PDF
            pdf_bytes = pdf_file.read()
            pdf_file_obj = tempfile.NamedTemporaryFile(delete=False)
            pdf_file_obj.write(pdf_bytes)
            pdf_file_obj.close()
            
            reader = PyPDF2.PdfReader(pdf_file_obj.name)
            full_text = " ".join(page.extract_text() for page in reader.pages if page.extract_text())
            
            # Clean up temporary file
            os.unlink(pdf_file_obj.name)
            
            # Truncate text to avoid API limits
            truncated_text = full_text[:8000]  # Increased limit for better context
            
            # Step 1: Extract medical terms using NER
            response = requests.post(
                self.ner_model_url,
                headers=self.headers,
                json={"inputs": truncated_text}
            )

            if response.status_code != 200:
                st.error(f"NER model error: {response.status_code}")
                return None
                
            result = response.json()

            # Process NER results
            medical_terms = []
            try:
                if isinstance(result, list):
                    for entity in result:
                        term = entity.get("word", "").strip()
                        if term and len(term) > 3:
                            medical_terms.append(term)
                
                # Remove duplicates and limit terms
                medical_terms = list(set(medical_terms))[:20]
            except Exception as e:
                st.error(f"Error processing NER response: {str(e)}")
                medical_terms = []
            
            # Step 2: Generate explanations and summary using a more powerful model
            explanation_prompt = (
                "You are a medical professional explaining complex medical concepts to patients. Your task is to:\n\n"
                f"1) Explain these medical terms in simple language a patient could understand: {', '.join(medical_terms)}\n\n"
                f"2) Provide a patient-friendly summary of this medical report, explaining what it means for the patient's health:\n\n{truncated_text}\n\n"
                "Format your response with clear headings:\n\n"
                "MEDICAL TERMS EXPLAINED:\n"
                "(Explain all medical terms, tests, conditions, and measurements)\n\n"
                "REPORT SUMMARY FOR PATIENT:\n"
                "(Provide a 2-3 paragraph summary of what the report means in everyday language)\n\n"
                "KEY FINDINGS:\n"
                "(List 3-5 bullet points of the most important information patients should know)\n\n"
                "RECOMMENDED QUESTIONS FOR DOCTOR:\n"
                "(Suggest 3 questions the patient might want to ask their healthcare provider)"
            )
            
            # Make API call to the more powerful LLM model
            response = requests.post(
                self.llm_url,
                headers=self.headers,
                json={"inputs": explanation_prompt, "parameters": {"max_new_tokens": 1500}}
            )
            
            if response.status_code != 200:
                st.error(f"LLM model error: {response.status_code}")
                return None
                
            result = response.json()
            if not isinstance(result, list) or not result:
                st.error("Invalid response from LLM model")
                return None
                
            raw_text = result[0].get("generated_text", "")
            
            # Extract structured sections using regex
            sections = {}
            section_pattern = r"(MEDICAL TERMS EXPLAINED|REPORT SUMMARY FOR PATIENT|KEY FINDINGS|RECOMMENDED QUESTIONS FOR DOCTOR):(.*?)(?=MEDICAL TERMS EXPLAINED|REPORT SUMMARY FOR PATIENT|KEY FINDINGS|RECOMMENDED QUESTIONS FOR DOCTOR:|$)"
            
            matches = re.finditer(section_pattern, raw_text, re.DOTALL)
            for match in matches:
                section_title = match.group(1).strip()
                section_content = match.group(2).strip()
                sections[section_title] = section_content
            
            return sections

        except Exception as e:
            st.error(f"Error analyzing medical report: {str(e)}")
            return None