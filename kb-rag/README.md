# Production RAG System - Jenkins Knowledge Base

Enterprise-grade RAG (Retrieval-Augmented Generation) system with LangChain semantic chunking, multi-level logging, and production monitoring.

## Features

- **LangChain Semantic Chunking**: Intelligent document splitting based on semantic meaning
- **Production-Grade Logging**: Multi-file logging (all/info/error) with timestamps and stack traces
- **Environment Variables**: All secrets stored in `.env` file (never hardcoded)
- **Error Handling**: Comprehensive exception handling with full context
- **Clean Architecture**: Modular, testable, maintainable code
- **OpenAI Embeddings**: text-embedding-3-small (1536 dimensions)
- **Weaviate Vector Database**: Fast vector similarity search
- **S3 Integration**: Load documents from AWS S3

## Setup

### 1. Install Dependencies

```bash
cd kb-rag
pip install -r requirements.txt
```

### 2. Configure Environment

Copy `.env.template` to `.env` and fill in your credentials:

```bash
cp .env.template .env
```

Edit `.env`:
```
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
OPENAI_API_KEY=your_openai_key
WEAVIATE_URL=your_weaviate_url
WEAVIATE_API_KEY=your_weaviate_key
```

## Usage

### Step 1: Index Documents (One-time setup)

```bash
python rag_indexer.py
```

This will:
1. **Load** all `.md` files from S3 bucket
2. **Chunk** documents using LangChain SemanticChunker
3. **Embed** chunks with OpenAI embeddings
4. **Store** in Weaviate vector database

Output:
```
[STEP 1] Document Loading from S3...
  Loading: jenkins-error-kb-001-outofmemory.md
  Total documents loaded: 1

[STEP 2] Chunking Documents (LangChain)...
  Method: semantic
  Using SemanticChunker (splits based on semantic similarity)
  jenkins-error-kb-001-outofmemory.md: 7500 chars → 12 chunks

[STEP 3] Embedding Generation...
  Total embeddings generated: 12

[STEP 4] Vector Database Storage...
  Successfully stored 12 chunks in Weaviate
```

### Step 2: Query the Knowledge Base

```bash
python rag_query.py
```

This will:
1. **Embed** your question
2. **Search** Weaviate for similar chunks
3. **Generate** answer using retrieved context

Example:
```
Question: What causes OutOfMemoryError in Docker containers?

FINAL ANSWER:
OutOfMemoryError in Docker containers is caused by:
1. Container memory limit set too low (default or insufficient)
2. Memory leaks in application code
3. Large file processing without streaming
...

SOURCES:
  - jenkins-error-kb-001-outofmemory.md (chunk 3)
  - jenkins-error-kb-001-outofmemory.md (chunk 7)
```

## Chunking Methods

The system supports two chunking methods (edit in `simple_rag.py`):

### 1. Semantic Chunking (Default - Recommended)

```python
chunks = step2_chunking(documents, method="semantic")
```

- Splits based on **semantic meaning** (not just characters)
- Uses embeddings to find natural breakpoints
- Better for Q&A and retrieval
- Slower but more intelligent

### 2. Recursive Character Splitting

```python
chunks = step2_chunking(documents, method="recursive")
```

- Splits by characters smartly (respects paragraphs, sentences)
- Faster than semantic
- Good for very large documents

## Architecture

```
┌─────────────────────────────────────────┐
│         STEP 1: INDEXING                │
│         (Offline - Run Once)            │
└─────────────────────────────────────────┘
              │
    ┌─────────┴─────────┐
    │                   │
┌───▼────┐      ┌──────▼──────┐
│  S3    │      │  Documents  │
│ Bucket │─────▶│   Loading   │
└────────┘      └──────┬──────┘
                       │
                ┌──────▼──────────┐
                │   LangChain     │
                │Semantic Chunking│
                └──────┬──────────┘
                       │
                ┌──────▼──────┐
                │   OpenAI    │
                │  Embeddings │
                └──────┬──────┘
                       │
                ┌──────▼──────┐
                │  Weaviate   │
                │   Storage   │
                └─────────────┘

┌─────────────────────────────────────────┐
│         STEP 2: QUERY                   │
│         (Online - Each Question)        │
└─────────────────────────────────────────┘
              │
    ┌─────────┴─────────┐
    │                   │
┌───▼────────┐   ┌──────▼──────┐
│ User       │   │   OpenAI    │
│ Question   │──▶│  Embedding  │
└────────────┘   └──────┬──────┘
                        │
                ┌───────▼────────┐
                │   Weaviate     │
                │Vector Search   │
                └───────┬────────┘
                        │
                ┌───────▼────────┐
                │  GPT-4o-mini   │
                │ Answer Gen     │
                └───────┬────────┘
                        │
                    ┌───▼────┐
                    │ Answer │
                    └────────┘
```

