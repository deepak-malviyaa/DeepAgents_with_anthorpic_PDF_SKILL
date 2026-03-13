"""
Calculator Skill

Safely evaluates mathematical expressions.
"""


def run(expression: str) -> str:
    """
    Evaluate a mathematical expression.
    
    Args:
        expression: Math expression to evaluate (e.g., "2+2", "15*23", "pow(2,8)")
    
    Returns:
        Result of the calculation as a string
    """
    try:
        # Safe evaluation with limited builtins
        allowed_names = {
            'abs': abs,
            'round': round,
            'min': min,
            'max': max,
            'sum': sum,
            'pow': pow,
            'len': len,
        }
        
        result = eval(expression, {"__builtins__": {}}, allowed_names)
        
        return f"Result: {result}\n\nCalculation: {expression} = {result}"
        
    except Exception as e:
        return f"Error evaluating expression '{expression}': {str(e)}\n\nPlease check your syntax and try again."
