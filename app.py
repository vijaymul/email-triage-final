from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import os
import sys

# Ensure server package logic is accessible
from .models import Action, Observation, Reward, EnvironmentState
from .environment import EmailEnv

app = FastAPI()
# Initialize global environment instance
env = EmailEnv(task_level="hard")

class StepResponse(BaseModel):
    observation: Observation
    reward: Reward

@app.get("/")
async def root():
    return {"status": "ok", "message": "Email Triage OpenEnv is running."}

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/reset")
@app.post("/reset/")
async def reset(request: Request):
    """
    Handle environment resets. 
    Accepts task_level from query params, defaulting to easy.
    """
    params = request.query_params
    task_level = params.get("task_level", "easy")
    env.task_level = task_level.lower()
    obs = env.reset()
    return obs

@app.post("/step")
@app.post("/step/")
async def step(action: Action):
    """
    Step the environment using the provided agent action.
    """
    try:
        obs, reward = env.step(action)
        return {"observation": obs, "reward": reward}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/state")
@app.get("/state/")
async def get_state():
    """
    Returns the full internal state (for grading/debug).
    """
    return env.state()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)
