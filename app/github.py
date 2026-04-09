import os
import requests

def post_pr_comment(comment):
    repo = os.getenv("GITHUB_REPOSITORY")
    token = os.getenv("GITHUB_TOKEN")
    pr_number = os.getenv("PR_NUMBER")

    if not pr_number:
        print("❌ PR number not found")
        return

    if not all([repo, token]):
        print("❌ Missing GitHub environment variables")
        return

    url = f"https://api.github.com/repos/{repo}/issues/{pr_number}/comments"

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json"
    }

    data = {
        "body": f"""## 🤖 AI DevOps Review

{comment}
"""
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 201:
        print("✅ Comment posted successfully")
    else:
        print(f"❌ Failed to post comment: {response.status_code}")
        print(response.text)
