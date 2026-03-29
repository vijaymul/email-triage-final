# app.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
import uvicorn

from models import Observation, Action, State
from tasks import TASKS
from grader import grade

app = FastAPI(title="Email Triage OpenEnv")

@app.get("/")
def read_root():
    return {"status": "ok", "message": "Email Triage OpenEnv is running."}

# In-memory state
current_state = State()

class ResetRequest(BaseModel):
    task_level: str = "easy"

class StepResponse(BaseModel):
    observation: Observation
    reward: float
    done: bool
    info: Dict[str, Any]

@app.post("/reset", response_model=Observation)
def reset_env(req: ResetRequest):
    if req.task_level not in TASKS:
        raise HTTPException(status_code=400, detail="Invalid task level.")
    
    global current_state
    current_state = State(task_level=req.task_level, score=0.0, is_done=False)
    
    task_data = TASKS[req.task_level]
    return Observation(
        inbox=task_data["inbox"],
        available_folders=task_data["available_folders"],
        calendar_slots=task_data.get("calendar_slots")
    )

@app.post("/step", response_model=StepResponse)
def step_env(action: Action):
    global current_state
    
    if current_state.is_done:
        raise HTTPException(status_code=400, detail="Environment is done. Please reset.")
        
    task_level = current_state.task_level
    task_data = TASKS[task_level]
    expected = task_data["expected"]
    
    # Calculate score
    reward = grade(task_level, action, expected)
    current_state.score = reward
    current_state.is_done = True
    
    # Next observation
    obs = Observation(
        inbox=task_data["inbox"],
        available_folders=task_data["available_folders"],
        calendar_slots=task_data.get("calendar_slots")
    )
    
    return StepResponse(
        observation=obs,
        reward=reward,
        done=True,
        info={"expected": expected, "notes": "Task complete"}
    )

@app.get("/state", response_model=State)
def get_state():
    return current_state

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=7860)
