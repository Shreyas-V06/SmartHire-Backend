def CalculateQuantitativeScore(parameter, max_value, benefit_type, query_engine):
    """
    Calculate score for quantitative parameters based on RAG query value and scoring rules.

    Parameters:
    - parameter: String describing the parameter to search for
    - max_value: Maximum acceptable value for normalization
    - benefit_type: String indicating if higher or lower values are better ('higher' or 'lower')
    - query_engine: RAG query engine to search for parameter value

    Returns:
    - score: Calculated percentage score (0-100)
    """
    prompt_quant = f'''Extract the numerical value for: {parameter}

    Instructions:
    Search for the numerical value for the parameter. 
    Do not include any other text in your response.
    Do not round the value off.
    Double check the value is correct or not

    Example outputs:
    3.8
    5
    0
    '''

    response = query_engine.query(prompt_quant)
    try:
        # Clean the response string and extract numbers
        response_str = str(response).strip().lower()
        # Try to find any number in the response
        import re
        numbers = re.findall(r'\d*\.?\d+', response_str)
        if numbers:
            value = float(numbers[0])  # Take the first number found
        else:
            value = 0  # Default to 0 if no number is found
        
        value = int(value) if value.is_integer() else value
    except (ValueError, AttributeError):
        value = 0  # Default to 0 for any parsing errors

    # Cap value at max_value
    value = min(value, max_value)

    if benefit_type.lower() == 'higher':
        # Higher values are better - direct scoring
        score = (value / max_value) * 100
    elif benefit_type.lower() == 'lower':
        # Lower values are better - inverse scoring
        score = 100 - (value / max_value) * 100
    else:
        raise ValueError("benefit_type must be 'higher' or 'lower'")

    return score

