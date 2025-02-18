import re
import requests
import base64

# GitHub API settings
GITHUB_API_TOKEN = "insert_key"  # Replace with your GitHub token
GITHUB_API_ENDPOINT = "https://api.github.com"

def fetch_user_repos(username):
    """
    Fetch all public repositories for the given username.
    """
    headers = {"Authorization": f"token {GITHUB_API_TOKEN}"}
    url = f"{GITHUB_API_ENDPOINT}/users/{username}/repos"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching repositories: {response.status_code} - {response.text}")
        return []

def fetch_repo_details(owner, repo_name):
    """
    Fetch details of a specific repository.
    """
    headers = {"Authorization": f"token {GITHUB_API_TOKEN}"}
    url = f"{GITHUB_API_ENDPOINT}/repos/{owner}/{repo_name}"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    elif response.status_code == 404:
        return {"error": "Repository not found."}
    else:
        print(f"Error fetching repository: {response.status_code} - {response.text}")
        return {}

def fetch_repo_commits(owner, repo_name, username):
    """
    Fetch commit history for a repository and filter by the candidate's username.
    """
    headers = {"Authorization": f"token {GITHUB_API_TOKEN}"}
    url = f"{GITHUB_API_ENDPOINT}/repos/{owner}/{repo_name}/commits?author={username}"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching commits: {response.status_code} - {response.text}")
        return []

import base64

def fetch_readme(owner, repo_name):
    """
    Fetch the README.md content for a repository and decode it from Base64.
    """
    headers = {"Authorization": f"token {GITHUB_API_TOKEN}"}
    url = f"{GITHUB_API_ENDPOINT}/repos/{owner}/{repo_name}/contents/README.md"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        readme_data = response.json()
        encoded_content = readme_data.get("content", "No content available")
        if encoded_content != "No content available":
            # Decode Base64 content to plain text
            decoded_content = base64.b64decode(encoded_content).decode("utf-8")
            return decoded_content
        else:
            return "README.md is empty or not available."
    elif response.status_code == 404:
        return "README.md not found"
    else:
        print(f"Error fetching README.md: {response.status_code} - {response.text}")
        return "Error fetching README.md"

def extract_github_links(text):
    """
    Extract GitHub repository links from a given text.
    """
    pattern = r"https:\/\/github\.com\/[a-zA-Z0-9\-_]+\/[a-zA-Z0-9\-_]+"
    return re.findall(pattern, text)

def fetch_repo_details_from_url(repo_url):
    """
    Fetch repository details using a GitHub URL.
    """
    parts = repo_url.split("/")
    if len(parts) >= 5:
        owner = parts[3]
        repo_name = parts[4]
        return fetch_repo_details(owner, repo_name)
    else:
        return {"error": "Invalid repository URL"}

if __name__ == "__main__":
    # Input
    github_username = input("Enter the candidate's GitHub username: ")
    best_repo_name = input("Enter the name of the repository to evaluate: ")

    # Step 1: Validate Repository Ownership
    repos = fetch_user_repos(github_username)
    repo_names = [repo["name"] for repo in repos]
    
    if best_repo_name not in repo_names:
        print(f"Error: Repository '{best_repo_name}' does not belong to user '{github_username}'.")
    else:
        print(f"Repository '{best_repo_name}' belongs to user '{github_username}'.")

        # Step 2: Fetch Repository Details
        repo_details = fetch_repo_details(github_username, best_repo_name)
        print("\n--- Repository Details ---")
        print(f"Name: {repo_details.get('name')}")
        print(f"Description: {repo_details.get('description', 'No description provided')}")
        print(f"Languages: {repo_details.get('language', 'Not specified')}")
        print(f"Size (KB): {repo_details.get('size', 'Unknown')}")

        # Step 3: Validate Commit History
        commits = fetch_repo_commits(github_username, best_repo_name, github_username)
        print(f"\nTotal commits by '{github_username}': {len(commits)}")
        if len(commits) == 0:
            print(f"Warning: No significant contributions detected by '{github_username}'.")

        # Step 4: Fetch README Content and Extract Links
        readme_content = fetch_readme(github_username, best_repo_name)
        print(f"\n--- README Content (First 200 characters) ---\n{readme_content[:200]}...\n")

        # Step 5: Extract and Process Linked Repositories
        description = repo_details.get("description", "") or ""  # Ensure description is a string
        description_links = extract_github_links(description)
        readme_links = extract_github_links(readme_content or "")  # Ensure README content is a string
        all_links = set(description_links + readme_links)

        print(f"\n--- Linked Repositories Found: {len(all_links)} ---")
        for link in all_links:
            print(f"\nProcessing linked repository: {link}")
            linked_repo_details = fetch_repo_details_from_url(link)
            if "error" not in linked_repo_details:
                print(f"Linked Repo: {linked_repo_details.get('name')}")
                print(f"Description: {linked_repo_details.get('description', 'No description provided')}")
                print(f"Size: {linked_repo_details.get('size', 'Unknown')} KB")
            else:
                print(f"Error processing linked repository: {linked_repo_details['error']}")
