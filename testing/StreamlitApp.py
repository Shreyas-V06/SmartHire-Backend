import streamlit as st
import pandas as pd
import sys
import os

# Add project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.append(project_root)

from core.ModelInitializers.DataIngestion import LoadDocument
from core.ScoreCalculators.ScoreCalculators import (
    CalculateQuantitativeScore, 
    CalculateBooleanScore,
    CalculateTextualScore
)
from core.ModelInitializers.Model import LoadModel
from core.ModelInitializers.Embedding import DownloadGeminiEmbedding
from interfaces.admin.ClassificationModel import ClassifyParameter
import time
from interfaces.utils.ParameterManager import ParameterManager

def setup_page_config():
    st.set_page_config(
        page_title="SmartHire System-T2",
        page_icon="📄",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS
    st.markdown("""
        <style>
        .main {
            padding: 2rem;
        }
        .stButton > button {
            width: 100%;
            border-radius: 5px;
            height: 3em;
            background-color: #4CAF50;
            color: white;
        }
        .stTextInput > div > div > input {
            border-radius: 5px;
        }
        .stNumberInput > div > div > input {
            border-radius: 5px;
        }
        .css-1d391kg {
            padding: 2rem 1rem;
        }
        h1 {
            color: #1E88E5;
            text-align: center;
            padding-bottom: 2rem;
        }
        h2 {
            color: #424242;
        }
        .metric-card {
            background-color: #f8f9fa;
            padding: 1rem;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 1rem;
        }
        </style>
    """, unsafe_allow_html=True)

def admin_interface():
    st.title("Admin Section")
    
    param_manager = ParameterManager()
    
    # Initialize session state for parameters if not exists
    if 'current_session_parameters' not in st.session_state:
        st.session_state.current_session_parameters = []
    
    # Reset parameters button
    if st.button("Reset Parameters"):
        st.session_state.current_session_parameters = []
        st.rerun()
    
    with st.form("parameter_form"):
        st.write("### Add New Parameter")
        name = st.text_input("Parameter Name (e.g., 'Years of Experience')")
        weight = st.slider("Parameter Weight", min_value=0.0, max_value=20.0, value=5.0, step=0.1)
        
        if st.form_submit_button("Process Parameter"):
            if name:  # Only process if name is not empty
                category = ClassifyParameter(name).strip().lower()
                if category == "quantitative":
                    st.session_state.new_param = {
                        "name": name,
                        "category": category,
                        "weight": weight,
                        "max_value": None,
                        "benefit_type": None
                    }
                else:
                    new_param = {
                        "name": name,
                        "category": category,
                        "weight": weight,
                        "max_value": None,
                        "benefit_type": None
                    }
                    st.session_state.current_session_parameters.append(new_param)
                st.rerun()
    
    if 'new_param' in st.session_state:
        st.write("### Set Quantitative Parameter Details")
        st.session_state.new_param["max_value"] = st.number_input("Maximum Value", min_value=0.1, value=10.0, step=0.1)
        st.session_state.new_param["benefit_type"] = st.selectbox("Benefit Type", ["High is better", "Low is better"])
        
        if st.button("Save Quantitative Parameter"):
            st.session_state.current_session_parameters.append(st.session_state.new_param)
            del st.session_state.new_param
            st.rerun()
    
    if st.session_state.current_session_parameters:
        st.write("### Current Session Parameters")
        
        # Create a more attractive dataframe
        df = pd.DataFrame(st.session_state.current_session_parameters)
        
        # Rename columns for better display
        df = df.rename(columns={
            'name': 'Parameter Name',
            'category': 'Type',
            'weight': 'Weight',
            'max_value': 'Maximum Value',
            'benefit_type': 'Scoring Type'
        })
        
        # Apply styling to the dataframe
        styled_df = df.style.set_properties(**{
            'background-color': '#f0f2f6',
            'color': '#1e1e1e',
            'border-color': '#e1e4e8'
        }).set_table_styles([
            {'selector': 'th',
             'props': [('background-color', '#0e1117'),
                      ('color', 'white'),
                      ('font-weight', 'bold'),
                      ('padding', '12px 15px')]},
            {'selector': 'td',
             'props': [('padding', '8px 15px')]},
        ]).hide(axis="index")
        
        st.dataframe(styled_df, use_container_width=True)
        
        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button("Save All Parameters", key="save_params"):
                param_manager.save_parameters(st.session_state.current_session_parameters)
                st.success("Parameters saved successfully!")
                # Keep the parameters in session until explicitly reset
        with col2:
            st.info("Click 'Reset Parameters' at the top to start fresh.")

def user_interface():
    param_manager = ParameterManager()
    
    st.title("User Section")
    
    # Add debug expander
    debug_mode = st.sidebar.checkbox("Enable Debug Mode")
    
    uploaded_file = st.file_uploader("Upload Resume", type=["pdf"])
    
    if uploaded_file is not None:
        try:
            with st.spinner("Processing resume..."):
                documents = LoadDocument(uploaded_file)
                if not documents:
                    st.error("Could not process the uploaded file")
                    return
                    
                model = LoadModel()
                query_engine = DownloadGeminiEmbedding(model, documents)
                
                # Extract resume text
                resume_text = " ".join([doc.text for doc in documents])
                
                parameter_details = param_manager.get_parameter_details()
                if not parameter_details:
                    st.warning("No parameters configured. Please set up parameters in the Admin Section first.")
                    return
                    
                scores = {}
                total_weighted_score = 0.0
                total_weight = 0.0
                
                for param_name, details in parameter_details.items():
                    try:
                        parameter_type = details["type"].lower()
                        weight = float(details.get("weight", 0))
                        
                        if weight <= 0:
                            continue
                            
                        if parameter_type == "textual":
                            if debug_mode:
                                st.write(f"---\nProcessing textual parameter: {param_name}")
                                st.write("Parameter details:", details)
                                st.write("Resume text sample:", resume_text[:500] + "...")
                                
                            score = CalculateTextualScore(
                                parameter=details["description"],
                                resume_text=resume_text
                            )
                            
                            if debug_mode:
                                st.write(f"Response is calculated")
                                st.write("---")
                                
                        elif parameter_type == "quantitative":
                            score = CalculateQuantitativeScore(
                                parameter=details["description"],
                                max_value=details["max_value"],
                                benefit_type=details["benefit_type"],
                                query_engine=query_engine
                            )
                        elif parameter_type == "boolean":
                            score = CalculateBooleanScore(
                                parameter=details["description"],
                                query_engine=query_engine
                            )
                        
                        weighted_score = score * weight
                        scores[param_name] = {
                            "raw_score": score,
                            "weighted_score": weighted_score,
                            "weight": weight
                        }
                        
                        if debug_mode:
                            st.write(f"Final weighted score for {param_name}: {weighted_score}")
                        
                        total_weighted_score += weighted_score
                        total_weight += weight
                        
                    except Exception as e:
                        st.warning(f"Error processing parameter {param_name}: {str(e)}")
                        if debug_mode:
                            st.error(f"Full error details for {param_name}: {str(e)}")
                            st.exception(e)
                        continue
                
                # Only calculate final score if we have valid scores
                if scores and total_weight > 0:
                    final_score = (total_weighted_score / total_weight)
                    # Display results
                    st.header("Evaluation Results")
                    
                    # Calculate final score as percentage
                    final_score = float((total_weighted_score / total_weight))
                    passing_score = 70.0
                    status = "PASS" if final_score >= passing_score else "FAIL"
                    
                    # Create professional score display with darker background
                    st.markdown(f"""
                    <div style='background-color: #2C3E50; padding: 20px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.2);'>
                        <div style='text-align: center; padding: 20px;'>
                            <h1 style='font-size: 48px; color: {"#00c853" if status == "PASS" else "#ff5252"};'>
                                {final_score:.2f}
                            </h1>
                            <p style='font-size: 24px; color: #ffffff;'>Overall Score</p>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Display key metrics with darker background
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.markdown("""
                        <div style='background-color: #34495E; padding: 20px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.2); text-align: center;'>
                            <h3 style='color: #ffffff;'>Status</h3>
                        """, unsafe_allow_html=True)
                        st.markdown(f"""
                            <h2 style='color: {"#00c853" if status == "PASS" else "#ff5252"};'>{status}</h2>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col2:
                        st.markdown("""
                        <div style='background-color: #34495E; padding: 20px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.2); text-align: center;'>
                            <h3 style='color: #ffffff;'>Parameters Evaluated</h3>
                        """, unsafe_allow_html=True)
                        st.markdown(f"""
                            <h2 style='color: #ffffff;'>{len(scores)}</h2>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col3:
                        st.markdown("""
                        <div style='background-color: #34495E; padding: 20px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.2); text-align: center;'>
                            <h3 style='color: #ffffff;'>Passing Score</h3>
                        """, unsafe_allow_html=True)
                        st.markdown(f"""
                            <h2 style='color: #ffffff;'>{passing_score:.2f}</h2>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # Add spacing
                    st.markdown("<br>", unsafe_allow_html=True)
                    
                    # Display parameter scores in a dark table
                    st.markdown("""
                    <div style='background-color: #34495E; padding: 20px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.2);'>
                        <h3 style='color: #ffffff;'>Parameter Scores</h3>
                    """, unsafe_allow_html=True)
                    
                    # Create and display the dataframe with proper decimal formatting
                    scores_df = pd.DataFrame([
                        {
                            "Parameter": param,
                            "Score": f"{details['raw_score']:.2f}",
                            "Weight": f"{details['weight']:.2f}",
                            "Weighted Score": f"{details['weighted_score']:.2f}"
                        }
                        for param, details in scores.items()
                    ])
                    
                    st.dataframe(
                        scores_df,
                        hide_index=True,
                        use_container_width=True
                    )
                    
                    st.markdown("</div>", unsafe_allow_html=True)
                else:
                    st.error("No parameters were successfully evaluated")
                    return

        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            st.exception(e)  # Show detailed error in development

def main():
    setup_page_config()
    
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox("Go to", ["Admin Section", "User Section"])
    
    if page == "Admin Section":
        admin_interface()
    else:
        user_interface()

if __name__ == "__main__":
    main()