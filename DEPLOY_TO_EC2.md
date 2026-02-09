# 🚀 Deploy to AWS EC2 - Complete Guide

**Deploy all 4 apps (Flask, Streamlit, kb-rag, kb-sync) to your EC2 instance `100.30.102.67`**

---

## ✅ Prerequisites

Before deploying, you need:

### 1. Weaviate Cloud Cluster
- Go to: https://console.weaviate.cloud/
- Create Cluster → Serverless ($25/month)
- Note down:
  - `WEAVIATE_URL`: https://your-cluster-xyz.weaviate.network
  - `WEAVIATE_API_KEY`: your_api_key_here

### 2. OpenAI API Key
- Get from: https://platform.openai.com/api-keys
- Note down: `OPENAI_API_KEY`: sk-proj-...

### 3. AWS Credentials (for kb-sync)
- IAM user with S3 read access to `jenkins-kb` bucket
- Note down:
  - `AWS_ACCESS_KEY_ID`: AKIA...
  - `AWS_SECRET_ACCESS_KEY`: ...

### 4. Jenkins API Token
- Your existing Jenkins: http://100.30.102.67:8080
- User → Configure → API Token → Generate
- Note down: `JENKINS_TOKEN`: ...

---

## 📋 Step-by-Step Deployment

### Step 1: Add Credentials to Jenkins

1. Open Jenkins: http://100.30.102.67:8080
2. Go to: **Manage Jenkins** → **Credentials** → **(global)** → **Add Credentials**

Add these 5 credentials (Type: **Secret text**):

| ID (exact name) | Secret Value |
|-----------------|--------------|
| `openai-api-key` | `sk-proj-your_openai_key` |
| `weaviate-url` | `https://your-cluster.weaviate.network` |
| `weaviate-api-key` | `your_weaviate_api_key` |
| `aws-kb-access-key-id` | `AKIA...` |
| `aws-kb-secret-access-key` | `your_aws_secret_key` |

**Important**: Use exact IDs from the table above.

---

### Step 2: Push Code to GitHub

```bash
# Add all files
git add .

# Commit
git commit -m "Deploy full stack to EC2 with RAG chatbot"

# Push
git push origin main
```

---

### Step 3: Jenkins Auto-Deploys

**Option A: Wait for Auto-Deploy** (Jenkins checks every 5 hours)

**Option B: Trigger Manually**
1. Go to Jenkins: http://100.30.102.67:8080
2. Click on **ai-devops-pipeline** job
3. Click **Build Now**

---

### Step 4: Monitor Deployment

Watch the Jenkins build console output. You should see:

```
========================================
Build #123
Building AI DevOps Platform (Full Stack)
========================================
✓ Checking required files...
✓ Docker image built
✓ Deploying Full Stack to EC2...
✓ Flask app is healthy on port 5000
✓ Streamlit app is healthy on port 8501
✓ Application container is running
✓ KB Sync completed successfully

==========================================
🚀 DEPLOYMENT SUCCESSFUL!
==========================================

📍 Access Your Applications:

Jenkins:        http://100.30.102.67:8080
Flask API:      http://100.30.102.67:5000
Streamlit UI:   http://100.30.102.67:8501

Features Enabled:
✓ Jenkins Integration
✓ RAG Chatbot (in Streamlit)
✓ Weaviate Cloud Connected
✓ Knowledge Base Synced
==========================================
```

---

## 🧪 Testing on EC2

### Test 1: Flask API

```bash
curl http://100.30.102.67:5000/health
```

**Expected**: `{"status": "healthy"}`

---

### Test 2: Streamlit Dashboard

**Open in browser**: http://100.30.102.67:8501

**You should see**:
- Jenkins pipeline triggers
- Build monitoring
- **RAG Chatbot** section

---

### Test 3: RAG Chatbot

1. Open Streamlit: http://100.30.102.67:8501
2. Find the **RAG Chatbot** interface (sidebar or main page)
3. Type question: **"What causes OutOfMemoryError?"**
4. Click **Submit** or **Send**

**Expected**: Answer from knowledge base about OOM errors

---

### Test 4: Check Logs (SSH to EC2)

```bash
# SSH to EC2
ssh -i your-key.pem ec2-user@100.30.102.67

# Check container running
docker ps | grep ai-devops-app

# View logs
docker logs -f ai-devops-app

# Check Flask health
curl http://localhost:5000/health

# Check Streamlit health
curl http://localhost:8501/_stcore/health
```

---

### Test 5: Test KB Sync (Manual)

```bash
# SSH to EC2
ssh -i your-key.pem ec2-user@100.30.102.67

# Run KB Sync manually
docker exec ai-devops-app bash -c "cd /app/kb-sync && python kb_sync_agent.py"

# Expected output:
# [S3 Fetcher] Fetching from S3...
# [Document Parser] Processing...
# [Embedder] Creating embeddings...
# [Weaviate Uploader] Uploading...
# ✓ Sync completed successfully
```

