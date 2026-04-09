import os
from utils import get_changed_code
from github import post_pr_comment, post_inline_comment, add_labels


# 🔥 Ignore scanner files
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


# 🔍 Parse diff
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


# 🔎 Analyzer (NO DUPLICATES 💀)
def analyze_files(files):
    issues = []
    warnings = []
    suggestions = []

    seen = set()

    def add_unique(container, item):
        key = (item[0], item[1], item[3])
        if key not in seen:
            seen.add(key)
            container.append(item)

    for file, lines in files.items():
        for line_no, code in lines:
            code_lower = code.lower()

            # 🔴 CRITICAL
            if "0.0.0.0/0" in code:
                add_unique(issues, (file, line_no, code,
                                    "Open to internet",
                                    "Restrict CIDR range"))

            if "public-read" in code or "public-read-write" in code:
                add_unique(issues, (file, line_no, code,
                                    "Public access enabled",
                                    "Disable public access"))

            if "password=" in code_lower or "admin123" in code_lower:
                add_unique(issues, (file, line_no, code,
                                    "Hardcoded credentials",
                                    "Use secrets manager"))

            if "privileged: true" in code_lower:
                add_unique(issues, (file, line_no, code,
                                    "Privileged container",
                                    "Disable privileged mode"))

            # 🐳 Docker
            if file.lower().endswith("dockerfile"):
                if "latest" in code_lower:
                    add_unique(issues, (file, line_no, code,
                                        "Using latest image",
                                        "Pin version"))

            # ☸️ Kubernetes
            if file.endswith(".yaml") or file.endswith(".yml"):
                if "password" in code_lower:
                    add_unique(issues, (file, line_no, code,
                                        "Secret in YAML",
                                        "Use Kubernetes secrets"))

            # 🌍 Terraform
            if file.endswith(".tf"):
                if "public-read" in code:
                    add_unique(issues, (file, line_no, code,
                                        "Public S3 bucket",
                                        "Disable public access"))

            # 🟠 WARNINGS
            if "latest" in code_lower:
                add_unique(warnings, (file, line_no, code,
                                     "Using latest tag",
                                     "Pin version"))

            if "versioning" in code_lower and "false" in code_lower:
                add_unique(warnings, (file, line_no, code,
                                     "Versioning disabled",
                                     "Enable versioning"))

            # 🟢 SUGGESTIONS
            if "aws_instance" in code_lower:
                add_unique(suggestions, (file, line_no,
                                        "Use IAM roles",
                                        "Avoid static credentials"))

    return issues, warnings, suggestions


# 📊 Score
def calculate_score(issues, warnings):
    score = 10
    score -= len(issues) * 2
    score -= len(warnings)
    return max(score, 1)


# 📊 File-wise summary
def file_summary(issues):
    summary = {}
    for item in issues:
        file = item[0]
        summary[file] = summary.get(file, 0) + 1

    text = "## 📁 File-wise Issues\n"
    for f, count in summary.items():
        text += f"- {f}: {count} issues\n"

    return text


# 🧠 Format review
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

        return text + "\n"

    return f"""
## 🤖 AI DevOps Review

### 📊 Score: {score}/10

{file_summary(issues)}

{format_items('## 🔴 Critical Issues', issues)}

{format_items('## 🟠 Warnings', warnings)}

{format_items('## 🟢 Suggestions', suggestions)}
""".strip()


# 🚀 MAIN
if __name__ == "__main__":
    print("🚀 Running AI Reviewer...")

    full_diff = get_changed_code()
    full_diff = ignore_scanner_files(full_diff)

    files = parse_diff(full_diff)

    if not files:
        review = "✅ No relevant DevOps changes found."
    else:
        issues, warnings, suggestions = analyze_files(files)
        review = format_review(issues, warnings, suggestions)

        # 💀 INLINE COMMENTS
        for file, line, code, problem, solution in issues:
            post_inline_comment(file, line, f"❌ {problem}\n💡 {solution}")

        # 🏷️ LABELS
        labels = []
        if issues:
            labels.append("security-risk")
        if warnings:
            labels.append("needs-fix")

        add_labels(labels)

    print("\n=== 🤖 REVIEW ===")
    print(review)

    post_pr_comment(review)
