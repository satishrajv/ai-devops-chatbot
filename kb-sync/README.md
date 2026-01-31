# KB Sync - LangGraph Multi-Agent Knowledge Base Synchronization

Automated system that syncs Jenkins error documentation from S3 to Weaviate vector database using LangGraph multi-agent orchestration.

## Architecture

```
S3 Bucket (jenkins-kb)
    ↓
[Agent 1: S3 Fetcher] → Downloads .md files, tracks changes
    ↓
[Agent 2: Document Parser] → Extracts metadata & sections
    ↓
[Agent 3: Embedder] → Generates OpenAI embeddings
    ↓
[Agent 4: Weaviate Uploader] → Inserts/updates documents
    ↓
[Agent 5: Reporter] → Logs results & metrics
```

## Features

- **Multi-Agent Orchestration**: LangGraph coordinates 5 specialized agents
- **Markdown-Only**: Processes `.md` files from S3
- **Smart Change Detection**: SQLite tracks file ETags to avoid reprocessing
- **Vector Embeddings**: OpenAI text-embedding-3-small (1536 dimensions)
- **Weaviate v4**: Modern vector database client
- **Cron-Based**: Runs every 5 minutes on EC2
- **Production-Ready**: Error handling, logging, state management

## Project Structure

```
kb-sync/
├── kb_sync_agent.py          # Main LangGraph orchestrator
├── agents/
│   ├── s3_fetcher.py          # Downloads files from S3
│   ├── document_parser.py     # Parses markdown & extracts metadata
│   ├── embedder.py            # Generates OpenAI embeddings
│   ├── weaviate_uploader.py   # Uploads to Weaviate
│   └── reporter.py            # Generates sync reports
├── config/
│   ├── settings.py            # Configuration loader
│   ├── .env.template          # Template for credentials
│   └── .env                   # Your actual credentials
├── utils/
│   ├── state_tracker.py       # SQLite change tracking
│   └── helpers.py             # Utility functions
├── requirements.txt           # Python dependencies
├── sync.sh                    # Cron wrapper script
├── deploy.sh                  # EC2 deployment script
├── local_test.sh              # Local testing script
└── README.md                  # This file
```

## Prerequisites

- Python 3.8 or higher
- AWS account with S3 access
- OpenAI API key
- Weaviate Cloud account
- EC2 instance (Ubuntu 24.04 recommended)

## Quick Start

### 1. Local Testing (Windows)

```bash
# Navigate to kb-sync directory
cd C:\code\AI-DevOps-chatbot\kb-sync

# Run local test (creates venv, installs deps, runs sync)
bash local_test.sh
```

**Expected Output**:
```
[AGENT 1] S3 Fetcher - Found 1 files to process
[AGENT 2] Document Parser - Successfully parsed 1 documents
[AGENT 3] Embedder - Successfully embedded 1 documents
[AGENT 4] Weaviate Uploader - Successfully uploaded 1 documents
[AGENT 5] Reporter - Report generated

KB SYNC REPORT
Run ID: 20260120_143025
Statistics:
  - S3 Files Found: 1
  - Documents Parsed: 1
  - Documents Embedded: 1
  - Documents Uploaded: 1
```

### 2. EC2 Deployment

```bash
# Deploy to EC2 (uploads files, installs deps, sets up cron)
bash deploy.sh
```

**What it does**:
1. Creates `/home/ubuntu/kb-sync/` directory on EC2
2. Uploads all code files
3. Creates Python virtual environment
4. Installs dependencies
5. Configures cron job (every 5 minutes)
6. Runs initial sync

## Configuration

### Environment Variables (.env)

```bash
# AWS Configuration
AWS_ACCESS_KEY_ID=your_aws_access_key_here
AWS_SECRET_ACCESS_KEY=your_aws_secret_key_here
AWS_REGION=us-east-1
S3_KB_BUCKET=jenkins-kb

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
EMBEDDING_DIMENSION=1536

# Weaviate Configuration
WEAVIATE_URL=your_weaviate_cluster_url_here
WEAVIATE_API_KEY=your_weaviate_api_key_here
WEAVIATE_COLLECTION_NAME=JenkinsKnowledgeBase

# State Tracking
STATE_DB_PATH=kb_sync_state.db
```

