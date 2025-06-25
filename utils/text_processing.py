"""
Text processing utilities for MedClarify application.
"""

import json
import re
from typing import Dict, Optional

def extract_json(text: str) -> Optional[Dict]:
    """
    Extract first complete JSON object from a string using bracket balancing.
    
    Args:
        text: Text containing JSON object
        
    Returns:
        Parsed JSON object or None if extraction failed
    """
    try:
        stack = []
        start = None
        for i, char in enumerate(text):
            if char == '{':
                if start is None:
                    start = i
                stack.append('{')
            elif char == '}':
                if stack:
                    stack.pop()
                    if not stack:
                        json_str = text[start:i+1]
                        return json.loads(json_str)
        return None
    except json.JSONDecodeError:
        return None

def clean_text(text: str) -> str:
    """
    Clean and normalize text for processing.
    
    Args:
        text: Input text to clean
        
    Returns:
        Cleaned text string
    """
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text