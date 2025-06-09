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
    deployment_dir.mkdir(parents=True, exist_ok=True)
    
    with open(base_path / "docker-compose.yml", 'w') as f:
        f.write(docker_compose)
    print("✅ Created docker-compose.yml")

def create_main_app(base_path: Path):
    """Create main FastAPI application file."""
    main_py = '''"""
Main FastAPI application for Studio338 AI Intelligence System
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import logging
from contextlib import asynccontextmanager

from app.config import settings
from app.routers import agents, health
from app.routers.studio338 import emails, whatsapp, events, operations
from app.services.agent_orchestrator import AgentOrchestrator

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global agent orchestrator instance
orchestrator = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle application startup and shutdown."""
    global orchestrator
    
    # Startup
    logger.info("Starting Studio338 AI Intelligence System...")
    
    # Initialize agent orchestrator
    orchestrator = AgentOrchestrator(settings)
    await orchestrator.initialize()
    
    # Start agents
    await orchestrator.start_all_agents()
    
    logger.info("System initialized successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Studio338 AI Intelligence System...")
    await orchestrator.shutdown()
    logger.info("System shutdown complete")

# Create FastAPI app
app = FastAPI(
    title="Studio338 AI Intelligence",
    description="Advanced multi-agent system for venue operations",
    version="2.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix="/health", tags=["health"])
app.include_router(agents.router, prefix="/api/v1/agents", tags=["agents"])
app.include_router(emails.router, prefix="/api/v1/studio338/emails", tags=["studio338-emails"])
app.include_router(whatsapp.router, prefix="/api/v1/studio338/whatsapp", tags=["studio338-whatsapp"])
app.include_router(events.router, prefix="/api/v1/studio338/events", tags=["studio338-events"])
app.include_router(operations.router, prefix="/api/v1/studio338/operations", tags=["studio338-operations"])

@app.get("/")
async def root():
    """Root endpoint with system information."""
    return {
        "name": "Studio338 AI Intelligence System",
        "version": "2.0.0",
        "status": "operational",
        "agents": {
            "ela": "Email Learning Agent",
            "wotson": "WhatsApp Operations Intelligence"
        },
        "documentation": "/docs"
    }

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for unhandled errors."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "type": type(exc).__name__
        }
    )

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG,
        workers=settings.WORKER_COUNT if not settings.DEBUG else 1
    )
'''
    
    app_dir = base_path / "app"
    app_dir.mkdir(exist_ok=True)
    
    with open(app_dir / "main.py", 'w') as f:
        f.write(main_py)
    print("✅ Created app/main.py")

def create_config_file(base_path: Path):
    """Create configuration management file."""
    config_py = '''"""
Configuration management for Studio338 AI Intelligence System
"""

from pydantic_settings import BaseSettings
from typing import List, Optional
import os
from pathlib import Path

class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # Application
    APP_NAME: str = "Studio338 AI Intelligence"
    VERSION: str = "2.0.0"
    DEBUG: bool = False
    
    # API Configuration
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_BASE_URL: str = "http://localhost:8000"
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    
    # Agent Configuration
    ELA_AGENT_ID: str = "ela-studio338-001"
    WOTSON_AGENT_ID: str = "wotson-studio338-001"
    
    # Email Configuration
    ICLOUD_EMAIL: str
    ICLOUD_APP_PASSWORD: str
    IMAP_SERVER: str = "imap.mail.me.com"
    IMAP_PORT: int = 993
    
    # WhatsApp Configuration
    WHATSAPP_API_URL: str = "http://localhost:3000"
    WHATSAPP_API_TOKEN: Optional[str] = None
    
    # Storage Configuration
    EXTERNAL_DRIVE_PATH: Path = Path("/Volumes/Studio338Data")
    DATABASE_PATH: Path = Path("/Volumes/Studio338Data/studio338.db")
    KNOWLEDGE_GRAPH_PATH: Path = Path("/Volumes/Studio338Data/knowledge_graph")
    
    # MCP Servers
    EMAIL_MCP_SERVER: str = "http://localhost:8001"
    NLP_MCP_SERVER: str = "http://localhost:8002"
    KNOWLEDGE_MCP_SERVER: str = "http://localhost:8003"
    VENUE_MCP_SERVER: str = "http://localhost:8004"
    WHATSAPP_MCP_SERVER: str = "http://localhost:8005"
    
    # Security
    SECRET_KEY: str
    API_KEY: Optional[str] = None
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: Optional[Path] = None
    
    # Performance
    WORKER_COUNT: int = 4
    MAX_CONNECTIONS: int = 100
    POLL_INTERVAL: int = 5
    
    # Studio338 Specific
    VENUE_NAME: str = "Studio338"
    KEY_PERSONNEL: List[str] = []
    EQUIPMENT_CATEGORIES: List[str] = ["audio", "lighting", "staging", "power", "safety"]
    
    # Known Events (can be loaded from file or database)
    KNOWN_EVENTS: dict = {}
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Parse comma-separated lists
        if isinstance(self.KEY_PERSONNEL, str):
            self.KEY_PERSONNEL = [p.strip() for p in self.KEY_PERSONNEL.split(',')]
        if isinstance(self.EQUIPMENT_CATEGORIES, str):
            self.EQUIPMENT_CATEGORIES = [c.strip() for c in self.EQUIPMENT_CATEGORIES.split(',')]
        
        # Ensure directories exist
        self.EXTERNAL_DRIVE_PATH.mkdir(parents=True, exist_ok=True)
        if self.LOG_FILE:
            self.LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        
        # Load known events from file if exists
        events_file = self.EXTERNAL_DRIVE_PATH / "known_events.json"
        if events_file.exists():
            import json
            with open(events_file) as f:
                self.KNOWN_EVENTS = json.load(f)

# Create global settings instance
settings = Settings()
'''
    
    with open(base_path / "app" / "config.py", 'w') as f:
        f.write(config_py)
    print("✅ Created app/config.py")

