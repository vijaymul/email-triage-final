from typing import List, Literal, Union, Annotated
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field

class FolderType(str, Enum):
    INBOX = "inbox"
    SPAM = "spam"
    INVOICES = "invoices"
    MEETINGS = "meetings"
    TRASH = "trash"
    ARCHIVE = "archive"

class Email(BaseModel):
        id: str = Field(..., description="Unique identifier for the email")
        sender: str = Field(..., description="Email address of the sender")
        subject: str = Field(..., description="Subject line of the email")
        body: str = Field(..., description="Content of the email")
        folder: FolderType = Field(default=FolderType.INBOX, description="Current folder of the email")
        timestamp: datetime = Field(..., description="Time the email was received")
        is_read: bool = Field(default=False, description="Whether the email has been read")

class CalendarSlot(BaseModel):
    id: str = Field(..., description='Unique identifier for the calendar slot')
    start_time: datetime = Field(..., description='Start time of the slot')
    end_time: datetime = Field(..., description='End time of the slot')
    is_available: bool = Field(default=True, description='Whether the slot is available to be booked')

class Observation(BaseModel):
    """Observation provided to the agent at each step."""""
    emails: List[Email] = Field(..., description="List of emails in the current folder or search result")
    calendar: List[CalendarSlot] = Field(..., description="Agent's relevant calendar events")
    current_time: datetime = Field(..., description="Current system time in the environment")
    current_folder: FolderType = Field(..., description="The folder currently being viewed")
    unread_count: int = Field(..., description="Total number of unread emails in the inbox")

class ActionType(str, Enum):
    DELETE = "delete"
    MOVE = "move"
    REPLY = "reply"
    SCHEDULE = "schedule"
    NOTHING = "nothing"

class DeleteAction(BaseModel):
    action_type: Literal[ActionType.DELETE] = ActionType.DELETE
    email_id: str = Field(..., description="ID of the email to delete")

class MoveToFolderAction(BaseModel):
    action_type: Literal[ActionType.MOVE] = ActionType.MOVE
    email_id: str = Field(..., description="ID of the email to move")
    target_folder: FolderType = Field(..., description="Folder to move the email to")

class ReplyAction(BaseModel):
    action_type: Literal[ActionType.REPLY] = ActionType.REPLY
    email_id: str = Field(..., description="ID of the email to reply to")
    reply_body: str = Field(..., description="Body of the reply email")

class ScheduleMeetingAction(BaseModel):
    action_type: Literal[ActionType.SCHEDULE] = ActionType.SCHEDULE
    start_time: datetime = Field(..., description="Start time for the meeting")
    end_time: datetime = Field(..., description="End time for the meeting")
    summary: str = Field(..., description="Meeting title/summary")

class DoNothingAction(BaseModel):
        action_type: Literal[ActionType.NOTHING] = ActionType.NOTHING

Action = Annotated[Union[
    DeleteAction,
    MoveToFolderAction,
    ReplyAction,
    ScheduleMeetingAction,
    DoNothingAction
], Field(discriminator="action_type")]

class Reward(BaseModel):
    score: float = Field(..., description="Reward score from 0.0 to 1.0 (graded evaluation)", ge=0.0, le=1.0)
    reason: str = Field(..., description="Explanation of the assigned score or penalty")
    is_done: bool = Field(..., description="Whether the episode/task has completed")

class EnvironmentState(BaseModel):
    """Internal master state of the environment, tracking true ground truth."""""
    all_emails: List[Email] = Field(default_factory=list)
    calendar_slots: List[CalendarSlot] = Field(default_factory=list)
    current_time: datetime

# Backward compatibility alias
State = EnvironmentState

