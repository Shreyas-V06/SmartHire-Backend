#IMPORT IN ACTUAL 

import os
from dotenv import load_dotenv
from llama_index.llms.gemini import Gemini

load_dotenv()
google_api_key=os.getenv('GOOGLE_API_KEY') 
llm = Gemini(models='gemini-1.5-pro',api_key=google_api_key)

def ClassifyParameter(parameter):
    # CLASSIFICATION PROMPT TO CLASSIFY THE GIVEN PARAMETER INTO ONE OF THREE CATEGORIES
    
    prompt = f"""
    You are an AI system designed to assist in resume screening. 
    Your task is to classify the given parameter into one of three categories:
    
    1. Quantitative: A parameter measured numerically (e.g., years of experience, number of projects, GPA).  
    2. Boolean: A parameter whose answer is a Yes or No ,they usually begin with 'has','knows','is' words.
       (e.g., "Has AWS Certification?", "Knows DevOps?").  
    3. Textual: A parameter requiring knowledge evaluation,skill-assesment or detailed analysis of the entire
       resume, they usually look for 'knowledge','proficiency','relevance' (e.g., "Proficiency in Python","Knowledge in ML).  
    
    Instructions:  
    - Carefully analyze the parameter and determine the correct category.  
    - Output must be a single word only and should be exactly any three of these
    'Quantitative','Boolean' or 'Textual'
    
    **Input Parameter:** "{parameter}"
    """
   
    response = llm.complete(prompt)
    return response.text.strip()