## Usage

### Manual Sync (Local)

```bash
cd C:\code\AI-DevOps-chatbot\kb-sync
python kb_sync_agent.py
```

### Manual Sync (EC2)

```bash
ssh -i "C:\Users\Yashvi\myec2_jenkins.pem" ubuntu@35.174.138.165
cd /home/ubuntu/kb-sync
./sync.sh
```

### View Logs (EC2)

```bash
# Real-time logs
ssh -i "C:\Users\Yashvi\myec2_jenkins.pem" ubuntu@35.174.138.165 'tail -f /home/ubuntu/kb-sync/cron.log'

# View kb_sync.log
ssh -i "C:\Users\Yashvi\myec2_jenkins.pem" ubuntu@35.174.138.165 'tail -f /home/ubuntu/kb-sync/kb_sync.log'
```

### Check Cron Status

```bash
ssh -i "C:\Users\Yashvi\myec2_jenkins.pem" ubuntu@35.174.138.165 'crontab -l | grep kb-sync'
```

### Manage Cron Job

```bash
# Disable cron
ssh -i "C:\Users\Yashvi\myec2_jenkins.pem" ubuntu@35.174.138.165 'crontab -l | grep -v kb-sync | crontab -'

# Re-enable cron (every 5 minutes)
ssh -i "C:\Users\Yashvi\myec2_jenkins.pem" ubuntu@35.174.138.165 'bash /home/ubuntu/kb-sync/deploy.sh'
```

## How It Works

### Agent 1: S3 Fetcher
- Lists all objects in S3 bucket
- Filters for `.md` files only
- Checks SQLite database for file changes (compares ETags)
- Downloads new/modified files
- Returns file metadata + content

### Agent 2: Document Parser
- Parses markdown content
- Extracts metadata (error ID, category, severity, etc.)
- Extracts key sections (symptoms, resolution, etc.)
- Creates optimized text for embedding
- Returns structured document

### Agent 3: Embedder
- Takes structured text from parser
- Calls OpenAI API (text-embedding-3-small)
- Generates 1536-dimensional vector
- Returns document with embedding

### Agent 4: Weaviate Uploader
- Connects to Weaviate cluster
- Creates schema if doesn't exist
- Checks if document exists (by s3_key)
- Inserts new or updates existing document
- Updates SQLite state tracker
- Returns upload status

### Agent 5: Reporter
- Collects statistics from all agents
- Generates formatted report
- Logs to console and file
- Returns summary

### State Tracking
- SQLite database tracks processed files
- Stores: s3_key, etag, weaviate_uuid, last_processed
- Prevents reprocessing unchanged files
- Enables incremental sync

## Weaviate Schema

**Collection**: `JenkinsKnowledgeBase`

**Properties**:
- `file_name` (TEXT) - Markdown filename
- `s3_key` (TEXT) - S3 object key
- `title` (TEXT) - Document title
- `error_id` (TEXT) - Error ID (e.g., ERROR-001)
- `error_name` (TEXT) - Human-readable name
- `category` (TEXT) - Error category
- `severity` (TEXT) - Severity level
- `quick_summary` (TEXT) - Brief summary
- `symptoms` (TEXT) - Observable symptoms
- `error_messages` (TEXT) - Actual error text
- `root_cause` (TEXT) - Root cause analysis
- `resolution_steps` (TEXT) - Fix instructions
- `prevention` (TEXT) - Prevention strategies
- `tags` (TEXT_ARRAY) - Searchable tags
- `raw_content` (TEXT) - Full markdown
- `last_modified` (TEXT) - Timestamp
- `etag` (TEXT) - S3 ETag

**Vector**: 1536-dimensional embedding (OpenAI)

## Querying Weaviate

