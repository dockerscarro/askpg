import os
from git import Repo
import uuid
import requests
import re
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage

# ----------------- CONFIG -----------------
repo_dir = os.getcwd()
main_branch = "main"
target_file = "main.py"  # Your Python file

# Read API keys from environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
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
generate_prompt = f"""
You are an expert Python developer.

Current {target_file} code:
{code}

Issue to solve:
Title: {issue_title}
Description: {issue_body}

Update the ENTIRE code file to fix the issue.
Return ONLY the full Python script (no markdown, no explanations).
Ensure the final code is valid and executable.
"""

# ----------------- CALL OPENAI -----------------
chat_model = ChatOpenAI(
    temperature=0,
    model="gpt-4o-mini",
    openai_api_key=OPENAI_API_KEY,
    max_tokens=1500
)

try:
    response = chat_model.invoke([HumanMessage(content=generate_prompt)])
    updated_code = response.content.strip()
except Exception as e:
    print(f"❌ GPT failed to generate updated code: {e}")
    exit(1)

# ----------------- STRIP MARKDOWN/EXTRA TEXT -----------------
code_blocks = re.findall(r"```(?:python)?\s*(.*?)```", updated_code, flags=re.S)
if code_blocks:
    clean_code = code_blocks[0].strip()
else:
    clean_code = updated_code.strip()

# Fallback: if the new code is suspiciously short, keep original
if len(clean_code.splitlines()) < len(code.splitlines()) // 2:
    print("⚠️ Warning: Model returned partial code, keeping original.")
    clean_code = code

# ----------------- CREATE NEW BRANCH -----------------
branch_name = f"issue-{uuid.uuid4().hex[:8]}"
repo.git.checkout("-b", branch_name)

# ----------------- WRITE CLEAN CODE -----------------
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
