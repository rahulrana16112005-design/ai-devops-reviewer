import os
import subprocess

def get_changed_code():
    try:
        base_branch = os.getenv("GITHUB_BASE_REF", "main")

        result = subprocess.run(
            ["git", "diff", f"origin/{base_branch}...HEAD"],
            capture_output=True,
            text=True
        )

        diff = result.stdout

        # ✅ Fallback for local testing
        if not diff.strip():
            if os.path.exists("test.tf"):
                with open("test.tf", "r") as f:
                    return f.read()

        return diff

    except Exception as e:
        return f"Error fetching diff: {str(e)}"


def filter_devops_files(diff):
    # ✅ Return full diff if relevant file exists
    allowed_keywords = [".tf", ".yml", ".yaml", "Dockerfile"]

    if any(keyword in diff for keyword in allowed_keywords):
        return diff

    return ""
