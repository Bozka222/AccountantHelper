import os
import chromadb
from chromadb.utils import embedding_functions

# Resolve paths relative to this script: .../src/accountant_helper/vector_store/search.py
# Root is 3 levels up
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
CHROMA_DB_PATH = os.path.join(PROJECT_ROOT, "data/vector_db")
COLLECTION_NAME = "eu_accounting_standards_cs"

def search(query_text, n_results=3):
    client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
    
    model_name = "paraphrase-multilingual-MiniLM-L12-v2"
    emb_fn = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=model_name)

    collection = client.get_collection(
        name=COLLECTION_NAME,
        embedding_function=emb_fn
    )

    results = collection.query(
        query_texts=[query_text],
        n_results=n_results
    )

    return results

if __name__ == "__main__":
    import sys
    query = sys.argv[1] if len(sys.argv) > 1 else "Co je to IAS 1?"
    
    print(f"Searching for: '{query}'")
    res = search(query)
    
    for i in range(len(res['ids'][0])):
        print(f"\n--- Result {i+1} (Score: {res['distances'][0][i]:.4f}) ---")
        # print(f"ID: {res['ids'][0][i]}")
        meta = res['metadatas'][0][i]
        print(f"Source: {meta.get('hierarchy_str', 'N/A')}")
        print(f"Content: {meta.get('content_verbatim')[:300]}...")
