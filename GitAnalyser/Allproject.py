import requests
import math
from sentence_transformers import SentenceTransformer, util

#############################################
# CONFIGURATION
#############################################

# Gemini API settings
GEMINI_API_ENDPOINT = "https://api.gemini.example.com/v1/generate"  # Replace with the actual endpoint
GEMINI_API_KEY = "GOOGLE_API_KEY"  # Replace with your key
GEMINI_TEMPERATURE = 0.3  # Lower temperature for more deterministic responses

# GitHub API settings
GITHUB_API_TOKEN = "GITHUB_API_KEY"  # Replace with your GitHub token
GITHUB_API_ENDPOINT = "https://api.github.com"

# Normalization factor for project scoring
NORM_FACTOR = 100  # Adjust this value to calibrate the raw scores into a 0-100 scale

#############################################
# HELPER FUNCTIONS
#############################################

def load_embedding_model():
    """
    Load the SentenceTransformer model.
    """
    print("Loading SentenceTransformer model...")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    return model

def compute_text_similarity(text1, text2, model):
    """
    Compute cosine similarity between two texts using SentenceTransformer.
    Returns a value between 0 and 1.
    """
    embeddings = model.encode([text1, text2], convert_to_tensor=True)
    similarity = util.pytorch_cos_sim(embeddings[0], embeddings[1])
    return similarity.item()

def get_github_repos(username):
    """
    Retrieve public repositories for the given GitHub username.
    Returns a list of repositories (as JSON dictionaries).
    """
    headers = {
        "Authorization": f"token {GITHUB_API_TOKEN}"
    }
    repos_url = f"{GITHUB_API_ENDPOINT}/users/{username}/repos"
    response = requests.get(repos_url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"GitHub API Error {response.status_code}: {response.text}")
        return []

def score_repository(repo, job_description, model):
    """
    Calculate a score for a single repository.
    The formula is:
        repo_score = (2 * stars + 1.5 * forks + 1 * watchers) * similarity_factor
    """
    stars = repo.get("stargazers_count", 0)
    forks = repo.get("forks_count", 0)
    watchers = repo.get("watchers_count", 0)
    description = repo.get("description") or ""
    
    if description.strip():
        similarity_factor = compute_text_similarity(description, job_description, model)
    else:
        similarity_factor = 0.5  # default value if no description is provided
    
    raw_score = (2 * stars + 1.5 * forks + 1 * watchers) * similarity_factor
    return raw_score, similarity_factor, stars, forks, watchers, description

def score_github_projects(username, job_description, model):
    """
    Retrieve and score all public repositories for the candidate.
    Returns:
      - final_project_score: normalized to a 0-100 scale.
      - details: a list of dictionaries with repo-level scoring details for breakdown.
    """
    repos = get_github_repos(username)
    total_raw_score = 0
    details = []
    
    for repo in repos:
        repo_score, sim_factor, stars, forks, watchers, description = score_repository(repo, job_description, model)
        total_raw_score += repo_score
        details.append({
            "name": repo.get("name"),
            "score": round(repo_score, 2),
            "similarity": round(sim_factor, 2),
            "stars": stars,
            "forks": forks,
            "watchers": watchers,
            "description": description
        })
    
    final_project_score = min(100, round((total_raw_score / NORM_FACTOR) * 100, 2))
    return final_project_score, details, total_raw_score

def call_gemini_api(prompt, temperature=GEMINI_TEMPERATURE):
    """
    Call the Gemini API with the provided prompt and temperature.
    Returns the generated text response.
    """
    headers = {
        "Content-Type": "application/json"
    }
    
    payload = {
        "contents": [{
            "parts": [{
                "text": prompt
            }]
        }],
        "generationConfig": {
            "temperature": temperature,
            "maxOutputTokens": 800,
        }
    }
    
    try:
        response = requests.post(
            f"{GEMINI_API_ENDPOINT}?key={GEMINI_API_KEY}",
            headers=headers,
            json=payload
        )
        
        if response.status_code == 200:
            data = response.json()
            # Extract text from Gemini's response structure
            if data.get("candidates") and data["candidates"][0].get("content"):
                return data["candidates"][0]["content"]["parts"][0]["text"]
            return "No response text returned."
        else:
            print(f"Gemini API Error {response.status_code}: {response.text}")
            return "Error in generating evaluation."
    except Exception as e:
        print(f"Exception when calling Gemini API: {str(e)}")
        return "Error in generating evaluation."

def generate_project_evaluation(job_description, github_username, final_project_score, total_raw_score, details):
    """
    Generate a detailed evaluation of the candidate's projects using Gemini.
    """
    repo_summary = ""
    sorted_details = sorted(details, key=lambda x: x["score"], reverse=True)
    top_repos = sorted_details[:3]
    for repo in top_repos:
        repo_summary += (f"Repo: {repo['name']}\n"
                         f"- Score: {repo['score']}\n"
                         f"- Similarity: {repo['similarity']}\n"
                         f"- Stars: {repo['stars']}, Forks: {repo['forks']}, Watchers: {repo['watchers']}\n\n")
    
    prompt = (
        "You are an expert technical evaluator. "
        "Evaluate the candidate's project portfolio based on the following details. "
        "The candidate's GitHub username is: " + github_username + ".\n\n"
        "Job Description:\n" + job_description + "\n\n"
        "Project Portfolio Summary:\n"
        f"- Total Raw Project Score: {round(total_raw_score, 2)}\n"
        f"- Final Normalized Project Score (0-100): {final_project_score}\n"
        f"- Top Projects:\n{repo_summary}\n\n"
        "Based on the above, provide a detailed evaluation of how well the candidate's projects "
        "demonstrate the skills and efforts needed for the job, including strengths, weaknesses, and suggestions for improvement. "
        "Conclude with a final recommendation score between 0 and 100."
    )
    return call_gemini_api(prompt, temperature=GEMINI_TEMPERATURE)

#############################################
# MAIN PROGRAM
#############################################

if __name__ == "__main__":
    # Input: Job description and GitHub username
    job_description = input("Enter the job description: ")
    github_username = input("Enter the candidate's GitHub username: ")

    # Load embedding model
    model = load_embedding_model()

    # Score GitHub projects
    final_project_score, repo_details, total_raw_score = score_github_projects(github_username, job_description, model)

    # Display results
    print("\n--- Project Evaluation Score ---")
    print(f"Final Project Score: {final_project_score} / 100")

    print("\n--- Repository Breakdown ---")
    for repo in repo_details:
        print(f"Repo Name: {repo['name']}")
        print(f"- Score: {repo['score']}")
        print(f"- Similarity Factor: {repo['similarity']}")
        print(f"- Stars: {repo['stars']}, Forks: {repo['forks']}, Watchers: {repo['watchers']}")
        print(f"- Description: {repo['description'] or 'No description provided'}")
        print("---")

    # Generate detailed evaluation
    print("\n--- Detailed Evaluation ---")
    evaluation = generate_project_evaluation(job_description, github_username, final_project_score, total_raw_score, repo_details)
    print(evaluation)
