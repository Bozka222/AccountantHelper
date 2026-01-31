from src.accountant_helper.mcp.utils.db import get_collection

def get_citation(query: str, paragraph_number: str = None) -> str:
    """
    Retrieve a specific citation from the accounting standards.
    
    Args:
        query: The standard or context to look for (e.g., "IAS 1").
        paragraph_number: Optional specific paragraph number (e.g., "15").
        
    Returns:
        The verbatim text of the requested citation or a search result if an exact match isn't found.
    """
    try:
        collection = get_collection()
        
        where_clause = {}
        
        # If we have a paragraph number, we can try to filter by it.
        # Note: Depending on how strict the user is, they might say "15" or "15." or "odst. 15".
        # The metadata 'paragraph_number' is stored as the raw number string (e.g. "15").
        if paragraph_number:
            where_clause["paragraph_number"] = paragraph_number.strip()
            
        # If query is provided, we use it for semantic search but filter by the where_clause
        # Using a higher n_results to filter down after if needed, but Chroma does pre-filtering with 'where'
        
        results = collection.query(
            query_texts=[query],
            n_results=5,
            where=where_clause if where_clause else None
        )
        
        if not results or not results['ids'] or len(results['ids'][0]) == 0:
            return f"No citation found for '{query}'" + (f" with paragraph '{paragraph_number}'" if paragraph_number else ".")

        output = []
        # Filter results closer to the query standard in the hierarchy string?
        # The semantic search does this naturally.
        
        for i in range(len(results['ids'][0])):
            meta = results['metadatas'][0][i]
            hierarchy = meta.get('hierarchy_str', 'Unknown Source')
            content = meta.get('content_verbatim', 'No content available')
            
            # If paragraph number was requested, we are confident.
            # If not, we rely on semantic relevance.
            
            output.append(f"--- CITATION: {hierarchy} ---\n{content}\n")
            
        return "\n".join(output)

    except Exception as e:
        return f"Error retrieval citation: {str(e)}"