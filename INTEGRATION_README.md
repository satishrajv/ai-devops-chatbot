# RAG Chatbot Integration with Streamlit UI

The RAG chatbot has been successfully integrated into the existing Jenkins DevOps Platform Streamlit UI.

## Changes Made

### 1. Configuration File Created

**File**: `kb-rag/config.py`

All chatbot settings are now centralized in a configuration file instead of UI controls:

```python
# RAG Retrieval Settings
TOP_K_CHUNKS = 3              # Number of chunks to retrieve
DISTANCE_THRESHOLD = 0.7      # Relevance threshold

# LLM Generation Settings
TEMPERATURE = 0.3             # LLM creativity (0.0-1.0)
LLM_MODEL = "gpt-4o-mini"     # OpenAI model
```

### 2. LangGraph Chatbot Updated

**File**: `kb-rag/langgraph_chatbot.py`

Updated to read settings from `config.py` instead of hardcoded values:

```python
import config

# Uses config.TOP_K_CHUNKS instead of hardcoded 3
# Uses config.DISTANCE_THRESHOLD instead of hardcoded 0.7
# Uses config.TEMPERATURE instead of hardcoded 0.3
# Uses config.LLM_MODEL instead of hardcoded "gpt-4o-mini"
```

### 3. Streamlit App Integration

**File**: `streamlit_app/app.py`

Added a new **5th tab** called "🤖 Knowledge Assistant" to the existing Jenkins dashboard:

**Features**:
- ✅ Integrated chatbot (not standalone)
- ✅ Chat interface with message history
- ✅ Source citations showing which KB documents were used
- ✅ Metadata badges (chunks, tokens, confidence, response time)
- ✅ Example question buttons
- ✅ Statistics tracking (total queries, tokens)
- ✅ Clear chat history button
- ❌ **Removed** Top-K slider (now in config.py)
- ❌ **Removed** Temperature slider (now in config.py)

### 4. Dependencies Updated

**File**: `streamlit_app/requirements.txt`

Added all RAG chatbot dependencies so the Streamlit app can import the chatbot modules:

```
python-dotenv==1.0.0
boto3==1.34.34
openai==1.58.1
weaviate-client==4.9.3
langchain==0.3.13
langchain-openai==0.2.14
langchain-experimental==0.3.3
langchain-text-splitters>=0.3.3
langgraph>=0.2.0
langchain-core>=0.3.0
```

## How to Run

### Step 1: Install Dependencies

```bash
cd C:\code\AI-DevOps-chatbot\streamlit_app

# Activate venv (if not already)
venv\Scripts\activate

# Install updated dependencies
pip install -r requirements.txt
```

### Step 2: Index Knowledge Base (First Time Only)

```bash
cd C:\code\AI-DevOps-chatbot\kb-rag
python rag_indexer.py
```

Expected output:
```
Successfully indexed documents into Weaviate
```

### Step 3: Run the Integrated Streamlit App

```bash
cd C:\code\AI-DevOps-chatbot\streamlit_app
streamlit run app.py
```

Your browser will open at `http://localhost:8501`

### Step 4: Use the Knowledge Assistant Tab

1. Click on the **"🤖 Knowledge Assistant"** tab
2. Try example questions or type your own
3. See sources, confidence scores, and tokens used

## Tab Layout

The Streamlit app now has 5 tabs:

1. **🎯 Trigger Jobs** - Trigger Jenkins builds
2. **📊 Job Status** - Check build status
3. **📋 All Jobs** - View all Jenkins jobs
4. **📝 Build Logs** - View console logs
5. **🤖 Knowledge Assistant** - NEW! RAG chatbot for DevOps questions

## Changing Settings

To adjust chatbot behavior, edit `kb-rag/config.py`:

```python
# Increase chunks retrieved
TOP_K_CHUNKS = 5

# Make answers more creative
TEMPERATURE = 0.7

# Use a different model
LLM_MODEL = "gpt-4"
```

**No UI changes needed!** Settings are centralized in the config file.

## Architecture

