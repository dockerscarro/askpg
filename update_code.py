import sys
import os
from openai import OpenAI

def main():
    if len(sys.argv) < 3:
        print("Usage: python update_code.py <issue_title> <issue_body_file>")
        sys.exit(1)

    issue_title = sys.argv[1]
    issue_body_file = sys.argv[2]

    with open(issue_body_file, "r", encoding="utf-8") as f:
        issue_body = f.read().replace('\r','')

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    # Collect current .py files (skip .github folder)
    # Only include store.py, ignore all others
     # Collect current .py files (skip .github folder)
    code_files = {}
    for root, _, files in os.walk("."):
        if ".github" in root:
            continue
        for file in files:
            if file.endswith(".py"):
                path = os.path.join(root, file)
                with open(path, "r", encoding="utf-8") as f:
                    code_files[path] = f.read()


    # Prepare prompt with all .py files
    prompt = f"""
Issue Title: {issue_title}
Issue Body: {issue_body}

Here are the current code files:
"""
    for path, content in code_files.items():
        prompt += f"\n===== {path} =====\n{content}\n"

    prompt += """
Please update only the files that are affected by this issue.
Return results strictly in this format for each updated file:

FILE: <filepath>
<updated file content>

Do not include explanations. Only return the updated files.
"""

    # Call OpenAI
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are an expert Python developer."},
            {"role": "user", "content": prompt}
        ]
    )

    updated_code = response.choices[0].message.content.strip()

    # Parse and write updated files
    for block in updated_code.split("FILE: "):
        if not block.strip():
            continue
        header, *body = block.split("\n", 1)
        filepath = header.strip()
        if not filepath or not body:
            continue
        new_content = body[0].rstrip() + "\n"

        # Ensure directory exists
        dirpath = os.path.dirname(filepath)
        if dirpath:
            os.makedirs(dirpath, exist_ok=True)

        # Write updated file
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(new_content)

        print(f"Updated file: {filepath}")

if __name__ == "__main__":
    main()

