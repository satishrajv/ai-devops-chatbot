# Chatbot Fix Guide - Feb 1, 2026

## 🔍 Issue Identified

The RAG Chatbot in Streamlit UI was not allowing users to ask questions (input disabled).

---

## 🎯 Root Cause

Missing environment variable in AWS Secrets Manager:
- `WEAVIATE_COLLECTION_NAME` was not set in the secrets
- This caused the chatbot initialization to fail
- When initialization fails, the chat input is disabled

---

## ✅ Fixes Applied

### 1. Updated AWS Secrets Manager

Added missing environment variables to `ai-devops-platform/credentials`:

```json
{
  "OPENAI_API_KEY": "sk-svcacct-eQT...",
  "WEAVIATE_URL": "https://ms1b1r79sesauja7ftuz0a.c0.us-west3.gcp.weaviate.cloud",
  "WEAVIATE_API_KEY": "VFJ5dW1KR0M4...",
  "WEAVIATE_COLLECTION_NAME": "JenkinsKB",    <-- ADDED
  "AWS_ACCESS_KEY_ID": "AKIA...",
  "AWS_SECRET_ACCESS_KEY": "IRnF...",
  "JENKINS_USER": "admin",
  "JENKINS_TOKEN": "0b94...",
  "JENKINS_URL": "http://100.30.102.67:8080"  <-- ADDED
}
```

**Key Changes:**
- ✅ Added `WEAVIATE_COLLECTION_NAME`: "JenkinsKB"
- ✅ Added `JENKINS_URL`: "http://100.30.102.67:8080"
- ✅ Verified `WEAVIATE_URL` has correct `https://` protocol

### 2. Updated Local Configuration

Fixed `kb-rag/.env` file (for local development):
```bash
WEAVIATE_URL=https://ms1b1r79sesauja7ftuz0a.c0.us-west3.gcp.weaviate.cloud
# (was missing https:// prefix)
```

### 3. Verified Weaviate Connectivity

Tested Weaviate Cloud cluster:
```bash
✓ Cluster accessible: HTTP 200 OK
✓ Collection "JenkinsKB" exists
✓ Collection has data (jenkins-error-kb-001-outofmemory.md)
✓ API Key authentication working
```

### 4. Committed Changes

```bash
git commit -m "Update IP address to 100.30.102.67 and add troubleshooting guide"
git push origin main
```

---

## 🚀 Deployment Instructions

### Option 1: Manual Jenkins Build (Recommended)

1. **Open Jenkins**: http://100.30.102.67:8080
2. **Log in** with credentials:
   - Username: `admin`
   - Password: `0b94639151854a66bf03c6467e5a7101`
3. **Go to** `ai-devops-pipeline` job
4. **Click** "Build Now" button
5. **Wait** for build to complete (~5-10 minutes)
6. **Verify** Streamlit at http://100.30.102.67:8501

### Option 2: Automatic Build (Wait 5 hours)

Jenkins polls GitHub every 5 hours. The build will automatically trigger when it detects the new commit.

### Option 3: SSH and Manual Restart (If needed)

If you need immediate restart without rebuilding:

```bash
# SSH to EC2 (if key works)
ssh -i "C:/Users/Yashvi/myec2_jenkins.pem" ec2-user@100.30.102.67

# Restart the Docker container
docker restart ai-devops-app

# Check logs
docker logs -f ai-devops-app
```

---

## 🧪 Testing the Fix

After the Jenkins build completes:

### 1. Open Streamlit UI
```
http://100.30.102.67:8501
```

### 2. Go to "Knowledge Assistant" Tab

### 3. Test with Example Questions

Click any of the example buttons:
- "What causes OutOfMemoryError?"
- "How to prevent OOM errors?"
- "How do I fix Jenkins build failures?"

Or type your own question.

### 4. Expected Behavior

✅ **Chat input should be enabled** (you can type)
✅ **Example buttons should work**
✅ **Chatbot should respond with answers from knowledge base**
✅ **Sources should be displayed** (e.g., jenkins-error-kb-001-outofmemory.md)
✅ **Metadata should show**: chunks used, tokens, confidence, response time

