import base64
import requests
import os
import time

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO = "rahulrana16112005-design/ai-devops-reviewer"

headers = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}


# 🔹 Upload file to scan-target branch
def upload_file_to_github(filename, content):
    filename = f"{int(time.time())}_{filename}"

    encoded = base64.b64encode(content).decode()

    url = f"https://api.github.com/repos/{REPO}/contents/PR-Scanner/{filename}"

    data = {
        "message": "User uploaded file",
        "content": encoded,
        "branch": "scan-target"
    }

    res = requests.put(url, headers=headers, json=data)

    if res.status_code not in [200, 201]:
        return {"error": "Upload failed", "details": res.json()}

    return res.json()


# 🔹 Check if PR already exists
def get_open_pr():
    url = f"https://api.github.com/repos/{REPO}/pulls?state=open"
    res = requests.get(url, headers=headers)

    if res.status_code != 200:
        return None

    prs = res.json()

    for pr in prs:
        if pr["head"]["ref"] == "scan-target":
            return pr

    return None


# 🔹 Create or reuse PR
def create_pr():
    existing_pr = get_open_pr()

    if existing_pr:
        print("Using existing PR")
        return existing_pr

    url = f"https://api.github.com/repos/{REPO}/pulls"

    data = {
        "title": "User Upload Review",
        "head": "scan-target",
        "base": "main",
        "body": "Auto PR from UI"
    }

    res = requests.post(url, headers=headers, json=data)

    if res.status_code not in [200, 201]:
        return {"error": "PR creation failed", "details": res.json()}

    return res.json()


# 🔥 FINAL: GET REAL GITHUB REVIEW (LINE COMMENTS)
def get_pr_comments(pr_number):
    url = f"https://api.github.com/repos/{REPO}/pulls/{pr_number}/comments"
    res = requests.get(url, headers=headers)

    if res.status_code != 200:
        return []

    return res.json()
