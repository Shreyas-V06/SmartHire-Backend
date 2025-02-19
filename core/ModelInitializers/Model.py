#IMPORT IN ACTUAL 

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
    #returns an instance of the Gemini model   
    model=Gemini(models='gemini-1.5-pro',api_key=google_api_key)
    return model
  