## File Structure

```
kb-rag/                   # Knowledge Base RAG System
├── rag_indexer.py        # Indexing pipeline (production-grade)
├── rag_query.py          # Query pipeline (production-grade)
├── requirements.txt      # Python dependencies
├── .env                  # Your secrets (DO NOT COMMIT)
├── .env.template         # Template for credentials
├── .gitignore           # Excludes logs and .env
├── logs/                # Production logs (auto-created)
│   ├── rag_indexing_YYYYMMDD_HHMMSS_all.log      # All logs (DEBUG+)
│   ├── rag_indexing_YYYYMMDD_HHMMSS_info.log     # Info only
│   ├── rag_indexing_YYYYMMDD_HHMMSS_error.log    # Errors/Warnings only
│   ├── rag_query_YYYYMMDD_HHMMSS_all.log         # All query logs
│   ├── rag_query_YYYYMMDD_HHMMSS_info.log        # Query info only
│   └── rag_query_YYYYMMDD_HHMMSS_error.log       # Query errors only
├── LOGGING_GUIDE.md     # Detailed logging documentation
└── README.md            # This file
```

## Key Differences: Semantic vs Recursive Chunking

| Feature | Semantic | Recursive |
|---------|----------|-----------|
| **Split Logic** | Based on meaning | Based on characters |
| **Quality** | Higher (context-aware) | Good (smart separators) |
| **Speed** | Slower (uses embeddings) | Faster |
| **Best For** | Q&A, precise retrieval | Large docs, speed priority |
| **Cost** | Higher (embedding API calls) | Lower |

## Example Questions

Try asking:
- "What causes OutOfMemoryError in Docker containers?"
- "How do I fix Jenkins build failures?"
- "What are the symptoms of memory issues?"
- "How to prevent OOM errors in production?"

## Troubleshooting

**Error: No module named 'dotenv'**
```bash
pip install python-dotenv
```

**Error: Weaviate connection failed**
- Check WEAVIATE_URL and WEAVIATE_API_KEY in `.env`
- Ensure URL doesn't include `https://`

**Error: OpenAI API key invalid**
- Verify OPENAI_API_KEY in `.env`

**No documents found**
- Check S3_KB_BUCKET name in `.env`
- Verify AWS credentials have S3 read access

## Production Logging

### Multi-File Logging Strategy

Each execution creates **3 separate log files** for easier troubleshooting:

| Log File | Level | Purpose | Use Case |
|----------|-------|---------|----------|
| `*_all.log` | DEBUG+ | Complete execution trace | Debugging, full audit trail |
| `*_info.log` | INFO+ | Important operations only | Quick summary, monitoring |
| `*_error.log` | WARNING+ | Errors and warnings only | Incident response, alerts |

### Example Log Files

After running `python simple_rag.py` on 2026-01-22 at 10:30:15:
```
logs/
├── rag_indexing_20260122_103015_all.log      # Everything (2,450 lines)
├── rag_indexing_20260122_103015_info.log     # Summary only (48 lines)
└── rag_indexing_20260122_103015_error.log    # Empty (no errors)
```

### Sample Log Content

**Info Log** (`rag_indexing_20260122_103015_info.log`):
```
2026-01-22 10:30:15 - __main__ - INFO - RAG Indexing System Started
2026-01-22 10:30:15 - __main__ - INFO - [STEP 1] Document Loading from S3
2026-01-22 10:30:15 - __main__ - INFO - Connected to S3 - Region: us-east-1, Bucket: jenkins-kb
2026-01-22 10:30:16 - __main__ - INFO - Loading document: jenkins-error-kb-001-outofmemory.md (Size: 7500 bytes)
2026-01-22 10:30:17 - __main__ - INFO - Total documents loaded: 1
2026-01-22 10:30:17 - __main__ - INFO - [STEP 2] Chunking Documents (LangChain)
2026-01-22 10:30:17 - __main__ - INFO - Chunking method: semantic
2026-01-22 10:30:25 - __main__ - INFO - Created 12 chunks from jenkins-error-kb-001-outofmemory.md
2026-01-22 10:30:26 - __main__ - INFO - [STEP 3] Embedding Generation
2026-01-22 10:30:35 - __main__ - INFO - Total embeddings generated: 12
2026-01-22 10:30:36 - __main__ - INFO - [STEP 4] Vector Database Storage
2026-01-22 10:30:42 - __main__ - INFO - Successfully stored 12/12 chunks in Weaviate
2026-01-22 10:30:42 - __main__ - INFO - INDEXING COMPLETE!
2026-01-22 10:30:42 - __main__ - INFO - Total duration: 27.45 seconds
```

