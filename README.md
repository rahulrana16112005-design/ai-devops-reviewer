# AI DevOps Reviewer 🚀

AI-powered DevOps PR reviewer that automatically analyzes infrastructure/code files, detects issues, and provides actionable feedback — reducing manual debugging effort.

---

## About the Project

This project solves a real DevOps problem:

Debugging infrastructure (Terraform, CI/CD, cloud configs) is slow, repetitive, and error-prone.

This tool automates that process.

Instead of manual debugging:
- Upload a file
- AI analyzes it
- Get instant feedback

---

## Problem Statement

Developers face:

- Hidden security issues
- Hard-to-detect misconfigurations
- Time-consuming manual debugging
- Need for deep cloud knowledge

---

## Solution

AI DevOps Reviewer provides:

- Automated PR workflow
- AI-powered code analysis
- Instant feedback
- Centralized results

---

## Workflow

User uploads file  
→ Backend pushes to GitHub  
→ Pull Request created  
→ GitHub Actions triggered  
→ AI analyzes code  
→ Comments generated  
→ Output returned  

---

## Example

Terraform input:


resource "aws_s3_bucket" "test" {
bucket = "my-bucket"
}


AI detects:
- Missing encryption
- Public access risk

Returns:
- Issue explanation
- Fix suggestions
- Risk impact

---

## Features

- File upload API
- GitHub PR automation
- GitHub Actions integration
- AI code review
- Security detection
- Clean output
- Cloud deployment

---

## Tech Stack

- Backend: FastAPI (Python)
- Deployment: Render
- GitHub API
- GitHub Actions
- OpenAI API

---

## Project Structure


ai-devops-reviewer/
│
├── api/
│ ├── main.py
│ ├── github_api.py
│
├── app/
├── frontend/
├── .github/workflows/
├── requirements.txt
├── README.md
└── test.tf


---

## Branch Strategy

### main
Stable production code

### scan-target
Temporary branch for uploaded files

---

## API

### GET /
Check service status

Response:

{
"message": "AI DevOps Reviewer Running"
}


---

### POST /upload

Upload file for analysis

Response:

{
"pr_number": 2,
"pr_url": "...",
"review": "AI generated feedback"
}


---

## Deployment

Live:
https://ai-devops-reviewer.onrender.com

Docs:
https://ai-devops-reviewer.onrender.com/docs

---

## Debugging Learnings

- Dependency issues → fixed via requirements.txt
- GitHub auth errors → corrected tokens
- PR delay → temporary sleep used
- Local vs production mismatch → env consistency

---

## Key Learnings

- DevOps = automation
- Debugging is the real bottleneck
- AI reduces manual effort
- Integration matters more than tools

---

## Future Improvements

- Async processing (remove sleep)
- Logging & monitoring
- Rate limiting
- Better UI
- Structured AI output

---

## Author

Rahul Rana  
DevOps & Cloud Enthusiast

---

## Final Note

This project reflects real-world problem solving using DevOps + AI.
