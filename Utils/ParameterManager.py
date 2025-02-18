import json
import os
from pathlib import Path
from typing import Dict

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
    
    def get_parameter_details(self) -> Dict:
        """Load and convert parameters to dictionary format."""
        try:
            params = self.load_parameters()
            return {
                param["name"].lower().replace(" ", "_"): {
                    "type": param["category"],
                    "weight": param["weight"],
                    "max_value": param.get("max_value"),
                    "benefit_type": "higher" if param.get("benefit_type") == "High is better" else "lower",
                    "description": param["name"]
                }
                for param in params
            }
        except Exception as e:
            print(f"Error getting parameter details: {e}")
            return {}

    def validate_parameter(self, param: Dict) -> bool:
        required_fields = ["name", "category", "weight"]
        if not all(field in param for field in required_fields):
            return False
            
        if param["category"].lower() == "quantitative":
            return "max_value" in param and "benefit_type" in param
        elif param["category"].lower() in ["boolean", "textual"]:
            return True
            
        return False