```
┌──────────────────────────────────────────────────────────┐
│           Streamlit UI (streamlit_app/app.py)            │
│                                                          │
│  Tab 1: Trigger Jobs                                    │
│  Tab 2: Job Status                                      │
│  Tab 3: All Jobs                                        │
│  Tab 4: Build Logs                                      │
│  Tab 5: Knowledge Assistant (NEW!)                      │
│           │                                              │
│           ├─ Imports: kb-rag/langgraph_chatbot.py       │
│           ├─ Reads: kb-rag/config.py                    │
│           └─ Uses: kb-rag/agents/*                      │
│                                                          │
└──────────────────────────────────────────────────────────┘
                     │
                     ▼
┌──────────────────────────────────────────────────────────┐
│              LangGraph Workflow (kb-rag/)                │
│                                                          │
│  Agent 1: Query Processor                               │
│    ├─ Clean question                                    │
│    └─ Generate embedding                                │
│           │                                              │
│           ▼                                              │
│  Agent 2: RAG Retriever                                 │
│    ├─ Search Weaviate (top_k from config)              │
│    └─ Filter by distance (threshold from config)       │
│           │                                              │
│           ▼                                              │
│  Decision: Chunks found?                                │
│    ├─ Yes → Agent 3: Answer Generator                   │
│    │         └─ Generate with LLM (temp from config)   │
│    └─ No  → Fallback Response                           │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

## Troubleshooting

### Error: "ModuleNotFoundError: No module named 'langgraph_chatbot'"

**Solution**: Make sure you're running from `streamlit_app/` directory:
```bash
cd C:\code\AI-DevOps-chatbot\streamlit_app
streamlit run app.py
```

### Error: "Chatbot initialization failed"

**Possible causes**:
1. Weaviate credentials not set in `kb-rag/.env`
2. Knowledge base not indexed yet (run `python rag_indexer.py`)
3. OpenAI API key not set in `kb-rag/.env`

**Solution**: Check `kb-rag/.env` file has all required variables:
```bash
OPENAI_API_KEY=...
WEAVIATE_URL=ms1b1r79sesauja7ftuz0a.c0.us-west3.gcp.weaviate.cloud
WEAVIATE_API_KEY=...
WEAVIATE_COLLECTION_NAME=JenkinsKB
```

### Chatbot always returns fallback responses

**Solution**: Re-index the knowledge base:
```bash
cd C:\code\AI-DevOps-chatbot\kb-rag
python rag_indexer.py
```

### Want to change settings

**Solution**: Edit `kb-rag/config.py` and restart Streamlit app.

## Testing

### Test the Chatbot Tab

1. Open the app: `streamlit run app.py`
2. Click **"🤖 Knowledge Assistant"** tab
3. Try example questions:
   - "What causes OutOfMemoryError?"
   - "How do I fix Jenkins build failures?"
   - "What are symptoms of memory issues?"

### Expected Behavior

✅ Should see typing animation while answer generates
✅ Should show sources with relevance scores
✅ Should show metadata badges (chunks, tokens, confidence)
✅ Should track total queries and tokens in statistics
✅ Should NOT have Top-K or Temperature sliders

## Configuration Reference

### `kb-rag/config.py`

| Setting | Default | Description |
|---------|---------|-------------|
| `TOP_K_CHUNKS` | 3 | Number of document chunks to retrieve from Weaviate |
| `DISTANCE_THRESHOLD` | 0.7 | Maximum distance for relevant chunks (0.0-1.0) |
| `TEMPERATURE` | 0.3 | LLM creativity (0.0=precise, 1.0=creative) |
| `LLM_MODEL` | "gpt-4o-mini" | OpenAI model for answer generation |
| `DEBUG_MODE` | False | Enable detailed logging |

### `kb-rag/.env`

| Variable | Example | Description |
|----------|---------|-------------|
| `OPENAI_API_KEY` | sk-... | OpenAI API key |
| `OPENAI_EMBEDDING_MODEL` | text-embedding-3-small | Embedding model |
| `WEAVIATE_URL` | ms1b1r79sesauja7ftuz0a... | Weaviate cluster URL |
| `WEAVIATE_API_KEY` | VFJ5dW1K... | Weaviate API key |
| `WEAVIATE_COLLECTION_NAME` | JenkinsKB | Weaviate collection name |
| `AWS_ACCESS_KEY_ID` | AKIA... | AWS access key (for S3) |
| `AWS_SECRET_ACCESS_KEY` | ... | AWS secret key |
| `AWS_REGION` | us-east-1 | AWS region |
| `S3_KB_BUCKET` | jenkins-kb | S3 bucket name |

## Summary

✅ **Chatbot integrated** into existing Streamlit UI (not standalone)
✅ **Settings moved** to `config.py` (no UI sliders)
✅ **New tab added** to Jenkins dashboard (5th tab)
✅ **Dependencies updated** in `streamlit_app/requirements.txt`
✅ **LangGraph workflow** unchanged (reads from config)

**Next Steps**:
1. Run `pip install -r requirements.txt` in streamlit_app
2. Run the app: `streamlit run app.py`
3. Test the **"🤖 Knowledge Assistant"** tab

**To modify settings**: Edit `kb-rag/config.py` and restart the app 🚀
