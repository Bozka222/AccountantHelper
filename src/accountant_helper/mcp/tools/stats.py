from src.accountant_helper.mcp.utils.db import get_collection

def count_standards() -> str:
    """
    Returns the total number of indexed articles and paragraphs in the accounting standards database.
    Useful for system health checks or providing context about the knowledge base size.
    """
    try:
        collection = get_collection()
        count = collection.count()
        return f"The database contains {count} indexed items (articles and paragraphs) from EU accounting standards."
    except Exception as e:
        return f"Error counting standards: {str(e)}"
