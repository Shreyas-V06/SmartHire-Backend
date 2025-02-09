from llama_index.core import SimpleDirectoryReader
import sys
import tempfile
import os

def LoadDocument(uploaded_file):
    """
    Load document from uploaded file.

    Parameters:
    - uploaded_file: User interface uploaded file object containing the document

    Returns:
    - A list containing the loaded document
    """       
    if uploaded_file is None:
        raise ValueError("No file uploaded")
            

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_file_path = os.path.join(temp_dir, uploaded_file.name)
        with open(temp_file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
            
        
        loader = SimpleDirectoryReader(temp_dir)
        documents = loader.load_data()
            
        
    return documents
        
