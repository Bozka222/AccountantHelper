from src.accountant_helper.mcp.utils.db import get_collection

def count_standards() -> dict:
    """
    Returns the total number of indexed articles and paragraphs in the accounting standards database.
    Useful for system health checks or providing context about the knowledge base size.
    """
    try:
        collection = get_collection()
        count = collection.count()
        return {
            "total_records": count,
            "status": "healthy",
            "message": f"The database contains {count} indexed items from EU accounting standards."
        }
    except Exception as e:
        return {
            "total_records": 0,
            "status": "error",
            "message": f"Error counting standards: {str(e)}"
        }
