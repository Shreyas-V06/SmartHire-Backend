import streamlit as st
import pandas as pd
from classification_model import classify_parameter

def parameter_creation_interface():
    st.title("Parameter Creation Interface")
    
    # Initialize session states
    if 'parameters' not in st.session_state:
        st.session_state.parameters = []
    if 'step' not in st.session_state:
        st.session_state.step = 1
        
    # Step 1: Parameter Name and Weight Input
    if st.session_state.step == 1:
        with st.form(key='parameter_form'):
            st.write("### Add New Parameter")
            name = st.text_input("Parameter name (e.g., 'Years of Experience')")
            weight = st.slider("Parameter weight", min_value=0.0, max_value=50.0, value=5.0, step=0.1)
            submit_button = st.form_submit_button("Add Parameter")
            
            if submit_button and name:
                parameter = {
                    "name": name,
                    "weight": weight,
                    "category": None,
                    "max_value": None
                }
                st.session_state.parameters.append(parameter)
        
        # Display current parameters table (only name and weight)
        if st.session_state.parameters:
            df = pd.DataFrame(st.session_state.parameters)[['name', 'weight']]
            df.rename(columns={
                'name': 'Name',
                'weight': 'Weight'
            }, inplace=True)
            df.index = range(1, len(st.session_state.parameters) + 1)
            st.write("### Current Parameters:")
            st.dataframe(df)
        
        # Process Parameters button
        if st.button("Process Parameters") and st.session_state.parameters:
            for param in st.session_state.parameters:
                param["category"] = classify_parameter(param["name"]).text.strip()
            st.session_state.step = 2
            st.rerun()
            
    # Step 2: Set Maximum Values
    elif st.session_state.step == 2:
        st.write("### Set Maximum Values for Quantitative Parameters")
        for param in st.session_state.parameters:
            if param["category"] == "Quantitative":
                param["max_value"] = st.number_input(
                    f"Maximum value for {param['name']}", 
                    min_value=0.1, 
                    value=1.0,
                    step=1.0,
                    key=f"max_value_{param['name']}"
                )
            else:
                param["max_value"] = "-"
        
        # Display table with all details
        df = pd.DataFrame(st.session_state.parameters)
        df.rename(columns={
            'name': 'Name',
            'weight': 'Weight',
            'category': 'Category',
            'max_value': 'Maximum Value'
        }, inplace=True)
        df.index = range(1, len(st.session_state.parameters) + 1)
        st.write("### Parameters with Classifications:")
        st.dataframe(df)
        
        if st.button("Submit All Parameters"):
            st.session_state.step = 3
            return st.session_state.parameters
            
    # Step 3: Final Display
    elif st.session_state.step == 3:
        st.write("### Final Parameters")
        if st.button("Add More Parameters"):
            st.session_state.step = 1
            st.session_state.parameters = []
            st.rerun()
            
        df = pd.DataFrame(st.session_state.parameters)
        df.rename(columns={
            'name': 'Name',
            'weight': 'Weight',
            'category': 'Category',
            'max_value': 'Maximum Value'
        }, inplace=True)
        df.index = range(1, len(st.session_state.parameters) + 1)
        st.dataframe(df)
    
    return None

if __name__ == "__main__":
    parameters = parameter_creation_interface()