#IMPORT IN ACTUAL 

from llama_index.core import VectorStoreIndex
from llama_index.core import Settings
from llama_index.core import StorageContext, load_index_from_storage
from llama_index.embeddings.gemini import GeminiEmbedding

def DownloadGeminiEmbedding(model, documents):
    # Load the Gemini embedding model
    gemini_embed_model = GeminiEmbedding(model_name="models/embedding-001")
    
    # Set the model and embedding model in the settings
    Settings.llm = model
    Settings.embed_model = gemini_embed_model 
    Settings.chunk_size = 70  #lower chunk size for extracting minute details
    Settings.chunk_overlap = 10

    index = VectorStoreIndex.from_documents(documents)
    index.storage_context.persist()

    query_engine = index.as_query_engine()
    return query_engine