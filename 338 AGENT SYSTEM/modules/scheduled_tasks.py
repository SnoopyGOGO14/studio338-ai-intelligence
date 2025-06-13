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
from db.database import get_unanswered_questions, get_upcoming_events, get_group_silence_state
from modules.whatsapp_service import send_group_message, send_private_message

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
            send_group_message(question["group_id"], response)
        else:
            # Low confidence, forward to admin
            for admin_id in admin_ids:
                message = f"An unanswered question in a group needs your attention: '{question['content']}'"
                send_private_message(admin_id, message)

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
        reminder_message = f"🔔 REMINDER: The event '{event['name']}' is scheduled to start soon."
        send_group_message(event["group_id"], reminder_message)

def check_group_inactivity():
    """
    Detects inactive groups and sends a check-in message.
    """
    inactive_hours = CONFIG.get("inactivity_threshold_hours", 8)
    silent_groups = get_group_silence_state(inactive_hours)
    
    if not silent_groups:
        print("SCHEDULER: No inactive groups found.")
        return

    for group in silent_groups:
        check_in_message = f"👋 Just checking in! It's been a bit quiet in the '{group['event_name']}' group. Is everything running smoothly?"
        send_group_message(group["group_id"], check_in_message)

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