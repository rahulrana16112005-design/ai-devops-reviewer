import os
from utils import get_changed_code
from github import post_pr_comment


# 🔥 Ignore scanner files (VERY IMPORTANT)
def ignore_scanner_files(diff):
    result = []
    skip = False

    for line in diff.split("\n"):
        if line.startswith("diff --git"):
            file_name = line.split(" b/")[-1]

            if file_name.startswith("app/") or file_name.startswith(".github/"):
                skip = True
            else:
                skip = False

        if not skip:
            result.append(line)

    return "\n".join(result)


# 🔍 Keep only added lines
def keep_added_lines(diff):
    lines = []
    for line in diff.split("\n"):
        if line.startswith("+") and not line.startswith("+++"):
            lines.append(line[1:])
    return "\n".join(lines)


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


# 🔎 Analyzer
def analyze_files(files):
    issues = []
    warnings = []
    suggestions = []

    for file, lines in files.items():
        for line_no, code in lines:
            code_lower = code.lower()

            # 🔴 CRITICAL
            if "0.0.0.0/0" in code:
                issues.append((file, line_no, code,
                               "Open to internet",
                               "Restrict CIDR range"))

            if "public-read" in code or "public-read-write" in code:
                issues.append((file, line_no, code,
                               "Public access enabled",
                               "Disable public access"))

            if "password=" in code_lower or "admin123" in code_lower:
                issues.append((file, line_no, code,
                               "Hardcoded credentials",
                               "Use secrets manager"))

            if "privileged: true" in code_lower:
                issues.append((file, line_no, code,
                               "Privileged container",
                               "Disable privileged mode"))

            # 🐳 Docker
            if file.lower().endswith("dockerfile"):
                if "latest" in code_lower:
                    issues.append((file, line_no, code,
                                   "Using latest image",
                                   "Pin version"))

            # ☸️ Kubernetes
            if file.endswith(".yaml") or file.endswith(".yml"):
                if "password" in code_lower:
                    issues.append((file, line_no, code,
                                   "Secret in YAML",
                                   "Use Kubernetes secrets"))

            # 🌍 Terraform
            if file.endswith(".tf"):
                if "public-read" in code:
                    issues.append((file, line_no, code,
                                   "Public S3 bucket",
                                   "Disable public access"))

            # 🟠 WARNINGS
            if "latest" in code_lower:
                warnings.append((file, line_no, code,
                                 "Using latest tag",
                                 "Pin version"))

            if "versioning" in code_lower and "false" in code_lower:
                warnings.append((file, line_no, code,
                                 "Versioning disabled",
                                 "Enable versioning"))

            # 🟢 SUGGESTIONS
            if "aws_instance" in code_lower:
                suggestions.append((file, line_no,
                                    "Use IAM roles",
                                    "Avoid static credentials"))

    return issues, warnings, suggestions


# 📊 Score
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
                text += f"❌ {problem}\n"
                text += f"💡 {solution}\n"
                text += f"🔍 `{code.strip()}`\n"

            elif len(item) == 4:
                file, line, problem, solution = item
                text += f"\n📄 {file} | Line {line}\n"
                text += f"💡 {problem}\n"
                text += f"👉 {solution}\n"

        return text + "\n"

    return f"""
## 🤖 AI DevOps Review

### 📊 Score: {score}/10

{format_items('## 🔴 Critical Issues', issues)}

{format_items('## 🟠 Warnings', warnings)}

{format_items('## 🟢 Suggestions', suggestions)}
""".strip()


# 🚀 MAIN
if __name__ == "__main__":
    print("🚀 Running AI Reviewer...")

    full_diff = get_changed_code()

    # 💀 FIX 1: Ignore scanner files
    full_diff = ignore_scanner_files(full_diff)

    # 💀 FIX 2: Keep only new lines
    filtered_diff = keep_added_lines(full_diff)

    if not filtered_diff.strip():
        review = "✅ No relevant DevOps changes found."
    else:
        files = parse_diff(full_diff)
        issues, warnings, suggestions = analyze_files(files)
        review = format_review(issues, warnings, suggestions)

    print("\n=== 🤖 REVIEW ===")
    print(review)

    post_pr_comment(review)
