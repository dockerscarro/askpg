import os, re, uuid, requests
from git import Repo
import openai

# ---------------- CONFIG ----------------
repo_dir = os.getcwd()
main_branch = "main"
target_file = "main.py"
openai.api_key = os.getenv("OPENAI_API_KEY")
GH_PAT = os.getenv("GH_PAT")
repo_owner, repo_name = os.getenv("GITHUB_REPOSITORY").split("/")
issue_title = os.getenv("ISSUE_TITLE")
issue_body = os.getenv("ISSUE_BODY")

# ---------------- GIT ----------------
repo = Repo(repo_dir)
repo.git.config("user.name", "github-actions[bot]")
repo.git.config("user.email", "github-actions[bot]@users.noreply.github.com")
repo.git.checkout(main_branch)

# ---------------- READ CODE ----------------
with open(target_file, "r") as f:
    code = f.read()

# ---------------- PROMPT ----------------
prompt = f"""
You are a code refactoring assistant.

Issue: {issue_title}
Description: {issue_body}

Current file main.py:
{code}

⚠️ Return only patch instructions in this format:

REPLACE:
<old code>
WITH:
<new code>

INSERT ABOVE FUNCTION function_name:
<new code>

INSERT BELOW FUNCTION function_name:
<new code>

INSERT ABOVE LINE exact_line_text:
<new code>

REMOVE:
<code to remove>
"""

# ---------------- CALL OPENAI ----------------
response = openai.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": prompt}],
    temperature=0
)
patch_text = response.choices[0].message.content.strip()

# ---------------- APPLY PATCH ----------------
def find_function_block(lines, name):
    start, end = None, None
    pattern = re.compile(rf"^\s*def\s+{re.escape(name)}\s*\(")
    for i, l in enumerate(lines):
        if start is None and pattern.match(l):
            start = i
        elif start is not None and l.startswith("def ") and i > start:
            end = i
            break
    if start is not None and end is None:
        end = len(lines)
    return start, end

def apply_patch(code, patch):
    new_code = code
    lines = patch.splitlines()
    i = 0
    while i < len(lines):
        l = lines[i].strip()
        if l.startswith("REPLACE:"):
            old, new = [], []
            i += 1
            while i < len(lines) and not lines[i].startswith("WITH:"):
                old.append(lines[i]); i+=1
            i += 1
            while i < len(lines) and not any(lines[i].startswith(x) for x in ["REPLACE:","INSERT","REMOVE"]):
                new.append(lines[i]); i+=1
            new_code = new_code.replace("\n".join(old).strip(), "\n".join(new).strip())
        elif l.startswith("REMOVE:"):
            block=[]
            i+=1
            while i < len(lines) and not lines[i].startswith(("REPLACE:","INSERT","REMOVE")):
                block.append(lines[i]); i+=1
            new_code = new_code.replace("\n".join(block).strip(),"")
        elif l.startswith("INSERT ABOVE FUNCTION"):
            func = l.split("INSERT ABOVE FUNCTION")[1].strip(" :")
            block=[]; i+=1
            while i < len(lines) and not lines[i].startswith(("REPLACE:","INSERT","REMOVE")):
                block.append(lines[i]); i+=1
            ins="\n".join(block)
            clines=new_code.splitlines()
            start,_=find_function_block(clines,func)
            if start is not None: clines=clines[:start]+[ins]+clines[start:]
            else: clines.append(ins)
            new_code="\n".join(clines)
        elif l.startswith("INSERT BELOW FUNCTION"):
            func = l.split("INSERT BELOW FUNCTION")[1].strip(" :")
            block=[]; i+=1
            while i < len(lines) and not lines[i].startswith(("REPLACE:","INSERT","REMOVE")):
                block.append(lines[i]); i+=1
            ins="\n".join(block)
            clines=new_code.splitlines()
            start,end= find_function_block(clines,func)
            if start is not None:
                clines=clines[:end]+[ins]+clines[end:]
            else: clines.append(ins)
            new_code="\n".join(clines)
        elif l.startswith("INSERT ABOVE LINE"):
            exact = l.split("INSERT ABOVE LINE")[1].strip(" :")
            block=[]; i+=1
            while i < len(lines) and not lines[i].startswith(("REPLACE:","INSERT","REMOVE")):
                block.append(lines[i]); i+=1
            ins="\n".join(block)
            idx=new_code.find(exact)
            if idx>=0: new_code=new_code[:idx]+ins+"\n"+new_code[idx:]
            else: new_code+="\n"+ins
        else: i+=1
    return new_code

merged_code = apply_patch(code, patch_text)

# ---------------- COMMIT ----------------
branch_name = f"issue-{uuid.uuid4().hex[:8]}"
repo.git.checkout("-b", branch_name)
with open(target_file,"w") as f: f.write(merged_code)
repo.git.add(target_file)
repo.git.commit("-m", f"Update code for issue: {issue_title}")
repo.git.push("origin", branch_name)

# ---------------- CREATE PR ----------------
pr_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/pulls"
headers = {"Authorization":f"token {GH_PAT}","Accept":"application/vnd.github+json"}
pr_data={"title":f"Fix: {issue_title}","head":branch_name,"base":main_branch,"body":f"Auto-generated update:\n\n{issue_body}\n\nPatch:\n\n{patch_text}"}
r=requests.post(pr_url,headers=headers,json=pr_data)
if r.status_code==201: print(f"✅ PR created: {r.json()['html_url']}")
else: print(f"❌ Failed to create PR: {r.status_code} {r.text}")
