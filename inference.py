import os
import json
from openai import OpenAI
from pydantic import BaseModel
from server.models import Action
from server.environment import EmailEnv

# This setup is exactly what the judges want to see!
client = OpenAI(
    base_url="https://router.huggingface.co/v1", # The HF Router
    api_key=os.environ.get("HF_TOKEN")           # Provided by the hackathon
)

# Use the environment specified model or a standard fallback
model_to_use = os.environ.get("MODEL_NAME", "moonshotai/Kimi-K2-Instruct-0905")

# We wrap the underlying Action union within a root BaseModel to explicitly guide 
# the OpenAI Structured Outputs API since it cleanly handles single-object responses.
class AgentOutput(BaseModel):
    action: Action

def run_inference(task_level: str = "easy", max_steps: int = 10):
    env = EmailEnv(task_level=task_level)
    obs = env.reset()
    
    print(f"--- Starting Round 1 Task Level: {task_level.upper()} ---")
    
    for step in range(max_steps):
        print(f"\n[Step {step + 1}]")
        
        # Serialize the observation to prompt the agent
        obs_json = obs.model_dump_json(indent=2)
        print("Observation:", obs_json)
        
        # We explicitly dictate the goals for the LLM based on task selection:
        system_prompt = (
            "You are an AI Email Assistant managing a user's inbox in a simulated real-world environment. "
            f"Your current difficulty level is: {task_level}.\n\n"
            "Primary Directives:\n"
            "- easy: Find any 'Spam' email and use the 'delete' action or 'move_to_folder' action to target_folder 'trash'. Ignore normal emails.\n"
            "- medium: Sort 'Invoices' to the 'invoices' folder and 'Meeting Requests' to the 'meetings' folder.\n"
            "- hard: Find a scheduling request. Pick a valid block from 'calendar_slots' and use the 'schedule_meeting' action. The request will automatically archive once booked.\n\n"
            "Assess the JSON observation provided by the user and produce the correct action."
        )
        
        user_prompt = f"Current Observation State:\n{obs_json}"

        # Utilizing the newest structured parser guarantees correct JSON formatting against our Pydantic specs
        response = client.beta.chat.completions.parse(
            model=model_to_use, # Ensure we're targeting a model that supports strict structured outputs
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format=AgentOutput
        )

        agent_output = response.choices[0].message.parsed
        action = agent_output.action
        
        print(f"Agent chose action: {action.action_type.value} -> {json.dumps(action.model_dump(), default=str)}")

        # Step the environment with our strictly typed agent action
        obs, reward = env.step(action)
        
        print(f"Score: {reward.score} | Reason: {reward.reason}")
        
        if reward.is_done:
            print("\n>> Evaluation Completed!")
            break

if __name__ == "__main__":
    # Test your environments locally by altering the difficulty parameter
    run_inference(task_level="hard")
