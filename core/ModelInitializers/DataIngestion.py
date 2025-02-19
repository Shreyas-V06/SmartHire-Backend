#IMPORT IN ACTUAL 


from llama_index.core import Document, SimpleDirectoryReader
import tempfile
import os
from PyPDF2 import PdfReader
import re
import time
from tenacity import retry, stop_after_attempt, wait_exponential
from interfaces.utils.RateLimiter import RateLimiter
import hashlib
import pickle
import os

def extract_sections(text):
    """Extract common resume sections from text"""
    
    text = text.replace('\n\n', '\n').strip()
    
    #Dividing the resume into sections for accurate extraction
    experience_section = ""
    education_section = ""
    skills_section = ""
       
    sections = text.split('\n')
    current_section = ""
    
    for line in sections:
        line = line.strip()
        lower_line = line.lower()
        
        if any(keyword in lower_line for keyword in ['experience', 'work history', 'employment']):
            current_section = "experience"
            continue
        elif any(keyword in lower_line for keyword in ['education', 'academic', 'qualification']):
            current_section = "education"
            continue
        elif any(keyword in lower_line for keyword in ['skills', 'technologies', 'competencies']):
            current_section = "skills"
            continue
            
        if current_section == "experience":
            experience_section += line + "\n"
        elif current_section == "education":
            education_section += line + "\n"
        elif current_section == "skills":
            skills_section += line + "\n"
    
    return {
        "experience": experience_section.strip(),
        "education": education_section.strip(),
        "skills": skills_section.strip(),
    }

# Rate limiter for API requests
rate_limiter = RateLimiter(max_requests=50, window_size=60)

def get_cache_path(file_hash):
    cache_dir = os.path.join(os.path.dirname(__file__), '../cache')
    os.makedirs(cache_dir, exist_ok=True)
    return os.path.join(cache_dir, f"{file_hash}.pickle")

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10)
)
def LoadDocument(uploaded_file):
    """Load and process uploaded document."""
    try:
        # Save uploaded file temporarily
        with open(f"temp_upload.pdf", "wb") as f:
            f.write(uploaded_file.getbuffer())
            
        # Load using SimpleDirectoryReader
        documents = SimpleDirectoryReader(input_files=["temp_upload.pdf"]).load_data()
        
        
        import os
        os.remove("temp_upload.pdf")
        
        return documents
    except Exception as e:
        print(f"Error loading document: {e}")
        return None