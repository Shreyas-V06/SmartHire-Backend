#IGNORE , FOR TESTING INTERFACE ONLY

import json
import os

PARAMETERS_FILE = "parameters.json"

def LoadParameterDetails():
    
    if os.path.exists(PARAMETERS_FILE):
        with open(PARAMETERS_FILE, "r") as file:
            return json.load(file)
    return {}

def SaveParameterDetails(parameters):
   
    with open(PARAMETERS_FILE, "w") as file:
        json.dump(parameters, file, indent=4)
