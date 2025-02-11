import streamlit as st
from llama_index.core import VectorStoreIndex
from LoadParameters import LoadParameterDetails
from DataIngestion import LoadDocument
from ScoreCalculators.QuantitativeParameters import CalculateQuantitativeScore
from ScoreCalculators.BooleanParameters import CalculateBooleanScore
from Model import LoadModel
from Embedding import DownloadGeminiEmbedding

def main():
    st.title("Resume Evaluation System")
    
    # File upload
    uploaded_file = st.file_uploader("Upload Resume", type=["txt", "pdf"])
    
    if uploaded_file is not None:
        try:
            # Load the document
            documents = LoadDocument(uploaded_file)
            
            # Initialize model and query engine
            model = LoadModel()
            query_engine = DownloadGeminiEmbedding(model, documents)
            
            # Load parameter details
            parameter_details = LoadParameterDetails()
            
            # Calculate scores for each parameter
            total_weighted_score = 0
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
                scores[param] = {
                    "raw_score": score,
                    "weighted_score": weighted_score
                }
            
            # Display results
            st.header("Evaluation Results")
            
            # Show individual parameter scores
            st.subheader("Parameter Scores:")
            for param, score_details in scores.items():
                st.write(f"{param.replace('_', ' ').title()}:")
                st.write(f"Raw Score: {score_details['raw_score']:.2f}")
                st.write(f"Weighted Score: {score_details['weighted_score']:.2f}")
                st.write("---")
            
            # Show final score
            st.subheader("Final Score:")
            st.write(f"{total_weighted_score:.2f}/100")
            
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()
