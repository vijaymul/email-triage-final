---
title: Email Triage OpenEnv
emoji: 📨
colorFrom: blue
colorTo: purple
sdk: docker
pinned: false
app_file: app.py
---

# OpenEnv Hackathon R1: Email Triage & Inbox Management

A real-world automated inbox triage simulator. Built for the OpenEnv API evaluation spec using strict Pydantic models.

## Tasks
1. **Easy (Spam Deletion)**: Identifies classic scam emails ("$1M Prize!") and routes them using the `delete` action or moving them to the `trash` folder.
2. **Medium (Sorting)**: Sorts incoming Invoices into `invoices` and Meeting Requests into `meetings`. Assesses both success criteria securely using a 0.5/1.0 grading gradient.
3. **Hard (Scheduling)**: Automates dynamic calendar slots. Given an arbitrary scheduling request email, the agent correctly reads the `calendar_slots` Observation context, allocates an available meeting slot, books it, and archives the root email out of the inbox. 

## Structure
- `models.py`: Rigid Pydantic state specs (Observation, Action, Reward, State).
- `environment.py`: Simulated Email Engine and deterministic task grading pipeline. 
- `main.py`: The FastAPI server enabling the validator to strictly poke `POST /reset`, `POST /step`, and `GET /state`.
- `inference.py`: Baseline native script successfully evaluating R1 configurations securely utilizing structured outputs formats.
- `requirements.txt`: Standard environment bindings ensuring FastAPI evaluation parameters function effectively out of the box.

## How to Run Locally 

### 1. Docker Build & Run (Judgement Protocol Strategy)
```bash
docker build -t email-triage-env .
docker run -p 7860:7860 email-triage-env
```
The FastAPI instance will natively boot to `http://0.0.0.0:7860` waiting for the simulator pings.

### 2. Evaluator Diagnostic Testing (Testing inference logic natively)
Activate a virtual environment and map dependencies securely out of `requirements.txt`, then run the evaluation script natively via shell execution:
```bash
export GEMINI_API_KEY="AIza..."
python inference.py
```
*(Optionally you can map to an alternate test baseline by setting your `OPENAI_API_KEY` respectively and configuring `model_to_use` manually inside `inference.py`)*
