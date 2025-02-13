import re
import time
from llama_index.llms.gemini import Gemini
from dotenv import load_dotenv
import os

load_dotenv()
google_api_key = os.getenv('GOOGLE_API_KEY')

def extract_number(text):
    """Extract the first number from text."""
    numbers = re.findall(r'\d*\.?\d+', str(text))
    return float(numbers[0]) if numbers else 0

def CalculateQuantitativeScore(parameter, max_value, benefit_type, query_engine):
    """Calculate score for quantitative parameters using RAG."""
    try:
        query_text = f"What is the {parameter}? Return only the numerical value."
        response = query_engine.query(query_text)
        time.sleep(1)  # Rate limiting delay
        
        if not response:
            return 0
            
        raw_value = extract_number(str(response))
        
        # Normalize the score to percentage (0-100)
        if benefit_type == "higher":
            score = min((raw_value / max_value) * 100, 100)
        else:  # Low is better
            score = max((1 - (raw_value / max_value)) * 100, 0)
        
        return score
    except Exception as e:
        print(f"Error in quantitative scoring: {e}")
        return 0

def CalculateBooleanScore(parameter, query_engine):
    """Calculate score for boolean parameters."""
    try:
        query_text = f"Does the candidate have {parameter}? Answer with True or False only."
        response = query_engine.query(query_text)
        time.sleep(1)  # Rate limiting delay
        answer = str(response).lower()
        return 100 if "true" in answer or "yes" in answer else 0
    except Exception as e:
        print(f"Error in boolean scoring: {e}")
        return 0