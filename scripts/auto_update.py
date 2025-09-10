import os
import openai
from git import Repo
import uuid
import requests

# Config
repo_dir = os.getcwd()
main_branch = "main"
openai.api_key = os.getenv("OPENAI_API_KEY")

# Get issue info
issue_title = os.getenv("ISSUE_TITLE")
issue_body = os.getenv("ISSUE_BODY")

# Checkout repo
repo = Repo(repo_dir)
repo.git.checkout(main_branch)

# Example: update main.py (adjust for your repo)
target_file = "main.py"
with open(target_file, "r") as f:
    code = f.read()

# Create prompt for OpenAI
prompt = f"""
Issue: {issue_title}\nDescription: {issue_body}\n
Here is the existing Python code:\n{code}\n
Update the code to fix the issue.
"""

response = openai.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": prompt}],
    temperature=0
)

# Access the content correctly
updated_code = response.choices[0].message.content



# Create new branch
branch_name = f"issue-{uuid.uuid4().hex[:8]}"
repo.git.checkout('-b', branch_name)

# Write updated code
with open(target_file, "w") as f:
    f.write(updated_code)

# Commit and push
repo.git.add(target_file)
repo.git.commit("-m", f"Update code for issue: {issue_title}")
repo.git.push("origin", branch_name)

# Create Pull Request
GITHUB_TOKEN = os.getenv("GH_PAT")
repo_owner, repo_name = os.getenv("GITHUB_REPOSITORY").split("/")

url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/pulls"
headers = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json"
}
data = {
    "title": f"Fix: {issue_title}",
    "head": branch_name,
    "base": main_branch,
    "body": f"Auto-generated update for issue: {issue_body}"
}

r = requests.post(url, headers=headers, json=data)
if r.status_code == 201:
    print(f"Pull request created for branch {branch_name}")
else:
    print(f"Failed to create PR: {r.status_code} {r.text}")
