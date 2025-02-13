import json
import os
from pathlib import Path

class ParameterManager:
    def __init__(self):
        self.file_path = Path(os.path.dirname(__file__)).parent / "parameters.json"
        # Start with empty default parameters
        self.default_parameters = []
    
    def load_parameters(self):
        """Load parameters from JSON file"""
        try:
            if self.file_path.exists():
                with open(self.file_path, 'r') as file:
                    params = json.load(file)
                    # Convert list to dictionary if needed
                    if isinstance(params, list):
                        return params
                    return list(params.values())
            return self.default_parameters
        except Exception as e:
            print(f"Error loading parameters: {e}")
            return self.default_parameters
    
    def save_parameters(self, parameters):
        """Save parameters to JSON file"""
        # Ensure parameters is a list
        if isinstance(parameters, dict):
            parameters = list(parameters.values())
        with open(self.file_path, 'w') as file:
            json.dump(parameters, file, indent=4)
    
    def get_parameter_details(self):
        """Get parameters in a format suitable for scoring engine"""
        params = self.load_parameters()
        params_dict = {}
        
        for param in params:
            key = param["name"].lower().replace(" ", "_")
            params_dict[key] = {
                "type": param["category"],
                "weight": param["weight"],  # Remove division by 10
                "max_value": param.get("max_value"),
                "benefit_type": "higher" if param.get("benefit_type") == "High is better" else "lower",
                "description": param["name"]
            }
            
        return params_dict
