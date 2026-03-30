import os
import sys
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict, Any

# Ensure root directory is in sys.path so we can import modules from there
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if root_dir not in sys.path:
    sys.path.append(root_dir)

from models import Observation, Action, Reward, EnvironmentState
from environment import EmailEnv

app = FastAPI(title="Email Triage OpenEnv Interface")

# Instantiate a global instance of our environment.
env = EmailEnv(task_level="hard")

class StepResponse(BaseModel):
    observation: Observation
    reward: Reward

@app.get("/")
async def root():
    return {
        "status": "online", 
        "message": "OpenEnv Hackathon Email Triage Simulator. Visit http://127.0.0.1:7860/docs for the API Swagger interface!"
    }

@app.post("/reset", response_model=Observation)
async def reset_env(task_level: str = "easy"):
    """
    Reset the environment observation explicitly.
    Supports a custom difficulty string matching Hackathon Matrix IDs.
    """
    env.task_level = task_level.lower()
    return env.reset()

@app.post("/step", response_model=StepResponse)
async def step_env(action: Action):
    """
    Accepts Pydantic wrapped action unions strictly enforced natively via FastAPI route specs.
    Steps the environment and returns the subsequent observation state + exact grader score.
    """
    obs, reward = env.step(action)
    return StepResponse(observation=obs, reward=reward)

@app.get("/state", response_model=EnvironmentState)
async def get_state():
    """
    Dumps the internal proxy ground truth validation state required by standard automated testing schemas.
    """
    return env.state()

def main():
    import uvicorn
    # Import root modules via the server package if possible,
    # but since we already appended root to sys.path, simple import works.
    uvicorn.run("server.app:app", host="0.0.0.0", port=7860, reload=False)

if __name__ == "__main__":
    main()
