import streamlit as st
import pandas as pd
from AdminInterface.LoadParameters import LoadParameterDetails, SaveParameterDetails
from UserInterface.ModelInitializers.DataIngestion import LoadDocument
from UserInterface.ScoreCalculators import CalculateQuantitativeScore, CalculateBooleanScore
from UserInterface.ModelInitializers.Model import LoadModel
from UserInterface.ModelInitializers.Embedding import DownloadGeminiEmbedding
from AdminInterface.ClassificationModel import ClassifyParameter
import plotly.graph_objects as go
import time

def setup_page_config():
    st.set_page_config(
        page_title="SmartHire System",
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
    
    if 'parameters' not in st.session_state:
        st.session_state.parameters = []
    
    with st.form("parameter_form"):
        st.write("### Add New Parameter")
        name = st.text_input("Parameter Name (e.g., 'Years of Experience')")
        weight = st.slider("Parameter Weight", 1, 10, 5)
        
        if st.form_submit_button("Process Parameter"):
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
                st.session_state.parameters.append({
                    "name": name,
                    "category": category,
                    "weight": weight,
                    "max_value": None,
                    "benefit_type": None
                })
    
    if 'new_param' in st.session_state:
        st.write("### Set Quantitative Parameter Details")
        st.session_state.new_param["max_value"] = st.number_input("Maximum Value", min_value=0.1, value=10.0, step=0.1)
        st.session_state.new_param["benefit_type"] = st.selectbox("Benefit Type", ["High is better", "Low is better"])
        
        if st.button("Save Quantitative Parameter"):
            st.session_state.parameters.append(st.session_state.new_param)
            del st.session_state.new_param
    
    if st.session_state.parameters:
        st.write("### Current Parameters")
        df = pd.DataFrame(st.session_state.parameters)
        st.dataframe(df, use_container_width=True)
        
        if st.button("Save Parameters"):
            SaveParameterDetails(st.session_state.parameters)
            st.success("Parameters saved successfully!")

def user_interface():
    st.title("User Section")
    
    uploaded_file = st.file_uploader("Upload Resume", type=["pdf"])
    
    if uploaded_file is not None:
        try:
            with st.spinner("Processing resume..."):
                # Load the document and extract text properly
                documents = LoadDocument(uploaded_file)
                # Handle documents based on their actual structure
                resume_text = ""
                if isinstance(documents, list):
                    resume_text = " ".join([str(doc) for doc in documents])
                else:
                    resume_text = str(documents)
                
                # Initialize model and query engine for boolean parameters
                model = LoadModel()
                query_engine = DownloadGeminiEmbedding(model, documents)
                
                # Load parameter details
                parameter_details = LoadParameterDetails()
                
                # Calculate scores
                total_weighted_score = 0
                total_weight = 0
                scores = {}
                
                # Add progress bar
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                # Calculate scores with batching
                total_params = len(parameter_details)
                batch_size = 3  # Process 3 parameters at a time
                
                for i in range(0, len(parameter_details), batch_size):
                    batch = parameter_details[i:i + batch_size]
                    
                    for param_detail in batch:
                        param_name = param_detail["name"]
                        try:
                            if param_detail["category"].lower() == "quantitative":
                                score = CalculateQuantitativeScore(
                                    parameter=param_name,
                                    max_value=param_detail["max_value"],
                                    benefit_type=param_detail["benefit_type"],
                                    resume_text=resume_text
                                )
                            elif param_detail["category"].lower() == "boolean":
                                score = CalculateBooleanScore(
                                    parameter=param_name,
                                    query_engine=query_engine
                                )
                            else:
                                continue
                            
                            weighted_score = score * param_detail["weight"]
                            total_weighted_score += weighted_score
                            total_weight += param_detail["weight"]
                            scores[param_name] = {
                                "raw_score": score,
                                "weighted_score": weighted_score,
                                "weight": param_detail["weight"]
                            }
                            
                        except Exception as e:
                            st.warning(f"Error processing parameter {param_name}: {str(e)}")
                            continue
                        
                        # Update progress
                        progress = min((i + len(scores)) / total_params, 1.0)
                        progress_bar.progress(progress)
                        status_text.text(f"Processing parameters... {int(progress * 100)}%")
                        
                    # Add delay between batches
                    time.sleep(2)
                
                progress_bar.empty()
                status_text.empty()

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

        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

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