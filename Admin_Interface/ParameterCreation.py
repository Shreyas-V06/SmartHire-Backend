from AdminInterface.ClassificationModel import classify_parameter

def create_parameter():
    
    # Get parameter name
    name = input("Enter parameter name (e.g., 'Years of Experience'): ")
    
    # Classify parameter
    category = classify_parameter(name).text.strip()
    
    # Get weight (1-10)
    while True:
        try:
            weight = float(input("Enter parameter weight (1-10): "))
            if 1 <= weight <= 10:
                break
            print("Weight must be between 1 and 10")
        except ValueError:
            print("Please enter a valid number")
    
    parameter = {
        "name": name,
        "category": category,
        "weight": weight,
        "max_value": None
    }
    
    # Get max value for quantitative parameters
    if category == "Quantitative":
        while True:
            try:
                max_value = float(input("Enter maximum value for this parameter: "))
                if max_value > 0:
                    break
                print("Maximum value must be greater than 0")
            except ValueError:
                print("Please enter a valid number")
        parameter["max_value"] = max_value
    
    return parameter

def collect_parameters():
   
    parameters = []
    while True:
        parameters.append(create_parameter())
        if input("Add another parameter? (y/n): ").lower() != 'y':
            break
    return parameters
