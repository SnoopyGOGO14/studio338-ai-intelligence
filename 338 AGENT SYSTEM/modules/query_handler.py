"""
Query Handler for WOTSON Agent
This module is responsible for processing incoming WhatsApp messages,
determining the appropriate action, and returning a result to the main agent.
"""

from typing import Dict, Any

def handle_message_query(message: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Processes a WhatsApp message and decides on the next action.

    Args:
        message: A dictionary representing the WhatsApp message.
        config: The application's configuration dictionary.

    Returns:
        A dictionary containing the decided action and any relevant data.
    """
    # This is a placeholder for the logic that was in _process_message.
    # In a real implementation, this would involve NLP, rule-based checks, etc.
    
    urgency_threshold = config.get("agent", {}).get("urgency_threshold", 0.7)
    
    # Placeholder for urgency calculation
    urgency_score = _calculate_message_urgency(message, config)

    action = "log"
    details = f"Processed message {message.get('message_id')} with urgency {urgency_score:.2f}."

    if urgency_score > urgency_threshold:
        action = "escalate"
        details = f"Urgent message {message.get('message_id')} detected with score {urgency_score:.2f}."

    return {
        "action": action,
        "details": details,
        "message_id": message.get("message_id"),
        "urgency_score": urgency_score,
    }

def _calculate_message_urgency(message: Dict[str, Any], config: Dict[str, Any]) -> float:
    """
    Placeholder for urgency calculation logic.
    In a real scenario, this would use the urgency patterns from the config.
    """
    # Simple example: if "urgent" is in the message, score is high.
    if "urgent" in message.get("content", "").lower():
        return 0.9
    return 0.1 