# inference.py
import os
import requests
import json
from openai import OpenAI

API_BASE_URL = os.environ.get("API_BASE_URL", "https://api.openai.com/v1")
MODEL_NAME = os.environ.get("MODEL_NAME", "gpt-4o")
HF_TOKEN = os.environ.get("HF_TOKEN", "")

if not HF_TOKEN:
    print("WARNING: HF_TOKEN environment variable is not set. Inference might fail.")

client = OpenAI(
    base_url=API_BASE_URL,
    api_key=HF_TOKEN or "dummy"
)

ENV_URL = "http://localhost:7860"

def run_task(level: str):
    print(f"\n--- Running Task: {level.upper()} ---")
    
    try:
        res = requests.post(f"{ENV_URL}/reset", json={"task_level": level})
        res.raise_for_status()
        observation = res.json()
        print(f"Observation: {observation}")
    except requests.exceptions.RequestException as e:
        print(f"Failed to reset env for {level}: {e}")
        return

    system_prompt = """You are an Elite Autonomous Inbox Manager.
You will receive an observation (JSON) showing emails currently in the inbox, available_folders, and calendar_slots.
Your job is to read the emails and categorize them, route them, or book a meeting.

You MUST respond with a valid JSON object matching the following Action schema (no markdown blocks, just pure JSON).

Schema:
{
  "category": "spam" | "invoice" | "meeting_request" | "general",
  "routed_folder": string | null (choose from available_folders),
  "meeting_booked_time": string | null (choose from calendar_slots if 'meeting_request'),
  "is_deleted": boolean,
  "notes": "string explaining reasoning"
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
        action_json_str = response.choices[0].message.content
        action_dict = json.loads(action_json_str)
        print(f"Agent Action: {action_dict}")
    except Exception as e:
        print(f"LLM Error: {e}")
        return

    try:
        step_res = requests.post(f"{ENV_URL}/step", json=action_dict)
        step_res.raise_for_status()
        result = step_res.json()
        print(f"Step Result -> Reward: {result['reward']} | Done: {result['done']}")
        print(f"Info: {result['info']}")
    except Exception as e:
        print(f"Step Error: {e}")

if __name__ == "__main__":
    for level in ["easy", "medium", "hard"]:
        run_task(level)
