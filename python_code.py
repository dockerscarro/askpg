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
        issue_body = f.read().replace("\r", "")

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    # Only target app.py (you can add more files to this list if needed)
    target_files = ["app.py"]
    code_files = {}

    for filepath in target_files:
        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                code_files[filepath] = f.read()

    # Prepare prompt
    prompt = f"""
Issue Title: {issue_title}
Issue Body: {issue_body}

Here is the current code file(s):
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
            {"role": "user", "content": prompt},
        ],
    )

    # Handle response correctly (new SDK returns structured objects)
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

        print(f"✅ Updated file: {filepath}")

if __name__ == "__main__":
    main()
