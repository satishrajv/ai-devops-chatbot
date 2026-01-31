# 📚 AI DevOps Platform - Documentation Index

**Complete guide to all documentation in this project**

Welcome to the AI DevOps Platform documentation! This index will help you find the right documentation for your needs.

---

## 🎯 Quick Navigation

### For New Users
1. [Getting Started](#getting-started) - Start here!
2. [Installation Guide](#installation)
3. [Docker Compose Guide](#docker-deployment)

### For Developers
1. [Architecture Overview](#architecture)
2. [Development Guide](#development)
3. [API Reference](#api-reference)

### For DevOps Engineers
1. [Deployment Guide](#deployment)
2. [Configuration Reference](#configuration)
3. [Monitoring & Logging](#monitoring)

---

## 📖 Documentation Structure

```
AI-DevOps-chatbot/
├── README.md                          # 👈 Start here - Main project overview
├── DOCUMENTATION_INDEX.md             # 👈 This file
│
├── 🔧 Setup & Installation
│   ├── DOCKER_COMPOSE_GUIDE.md       # Complete Docker Compose guide
│   ├── INTEGRATION_README.md          # RAG integration guide
│   └── DEPENDENCIES.md                # Dependency explanations
│
├── 🔒 Security
│   └── SECURITY_WARNING.md            # Critical security fixes and best practices
│
├── 🏗️ Architecture & Design
│   ├── kb-rag/ARCHITECTURE.md         # RAG system architecture
│   ├── kb-rag/LANGGRAPH_ARCHITECTURE.md  # LangGraph multi-agent design
│   └── kb-rag/CHATBOT_README.md       # RAG chatbot implementation
│
├── 🛠️ Configuration & Customization
│   ├── kb-rag/PROMPTS_README.md       # LLM prompt management
│   ├── kb-rag/LOGGING_GUIDE.md        # Logging system guide
│   └── kb-sync/README.md              # KB sync system guide
│
├── 📦 Application-Specific Docs
│   ├── flask_app/README.md            # Flask API documentation
│   └── streamlit_app/README.md        # Streamlit dashboard guide (if exists)
│
└── 📋 Knowledge Base
    └── docs/                          # Knowledge base articles
        └── jenkins-error-kb-001-outofmemory.md
```

---

## 🚀 Getting Started

### For Absolute Beginners

**Read in this order**:

1. **[README.md](README.md)** (5 min read)
   - Project overview
   - What this platform does
   - Key features

2. **[DEPENDENCIES.md](DEPENDENCIES.md)** (3 min read)
   - What technologies are used
   - Why we chose them

3. **[DOCKER_COMPOSE_GUIDE.md](DOCKER_COMPOSE_GUIDE.md)** (10 min read)
   - How to run everything with Docker
   - Quick start commands
   - Troubleshooting

4. **[SECURITY_WARNING.md](SECURITY_WARNING.md)** (5 min read) ⚠️
   - **CRITICAL**: Security setup
   - Credential management
   - Never skip this!

**Total Time**: ~25 minutes to get started

---

## 📦 Installation

### Quick Start (Docker - Recommended)

**File**: [DOCKER_COMPOSE_GUIDE.md](DOCKER_COMPOSE_GUIDE.md)

**What you'll learn**:
- Running all services with one command
- Configuration with environment variables
- Common troubleshooting

**Quick commands**:
```bash
cp streamlit_app/.env.example .env
# Edit .env with your credentials
docker-compose up -d
```

### Manual Installation

**File**: [INTEGRATION_README.md](INTEGRATION_README.md)

**What you'll learn**:
- Installing each component separately
- Python virtual environment setup
- Weaviate setup
- Testing individual components

**When to use**: Custom deployment or development setup

---

## 🏗️ Architecture

### System Architecture Overview

**File**: [kb-rag/ARCHITECTURE.md](kb-rag/ARCHITECTURE.md)

**What you'll learn**:
- High-level system design
- How RAG (Retrieval-Augmented Generation) works
- Component interactions
- Data flow diagrams

**Who should read**: Developers, architects, technical stakeholders

**Visual aids**: ✅ Includes diagrams

---

### LangGraph Multi-Agent Architecture

**File**: [kb-rag/LANGGRAPH_ARCHITECTURE.md](kb-rag/LANGGRAPH_ARCHITECTURE.md)

**What you'll learn**:
- How the 3-agent system works
  1. Query Processor Agent
  2. RAG Retriever Agent
  3. Answer Generator Agent
- Agent orchestration with LangGraph
- State management
- Workflow diagrams

**Who should read**: AI/ML engineers, backend developers

**Visual aids**: ✅ Includes Mermaid diagrams and execution flow

---

### RAG Chatbot Implementation

**File**: [kb-rag/CHATBOT_README.md](kb-rag/CHATBOT_README.md)

**What you'll learn**:
- RAG chatbot UI and backend
- Integration with Streamlit dashboard
- Query processing pipeline
- Response generation

**Who should read**: Frontend developers, UX designers, product managers

---

## 🛠️ Development

### Working with LLM Prompts

**File**: [kb-rag/PROMPTS_README.md](kb-rag/PROMPTS_README.md)

**What you'll learn**:
- Centralized prompt management
- Available prompt templates
- Customizing system prompts
- A/B testing prompts
- Question type detection

**Who should read**: AI engineers, prompt engineers, anyone modifying chatbot behavior

**Quick example**:
```python
# All prompts in prompts.py
from prompts import SYSTEM_PROMPT_DEVOPS_ASSISTANT

# Customize behavior easily
SYSTEM_PROMPT_DEVOPS_ASSISTANT = """Your custom prompt..."""
```

---

### Logging System

**File**: [kb-rag/LOGGING_GUIDE.md](kb-rag/LOGGING_GUIDE.md)

**What you'll learn**:
- Logging configuration
- Log levels and when to use them
- Reading log files
- Debugging with logs
- Performance monitoring

**Who should read**: All developers

**Log locations**:
- `kb-rag/logs/rag_YYYYMMDD_HHMMSS.log`
- `kb-rag/logs/langgraph_YYYYMMDD_HHMMSS.log`

---

### KB Sync System

**File**: [kb-sync/README.md](kb-sync/README.md)

**What you'll learn**:
- Multi-agent knowledge base synchronization
- S3 to Weaviate pipeline
- State tracking with SQLite
- Incremental sync strategy

**Who should read**: Backend developers, DevOps engineers

**Components**:
- S3 Fetcher Agent
- Text Processor Agent
- Embedding Agent
- Vector Store Agent
- State Manager Agent

---

## ⚙️ Configuration

### Environment Variables

**Files**:
- `streamlit_app/.env.example` - Streamlit app configuration
- `kb-sync/.env.example` - KB sync configuration
- `kb-rag/.env.template` - RAG system configuration

**Required variables**:
```bash
JENKINS_URL=http://your-jenkins:8080
JENKINS_USER=admin
JENKINS_TOKEN=your_token
OPENAI_API_KEY=sk-...
WEAVIATE_URL=http://localhost:8080
WEAVIATE_API_KEY=your_key
```

**Documentation**: [SECURITY_WARNING.md](SECURITY_WARNING.md) - Secure credential management

---

### Application Settings

**RAG System**: `kb-rag/config.py`
```python
LLM_MODEL = "gpt-4o-mini"
TEMPERATURE = 0.3
TOP_K_CHUNKS = 5
SIMILARITY_THRESHOLD = 0.7
```

**KB Sync**: `kb-sync/config/settings.py`
```python
S3_KB_BUCKET = "jenkins-kb"
EMBEDDING_DIMENSION = 1536
SYNC_INTERVAL_HOURS = 24
```

---

## 🔒 Security

### Security Best Practices

**File**: [SECURITY_WARNING.md](SECURITY_WARNING.md)

**Critical topics**:
- ⚠️ Exposed credentials remediation (MUST READ)
- Credential rotation checklist
- Git repository cleanup
- Pre-commit hooks
- .gitignore best practices
- Secrets management

**Immediate actions required**:
1. Rotate exposed credentials
2. Remove .env from git tracking
3. Set up environment variables
4. Install pre-commit hooks

**Priority**: 🔴 HIGH - Read immediately if setting up the project

---

## 🐳 Docker Deployment

### Complete Docker Guide

**File**: [DOCKER_COMPOSE_GUIDE.md](DOCKER_COMPOSE_GUIDE.md)

**Comprehensive coverage**:
- Quick start (5 minutes to running)
- Service overview (6 services)
- Configuration with .env
- Usage examples
- Docker Compose profiles
- Common commands
- Troubleshooting (6 common issues)
- Production deployment checklist

**Services**:
- `flask-api` (port 5001)
- `streamlit-app` (port 8501)
- `weaviate` (port 8080)
- `jenkins` (optional, port 8082)
- `rag-chatbot` (optional, port 8502)
- `kb-sync` (optional, background)

**Common commands**:
```bash
docker-compose up -d                    # Start core services
docker-compose --profile rag-ui up -d   # Include RAG chatbot
docker-compose logs -f                  # View logs
docker-compose down                     # Stop all
```

---

## 📱 Applications

### Flask API Backend

**File**: [flask_app/README.md](flask_app/README.md)

**What you'll learn**:
- REST API endpoints
- Request/response formats
- Error handling
- Testing the API

**Endpoints**:
- `GET /health` - Health check
- Additional endpoints documented in README

**Running**:
```bash
cd flask_app
pip install -r requirements.txt
python app.py
```

---

### Streamlit Dashboard

**File**: [streamlit_app/app.py](streamlit_app/app.py) (code)

**Features**:
- Jenkins pipeline monitoring
- Build triggering
- RAG chatbot integration
- Real-time status updates

**Running**:
```bash
cd streamlit_app
pip install -r requirements.txt
streamlit run app.py
```

**Access**: http://localhost:8501

---

## 🔍 Monitoring & Logging

### Logging

**File**: [kb-rag/LOGGING_GUIDE.md](kb-rag/LOGGING_GUIDE.md)

**Log files**:
- RAG system: `kb-rag/logs/rag_*.log`
- LangGraph: `kb-rag/logs/langgraph_*.log`

**Log levels**:
- DEBUG: Detailed diagnostic info
- INFO: General informational messages
- WARNING: Warning messages
- ERROR: Error messages
- CRITICAL: Critical errors

**Viewing logs**:
```bash
# Latest RAG log
ls -lt kb-rag/logs/rag_*.log | head -1 | xargs tail -f

# Latest LangGraph log
ls -lt kb-rag/logs/langgraph_*.log | head -1 | xargs tail -f

# Docker logs
docker-compose logs -f streamlit-app
```

---

### Health Checks

**Endpoints**:
```bash
# Flask API
curl http://localhost:5001/health

# Streamlit
curl http://localhost:8501/_stcore/health

# Weaviate
curl http://localhost:8080/v1/.well-known/ready
```

**Docker health**:
```bash
docker-compose ps  # Shows health status
docker inspect <container_id> --format='{{.State.Health.Status}}'
```

---

## 📋 Knowledge Base

### KB Articles

**Location**: `docs/`

**Current articles**:
1. `jenkins-error-kb-001-outofmemory.md` - OutOfMemoryError troubleshooting

**Adding new articles**:
1. Create markdown file in `docs/`
2. Follow naming convention: `jenkins-error-kb-###-description.md`
3. Upload to S3 bucket (if using kb-sync)
4. Run kb-sync to index: `docker-compose --profile kb-sync up -d`

**Article template**:
```markdown
# Error: [Error Name]

## Symptoms
- [List of symptoms]

## Causes
- [Root causes]

## Solution
1. [Step-by-step fix]

## Prevention
- [How to prevent]
```

---

## 🔧 Troubleshooting

### Common Issues & Solutions

**Docker issues**: [DOCKER_COMPOSE_GUIDE.md - Troubleshooting](DOCKER_COMPOSE_GUIDE.md#troubleshooting)

**Security issues**: [SECURITY_WARNING.md](SECURITY_WARNING.md)

**Logging issues**: [kb-rag/LOGGING_GUIDE.md](kb-rag/LOGGING_GUIDE.md)

**Integration issues**: [INTEGRATION_README.md](INTEGRATION_README.md)

### Getting Help

**Check logs first**:
```bash
# Application logs
docker-compose logs -f

# Specific service
docker-compose logs streamlit-app

# RAG system logs
cat kb-rag/logs/rag_*.log
```

**Common error patterns**:
1. **Connection refused**: Check service is running, correct URL
2. **401 Unauthorized**: Check credentials in .env
3. **Module not found**: Install dependencies, check virtual environment
4. **Port already in use**: Change port in docker-compose.yml

---

## 🎓 Learning Paths

### Path 1: DevOps Engineer (Focus: Deployment)

**Recommended reading order**:
1. README.md - Overview
2. DOCKER_COMPOSE_GUIDE.md - Deployment
3. SECURITY_WARNING.md - Security setup
4. INTEGRATION_README.md - Manual deployment
5. kb-rag/LOGGING_GUIDE.md - Monitoring

**Time**: ~1.5 hours

---

### Path 2: Backend Developer (Focus: Code)

**Recommended reading order**:
1. README.md - Overview
2. DEPENDENCIES.md - Tech stack
3. kb-rag/ARCHITECTURE.md - System design
4. kb-rag/LANGGRAPH_ARCHITECTURE.md - Agent system
5. kb-rag/PROMPTS_README.md - Prompt engineering
6. kb-rag/LOGGING_GUIDE.md - Debugging

**Time**: ~2 hours

---

### Path 3: ML Engineer (Focus: RAG/AI)

**Recommended reading order**:
1. README.md - Overview
2. DEPENDENCIES.md - AI stack (OpenAI, Weaviate)
3. kb-rag/ARCHITECTURE.md - RAG architecture
4. kb-rag/LANGGRAPH_ARCHITECTURE.md - Multi-agent system
5. kb-rag/CHATBOT_README.md - Chatbot implementation
6. kb-rag/PROMPTS_README.md - Prompt management
7. kb-sync/README.md - KB sync pipeline

**Time**: ~2.5 hours

---

### Path 4: Frontend Developer (Focus: UI)

**Recommended reading order**:
1. README.md - Overview
2. DOCKER_COMPOSE_GUIDE.md - Running locally
3. kb-rag/CHATBOT_README.md - Chatbot UI
4. streamlit_app/app.py - Dashboard code
5. flask_app/README.md - API reference

**Time**: ~1 hour

---

## 📊 Documentation Health

### Documentation Coverage

| Component | Documentation | Status |
|-----------|---------------|--------|
| Setup & Installation | ✅ Complete | DOCKER_COMPOSE_GUIDE.md, INTEGRATION_README.md |
| Security | ✅ Complete | SECURITY_WARNING.md |
| Architecture | ✅ Complete | Multiple architecture docs |
| Configuration | ✅ Complete | PROMPTS_README.md, config files |
| Logging | ✅ Complete | LOGGING_GUIDE.md |
| Troubleshooting | ✅ Good | Covered in multiple docs |
| API Reference | ⚠️ Partial | flask_app/README.md |
| Testing | ⚠️ Minimal | Not fully documented |
| Contributing | ❌ Missing | No CONTRIBUTING.md yet |

---

## 🔄 Keeping Documentation Updated

### When to Update Docs

**After adding features**:
- Update relevant architecture docs
- Add new configuration options
- Update example commands

**After fixing bugs**:
- Add to troubleshooting section
- Update known issues

**After changing APIs**:
- Update API reference
- Update code examples
- Update integration guides

### Documentation Standards

**Markdown formatting**:
- Use headers for sections (##, ###)
- Include code blocks with language tags
- Add emoji for visual navigation (optional)
- Include table of contents for long docs

**Code examples**:
- Always test code examples
- Include expected output
- Show both success and error cases

**Screenshots/Diagrams**:
- Store in `docs/images/` or `kb-rag/images/`
- Use descriptive filenames
- Compress for web use

---

## 🎯 Quick Reference Cards

### For Daily Development

**Files to bookmark**:
- kb-rag/config.py - Settings
- kb-rag/prompts.py - LLM prompts
- kb-rag/LOGGING_GUIDE.md - Debugging
- DOCKER_COMPOSE_GUIDE.md - Docker commands

**Common commands**:
```bash
# Start dev environment
docker-compose up -d

# View logs
docker-compose logs -f streamlit-app

# Restart after code changes
docker-compose restart streamlit-app

# Check health
docker-compose ps
```

---

### For Deployment

**Files to bookmark**:
- DOCKER_COMPOSE_GUIDE.md - Production deployment
- SECURITY_WARNING.md - Security checklist
- .env.example files - Configuration templates

**Deployment checklist**:
- [ ] Set production environment variables
- [ ] Enable authentication
- [ ] Configure HTTPS
- [ ] Set resource limits
- [ ] Enable monitoring
- [ ] Configure backups

---

### For Troubleshooting

**First steps**:
1. Check logs: `docker-compose logs -f`
2. Check health: `docker-compose ps`
3. Verify config: `cat .env`
4. Test connectivity: `curl` health endpoints

**Documentation references**:
- Docker issues: DOCKER_COMPOSE_GUIDE.md#troubleshooting
- Security: SECURITY_WARNING.md
- Logging: kb-rag/LOGGING_GUIDE.md

---

## 📞 Support & Contribution

### Getting Support

**Documentation not helpful?**
1. Check troubleshooting sections
2. Search existing issues (GitHub/GitLab)
3. Review logs for error messages
4. Create detailed issue report

**Issue template**:
```
**Issue**: Brief description

**Environment**:
- OS: Windows/macOS/Linux
- Docker version: X.X.X
- Python version: 3.X

**Steps to reproduce**:
1. Step 1
2. Step 2

**Expected behavior**: What should happen

**Actual behavior**: What actually happens

**Logs**: Relevant log excerpts

**Configuration**: Relevant config (sanitize secrets!)
```

---

## ✅ Documentation Checklist

### Before Deploying

- [ ] Read SECURITY_WARNING.md
- [ ] Configure .env files
- [ ] Review docker-compose.yml
- [ ] Test with docker-compose up -d
- [ ] Verify all health checks pass
- [ ] Review logs for errors
- [ ] Test core functionality

### Before Contributing

- [ ] Read relevant architecture docs
- [ ] Follow code standards in existing files
- [ ] Update documentation for changes
- [ ] Test changes locally
- [ ] Update CHANGELOG (if exists)

---

## 🎉 Summary

**Core Documentation Files** (Must Read):
1. [README.md](README.md) - Start here
2. [SECURITY_WARNING.md](SECURITY_WARNING.md) - Security (CRITICAL)
3. [DOCKER_COMPOSE_GUIDE.md](DOCKER_COMPOSE_GUIDE.md) - Running the platform
4. [kb-rag/ARCHITECTURE.md](kb-rag/ARCHITECTURE.md) - How it works

**Total Reading Time**: ~1 hour for basics, 3-4 hours for deep understanding

**Quick Start** (< 30 min):
```bash
# 1. Read README.md (5 min)
# 2. Read SECURITY_WARNING.md (5 min)
# 3. Setup (15 min)
cp streamlit_app/.env.example .env
# Edit .env with your credentials
docker-compose up -d
# 4. Verify (5 min)
docker-compose ps
curl http://localhost:8501
```

---

📚 **All documentation is living documentation** - it improves with your feedback and contributions!

Happy coding! 🚀