---

## 🐛 Troubleshooting

### Issue 1: Build Fails in Jenkins

**Check**: Jenkins console output for errors

**Common causes**:
- Missing Jenkins credentials (check all 5 are added)
- Wrong credential IDs (must match exactly)
- Docker build error (check Dockerfile syntax)

**Fix**:
1. Verify credentials: Jenkins → Manage Jenkins → Credentials
2. Check credential IDs match exactly
3. Re-run build

---

### Issue 2: Container Won't Start on EC2

**SSH to EC2 and check**:
```bash
ssh -i your-key.pem ec2-user@100.30.102.67

# Check container status
docker ps -a | grep ai-devops-app

# Check logs
docker logs ai-devops-app

# Common errors:
# - Port already in use
# - Missing environment variables
# - Permission denied on start.sh
```

**Fix**:
```bash
# Stop old container
docker stop ai-devops-app || true
docker rm ai-devops-app || true

# Rebuild and deploy
# Go back to Jenkins and re-run build
```

---

### Issue 3: RAG Chatbot Not Working

**Check**:
1. Weaviate Cloud cluster is running
2. API key is correct in Jenkins credentials
3. OpenAI API key is valid

**Test Weaviate connection from EC2**:
```bash
ssh -i your-key.pem ec2-user@100.30.102.67

# Test Weaviate
docker exec ai-devops-app bash -c "
curl -I https://your-cluster.weaviate.network/v1/.well-known/ready
"

# Should return: HTTP/2 200
```

**Test OpenAI connection**:
```bash
docker exec ai-devops-app bash -c "
cd /app/kb-rag && python -c '
import openai
import os
client = openai.OpenAI(api_key=os.getenv(\"OPENAI_API_KEY\"))
print(\"OpenAI connection OK\")
'
"
```

---

### Issue 4: KB Sync Fails

**Check S3 access**:
```bash
ssh -i your-key.pem ec2-user@100.30.102.67

# Test S3 access
docker exec ai-devops-app bash -c "
aws s3 ls s3://jenkins-kb/
"

# Should list files in S3 bucket
```

**Common causes**:
- AWS credentials incorrect
- S3 bucket doesn't exist
- IAM user doesn't have S3 read permission

**Fix**: Update AWS credentials in Jenkins

---

## 🔄 Update Deployment

### Update Code

```bash
# Make changes to code
git add .
git commit -m "Update XYZ"
git push origin main

# Jenkins auto-deploys (or trigger manually)
```

### Update Credentials

1. Jenkins → Manage Jenkins → Credentials
2. Click on credential to update
3. Click **Update**
4. Enter new secret value
5. Save
6. Re-run Jenkins build

---

## 📊 What's Running on EC2

```
EC2 Instance: 100.30.102.67
├── Jenkins (port 8080) - Already running
└── Docker Container: ai-devops-app
    ├── Flask API (port 5000)
    ├── Streamlit Dashboard (port 8501)
    │   └── RAG Chatbot (integrated)
    ├── kb-rag libraries
    └── kb-sync agent (runs via Jenkins job)

External:
└── Weaviate Cloud (managed service)
    - Stores knowledge base vectors
    - Accessed via HTTPS API
```

---

## 📝 Deployment Checklist

Before deploying:
- [ ] Weaviate Cloud cluster created
- [ ] OpenAI API key obtained
- [ ] AWS credentials for S3 access ready
- [ ] Jenkins API token generated
- [ ] All 5 credentials added to Jenkins
- [ ] Code pushed to GitHub

After deploying:
- [ ] Jenkins build succeeded
- [ ] Flask API responds: http://100.30.102.67:5000/health
- [ ] Streamlit UI loads: http://100.30.102.67:8501
- [ ] RAG Chatbot visible in Streamlit
- [ ] Can ask questions and get answers
- [ ] KB Sync completed successfully
- [ ] Container running on EC2

---

## ✅ Success!

**Access your applications**:
- **Streamlit Dashboard**: http://100.30.102.67:8501
- **Flask API**: http://100.30.102.67:5000
- **Jenkins**: http://100.30.102.67:8080

**Features working**:
- ✅ Jenkins integration
- ✅ Build monitoring
- ✅ RAG Chatbot with Weaviate Cloud
- ✅ Knowledge base queries
- ✅ Automated deployments

**Cost**: ~$35-75/month (Weaviate + OpenAI + existing EC2)

---

## 🎯 Summary

**Workflow**:
1. Add credentials to Jenkins (one-time)
2. Push code to GitHub
3. Jenkins auto-deploys to EC2
4. Access at http://100.30.102.67:8501
5. Test RAG chatbot

**No local testing needed - deploy directly to cloud!** ✨
