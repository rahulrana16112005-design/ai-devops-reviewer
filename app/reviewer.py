import os
from utils import get_changed_code
from github import post_pr_comment, post_inline_comment, add_labels

def keep_only_target_folder(diff):
    result = []
    skip = False

    for line in diff.split("\n"):
        if line.startswith("diff --git"):
            file_name = line.split(" b/")[-1]
            skip = not file_name.startswith("PR-Scanner/")

        if not skip:
            result.append(line)

    return "\n".join(result)


def ignore_scanner_files(diff):
    result = []
    skip = False

    for line in diff.split("\n"):
        if line.startswith("diff --git"):
            file_name = line.split(" b/")[-1]
            skip = file_name.startswith("app/") or file_name.startswith(".github/")

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

            if "public-read" in code or "public-read-write" in code:
                add_unique(issues, (file, line_no, code, "Public access enabled", "Disable public access"))

            if "password=" in code_lower or "admin123" in code_lower:
                add_unique(issues, (file, line_no, code, "Hardcoded credentials", "Use secrets manager"))

            if "privileged: true" in code_lower:
                add_unique(issues, (file, line_no, code, "Privileged container", "Disable privileged mode"))

            if file.lower().endswith("dockerfile") and "latest" in code_lower:
                add_unique(issues, (file, line_no, code, "Using latest image", "Pin version"))

            if (file.endswith(".yaml") or file.endswith(".yml")) and "password" in code_lower:
                add_unique(issues, (file, line_no, code, "Secret in YAML", "Use Kubernetes secrets"))

            if file.endswith(".tf") and "public-read" in code:
                add_unique(issues, (file, line_no, code, "Public S3 bucket", "Disable public access"))

            if "latest" in code_lower:
                warnings.append((file, line_no, code, "Using latest tag", "Pin version"))

            if "versioning" in code_lower and "false" in code_lower:
                warnings.append((file, line_no, code, "Versioning disabled", "Enable versioning"))

            if "aws_instance" in code_lower:
                suggestions.append((file, line_no, "Use IAM roles", "Avoid static credentials"))

    return issues, warnings, suggestions


if __name__ == "__main__":
    full_diff = get_changed_code()
    full_diff = keep_only_target_folder(full_diff)
    full_diff = ignore_scanner_files(full_diff)

    files = parse_diff(full_diff)

    issues, warnings, suggestions = analyze_files(files)

    if not issues and not warnings and not suggestions:
        review = "No relevant DevOps changes found."
    else:
        review = "## 🤖 AI DevOps Review\n"

    for file, line, code, problem, solution in issues:
        try:
            post_inline_comment(file, line, f"❌ {problem}\n💡 {solution}")
        except:
            pass

    print(review)
    post_pr_comment(review)

    labels = []
    if issues:
        labels.append("security-risk")
    if warnings:
        labels.append("needs-fix")

    if labels:
        add_labels(labels)
