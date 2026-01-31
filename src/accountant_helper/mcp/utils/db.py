import os
import chromadb
from chromadb.utils import embedding_functions

# Resolve paths relative to this script: .../src/accountant_helper/mcp/utils/db.py
# Root is 4 levels up
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../"))
CHROMA_DB_PATH = os.path.join(PROJECT_ROOT, "data", "vector_db")
COLLECTION_NAME = "eu_accounting_standards_cs"

_client = None
_collection = None

def get_collection():
    global _client, _collection
    if _collection is None:
        if not os.path.exists(CHROMA_DB_PATH):
            raise FileNotFoundError(f"ChromaDB not found at {CHROMA_DB_PATH}. Please run ingestion first.")
            
        _client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
        model_name = "paraphrase-multilingual-MiniLM-L12-v2"
        emb_fn = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=model_name)
        _collection = _client.get_collection(name=COLLECTION_NAME, embedding_function=emb_fn)
    return _collection
