import json
import logging
import requests
from typing import Dict, List
from config.settings import Config
from utils.text_processing import extract_json

logger = logging.getLogger(__name__)

class HealthClaimProcessor:
    """Process and verify health claims using LLM"""
    def __init__(self):
        self.hf_api_url = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.3"
        self.headers = {"Authorization": f"Bearer {Config.HF_TOKEN}"}
        
    def synthesize_web_content(self, claim: str, web_content: List[Dict]) -> Dict:
        """Synthesize web search results into a structured health claim"""
        if not web_content:
            return {}
            
        # Combine content from all sources
        combined_content = f"Health claim to analyze: {claim}\n\n"
        
        for i, content in enumerate(web_content):
            combined_content += f"Source {i+1} - {content['title']}\n"
            combined_content += f"URL: {content['link']}\n"
            combined_content += f"Content: {content['content'][:3000]}\n\n"  # Limit content length
        
        # Prompt the LLM to synthesize the information
        prompt = (
            "You are an expert medical researcher analyzing health claims. Based on the following information from "
            f"reputable medical sources, analyze this health claim: '{claim}'\n\n"
            "Structure your response in JSON format with the following fields:\n"
            "1. claim: Restate the health claim clearly\n"
            "2. evidence_level: Categorize as 'High', 'Medium', or 'Low' based on scientific consensus\n"
            "3. explanation: Provide a detailed, evidence-based explanation about the claim's validity\n"
            "4. sources: List the key sources with name and URL\n\n"
            f"Source information:\n{combined_content}\n\n"
            "Output ONLY valid JSON with no additional text. Format:\n"
            "{\n"
            '  "claim": "...",\n'
            '  "evidence_level": "...",\n'
            '  "explanation": "...",\n'
            '  "sources": [\n'
            '    {"name": "...", "url": "..."},\n'
            '    {"name": "...", "url": "..."}\n'
            '  ]\n'
            "}"
        )
        
        try:
            # Make API call to Hugging Face
            response = requests.post(
                self.hf_api_url,
                headers=self.headers,
                json={"inputs": prompt, "parameters": {"max_new_tokens": 800}}
            )
            
            if response.status_code != 200:
                logger.error(f"LLM API error: {response.status_code}")
                return {}
                
            result = response.json()
            logger.info(f"Raw LLM response: {result}")
            # Extract generated text
            if isinstance(result, list) and result:
                generated_text = result[0].get("generated_text", "")
                parsed_json = extract_json(generated_text)

                if parsed_json and all(k in parsed_json for k in ["claim", "evidence_level", "explanation", "sources"]):
                    parsed_json["origin"] = "web_search"
                    return parsed_json
            
            logger.error("Failed to parse LLM response into valid JSON")
            return {}
            
        except Exception as e:
            logger.error(f"Synthesis error: {str(e)}")
            return {}