### 5. If Still Not Working

Check the error message displayed in the Knowledge Assistant tab. Common issues:

**Error: "Chatbot initialization failed"**
- Check Docker logs: `docker logs ai-devops-app`
- Verify environment variables are loaded
- Ensure Weaviate cluster is accessible from EC2

**Error: "No API key provided"**
- OpenAI API key not loaded from Secrets Manager
- Check EC2 IAM role has `secretsmanager:GetSecretValue` permission

**Error: "Cannot connect to Weaviate"**
- WEAVIATE_URL might be incorrect
- WEAVIATE_API_KEY might be expired
- Check network connectivity from EC2 to Weaviate Cloud

---

## 📊 Environment Variables Required

| Variable | Example | Where Used |
|----------|---------|------------|
| `OPENAI_API_KEY` | `sk-svcacct-...` | Query embedding, Answer generation |
| `WEAVIATE_URL` | `https://...weaviate.cloud` | Vector database connection |
| `WEAVIATE_API_KEY` | `VFJ5dW1K...` | Weaviate authentication |
| `WEAVIATE_COLLECTION_NAME` | `JenkinsKB` | Collection to query |
| `JENKINS_URL` | `http://100.30.102.67:8080` | Jenkins API calls |
| `JENKINS_USER` | `admin` | Jenkins authentication |
| `JENKINS_TOKEN` | `0b94...` | Jenkins API token |

**All stored in**: AWS Secrets Manager → `ai-devops-platform/credentials`

---

## 🔧 Troubleshooting Commands

### Check if secrets are loaded in container
```bash
docker exec ai-devops-app env | grep -E "WEAVIATE|OPENAI|JENKINS"
```

### Test Weaviate from container
```bash
docker exec ai-devops-app python -c "
import weaviate
import os
client = weaviate.Client(
    url=os.getenv('WEAVIATE_URL'),
    auth_client_secret=weaviate.AuthApiKey(os.getenv('WEAVIATE_API_KEY'))
)
print(client.is_ready())
"
```

### Check Streamlit logs
```bash
docker logs ai-devops-app 2>&1 | grep -i "streamlit\|chatbot\|error"
```

### Restart services without rebuild
```bash
docker restart ai-devops-app
```

---

## ✅ Success Checklist

After deploying the fix:

- [ ] Jenkins build #22 (or later) completed successfully
- [ ] Streamlit UI loads at http://100.30.102.67:8501
- [ ] Knowledge Assistant tab shows no errors
- [ ] Chat input field is enabled (can type)
- [ ] Example question buttons work
- [ ] Chatbot responds with relevant answers
- [ ] Sources are displayed correctly
- [ ] Metadata shows token usage and confidence

---

## 📝 Summary

**Problem**: Missing `WEAVIATE_COLLECTION_NAME` environment variable caused chatbot initialization to fail.

**Solution**: Updated AWS Secrets Manager with all required environment variables.

**Next Step**: Trigger Jenkins build to redeploy with new secrets.

**Expected Result**: Chatbot will initialize successfully and chat input will be enabled.

---

## 🔗 Related Files

- `streamlit_app/app.py` - Main Streamlit UI (lines 170-178: chatbot initialization)
- `kb-rag/langgraph_chatbot.py` - RAG chatbot implementation
- `kb-rag/config.py` - Configuration settings
- `start-with-secrets.sh` - Startup script that loads secrets
- `scripts/fetch_secrets.py` - Fetches secrets from AWS Secrets Manager

---

## 📞 Support

If issues persist after deployment:

1. Check Jenkins build logs for errors
2. Check Docker container logs: `docker logs ai-devops-app`
3. Verify Weaviate connectivity from EC2
4. Ensure OpenAI API key is valid and has credits
5. Review this guide's troubleshooting section

---

**Last Updated**: Feb 1, 2026
**Status**: Ready for deployment
**Next Action**: Trigger Jenkins build to apply changes
