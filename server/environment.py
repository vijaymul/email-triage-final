from datetime import datetime, timedelta
import random
import uuid
from typing import Tuple, List

from .models import (
    Observation, Action, ActionType, Reward, EnvironmentState,
    Email, FolderType, CalendarSlot, DeleteAction, MoveToFolderAction,
    ReplyAction, ScheduleMeetingAction
)

class EmailEnv:
    """
    Simulation environment for the Email Triage agent.
    """
    def __init__(self, task_level: str = "easy"):
        self.task_level = task_level.lower()
        self.reset()

    def reset(self) -> Observation:
        self.state = self._generate_initial_state()
        return self._get_observation()

    def _generate_initial_state(self) -> EnvironmentState:
        now = datetime(2024, 3, 30, 10, 0, 0)
        emails = []
        
        # 1. Spam (Easy)
        emails.append(Email(
            id=str(uuid.uuid4()),
            sender="lottery@scam.com",
            subject="YOU WON $1,000,000!!",
            body="Congratulations! You have won the international mega lottery. Click link below to claim your prize.",
            folder=FolderType.INBOX,
            timestamp=now - timedelta(minutes=5)
        ))

        # 2. Invoice (Medium)
        emails.append(Email(
            id=str(uuid.uuid4()),
            sender="billing@cloudprovider.com",
            subject="Invoice #INV-2024-001",
            body="Your monthly invoice for cloud services is attached. Please pay by the 15th of next month.",
            folder=FolderType.INBOX,
            timestamp=now - timedelta(minutes=10)
        ))

        # 3. Meeting Request (Medium/Hard)
        emails.append(Email(
            id=str(uuid.uuid4()),
            sender="boss@company.com",
            subject="Weekly Sync Request",
            body="Hi, I'd like to schedule our weekly sync. Please find a slot on Monday afternoon.",
            folder=FolderType.INBOX,
            timestamp=now - timedelta(minutes=15)
        ))

        # Normal Emails
        emails.append(Email(
            id=str(uuid.uuid4()),
            sender="newsletter@tech.com",
            subject="Weekly Tech Digest",
            body="Here is your weekly summary of tech news. Trends this week: AI, Web3, and standard packages.",
            folder=FolderType.INBOX,
            timestamp=now - timedelta(minutes=20)
        ))

        # Generate Calendar Slots (For Hard task)
        slots = [
            CalendarSlot(id="slot-1", start_time=now + timedelta(days=1, hours=4), end_time=now + timedelta(days=1, hours=5), is_available=True),
            CalendarSlot(id="slot-2", start_time=now + timedelta(days=1, hours=5), end_time=now + timedelta(days=1, hours=6), is_available=False),
            CalendarSlot(id="slot-3", start_time=now + timedelta(days=1, hours=6), end_time=now + timedelta(days=1, hours=7), is_available=True),
        ]

        return EnvironmentState(
            all_emails=emails,
            calendar_slots=slots,
            current_time=now
        )

    def _get_observation(self) -> Observation:
        # Agent only sees emails currently in the INBOX
        inbox_emails = [e for e in self.state.all_emails if e.folder == FolderType.INBOX]
        return Observation(
            emails=inbox_emails,
            calendar_slots=self.state.calendar_slots,
            current_time=self.state.current_time
        )

    def step(self, action: Action) -> Tuple[Observation, Reward]:
        reward = Reward(score=0.0, reason="Action ignored or invalid for task level.", is_done=False)
        
        if self.task_level == "easy":
            reward = self._evaluate_easy(action)
        elif self.task_level == "medium":
            reward = self._evaluate_medium(action)
        elif self.task_level == "hard":
            reward = self._evaluate_hard(action)

        return self._get_observation(), reward

    def _evaluate_easy(self, action: Action) -> Reward:
        # Goal: Delete the scam email
        target_subject = "YOU WON $1,000,000!!"
        if action.action_type in [ActionType.DELETE, ActionType.MOVE_TO_FOLDER]:
            email = self._get_email(getattr(action, 'email_id'))
            if email and email.subject == target_subject:
                if action.action_type == ActionType.DELETE or (action.action_type == ActionType.MOVE_TO_FOLDER and action.target_folder == FolderType.TRASH):
                    email.folder = FolderType.TRASH
                    return Reward(score=1.0, reason="Successfully deleted spam email.", is_done=True)
                
        return Reward(score=0.0, reason="Did not correctly triage the spam email.", is_done=True)

    def _evaluate_medium(self, action: Action) -> Reward:
        # Goal: Move invoice to invoices and boss sync to meetings
        if action.action_type == ActionType.MOVE_TO_FOLDER:
            email = self._get_email(action.email_id)
            if email:
                if "Invoice" in email.subject and action.target_folder == FolderType.INVOICES:
                    email.folder = FolderType.INVOICES
                    return Reward(score=0.5, reason="Correctly sorted invoice.", is_done=False)
                if "Weekly Sync" in email.subject and action.target_folder == FolderType.MEETINGS:
                    email.folder = FolderType.MEETINGS
                    return Reward(score=1.0, reason="Correctly sorted meeting request.", is_done=True)
        
        return Reward(score=0.0, reason="Invalid move or wrong target folder.", is_done=True)

    def _evaluate_hard(self, action: Action) -> Reward:
        # Goal: Schedule meeting in an available slot
        if action.action_type == ActionType.SCHEDULE_MEETING:
            email = self._get_email(action.email_id)
            slot = self._get_slot(action.slot_id)
            if email and "Weekly Sync" in email.subject and slot and slot.is_available:
                slot.is_available = False
                email.folder = FolderType.ARCHIVE
                return Reward(score=1.0, reason="Successfully scheduled meeting in an available slot.", is_done=True)
        
        return Reward(score=0.0, reason="Failed to schedule meeting correctly.", is_done=True)

    def _get_email(self, email_id: str) -> Email:
        for e in self.state.all_emails:
            if e.id == email_id:
                return e
        return None

    def _get_slot(self, slot_id: str) -> CalendarSlot:
        for s in self.state.calendar_slots:
            if s.id == slot_id:
                return s
        return None
    
    def get_full_state(self):
        return self.state