def initialize_git_repository(base_path: Path):
    """Initialize git repository and make initial commit."""
    try:
        # Initialize git
        subprocess.run(["git", "init"], cwd=base_path, check=True)
        print("✅ Initialized git repository")
        
        # Add all files
        subprocess.run(["git", "add", "."], cwd=base_path, check=True)
        
        # Initial commit
        subprocess.run(
            ["git", "commit", "-m", "Initial commit: Studio338 AI Intelligence System structure"],
            cwd=base_path,
            check=True
        )
        print("✅ Created initial commit")
        
        # Add origin (user needs to create repo on GitHub first)
        print(f"\n📌 Next steps:")
        print(f"1. Create a new repository on GitHub: {REPO_NAME}")
        print(f"2. Run these commands:")
        print(f"   git remote add origin https://github.com/{GITHUB_USERNAME}/{REPO_NAME}.git")
        print(f"   git branch -M main")
        print(f"   git push -u origin main")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Git initialization failed: {e}")
        print("   You may need to install git or configure it properly")

def create_initial_docs(base_path: Path):
    """Create initial documentation files."""
    
    # System Overview
    system_overview = """# Studio338 AI Intelligence System - Architecture Overview

## Introduction

The Studio338 AI Intelligence System is an advanced multi-agent platform designed specifically for venue operations management. It combines email intelligence, WhatsApp monitoring, and collaborative AI agents to provide comprehensive operational insights and real-time decision support.

## Core Components

### 1. Intelligent Agents

#### ELA (Email Learning Agent)
- Processes historical email communications
- Builds institutional knowledge from past interactions
- Identifies operational patterns and procedures
- Provides historical context for decision-making

#### WOTSON (WhatsApp Operations Intelligence)
- Monitors venue WhatsApp groups in real-time
- Detects urgent situations and equipment issues
- Tracks personnel and resource availability
- Coordinates immediate responses

### 2. Communication Protocols

#### A2A (Agent-to-Agent) Protocol
- Enables direct agent collaboration
- Standardized task delegation
- Knowledge sharing between agents
- Consensus building for complex decisions

#### MCP (Model Context Protocol)
- Provides tool access abstraction
- Standardized resource management
- Security and access control
- Performance monitoring

### 3. Core Modules

#### Gateway Checker
- Categorizes communications by event/promoter
- Uses explicit, traceable decision logic
- Creates new categories dynamically
- Maintains decision audit trail

#### Event Index
- Centralized data storage
- Chronological organization
- Cross-reference between sources
- Quick search and retrieval

## Data Flow

1. **Input Sources**
   - Email (iCloud via IMAP)
   - WhatsApp (via local API bridge)
   
2. **Processing**
   - Real-time analysis (WOTSON)
   - Historical learning (ELA)
   - Pattern recognition
   - Urgency detection
   
3. **Knowledge Building**
   - Entity extraction
   - Relationship mapping
   - Confidence scoring
   - Cross-validation
   
4. **Output**
   - Operational insights
   - Urgent alerts
   - Decision recommendations
   - Performance metrics

## Deployment Architecture

The system runs entirely on local infrastructure:
- macOS host system
- External drive for data storage
- Local API bridges for communication
- No cloud dependencies for core operations

## Security Model

- All processing occurs locally
- Encrypted storage on external drive
- API key authentication
- Audit logging for all decisions
- GDPR-compliant data handling
"""
    
    docs_arch_dir = base_path / "docs" / "architecture"
    docs_arch_dir.mkdir(parents=True, exist_ok=True)
    
    with open(docs_arch_dir / "system-overview.md", 'w') as f:
        f.write(system_overview)
    print("✅ Created docs/architecture/system-overview.md")
    
    # Local Setup Guide
    local_setup = """# Local Development Setup Guide

## Prerequisites

- macOS (latest version recommended)
- Python 3.11 or higher
- External drive mounted at `/Volumes/Studio338Data`
- Access to Studio338 email accounts
- WhatsApp Business API credentials

## Step 1: Clone Repository

```bash
git clone https://github.com/{}/studio338-ai-intelligence.git
cd studio338-ai-intelligence
```

## Step 2: Python Environment

```bash
# Create virtual environment
python -m venv venv

# Activate environment
source venv/bin/activate  # On macOS

# Install dependencies
pip install -r requirements.txt

# Install spaCy language model
python -m spacy download en_core_web_sm
```

## Step 3: Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your credentials
nano .env
```

Required configuration:
- `ICLOUD_EMAIL`: Your iCloud email address
- `ICLOUD_APP_PASSWORD`: App-specific password for iCloud
- `WHATSAPP_API_TOKEN`: Your WhatsApp API credentials
- `SECRET_KEY`: Generate a secure secret key

## Step 4: External Drive Setup

Ensure your external drive is mounted at `/Volumes/Studio338Data`:

```bash
# Create necessary directories
mkdir -p /Volumes/Studio338Data/logs
mkdir -p /Volumes/Studio338Data/knowledge_graph
mkdir -p /Volumes/Studio338Data/event_data
```

## Step 5: Database Initialization

```bash
# Run database migrations
alembic upgrade head

# Initialize agent data
python scripts/setup/init_project.py
```

## Step 6: Start Services

### Option A: Direct Python

```bash
# Terminal 1: Start API server
python -m app.main

# Terminal 2: Start ELA agent
python -m agents.studio338.email_learning_agent

# Terminal 3: Start WOTSON agent
python -m agents.studio338.wotson_whatsapp_agent
```

### Option B: Docker Compose

```bash
# Build and start all services
docker-compose up --build
```

## Step 7: Verify Installation

1. Check API health: http://localhost:8000/health
2. View API docs: http://localhost:8000/docs
3. Check agent status: http://localhost:8000/api/v1/agents/status

## Troubleshooting

### External Drive Not Found
- Ensure drive is mounted at correct path
- Check permissions: `ls -la /Volumes/Studio338Data`

### Email Connection Issues
- Verify app-specific password is correct
- Check IMAP is enabled in iCloud settings
- Test connection: `python scripts/test_email_connection.py`

### WhatsApp Connection Issues
- Verify API endpoint is accessible
- Check authentication token
- Review WhatsApp API logs

## Next Steps

1. Import historical email data: `python scripts/import_email_history.py`
2. Configure known events: Edit `/Volumes/Studio338Data/known_events.json`
3. Start monitoring WhatsApp groups
4. Access dashboard at http://localhost:3000 (when implemented)
""".format(GITHUB_USERNAME)
    
    docs_deploy_dir = base_path / "docs" / "deployment"
    docs_deploy_dir.mkdir(parents=True, exist_ok=True)
    
    with open(docs_deploy_dir / "local-setup.md", 'w') as f:
        f.write(local_setup)
    print("✅ Created docs/deployment/local-setup.md")

