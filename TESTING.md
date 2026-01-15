# Testing the Pipeline

Quick guide to test the complete GitHub → Jenkins → Deploy pipeline.

## Pre-Test Checklist

Ensure these are ready:

```bash
# 1. Docker Desktop is running
docker ps

# 2. All containers are up
docker-compose ps

# 3. Jenkins is accessible
curl http://localhost:8080

# 4. Streamlit is accessible
curl http://localhost:8501
```

## Test 1: Local Validation

Run the test suite:

```bash
python test_local.py
```

**Expected Result:** All tests PASS
- ✓ File Structure
- ✓ Dependencies
- ✓ Flask App
- ✓ Unit Tests

## Test 2: Manual Jenkins Build

1. Open http://localhost:8080
2. Click on `ai-devops-pipeline`
3. Click **Build with Parameters**
4. Select:
   - BRANCH: `main`
   - ENVIRONMENT: `development`
5. Click **Build**

**Expected Result:**
- ✓ Build starts immediately
- ✓ All stages complete successfully
- ✓ Flask app deployed to port 5001

Verify deployment:
```bash
curl http://localhost:5001/health
# Should return: {"status":"healthy","service":"flask-app"}
```

## Test 3: Streamlit Dashboard Trigger

1. Open http://localhost:8501
2. Configure sidebar:
   - Jenkins URL: `http://jenkins:8080`
   - Username: `admin`
   - Token: (from .env file)
3. Go to **Trigger Jobs** tab
4. Job Name: `ai-devops-pipeline`
5. Click **🚀 Trigger Build**

**Expected Result:**
- ✓ Success message appears
- ✓ Build starts in Jenkins

## Test 4: View Build Logs

In Streamlit dashboard:

1. Go to **Build Logs** tab
2. Job Name: `ai-devops-pipeline`
3. Build Number: `lastBuild`
4. Click **📥 Fetch Logs**

**Expected Result:**
- ✓ Console logs appear
- ✓ Shows all pipeline stages
- ✓ Can see test results

## Test 5: Check Job Status

In Streamlit dashboard:

1. Go to **Job Status** tab
2. Job Name: `ai-devops-pipeline`
3. Click **🔄 Refresh Status**

**Expected Result:**
- ✓ Shows build result (SUCCESS)
- ✓ Displays build number
- ✓ Shows duration
- ✓ Provides build URL

## Test 6: All Jobs View

In Streamlit dashboard:

1. Go to **All Jobs** tab
2. Click **🔄 Load Jobs**

**Expected Result:**
- ✓ Lists all Jenkins jobs
- ✓ Shows status icons
- ✓ Can trigger jobs from list

## Test 7: GitHub Webhook (Optional)

**Prerequisites:**
- ngrok running: `ngrok http 8080`
- GitHub webhook configured

Test the webhook:

```bash
# Make a change
echo "# Webhook test" >> README.md

# Commit and push
git add README.md
git commit -m "Test webhook trigger"
git push
```

**Expected Result:**
- ✓ GitHub webhook delivers successfully
- ✓ Jenkins build starts automatically (within 30 seconds)
- ✓ Build completes successfully
- ✓ Can view in Streamlit dashboard

Check webhook delivery:
1. Go to GitHub → Settings → Webhooks
2. Click on your webhook
3. Check **Recent Deliveries**
4. Should show green checkmark

## Test 8: Different Environments

Test deployment to different environments:

### Development
```bash
# In Jenkins or Streamlit, trigger with ENVIRONMENT=development
# Deployed to port 5001
curl http://localhost:5001/api/info
```

### Staging
```bash
# Trigger with ENVIRONMENT=staging
# Deployed to port 5002
curl http://localhost:5002/api/info
```

### Production
```bash
# Trigger with ENVIRONMENT=production
# Deployed to port 5000
curl http://localhost:5000/api/info
```

**Expected Result:**
- ✓ Each environment runs on different port
- ✓ BUILD_NUMBER env var is set
- ✓ ENVIRONMENT env var matches selection

## Test 9: Pipeline Stages

Verify each stage completes:

1. **Checkout** - Code pulled from GitHub
2. **Install Dependencies** - Python packages installed
3. **Lint** - Code quality checks
4. **Test** - Unit tests pass
5. **Build Docker Image** - Container created
6. **Push to Registry** - (skipped for development)
7. **Deploy** - Container running
8. **Health Check** - App responds correctly

View in Jenkins console output or Streamlit logs.

## Test 10: Error Handling

Test failure scenarios:

### Test Failure
1. Modify flask_app/test_app.py to fail:
```python
assert False  # Intentional failure
```
2. Commit and push
3. Build should fail at Test stage

### Lint Failure
1. Add bad code to flask_app/app.py:
```python
x=1+2  # No spaces
```
2. Build continues (lint errors don't fail build)

### Health Check Failure
1. Modify Jenkinsfile to check wrong port
2. Build should fail at Health Check stage

**Restore after testing!**

## Performance Tests

### Build Time
```bash
# Time a full build
time curl -X POST http://localhost:8080/job/ai-devops-pipeline/build \
  --user admin:YOUR_TOKEN
```

**Expected:** < 3 minutes for development build

### Streamlit Response
```bash
# Test dashboard response time
time curl http://localhost:8501
```

**Expected:** < 2 seconds

## Troubleshooting Tests

If any test fails, check:

### Services Running
```bash
docker-compose ps
# All should be "Up"
```

### Jenkins Logs
```bash
docker-compose logs jenkins | tail -50
```

### Streamlit Logs
```bash
docker-compose logs app | tail -50
```

### Flask App Logs
```bash
docker logs flask-app-dev
```

### Network Connectivity
```bash
# From inside Streamlit container
docker exec ai-devops-app curl http://jenkins:8080

# From host
curl http://localhost:8080
```

## Test Summary Checklist

Mark each test as completed:

- [ ] Test 1: Local Validation
- [ ] Test 2: Manual Jenkins Build
- [ ] Test 3: Streamlit Dashboard Trigger
- [ ] Test 4: View Build Logs
- [ ] Test 5: Check Job Status
- [ ] Test 6: All Jobs View
- [ ] Test 7: GitHub Webhook (Optional)
- [ ] Test 8: Different Environments
- [ ] Test 9: Pipeline Stages
- [ ] Test 10: Error Handling

## Success Criteria

All tests passing means:

✓ **GitHub** - Code pushed successfully
✓ **Jenkins** - Pipeline executes all stages
✓ **Docker** - Images built and containers deployed
✓ **Streamlit** - Dashboard controls and monitors builds
✓ **Flask** - Application running and responding
✓ **Integration** - Complete flow works end-to-end

## Next Steps After Testing

1. Customize pipeline for your needs
2. Add more comprehensive tests
3. Set up production environment
4. Configure monitoring and alerts
5. Document custom workflows

## Quick Reset

If you need to start fresh:

```bash
# Stop everything
docker-compose down -v

# Clean Docker
docker system prune -a -f

# Rebuild
docker-compose up -d --build

# Re-run tests
python test_local.py
```

## Getting Help

If tests fail:
1. Check logs: `docker-compose logs`
2. Review DEPLOYMENT.md troubleshooting section
3. Verify prerequisites are met
4. Check GitHub issues: https://github.com/satishrajv/AI-DevOps-chatbot/issues
