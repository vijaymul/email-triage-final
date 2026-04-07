import os
import sys
import json
from openai import OpenAI
from pydantic import BaseModel, ValidationError
from server.models import Action, DoNothingAction, ActionType
from server.environment import EmailEnv

# Ensure stdout is line-buffered for immediate visibility in evaluation logs
if sys.version_info >= (3, 7):
    sys.stdout.reconfigure(line_buffering=True)

class AgentOutput(BaseModel):
    action: Action

def run_inference():
    # Read configuration from environment with standard defaults
    task_level = os.environ.get("TASK_LEVEL", "hard").lower()
    max_steps = int(os.environ.get("MAX_STEPS", "10"))
    model_name = os.environ.get("MODEL_NAME")
    hf_token = os.environ.get("HF_TOKEN")
    
    # 1. IMMEDIATE PRINT OF START BLOCK
    print(f"[START] task={task_level}", flush=True)
    
    env = EmailEnv(task_level=task_level)
    obs = env.reset()
    
    total_score = 0.0
    current_step = 0
    
    try:
        # 1. Initialize OpenAI client with the mandatory SST Proxy credentials
        # Use API_BASE_URL and API_KEY strictly as provided by the platform.
        client = OpenAI(
            base_url=os.environ.get("API_BASE_URL"),
            api_key=os.environ.get("API_KEY")
        )

        for step in range(max_steps):
            current_step = step + 1
            
            # Serialize observation for the agent
            obs_json = obs.model_dump_json(indent=2)
            
            system_prompt = (
                "You are an AI Email Assistant managing a user's inbox.\n"
                f"Difficulty: {task_level}\n\n"
                "Directives:\n"
                "- easy: Move Spam to trash.\n"
                "- medium: Sort Invoices to 'invoices', Meeting Requests to 'meetings'.\n"
                "- hard: Schedule a meeting using a valid calendar slot.\n"
                "Output ONLY valid JSON matching the required schema."
            )
            
            try:
                response = client.chat.completions.create(
                    model=model_name,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": f"Observations:\n{obs_json}"}
                    ],
                    response_format={"type": "json_object"}
                )

                raw_content = response.choices[0].message.content
                agent_output = AgentOutput.model_validate_json(raw_content)
                action = agent_output.action
            except Exception as err:
                # Handle API or parsing errors gracefully
                print(f"DEBUG: Step {current_step} error: {err}", file=sys.stderr)
                action = DoNothingAction()

            # Execute action
            obs, reward = env.step(action)
            total_score = reward.score
            
            # 2. STEP BLOCK
            print(f"[STEP] step={current_step} reward={total_score}", flush=True)
            
            if reward.is_done:
                break

    except Exception as fatal_err:
        print(f"CRITICAL ERROR: {fatal_err}", file=sys.stderr)
    finally:
        # 3. GUARANTEED END BLOCK
        # Note: total_score should be the final achieved score
        print(f"[END] task={task_level} score={total_score} steps={current_step}", flush=True)

if __name__ == "__main__":
    run_inference()