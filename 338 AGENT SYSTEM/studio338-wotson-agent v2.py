"""
WOTSON - WhatsApp Operations Intelligence Agent for Studio338

This agent monitors WhatsApp groups for real-time operational intelligence,
identifying urgent situations and coordinating responses with other agents.
"""

import asyncio
import re
from typing import Dict, Any, List, Optional, Set
from datetime import datetime, timedelta
from dataclasses import dataclass
import json

from utils.config import CONFIG
from modules.query_handler import handle_message_query
from agents.base.base_agent import BaseAgent, AgentType, KnowledgeEntity, A2ATask
from agents.base.a2a_agent import A2AProtocolManager
from agents.base.mcp_client import MCPManager

@dataclass
class WhatsAppMessage:
    """Represents a WhatsApp message with metadata"""
    message_id: str
    group_id: str
    group_name: str
    sender: str
    content: str
    timestamp: datetime
    attachments: List[str] = None
    mentions: List[str] = None

@dataclass
class GroupContext:
    """Maintains context for a WhatsApp group"""
    group_id: str
    group_name: str
    event_id: Optional[str]
    promoter: Optional[str]
    participants: Set[str]
    recent_messages: List[WhatsAppMessage]
    urgency_score: float = 0.0
    last_activity: datetime = None

class WotsonWhatsAppAgent(BaseAgent):
    """
    WOTSON - WhatsApp Operations and Tactical Support Operations Network
    
    Real-time monitoring and intelligence extraction from WhatsApp groups
    for Studio338 venue operations.
    """
    
    def __init__(self):
        super().__init__(CONFIG["agent"]["id"], AgentType.WHATSAPP_MONITOR, CONFIG)
        
        # WhatsApp-specific components
        self.gateway_checker = GatewayChecker(CONFIG.get("known_events", {}))
        self.link_extractor = LinkParticipantExtractor()
        self.event_index = EventIndex()
        
        # Group monitoring state
        self.monitored_groups: Dict[str, GroupContext] = {}
        self.urgency_patterns = self._load_urgency_patterns()
        self.equipment_keywords = self._load_equipment_keywords()
        
        # A2A and MCP managers
        self.a2a_manager = A2AProtocolManager(self.agent_id, CONFIG.get("a2a_config", {}))
        self.mcp_manager = MCPManager(self.agent_id, CONFIG.get("mcp_config", {}))
        
        # Performance tracking
        self.monitoring_stats = {
            "messages_processed": 0,
            "urgent_situations_detected": 0,
            "knowledge_entities_created": 0,
            "ela_consultations": 0
        }
        
    async def initialize(self) -> None:
        """Initialize WOTSON with all necessary connections."""
        
        # Initialize A2A protocol manager
        await self.a2a_manager.initialize()
        await self.a2a_manager.register_agent(await self.generate_agent_card())
        
        # Initialize MCP tool connections
        await self.mcp_manager.initialize()
        await self._setup_mcp_tools()
        
        # Set up WhatsApp connection
        await self._setup_whatsapp_connection()
        
        # Load existing group contexts from storage
        await self._load_group_contexts()
        
        # Set up collaboration with ELA
        await self._setup_ela_collaboration()
        
        self.logger.info("WOTSON initialized successfully")
        
    async def _setup_mcp_tools(self) -> None:
        """Set up MCP tool connections for WhatsApp operations."""
        
        # WhatsApp API tools
        await self.mcp_manager.connect_tool_server("whatsapp-api", {
            "server_url": CONFIG["services"]["whatsapp_mcp_server"],
            "capabilities": [
                "group-monitoring", "message-retrieval", "participant-tracking",
                "media-download", "status-updates"
            ]
        })
        
        # Real-time analysis tools
        await self.mcp_manager.connect_tool_server("realtime-analyzer", {
            "server_url": CONFIG["services"]["analysis_mcp_server"],
            "capabilities": [
                "urgency-detection", "sentiment-analysis", "entity-extraction",
                "context-synthesis", "anomaly-detection"
            ]
        })
        
    async def _setup_ela_collaboration(self) -> None:
        """Establish collaboration with ELA for historical context."""
        
        await self.a2a_manager.register_collaboration_partner("ela-studio338-001", {
            "collaboration_types": [
                "historical-context", "equipment-history", "personnel-lookup",
                "procedure-query", "incident-analysis"
            ],
            "communication_preferences": {
                "timeout": 5000,
                "retry_attempts": 2,
                "priority": "high"
            },
            "trust_level": "high"
        })
        
    async def generate_agent_card(self) -> Dict[str, Any]:
        """Generate A2A agent card for WOTSON capabilities."""
        return {
            "agentId": self.agent_id,
            "name": "WOTSON - WhatsApp Operations Intelligence",
            "description": "Real-time WhatsApp monitoring and operational intelligence for Studio338",
            "version": "2.0.0",
            "agentType": "whatsapp_intelligence",
            "endpoint": f"{CONFIG['agent']['base_url']}/agents/{self.agent_id}",
            "capabilities": {
                "skills": [
                    {
                        "id": "realtime-monitoring",
                        "name": "Real-time WhatsApp Monitoring",
                        "description": "Monitor WhatsApp groups for operational updates and urgent situations",
                        "inputModes": ["application/json"],
                        "outputModes": ["application/json"],
                        "parameters": {
                            "group_ids": {"type": "array", "items": {"type": "string"}},
                            "urgency_threshold": {"type": "number", "minimum": 0, "maximum": 1},
                            "monitor_duration": {"type": "string", "enum": ["continuous", "1h", "24h"]},
                            "alert_types": {"type": "array", "items": {"type": "string"}}
                        }
                    },
                    {
                        "id": "urgency-detection",
                        "name": "Urgency Detection and Response",
                        "description": "Detect urgent situations and coordinate immediate responses",
                        "inputModes": ["text/plain", "application/json"],
                        "outputModes": ["application/json"],
                        "parameters": {
                            "message_content": {"type": "string"},
                            "group_context": {"type": "object"},
                            "urgency_factors": {"type": "array", "items": {"type": "string"}}
                        }
                    },
                    {
                        "id": "group-categorization",
                        "name": "WhatsApp Group Categorization",
                        "description": "Categorize WhatsApp groups by event and promoter",
                        "inputModes": ["application/json"],
                        "outputModes": ["application/json"],
                        "parameters": {
                            "group_name": {"type": "string"},
                            "participants": {"type": "array", "items": {"type": "string"}},
                            "recent_messages": {"type": "array"}
                        }
                    },
                    {
                        "id": "context-synthesis",
                        "name": "Real-time Context Synthesis",
                        "description": "Synthesize current situation from multiple WhatsApp groups",
                        "inputModes": ["application/json"],
                        "outputModes": ["application/json"],
                        "parameters": {
                            "group_ids": {"type": "array", "items": {"type": "string"}},
                            "time_window": {"type": "string"},
                            "focus_areas": {"type": "array", "items": {"type": "string"}}
                        }
                    }
                ],
                "collaborationCapabilities": [
                    "real-time-alerts", "context-sharing", "urgency-escalation",
                    "historical-context-request", "decision-support"
                ],
                "dataTypes": [
                    "whatsapp-messages", "group-metadata", "participant-lists",
                    "urgency-assessments", "operational-updates"
                ]
            },
            "authentication": {
                "type": "bearer",
                "description": "Bearer token authentication required"
            },
            "rateLimit": {
                "requestsPerMinute": 120,
                "concurrentRequests": 20
            },
            "metadata": {
                "vendor": "Studio338",
                "category": "real-time-intelligence",
                "tags": ["whatsapp", "monitoring", "urgency-detection", "venue-operations"],
                "documentation": f"{CONFIG['agent']['docs_url']}/agents/wotson"
            }
        }
    
    async def process_task(self, task: A2ATask) -> Dict[str, Any]:
        """Process incoming A2A tasks."""
        
        self.logger.info(f"Processing A2A task: {task.skill_id}")
        
        try:
            if task.skill_id == "realtime-monitoring":
                return await self._handle_monitoring_request(task)
            elif task.skill_id == "urgency-detection":
                return await self._handle_urgency_detection(task)
            elif task.skill_id == "group-categorization":
                return await self._handle_group_categorization(task)
            elif task.skill_id == "context-synthesis":
                return await self._handle_context_synthesis(task)
            else:
                return await self._handle_generic_task(task)
                
        except Exception as e:
            self.logger.error(f"Task processing failed: {e}")
            return {
                "taskId": task.id,
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def monitor_whatsapp_group(self, group_id: str, group_name: str) -> None:
        """
        Main monitoring loop for a WhatsApp group.
        Called when WOTSON is added to a new group or reconnects.
        """
        
        self.logger.info(f"Starting monitoring of group: {group_name} ({group_id})")
        
        # Categorize the group
        event_id, reason = await self._categorize_group(group_id, group_name)
        self._log_decision("group_categorization", reason, {
            "group_id": group_id,
            "group_name": group_name,
            "event_id": event_id
        })
        
        # Initialize group context
        if group_id not in self.monitored_groups:
            self.monitored_groups[group_id] = GroupContext(
                group_id=group_id,
                group_name=group_name,
                event_id=event_id,
                participants=set(),
                recent_messages=[]
            )
        
        # Start monitoring loop
        try:
            while self.monitoring_active:
                new_messages = await self._fetch_new_messages(group_id)
                for message in new_messages:
                    await self._process_message(message)
                
                # Brief pause before next check
                await asyncio.sleep(CONFIG.get("agent", {}).get("poll_interval", 5))
                
        except Exception as e:
            self.logger.error(f"Monitoring loop for group {group_id} failed: {e}")
    
    async def _process_message(self, message: WhatsAppMessage) -> None:
        """Process a single incoming WhatsApp message by passing it to the query handler."""
        
        # Update group context
        self.monitored_groups[message.group_id].recent_messages.append(message)
        self.monitored_groups[message.group_id].last_activity = message.timestamp
        self.monitoring_stats["messages_processed"] += 1
        
        # Pass to query handler for decision making
        # The message dataclass needs to be converted to a dict for the handler
        message_dict = {
            "message_id": message.message_id,
            "group_id": message.group_id,
            "group_name": message.group_name,
            "sender": message.sender,
            "content": message.content,
            "timestamp": message.timestamp.isoformat(),
            "attachments": message.attachments,
            "mentions": message.mentions,
        }
        
        action_result = handle_message_query(message_dict, CONFIG)
        
        self.logger.info(f"Query handler result for message {message.message_id}: {action_result['action']} - {action_result['details']}")

        # Act on the result from the query handler
        if action_result["action"] == "escalate":
            await self._handle_urgent_message(message, action_result["urgency_score"])
        
        # Extract knowledge if worthy (this logic could also move to the query handler)
        if await self._is_knowledge_worthy(message):
            knowledge_entities = await self.extract_knowledge(message)
            for entity in knowledge_entities:
                await self.add_knowledge(entity)
                self.monitoring_stats["knowledge_entities_created"] += 1
    
    async def _handle_urgent_message(self, message: WhatsAppMessage, urgency_score: float) -> None:
        """Handles a message identified as urgent by the query handler."""
        self.logger.warning(
            f"URGENT SITUATION DETECTED in group '{message.group_name}' "
            f"(Score: {urgency_score:.2f}): '{message.content}'"
        )
        # Logic to escalate, e.g., create A2A task, notify admin, etc.
        self.monitoring_stats["urgent_situations_detected"] += 1

        # Example: Consult ELA for historical context on similar issues
        historical_context = await self._get_historical_context(message)
        if historical_context:
            self.logger.info(f"ELA provided historical context: {historical_context}")
    
    async def _get_historical_context(self, message: WhatsAppMessage) -> Dict[str, Any]:
        """Consult with ELA for historical context on an urgent issue."""
        self.logger.info("Consulting ELA for historical context...")
        self.monitoring_stats["ela_consultations"] += 1
        
        try:
            response = await self.a2a_manager.send_task("ela-studio338-001", {
                "taskId": f"wotson-urgency-{message.message_id}",
                "skill_id": "historical-context",
                "parameters": {
                    "query": message.content,
                    "equipment": self._extract_equipment_references(message.content),
                    "context": {
                        "group": message.group_name,
                        "sender": message.sender
                    }
                }
            })
            return response.get("data", {})
        except Exception as e:
            self.logger.error(f"Failed to get historical context from ELA: {e}")
            return {}
    
    async def extract_knowledge(self, message: WhatsAppMessage) -> List[KnowledgeEntity]:
        """
        Extracts structured knowledge from a WhatsApp message.
        This could be event details, equipment status, procedural updates, etc.
        """
        entities = []
        content_lower = message.content.lower()
        
        # Extract equipment-related knowledge
        equipment_refs = self._extract_equipment_references(message.content)
        for equipment in equipment_refs:
            if self._is_equipment_issue(message.content, equipment):
                entity = KnowledgeEntity(
                    entity_id=f"whatsapp_equipment_{equipment}_{message.message_id}",
                    entity_type="equipment",
                    content=f"Equipment issue reported: {equipment} - {message.content}",
                    confidence_score=0.8,
                    source_agent=self.agent_type,
                    source_data=[message.message_id],
                    created_at=datetime.utcnow(),
                    last_updated=datetime.utcnow(),
                    relationships=[],
                    venue_context={
                        "equipment_type": equipment,
                        "issue_type": self._classify_equipment_issue(message.content),
                        "reporter": message.sender,
                        "group": message.group_name
                    }
                )
                entities.append(entity)
        
        # Extract procedural updates
        if self._contains_procedure_update(message.content):
            entity = KnowledgeEntity(
                entity_id=f"whatsapp_procedure_{message.message_id}",
                entity_type="procedure",
                content=message.content,
                confidence_score=0.7,
                source_agent=self.agent_type,
                source_data=[message.message_id],
                created_at=datetime.utcnow(),
                last_updated=datetime.utcnow(),
                relationships=[],
                venue_context={
                    "update_type": "real-time",
                    "group": message.group_name
                }
            )
            entities.append(entity)
        
        return entities
    
    # Helper methods for WOTSON functionality
    async def _categorize_group(self, group_id: str, group_name: str) -> tuple[str, str]:
        """Categorize a WhatsApp group using the gateway checker."""
        
        # Get participant list
        participants = await self._get_group_participants(group_id)
        
        # Use gateway checker for categorization
        event_id, reason = self.gateway_checker.categorize_whatsapp_group(
            group_name, participants
        )
        
        return event_id, reason
    
    async def _fetch_new_messages(self, group_id: str) -> List[WhatsAppMessage]:
        """
        Fetches new messages from a WhatsApp group since the last check.
        This is a placeholder for the actual WhatsApp API integration.
        """
        # In a real implementation, this would connect to the WhatsApp API
        # and retrieve messages since the last known timestamp.
        await asyncio.sleep(2) # Simulate network delay
        return []
    
    def _extract_equipment_references(self, text: str) -> List[str]:
        """Extract equipment references from message text."""
        equipment_found = []
        text_lower = text.lower()
        
        for equipment in self.equipment_keywords:
            if re.search(r'\b' + re.escape(equipment) + r'\b', text, re.IGNORECASE):
                equipment_found.append(equipment)
        
        return equipment_found
    
    def _is_equipment_issue(self, text: str, equipment: str) -> bool:
        """Checks if text mentions an issue with a piece of equipment."""
        # Simple keyword matching for demonstration
        issue_keywords = ["broken", "down", "issue", "fault", "not working", "problem"]
        text_lower = text.lower()
        if equipment.lower() in text_lower:
            for keyword in issue_keywords:
                if keyword in text_lower:
                    return True
        return False
    
    def _load_urgency_patterns(self) -> Dict[str, float]:
        """Loads urgency patterns from a file or config."""
        # This should come from a config file or a dedicated patterns file.
        return {
            r"\b(urgent|asap|critical)\b": 1.0,
            r"\b(help|issue|problem)\b": 0.8,
            r"\b(down|broken|failed)\b": 0.9,
            r"\b(power cut|power loss|no power)\b": 1.0,
            r"\b(leak|flood|water)\b": 0.95,
        }
    
    def _load_equipment_keywords(self) -> List[str]:
        """Loads equipment keywords from a file or config."""
        # This should come from a config file.
        return ["Pioneer", "CDJ", "mixer", "lights", "sound system", "generator"]
    
    async def _is_knowledge_worthy(self, message: WhatsAppMessage) -> bool:
        """Determines if a message contains valuable information for the knowledge base."""
        # Simple logic: if it's not urgent but contains equipment names or procedure updates.
        text = message.content.lower()
        if self._extract_equipment_references(text):
            return True
        if self._contains_procedure_update(text):
            return True
        return False
    
    def _contains_procedure_update(self, text: str) -> bool:
        """Checks for keywords indicating a procedural update."""
        update_keywords = ["procedure", "protocol", "new way", "do this from now on"]
        for keyword in update_keywords:
            if keyword in text:
                return True
        return False