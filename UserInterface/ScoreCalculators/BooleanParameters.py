def CalculateBooleanScore(parameter, query_engine):
    """
    Calculate score for boolean parameters based on RAG query value.
    
    Parameters:
    - parameter: String describing the parameter to search for
    - query_engine: RAG query engine to search for parameter value
    
    Returns:
    - score: Calculated score (0 or 100)
    """
    prompt_bool = f'''Determine if the following condition is true: {parameter}

    Instructions:
    1. Search the text carefully for any mention of this condition
    2. Consider both direct and indirect confirmations
    3. If there's any uncertainty, return False
    4. Return ONLY "True" or "False", nothing else

    Example responses:
    True
    False
    '''
    
    response = query_engine.query(prompt_bool)
    
    # Convert response to boolean with extensive pattern matching
    response_str = str(response).strip().lower()
    
    # List of patterns that indicate true
    true_patterns = ['true', 'yes', '1', 'correct', 'confirmed', 'present', 'found']
    
    # Check if any true pattern is in the response
    value = any(pattern in response_str for pattern in true_patterns)
    
    # Score based on boolean value
    score = 100 if value else 0
    
    return score
