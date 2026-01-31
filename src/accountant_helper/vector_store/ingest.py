import json
import os
import chromadb
from chromadb.utils import embedding_functions
from sentence_transformers import SentenceTransformer
from tqdm import tqdm

# Path Configuration
# Resolve paths relative to this script: .../src/accountant_helper/vector_store/ingest.py
# Root is 3 levels up
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
CLEANED_DATA_PATH = os.path.join(PROJECT_ROOT, "data/processed/cleaned_data.json")
CHROMA_DB_PATH = os.path.join(PROJECT_ROOT, "data/vector_db")
COLLECTION_NAME = "eu_accounting_standards_cs"

def ingest():
    print(f"Loading cleaned data from {CLEANED_DATA_PATH}...")
    with open(CLEANED_DATA_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Initialize Chroma Client
    # Persistent storage
    client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
    
    # Use a multilingual embedding model
    # paraphrase-multilingual-MiniLM-L12-v2 is good for Czech and relatively light
    model_name = "paraphrase-multilingual-MiniLM-L12-v2"
    print(f"Initializing embedding model: {model_name}...")
    
    # Custom embedding function for Chroma using SentenceTransformer
    # Note: SentenceTransformerEmbeddingFunction from chromadb.utils uses the same underlying lib
    emb_fn = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=model_name)

    # Get or create collection
    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=emb_fn,
        metadata={"hnsw:space": "cosine"} # Using cosine similarity
    )

    print(f"Ingesting {len(data)} items into ChromaDB...")
    
    # Prepare data for batch insertion
    # Chroma performs best with batches
    batch_size = 100
    for i in tqdm(range(0, len(data), batch_size)):
        batch = data[i : i + batch_size]
        
        ids = [f"id_{i+j}" for j in range(len(batch))]
        documents = [item['text_to_embed'] for item in batch]
        
        # Flatten and stringify metadata for Chroma (it only supports simple types)
        metadatas = []
        for item in batch:
            m = item['metadata'].copy()
            m['type'] = item['type']
            m['content_verbatim'] = item['content'] # Store full text for retrieval
            
            # Convert list hierarchy to string if present
            if 'hierarchy' in m:
                m['hierarchy_str'] = " > ".join(m['hierarchy'])
                del m['hierarchy']
            
            metadatas.append(m)

        collection.add(
            ids=ids,
            documents=documents,
            metadatas=metadatas
        )

    print(f"Ingestion complete. Collection '{COLLECTION_NAME}' now has {collection.count()} items.")

if __name__ == "__main__":
    ingest()
