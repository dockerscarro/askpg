import os
import openai
from git import Repo
import uuid
import requests
import re

# ----------------- CONFIG -----------------
repo_dir = os.getcwd()
main_branch = "main"
target_file = "main.py"  # Your Python file
openai.api_key = os.getenv("OPENAI_API_KEY")
GH_PAT = os.getenv("GH_PAT")
repo_owner, repo_name = os.getenv("GITHUB_REPOSITORY").split("/")
issue_title = os.getenv("ISSUE_TITLE")
issue_body = os.getenv("ISSUE_BODY")

# ----------------- GIT SETUP -----------------
repo = Repo(repo_dir)
repo.git.config("user.name", "github-actions[bot]")
repo.git.config("user.email", "github-actions[bot]@users.noreply.github.com")
repo.git.checkout(main_branch)

# ----------------- READ EXISTING CODE -----------------
with open(target_file, "r") as f:
    code = f.read()

# ----------------- CREATE OPENAI PROMPT -----------------
prompt = f"""
Issue: {issue_title}
Description: {issue_body}

Here is the full existing Python code from {target_file}:
{code}

Please return the entire updated Python file with all changes applied.
Do NOT include Markdown, explanations, or placeholders like '# ... rest of the code ...'.
Every line from the original file must be included, even if unchanged.
"""

# ----------------- CALL OPENAI -----------------
response = openai.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": prompt}],
    temperature=0,
    max_tokens=5000  # increase if file is large
)

updated_code = response.choices[0].message.content

# ----------------- CLEAN OUTPUT -----------------
# Remove ``` or ```python blocks
clean_code = re.sub(r"```(?:python)?\n?", "", updated_code)
clean_code = re.sub(r"```", "", clean_code)
clean_code = clean_code.strip()

# ----------------- CREATE NEW BRANCH -----------------
branch_name = f"issue-{uuid.uuid4().hex[:8]}"
repo.git.checkout("-b", branch_name)

# ----------------- WRITE UPDATED CODE -----------------
with open(target_file, "w") as f:
    f.write(clean_code)

# ----------------- COMMIT & PUSH -----------------
repo.git.add(target_file)
repo.git.commit("-m", f"Update code for issue: {issue_title}")
repo.git.push("origin", branch_name)

# ----------------- CREATE PULL REQUEST -----------------
pr_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/pulls"
headers = {
    "Authorization": f"token {GH_PAT}",
    "Accept": "application/vnd.github+json"
}
pr_data = {
    "title": f"Fix: {issue_title}",
    "head": branch_name,
    "base": main_branch,
    "body": f"Auto-generated update for issue:\n\n{issue_body}"
}

r = requests.post(pr_url, headers=headers, json=pr_data)
if r.status_code == 201:
    print(f"✅ Pull request created: {r.json()['html_url']}")
else:
    print(f"❌ Failed to create PR: {r.status_code} {r.text}")
