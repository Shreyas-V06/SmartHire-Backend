import os
from dotenv import load_dotenv
import sys

from llama_index.llms.gemini import Gemini
from IPython.display import Markdown, display
import google.generativeai as genai


load_dotenv()

google_api_key=os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=google_api_key)

def LoadModel():
    
    """
    Loads Gemini-1.5-Pro model for natural language processing.

    Returns:
    - Gemini: An instance of the Gemini class initialized with the 'gemini-pro' model.
    """
    
    model=Gemini(models='gemini-1.5-pro',api_key=google_api_key,temperature=0)
    return model
  