# RAG Chatbot with LangGraph

Interactive chatbot UI that queries your Jenkins knowledge base using LangGraph multi-agent workflow.

## Architecture

```
┌──────────────────────────────────────────────────────────┐
│                   Streamlit UI                           │
│  User types question → Beautiful chat interface          │
└────────────────────┬─────────────────────────────────────┘
                     │
                     ▼
┌──────────────────────────────────────────────────────────┐
│              LangGraph Workflow                          │
│                                                          │
│  Agent 1: Query Processor                               │
│    ├─ Clean question                                    │
│    └─ Generate embedding                                │
│           │                                              │
│           ▼                                              │
│  Agent 2: RAG Retriever                                 │
│    ├─ Search Weaviate                                   │
│    ├─ Rank by relevance                                 │
│    └─ Filter by distance                                │
│           │                                              │
│           ▼                                              │
│  Decision: Chunks found?                                │
│    ├─ Yes → Agent 3: Answer Generator                   │
│    │         └─ Generate with LLM + context             │
│    └─ No  → Fallback Response                           │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

## File Structure

```
kb-rag/
├── chatbot_ui.py              # Streamlit UI (run this!)
├── langgraph_chatbot.py       # LangGraph workflow
├── agents/
│   ├── __init__.py
│   ├── query_processor.py     # Agent 1: Clean + embed
│   ├── rag_retriever.py       # Agent 2: Search Weaviate
│   └── answer_generator.py    # Agent 3: Generate answer
├── rag_indexer.py             # Index documents (run first)
└── requirements.txt           # Updated with langgraph + streamlit
```

## Setup

### 1. Install Dependencies

```bash
cd C:\code\AI-DevOps-chatbot\kb-rag

# Activate venv
venv\Scripts\activate

# Install new dependencies
pip install -r requirements.txt
```

New packages installed:
- `langgraph` - Multi-agent workflow
- `langchain-core` - LangChain core
- `streamlit` - Web UI

### 2. Index Your Knowledge Base (First Time)

```bash
python rag_indexer.py
```

This loads documents from S3 into Weaviate.

### 3. Run the Chatbot UI

```bash
streamlit run chatbot_ui.py
```

Your browser will open automatically at `http://localhost:8501`

## How to Use

### Chatbot Interface

1. **Ask Questions**: Type in the chat input at the bottom
2. **See Sources**: Click "📚 Sources" to see which documents were used
3. **View Metadata**: See chunks used, tokens, confidence, and response time
4. **Example Questions**: Click sidebar buttons for quick questions
5. **Adjust Settings**: Use sidebar sliders for Top-K and Temperature

### Example Questions

```
✅ "What causes OutOfMemoryError in Docker containers?"
✅ "How do I fix Jenkins build failures?"
✅ "What are symptoms of memory issues?"
✅ "How to prevent OOM errors in production?"
```

### Understanding the Response

Each answer shows:
- 📚 **Sources**: Which KB documents were used
- 🎯 **Chunks**: How many document chunks retrieved
- 🔢 **Tokens**: OpenAI API tokens used (for cost tracking)
- 📊 **Confidence**: How confident (0-100%)
- ⏱️ **Time**: Response time in seconds
- ⚠️ **Fallback**: Shows if no relevant docs found

## LangGraph Workflow Details

### Agent 1: Query Processor

**Input**: Raw user question
**Output**: Cleaned query + embedding

```python
User: "what causes oom errors"
↓
Cleaned: "What causes OOM errors?"
Embedding: [0.123, -0.456, ...] (1536 dims)
```

### Agent 2: RAG Retriever

**Input**: Query embedding
**Output**: Relevant chunks from Weaviate

```python
Embedding → Weaviate Search
↓
Top 3 chunks (distance < 0.7)
- jenkins-error-kb-001-outofmemory.md (distance: 0.23)
- jenkins-error-kb-001-outofmemory.md (distance: 0.35)
```

### Agent 3: Answer Generator

**Input**: Original question + retrieved chunks
**Output**: LLM-generated answer

```python
Context: [3 chunks from KB]
Question: "What causes OOM errors?"
↓
GPT-4o-mini generates answer
↓
"OutOfMemoryError occurs when..."
```

### Fallback Node

