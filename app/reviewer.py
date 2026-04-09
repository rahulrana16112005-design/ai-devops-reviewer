import os
from utils import get_changed_code, filter_devops_files
from github import post_pr_comment


def analyze_devops_code(code):
    issues = []
    warnings = []
    suggestions = []

    code_lower = code.lower()

    # 🔴 Critical Issues
    if "0.0.0.0/0" in code:
        issues.append("Security group खुला है (0.0.0.0/0) → anyone can access")

    if "public-read-write" in code or "public-read" in code:
        issues.append("S3 bucket public access enabled")

    if "password=" in code or "admin123" in code:
        issues.append("Hardcoded secret detected")

    if "privileged: true" in code:
        issues.append("Container running in privileged mode")

    # 🟠 Warnings
    if "latest" in code:
        warnings.append("Using latest tag → not stable for production")

    if "versioning" in code and "false" in code:
        warnings.append("S3 versioning disabled")

    if "cpu: \"0\"" in code:
        warnings.append("Invalid CPU request configuration")

    # 🟢 Suggestions
    if "aws_instance" in code:
        suggestions.append("Use IAM roles instead of hardcoded credentials")

    if "dockerfile" in code_lower:
        suggestions.append("Use slim base image and pin versions")

    if not suggestions:
        suggestions.append("Follow least privilege principle and secure configs")

    return issues, warnings, suggestions


def format_review(issues, warnings, suggestions):
    def format_section(title, items):
        if not items:
            return f"{title}\n- None"
        return f"{title}\n" + "\n".join([f"- {item}" for item in items])

    review = f"""
## 🤖 AI DevOps Review

{format_section('## 🔴 Critical Issues', issues)}

{format_section('## 🟠 Warnings', warnings)}

{format_section('## 🟢 Suggestions', suggestions)}
"""
    return review.strip()


def review_code(code):
    if not code.strip():
        return "⚠️ No relevant DevOps changes found in this PR."

    issues, warnings, suggestions = analyze_devops_code(code)

    return format_review(issues, warnings, suggestions)


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
