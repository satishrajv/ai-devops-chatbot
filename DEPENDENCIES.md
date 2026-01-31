# Dependency Management Guide

## Project Structure

This project contains **4 separate applications**, each with its own dependencies:

```
AI-DevOps-chatbot/
├── flask_app/              # Flask backend API
│   ├── venv/               # Own virtual environment
│   └── requirements.txt    # Flask, gunicorn, pytest
│
├── streamlit_app/          # Jenkins monitoring dashboard
│   ├── venv/               # Own virtual environment
│   └── requirements.txt    # Streamlit, requests
│
├── kb-rag/                 # Production RAG system ⭐ MAIN FOCUS
│   ├── venv/               # Own virtual environment
│   └── requirements.txt    # LangChain, OpenAI, Weaviate, boto3
│
└── kb-sync/                # Multi-agent LangGraph system
    ├── venv/               # Own virtual environment
    └── requirements.txt    # LangGraph, OpenAI, Weaviate, boto3
```

## Why Separate Virtual Environments?

✅ **Isolation**: No version conflicts between applications
✅ **Independence**: Deploy each app separately
✅ **Clarity**: Clear which dependencies belong to which app
✅ **Production-ready**: Standard best practice

## Installation Per Application

### 1. Flask Backend API

```bash
cd C:\code\AI-DevOps-chatbot\flask_app
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

**Dependencies**: Flask, gunicorn, pytest, pytest-cov, flake8

---

### 2. Streamlit Dashboard (Jenkins Monitoring)

```bash
cd C:\code\AI-DevOps-chatbot\streamlit_app
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

**Dependencies**: Streamlit, requests

---

### 3. Production RAG System (kb-rag) ⭐

```bash
cd C:\code\AI-DevOps-chatbot\kb-rag
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python rag_indexer.py
```

**Dependencies**:
- `python-dotenv` - Environment variables
- `boto3` - AWS S3 access
- `openai` - Embeddings and LLM
- `weaviate-client` - Vector database
- `langchain` family - Semantic chunking

---

### 4. Multi-Agent System (kb-sync)

```bash
cd C:\code\AI-DevOps-chatbot\kb-sync
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

**Dependencies**: LangGraph, LangChain, OpenAI, Weaviate, boto3

---

## Dependency Comparison

| Package | flask_app | streamlit_app | kb-rag | kb-sync |
|---------|-----------|---------------|--------|---------|
| Flask | ✅ 3.0.0 | ❌ | ❌ | ❌ |
| Streamlit | ❌ | ✅ 1.29.0 | ❌ | ❌ |
| LangChain | ❌ | ❌ | ✅ 0.3.13 | ✅ >=0.3.0 |
| LangGraph | ❌ | ❌ | ❌ | ✅ >=0.2.0 |
| OpenAI | ❌ | ❌ | ✅ 1.58.1 | ✅ >=1.54.0 |
| Weaviate | ❌ | ❌ | ✅ 4.9.3 | ✅ >=4.9.0 |
| boto3 | ❌ | ❌ | ✅ 1.34.34 | ✅ >=1.35.0 |
| requests | ❌ | ✅ 2.31.0 | ❌ | ✅ >=2.32.0 |

## Version Conflict Resolution

### Issue: kb-rag vs kb-sync have similar dependencies

**kb-rag** (pinned versions):
```
boto3==1.34.34
openai==1.58.1
```

**kb-sync** (flexible versions):
```
boto3>=1.35.0
openai>=1.54.0
```

**Resolution**: Keep them separate! Each app has its own venv, so no conflicts.

## Root requirements.txt - Deprecated

The root `requirements.txt` is **outdated** and should NOT be used.

**Options**:
1. Delete it (clean approach)
2. Replace with documentation (current approach)
3. Keep for reference (not recommended)

## Best Practices

### ✅ DO

- Create separate venv for each application
- Pin exact versions in production apps (`==`)
- Use flexible versions for libraries (`>=`)
- Document dependencies clearly
- Keep requirements.txt in each app folder

### ❌ DON'T

- Share one venv across all apps
- Install everything globally
- Mix development and production dependencies
- Commit venv/ folders to git

## Quick Reference

```bash
# Which app are you working on?

# Flask API
cd flask_app && venv\Scripts\activate

# Streamlit Dashboard
cd streamlit_app && venv\Scripts\activate

# RAG System (MAIN)
cd kb-rag && venv\Scripts\activate

# Multi-Agent System
cd kb-sync && venv\Scripts\activate
```

## For Your Current Focus: kb-rag

Since you're working on the **Production RAG System**, use:

```bash
cd C:\code\AI-DevOps-chatbot\kb-rag
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python rag_indexer.py
```

**Only kb-rag/requirements.txt matters for your RAG work.**

Other requirements.txt files are for other applications you built previously.
