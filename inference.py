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
    
    # 1. IMMEDIATE PRINT OF START BLOCK FOR PIPELINE CONSISTENCY
    # This must happen before any potential fatal checks.
    print(f"[START] task={task_level}", flush=True)

    # Validate mandatory platform proxy variables
    required_vars = ["API_BASE_URL", "API_KEY"]
    missing_vars = [var for var in required_vars if var not in os.environ]
    
    total_score = 0.0
    current_step = 0

    if missing_vars:
        print(f"CRITICAL ERROR: Missing required environment variables: {', '.join(missing_vars)}", file=sys.stderr)
        # We print [END] and exit gracefully so the pipeline captures the failure state correctly.
        print(f"[END] task={task_level} score=0.0 steps=0", flush=True)
        sys.exit(1)

    # Optional variables with sensible defaults
    model_name = os.environ.get("MODEL_NAME", "gpt-4o")
    
    try:
        env = EmailEnv(task_level=task_level)
        obs = env.reset()
        
        # Initialize OpenAI client with the provided proxy credentials
        client = OpenAI(
            base_url=os.environ["API_BASE_URL"],
            api_key=os.environ["API_KEY"]
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
                # 2. WRAP RISKY LLM OPERATIONS
                response = client.chat.completions.create(
                    model=model_name,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": f"Observations:\n{obs_json}"}
                    ],
                    response_format={"type": "json_object"},
                    timeout=30 # Add timeout to prevent hanging
                )

                raw_content = response.choices[0].message.content
                agent_output = AgentOutput.model_validate_json(raw_content)
                action = agent_output.action
            except Exception as err:
                # Handle API timeouts, parsing errors, or model refusals
                print(f"DEBUG: Step {current_step} error (LLM/Parsing): {err}", file=sys.stderr)
                action = DoNothingAction()

            # Execute action in environment
            try:
                obs, reward = env.step(action)
                total_score = reward.score
                
                # 3. STEP BLOCK
                print(f"[STEP] step={current_step} reward={total_score}", flush=True)
                
                if reward.is_done:
                    break
            except Exception as env_err:
                print(f"DEBUG: Step {current_step} error (Environment): {env_err}", file=sys.stderr)
                break

    except Exception as fatal_err:
        print(f"CRITICAL ERROR (Setup/Fatal): {fatal_err}", file=sys.stderr)
    finally:
        # 4. GUARANTEED END BLOCK
        # This ensures that even if something fails halfway, the pipeline gets a final score report.
        print(f"[END] task={task_level} score={total_score} steps={current_step}", flush=True)

if __name__ == "__main__":
    run_inference()