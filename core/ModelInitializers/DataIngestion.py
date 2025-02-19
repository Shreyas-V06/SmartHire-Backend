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