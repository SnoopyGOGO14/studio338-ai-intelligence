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
                        "description