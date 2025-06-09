#!/usr/bin/env python3
"""
GitHub Repository Setup Script for Studio338 AI Intelligence

This script initializes the GitHub repository with all necessary files
and structure for the Studio338 multi-agent system.
"""

import os
import sys
import subprocess
import json
from pathlib import Path
from datetime import datetime

# Repository configuration
REPO_NAME = "studio338-ai-intelligence"
REPO_DESCRIPTION = "Advanced multi-agent system for Studio338 venue operations using A2A+MCP protocols"
GITHUB_USERNAME = os.getenv("GITHUB_USERNAME", "your-username")

# Project structure
PROJECT_STRUCTURE = {
    "agents": {
        "base": ["__init__.py", "base_agent.py", "a2a_agent.py", "mcp_client.py", "security_context.py"],
        "studio338": {
            "email_learning_agent": ["__init__.py", "processor.py", "learner.py", "knowledge_builder.py"],
            "wotson_whatsapp_agent": ["__init__.py", "group_monitor.py", "message_analyzer.py", "urgency_detector.py"],
            "__init__.py": None,
            "core_modules.py": None
        },
        "collaboration": ["__init__.py", "a2a_protocol_manager.py", "knowledge_sharing.py", "task_delegation.py"],
        "tools": ["__init__.py", "email_mcp_server.py", "whatsapp_mcp_server.py", "knowledge_mcp_server.py"],
        "__init__.py": None
    },
    "app": {
        "routers": {
            "studio338": ["__init__.py", "emails.py", "whatsapp.py", "events.py", "operations.py"],
            "__init__.py": None,
            "agents.py": None,
            "health.py": None
        },
        "services": {
            "studio338": ["__init__.py", "venue_service.py", "event_service.py", "intelligence_service.py"],
            "__init__.py": None,
            "agent_orchestrator.py": None
        },
        "schemas": {
            "studio338": ["__init__.py", "emails.py", "whatsapp.py", "events.py", "operations.py"],
            "__init__.py": None,
            "agents.py": None
        },
        "__init__.py": None,
        "main.py": None,
        "config.py": None
    },
    "scripts": {
        "setup": ["__init__.py", "init_project.py", "configure_environment.py"],
        "agents": ["__init__.py", "initialize_agents.py", "monitor_agents.py"],
        "__init__.py": None
    },
    "docs": {
        "architecture": ["system-overview.md", "agent-design.md", "protocol-integration.md"],
        "deployment": ["production-setup.md", "local-setup.md"],
        "studio338": ["operational-guide.md", "agent-training.md"],
        "README.md": None
    },
    "tests": {
        "unit": ["__init__.py", "test_base_agents.py", "test_gateway_checker.py"],
        "integration": ["__init__.py", "test_agent_communication.py"],
        "__init__.py": None,
        "conftest.py": None
    },
    "deployment": {
        "docker": ["Dockerfile.agents", "docker-compose.yml"],
        "kubernetes": ["namespace.yaml", "deployment.yaml", "service.yaml"]
    }
}

def create_directory_structure(base_path: Path, structure: dict, level=0):
    """Recursively create directory structure with files."""
    indent = "  " * level
    
    for name, content in structure.items():
        path = base_path / name
        
        if content is None:
            # It's a file
            print(f"{indent}📄 Creating file: {name}")
            path.touch(exist_ok=True)
            
            # Add basic content to Python files
            if name.endswith('.py') and name != "__init__.py":
                with open(path, 'w') as f:
                    f.write(f'"""\n{name} - Part of Studio338 AI Intelligence System\n"""\n\n')
                    f.write('# TODO: Implement this module\n')
            elif name == "__init__.py":
                with open(path, 'w') as f:
                    f.write(f'"""Package initialization for {base_path.name}"""\n')
                    
        elif isinstance(content, list):
            # It's a directory with a list of files
            print(f"{indent}📁 Creating directory: {name}/")
            path.mkdir(exist_ok=True)
            for filename in content:
                file_path = path / filename
                print(f"{indent}  📄 Creating file: {filename}")
                file_path.touch(exist_ok=True)
                
                if filename.endswith('.py') and filename != "__init__.py":
                    with open(file_path, 'w') as f:
                        f.write(f'"""\n{filename} - Part of Studio338 AI Intelligence System\n"""\n\n')
                        f.write('# TODO: Implement this module\n')
                elif filename == "__init__.py":
                    with open(file_path, 'w') as f:
                        f.write(f'"""Package initialization for {name}"""\n')
                        
        elif isinstance(content, dict):
            # It's a directory with subdirectories
            print(f"{indent}📁 Creating directory: {name}/")
            path.mkdir(exist_ok=True)
            create_directory_structure(path, content, level + 1)

def create_requirements_file(base_path: Path):
    """Create requirements.txt with necessary dependencies."""
    requirements = """# Core dependencies
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
python-dotenv==1.0.0

# AI/ML dependencies
spacy==3.7.2
transformers==4.35.2
torch==2.1.1
scikit-learn==1.3.2
numpy==1.26.2

# Communication protocols
websockets==12.0
httpx==0.25.2
aiohttp==3.9.1

# Database
sqlalchemy==2.0.23
alembic==1.12.1
asyncpg==0.29.0

# Email processing
imaplib2==3.6
email-validator==2.1.0

# WhatsApp integration
# Note: Actual WhatsApp integration will depend on your chosen solution
# whatsapp-web-api==1.0.0  # Example, adjust based on actual implementation

# Monitoring and logging
prometheus-client==0.19.0
structlog==23.2.0

# Testing
pytest==7.4.3
pytest-asyncio==0.21.1
pytest-cov==4.1.0

# Development
black==23.11.0
flake8==6.1.0
mypy==1.7.1
pre-commit==3.5.0
"""
    
    with open(base_path / "requirements.txt", 'w') as f:
        f.write(requirements)
    print("✅ Created requirements.txt")

