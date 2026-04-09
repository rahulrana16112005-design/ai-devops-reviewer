import os
from openai import OpenAI
from utils import get_changed_code, filter_devops_files
from github import post_pr_comment

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def review_code(code):
    if not code.strip():
        return "⚠️ No relevant DevOps changes found in this PR."

    prompt = f"""
You are a senior DevOps engineer.

Analyze the code and respond strictly in this format:

## 🔴 Critical Issues
- ...

## 🟠 Warnings
- ...

## 🟢 Suggestions
- ...

Focus on:
Terraform, Kubernetes YAML, Docker, CI/CD

Code:
{code[:8000]}
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": "You are an expert DevOps reviewer."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"❌ Error during AI review: {str(e)}"


if __name__ == "__main__":
    print("🚀 Running AI DevOps Reviewer...")

    full_diff = get_changed_code()

    print("\n=== 🔍 RAW DIFF ===")
    print(full_diff if full_diff.strip() else "❌ No diff found")

    filtered_code = filter_devops_files(full_diff)

    print("\n=== ⚙️ FILTERED CODE ===")
    print(filtered_code if filtered_code.strip() else "❌ No DevOps changes")

    review = review_code(filtered_code)

    print("\n=== 🤖 AI REVIEW ===")
    print(review)

    # ✅ Post to GitHub PR
    post_pr_comment(review)
