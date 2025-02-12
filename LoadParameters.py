import json
import os

PARAMETERS_FILE = "parameters.json"

def LoadParameterDetails():
    """
    Load parameter details from a JSON file.

    Returns:
    - A dictionary containing parameter details
    """
    if os.path.exists(PARAMETERS_FILE):
        with open(PARAMETERS_FILE, "r") as file:
            return json.load(file)
    return {}

def SaveParameterDetails(parameters):
    """
    Save parameter details to a JSON file.

    Parameters:
    - parameters: A list of parameter details to save
    """
    with open(PARAMETERS_FILE, "w") as file:
        json.dump(parameters, file, indent=4)
