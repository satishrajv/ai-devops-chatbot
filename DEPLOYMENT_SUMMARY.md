# 🚀 Deployment Summary - EC2 Single Instance

**All 4 apps deployed to your existing EC2 instance**

---

## ✅ What Changed

### Updated Files

| File | What Changed |
|------|--------------|
| `Dockerfile` | Added kb-rag and kb-sync dependencies + env vars |
| `Jenkinsfile.ec2-simple` | Added Weaviate/OpenAI env vars + KB Sync stage |
| `start.sh` | Updated to include RAG chatbot info |

### Backup Files Created

- `Dockerfile.old` - Your original Dockerfile
- `Jenkinsfile.ec2-simple.old` - Your original Jenkinsfile

---

## 🎯 Deployment Architecture

```
EC2 Instance: 35.174.138.165
├── Jenkins (port 8080) ← Already running
└── Docker Container: ai-devops-app
    ├── Flask API → port 5000
    ├── Streamlit UI → port 8501
    │   └── RAG Chatbot (integrated)
    ├── /app/kb-rag (libraries)
    └── /app/kb-sync (agent)

External Services:
└── Weaviate Cloud ← Managed vector database
    (Access via API from EC2)
```

---

## 🔧 Quick Setup

### 1. Create Weaviate Cluster

```
https://console.weaviate.cloud/
→ Create Cluster
→ Serverless plan ($25/month)
→ Save URL and API Key
```

### 2. Add Jenkins Credentials

Go to: Jenkins → Manage Jenkins → Credentials → Add Credentials

Add these 5 secrets (Type: "Secret text"):

| ID | Value |
|-----|-------|
| `openai-api-key` | `sk-proj-...` |
| `weaviate-url` | `https://your-cluster.weaviate.network` |
| `weaviate-api-key` | `your_key` |
| `aws-kb-access-key-id` | `AKIA...` |
| `aws-kb-secret-access-key` | `your_secret` |

### 3. Deploy

```bash
# Push updated code
git add Dockerfile Jenkinsfile.ec2-simple start.sh
git commit -m "Add kb-rag and kb-sync to EC2 deployment"
git push origin main

# Jenkins auto-deploys (or trigger manually)
```

### 4. Access

- **Streamlit Dashboard**: http://35.174.138.165:8501
- **Flask API**: http://35.174.138.165:5000
- **Jenkins**: http://35.174.138.165:8080

---

## 📊 What Runs Where

| Component | Location | Port | Always Running? |
|-----------|----------|------|-----------------|
| Flask API | Docker container | 5000 | ✅ Yes |
| Streamlit UI | Docker container | 8501 | ✅ Yes |
| RAG Chatbot | Integrated in Streamlit | 8501 | ✅ Yes |
| kb-rag | Libraries in container | - | Used by Streamlit |
| kb-sync | Script in container | - | ❌ Runs on schedule |
| Weaviate | Cloud (external) | 443 | ✅ Yes (managed) |

---

## 🔍 Verify Deployment

```bash
# Check container running
docker ps | grep ai-devops-app

# Check Flask
curl http://35.174.138.165:5000/health

# Check Streamlit (browser)
http://35.174.138.165:8501

# Check logs
docker logs -f ai-devops-app

# Test RAG chatbot
# Go to Streamlit UI → Ask: "What causes OutOfMemoryError?"
```

---

## 🔄 Run KB Sync

### Manual

```bash
docker exec ai-devops-app bash -c "cd /app/kb-sync && python kb_sync_agent.py"
```

### Scheduled (Cron)

```bash
# On EC2
crontab -e

# Add:
0 2 * * * docker exec ai-devops-app bash -c "cd /app/kb-sync && python kb_sync_agent.py" >> /var/log/kb-sync.log 2>&1
```

---

## 📝 Environment Variables

The Dockerfile and Jenkinsfile now handle these:

```bash
# Jenkins
JENKINS_URL=http://35.174.138.165:8080
JENKINS_USER=admin
JENKINS_TOKEN=<from Jenkins credentials>

# AI Services
OPENAI_API_KEY=<from Jenkins credentials>
WEAVIATE_URL=<from Jenkins credentials>
WEAVIATE_API_KEY=<from Jenkins credentials>

# AWS (for kb-sync)
AWS_ACCESS_KEY_ID=<from Jenkins credentials>
AWS_SECRET_ACCESS_KEY=<from Jenkins credentials>
S3_KB_BUCKET=jenkins-kb
```

---

## 💡 Key Points

1. **Uses Weaviate Cloud** - No local Weaviate installation needed
2. **Single Docker Container** - Flask + Streamlit + kb-rag + kb-sync
3. **No New Infrastructure** - Uses your existing EC2 instance
4. **Credentials in Jenkins** - Secure storage, not in code
5. **kb-sync Runs on Demand** - Not a constantly running service

---

## 🐛 Quick Troubleshooting

| Issue | Check | Fix |
|-------|-------|-----|
| Container won't start | `docker logs ai-devops-app` | Check env vars, restart |
| Can't reach Weaviate | `curl -I $WEAVIATE_URL/v1/.well-known/ready` | Check URL (https://), API key |
| RAG not working | Check Streamlit logs | Verify OpenAI & Weaviate credentials |
| KB Sync fails | `docker exec ai-devops-app bash -c "aws s3 ls s3://jenkins-kb"` | Check AWS credentials |

---

## 💰 Additional Cost

| Service | Cost |
|---------|------|
| EC2 | $0 (already running) |
| Weaviate Cloud | $25/month |
| OpenAI API | $10-50/month |
| **Total** | **$35-75/month** |

---

## 📚 Documentation

- **Complete Setup**: `EC2_SETUP_GUIDE.md`
- **Folder Review**: `FOLDER_STRUCTURE_REVIEW.md`
- **Security**: `SECURITY_WARNING.md`
- **All Docs**: `DOCUMENTATION_INDEX.md`

---

## ✅ Next Steps

1. ✅ Configure Jenkins credentials
2. ✅ Create Weaviate Cloud cluster
3. ✅ Push code to trigger deployment
4. ✅ Verify all services running
5. ✅ Test RAG chatbot
6. ✅ Add KB files to S3
7. ✅ Run KB Sync

---

**🎉 Your EC2 now runs the complete AI DevOps Platform!**

**Access**: http://35.174.138.165:8501