def create_env_example(base_path: Path):
    """Create .env.example file with configuration template."""
    env_example = """# Studio338 AI Intelligence Configuration

# Agent Configuration
ELA_AGENT_ID=ela-studio338-001
WOTSON_AGENT_ID=wotson-studio338-001

# Email Configuration (iCloud)
ICLOUD_EMAIL=your-email@icloud.com
ICLOUD_APP_PASSWORD=your-app-specific-password
IMAP_SERVER=imap.mail.me.com
IMAP_PORT=993

# WhatsApp Configuration
WHATSAPP_API_URL=http://localhost:3000
WHATSAPP_API_TOKEN=your-whatsapp-api-token

# Storage Configuration (External Drive)
EXTERNAL_DRIVE_PATH=/Volumes/Studio338Data
DATABASE_PATH=/Volumes/Studio338Data/studio338.db
KNOWLEDGE_GRAPH_PATH=/Volumes/Studio338Data/knowledge_graph

# MCP Server Configuration
EMAIL_MCP_SERVER=http://localhost:8001
NLP_MCP_SERVER=http://localhost:8002
KNOWLEDGE_MCP_SERVER=http://localhost:8003
VENUE_MCP_SERVER=http://localhost:8004
WHATSAPP_MCP_SERVER=http://localhost:8005

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_BASE_URL=http://localhost:8000

# Security
SECRET_KEY=your-secret-key-change-this
API_KEY=your-api-key-for-external-access

# Logging
LOG_LEVEL=INFO
LOG_FILE=/Volumes/Studio338Data/logs/studio338.log

# Performance
WORKER_COUNT=4
MAX_CONNECTIONS=100
POLL_INTERVAL=5

# Studio338 Specific
VENUE_NAME=Studio338
KEY_PERSONNEL=Alice Johnson,Bob Smith,Charlie Brown
EQUIPMENT_CATEGORIES=audio,lighting,staging,power,safety
"""
    
    with open(base_path / ".env.example", 'w') as f:
        f.write(env_example)
    print("✅ Created .env.example")

def create_gitignore(base_path: Path):
    """Create .gitignore file."""
    gitignore = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
ENV/
.venv

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# Environment
.env
.env.local
.env.*.local

# Logs
logs/
*.log

# Database
*.db
*.sqlite
*.sqlite3

# External drive data (should not be committed)
/Volumes/
external_data/

# OS
.DS_Store
Thumbs.db

# Testing
.coverage
.pytest_cache/
htmlcov/

# Build
build/
dist/
*.egg-info/

# Documentation build
docs/_build/

# Temporary files
*.tmp
*.temp
.cache/

# Security
*.pem
*.key
secrets/
"""
    
    with open(base_path / ".gitignore", 'w') as f:
        f.write(gitignore)
    print("✅ Created .gitignore")

def create_docker_compose(base_path: Path):
    """Create docker-compose.yml for local development."""
    docker_compose = """version: '3.8'

services:
  # Main API service
  api:
    build:
      context: .
      dockerfile: deployment/docker/Dockerfile.api
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://studio338:password@db:5432/studio338
    volumes:
      - ./app:/app/app
      - ./agents:/app/agents
      - /Volumes/Studio338Data:/data
    depends_on:
      - db
      - redis

  # PostgreSQL database
  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: studio338
      POSTGRES_PASSWORD: password
      POSTGRES_DB: studio338
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  # Redis for caching and pub/sub
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  # MCP Email Server
  mcp-email:
    build:
      context: .
      dockerfile: deployment/docker/Dockerfile.mcp
    command: python -m agents.tools.email_mcp_server
    ports:
      - "8001:8001"
    volumes:
      - /Volumes/Studio338Data:/data

  # MCP WhatsApp Server
  mcp-whatsapp:
    build:
      context: .
      dockerfile: deployment/docker/Dockerfile.mcp
    command: python -m agents.tools.whatsapp_mcp_server
    ports:
      - "8005:8005"
    volumes:
      - /Volumes/Studio338Data:/data

  # Agent: ELA
  agent-ela:
    build:
      context: .
      dockerfile: deployment/docker/Dockerfile.agents
    command: python -m agents.studio338.email_learning_agent
    environment:
      - AGENT_TYPE=EMAIL_LEARNING
    volumes:
      - /Volumes/Studio338Data:/data
    depends_on:
      - api
      - mcp-email

  # Agent: WOTSON
  agent-wotson:
    build:
      context: .
      dockerfile: deployment/docker/Dockerfile.agents
    command: python -m agents.studio338.wotson_whatsapp_agent
    environment:
      - AGENT_TYPE=WHATSAPP_MONITOR
    volumes:
      - /Volumes/Studio338Data:/data
    depends_on:
      - api
      - mcp-whatsapp

volumes:
  postgres_data:
"""
    
    deployment_dir = base_path / "deployment" / "docker"
    deployment