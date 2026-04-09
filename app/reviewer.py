import os
from utils import get_changed_code, filter_devops_files
from github import post_pr_comment


# 🔍 Universal analyzer
def analyze_code(code):
    issues = []
    warnings = []
    suggestions = []

    code_lower = code.lower()

    # =========================
    # 🔴 CRITICAL SECURITY ISSUES
    # =========================

    if "0.0.0.0/0" in code:
        issues.append("Open access detected (0.0.0.0/0) - security risk")

    if "public-read" in code or "public-read-write" in code:
        issues.append("Public access enabled on resource")

    if "password=" in code or "secret" in code_lower or "api_key" in code_lower:
        issues.append("Hardcoded secret or credential detected")

    if "privileged: true" in code:
        issues.append("Container running in privileged mode")

    if "latest" in code and "image" in code_lower:
        warnings.append("Using latest tag for container image")

    # =========================
    # 🟠 CONFIG / DEVOPS WARNINGS
    # =========================

    if "versioning" in code and "false" in code:
        warnings.append("Versioning is disabled")

    if "cpu" in code and '"0"' in code:
        warnings.append("Invalid CPU allocation detected")

    if "ami" in code and "123" in code:
        warnings.append("Hardcoded AMI might be invalid")

    # =========================
    # 🟡 GENERAL CODE ISSUES
    # =========================

    if "print(" in code:
        warnings.append("Debug print statements found")

    if "todo" in code_lower:
        warnings.append("TODO comments present in code")

    if "except:" in code:
        warnings.append("Generic exception handling used")

    # =========================
    # 🟢 BEST PRACTICE SUGGESTIONS
    # =========================

    if "aws_instance" in code:
        suggestions.append("Use IAM roles instead of static credentials")

    if "dockerfile" in code_lower:
        suggestions.append("Use minimal base image and fixed versions")

    if "env" in code_lower:
        suggestions.append("Avoid exposing sensitive data via environment variables")

    if not suggestions:
        suggestions.append("Follow security and least privilege principles")

    return issues, warnings, suggestions


# 📊 Score system
def calculate_score(issues, warnings):
    score = 10
    score -= len(issues) * 2
    score -= len(warnings) * 1
    return max(score, 1)


# 🧠 Format output
def format_review(issues, warnings, suggestions):
    score = calculate_score(issues, warnings)

    def format_section(title, items):
        if not items:
            return f"{title}\n- None"
        return f"{title}\n" + "\n".join([f"- {item}" for item in items])

    review = f"""
## 🤖 AI DevOps + Code Review

### 📊 Overall Score: {score}/10

{format_section('## 🔴 Critical Issues', issues)}

{format_section('## 🟠 Warnings', warnings)}

{format_section('## 🟢 Suggestions', suggestions)}
"""

    return review.strip()


# 🔁 Main review function
def review_code(code):
    if not code.strip():
        return "⚠️ No relevant changes found."

    issues, warnings, suggestions = analyze_code(code)
    return format_review(issues, warnings, suggestions)


# 🚀 Entry point
if __name__ == "__main__":
    print("🚀 Running Advanced AI Reviewer...")

    full_diff = get_changed_code()

    print("\n=== 🔍 RAW DIFF ===")
    print(full_diff if full_diff.strip() else "❌ No diff found")

    filtered_code = filter_devops_files(full_diff)

    print("\n=== ⚙️ FILTERED CODE ===")
    print(filtered_code if filtered_code.strip() else "❌ No relevant changes")

    review = review_code(filtered_code)

    print("\n=== 🤖 REVIEW OUTPUT ===")
    print(review)

    # ✅ Post comment
    post_pr_comment(review)
