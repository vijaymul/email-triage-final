from pydantic import BaseModel, Field
from typing import List, Optional, Literal

class Email(BaseModel):
    id: str
    sender: str
    subject: str
    body: str
    date: str

class Observation(BaseModel):
    inbox: List[Email] = Field(description="List of emails currently in the inbox")
    available_folders: List[str] = Field(description="Available system folders to route emails into")
    calendar_slots: Optional[List[str]] = Field(default=None, description="Available timeslots for booking meetings")

class Action(BaseModel):
    category: Literal["spam", "invoice", "meeting_request", "general"] = Field(description="Categorization of the parsed email")
    routed_folder: Optional[str] = Field(default=None, description="Folder to move the email to")
    meeting_booked_time: Optional[str] = Field(default=None, description="Time slot booked, if applicable")
    is_deleted: bool = Field(default=False, description="Whether the email should be permanently deleted")
    notes: str = Field(description="Reasoning for the triage action")

class State(BaseModel):
    task_level: Literal["easy", "medium", "hard"] = Field(default="easy")
    score: float = Field(default=0.0)
    is_done: bool = Field(default=False)
