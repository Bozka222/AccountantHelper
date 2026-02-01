from src.accountant_helper.mcp.utils.db import get_collection

def get_verbatim_text(ref_id: str) -> str:
    """
    Retrieve the verbatim text of a specific article or paragraph using its unique Reference ID.
    
    Args:
        ref_id: The unique reference ID (e.g., "REG:5", "STD:IAS 23:5").
        
    Returns:
        The verbatim text of the requested content.
    """
    try:
        collection = get_collection()
        
        # 1. Try exact match on ref_id in metadata
        search_ref = ref_id.strip()
        
        results = collection.get(
            where={"ref_id": search_ref},
            limit=1
        )
        
        if not results or not results['ids'] or len(results['ids']) == 0:
             # Fallback: Try a semantic query in case the ID was slightly misformatted by LLM
             # but we really want to encourage exact IDs.
             results = collection.query(
                query_texts=[search_ref],
                n_results=1,
                where={"ref_id": search_ref} # Still filter by ref_id if possible
             )

        if not results or not results['ids'] or (isinstance(results['ids'], list) and len(results['ids']) == 0) or (isinstance(results['ids'][0], list) and len(results['ids'][0]) == 0):
            return f"Lituji, ale referenční kód '{ref_id}' nebyl v databázi nalezen."

        # Handle different return formats between collection.get and collection.query
        metadatas = results.get('metadatas')
        if not metadatas:
            return f"Lituji, ale referenční kód '{ref_id}' nebyl v databázi nalezen."

        if isinstance(metadatas[0], list):
            if len(metadatas[0]) == 0:
                return f"Lituji, ale referenční kód '{ref_id}' nebyl v databázi nalezen."
            meta = metadatas[0][0]
        else:
            meta = metadatas[0]

        content = meta.get('content_verbatim', 'Obsah není k dispozici.')
        
        # Strip leading paragraph number or article title if it exists
        # Regulation: "Článek 1 Text..." -> "Text..."
        # Standard: "1 Text..." -> "Text..."
        article_num = meta.get('article_number', '').strip()
        paragraph_num = meta.get('paragraph_number', '').strip()
        
        if article_num and content.startswith(article_num):
            content = content[len(article_num):].strip()
        elif paragraph_num and content.startswith(paragraph_num):
            # Ensure we don't accidentally strip "10" when paragraph is "1"
            # We check if the character after the number is a space or start of text
            if len(content) == len(paragraph_num) or content[len(paragraph_num)] == ' ':
                content = content[len(paragraph_num):].strip()
        
        return content

    except Exception as e:
        return f"Chyba při získávání textu: {str(e)}"

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