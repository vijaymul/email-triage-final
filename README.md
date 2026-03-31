---
title: Email Triage OpenEnv
emoji: 📨
colorFrom: blue
colorTo: purple
sdk: docker
pinned: false
---

# Email Triage OpenEnv

A real-world automated inbox triage simulator. Built for the OpenEnv API evaluation spec using strict Pydantic models.

## Structure
- `server/models.py`: Rigid Pydantic state specs (Observation, Action, Reward, State).
- `server/environment.py`: Simulated Email Engine and deterministic task grading pipeline. 
- `server/app.py`: The FastAPI server enabling the validator to strictly poke `POST /reset`, `POST /step`, and `GET /state`.

## How to Run Locally 

### 1. Docker Build & Run
```bash
docker build -t email-triage-env .
docker run -p 7860:7860 email-triage-env
```
The FastAPI instance will boot to `http://0.0.0.0:7860`.

### 2. Manual Installation
```bash
pip install .
uvicorn server.app:app --host 0.0.0.0 --port 7860
```
