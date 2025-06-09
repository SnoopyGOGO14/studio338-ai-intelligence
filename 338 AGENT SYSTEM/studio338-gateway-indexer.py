"""
Core modules for Studio338 AI Intelligence System

Includes GatewayChecker for event categorization, LinkParticipantExtractor
for data parsing, and EventIndex for centralized data storage.
"""

import re
import json
from typing import Dict, List, Any, Optional, Set, Tuple
from datetime import datetime
from collections import defaultdict
import os

class GatewayChecker:
    """
    Determines how WhatsApp groups and email threads map to event categories.
    Uses explicit rules with transparent decision logging.
    """
    
    def __init__(self, known_events: Dict[str, Dict[str, Any]]):
        """
        Initialize with known events database.
        
        Args:
            known_events: Dictionary of event records with attributes like
                         'name', 'date', 'promoter', keywords, and participants
        """
        self.known_events = known_events
        self.decision_log = []
        
    def categorize_whatsapp_group(
        self, 
        group_name: str, 
        participant_names: List[str]
    ) -> Tuple[str, str]:
        """
        Determine which event/promoter category a WhatsApp group belongs to.
        
        Returns:
            Tuple of (event_id, reason_for_decision)
        """
        group_name_lower = group_name.lower()
        
        # 1. Check group name against known event names and promoter names
        for eid, event in self.known_events.items():
            name_kw = event["name"].lower()
            promoter_kw = event["promoter"].lower() if event.get("promoter") else ""
            
            if name_kw in group_name_lower or promoter_kw in group_name_lower:
                reason = f"Group name contains '{event['name']}' or promoter '{event['promoter']}'"
                self._log_decision("whatsapp_group", group_name, eid, reason)
                return eid, reason
            
            # Check known keywords for the event
            for kw in event.get("keywords", []):
                if kw.lower() in group_name_lower:
                    reason = f"Group name contains keyword '{kw}' for event '{event['name']}'"
                    self._log_decision("whatsapp_group", group_name, eid, reason)
                    return eid, reason
        
        # 2. Check if participant names match known promoters or VIPs
        participant_set = {p.lower() for p in participant_names}
        for eid, event in self.known_events.items():
            # Check promoter first name
            if event.get("promoter"):
                prom_name = event["promoter"].split()[0].lower()
                if prom_name and prom_name in participant_set:
                    reason = f"Participant '{prom_name.capitalize()}' is promoter for event '{event['name']}'"
                    self._log_decision("whatsapp_group", group_name, eid, reason)
                    return eid, reason
            
            # Check for overlap with known team members
            known_team = {p.lower() for p in event.get("participants", [])}
            overlap = participant_set & known_team
            if overlap:
                reason = f"Group shares {len(overlap)} members with event '{event['name']}'"
                self._log_decision("whatsapp_group", group_name, eid, reason)
                return eid, reason
        
        # 3. Attempt to detect date in group name
        date = self._find_date(group_name)
        if date:
            # Check if date matches existing event
            for eid, event in self.known_events.items():
                if event.get("date") == date:
                    reason = f"Detected date {date} matching event '{event['name']}'"
                    self._log_decision("whatsapp_group", group_name, eid, reason)
                    return eid, reason
            
            # Create new event for this date
            new_event_id = self._create_new_event(group_name, date, participant_names)
            reason = f"No match found; created new event entry for date {date}"
            self._log_decision("whatsapp_group", group_name, new_event_id, reason)
            return new_event_id, reason
        
        # 4. Create new miscellaneous event as fallback
        new_event_id = self._create_new_event(group_name, None, participant_names)
        reason = "No known event criteria matched; initialized new event category"
        self._log_decision("whatsapp_group", group_name, new_event_id, reason)
        return new_event_id, reason
    
    def categorize_email_thread(
        self, 
        email_subject: str, 
        sender_address: str, 
        email_body: str
    ) -> Tuple[str, str]:
        """
        Categorize an email thread by event date and promoter brand.
        
        Returns:
            Tuple of (event_id, reason_for_decision)
        """
        text = (email_subject + " " + email_body).lower()
        
        # 1. Check for known promoter brands in sender or content
        for eid, event in self.known_events.items():
            if event.get("promoter"):
                promoter_lower = event["promoter"].lower()
                
                # Check sender domain
                if promoter_lower in sender_address.lower():
                    # Try to confirm with date
                    maybe_date = self._find_date(email_subject)
                    if maybe_date and event.get("date") == maybe_date:
                        reason = f"Sender matches promoter '{event['promoter']}', date {maybe_date} confirms"
                    else:
                        reason = f"Sender domain matches promoter '{event['promoter']}'"
                    self._log_decision("email", email_subject, eid, reason)
                    return eid, reason
                
                # Check content for promoter name
                if promoter_lower in text:
                    reason = f"Email mentions promoter '{event['promoter']}'"
                    self._log_decision("email", email_subject, eid, reason)
                    return eid, reason
            
            # Check for event name in content
            if event["name"].lower() in text:
                reason = f"Email mentions event name '{event['name']}'"
                self._log_decision("email", email_subject, eid, reason)
                return eid, reason
        
        # 2. Look for date in email content
        date = self._find_date(text)
        if date:
            # Check if any known event has this date
            for eid, event in self.known_events.items():
                if event.get("date") == date:
                    reason = f"Found date {date} in email, matching event '{event['name']}'"
                    self._log_decision("email", email_subject, eid, reason)
                    return eid, reason
            
            # Create new event for this date
            new_event_id = self._create_new_event(email_subject, date, [])
            reason = f"No known event on {date}; created new event entry"
            self._log_decision("email", email_subject, new_event_id, reason)
            return new_event_id, reason
        
        # 3. Create general event entry as fallback
        new_event_id = self._create_new_event(email_subject, None, [])
        reason = "Uncategorized thread; created new general event entry"
        self._log_decision("email", email_subject, new_event_id, reason)
        return new_event_id, reason
    
    def _find_date(self, text: str) -> Optional[str]:
        """
        Parse a date from text using multiple patterns.
        Returns standardized date string or None.
        """
        # Pattern 1: Month name and day (e.g., "Oct 15", "October 15th")
        month_pattern = r'\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2}(?:st|nd|rd|th)?\b'
        match = re.search(month_pattern, text, re.IGNORECASE)
        if match:
            return self._standardize_date(match.group(0))
        
        # Pattern 2: DD/MM/YYYY or DD-MM-YYYY
        date_pattern = r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b'
        match = re.search(date_pattern, text)
        if match:
            return self._standardize_date(match.group(0))
        
        # Pattern 3: YYYY-MM-DD (ISO format)
        iso_pattern = r'\b\d{4}-\d{2}-\d{2}\b'
        match = re.search(iso_pattern, text)
        if match:
            return match.group(0)
        
        return None
    
    def _standardize_date(self, date_str: str) -> str:
        """Convert various date formats to YYYY-MM-DD."""
        # This is a simplified version - in production, use dateutil.parser
        # For now, just return the original string
        # In real implementation, convert to standard format
        return date_str
    
    def _create_new_event(
        self, 
        name_source: str, 
        date: Optional[str], 
        participants: List[str]
    ) -> str:
        """Register a new event category."""
        new_id = f"event_{len(self.known_events) + 1}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        self.known_events[new_id] = {
            "name": name_source[:50],  # Truncate for event name
            "date": date,
            "promoter": None,
            "participants": participants,
            "keywords": [],
            "created_at": datetime.utcnow().isoformat(),
            "source": "auto_detected"
        }
        
        return new_id
    
    def _log_decision(self, source_type: str, source_name: str, event_id: str, reason: str):
        """Log categorization decision for transparency."""
        self.decision_log.append({
            "timestamp": datetime.utcnow().isoformat(),
            "source_type": source_type,
            "source_name": source_name,
            "event_id": event_id,
            "reason": reason
        })
    
    def get_decision_log(self) -> List[Dict[str, Any]]:
        """Get the decision log for audit purposes."""
        return self.decision_log


class LinkParticipantExtractor:
    """
    Extracts links, participants, and other structured data from messages.
    Standardizes data extraction across WhatsApp and email sources.
    """
    
    # URL pattern for link extraction
    URL_PATTERN = re.compile(
        r'(https?://[^\s<>"{}|\\^`\[\]]+)'
    )
    
    # Email pattern for participant extraction
    EMAIL_PATTERN = re.compile(
        r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})'
    )
    
    def extract_from_whatsapp(self, chat_messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Extract structured data from WhatsApp messages.
        
        Args:
            chat_messages: List of message dicts with 'sender', 'text', 'timestamp'
            
        Returns:
            List of extracted items with links and participant info
        """
        extracted_items = []
        
        for msg in chat_messages:
            text = msg.get("text", "")
            sender = msg.get("sender", "")
            ts = msg.get("timestamp", "")
            
            # Extract links from message text
            links = self.URL_PATTERN.findall(text)
            
            # Clean and validate links
            links = [self._clean_url(link) for link in links]
            links = [link for link in links if link]  # Remove None values
            
            # Extract sender's first