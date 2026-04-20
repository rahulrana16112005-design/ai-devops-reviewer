from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import time

from api.github_api import upload_file_to_github, create_pr, get_pr_comments

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def home():
    return {"message": "AI DevOps Reviewer Running 🚀"}


# 🔥 FINAL INTELLIGENT CLEANER (SMART ENGINE)
def clean_review(comments):
    issues_map = {}

    for c in comments:
        body = c.get("body", "").strip()

        if not body or "❌" not in body:
            continue

        lines = [l.strip() for l in body.split("\n") if l.strip()]

        title = ""
        why = ""
        fix = ""

        for i, line in enumerate(lines):

            if line.startswith("❌"):
                title = line.strip()

            if "🧠" in line and i + 1 < len(lines):
                why = lines[i + 1].strip()

            if "🛠" in line and i + 1 < len(lines):
                fix = lines[i + 1].strip()

        if not title:
            continue

        # 🔥 GROUP SIMILAR ISSUES INTO ONE CATEGORY
        normalized = title.lower()

        if "hardcoded" in normalized or "password" in normalized:
            group = "credentials"
        elif "public" in normalized:
            group = "public_access"
        elif "0.0.0.0" in normalized or "internet" in normalized:
            group = "network"
        elif "latest" in normalized:
            group = "docker"
        else:
            group = normalized

        # 🔥 detect if this is specific
        is_specific = any(sym in title for sym in ["=", "/", ".", ":", "0.0.0.0"])

        if group not in issues_map:
            issues_map[group] = {
                "title": title,
                "why": why,
                "fix": fix,
                "specific": is_specific
            }
        else:
            existing = issues_map[group]

            # 💀 KEEP BEST VERSION
            if is_specific or (why and fix and not existing["why"]):
                issues_map[group] = {
                    "title": title,
                    "why": why,
                    "fix": fix,
                    "specific": is_specific
                }

    # 🔥 FINAL OUTPUT
    output = []

    for issue in issues_map.values():
        block = (
            "━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"{issue['title']}\n\n"

            f"📖 Meaning:\n"
            f"{issue['why'] if issue['why'] else 'This is a serious DevOps issue affecting system reliability or security.'}\n\n"

            f"🛠 Fix:\n"
            f"{issue['fix'] if issue['fix'] else 'Follow DevOps best practices to resolve this issue.'}\n\n"

            f"🚀 Benefit:\n"
            f"Improves performance, security, and maintainability.\n\n"

            f"⚠️ Risk if not fixed:\n"
            f"May lead to vulnerabilities, downtime, or data leaks.\n"
        )

        output.append(block)

    if not output:
        return "✅ No issues found"

    return "\n\n".join(output)


@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    content = await file.read()

    # 1️⃣ Upload file
    upload_file_to_github(file.filename, content)

    # 2️⃣ Create / reuse PR
    pr = create_pr()
    pr_number = pr.get("number")

    if not pr_number:
        return {"error": "PR not created", "details": pr}

    # 3️⃣ Wait for GitHub Action
    time.sleep(20)

    # 4️⃣ Fetch PR comments
    comments = get_pr_comments(pr_number)

    # 5️⃣ Clean & format
    final_review = clean_review(comments)

    return {
        "pr_number": pr_number,
        "pr_url": pr.get("html_url"),
        "review": final_review
    }
