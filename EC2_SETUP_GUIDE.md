# EC2 Setup Guide - AI DevOps Platform

**Deploy all 4 apps (Flask, Streamlit, kb-rag, kb-sync) to your existing EC2 instance**

Your current setup: EC2 instance `100.30.102.67` with Jenkins running

---

## 🎯 What Will Be Deployed

On your **existing EC2 instance**:
- ✅ Flask API (port 5000)
- ✅ Streamlit Dashboard (port 8501) with integrated RAG Chatbot
- ✅ kb-rag system (integrated in Streamlit)
- ✅ kb-sync agent (runs as Jenkins job)

**Uses Weaviate Cloud** (managed service - no local Weaviate needed)

---

## 📋 Prerequisites

### 1. Weaviate Cloud Setup

**Create a Weaviate cluster** (if you don't have one):

```bash
# 1. Go to https://console.weaviate.cloud/
# 2. Sign up / Log in
# 3. Click "Create Cluster"
# 4. Select plan:
#    - Sandbox (Free for testing)
#    - Serverless ($25/month - recommended)
# 5. Configure:
#    Cluster Name: jenkins-kb-vectordb
#    Region: us-east-1
#    Authentication: API Key
#    Modules: text2vec-openai, generative-openai
# 6. Save these:
#    WEAVIATE_URL: https://your-cluster-xyz.weaviate.network
#    WEAVIATE_API_KEY: your_api_key_here
```

### 2. OpenAI API Key

Get from: https://platform.openai.com/api-keys

### 3. AWS Credentials for KB Sync

You need AWS credentials with S3 access to read from `jenkins-kb` bucket.

---

## 🔧 Step 1: Configure Jenkins Credentials

**Add credentials in Jenkins** (Manage Jenkins → Credentials):

| ID | Type | Value |
|-----|------|-------|
| `openai-api-key` | Secret text | `sk-your_openai_key_here` |
| `weaviate-url` | Secret text | `https://your-cluster.weaviate.network` |
| `weaviate-api-key` | Secret text | `your_weaviate_api_key` |
| `aws-kb-access-key-id` | Secret text | `AKIA...` |
| `aws-kb-secret-access-key` | Secret text | `your_aws_secret_key` |

**Steps to add**:
1. Jenkins → Manage Jenkins → Credentials
2. Click "(global)" domain
3. Click "Add Credentials"
4. Kind: "Secret text"
5. Scope: Global
6. Secret: `<paste your value>`
7. ID: `<use exact ID from table above>`
8. Click "Create"
9. Repeat for all 5 credentials

---

## 🚀 Step 2: Deploy to EC2

### Option A: Via Jenkins (Recommended)

```bash
# 1. Commit your updated code
git add Dockerfile Jenkinsfile.ec2-simple start.sh
git commit -m "Add kb-rag and kb-sync to deployment"
git push origin main

# 2. Jenkins will auto-detect changes (checks every 5 hours)
# Or trigger manually:
# Go to Jenkins → ai-devops-pipeline → "Build Now"
```

### Option B: Manual Deployment on EC2

SSH into your EC2 instance:

```bash
ssh -i your-key.pem ec2-user@100.30.102.67

# Pull latest code
cd AI-DevOps-chatbot
git pull origin main

# Build Docker image
docker build -t ai-devops-app:latest .

# Stop old container
docker stop ai-devops-app || true
docker rm ai-devops-app || true

# Run new container with all env vars
docker run -d \
    --name ai-devops-app \
    --restart unless-stopped \
    -p 5000:5000 \
    -p 8501:8501 \
    -e JENKINS_URL=http://100.30.102.67:8080 \
    -e JENKINS_USER=admin \
    -e JENKINS_TOKEN=your_jenkins_token \
    -e OPENAI_API_KEY=sk-your_key \
    -e WEAVIATE_URL=https://your-cluster.weaviate.network \
    -e WEAVIATE_API_KEY=your_weaviate_key \
    -e AWS_ACCESS_KEY_ID=AKIA... \
    -e AWS_SECRET_ACCESS_KEY=your_secret \
    -e AWS_REGION=us-east-1 \
    -e S3_KB_BUCKET=jenkins-kb \
    ai-devops-app:latest

# Check logs
docker logs -f ai-devops-app
```

---

## ✅ Step 3: Verify Deployment

### Check Services are Running

```bash
# Check container
docker ps | grep ai-devops-app

# Check Flask API
curl http://100.30.102.67:5000/health

# Check Streamlit (in browser)
# http://100.30.102.67:8501
```

### Test RAG Chatbot

1. Open Streamlit: `http://100.30.102.67:8501`
2. You should see RAG Chatbot interface in the sidebar or main page
3. Ask a question: "What causes OutOfMemoryError?"
4. Should get answer from knowledge base

### Test KB Sync

```bash
# Run kb-sync manually
docker exec ai-devops-app bash -c "cd /app/kb-sync && python kb_sync_agent.py"

# Check logs
docker logs ai-devops-app | grep "KB Sync"
```

---

## 📊 Application Structure on EC2

```
EC2 Instance (100.30.102.67)
├── Jenkins (port 8080) - Already running
└── Docker Container: ai-devops-app
    ├── Flask API (port 5000)
    ├── Streamlit Dashboard (port 8501)
    │   └── RAG Chatbot (integrated)
    ├── kb-rag/ (libraries for chatbot)
    └── kb-sync/ (runs via Jenkins job)
```

**Weaviate Cloud** (external managed service)
- Stores knowledge base vectors
- Accessed via API from EC2

---

## 🔄 KB Sync Scheduling

### Option 1: Via Jenkins (Recommended)

Already configured in `Jenkinsfile.ec2-simple` - runs after each deployment.

**To run on schedule**:

1. Create new Jenkins job: "kb-sync-daily"
2. Pipeline script:
```groovy
pipeline {
    agent any
    triggers {
        cron('0 2 * * *')  // Run at 2 AM daily
    }
    stages {
        stage('Run KB Sync') {
            steps {
                sh '''
                    docker exec ai-devops-app bash -c "
                        cd /app/kb-sync && python kb_sync_agent.py
                    "
                '''
            }
        }
    }
}
```

### Option 2: Via Cron on EC2

```bash
# SSH to EC2
ssh -i your-key.pem ec2-user@100.30.102.67

# Add cron job
crontab -e

# Add this line (runs daily at 2 AM):
0 2 * * * docker exec ai-devops-app bash -c "cd /app/kb-sync && python kb_sync_agent.py" >> /var/log/kb-sync.log 2>&1

# Save and exit
```

---

## 🐛 Troubleshooting

### Issue 1: Container Won't Start

```bash
# Check logs
docker logs ai-devops-app

# Common issues:
# - Missing environment variables
# - Weaviate URL incorrect (must be https://)
# - Port 5000 or 8501 already in use
```

**Fix**:
```bash
# Check if ports are in use
sudo netstat -tulpn | grep -E '5000|8501'

# Kill processes if needed
sudo kill <PID>

# Restart container
docker restart ai-devops-app
```

### Issue 2: Can't Connect to Weaviate

```bash
# Test Weaviate connection from EC2
curl -I https://your-cluster.weaviate.network/v1/.well-known/ready

# Test with API key
curl -H "Authorization: Bearer your_weaviate_key" \
    https://your-cluster.weaviate.network/v1/schema
```

**Common causes**:
- Wrong WEAVIATE_URL (check https:// not http://)
- Wrong WEAVIATE_API_KEY
- Firewall blocking outbound HTTPS

### Issue 3: RAG Chatbot Not Working

```bash
# Check if kb-rag dependencies installed
docker exec ai-devops-app python -c "import weaviate; import openai; print('OK')"

# Check environment variables in container
docker exec ai-devops-app env | grep -E "WEAVIATE|OPENAI"

# Check logs
docker logs ai-devops-app 2>&1 | grep -i error
```

### Issue 4: KB Sync Fails

```bash
# Check S3 access
docker exec ai-devops-app bash -c "aws s3 ls s3://jenkins-kb"

# Check logs
docker exec ai-devops-app bash -c "cd /app/kb-sync && python kb_sync_agent.py"
```

---

## 📝 Environment Variables Reference

| Variable | Example | Purpose |
|----------|---------|---------|
| `JENKINS_URL` | `http://100.30.102.67:8080` | Jenkins server URL |
| `JENKINS_USER` | `admin` | Jenkins username |
| `JENKINS_TOKEN` | `0b94...7101` | Jenkins API token |
| `OPENAI_API_KEY` | `sk-proj-...` | OpenAI API access |
| `WEAVIATE_URL` | `https://xyz.weaviate.network` | Weaviate Cloud cluster |
| `WEAVIATE_API_KEY` | `abc...xyz` | Weaviate authentication |
| `AWS_ACCESS_KEY_ID` | `AKIA...` | AWS S3 access (kb-sync) |
| `AWS_SECRET_ACCESS_KEY` | `secret...` | AWS credentials |
| `S3_KB_BUCKET` | `jenkins-kb` | S3 bucket with KB files |

---

## 🔐 Security Checklist

- [ ] Store credentials in Jenkins Credentials (not in code)
- [ ] Use HTTPS for Weaviate URL
- [ ] Restrict EC2 security group (ports 5000, 8501 only from your IP if needed)
- [ ] Rotate Jenkins API token regularly
- [ ] Use IAM role for EC2 instead of AWS keys (recommended)
- [ ] Enable HTTPS for Streamlit (optional, use nginx reverse proxy)

---

## 💰 Cost Estimate

**EC2**: Already running (no additional cost)
**Weaviate Cloud**: $25/month (Serverless plan)
**OpenAI API**: ~$10-50/month (usage-based)
**S3**: ~$1/month (for jenkins-kb bucket)

**Total Additional**: ~$36-76/month

---

## 📚 Next Steps

After deployment:

1. **Test RAG Chatbot**
   - Go to http://100.30.102.67:8501
   - Try asking DevOps questions

2. **Populate Knowledge Base**
   - Add markdown files to S3 bucket `jenkins-kb`
   - Run KB Sync: `docker exec ai-devops-app bash -c "cd /app/kb-sync && python kb_sync_agent.py"`

3. **Monitor Logs**
   - Jenkins: http://100.30.102.67:8080
   - S3 logs: `s3://jenkins-logs-aidevops-2026/`
   - Docker: `docker logs -f ai-devops-app`

4. **Set Up Scheduled KB Sync**
   - Create Jenkins job (see above)
   - Or use cron

---

## ✅ Success Checklist

- [ ] Weaviate Cloud cluster created and accessible
- [ ] OpenAI API key obtained
- [ ] Jenkins credentials configured (5 secrets)
- [ ] Code pushed to GitHub
- [ ] Jenkins pipeline ran successfully
- [ ] Flask API responding: http://100.30.102.67:5000/health
- [ ] Streamlit UI loaded: http://100.30.102.67:8501
- [ ] RAG Chatbot working in Streamlit
- [ ] KB Sync completed successfully
- [ ] Knowledge base queries returning results

---

## 🎉 You're Done!

Your EC2 instance now runs:
- ✅ Jenkins (existing)
- ✅ Flask API
- ✅ Streamlit Dashboard
- ✅ RAG Chatbot (integrated)
- ✅ KB Sync agent

**Access**: http://100.30.102.67:8501

All running in **one Docker container** on your **existing EC2 instance**.

No new infrastructure created. ✨
