from fastapi import FastAPI, Request
from pydantic import BaseModel

app = FastAPI()

# Add a Root GET for Hugging Face Health Check
@app.get("/")
async def root():
    return {"status": "ok", "message": "Email Triage OpenEnv is running."}

# The Validator sends a POST to /reset with a JSON body
@app.post("/reset")
@app.post("/reset/")  # Double-check with trailing slash
async def reset(request: Request):
    # This ensures the POST request doesn't return 405 Method Not Allowed
    return {
        "inbox": [
            {"id": "1", "sender": "HR", "subject": "Interview", "body": "Schedule it.", "date": "2026-03-29"}
        ],
        "available_folders": ["Inbox", "Spam"],
        "calendar_slots": ["10:00 AM", "02:00 PM"]
    }

@app.post("/step")
@app.post("/step/")
async def step(action: dict):
    return {"reward": 1.0, "done": True, "info": "Step successful"}