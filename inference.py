import os
import requests
import json
from openai import OpenAI

# 1. SETTINGS
# Change this to your direct HF Space URL for the final test
ENV_URL = "https://abhijeet-openenv-email-triage-final.hf.space"

API_BASE_URL = os.environ.get("API_BASE_URL", "https://api.openai.com/v1")
MODEL_NAME = os.environ.get("MODEL_NAME", "gpt-4o")
HF_TOKEN = os.environ.get("HF_TOKEN", "") # Ensure your API Key is set in your terminal

if not HF_TOKEN:
    print("WARNING: HF_TOKEN environment variable is not set. Inference might fail.")

client = OpenAI(
    base_url=API_BASE_URL,
    api_key=HF_TOKEN or "dummy"
)

def run_task(level: str):
    print(f"\n--- Running Task: {level.upper()} ---")
    
    try:
        # Note: Sending task_level in the body as per your script logic
        res = requests.post(f"{ENV_URL}/reset", json={"task_level": level})
        res.raise_for_status()
        observation = res.json()
        print(f"Observation: {observation}")
    except requests.exceptions.RequestException as e:
        print(f"Failed to reset env for {level}: {e}")
        return

    system_prompt = """You are an Elite Autonomous Inbox Manager.
You will receive an observation (JSON) showing emails, folders, and calendar slots.
Respond with valid JSON matching the schema:
{
  "category": "spam" | "invoice" | "meeting_request" | "general",
  "routed_folder": string | null,
  "meeting_booked_time": string | null,
  "is_deleted": boolean,
  "notes": "string"
}"""

    user_prompt = f"Observation: {json.dumps(observation, indent=2)}\n\nProvide your Action JSON."

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.0
        )
        action_dict = json.loads(response.choices[0].message.content)
        print(f"Agent Action: {action_dict}")
    except Exception as e:
        print(f"LLM Error: {e}")
        return

    try:
        # Submitting the action to the cloud environment
        step_res = requests.post(f"{ENV_URL}/step", json=action_dict)
        step_res.raise_for_status()
        result = step_res.json()
        print(f"Step Result -> Reward: {result.get('reward')} | Done: {result.get('done')}")
    except Exception as e:
        print(f"Step Error: {e}")

if __name__ == "__main__":
    for level in ["easy", "medium", "hard"]:
        run_task(level)