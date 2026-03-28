# tasks.py

TASKS = {
    "easy": {
        "id": "easy-spam",
        "inbox": [{
            "id": "MSG-001",
            "sender": "lucky.winner@scammer.net",
            "subject": "YOU WON A FREE IPHONE 16!!!",
            "body": "Click the link below to claim your prize immediately!",
            "date": "2026-03-28T09:00:00Z"
        }],
        "available_folders": ["inbox", "invoices", "spam", "archive"],
        "calendar_slots": None,
        "expected": {
            "category": "spam",
            "routed_folder": "spam",
            "meeting_booked_time": None,
            "is_deleted": True
        }
    },
    "medium": {
        "id": "medium-invoice",
        "inbox": [{
            "id": "MSG-002",
            "sender": "billing@cloudservices.com",
            "subject": "Your monthly cloud hosting invoice - March",
            "body": "Dear customer, attached is your invoice #INV-9483 for the month of March in the amount of $45.60. Please pay by the 5th.",
            "date": "2026-03-28T10:15:00Z"
        }],
        "available_folders": ["inbox", "invoices", "spam", "archive"],
        "calendar_slots": None,
        "expected": {
            "category": "invoice",
            "routed_folder": "invoices",
            "meeting_booked_time": None,
            "is_deleted": False
        }
    },
    "hard": {
        "id": "hard-meeting",
        "inbox": [{
            "id": "MSG-003",
            "sender": "sarah.connor@acme-corp.com",
            "subject": "Urgent Sync on Q3 Strategy",
            "body": "Hi there, we really need to review the Q3 launch plan. Can we meet either at 2pm or 4pm tomorrow?",
            "date": "2026-03-28T14:30:00Z"
        }],
        "available_folders": ["inbox", "invoices", "spam", "archive", "priority"],
        "calendar_slots": ["2026-03-29T10:00:00Z", "2026-03-29T14:00:00Z", "2026-03-30T09:00:00Z"],
        "expected": {
            "category": "meeting_request",
            "routed_folder": "priority",
            "meeting_booked_time": "2026-03-29T14:00:00Z",
            "is_deleted": False
        }
    }
}
