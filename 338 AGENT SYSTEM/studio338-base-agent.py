"""
Base Agent Architecture for Studio338 AI Intelligence System

This module provides the foundation for all agents in the system,
implementing both A2A communication protocols and MCP tool access.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass
from datetime import datetime
import asyncio
import logging
from enum import Enum
import json
import uuid

class AgentType(Enum):
    """Types of agents in the Studio338 system"""
    EMAIL_LEARNING = "email_learning"
    WHATSAPP_MONITOR = "whatsapp_monitor"
    WORKFLOW_ORCHESTRATOR = "workflow_orchestrator"
    TOOL_COORDINATOR = "tool_coordinator"

class ProtocolType(Enum):
    """Communication protocol types"""
    A2A = "agent_to_agent"
    MCP = "model_context_protocol"

@dataclass
class A2ATask:
    """Standardized A2A task representation"""
    id: str
    skill_id: str
    agent_id: str
    parameters: Dict[str, Any]
    priority: int
    timeout: int
    requires_response: bool = True
    session_id: Optional[str] = None
    collaboration_context: Optional[Dict[str, Any]] = None

@dataclass
class MCPToolInvocation:
    """Standardized MCP tool invocation"""
    tool_name: str
    parameters: Dict[str, Any]
    context: Dict[str, Any]
    timeout: int = 30
    retry_count: int = 3

@dataclass
class KnowledgeEntity:
    """Universal knowledge representation across agents"""
    entity_id: str
    entity_type: str  # equipment, procedure, personnel, issue, event
    content: str
    confidence_score: float
    source_agent: AgentType
    source_data: List[str]  # Source message/email/document IDs
    created_at: datetime
    last_updated: datetime
    relationships: List[str]  # Related entity IDs
    venue_context: Optional[Dict[str, Any]] = None  # Studio338-specific context

class BaseAgent(ABC):
    """
    Enhanced base agent with A2A+MCP protocol support.
    
    This base class provides the foundation for all agents in the system,
    implementing both A2A communication protocols and MCP tool access.
    """
    
    def __init__(self, agent_id: str, agent_type: AgentType, config: Dict[str, Any]):
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.config = config
        
        # Knowledge and state management
        self.knowledge_base: Dict[str, KnowledgeEntity] = {}
        self.active_tasks: Dict[str, A2ATask] = {}
        self.performance_metrics = {
            "tasks_processed": 0,
            "tasks_succeeded": 0,
            "tasks_failed": 0,
            "avg_response_time": 0.0,
            "tool_invocations": 0,
            "knowledge_entities_created": 0
        }
        
        # Protocol managers (initialized in subclasses)
        self.a2a_manager = None  # Handles agent-to-agent communication
        self.mcp_manager = None  # Handles tool access and resource management
        
        # Collaboration and security
        self.trusted_agents: Set[str] = set()
        self.security_context = {
            "agent_id": agent_id,
            "permissions": config.get("permissions", []),
            "api_keys": {}  # Populated during initialization
        }
        
        # Logging and monitoring
        self.logger = logging.getLogger(f"agent.{agent_id}")
        self.logger.setLevel(logging.INFO)
        
        # Decision logging for transparency
        self.decision_log: List[Dict[str, Any]] = []
        
    @abstractmethod
    async def process_task(self, task: A2ATask) -> Dict[str, Any]:
        """
        Process an incoming A2A task. Each agent type implements this
        to handle domain-specific task processing.
        """
        pass
    
    @abstractmethod
    async def generate_agent_card(self) -> Dict[str, Any]:
        """
        Generate A2A agent card advertising this agent's capabilities.
        """
        pass
    
    @abstractmethod
    async def extract_knowledge(self, data: Any) -> List[KnowledgeEntity]:
        """
        Extract structured knowledge from processed data.
        """
        pass
    
    # A2A Protocol Methods
    async def delegate_task(
        self, 
        target_agent: str, 
        skill_id: str, 
        parameters: Dict[str, Any],
        priority: int = 5,
        timeout: int = 30
    ) -> Dict[str, Any]:
        """
        Delegate a task to another agent using A2A protocol.
        """
        if not self.a2a_manager:
            raise RuntimeError("A2A manager not initialized")
        
        # Create task with unique ID and context
        task = A2ATask(
            id=f"{self.agent_id}_{datetime.utcnow().isoformat()}_{uuid.uuid4().hex[:8]}",
            skill_id=skill_id,
            agent_id=target_agent,
            parameters=parameters,
            priority=priority,
            timeout=timeout,
            collaboration_context=self._build_collaboration_context()
        )
        
        # Log the delegation decision
        self._log_decision(
            "task_delegation",
            f"Delegating {skill_id} to {target_agent}",
            {"task_id": task.id, "parameters": parameters}
        )
        
        # Execute delegation with monitoring
        start_time = datetime.utcnow()
        try:
            result = await self.a2a_manager.delegate_task(task)
            self._update_performance_metrics(start_time, success=True)
            return result
        except Exception as e:
            self._update_performance_metrics(start_time, success=False)
            self.logger.error(f"Task delegation failed: {e}")
            raise
    
    async def broadcast_knowledge(self, knowledge_entities: List[KnowledgeEntity]) -> None:
        """
        Share knowledge with other agents in the ecosystem.
        """
        if not self.a2a_manager:
            return
        
        broadcast_message = {
            "type": "knowledge_sharing",
            "source_agent": self.agent_id,
            "timestamp": datetime.utcnow().isoformat(),
            "entities": [self._serialize_knowledge_entity(entity) for entity in knowledge_entities],
            "confidence_threshold": self.config.get("knowledge_sharing_threshold", 0.7)
        }
        
        await self.a2a_manager.broadcast_to_network(broadcast_message)
        self.logger.info(f"Broadcasted {len(knowledge_entities)} knowledge entities")
    
    # MCP Tool Access Methods
    async def invoke_mcp_tool(
        self, 
        tool_name: str, 
        parameters: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Invoke an MCP tool with proper security and monitoring.
        """
        if not self.mcp_manager:
            raise RuntimeError("MCP manager not initialized")
        
        invocation = MCPToolInvocation(
            tool_name=tool_name,
            parameters=parameters,
            context=context or self._build_tool_context(),
            timeout=self.config.get("tool_timeout", 30)
        )
        
        # Log tool invocation decision
        self._log_decision(
            "tool_invocation",
            f"Invoking MCP tool: {tool_name}",
            {"parameters": parameters}
        )
        
        try:
            result = await self.mcp_manager.invoke_tool(invocation)
            self.performance_metrics["tool_invocations"] += 1
            return result
        except Exception as e:
            self.logger.error(f"MCP tool invocation failed: {e}")
            raise
    
    # Knowledge Management Methods
    async def query_knowledge(
        self, 
        query: str, 
        context: Dict[str, Any],
        confidence_threshold: float = 0.5
    ) -> List[KnowledgeEntity]:
        """
        Query the agent's knowledge base with semantic search capabilities.
        """
        relevant_entities = []
        
        for entity in self.knowledge_base.values():
            if entity.confidence_score >= confidence_threshold:
                if await self._is_relevant_to_query(entity, query, context):
                    relevant_entities.append(entity)
        
        # Sort by relevance and confidence
        return sorted(
            relevant_entities, 
            key=lambda x: (x.confidence_score, self._calculate_relevance_score(x, query)),
            reverse=True
        )
    
    async def update_knowledge(self, entity: KnowledgeEntity) -> None:
        """
        Update or add knowledge entity with proper validation and indexing.
        """
        # Validate entity before storage
        if await self._validate_knowledge_entity(entity):
            self.knowledge_base[entity.entity_id] = entity
            self.performance_metrics["knowledge_entities_created"] += 1
            
            # Update relationships and cross-references
            await self._update_knowledge_relationships(entity)
            
            # Consider sharing with other agents if confidence is high
            if entity.confidence_score >= self.config.get("auto_share_threshold", 0.8):
                await self.broadcast_knowledge([entity])
    
    # Performance and Monitoring Methods
    async def get_performance_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics for monitoring and optimization."""
        return {
            "agent_id": self.agent_id,
            "agent_type": self.agent_type.value,
            "metrics": self.performance_metrics,
            "knowledge_entities": len(self.knowledge_base),
            "trusted_agents": len(self.trusted_agents),
            "active_tasks": len(self.active_tasks),
            "decision_log_entries": len(self.decision_log)
        }
    
    # Internal Helper Methods
    def _build_collaboration_context(self) -> Dict[str, Any]:
        """Build context information for A2A collaboration."""
        return {
            "source_agent": self.agent_id,
            "agent_type": self.agent_type.value,
            "timestamp": datetime.utcnow().isoformat(),
            "knowledge_scope": list(self.knowledge_base.keys())[:10],  # Sample of knowledge
            "performance_summary": {
                "success_rate": self._calculate_success_rate(),
                "avg_response_time": self.performance_metrics["avg_response_time"]
            }
        }
    
    def _build_tool_context(self) -> Dict[str, Any]:
        """Build context information for MCP tool invocation."""
        return {
            "requesting_agent": self.agent_id,
            "agent_type": self.agent_type.value,
            "security_context": self.security_context,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def _log_decision(self, decision_type: str, description: str, details: Dict[str, Any]):
        """Log agent decisions for transparency and auditability."""
        decision_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "decision_type": decision_type,
            "description": description,
            "details": details,
            "agent_id": self.agent_id
        }
        self.decision_log.append(decision_entry)
        self.logger.info(f"Decision logged: {description}")
    
    def _update_performance_metrics(self, start_time: datetime, success: bool):
        """Update performance metrics after task completion."""
        duration = (datetime.utcnow() - start_time).total_seconds()
        self.performance_metrics["tasks_processed"] += 1
        
        if success:
            self.performance_metrics["tasks_succeeded"] += 1
        else:
            self.performance_metrics["tasks_failed"] += 1
        
        # Update average response time
        current_avg = self.performance_metrics["avg_response_time"]
        total_tasks = self.performance_metrics["tasks_processed"]
        self.performance_metrics["avg_response_time"] = (
            (current_avg * (total_tasks - 1) + duration) / total_tasks
        )
    
    def _calculate_success_rate(self) -> float:
        """Calculate the agent's task success rate."""
        total = self.performance_metrics["tasks_processed"]
        if total == 0:
            return 0.0
        return self.performance_metrics["tasks_succeeded"] / total
    
    async def _is_relevant_to_query(
        self, 
        entity: KnowledgeEntity, 
        query: str, 
        context: Dict[str, Any]
    ) -> bool:
        """Determine if a knowledge entity is relevant to a query."""
        # Simple keyword-based relevance (can be enhanced with embeddings)
        query_lower = query.lower()
        content_lower = entity.content.lower()
        
        # Check for direct keyword matches
        query_words = set(query_lower.split())
        content_words = set(content_lower.split())
        
        # Calculate overlap
        overlap = query_words & content_words
        return len(overlap) >= min(3, len(query_words) // 2)
    
    def _calculate_relevance_score(self, entity: KnowledgeEntity, query: str) -> float:
        """Calculate relevance score for ranking search results."""
        # Base score from confidence
        base_score = entity.confidence_score
        
        # Boost recent entities
        days_old = (datetime.utcnow() - entity.last_updated).days
        recency_boost = max(0, 1 - (days_old / 365))
        
        # Simple keyword matching score
        query_words = set(query.lower().split())
        content_words = set(entity.content.lower().split())
        keyword_score = len(query_words & content_words) / max(len(query_words), 1)
        
        return base_score * (1 + recency_boost * 0.2 + keyword_score * 0.3)
    
    async def _validate_knowledge_entity(self, entity: KnowledgeEntity) -> bool:
        """Validate knowledge entity before storage."""
        # Check required fields
        if not all([entity.entity_id, entity.content, entity.entity_type]):
            return False
        
        # Validate confidence score
        if not 0 <= entity.confidence_score <= 1:
            return False
        
        # Check for duplicate entities
        if entity.entity_id in self.knowledge_base:
            existing = self.knowledge_base[entity.entity_id]
            # Only update if new entity has higher confidence
            return entity.confidence_score > existing.confidence_score
        
        return True
    
    async def _update_knowledge_relationships(self, entity: KnowledgeEntity) -> None:
        """Update relationships between knowledge entities."""
        # Find entities that might be related
        for existing_id, existing_entity in self.knowledge_base.items():
            if existing_id != entity.entity_id:
                if await self._are_entities_related(entity, existing_entity):
                    # Add bidirectional relationship
                    if existing_id not in entity.relationships:
                        entity.relationships.append(existing_id)
                    if entity.entity_id not in existing_entity.relationships:
                        existing_entity.relationships.append(entity.entity_id)
    
    async def _are_entities_related(
        self, 
        entity1: KnowledgeEntity, 
        entity2: KnowledgeEntity
    ) -> bool:
        """Determine if two knowledge entities are related."""
        # Check for shared venue context
        if (entity1.venue_context and entity2.venue_context and
            entity1.venue_context.get("event_id") == entity2.venue_context.get("event_id")):
            return True
        
        # Check for content similarity
        common_words = set(entity1.content.lower().split()) & set(entity2.content.lower().split())
        return len(common_words) >= 3
    
    def _serialize_knowledge_entity(self, entity: KnowledgeEntity) -> Dict[str, Any]:
        """Serialize knowledge entity for transmission."""
        return {
            "entity_id": entity.entity_id,
            "entity_type": entity.entity_type,
            "content": entity.content,
            "confidence_score": entity.confidence_score,
            "source_agent": entity.source_agent.value,
            "source_data": entity.source_data,
            "created_at": entity.created_at.isoformat(),
            "last_updated": entity.last_updated.isoformat(),
            "relationships": entity.relationships,
            "venue_context": entity.venue_context
        }