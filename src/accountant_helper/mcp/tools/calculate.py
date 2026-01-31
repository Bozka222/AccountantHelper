import math

def calculate_accounting_formula(expression: str) -> str:
    """
    Execute a mathematical calculation. Use this for all accounting calculations to ensure precision.
    The expression should be a valid Python math expression (e.g., '1500 * 0.21' or 'math.sqrt(256)').
    """
    try:
        # Restricted environment for evaluation
        allowed_names = {
            "__builtins__": None,
            "math": math,
            "abs": abs,
            "round": round,
            "min": min,
            "max": max,
            "sum": sum,
            "pow": pow,
        }
        # Add all math functions directly to allowed_names for convenience
        allowed_names.update({k: v for k, v in vars(math).items() if not k.startswith("_")})
        
        # We use eval with restricted globals and locals
        result = eval(expression, allowed_names, {})
        return f"Calculation: {expression}\nResult: {result}"
    except Exception as e:
        return f"Error calculating expression '{expression}': {str(e)}"