def main():
    """Main setup function."""
    print("🚀 Studio338 AI Intelligence - GitHub Repository Setup")
    print("=" * 50)
    
    # Get current directory
    base_path = Path.cwd()
    
    # Create project directory if needed
    project_path = base_path / REPO_NAME
    if project_path.exists():
        response = input(f"⚠️  Directory {REPO_NAME} already exists. Continue? (y/n): ")
        if response.lower() != 'y':
            print("❌ Setup cancelled")
            return
    else:
        project_path.mkdir()
        print(f"✅ Created project directory: {REPO_NAME}")
    
    # Change to project directory
    os.chdir(project_path)
    
    # Create directory structure
    print("\n📁 Creating directory structure...")
    create_directory_structure(project_path, PROJECT_STRUCTURE)
    
    # Create essential files
    print("\n📄 Creating essential files...")
    create_requirements_file(project_path)
    create_env_example(project_path)
    create_gitignore(project_path)
    create_docker_compose(project_path)
    create_main_app(project_path)
    create_config_file(project_path)
    create_initial_docs(project_path)
    
    # Copy existing artifacts if provided
    print("\n📋 Note: Copy the following files from the artifacts:")
    print("   - agents/base/base_agent.py")
    print("   - agents/studio338/wotson_whatsapp_agent.py")
    print("   - agents/studio338/core_modules.py")
    print("   - README.md")
    
    # Initialize git repository
    print("\n🔧 Initializing git repository...")
    initialize_git_repository(project_path)
    
    print("\n✅ Setup complete!")
    print(f"\n📂 Project created at: {project_path}")
    print("\n🎯 Next steps:")
    print("1. Copy the artifact files to their respective locations")
    print("2. Create the GitHub repository online")
    print("3. Push the code to GitHub")
    print("4. Follow the local setup guide in docs/deployment/local-setup.md")

if __name__ == "__main__":
    main()