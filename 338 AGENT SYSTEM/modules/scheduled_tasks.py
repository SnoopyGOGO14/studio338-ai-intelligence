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
from database import get_unanswered_questions, get_upcoming_events, get_all_groups_activity
from modules.whatsapp_service import send_group_reply, send_dm

# --- Core Scheduler Functions ---

def scan_unanswered_questions():
    """
    Scans for unanswered questions, categorizes them, and takes action.
    """
    questions = get_unanswered_questions()
    admin_ids = CONFIG.get("admin_ids", [])
    reply_threshold = CONFIG.get("group_reply_threshold", 0.85)

    if not questions:
        print("SCHEDULER: No unanswered questions found.")
        return

    for question in questions:
        # Use the query handler to assess the question
        result = handle_message_query(question, CONFIG)
        
        if result["urgency_score"] >= reply_threshold:
            # High confidence, auto-reply
            response = f"Hi! Based on our knowledge base, the answer to your question might be: [Automated Answer Placeholder]. If this isn't right, an admin will assist shortly."
            send_group_reply(question["group_id"], response)
        else:
            # Low confidence, forward to admin
            for admin_id in admin_ids:
                message = f"An unanswered question in '{question.get('group_name', 'a group')}' needs your attention: '{question['content']}'"
                send_dm(admin_id, message)

def send_event_reminders():
    """
    Sends reminders for events starting soon.
    """
    reminder_days = CONFIG.get("event_reminder_days", 1)
    events = get_upcoming_events(reminder_days)

    if not events:
        print("SCHEDULER: No upcoming events to send reminders for.")
        return

    for event in events:
        reminder_message = f"🔔 REMINDER: The event '{event['event_name']}' is scheduled to start soon."
        # The 'relevant_groups' column is stored as a JSON string
        import json
        try:
            group_ids = json.loads(event.get("relevant_groups", "[]"))
            for group_id in group_ids:
                send_group_reply(group_id, reminder_message)
        except json.JSONDecodeError:
            print(f"Error: Could not parse relevant_groups for event {event['event_id']}")

def check_group_inactivity():
    """
    Detects inactive groups and sends a check-in message.
    """
    groups_activity = get_all_groups_activity()
    inactivity_threshold = datetime.timedelta(hours=CONFIG.get("inactivity_threshold_hours", 48))
    
    if not groups_activity:
        print("SCHEDULER: No group activity found to check.")
        return

    for group in groups_activity:
        last_activity = datetime.datetime.fromisoformat(group["last_activity_ts"])
        if (datetime.datetime.utcnow() - last_activity) > inactivity_threshold:
            check_in_message = "👋 Just checking in! It's been a bit quiet here. Is everything running smoothly?"
            send_group_reply(group["group_id"], check_in_message)

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