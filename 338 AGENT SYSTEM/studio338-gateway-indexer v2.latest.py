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
            
            # Extract sender's first name
            first_name = self._extract_first_name(sender)
            
            # Extract any mentioned participants
            mentions = self._extract_mentions(text)
            
            item = {
                "source": "WhatsApp",
                "timestamp": ts,
                "sender": sender,
                "first_name": first_name,
                "links": links,
                "mentions": mentions,
                "message_id": msg.get("id", ""),
                "group_id": msg.get("group_id", "")
            }
            
            extracted_items.append(item)
        
        return extracted_items
    
    def extract_from_email(self, email_message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract structured data from email messages.
        
        Args:
            email_message: Dict with email data (from, to, cc, subject, body, etc.)
            
        Returns:
            Dict of extracted data including links and participants
        """
        # Combine subject and body for link search
        content = f"{email_message.get('subject', '')} {email_message.get('body', '')}"
        
        # Extract links
        links = self.URL_PATTERN.findall(content)
        links = [self._clean_url(link) for link in links]
        links = [link for link in links if link]
        
        # Extract all participants
        participants = []
        first_names = []
        
        # Process sender
        from_name = email_message.get("from_name", "")
        from_address = email_message.get("from_address", "")
        if from_name:
            participants.append(from_name)
            first_names.append(self._extract_first_name(from_name))
        
        # Process recipients (to and cc)
        for field in ["to", "cc"]:
            recipients = email_message.get(field, [])
            if isinstance(recipients, str):
                recipients = [recipients]
            
            for recipient in recipients:
                name = self._extract_name_from_email(recipient)
                if name:
                    participants.append(name)
                    first_names.append(self._extract_first_name(name))
        
        # Extract any email addresses mentioned in body
        body_emails = self.EMAIL_PATTERN.findall(content)
        
        item = {
            "source": "Email",
            "timestamp": email_message.get("timestamp", ""),
            "from": from_address,
            "from_name": from_name,
            "to": email_message.get("to", []),
            "cc": email_message.get("cc", []),
            "subject": email_message.get("subject", ""),
            "participants": participants,
            "first_names": list(set(first_names)),  # Unique first names
            "links": links,
            "email_mentions": body_emails,
            "message_id": email_message.get("message_id", ""),
            "thread_id": email_message.get("thread_id", "")
        }
        
        return item
    
    def _clean_url(self, url: str) -> Optional[str]:
        """Clean and validate URL."""
        # Remove trailing punctuation
        url = re.sub(r'[.,;:!?)]+, '', url)
        
        # Validate URL structure
        if not url.startswith(('http://', 'https://')):
            return None
        
        # Basic validation
        if len(url) < 10 or ' ' in url:
            return None
        
        return url
    
    def _extract_first_name(self, full_name: str) -> str:
        """Extract first name from full name string."""
        if not full_name:
            return ""
        
        # Handle "Last, First" format
        if ',' in full_name:
            parts = full_name.split(',')
            if len(parts) >= 2:
                return parts[1].strip().split()[0]
        
        # Standard "First Last" format
        return full_name.strip().split()[0]
    
    def _extract_name_from_email(self, email_str: str) -> Optional[str]:
        """Extract name from email string like 'John Doe <john@example.com>'."""
        if '<' in email_str and '>' in email_str:
            name = email_str.split('<')[0].strip()
            return name if name else None
        return None
    
    def _extract_mentions(self, text: str) -> List[str]:
        """Extract @mentions from text."""
        # WhatsApp mention pattern
        mention_pattern = r'@(\w+)'
        mentions = re.findall(mention_pattern, text)
        return mentions


class EventIndex:
    """
    Centralized datastore for all event communications.
    Maintains categorized data organized by event/promoter with chronological ordering.
    """
    
    def __init__(self, storage_path: Optional[str] = None):
        """
        Initialize event index.
        
        Args:
            storage_path: Path to persistent storage (JSON file)
        """
        self.events: Dict[str, Dict[str, Any]] = {}
        self.storage_path = storage_path or "/Volumes/Studio338Data/event_index.json"
        self.index_stats = {
            "total_events": 0,
            "total_communications": 0,
            "last_updated": None
        }
        
        # Load existing data if available
        self._load_from_storage()
    
    def add_event(
        self, 
        event_id: str, 
        name: str, 
        date: Optional[str] = None, 
        promoter: Optional[str] = None
    ) -> None:
        """Initialize a new event category in the index if not exists."""
        if event_id not in self.events:
            self.events[event_id] = {
                "event_name": name,
                "date": date,
                "promoter": promoter,
                "participants": set(),
                "communications": [],
                "equipment_mentions": defaultdict(int),
                "created_at": datetime.utcnow().isoformat(),
                "last_activity": datetime.utcnow().isoformat()
            }
            self.index_stats["total_events"] += 1
            self._save_to_storage()
    
    def update_participants(self, event_id: str, first_names: List[str]) -> None:
        """Add participant first names to the event record."""
        if event_id in self.events:
            self.events[event_id]["participants"].update(first_names)
            self.events[event_id]["last_activity"] = datetime.utcnow().isoformat()
            self._save_to_storage()
    
    def add_communication(self, event_id: str, item: Dict[str, Any]) -> None:
        """
        Add a communication item (from WhatsApp or Email) to the event's record.
        
        Args:
            event_id: Event identifier
            item: Communication data dict with at least 'timestamp' and 'source'
        """
        # Ensure event exists
        if event_id not in self.events:
            self.add_event(event_id, name=event_id)
        
        # Add timestamp if missing
        if not item.get("timestamp"):
            item["timestamp"] = datetime.utcnow().isoformat()
        
        # Append the communication item
        self.events[event_id]["communications"].append(item)
        
        # Keep communications sorted by timestamp
        self.events[event_id]["communications"].sort(
            key=lambda x: x.get("timestamp", "")
        )
        
        # Update participants
        if item.get("first_name"):
            self.update_participants(event_id, [item["first_name"]])
        if item.get("first_names"):
            self.update_participants(event_id, item["first_names"])
        
        # Track equipment mentions
        self._update_equipment_mentions(event_id, item)
        
        # Update stats
        self.events[event_id]["last_activity"] = datetime.utcnow().isoformat()
        self.index_stats["total_communications"] += 1
        self.index_stats["last_updated"] = datetime.utcnow().isoformat()
        
        self._save_to_storage()
    
    def get_event_communications(
        self, 
        event_id: str, 
        time_window: Optional[str] = None,
        source_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get communications for an event with optional filtering.
        
        Args:
            event_id: Event identifier
            time_window: Time window like "24h", "7d", "30d"
            source_filter: Filter by source ("WhatsApp" or "Email")
            
        Returns:
            List of communication items
        """
        if event_id not in self.events:
            return []
        
        communications = self.events[event_id]["communications"]
        
        # Apply time window filter
        if time_window:
            cutoff = self._calculate_cutoff_time(time_window)
            communications = [
                comm for comm in communications
                if datetime.fromisoformat(comm["timestamp"]) > cutoff
            ]
        
        # Apply source filter
        if source_filter:
            communications = [
                comm for comm in communications
                if comm.get("source") == source_filter
            ]
        
        return communications
    
    def get_event_summary(self, event_id: str) -> Dict[str, Any]:
        """Get a summary of an event's communications and activity."""
        if event_id not in self.events:
            return {}
        
        event = self.events[event_id]
        communications = event["communications"]
        
        # Calculate summary statistics
        whatsapp_count = sum(1 for c in communications if c.get("source") == "WhatsApp")
        email_count = sum(1 for c in communications if c.get("source") == "Email")
        
        # Get recent activity
        recent_cutoff = self._calculate_cutoff_time("24h")
        recent_comms = [
            c for c in communications
            if datetime.fromisoformat(c["timestamp"]) > recent_cutoff
        ]
        
        # Top equipment mentions
        top_equipment = sorted(
            event["equipment_mentions"].items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]
        
        return {
            "event_id": event_id,
            "event_name": event["event_name"],
            "date": event["date"],
            "promoter": event["promoter"],
            "total_communications": len(communications),
            "whatsapp_messages": whatsapp_count,
            "email_messages": email_count,
            "unique_participants": len(event["participants"]),
            "recent_activity_24h": len(recent_comms),
            "top_equipment_mentions": top_equipment,
            "created_at": event["created_at"],
            "last_activity": event["last_activity"]
        }
    
    def search_events(
        self, 
        query: str, 
        date_range: Optional[Tuple[str, str]] = None
    ) -> List[str]:
        """
        Search for events by name, promoter, or participant.
        
        Returns:
            List of matching event IDs
        """
        query_lower = query.lower()
        matching_events = []
        
        for event_id, event in self.events.items():
            # Check event name
            if query_lower in event["event_name"].lower():
                matching_events.append(event_id)
                continue
            
            # Check promoter
            if event["promoter"] and query_lower in event["promoter"].lower():
                matching_events.append(event_id)
                continue
            
            # Check participants
            for participant in event["participants"]:
                if query_lower in participant.lower():
                    matching_events.append(event_id)
                    break
        
        # Apply date range filter if provided
        if date_range and matching_events:
            start_date, end_date = date_range
            filtered_events = []
            for event_id in matching_events:
                event_date = self.events[event_id].get("date")
                if event_date and start_date <= event_date <= end_date:
                    filtered_events.append(event_id)
            matching_events = filtered_events
        
        return matching_events
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get overall index statistics."""
        total_participants = set()
        total_links = 0
        
        for event in self.events.values():
            total_participants.update(event["participants"])
            for comm in event["communications"]:
                total_links += len(comm.get("links", []))
        
        return {
            "total_events": len(self.events),
            "total_communications": self.index_stats["total_communications"],
            "unique_participants": len(total_participants),
            "total_links_shared": total_links,
            "last_updated": self.index_stats["last_updated"]
        }
    
    def export_to_json(self, filepath: Optional[str] = None) -> str:
        """
        Export the indexed data to JSON file.
        
        Args:
            filepath: Optional custom filepath
            
        Returns:
            Path to exported file
        """
        filepath = filepath or f"/Volumes/Studio338Data/event_index_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        # Convert sets to lists for JSON serialization
        export_data = {}
        for eid, info in self.events.items():
            export_data[eid] = {
                "event_name": info["event_name"],
                "date": info["date"],
                "promoter": info["promoter"],
                "participants": list(info["participants"]),
                "communications": info["communications"],
                "equipment_mentions": dict(info["equipment_mentions"]),
                "created_at": info["created_at"],
                "last_activity": info["last_activity"]
            }
        
        with open(filepath, 'w') as f:
            json.dump(export_data, f, indent=2, default=str)
        
        return filepath
    
    def _update_equipment_mentions(self, event_id: str, item: Dict[str, Any]) -> None:
        """Track equipment mentions in communications."""
        # Equipment keywords to track
        equipment_keywords = [
            "mixer", "CDJ", "speaker", "light", "laser", "stage",
            "generator", "cable", "microphone", "amplifier"
        ]
        
        # Check message content
        content = ""
        if item.get("source") == "WhatsApp":
            content = item.get("text", "")
        elif item.get("source") == "Email":
            content = f"{item.get('subject', '')} {item.get('body', '')}"
        
        content_lower = content.lower()
        
        for equipment in equipment_keywords:
            if equipment in content_lower:
                self.events[event_id]["equipment_mentions"][equipment] += 1
    
    def _calculate_cutoff_time(self, time_window: str) -> datetime:
        """Calculate cutoff datetime from time window string."""
        now = datetime.utcnow()
        
        if time_window.endswith('h'):
            hours = int(time_window[:-1])
            return now - timedelta(hours=hours)
        elif time_window.endswith('d'):
            days = int(time_window[:-1])
            return now - timedelta(days=days)
        else:
            # Default to 24 hours
            return now - timedelta(hours=24)
    
    def _save_to_storage(self) -> None:
        """Save index to persistent storage."""
        if not self.storage_path:
            return
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
        
        # Prepare data for JSON serialization
        save_data = {
            "events": {},
            "stats": self.index_stats
        }
        
        for eid, info in self.events.items():
            save_data["events"][eid] = {
                "event_name": info["event_name"],
                "date": info["date"],
                "promoter": info["promoter"],
                "participants": list(info["participants"]),
                "communications": info["communications"],
                "equipment_mentions": dict(info["equipment_mentions"]),
                "created_at": info["created_at"],
                "last_activity": info["last_activity"]
            }
        
        with open(self.storage_path, 'w') as f:
            json.dump(save_data, f, indent=2, default=str)
    
    def _load_from_storage(self) -> None:
        """Load index from persistent storage."""
        if not self.storage_path or not os.path.exists(self.storage_path):
            return
        
        try:
            with open(self.storage_path, 'r') as f:
                data = json.load(f)
            
            # Restore events
            for eid, info in data.get("events", {}).items():
                self.events[eid] = {
                    "event_name": info["event_name"],
                    "date": info["date"],
                    "promoter": info["promoter"],
                    "participants": set(info["participants"]),
                    "communications": info["communications"],
                    "equipment_mentions": defaultdict(int, info.get("equipment_mentions", {})),
                    "created_at": info["created_at"],
                    "last_activity": info["last_activity"]
                }
            
            # Restore stats
            self.index_stats = data.get("stats", self.index_stats)
            
        except Exception as e:
            print(f"Error loading index from storage: {e}")