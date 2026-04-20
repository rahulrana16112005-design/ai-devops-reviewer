import os
import requests


# 🔹 Common headers
def get_headers():
    token = os.getenv("GITHUB_TOKEN")
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json"
    }


# 🟢 1. PR SUMMARY COMMENT
def post_pr_comment(comment):
    repo = os.getenv("GITHUB_REPOSITORY")
    pr_number = os.getenv("PR_NUMBER")

    if not pr_number:
        print("❌ PR number not found")
        return

    url = f"https://api.github.com/repos/{repo}/issues/{pr_number}/comments"

    data = {
        "body": f"## 🤖 AI DevOps Review\n\n{comment}"
    }

    response = requests.post(url, headers=get_headers(), json=data)

    if response.status_code == 201:
        print("✅ PR summary comment posted")
    else:
        print(f"❌ Failed to post PR comment: {response.status_code}")
        print(response.text)


# 🔴 2. INLINE COMMENT (REAL MAGIC 💀)
def post_inline_comment(file_path, line_number, body):
    repo = os.getenv("GITHUB_REPOSITORY")
    pr_number = os.getenv("PR_NUMBER")

    # Get PR details to fetch HEAD SHA
    pr_url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}"
    pr_response = requests.get(pr_url, headers=get_headers())

    if pr_response.status_code != 200:
        print("❌ Failed to fetch PR details")
        return

    pr_data = pr_response.json()
    commit_id = pr_data["head"]["sha"]

    url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}/comments"

    data = {
        "body": body,
        "commit_id": commit_id,
        "path": file_path,
        "line": line_number,
        "side": "RIGHT"
    }

    response = requests.post(url, headers=get_headers(), json=data)

    if response.status_code == 201:
        print(f"💀 Inline comment added → {file_path}:{line_number}")
    else:
        print(f"❌ Failed inline comment → {file_path}:{line_number}")
        print(response.text)


# 🏷️ 3. ADD LABELS
def add_labels(labels):
    repo = os.getenv("GITHUB_REPOSITORY")
    pr_number = os.getenv("PR_NUMBER")

    url = f"https://api.github.com/repos/{repo}/issues/{pr_number}/labels"

    data = {
        "labels": labels
    }

    response = requests.post(url, headers=get_headers(), json=data)

    if response.status_code in [200, 201]:
        print(f"🏷️ Labels added: {labels}")
    else:
        print("❌ Failed to add labels")
        print(response.text)
