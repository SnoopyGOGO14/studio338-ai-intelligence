"""
WhatsApp Service module for WOTSON Agent.
This module is a placeholder for the actual WhatsApp integration.
It provides a consistent interface for sending messages, which can be
backed by any WhatsApp API or bridge (e.g., wweb.js, Baileys, etc.).
"""
import requests
from utils.config import CONFIG

WHATSAPP_API = CONFIG['whatsapp'].get('webhook_url', 'http://localhost:5001/send')

def send_group_message(group_id: str, message: str):
    """Send a message to a WhatsApp group via the bridge."""
    payload = {
        "to": group_id,
        "type": "group",
        "message": message,
    }
    try:
        res = requests.post(WHATSAPP_API, json=payload, timeout=10)
        res.raise_for_status()
        print(f"Sent to group {group_id}: {message}")
    except Exception as e:
        print(f"Failed to send group message: {e}")

def send_private_message(user_id: str, message: str):
    """Send a direct message to a user via the bridge."""
    payload = {
        "to": user_id,
        "type": "private",
        "message": message,
    }
    try:
        res = requests.post(WHATSAPP_API, json=payload, timeout=10)
        res.raise_for_status()
        print(f"Sent DM to {user_id}: {message}")
    except Exception as e:
        print(f"Failed to send DM: {e}") 