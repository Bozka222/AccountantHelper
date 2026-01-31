from src.accountant_helper.mcp.utils.db import get_collection

def search_accounting_standards(query: str, n_results: int = 3) -> str:
    """
    Search for EU accounting standards (IAS/IFRS) in Czech based on a semantic query.
    Returns the most relevant articles or paragraphs with their exact citations.
    Use this to find legal text for RAG.
    """
    try:
        collection = get_collection()
        results = collection.query(
            query_texts=[query],
            n_results=n_results
        )
        
        if not results or not results['ids'] or len(results['ids'][0]) == 0:
            return "No relevant accounting standards found for this query."
            
        output = []
        for i in range(len(results['ids'][0])):
            meta = results['metadatas'][0][i]
            hierarchy = meta.get('hierarchy_str', 'Unknown Source')
            content = meta.get('content_verbatim', 'No content available')
            distance = results['distances'][0][i] if 'distances' in results else 0
            
            output.append(f"--- CITATION: {hierarchy} (Relevance Score: {1-distance:.4f}) ---\n{content}\n")
        
        return "\n".join(output)
    except Exception as e:
        return f"Error during search: {str(e)}"