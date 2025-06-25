import re
import logging
import requests
from typing import List, Dict
from bs4 import BeautifulSoup
from langchain.text_splitter import RecursiveCharacterTextSplitter
from config.settings import Config

logger = logging.getLogger(__name__)

class WebSearchService:
    """Service for searching health information on the web"""
    def __init__(self):
        self.serpapi_key = Config.SERPAPI_KEY
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        
    def search_health_claim(self, query: str) -> List[Dict]:
        """Search for health claim information using SerpAPI"""
        try:
            search_query = f"health claim {query} evidence research"
            search_url = "https://serpapi.com/search"
            
            params = {
                "q": search_query,
                "api_key": self.serpapi_key,
                "engine": "google",
                "num": 10,  # Get top 10 results
                "gl": "us"  # US results
            }
            
            response = requests.get(search_url, params=params)
            if response.status_code != 200:
                logger.error(f"SerpAPI error: {response.status_code}")
                return []
                
            results = response.json()
            organic_results = results.get("organic_results", [])
            
            # Filter for trusted domains
            trusted_results = []
            for result in organic_results:
                link = result.get("link", "")
                if any(domain in link for domain in Config.TRUSTED_DOMAINS):
                    trusted_results.append({
                        "title": result.get("title", ""),
                        "link": link,
                        "snippet": result.get("snippet", "")
                    })
            
            # Extract content from top 3 trusted sources
            extracted_content = []
            for result in trusted_results[:3]:
                content = self._extract_article_content(result["link"])
                if content:
                    extracted_content.append({
                        "title": result["title"],
                        "link": result["link"],
                        "content": content
                    })
            
            return extracted_content
            
        except Exception as e:
            logger.error(f"Web search error: {str(e)}")
            return []
    
    def _extract_article_content(self, url: str) -> str:
        """Extract main content from a webpage"""
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code != 200:
                return ""
                
            soup = BeautifulSoup(response.content, "html.parser")
            
            # Remove unwanted elements
            for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
                tag.extract()
            
            # Extract article content - focus on main content areas
            article_tags = soup.find_all(["article", "main", "div", "section"])
            content = ""
            
            for tag in article_tags:
                if len(tag.get_text(strip=True)) > 200:  # Only substantial content
                    content += tag.get_text(strip=True) + "\n\n"
                    
            # Clean the text
            content = re.sub(r'\s+', ' ', content).strip()
            
            # Truncate if too long
            if len(content) > 10000:
                content = content[:10000]
                
            return content
            
        except Exception as e:
            logger.error(f"Content extraction error for {url}: {str(e)}")
            return ""