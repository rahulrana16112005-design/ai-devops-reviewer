import os
from utils import get_changed_code
from github import post_pr_comment, post_inline_comment, add_labels


def keep_only_target_folder(diff):
    result = []
    skip = False

    for line in diff.split("\n"):
        if line.startswith("diff --git"):
            file_name = line.split(" b/")[-1]

            if file_name.startswith("PR-Scanner/"):
                skip = False
            else:
                skip = True

        if not skip:
            result.append(line)

    return "\n".join(result)


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

            if "0.0.0.0/0" in code:
                add_unique(issues, (file, line_no, code, "Open to internet", "Restrict CIDR range"))

            if "public-read" in code:
                add_unique(issues, (file, line_no, code, "Public access enabled", "Disable public access"))

            if "password=" in code_lower:
                add_unique(issues, (file, line_no, code, "Hardcoded credentials", "Use secrets manager"))

            if "latest" in code_lower:
                add_unique(warnings, (file, line_no, code, "Using latest tag", "Pin version"))

            if "aws_instance" in code_lower:
                add_unique(suggestions, (file, line_no, "Use IAM roles", "Avoid static credentials"))

    return issues, warnings, suggestions


def calculate_score(issues, warnings):
    score = 10 - (len(issues) * 2) - len(warnings)
    return max(score, 1)


def file_summary(issues):
    summary = {}
    for item in issues:
        file = item[0]
        summary[file] = summary.get(file, 0) + 1

    text = "## 📁 File-wise Issues\n"
    for f, count in summary.items():
        text += f"- {f}: {count} issues\n"

    return text


def format_review(issues, warnings, suggestions):
    score = calculate_score(issues, warnings)

    return f"""
## 🤖 AI DevOps Review

### 📊 Score: {score}/10

{file_summary(issues)}

🔴 Critical Issues: {len(issues)}
🟠 Warnings: {len(warnings)}
🟢 Suggestions: {len(suggestions)}
""".strip()


if __name__ == "__main__":
    print("🚀 Running AI Reviewer...")

    full_diff = get_changed_code()
    full_diff = keep_only_target_folder(full_diff)

    files = parse_diff(full_diff)

    if not files or all(len(v) == 0 for v in files.values()):
        review = "✅ No relevant DevOps changes found."
    else:
        issues, warnings, suggestions = analyze_files(files)
        review = format_review(issues, warnings, suggestions)

        for file, line, code, problem, solution in issues[:10]:
            try:
                post_inline_comment(file, line, f"❌ {problem}\n💡 {solution}")
            except:
                pass

        labels = []
        if issues:
            labels.append("security-risk")
        if warnings:
            labels.append("needs-fix")

        if labels:
            add_labels(labels)

    print("\n=== REVIEW ===")
    print(review)

    post_pr_comment(review)