```python
import weaviate
from weaviate.classes.init import Auth

client = weaviate.connect_to_weaviate_cloud(
    cluster_url="wdrd8zyt4ewlcqwk0661w.c0.us-west3.gcp.weaviate.cloud",
    auth_credentials=Auth.api_key("YOUR_API_KEY"),
    skip_init_checks=True
)

collection = client.collections.get("JenkinsKnowledgeBase")

# Search by similarity
results = collection.query.near_text(
    query="OutOfMemoryError Docker container",
    limit=5
)

for obj in results.objects:
    print(f"Error: {obj.properties['error_name']}")
    print(f"Summary: {obj.properties['quick_summary']}")
    print(f"Resolution: {obj.properties['resolution_steps'][:200]}...")
    print()

client.close()
```

## Troubleshooting

### Error: "Unable to locate credentials"
- Check `.env` file exists and has correct AWS credentials
- Verify AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY

### Error: "No module named 'langgraph'"
- Activate virtual environment: `source venv/bin/activate` (Linux) or `source venv/Scripts/activate` (Windows Git Bash)
- Install dependencies: `pip install -r requirements.txt`

### Error: "Meta endpoint 404"
- This is normal for empty Weaviate cluster
- Schema will be created on first sync
- If persists, verify WEAVIATE_URL format (no `https://` prefix needed)

### Error: "File unchanged: xyz.md"
- This is normal - file hasn't changed since last sync
- To force reprocess, delete state DB: `rm kb_sync_state.db`

### Cron not running
```bash
# Check cron service
ssh -i "$PEM_FILE" ubuntu@35.174.138.165 'sudo systemctl status cron'

# View cron logs
ssh -i "$PEM_FILE" ubuntu@35.174.138.165 'grep CRON /var/log/syslog | tail -20'
```

## Adding New Documents

1. Create markdown file following ERROR-001 template
2. Upload to S3: `aws s3 cp jenkins-error-kb-002.md s3://jenkins-kb/`
3. Wait 5 minutes for cron OR run manual sync
4. Check logs to verify processing

## Development

### Adding a New Agent

1. Create new agent file in `agents/` directory
2. Implement agent class with main method
3. Add node function in `kb_sync_agent.py`
4. Update workflow graph with new node and edges

### Modifying Weaviate Schema

1. Update `_ensure_schema()` in `agents/weaviate_uploader.py`
2. Add new properties to `properties` list
3. Delete existing collection (data loss!) OR manually migrate
4. Run sync to create new schema

### Testing Changes

```bash
# Local test
bash local_test.sh

# Check logs
cat kb_sync.log

# Verify Weaviate
python -c "
import weaviate
from weaviate.classes.init import Auth
client = weaviate.connect_to_weaviate_cloud(
    cluster_url='wdrd8zyt4ewlcqwk0661w.c0.us-west3.gcp.weaviate.cloud',
    auth_credentials=Auth.api_key('YOUR_API_KEY'),
    skip_init_checks=True
)
collection = client.collections.get('JenkinsKnowledgeBase')
print(f'Total documents: {collection.aggregate.over_all(total_count=True).total_count}')
client.close()
"
```

## Performance

- **S3 Listing**: ~1-2 seconds
- **Document Parsing**: ~0.1 seconds per document
- **OpenAI Embedding**: ~0.5-1 second per document
- **Weaviate Upload**: ~0.2 seconds per document

**Total**: ~2-4 seconds per new document

## Costs

- **OpenAI Embeddings**: $0.00002 per 1K tokens (~$0.0001 per document)
- **Weaviate Cloud**: Free tier (up to 1M vectors)
- **S3 Storage**: Negligible (<1 MB per document)
- **S3 Requests**: Negligible (LIST + GET operations)

**Estimated**: < $0.01 per day for 10 documents

## Roadmap

- [ ] Add Lambda trigger for real-time S3 → Weaviate sync
- [ ] Implement batch processing for large imports
- [ ] Add support for PDF documents
- [ ] Build query interface for RAG retrieval
- [ ] Add metrics dashboard (S3 + CloudWatch)
- [ ] Integrate with Build Agent (multi-agent system)

## Support

- **GitHub**: https://github.com/satishrajv/AI-DevOps-chatbot
- **Jenkins**: http://35.174.138.165:8080
- **S3 Bucket**: s3://jenkins-kb

## License

MIT License - See repository for details