**Triggered when**: No relevant chunks found

```python
No chunks found (distance > 0.7)
↓
Fallback response:
"I couldn't find specific information about that..."
```

## Configuration

### Environment Variables (.env)

```bash
# Already configured
OPENAI_API_KEY=...
WEAVIATE_URL=...
WEAVIATE_API_KEY=...
WEAVIATE_COLLECTION_NAME=JenkinsKB
```

### Adjustable Settings (Sidebar)

| Setting | Range | Default | Purpose |
|---------|-------|---------|---------|
| **Top-K** | 1-5 | 3 | Number of chunks to retrieve |
| **Temperature** | 0.0-1.0 | 0.3 | LLM creativity (0=precise, 1=creative) |

**Distance Threshold**: 0.7 (hardcoded in `rag_retriever.py`)
- Lower = more similar (0.0 = identical)
- Higher = less similar
- Chunks with distance > 0.7 are filtered out

## Testing the Chatbot

### Option 1: Streamlit UI (Visual)

```bash
streamlit run chatbot_ui.py
```

### Option 2: Command Line (Testing)

```bash
python langgraph_chatbot.py
```

This runs 3 test questions and shows the workflow.

### Option 3: Python Code

```python
from langgraph_chatbot import RAGChatbot

chatbot = RAGChatbot()
response = chatbot.ask("What causes OutOfMemoryError?")

print(response['answer'])
print(response['sources'])
```

## Production Deployment

### Local Development

```bash
# Run locally
streamlit run chatbot_ui.py
```

### Deploy to Streamlit Cloud

1. Push code to GitHub
2. Go to https://share.streamlit.io
3. Connect your repo
4. Add secrets (`.env` variables)
5. Deploy!

### Deploy to Docker

```dockerfile
# Dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "chatbot_ui.py", "--server.port=8501"]
```

```bash
docker build -t rag-chatbot .
docker run -p 8501:8501 --env-file .env rag-chatbot
```

## Troubleshooting

### Error: "No module named 'langgraph'"

```bash
pip install langgraph langchain-core streamlit
```

### Error: "Weaviate connection failed"

Check `.env` file:
- `WEAVIATE_URL` correct (no `https://`)
- `WEAVIATE_API_KEY` valid

### Error: "No chunks found" (always fallback)

1. Check if indexing succeeded:
   ```bash
   python rag_indexer.py
   ```

2. Verify documents in Weaviate (should show SUCCESS)

3. Try a different question

### Slow Response Time

- Reduce `Top-K` to 2 (fewer chunks = faster)
- Use `gpt-4o-mini` instead of `gpt-4` (already set)

## Monitoring

### Check Logs

Streamlit terminal shows:
```
[Query Processor] Processing question: ...
[RAG Retriever] Retrieved 3 relevant chunks
[Answer Generator] Generated answer: 245 characters
```

### Track Costs

UI shows **Tokens Used** for each query:
- Embedding: ~100 tokens
- LLM: 500-2000 tokens
- Cost: ~$0.001 per query

## Advanced Features

### Add New Agents

Edit `langgraph_chatbot.py`:

```python
# Add new node
workflow.add_node("feedback_agent", feedback_node)

# Add to flow
workflow.add_edge("answer_generator", "feedback_agent")
```

### Customize UI

Edit `chatbot_ui.py`:
- Change colors in CSS section
- Add new sidebar widgets
- Modify chat display format

### Change LLM Model

Edit `agents/answer_generator.py`:

```python
# Change from gpt-4o-mini to gpt-4
def __init__(self, openai_api_key: str, model: str = "gpt-4"):
```

## Next Steps

1. ✅ **Working chatbot** - Done!
2. Add more documents to S3 → Re-index
3. Collect user feedback (thumbs up/down)
4. Add conversation memory (remember context)
5. Deploy to cloud (Streamlit Cloud or Docker)

## Summary

You now have a **production-grade RAG chatbot** with:

✅ **LangGraph multi-agent workflow**
✅ **Beautiful Streamlit UI**
✅ **Source citations**
✅ **Confidence scores**
✅ **Token tracking**
✅ **Fallback handling**
✅ **Example questions**
✅ **Settings panel**

**Run it**: `streamlit run chatbot_ui.py` 🚀
