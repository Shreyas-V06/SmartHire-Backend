from llama_index.core import Document
import tempfile
import os
from PyPDF2 import PdfReader
import re
import time
from tenacity import retry, stop_after_attempt, wait_exponential
from ..Utils.RateLimiter import RateLimiter
import hashlib
import pickle
import os

def extract_sections(text):
    """Extract common resume sections from text"""
    # Basic cleanup
    text = text.replace('\n\n', '\n').strip()
    
    # Try to identify sections
    experience_section = ""
    education_section = ""
    skills_section = ""
    
    # Simple section detection
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

# Fix the parameter name to match RateLimiter class
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
    """Load document from uploaded file with retry logic and caching."""
    if uploaded_file is None:
        raise ValueError("No file uploaded")
    
    try:
        # Calculate file hash for caching
        file_content = uploaded_file.getvalue()
        file_hash = hashlib.md5(file_content).hexdigest()
        cache_path = get_cache_path(file_hash)
        
        # Check cache first
        if os.path.exists(cache_path):
            with open(cache_path, 'rb') as f:
                return pickle.load(f)
        
        # Wait if needed due to rate limiting
        rate_limiter.wait_if_needed()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_file_path = os.path.join(temp_dir, uploaded_file.name)
            
            # Save the uploaded file
            with open(temp_file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            # Add small delay to prevent resource exhaustion
            time.sleep(1)
            
            # Extract text from PDF with error handling
            text = ""
            try:
                with open(temp_file_path, "rb") as file:
                    pdf_reader = PdfReader(file)
                    for page in pdf_reader.pages:
                        text += page.extract_text() + "\n"
            except Exception as e:
                raise Exception(f"Error reading PDF: {str(e)}")
            
            # Extract sections
            sections = extract_sections(text)
            
            # Create structured text
            structured_text = f"""
Full Resume Text:
{text}

Experience Section:
{sections['experience']}

Education Section:
{sections['education']}

Skills Section:
{sections['skills']}
"""
            
            # Cache the result
            document = Document(text=structured_text)
            with open(cache_path, 'wb') as f:
                pickle.dump([document], f)
            
            return [document]
            
    except Exception as e:
        if "quota exceeded" in str(e).lower():
            raise Exception("API quota exceeded. Please try again later.")
        raise Exception(f"Error processing document: {str(e)}")

