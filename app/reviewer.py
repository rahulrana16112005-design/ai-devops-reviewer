import os
from utils import get_changed_code
from github import post_pr_comment, post_inline_comment, add_labels

USE_LOCAL_FILES = False


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

    for file, lines in files.items():
        for line_no, code in lines:
            code_lower = code.lower()

            if "0.0.0.0/0" in code:
                issues.append((file, line_no, code, "Open to internet", "Restrict CIDR range"))

            if "public-read" in code or "public-read-write" in code:
                issues.append((file, line_no, code, "Public access enabled", "Disable public access"))

            if "password=" in code_lower or "admin123" in code_lower:
                issues.append((file, line_no, code, "Hardcoded credentials", "Use secrets manager"))

            if "privileged: true" in code_lower:
                issues.append((file, line_no, code, "Privileged container", "Disable privileged mode"))

            if file.lower().endswith("dockerfile") and "latest" in code_lower:
                issues.append((file, line_no, code, "Using latest image", "Pin version"))

            if (file.endswith(".yaml") or file.endswith(".yml")) and "password" in code_lower:
                issues.append((file, line_no, code, "Secret in YAML", "Use Kubernetes secrets"))

            if file.endswith(".tf") and "public-read" in code:
                issues.append((file, line_no, code, "Public S3 bucket", "Disable public access"))

            if "latest" in code_lower:
                warnings.append((file, line_no, code, "Using latest tag", "Pin version"))

            if "versioning" in code_lower and "false" in code_lower:
                warnings.append((file, line_no, code, "Versioning disabled", "Enable versioning"))

            if "aws_instance" in code_lower:
                suggestions.append((file, line_no, "Use IAM roles", "Avoid static credentials"))

    return issues, warnings, suggestions


def calculate_score(issues, warnings):
    score = 10
    score -= len(issues) * 2
    score -= len(warnings)
    return max(score, 1)


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
            else:
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


if __name__ == "__main__":
    if USE_LOCAL_FILES:
        files = {}
        base_path = "PR-Scanner"

        if os.path.exists(base_path):
            for root, _, filenames in os.walk(base_path):
                for file in filenames:
                    path = os.path.join(root, file)
                    try:
                        with open(path, "r", errors="ignore") as f:
                            content = f.readlines()
                        files[path] = [(i + 1, line.strip()) for i, line in enumerate(content)]
                    except:
                        pass

        if not files:
            review = "No files found in PR-Scanner folder."
        else:
            issues, warnings, suggestions = analyze_files(files)
            review = format_review(issues, warnings, suggestions)

    else:
        full_diff = get_changed_code()
        full_diff = keep_only_target_folder(full_diff)
        full_diff = ignore_scanner_files(full_diff)

        if not full_diff.strip():
            review = "No relevant DevOps changes found."
        else:
            files = parse_diff(full_diff)
            issues, warnings, suggestions = analyze_files(files)
            review = format_review(issues, warnings, suggestions)

    print(review)
    post_pr_comment(review)

    if issues:
        add_labels(["security-risk", "needs-fix"])
