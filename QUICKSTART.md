# Quick Start Guide - AI DevOps Platform

This guide will help you get the complete CI/CD pipeline running in minutes.

## Prerequisites

- Docker and Docker Compose installed
- Git installed
- Port 8080, 8501, and 5000 available

## Quick Setup (5 minutes)

### Option 1: Automated Setup (Recommended)

```bash
# Run the setup script
./setup.sh
```

### Option 2: Manual Setup

```bash
# 1. Create .env file
cp .env.example .env

# 2. Start all services
docker-compose up -d --build

# 3. Wait for services to start (2-3 minutes)
docker-compose logs -f
```

## Access the Services

Once containers are running:

1. **Jenkins**: http://localhost:8080
2. **Streamlit Dashboard**: http://localhost:8501
3. **Flask App**: http://localhost:5000

## Jenkins Initial Setup

### 1. Get Initial Admin Password

```bash
docker exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword
```

Copy the password and paste it into Jenkins when prompted.

### 2. Install Suggested Plugins

Click "Install suggested plugins" and wait for installation to complete.

### 3. Create Admin User

Create an admin user account (or skip and continue as admin).

### 4. Generate API Token

1. Click your username in top-right → **Configure**
2. Scroll to **API Token** section
3. Click **Add new Token**
4. Name it `streamlit-access`
5. Click **Generate**
6. Copy the token

### 5. Update .env File

Edit `.env` and add your credentials:

```bash
JENKINS_USER=admin
JENKINS_TOKEN=<paste-your-token-here>
```

### 6. Create Pipeline Job

1. Click **New Item**
2. Enter name: `ai-devops-pipeline`
3. Select **Pipeline**
4. Click **OK**
5. Under **Pipeline** section:
   - Definition: **Pipeline script from SCM**
   - SCM: **Git**
   - Repository URL: `https://github.com/satishrajv/AI-DevOps-chatbot.git`
   - Branch: `*/main`
   - Script Path: `Jenkinsfile`
6. Click **Save**

## Test the Pipeline

### Using Streamlit Dashboard

1. Open http://localhost:8501
2. Enter Jenkins credentials in the sidebar (from .env file)
3. Go to **Trigger Jobs** tab
4. Click **🚀 Trigger Build**
5. Go to **Build Logs** tab
6. Click **📥 Fetch Logs** to view the build output

### Using Jenkins UI

1. Open http://localhost:8080
2. Click on `ai-devops-pipeline`
3. Click **Build with Parameters**
4. Select environment (development/staging/production)
5. Click **Build**

## GitHub Webhook Setup (Auto-trigger on Push)

### 1. Install ngrok (for local testing)

```bash
# Download from https://ngrok.com/download
ngrok http 8080
```

Copy the HTTPS URL (e.g., `https://abc123.ngrok.io`)

### 2. Configure Jenkins Job

1. Open `ai-devops-pipeline` → **Configure**
2. Under **Build Triggers**, check:
   - ✅ **GitHub hook trigger for GITScm polling**
3. Click **Save**

### 3. Add GitHub Webhook

1. Go to https://github.com/satishrajv/AI-DevOps-chatbot
2. Navigate to **Settings** → **Webhooks**
3. Click **Add webhook**
4. Configure:
   - **Payload URL**: `https://your-ngrok-url/github-webhook/`
   - **Content type**: `application/json`
   - **Events**: Select "Just the push event"
5. Click **Add webhook**

### 4. Test Auto-trigger

```bash
# Make a small change
echo "# Test" >> README.md

# Commit and push
git add .
git commit -m "Test webhook trigger"
git push
```

Watch the build start automatically in Jenkins and Streamlit!

## Verify Everything Works

### 1. Check Services are Running

```bash
docker-compose ps
```

All services should show "Up".

### 2. Test Flask App

```bash
curl http://localhost:5000/health
```

Should return: `{"status":"healthy","service":"flask-app"}`

### 3. Test Streamlit Dashboard

Open http://localhost:8501 - you should see the dashboard.

### 4. Trigger a Build

Use Streamlit to trigger a build and verify:
- Build starts successfully
- Logs are visible in the "Build Logs" tab
- Flask app is deployed to a new container

## Common Issues & Solutions

### Jenkins container won't start

```bash
# Check logs
docker-compose logs jenkins

# Restart Jenkins
docker-compose restart jenkins
```

### Can't connect to Jenkins from Streamlit

1. Verify Jenkins is running: `docker ps | grep jenkins`
2. Check Jenkins URL in .env is correct
3. Verify API token is valid

### Docker commands fail in Jenkins

```bash
# Exec into Jenkins container
docker exec -it jenkins bash

# Check Docker is accessible
docker ps

# If not, restart Jenkins
docker-compose restart jenkins
```

### Build fails with "Docker not found"

Jenkins container needs access to Docker socket:
```bash
# Check volume mount
docker inspect jenkins | grep docker.sock
```

## Stopping Services

```bash
# Stop all services
docker-compose down

# Stop and remove volumes (clean slate)
docker-compose down -v
```

## Useful Commands

```bash
# View all logs
docker-compose logs -f

# View Jenkins logs only
docker-compose logs -f jenkins

# Restart a service
docker-compose restart jenkins

# Rebuild containers
docker-compose up -d --build

# Check container status
docker-compose ps
```

## Next Steps

1. Customize the Jenkinsfile for your needs
2. Add more tests to flask_app/test_app.py
3. Configure Docker Hub credentials for image registry
4. Add more monitoring to Streamlit dashboard
5. Set up production deployment

## Support

For issues or questions:
- GitHub: https://github.com/satishrajv/AI-DevOps-chatbot/issues
- Docs: See README.md for detailed documentation
