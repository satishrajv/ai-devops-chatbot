# Test the Pipeline Right Now

Follow these steps to test the complete pipeline locally.

## Step 1: Start Services (5-10 minutes)

The services are building now. You can monitor progress:

```bash
# Check build progress
docker-compose logs -f

# Or check which containers are running
docker ps
```

Wait until you see:
- `jenkins` container running on port 8080
- `ai-devops-app` container running on ports 5000 and 8501

## Step 2: Access Services

Once containers are running, open these URLs:

### Jenkins
**URL:** http://localhost:8080

Get the initial admin password:
```bash
docker exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword
```

Copy this password - you'll need it for Jenkins setup.

### Streamlit Dashboard
**URL:** http://localhost:8501

Should show the AI DevOps Platform dashboard immediately.

### Flask App
**URL:** http://localhost:5000

Should show: `{"message":"Welcome to AI DevOps Platform",...}`

## Step 3: Configure Jenkins (5 minutes)

### 3.1 Initial Setup
1. Open http://localhost:8080
2. Paste the admin password from Step 2
3. Click "Install suggested plugins"
4. Wait for plugins to install
5. Create admin user (or skip and continue as admin)

### 3.2 Create API Token
1. Click your username (top right)
2. Click **Configure**
3. Scroll to **API Token**
4. Click **Add new Token**
5. Name: `streamlit-access`
6. Click **Generate**
7. **COPY THE TOKEN** - you'll need it next

### 3.3 Update .env File
```bash
# Edit .env file
JENKINS_USER=admin
JENKINS_TOKEN=<paste-the-token-you-just-copied>
```

### 3.4 Create Pipeline Job
1. Click **New Item** (left sidebar)
2. Enter name: `ai-devops-pipeline`
3. Select **Pipeline**
4. Click **OK**
5. Scroll to **Pipeline** section
6. Set:
   - Definition: **Pipeline script from SCM**
   - SCM: **Git**
   - Repository URL: `https://github.com/satishrajv/AI-DevOps-chatbot.git`
   - Branch: `*/main`
   - Script Path: `Jenkinsfile`
7. Click **Save**

## Step 4: Test Manual Build (2 minutes)

### Via Jenkins UI:
1. Click on `ai-devops-pipeline`
2. Click **Build Now** (or **Build with Parameters**)
3. If parameters appear:
   - BRANCH: `main`
   - ENVIRONMENT: `development`
4. Click **Build**
5. Watch the build progress (blue ball = running, green = success)

### Expected Result:
- Build should complete in 2-3 minutes
- All stages should pass (green checkmarks)
- Flask app deployed to port 5001

### Verify Deployment:
```bash
# Check if Flask app is running
curl http://localhost:5001/health

# Should return:
# {"status":"healthy","service":"flask-app"}
```

## Step 5: Test Streamlit Dashboard (3 minutes)

### 5.1 Configure Credentials
1. Open http://localhost:8501
2. In the sidebar, enter:
   - **Jenkins URL:** `http://jenkins:8080` (inside container) or `http://localhost:8080` (from host)
   - **Username:** `admin`
   - **Token:** (the token from .env file)

### 5.2 Trigger a Build
1. Go to **Trigger Jobs** tab
2. Job Name: `ai-devops-pipeline`
3. Click **🚀 Trigger Build**
4. Should see success message

### 5.3 View Build Logs
1. Go to **Build Logs** tab
2. Job Name: `ai-devops-pipeline`
3. Build Number: `lastBuild`
4. Click **📥 Fetch Logs**
5. You should see the complete console output!

### 5.4 Check Job Status
1. Go to **Job Status** tab
2. Job Name: `ai-devops-pipeline`
3. Click **🔄 Refresh Status**
4. Should show:
   - Result: SUCCESS
   - Build Number
   - Duration
   - Build URL

## Step 6: Test Different Environments (Optional)

### Development (Port 5001)
```bash
# Trigger with ENVIRONMENT=development
curl http://localhost:5001/api/info
```

### Staging (Port 5002)
In Streamlit or Jenkins, trigger with ENVIRONMENT=staging
```bash
curl http://localhost:5002/api/info
```

### Production (Port 5000)
In Streamlit or Jenkins, trigger with ENVIRONMENT=production
```bash
curl http://localhost:5000/api/info
```

## Quick Verification Checklist

Run these commands to verify everything works:

```bash
# 1. Check all containers are running
docker ps

# 2. Test Jenkins is up
curl http://localhost:8080

# 3. Test Streamlit is up
curl http://localhost:8501

# 4. Test Flask is up
curl http://localhost:5000/health

# 5. Check deployed dev app
curl http://localhost:5001/health
```

## Troubleshooting

### Services won't start
```bash
# Check logs
docker-compose logs

# Restart
docker-compose restart
```

### Can't connect to Jenkins from Streamlit
- Use `http://jenkins:8080` if Streamlit is in Docker
- Use `http://localhost:8080` if running Streamlit locally

### Build fails with "Docker not found"
```bash
# Fix Docker access in Jenkins
docker exec -u root jenkins usermod -aG docker jenkins
docker-compose restart jenkins
```

### Port already in use
```bash
# Find what's using the port
netstat -ano | findstr :8080

# Stop the conflicting service or change port in docker-compose.yml
```

## Success Indicators

You've successfully tested the pipeline when:

✓ Jenkins accessible at http://localhost:8080
✓ Streamlit accessible at http://localhost:8501
✓ Can trigger build from Jenkins UI
✓ Can trigger build from Streamlit dashboard
✓ Can view logs in Streamlit
✓ Flask app responds at http://localhost:5001/health
✓ All pipeline stages complete successfully

## Next: Test GitHub Webhook

To test automatic builds on push, see DEPLOYMENT.md Phase 4.

## Get Help

If you're stuck:
1. Check `docker-compose logs` for errors
2. See DEPLOYMENT.md for detailed troubleshooting
3. Review TESTING.md for comprehensive test procedures