**All Log** (`rag_indexing_20260122_103015_all.log`) - includes DEBUG:
```
2026-01-22 10:30:15 - __main__ - INFO - RAG Indexing System Started
2026-01-22 10:30:16 - __main__ - DEBUG - Document content length: 7500 characters
2026-01-22 10:30:17 - __main__ - DEBUG - SemanticChunker configured with percentile breakpoint
2026-01-22 10:30:18 - __main__ - DEBUG - Chunk sizes: [645, 823, 567, 712, ...]
2026-01-22 10:30:28 - __main__ - DEBUG - Chunk 1: embedding dimension = 1536
2026-01-22 10:30:29 - __main__ - DEBUG - Chunk 2: embedding dimension = 1536
...
2026-01-22 10:30:37 - __main__ - DEBUG - Inserted chunk 1: jenkins-error-kb-001-outofmemory.md (chunk_id: 0)
```

**Error Log** (`rag_indexing_20260122_103015_error.log`) - only if errors occur:
```
2026-01-22 10:35:42 - __main__ - WARNING - Collection 'JenkinsKB' already exists - deleting for fresh start
2026-01-22 10:42:15 - __main__ - ERROR - Failed to insert chunk 5: Connection timeout
Traceback (most recent call last):
  File "simple_rag.py", line 285, in step4_vector_database_storage
    collection.data.insert(...)
  weaviate.exceptions.WeaviateConnectionError: Connection timeout
```

### Log Levels Explained

- **DEBUG**: Detailed technical info (chunk sizes, embedding dimensions, API responses)
- **INFO**: Normal operations (step progress, counts, durations)
- **WARNING**: Non-critical issues (collection already exists, retries)
- **ERROR**: Failures with stack traces (API errors, connection failures)
- **CRITICAL**: Fatal errors that stop execution

### Why Multiple Log Files?

| Scenario | Which Log to Check |
|----------|-------------------|
| Quick status check | `*_info.log` (48 lines vs 2,450) |
| Something failed | `*_error.log` (empty = success!) |
| Need to debug issue | `*_all.log` (complete trace) |
| Monitor in production | `*_error.log` (alert if not empty) |
| Performance analysis | `*_info.log` (duration, counts) |
| API troubleshooting | `*_all.log` (see full requests) |

### Benefits

✅ **Fast troubleshooting**: Check error log first (usually empty or very small)
✅ **Easy monitoring**: Alert when error log has content
✅ **Audit compliance**: All logs have complete history
✅ **Performance**: Don't parse huge files for simple checks
✅ **Cost-effective**: Archive `*_all.log`, keep `*_error.log` longer

## Production Deployment

### Running in Production

**Indexing (Scheduled - Daily/Weekly)**:
```bash
# Add to cron for daily indexing at 2 AM
0 2 * * * cd /path/to/kb-rag && python rag_indexer.py
```

**Query (On-Demand or API)**:
```bash
# Interactive query
python rag_query.py

# Programmatic query (from your application)
from rag_query import query_rag
answer = query_rag("What causes OOM errors?", top_k=3)
```

### Monitoring

**Check for errors**:
```bash
# Alert if error log has content
if [ -s logs/*_error.log ]; then
  echo "ALERT: RAG system has errors"
  cat logs/*_error.log
fi
```

**Performance metrics**:
```bash
# Extract execution times
grep "Total duration" logs/*_info.log
```

## Next Steps

1. Add more documents to S3 bucket (`jenkins-kb`)
2. Re-run indexing: `python rag_indexer.py`
3. Test different questions: `python rag_query.py`
4. Check logs in `logs/` directory for detailed execution traces
5. Compare semantic vs recursive chunking results (edit `rag_indexer.py` line 356)
6. Set up monitoring alerts on `*_error.log` files
