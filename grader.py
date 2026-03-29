# grader.py
from models import Action

def grade_easy(action: Action, expected: dict) -> float:
    score = 0.0
    if action.category == expected["category"]:
        score += 0.5
    if action.is_deleted == expected["is_deleted"] and action.routed_folder == expected["routed_folder"]:
        score += 0.5
    return score

def grade_medium(action: Action, expected: dict) -> float:
    score = 0.0
    if action.category == expected["category"]:
        score += 0.5
    if action.routed_folder == expected["routed_folder"]:
        score += 0.5
    return score

def grade_hard(action: Action, expected: dict) -> float:
    score = 0.0
    if action.category == expected["category"]:
        score += 0.3
    if action.routed_folder == expected["routed_folder"]:
        score += 0.3
    if action.meeting_booked_time == expected["meeting_booked_time"]:
        score += 0.4
    return score

def grade(task_level: str, action: Action, expected: dict) -> float:
    if task_level == "easy":
        return round(grade_easy(action, expected), 2)
    elif task_level == "medium":
        return round(grade_medium(action, expected), 2)
    elif task_level == "hard":
        return round(grade_hard(action, expected), 2)
    return 0.0
