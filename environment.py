from typing import Tuple, Optional
from datetime import datetime, timedelta
from models import (
    FolderType, Email, CalendarSlot, Observation, Action, Reward, EnvironmentState, ActionType
)

class EmailEnv:
    def __init__(self, task_level: str = "easy"):
        """
        Initialize the environment.
        :param task_level: Choose between 'easy', 'medium', 'hard'
        """
        self.task_level = task_level.lower()
        self._state = EnvironmentState(current_time=datetime.now())
        self.max_steps = 10
        self.current_step = 0
        self.reset()
        
    def reset(self) -> Observation:
        self.current_step = 0
        # Set a standard baseline time for the simulation
        base_time = datetime(2026, 3, 27, 9, 0, 0)
        self._state.current_time = base_time
        
        emails = []
        slots = []
        
        if self.task_level in ["easy", "all"]:
            emails.append(Email(
                id="email_easy_1", sender="spammer@scam.net", subject="You won $1M!!!",
                body="Click here to claim your prize.", folder=FolderType.INBOX, timestamp=base_time
            ))
            
        if self.task_level in ["medium", "all"]:
            emails.append(Email(
                id="email_med_1", sender="billing@vendor.com", subject="Invoice #1024",
                body="Please find the attached invoice for $500.", folder=FolderType.INBOX, timestamp=base_time
            ))
            emails.append(Email(
                id="email_med_2", sender="colleague@company.com", subject="Sync next week",
                body="Can we meet to discuss the project?", folder=FolderType.INBOX, timestamp=base_time
            ))
            
        if self.task_level in ["hard", "all"]:
            emails.append(Email(
                id="email_hard_1", sender="boss@company.com", subject="Urgent: Q3 Planning",
                body="Please schedule a time for us to review Q3 plans from the available slots.", folder=FolderType.INBOX, timestamp=base_time
            ))
            slots.extend([
                CalendarSlot(id="slot_1", start_time=base_time + timedelta(hours=1), end_time=base_time + timedelta(hours=2)),
                CalendarSlot(id="slot_2", start_time=base_time + timedelta(hours=3), end_time=base_time + timedelta(hours=4))
            ])
            
        self._state.all_emails = emails
        self._state.calendar_slots = slots
        
        return self._get_observation()
        
    def _get_observation(self) -> Observation:
        # Agent only sees emails currently residing in the INBOX.
        visible_emails = [e for e in self._state.all_emails if e.folder == FolderType.INBOX]
        return Observation(
            emails=visible_emails,
            calendar_slots=self._state.calendar_slots,
            current_time=self._state.current_time
        )
        
    def state(self) -> EnvironmentState:
        """Returns the internal ground truth state (OpenEnv standard API point)."""
        return self._state
        
    def step(self, action: Action) -> Tuple[Observation, Reward]:
        """
        Apply an action to the environment, update the state, and evaluate the reward.
        Returns: (Observation, Reward)
        """
        self.current_step += 1
        
        # 1. Apply Action Logic
        if action.action_type == ActionType.DELETE:
            for e in self._state.all_emails:
                if e.id == action.email_id:
                    e.folder = FolderType.TRASH
                    break
                    
        elif action.action_type == ActionType.MOVE_TO_FOLDER:
            for e in self._state.all_emails:
                if e.id == action.email_id:
                    e.folder = action.target_folder
                    break
                    
        elif action.action_type == ActionType.REPLY:
            # Simplified: Marks an email as read once replied to. 
            # In a real setup, we might log the agent's message text somewhere.
            for e in self._state.all_emails:
                if e.id == action.email_id:
                    e.is_read = True
                    break
                    
        elif action.action_type == ActionType.SCHEDULE_MEETING:
            # Mark the slot as booked
            for slot in self._state.calendar_slots:
                if slot.id == action.slot_id and slot.is_available:
                    slot.is_available = False
            # Clear the meeting request from the inbox 
            for e in self._state.all_emails:
                if e.id == action.email_id:
                    e.folder = FolderType.ARCHIVE
                    break
                    
        elif action.action_type == ActionType.DO_NOTHING:
            pass

        # 2. Grade the current state based on the task criteria
        reward = self._grade_task()
        
        # 3. Check termination conditions
        if reward.score == 1.0 or self.current_step >= self.max_steps:
            reward.is_done = True
            
        return self._get_observation(), reward

    def _grade_task(self) -> Reward:
        """
        Programmatic grader that returns a score between 0.0 and 1.0.
        """
        score = 0.0
        reason = "Task incomplete."
        
        if self.task_level == "easy":
            spam_email = next((e for e in self._state.all_emails if e.id == "email_easy_1"), None)
            if spam_email and spam_email.folder == FolderType.TRASH:
                score = 1.0
                reason = "Successfully identified and deleted the spam email."
            else:
                score = 0.0
                reason = "Spam email is still not in the TRASH folder."
                
        elif self.task_level == "medium":
            invoice = next((e for e in self._state.all_emails if e.id == "email_med_1"), None)
            meeting = next((e for e in self._state.all_emails if e.id == "email_med_2"), None)
            
            correct_invoice = invoice and invoice.folder == FolderType.INVOICES
            correct_meeting = meeting and meeting.folder == FolderType.MEETINGS
            
            if correct_invoice and correct_meeting:
                score = 1.0
                reason = "Successfully sorted both invoices and meeting requests."
            elif correct_invoice:
                score = 0.5
                reason = "Sorted the invoice, but missed the meeting request."
            elif correct_meeting:
                score = 0.5
                reason = "Sorted the meeting request, but missed the invoice."
            else:
                score = 0.0
                reason = "Emails are not sorted into their correct target folders yet."
                
        elif self.task_level == "hard":
            meeting_req = next((e for e in self._state.all_emails if e.id == "email_hard_1"), None)
            booked_slots = [s for s in self._state.calendar_slots if not s.is_available]
            
            if len(booked_slots) == 1 and meeting_req and meeting_req.folder != FolderType.INBOX:
                score = 1.0
                reason = "Successfully scheduled a valid meeting time and archived the request."
            elif len(booked_slots) == 1:
                score = 0.5
                reason = "Scheduled a meeting time, but the request email was left in the inbox."
            else:
                score = 0.0
                reason = "Valid meeting not yet scheduled."
                
        elif self.task_level == "all":
            score = 0.0
            reason = "Awaiting completion. ('all' level is a proxy that's not strictly graded yet)"

        return Reward(score=score, reason=reason, is_done=False)
