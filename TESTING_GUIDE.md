# Testing Guide - AI DevOps Platform

## 🎯 How to Test Your Chatbot

Your Streamlit UI should now be open at: **http://100.30.102.67:8501**

---

## 📋 Step-by-Step Testing

### Step 1: Navigate to Knowledge Assistant Tab

1. Look at the top of the Streamlit page
2. You'll see 5 tabs:
   - 🎯 Trigger Jobs
   - 📊 Job Status
   - 📋 All Jobs
   - 📝 Build Logs
   - **🤖 Knowledge Assistant** ← Click this one!

### Step 2: Check Chatbot Status

Look for these indicators:

✅ **Good Signs:**
- You see "Jenkins Knowledge Assistant" heading
- Example question buttons are visible
- Chat input box at the bottom is **enabled** (you can click and type)
- No red error messages

❌ **Bad Signs:**
- Red error message: "Chatbot initialization failed"
- Chat input is grayed out/disabled
- Warning: "Chatbot not initialized"

### Step 3: Test with Example Questions

Click any of the **blue example buttons**:

1. **"What causes OutOfMemoryError?"**
   - Should return information about Java heap memory issues
   - Should show sources from knowledge base

2. **"How to prevent OOM errors?"**
   - Should provide prevention strategies
   - Should reference Jenkins configuration

3. **"How do I fix Jenkins build failures?"**
   - Should give troubleshooting steps
   - Should cite relevant documentation

4. **"What are symptoms of memory issues?"**
   - Should describe memory-related symptoms
   - Should include log patterns to look for

### Step 4: Test with Custom Questions

Type your own questions in the chat input box:

**Try these:**
- "What is Jenkins?"
- "How do I configure Docker in Jenkins?"
- "What causes build timeouts?"
- "How to debug pipeline failures?"
- "What is CI/CD?"

### Step 5: Verify Response Quality

A good response should have:

✅ **Answer Section:**
- Clear, well-formatted text
- Relevant information
- Proper grammar and structure

✅ **Sources Section** (expandable):
- Shows which files the answer came from
- Displays relevance percentage (e.g., 85%)
- Lists document filenames

✅ **Metadata Section:**
- 🎯 Chunks: Number of text chunks used (e.g., 3-5)
- 🔢 Tokens: Token count (e.g., 500-1500)
- 📊 Confidence: Confidence score (e.g., 75%-95%)
- ⏱️ Time: Response time (e.g., 2-5 seconds)

---

## 🧪 Test Scenarios

### Scenario 1: Basic Query
**Question:** "What causes OutOfMemoryError?"

**Expected:**
- Answer about Java heap memory limits
- References to heap size configuration
- Sources: jenkins-error-kb-001-outofmemory.md
- Confidence: 80%+

### Scenario 2: Troubleshooting Query
**Question:** "How do I fix Jenkins build failures?"

**Expected:**
- Step-by-step troubleshooting guide
- Common causes listed
- Solution recommendations
- Confidence: 70%+

### Scenario 3: Configuration Query
**Question:** "How to configure Docker in Jenkins?"

**Expected:**
- Docker setup instructions
- Configuration examples
- Best practices
- May show lower confidence if not in KB

### Scenario 4: Out-of-Scope Query
**Question:** "What is the capital of France?"

**Expected:**
- May say "I don't have information about that"
- Or: "This is outside my knowledge base"
- Low confidence score
- May have ⚠️ Fallback indicator

---

## 🔍 What to Look For

### ✅ Signs Chatbot is Working Correctly

1. **Chat input is enabled** - You can type
2. **Responses appear within 2-10 seconds**
3. **Answers are relevant** to your questions
4. **Sources are displayed** with filenames
5. **Metadata shows reasonable values**:
   - Chunks: 1-10
   - Tokens: 200-2000
   - Confidence: 50%-95%
   - Time: 1-10 seconds

### ❌ Signs of Problems

1. **Chat input is disabled/grayed out**
   - → Chatbot initialization failed
   - → Check Docker logs

2. **Error message: "Error: NoneType..."**
   - → Environment variables not loaded
   - → Check AWS Secrets Manager

3. **Error message: "Cannot connect to Weaviate"**
   - → Weaviate URL incorrect
   - → Check WEAVIATE_URL has https://

4. **Error message: "No API key provided"**
   - → OpenAI key not loaded
   - → Check OPENAI_API_KEY in secrets

5. **Response: "I don't have enough information"** (always)
   - → Weaviate collection empty
   - → Need to run KB Sync

---

## 🎨 UI Features to Test

### Chat History
- Previous questions and answers should stay visible
- Scroll up to see older conversations
- Each message shows sources and metadata

### Example Questions
- All 4 example buttons should work
- Clicking fills the input and sends the question
- Different questions should give different answers

### Statistics (Expandable Section)
- Shows total queries count
- Shows total tokens used
- Shows average tokens per query
- Updates after each question

### Clear Chat Button
- "🗑️ Clear Chat History" button at bottom
- Clicking clears all messages
- Resets statistics to 0
- Ready for new questions

