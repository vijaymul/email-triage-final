---
title: Email Triage OpenEnv
emoji: 📧
colorFrom: blue
colorTo: indigo
sdk: docker
app_port: 7860
pinned: false
---

# OpenEnv Hackathon: Email Triage
Automated inbox management simulator for the OpenEnv R1 challenge.

## Environment Details
- **Domain**: Email Triage / Inbox Management
- **Tasks**: `easy` (Spam Filter), `medium` (Invoice Routing), `hard` (Meeting Scheduler)
- **Scoring**: 0.0 to 1.0 based on correct categorization, routing choices, deletion flags, and calendar bookings.
- **Spec**: See `openenv.yaml`.

## Structure
- `models.py`: Pydantic definitions for Inbox `Observation`, and `Action`.
- `grader.py`: Evaluation criteria and point scoring logic.
- `tasks.py`: Raw email scenarios for the 3 tasks.
- `app.py`: FastAPI implementation of the OpenEnv API.
- `inference.py`: Baseline script using the OpenAI client to solve the environment.

## Setup & Running

### Local Execution (PowerShell)
From the `c:\Users\abhijeett\Desktop\openevm project` directory:

**Step 1: Start the Env Server**
Open a PowerShell terminal and run:
```powershell
pip install -r requirements.txt
python -m uvicorn app:app --port 7860
```

**Step 2: In a separate PowerShell tab, run Inference**
```powershell
$env:API_BASE_URL="https://api.openai.com/v1"
$env:MODEL_NAME="gpt-4o"
$env:HF_TOKEN="your-api-key"
python inference.py
```

## Deployment to HF Spaces
1. Clone your space locally.
2. Push all the files into the root of the space domain.
3. The Space will automatically build the `Dockerfile` and expose the API on port 7860.
