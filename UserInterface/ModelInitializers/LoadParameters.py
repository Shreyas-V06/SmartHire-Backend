import json
import os

def SaveParameterDetails(parameters):
    """
    Saves parameter details to a JSON file.
    
    Parameters:
    - parameters: List of parameter dictionaries
    """
    parameter_details = {}
    
    for param in parameters:
        param_dict = {
            "type": param["category"].lower(),
            "weight": param["weight"] / 10,  # Convert 1-10 scale to 0-1
            "description": param["name"]
        }
        
        # Add max_value and benefit_type for quantitative parameters
        if param["category"] == "Quantitative":
            param_dict["max_value"] = param["max_value"]
            param_dict["benefit_type"] = "higher"  # Default to higher
            
        parameter_details[param["name"].lower().replace(" ", "_")] = param_dict
    
    # Save to JSON file
    with open('parameter_details.json', 'w') as f:
        json.dump(parameter_details, f, indent=4)

def LoadParameterDetails():
    """
    Loads parameter details from JSON file.
    
    Returns:
    - parameter_details: Dictionary with parameter specifications
    """
    try:
        with open('parameter_details.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        # Return default parameters if file doesn't exist
        return {
            "years_of_experience": {
                "type": "quantitative",
                "weight": 0.3,
                "max_value": 10,
                "benefit_type": "higher",
                "description": "Total years of professional experience"
            },
            "has_relevant_degree": {
                "type": "boolean",
                "weight": 0.2,
                "description": "Whether candidate has a relevant degree"
            }
        }

