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

INSERT BELOW FUNCTION <function_name>:
<new code>

INSERT ABOVE LINE <exact_line_text>:
<new code>

REMOVE:
<code to remove>

Only include the changes. No explanations, no markdown, no extra text.
"""

# ----------------- CALL OPENAI -----------------
response = openai.chat.completions.create(
    model="gpt-5",
    messages=[{"role": "user", "content": prompt}],
    temperature=0
)

patch_text = response.choices[0].message.content.strip()

# ----------------- APPLY PATCH LOCALLY -----------------
def apply_patch(original_code: str, patch: str) -> str:
    new_code = original_code
    lines = patch.splitlines()
    i = 0

    while i < len(lines):
        line = lines[i].strip()

        # ----------------- REPLACE -----------------
        if line.startswith("REPLACE:"):
            old_block, new_block = [], []
            i += 1
            while i < len(lines) and not lines[i].startswith("WITH:"):
                old_block.append(lines[i])
                i += 1
            i += 1
            while i < len(lines) and not any(lines[i].startswith(x) for x in ["REPLACE:", "INSERT", "REMOVE"]):
                new_block.append(lines[i])
                i += 1
            old_code = "\n".join(old_block).strip()
            new_code_block = "\n".join(new_block).strip()
            new_code = new_code.replace(old_code, new_code_block)

        # ----------------- INSERT BELOW FUNCTION -----------------
        elif line.startswith("INSERT BELOW FUNCTION"):
            func_name = re.search(r"INSERT BELOW FUNCTION (\w+):", line).group(1)
            block = []
            i += 1
            while i < len(lines) and not lines[i].startswith(("REPLACE:", "INSERT", "REMOVE")):
                block.append(lines[i])
                i += 1
            insert_text = "\n".join(block).strip()
            # find function definition anchor
            pattern = rf"(def {func_name}\(.*\):)"
            match = re.search(pattern, new_code)
            if match:
                insert_point = match.end()
                new_code = new_code[:insert_point] + "\n    " + insert_text.replace("\n", "\n    ") + new_code[insert_point:]
            else:
                # fallback: append at end
                new_code += "\n" + insert_text

        # ----------------- INSERT ABOVE LINE -----------------
        elif line.startswith("INSERT ABOVE LINE"):
            exact_line = re.search(r"INSERT ABOVE LINE (.+):", line).group(1)
            block = []
            i += 1
            while i < len(lines) and not lines[i].startswith(("REPLACE:", "INSERT", "REMOVE")):
                block.append(lines[i])
                i += 1
            insert_text = "\n".join(block).strip()
            # find exact line
            pattern = re.escape(exact_line)
            match = re.search(pattern, new_code)
            if match:
                insert_point = match.start()
                new_code = new_code[:insert_point] + insert_text + "\n" + new_code[insert_point:]
            else:
                # fallback: append at end
                new_code += "\n" + insert_text

        # ----------------- REMOVE -----------------
        elif line.startswith("REMOVE:"):
            block = []
            i += 1
            while i < len(lines) and not lines[i].startswith(("REPLACE:", "INSERT", "REMOVE")):
                block.append(lines[i])
                i += 1
            remove_text = "\n".join(block).strip()
            new_code = new_code.replace(remove_text, "")

        else:
            i += 1

    return new_code


# ----------------- APPLY PATCH -----------------
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