### Sources Expandable
- Click "📚 Sources" to expand/collapse
- Shows which documents were used
- Displays relevance scores
- Color-coded for easy reading

---

## 📊 Performance Benchmarks

**Normal Performance:**
- Response time: 2-8 seconds
- Token usage: 300-1500 per query
- Chunks retrieved: 3-8
- Confidence: 60%-90%

**Good Performance:**
- Response time: < 5 seconds
- Token usage: < 1000
- Chunks retrieved: 4-6
- Confidence: > 80%

**Needs Improvement:**
- Response time: > 10 seconds
- Token usage: > 2000
- Confidence: < 50%
- Frequent fallback responses

---

## 🐛 Troubleshooting

### Problem: Chat Input is Disabled

**Check:**
```bash
# View container logs
docker logs ai-devops-app 2>&1 | tail -50

# Check for initialization errors
docker logs ai-devops-app 2>&1 | grep -i "chatbot\|error\|failed"
```

**Solution:**
- Check if all environment variables are set
- Verify Weaviate connectivity
- Ensure OpenAI API key is valid

### Problem: "Chatbot initialization failed" Error

**Possible Causes:**
1. Missing environment variables
2. Weaviate URL incorrect
3. Invalid API keys
4. Network connectivity issues

**Check Environment Variables:**
```bash
docker exec ai-devops-app env | grep -E "WEAVIATE|OPENAI"
```

**Expected Output:**
```
WEAVIATE_URL=https://ms1b1r79sesauja7ftuz0a.c0.us-west3.gcp.weaviate.cloud
WEAVIATE_API_KEY=VFJ5dW1KR0M4...
WEAVIATE_COLLECTION_NAME=JenkinsKB
OPENAI_API_KEY=sk-svcacct-eQTlz...
```

### Problem: Getting Generic Answers

**Cause:** Knowledge base might be empty or not synced

**Solution:** Run KB Sync to populate Weaviate
```bash
# From local machine
ssh -i "C:/Users/Yashvi/myec2_jenkins.pem" ec2-user@100.30.102.67 \
  "docker exec ai-devops-app bash -c 'cd /app/kb-sync && python kb_sync_agent.py'"
```

### Problem: Slow Response Times (> 10 seconds)

**Possible Causes:**
1. OpenAI API slow
2. Weaviate cluster in different region
3. Large number of chunks being processed

**Check:**
- Look at metadata: Is token count very high?
- Are many chunks being retrieved?
- Is confidence low (requiring more processing)?

---

## ✅ Success Criteria

Your chatbot is working correctly if:

- [x] Chat input is enabled
- [x] Example buttons work
- [x] Custom questions get relevant answers
- [x] Sources are displayed correctly
- [x] Metadata shows reasonable values
- [x] Response time is under 10 seconds
- [x] No error messages appear
- [x] Chat history persists during session
- [x] Clear button works

---

## 📹 Testing Workflow

**Quick 2-Minute Test:**

1. Open http://100.30.102.67:8501
2. Go to "🤖 Knowledge Assistant" tab
3. Click "What causes OutOfMemoryError?" button
4. Wait for response (should be < 10 seconds)
5. Check if answer makes sense
6. Verify sources are shown
7. ✅ **If all works → Chatbot is working!**

**Comprehensive 5-Minute Test:**

1. Test all 4 example questions
2. Ask 2-3 custom questions
3. Check response quality
4. Verify sources for each
5. Check statistics section
6. Clear chat history
7. Ask one more question to verify it still works
8. ✅ **If all works → Chatbot is fully functional!**

---

## 📝 Reporting Issues

If something doesn't work:

1. **Take a screenshot** of the error
2. **Check Docker logs**:
   ```bash
   docker logs ai-devops-app 2>&1 | tail -100
   ```
3. **Note which specific test failed**
4. **Check if environment variables are set** (see above)
5. **Verify services are running**:
   - Flask: http://100.30.102.67:5000/health
   - Streamlit: http://100.30.102.67:8501

---

## 🎉 Next Steps After Successful Testing

Once the chatbot works:

1. **Add More Documents** to Jenkins KB
   - Upload to S3: `s3://jenkins-kb/`
   - Run KB Sync to update Weaviate

2. **Integrate with Your Workflow**
   - Use for troubleshooting build failures
   - Query for configuration help
   - Search Jenkins documentation

3. **Monitor Usage**
   - Check token usage (OpenAI costs)
   - Review query statistics
   - Identify common questions

4. **Expand Knowledge Base**
   - Add Docker troubleshooting docs
   - Include pipeline configuration examples
   - Document common error solutions

---

## 🔗 Quick Links

- **Streamlit UI**: http://100.30.102.67:8501
- **Flask API**: http://100.30.102.67:5000
- **Jenkins**: http://100.30.102.67:8080
- **Chatbot Guide**: CHATBOT_FIX_GUIDE.md
- **IP Update Guide**: UPDATED_IP_ADDRESS.md

---

**Happy Testing! 🚀**

If the chatbot works correctly, you're all set! If you encounter any issues, refer to the troubleshooting section above.
