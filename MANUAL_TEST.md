# Manual Testing Commands

Test locally before pushing to GitHub → Jenkins CI/CD deploys to EC2.

---

## 1. Setup Weaviate Cloud

```
https://console.weaviate.cloud/
→ Create Cluster → Serverless ($25/month)
→ Save URL and API Key
```

---

## 2. Create .env File

```bash
# Copy to root directory: .env
JENKINS_URL=http://35.174.138.165:8080
JENKINS_USER=admin
JENKINS_TOKEN=your_jenkins_token

OPENAI_API_KEY=sk-proj-your_key
WEAVIATE_URL=https://your-cluster.weaviate.network
WEAVIATE_API_KEY=your_key

AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=your_secret
S3_KB_BUCKET=jenkins-kb
```

---

## 3. Test with Docker (Recommended)

```bash
# Build
docker build -t ai-devops-app:test .

# Run
docker run -d --name ai-devops-test -p 5000:5000 -p 8501:8501 --env-file .env ai-devops-app:test

# Check logs
docker logs -f ai-devops-test

# Test Flask
curl http://localhost:5000/health

# Test Streamlit (browser)
http://localhost:8501

# Stop
docker stop ai-devops-test
docker rm ai-devops-test
```

---

## 4. Test Individual Python Components (Optional)

### Test kb-rag

```bash
cd kb-rag
python -c "
import os
os.environ['OPENAI_API_KEY'] = 'sk-proj-...'
os.environ['WEAVIATE_URL'] = 'https://...'
os.environ['WEAVIATE_API_KEY'] = '...'

from langgraph_chatbot import run_query
result = run_query('What causes OutOfMemoryError?')
print(result['final_answer'])
"
```

### Test kb-sync

```bash
cd kb-sync
python kb_sync_agent.py
```

---

## 5. Deploy to EC2

### Configure Jenkins Credentials

Jenkins → Manage Jenkins → Credentials → Add:
- `openai-api-key` → Secret text
- `weaviate-url` → Secret text
- `weaviate-api-key` → Secret text
- `aws-kb-access-key-id` → Secret text
- `aws-kb-secret-access-key` → Secret text

### Push to GitHub

```bash
git add .
git commit -m "Deploy to EC2"
git push origin main

# Jenkins auto-detects and deploys
# Access: http://35.174.138.165:8501
```

---

## That's It!

**Local**: Docker test → **GitHub**: Push → **EC2**: Jenkins deploys
