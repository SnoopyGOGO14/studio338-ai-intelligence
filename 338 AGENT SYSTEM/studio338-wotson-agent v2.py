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
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__("wotson-studio338-001", AgentType.WHATSAPP_MONITOR, config)
        
        # WhatsApp-specific components
        self.gateway_checker = GatewayChecker(config.get("known_events", {}))
        self.link_extractor = LinkParticipantExtractor()
        self.event_index = EventIndex()
        
        # Group monitoring state
        self.monitored_groups: Dict[str, GroupContext] = {}
        self.urgency_patterns = self._load_urgency_patterns()
        self.equipment_keywords = self._load_equipment_keywords()
        
        # A2A and MCP managers
        self.a2a_manager = A2AProtocolManager(self.agent_id, config.get("a2a_config", {}))
        self.mcp_manager = MCPManager(self.agent_id, config.get("mcp_config", {}))
        
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
            "server_url": self.config.get("whatsapp_mcp_server"),
            "capabilities": [
                "group-monitoring", "message-retrieval", "participant-tracking",
                "media-download", "status-updates"
            ]
        })
        
        # Real-time analysis tools
        await self.mcp_manager.connect_tool_server("realtime-analyzer", {
            "server_url": self.config.get("analysis_mcp_server"),
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
            "endpoint": f"{self.config.get('base_url')}/agents/{self.agent_id}",
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
                "documentation": f"{self.config.get('docs_url')}/agents/wotson"
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
        while True:
            try:
                # Fetch new messages
                messages = await self._fetch_new_messages(group_id)
                
                for message in messages:
                    await self._process_message(message)
                    
                # Update group urgency score
                await self._update_group_urgency(group_id)
                
                # Check for situations requiring immediate action
                await self._check_urgent_situations(group_id)
                
                # Brief pause before next check
                await asyncio.sleep(self.config.get("poll_interval", 5))
                
            except Exception as e:
                self.logger.error(f"Error monitoring group {group_id}: {e}")
                await asyncio.sleep(30)  # Longer pause on error
    
    async def _process_message(self, message: WhatsAppMessage) -> None:
        """Process a single WhatsApp message."""
        
        self.monitoring_stats["messages_processed"] += 1
        
        # Extract data from message
        extraction_result = self.link_extractor.extract_from_whatsapp([{
            "sender": message.sender,
            "text": message.content,
            "timestamp": message.timestamp.isoformat()
        }])
        
        # Update group context
        group_context = self.monitored_groups.get(message.group_id)
        if group_context:
            # Add participant
            first_name = message.sender.split()[0] if message.sender else ""
            group_context.participants.add(first_name)
            
            # Keep recent messages (last 100)
            group_context.recent_messages.append(message)
            if len(group_context.recent_messages) > 100:
                group_context.recent_messages.pop(0)
            
            group_context.last_activity = message.timestamp
        
        # Add to event index
        if extraction_result:
            item = extraction_result[0]
            await self.event_index.add_communication(
                group_context.event_id or "uncategorized",
                item
            )
        
        # Check for urgency indicators
        urgency_score = await self._calculate_message_urgency(message)
        if urgency_score > self.config.get("urgency_threshold", 0.7):
            await self._handle_urgent_message(message, urgency_score)
        
        # Extract knowledge if relevant
        if await self._is_knowledge_worthy(message):
            knowledge_entities = await self.extract_knowledge(message)
            for entity in knowledge_entities:
                await self.update_knowledge(entity)
    
    async def _calculate_message_urgency(self, message: WhatsAppMessage) -> float:
        """Calculate urgency score for a message."""
        
        content_lower = message.content.lower()
        urgency_score = 0.0
        
        # Check urgency patterns
        for pattern, weight in self.urgency_patterns.items():
            if re.search(pattern, content_lower):
                urgency_score += weight
                self._log_decision(
                    "urgency_detection",
                    f"Urgency pattern '{pattern}' detected",
                    {"message_id": message.message_id, "weight": weight}
                )
        
        # Use MCP tool for advanced urgency detection
        urgency_analysis = await self.invoke_mcp_tool("realtime-analyzer", {
            "action": "analyze-urgency",
            "text": message.content,
            "context": {
                "sender": message.sender,
                "group": message.group_name,
                "recent_activity": self._get_recent_group_activity(message.group_id)
            }
        })
        
        if urgency_analysis.get("success"):
            ai_urgency = urgency_analysis["result"].get("urgency_score", 0)
            urgency_score = max(urgency_score, ai_urgency)
        
        return min(urgency_score, 1.0)  # Cap at 1.0
    
    async def _handle_urgent_message(self, message: WhatsAppMessage, urgency_score: float) -> None:
        """Handle messages identified as urgent."""
        
        self.monitoring_stats["urgent_situations_detected"] += 1
        
        self.logger.warning(
            f"Urgent message detected (score: {urgency_score:.2f}) "
            f"in group {message.group_name}: {message.content[:100]}..."
        )
        
        # Get historical context from ELA
        historical_context = await self._get_historical_context(message)
        
        # Synthesize comprehensive response
        response_data = await self._synthesize_urgent_response(
            message, urgency_score, historical_context
        )
        
        # Notify relevant parties
        await self._notify_urgent_situation(response_data)
        
        # Create knowledge entity for future reference
        entity = KnowledgeEntity(
            entity_id=f"urgent_{message.message_id}",
            entity_type="incident",
            content=f"Urgent situation: {message.content}",
            confidence_score=urgency_score,
            source_agent=self.agent_type,
            source_data=[message.message_id],
            created_at=datetime.utcnow(),
            last_updated=datetime.utcnow(),
            relationships=[],
            venue_context={
                "urgency_score": urgency_score,
                "group": message.group_name,
                "response": response_data
            }
        )
        await self.update_knowledge(entity)
    
    async def _get_historical_context(self, message: WhatsAppMessage) -> Dict[str, Any]:
        """Get historical context from ELA for better decision making."""
        
        self.monitoring_stats["ela_consultations"] += 1
        
        # Identify equipment or procedures mentioned
        equipment_mentioned = self._extract_equipment_references(message.content)
        
        # Query ELA for historical context
        ela_response = await self.delegate_task(
            "ela-studio338-001",
            "historical-email-analysis",
            {
                "timeframe": "30d",
                "equipment_focus": equipment_mentioned,
                "categories": ["equipment-issues", "maintenance", "incidents"],
                "urgency_filter": "urgent"
            },
            priority=9,  # High priority for urgent situations
            timeout=10   # Quick response needed
        )
        
        return ela_response.get("result", {})
    
    async def extract_knowledge(self, message: WhatsAppMessage) -> List[KnowledgeEntity]:
        """Extract knowledge entities from WhatsApp messages."""
        
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
        """Fetch new messages from WhatsApp group."""
        
        # Use MCP tool to fetch messages
        result = await self.invoke_mcp_tool("whatsapp-api", {
            "action": "fetch-messages",
            "group_id": group_id,
            "since": self._get_last_fetch_time(group_id),
            "limit": 50
        })
        
        if not result.get("success"):
            return []
        
        # Convert to WhatsAppMessage objects
        messages = []
        for msg_data in result["result"]["messages"]:
            message = WhatsAppMessage(
                message_id=msg_data["id"],
                group_id=group_id,
                group_name=self.monitored_groups[group_id].group_name,
                sender=msg_data["sender"],
                content=msg_data["content"],
                timestamp=datetime.fromisoformat(msg_data["timestamp"]),
                attachments=msg_data.get("attachments", []),
                mentions=msg_data.get("mentions", [])
            )
            messages.append(message)
        
        return messages
    
    def _extract_equipment_references(self, text: str) -> List[str]:
        """Extract equipment references from message text."""
        equipment_found = []
        text_lower = text.lower()
        
        for equipment in self.equipment_keywords:
            if equipment.lower() in text_lower:
                equipment_found.append(equipment)
        
        return equipment_found
    
    def _is_equipment_issue(self, text: str, equipment: str) -> bool:
        """Determine if message indicates an equipment issue."""
        issue_indicators = [
            "broken", "not working", "failed", "issue", "problem",
            "malfunction", "error", "fault", "damaged", "needs repair"
        ]
        
        text_lower = text.lower()
        equipment_lower = equipment.lower()
        
        # Check if equipment and issue indicator appear near each other
        for indicator in issue_indicators:
            if indicator in text_lower and equipment_lower in text_lower:
                # Simple proximity check (within 50 characters)
                equipment_pos = text_lower.find(equipment_lower)
                indicator_pos = text_lower.find(indicator)
                if abs(equipment_pos - indicator_pos) < 50:
                    return True
        
        return False
    
    def _load_urgency_patterns(self) -> Dict[str, float]:
        """Load urgency detection patterns."""
        return {
            r'\b(urgent|emergency|critical|asap|immediately)\b': 0.8,
            r'\b(broken|failed|not working|down)\b': 0.6,
            r'\b(help|need|required|must)\b': 0.4,
            r'\b(accident|injury|fire|flood)\b': 1.0,
            r'\b(power out|blackout|no electricity)\b': 0.7,
            r'\b(cancelled|postponed)\b': 0.5,
            r'[!]{2,}': 0.3,  # Multiple exclamation marks
            r'\b(NOW|URGENT|HELP)\b': 0.7  # All caps urgency words
        }
    
    def _load_equipment_keywords(self) -> List[str]:
        """Load equipment keywords for Studio338."""
        return [
            # Audio equipment
            "mixer", "CDJ", "turntable", "speakers", "amplifier", "microphone",
            "sound system", "PA system", "monitor", "subwoofer",
            
            # Lighting
            "lights", "LED", "strobe", "laser", "moving head", "spotlight",
            "lighting rig", "DMX", "controller",
            
            # Infrastructure
            "generator", "power", "electrical", "HVAC", "air conditioning",
            "heating", "plumbing", "security system",
            
            # Staging
            "stage", "platform", "barrier", "fence", "scaffold",
            
            # Safety
            "fire extinguisher", "emergency exit", "first aid"
        ]
    
    async def _is_knowledge_worthy(self, message: WhatsAppMessage) -> bool:
        """Determine if a message contains knowledge worth extracting."""
        
        # Check for equipment references
        if self._extract_equipment_references(message.content):
            return True
        
        # Check for procedural information
        if self._contains_procedure_update(message.content):
            return True
        
        # Check for incident reports
        if await self._calculate_message_urgency(message) > 0.5:
            return True
        
        return False
    
    def _contains_procedure_update(self, text: str) -> bool:
        """Check if message contains procedural information."""
        procedure_indicators = [
            "procedure", "process", "protocol", "steps", "instructions",
            "how to", "make sure", "always", "never", "must",
            "policy", "rule", "requirement"
        ]
        
        text_lower = text.lower()
        return any(indicator in text_lower for indicator in procedure_indicators)