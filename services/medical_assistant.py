import logging
import requests
from typing import Dict, List, Tuple
from config.settings import Config

logger = logging.getLogger(__name__)

class MedVerifyAssistant:
    """Assistant for verifying medical claims with RAG and web search"""
    def __init__(self, vector_db, web_search, claim_processor):
        self.vector_db = vector_db
        self.web_search = web_search
        self.claim_processor = claim_processor
        self.hf_api_url = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.3"
        self.headers = {"Authorization": f"Bearer {Config.HF_TOKEN}"}
        
    def verify_claim(self, claim: str, top_k: int = 5) -> Tuple[str, List[Dict], bool]:
        """Verify a health claim using RAG and web search if needed"""
        # Step 1: Search vector database
        db_results = self.vector_db.search(claim, top_k=top_k)
        
        # Step 2: Determine if results are relevant enough
        relevant_results = [r for r in db_results if r["relevance_score"] > 0.75]
        
        # If we have relevant results, use them
        if relevant_results:  # Only items with score > 0.75
            logger.info(f"Found {len(relevant_results)} relevant results in vector database")
            response = self._generate_response(claim, relevant_results, top_k)
            return response, relevant_results, False
        
        # Step 3: If no relevant results, perform web search
        logger.info("No relevant results in database, performing web search")
        web_content = self.web_search.search_health_claim(claim)
        
        if not web_content:
            # No web results either
            logger.info("No relevant web content found")
            response = self._generate_response(claim, [], top_k)
            return response, [], False
        
        # Step 4: Synthesize web content into a health claim
        synthesized_claim = self.claim_processor.synthesize_web_content(claim, web_content)
        
        # Step 5: Add to vector database if valid
        new_content_added = False
        if synthesized_claim:
            logger.info("Adding synthesized claim to vector database")
            success = self.vector_db.add_claim(synthesized_claim)
            new_content_added = success
            
            # Use synthesized claim as result
            results = [synthesized_claim]
            response = self._generate_response(claim, results, top_k)
            return response, results, new_content_added
        
        # Fallback
        response = self._generate_response(claim, [], top_k)
        return response, [], False
    
    def _generate_response(self, claim: str, retrieved_claims: List[Dict], top_k: int = 3) -> str:
        """Generate a response based on the claim and retrieved information"""
        try:
            # Prepare context from retrieved claims
            context = ""
            # Sort retrieved claims by relevance score in descending order
            sorted_claims = sorted(retrieved_claims, key=lambda x: x.get('relevance_score', 0), reverse=True)
            
            # Limit to top_k results
            top_claims = sorted_claims[:top_k]
            
            if top_claims:
                context = "Retrieved medical evidence (ONLY USE THESE SPECIFIC EVIDENCE ITEMS):\n\n"
                for idx, result in enumerate(top_claims):
                    context += f"Evidence #{idx+1} (Relevance: {result.get('relevance_score', 0):.2f}):\n"
                    context += f"Claim: {result.get('claim', '')}\n"
                    context += f"Evidence Level: {result.get('evidence_level', '')}\n"
                    context += f"Explanation: {result.get('explanation', '')}\n\n"
            
            # Construct prompt
            system_prompt = (
                "You are MedClarify, an expert-level medical claim verification assistant. "
                "Your job is to evaluate health-related claims using only the specific evidence provided. "
                "You respond with clear, structured, and scientifically grounded analysis. "
                "Do not include personal opinions, and do not introduce information that is not explicitly in the provided sources. "
                "Be transparent and concise in your assessments."
            )

            
            instruction_prompt = (
                f"Analyze the following health claim: \"{claim}\"\n\n"
                "IMPORTANT INSTRUCTIONS:\n"
                "1. ONLY reference the specific evidence items provided below\n"
                "2. DO NOT create or generate your own evidence items\n"
                "3. If an evidence item has low relevance, you can mention that it's not strongly related\n"
                "4. Consider whether the claim appears to be supported by evidence\n"
                "5. Analyse the claim's validity based on the evidence\n\n"
            )
            
            if context:
                instruction_prompt += f"Retrieved Evidence:\n{context}\n"
            else:
                instruction_prompt += "No directly relevant evidence was found in our database. Provide a general assessment based on established medical knowledge.\n"
            
            full_prompt = system_prompt + instruction_prompt
            
            # Call the LLM API
            response = requests.post(
                self.hf_api_url,
                headers=self.headers,
                json={"inputs": full_prompt}
            )
            
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and result:
                    generated_text = result[0].get("generated_text", "")
                    # Remove the prompt from response
                    response_only = generated_text.replace(full_prompt, "").strip()
                    return response_only
            
            logger.error(f"LLM API error: {response.status_code}")
            return "I encountered a technical issue while analyzing this claim. Please try again later."
            
        except Exception as e:
            logger.error(f"Response generation error: {str(e)}")
            return "I encountered an error while analyzing this claim. Please try again later."