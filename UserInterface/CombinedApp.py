import streamlit as st
import pandas as pd
from LoadParameters import LoadParameterDetails, SaveParameterDetails
from DataIngestion import LoadDocument
from ScoreCalculators.QuantitativeParameters import CalculateQuantitativeScore
from ScoreCalculators.BooleanParameters import CalculateBooleanScore
from Model import LoadModel
from Embedding import DownloadGeminiEmbedding
import plotly.express as px
import plotly.graph_objects as go

def setup_page_config():
    st.set_page_config(
        page_title="Resume Evaluation System",
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

def parameter_creation_interface():
    st.title("Parameter Configuration")
    
    if 'parameters' not in st.session_state:
        st.session_state.parameters = []
    if 'step' not in st.session_state:
        st.session_state.step = 1
        
    col1, col2 = st.columns([2, 1])
    
    with col1:
        if st.session_state.step == 1:
            with st.form("parameter_form"):
                st.write("### Add New Parameter")
                name = st.text_input("Parameter Name (e.g., 'Years of Experience')")
                category = st.selectbox(
                    "Parameter Type",
                    ["Quantitative", "Boolean"]
                )
                weight = st.slider("Parameter Weight", 1, 10, 5)
                
                if category == "Quantitative":
                    max_value = st.number_input(
                        "Maximum Value",
                        min_value=0.1,
                        value=10.0,
                        step=0.1
                    )
                else:
                    max_value = None
                
                if st.form_submit_button("Add Parameter"):
                    st.session_state.parameters.append({
                        "name": name,
                        "category": category,
                        "weight": weight,
                        "max_value": max_value
                    })
    
    with col2:
        if st.session_state.parameters:
            st.write("### Current Parameters")
            df = pd.DataFrame(st.session_state.parameters)
            st.dataframe(df, use_container_width=True)
            
            if st.button("Save Parameters"):
                SaveParameterDetails(st.session_state.parameters)
                st.success("Parameters saved successfully!")
                st.session_state.step = 2

def resume_evaluation_interface():
    st.title("Resume Evaluation")
    
    uploaded_file = st.file_uploader("Upload Resume", type=["txt", "pdf"])
    
    if uploaded_file is not None:
        try:
            with st.spinner("Processing resume..."):
                # Load the document
                documents = LoadDocument(uploaded_file)
                
                # Initialize model and query engine
                model = LoadModel()
                query_engine = DownloadGeminiEmbedding(model, documents)
                
                # Load parameter details
                parameter_details = LoadParameterDetails()
                
                # Calculate scores
                total_weighted_score = 0
                total_weight=0
                scores = {}
                
                for param, details in parameter_details.items():
                    if details["type"] == "quantitative":
                        score = CalculateQuantitativeScore(
                            parameter=details["description"],
                            max_value=details["max_value"],
                            benefit_type=details["benefit_type"],
                            query_engine=query_engine
                        )
                    else:  # boolean parameters
                        score = CalculateBooleanScore(
                            parameter=details["description"],
                            query_engine=query_engine
                        )
                    
                    weighted_score = score * details["weight"]
                    total_weighted_score += weighted_score
                    total_weight += details["weight"]
                    scores[param] = {
                        "raw_score": score,
                        "weighted_score": weighted_score,
                        "weight": details["weight"]
                    }
                
                # Display results
                st.header("Evaluation Results")
                
                # Create three columns for metrics
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Overall Score", f"{(total_weighted_score / total_weight) :.2f}")
                
                with col2:
                    passing_score = 70
                    status = "PASS" if total_weighted_score >= passing_score else "FAIL"
                    st.metric("Status", status)
                
                with col3:
                    st.metric("Total Parameters", len(scores))
                
                # Create score breakdown visualization
                fig = go.Figure()
                
                # Add bar chart for scores
                categories = list(scores.keys())
                raw_scores = [scores[cat]["raw_score"] for cat in categories]
                weighted_scores = [scores[cat]["weighted_score"] for cat in categories]
                
                fig.add_trace(go.Bar(
                    name='Raw Score',
                    x=categories,
                    y=raw_scores,
                    marker_color='rgb(55, 83, 109)'
                ))
                
                fig.add_trace(go.Bar(
                    name='Weighted Score',
                    x=categories,
                    y=weighted_scores,
                    marker_color='rgb(26, 118, 255)'
                ))
                
                fig.update_layout(
                    title='Score Breakdown by Parameter',
                    xaxis_tickangle=-45,
                    barmode='group',
                    height=500
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Detailed breakdown in expandable section
                with st.expander("View Detailed Breakdown"):
                    for param, score_details in scores.items():
                        st.markdown(f"""
                        <div class="metric-card">
                            <h3>{param.replace('_', ' ').title()}</h3>
                            <p>Raw Score: {score_details['raw_score']:.1f}</p>
                            <p>Weight: {score_details['weight']:.2f}</p>
                            <p>Weighted Score: {score_details['weighted_score']:.1f}</p>
                        </div>
                        """, unsafe_allow_html=True)
                
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

def main():
    setup_page_config()
    
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Parameter Configuration", "Resume Evaluation"])
    
    if page == "Parameter Configuration":
        parameter_creation_interface()
    else:
        resume_evaluation_interface()

if __name__ == "__main__":
    main() 