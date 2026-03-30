from fastapi import FastAPI, Request
from pydantic import BaseModel
from typing import List, Optional
import os
import sys

# Ensure server package logic is accessible
# We keep the core logic so the environment actually works!
from .models import Action, Observation, Reward, EnvironmentState
from .environment import EmailEnv

app = FastAPI()
env = EmailEnv(task_level="hard")

class StepResponse(BaseModel):
    observation: Observation
    reward: Reward

@app.get("/")
async def root():
    return {"status": "ok", "message": "Email Triage OpenEnv is running."}

@app.post("/reset")
@app.post("/reset/")
async def reset(request: Request):
    """
    Handle environment resets. 
    We accept the task_level from query params if provided, else default to easy.
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
    Step the environment using the provided action.
    """
    obs, reward = env.step(action)
    return {"observation": obs, "reward": reward}

@app.get("/state")
@app.get("/state/")
async def get_state():
    return env.state()
