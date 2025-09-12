import os
import re
import uuid
import requests
from git import Repo
import openai

# ----------------- CONFIG -----------------
repo_dir = os.getcwd()
main_branch = "main"
target_file = "main.py"
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
You are a code refactoring assistant.

Issue: {issue_title}
Description: {issue_body}

Here is the current file **main.py**:
{code}

⚠️ IMPORTANT:
- Do NOT return the entire file.
- Instead, return patch instructions in this format:

REPLACE:
<old code>
WITH:
<new code>

INSERT ABOVE FUNCTION function_name:
<new code to insert>

INSERT BELOW FUNCTION function_name:
<new code to insert>

REMOVE:
<code to remove>

Only include the changes. No explanations, no markdown, no extra text.
"""

# ----------------- CALL OPENAI -----------------
response = openai.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": prompt}],
    temperature=0
)

patch_text = response.choices[0].message.content.strip()

# ----------------- APPLY PATCH LOCALLY -----------------
def find_function_block(code_lines, function_name):
    start_idx, end_idx = None, None
    pattern = re.compile(rf"^\s*def\s+{re.escape(function_name)}\s*\(")
    for i, line in enumerate(code_lines):
        if start_idx is None and pattern.match(line):
            start_idx = i
        elif start_idx is not None and line.startswith("def ") and i > start_idx:
            end_idx = i
            break
    if start_idx is not None and end_idx is None:
        end_idx = len(code_lines)
    return start_idx, end_idx

def apply_patch(original_code: str, patch: str) -> str:
    new_code = original_code
    lines = patch.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i].strip()

        if line.startswith("REPLACE:"):
            old_block, new_block = [], []
            i += 1
            while i < len(lines) and not lines[i].startswith("WITH:"):
                old_block.append(lines[i])
                i += 1
            i += 1
            while i < len(lines) and not any(
                lines[i].startswith(x) for x in ["REPLACE:", "INSERT", "REMOVE"]
            ):
                new_block.append(lines[i])
                i += 1
            old_code = "\n".join(old_block).strip()
            new_code_block = "\n".join(new_block).strip()
            new_code = new_code.replace(old_code, new_code_block)

        elif line.startswith("REMOVE:"):
            block = []
            i += 1
            while i < len(lines) and not lines[i].startswith(("REPLACE:", "INSERT", "REMOVE")):
                block.append(lines[i])
                i += 1
            remove_text = "\n".join(block).strip()
            new_code = new_code.replace(remove_text, "")

        elif line.startswith("INSERT ABOVE FUNCTION"):
            func_name = line.split("INSERT ABOVE FUNCTION")[1].strip(" :")
            block = []
            i += 1
            while i < len(lines) and not lines[i].startswith(("REPLACE:", "INSERT", "REMOVE")):
                block.append(lines[i])
                i += 1
            insert_text = "\n".join(block)
            code_lines = new_code.splitlines()
            start_idx, _ = find_function_block(code_lines, func_name)
            if start_idx is not None:
                code_lines = code_lines[:start_idx] + [insert_text] + code_lines[start_idx:]
            else:
                code_lines.append(insert_text)
            new_code = "\n".join(code_lines)

        elif line.startswith("INSERT BELOW FUNCTION"):
            func_name = line.split("INSERT BELOW FUNCTION")[1].strip(" :")
            block = []
            i += 1
            while i < len(lines) and not lines[i].startswith(("REPLACE:", "INSERT", "REMOVE")):
                block.append(lines[i])
                i += 1
            insert_text = "\n".join(block)
            code_lines = new_code.splitlines()
            start_idx, end_idx = find_function_block(code_lines, func_name)
            if start_idx is not None:
                code_lines = code_lines[:end_idx] + [insert_text] + code_lines[end_idx:]
            else:
                code_lines.append(insert_text)
            new_code = "\n".join(code_lines)

        else:
            i += 1

    return new_code

merged_code = apply_patch(code, patch_text)

# ----------------- CREATE NEW BRANCH -----------------
branch_name = f"issue-{uuid.uuid4().hex[:8]}"
repo.git.checkout("-b", branch_name)

# ----------------- WRITE MERGED CODE -----------------
with open(target_file, "w") as f:
    f.write(merged_code)

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
    "body": f"Auto-generated update for issue:\n\n{issue_body}\n\nPatch applied:\n\n{patch_text}"
}

r = requests.post(pr_url, headers=headers, json=pr_data)
if r.status_code == 201:
    print(f"✅ Pull request created: {r.json()['html_url']}")
else:
    print(f"❌ Failed to create PR: {r.status_code} {r.text}")
