"""
Scheduled Tasks for WOTSON Agent

This module contains functions for tasks that run on a schedule, such as
checking for unanswered questions, sending event reminders, and monitoring
group activity.
"""

import datetime
from typing import List, Dict, Any

from utils.config import CONFIG
from modules.query_handler import handle_message_query

# --- Placeholder/Mock Functions ---

def _get_unanswered_questions_from_db() -> List[Dict[str, Any]]:
    """MOCK: Simulates fetching unanswered questions from a database."""
    print("SCHEDULER: Checking for unanswered questions...")
    # In a real implementation, this would query a database.
    # Returning a sample message for demonstration.
    return [
        {
            "message_id": "mock_msg_123",
            "group_id": "group1@whatsapp.net",
            "group_name": "Event Staff",
            "sender": "user@whatsapp.net",
            "content": "Where can I find the spare extension cords?",
            "timestamp": (datetime.datetime.utcnow() - datetime.timedelta(hours=3)).isoformat(),
            "attachments": [],
            "mentions": [],
        }
    ]

def _get_upcoming_events_from_db() -> List[Dict[str, Any]]:
    """MOCK: Simulates fetching upcoming events from a database."""
    print("SCHEDULER: Checking for upcoming events...")
    return [
        {
            "event_id": "evt_abc",
            "event_name": "Summer Festival",
            "start_time": (datetime.datetime.utcnow() + datetime.timedelta(days=CONFIG.get("event_reminder_days", 1))).isoformat(),
            "relevant_groups": ["group1@whatsapp.net"],
        }
    ]

def _get_group_last_activity() -> Dict[str, str]:
    """MOCK: Simulates fetching the last activity timestamp for all groups."""
    print("SCHEDULER: Checking group inactivity...")
    return {
        "group1@whatsapp.net": datetime.datetime.utcnow().isoformat(),
        "group2@whatsapp.net": (datetime.datetime.utcnow() - datetime.timedelta(hours=CONFIG.get("inactivity_threshold_hours", 48) + 1)).isoformat(),
    }

def _send_whatsapp_group_reply(group_id: str, message: str):
    """MOCK: Simulates sending a reply to a WhatsApp group."""
    print(f"ACTION: Sending GROUP REPLY to {group_id}: '{message}'")

def _send_whatsapp_dm(user_id: str, message: str):
    """MOCK: Simulates sending a direct message to a user."""
    print(f"ACTION: Sending DM to {user_id}: '{message}'")

# --- Core Scheduler Functions ---

def scan_unanswered_questions():
    """
    Scans for unanswered questions, categorizes them, and takes action.
    """
    questions = _get_unanswered_questions_from_db()
    admin_ids = CONFIG.get("admin_ids", [])
    reply_threshold = CONFIG.get("group_reply_threshold", 0.85)

    for question in questions:
        # Use the query handler to assess the question
        result = handle_message_query(question, CONFIG)
        
        if result["urgency_score"] >= reply_threshold:
            # High confidence, auto-reply
            response = f"Hi! Based on our knowledge base, the answer to your question might be: [Automated Answer Placeholder]. If this isn't right, an admin will assist shortly."
            _send_whatsapp_group_reply(question["group_id"], response)
        else:
            # Low confidence, forward to admin
            for admin_id in admin_ids:
                message = f"An unanswered question in '{question['group_name']}' needs your attention: '{question['content']}'"
                _send_whatsapp_dm(admin_id, message)

def send_event_reminders():
    """
    Sends reminders for events starting soon.
    """
    events = _get_upcoming_events_from_db()
    for event in events:
        reminder_message = f"🔔 REMINDER: The event '{event['event_name']}' is scheduled to start soon."
        for group_id in event["relevant_groups"]:
            _send_whatsapp_group_reply(group_id, reminder_message)

def check_group_inactivity():
    """
    Detects inactive groups and sends a check-in message.
    """
    last_activity_map = _get_group_last_activity()
    inactivity_threshold = datetime.timedelta(hours=CONFIG.get("inactivity_threshold_hours", 48))
    
    for group_id, last_activity_ts in last_activity_map.items():
        last_activity = datetime.datetime.fromisoformat(last_activity_ts)
        if (datetime.datetime.utcnow() - last_activity) > inactivity_threshold:
            check_in_message = "👋 Just checking in! It's been a bit quiet here. Is everything running smoothly?"
            _send_whatsapp_group_reply(group_id, check_in_message)

def run_all_scheduled_tasks():
    """
    The main entry point to run all scheduled tasks sequentially.
    This would typically be called by a scheduler (e.g., cron, APScheduler).
    """
    print("\n--- Running Scheduled Tasks ---")
    scan_unanswered_questions()
    send_event_reminders()
    check_group_inactivity()
    print("--- Scheduled Tasks Complete ---\n") 