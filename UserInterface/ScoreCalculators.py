import re
import google.generativeai as genai
import os
from llama_index.llms.gemini import Gemini
from dotenv import load_dotenv
import time
from tenacity import retry, wait_exponential, stop_after_attempt

load_dotenv()
google_api_key=os.getenv('GOOGLE_API_KEY') 
genai.configure(api_key=google_api_key)

@retry(wait=wait_exponential(multiplier=1, min=4, max=10),
       stop=stop_after_attempt(3))
def make_gemini_call(prompt, model):
    """Make API call with retry mechanism"""
    try:
        response = model.complete(prompt)
        time.sleep(1)  # Rate limiting delay
        return response
    except Exception as e:
        if "429" in str(e):
            time.sleep(2)  # Additional delay for rate limits
            raise e
        raise e

def CalculateQuantitativeScore(parameter, max_value, benefit_type, resume_text):
    """Calculate score for quantitative parameters using direct prompting."""
    prompt = f"""
    Based on the following resume, what is the {parameter}? 
    Return only the numerical value, with no additional details, words or symbols.
    
    Resume:
    {resume_text}
    """
    
    model = Gemini(models='gemini-1.5-pro', api_key=google_api_key)
    response = make_gemini_call(prompt, model)
    
    try:
        raw_value = float(str(response).strip())
    except ValueError:
        raw_value = 0  # Default value if parsing fails
    
    if benefit_type == "High is better":
        score = min((raw_value / max_value) * 100, 100)
    else:
        score = max((1 - (raw_value / max_value)) * 100, 0)
    
    return score

@retry(wait=wait_exponential(multiplier=1, min=4, max=10),
       stop=stop_after_attempt(3))
def CalculateBooleanScore(parameter, query_engine):
    """Calculate score for boolean parameters with retry."""
    try:
        query_text = f"Does the candidate have {parameter}? Answer with True or False only."
        response = query_engine.query(query_text)
        time.sleep(1)  # Rate limiting delay
        answer = str(response).lower()
        return 100 if "true" in answer or "yes" in answer else 0
    except Exception as e:
        if "429" in str(e):
            time.sleep(2)
            raise e
        return 0  # Default to 0 if all retries fail