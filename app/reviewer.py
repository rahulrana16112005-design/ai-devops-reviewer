import os
from utils import get_changed_code, filter_devops_files
from github import post_pr_comment


# 🔍 Parse diff into file + line mapping
def parse_diff(diff):
    files = {}
    current_file = None
    line_number = 0

    for line in diff.split("\n"):
        if line.startswith("diff --git"):
            current_file = line.split(" b/")[-1]
            files[current_file] = []
            line_number = 0

        elif line.startswith("@@"):
            try:
                line_number = int(line.split("+")[1].split(",")[0])
            except:
                line_number = 0

        elif line.startswith("+") and not line.startswith("+++"):
            files[current_file].append((line_number, line[1:]))
            line_number += 1

    return files


# 🔎 Advanced analyzer (file-aware 💀)
def analyze_files(files):
    issues = []
    warnings = []
    suggestions = []

    for file, lines in files.items():
        for line_no, code in lines:
            code_lower = code.lower()

            # =========================
            # 🔴 CRITICAL ISSUES
            # =========================

            if "0.0.0.0/0" in code:
                issues.append((file, line_no, code,
                               "Open access to entire internet",
                               "Restrict CIDR range (e.g., 192.168.x.x/24)"))

            if "public-read" in code or "public-read-write" in code:
                issues.append((file, line_no, code,
                               "Public access enabled",
                               "Disable public access and enforce private ACL"))

            if "password=" in code or "admin123" in code:
                issues.append((file, line_no, code,
                               "Hardcoded credentials detected",
                               "Use environment variables or secrets manager"))

            if "privileged: true" in code:
                issues.append((file, line_no, code,
                               "Privileged container",
                               "Remove privileged mode"))

            # =========================
            # 🐳 DOCKERFILE RULES
            # =========================
            if file.lower().endswith("dockerfile"):
                if "latest" in code:
                    issues.append((file, line_no, code,
                                   "Using latest Docker image",
                                   "Pin to specific version (e.g., nginx:1.25)"))

                if "env password" in code_lower:
                    issues.append((file, line_no, code,
                                   "Hardcoded ENV secret",
                                   "Use runtime secrets"))

            # =========================
            # ☸️ KUBERNETES YAML RULES
            # =========================
            if file.endswith(".yaml") or file.endswith(".yml"):
                if "privileged: true" in code:
                    issues.append((file, line_no, code,
                                   "Privileged container",
                                   "Disable privileged mode"))

                if "containerport" in code_lower:
                    warnings.append((file, line_no, code,
                                     "Exposed container port",
                                     "Restrict access using services/network policies"))

                if "password" in code_lower:
                    issues.append((file, line_no, code,
                                   "Hardcoded secret in YAML",
                                   "Use Kubernetes secrets"))

            # =========================
            # 🌍 TERRAFORM RULES
            # =========================
            if file.endswith(".tf"):
                if "0.0.0.0/0" in code:
                    issues.append((file, line_no, code,
                                   "Open security group",
                                   "Restrict CIDR range"))

                if "public-read" in code:
                    issues.append((file, line_no, code,
                                   "Public S3 bucket",
                                   "Disable public access"))

            # =========================
            # 🟠 WARNINGS (GENERIC)
            # =========================
            if "latest" in code:
                warnings.append((file, line_no, code,
                                 "Using latest tag",
                                 "Pin to a specific version"))

            if "versioning" in code and "false" in code:
                warnings.append((file, line_no, code,
                                 "Versioning disabled",
                                 "Enable versioning"))

            if 'cpu: "0"' in code:
                warnings.append((file, line_no, code,
                                 "Invalid CPU config",
                                 "Use valid CPU request (e.g., 100m)"))

            if "print(" in code:
                warnings.append((file, line_no, code,
                                 "Debug print statement",
                                 "Remove before production"))

            # =========================
            # 🟢 SUGGESTIONS
            # =========================
            if "aws_instance" in code:
                suggestions.append((file, line_no,
                                    "Use IAM roles",
                                    "Avoid static credentials"))

            if "dockerfile" in file.lower():
                suggestions.append((file, line_no,
                                    "Use minimal base image",
                                    "Reduce image size & attack surface"))

    return issues, warnings, suggestions


# 📊 Score system
def calculate_score(issues, warnings):
    score = 10
    score -= len(issues) * 2
    score -= len(warnings)
    return max(score, 1)


# 🧠 Format output
def format_review(issues, warnings, suggestions):
    score = calculate_score(issues, warnings)

    def format_items(title, items):
        if not items:
            return f"{title}\n- None\n"

        text = f"{title}\n"
        for item in items:
            if len(item) == 5:
                file, line, code, problem, solution = item
                text += f"\n📄 {file} | Line {line}\n"
                text += f"❌ Issue: {problem}\n"
                text += f"💡 Fix: {solution}\n"
                text += f"🔍 Code: `{code.strip()}`\n"

            elif len(item) == 4:
                file, line, problem, solution = item
                text += f"\n📄 {file} | Line {line}\n"
                text += f"💡 Suggestion: {problem}\n"
                text += f"👉 {solution}\n"

        return text + "\n"

    return f"""
## 🤖 AI DevOps Advanced Review

### 📊 Security Score: {score}/10

{format_items('## 🔴 Critical Issues', issues)}

{format_items('## 🟠 Warnings', warnings)}

{format_items('## 🟢 Suggestions', suggestions)}
""".strip()


# 🚀 Main
def review_code(diff):
    if not diff.strip():
        return "⚠️ No changes detected."

    files = parse_diff(diff)
    issues, warnings, suggestions = analyze_files(files)

    return format_review(issues, warnings, suggestions)


if __name__ == "__main__":
    print("🚀 Running PRO AI Reviewer...")

    full_diff = get_changed_code()
    filtered_code = filter_devops_files(full_diff)

    review = review_code(filtered_code)

    print("\n=== 🤖 REVIEW ===")
    print(review)

    post_pr_comment(review)
