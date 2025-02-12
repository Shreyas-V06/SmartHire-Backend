from llama_index.core import VectorStoreIndex
from llama_index.core import Settings
from llama_index.core import StorageContext, load_index_from_storage
from llama_index.embeddings.gemini import GeminiEmbedding

def DownloadGeminiEmbedding(model, documents):
    """
    Downloads and initializes a Gemini Embedding model for vector embeddings.

    Parameters:
    - model: The loaded Gemini language model
    - documents: List of documents to embed

    Returns:
    - query_engine: Query engine for the vector index
    """
    gemini_embed_model = GeminiEmbedding(model_name="models/embedding-001")

    Settings.llm = model
    Settings.embed_model = gemini_embed_model 
    Settings.chunk_size = 70
    Settings.chunk_overlap = 10

    index = VectorStoreIndex.from_documents(documents)
    index.storage_context.persist()

    query_engine = index.as_query_engine()
    return query_engine
