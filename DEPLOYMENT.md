# Deployment Guide - AI DevOps Platform

Complete guide for deploying the GitHub → Jenkins → Local Deploy pipeline with Streamlit UI.

## Architecture Overview

```
GitHub Repository
       ↓ (webhook trigger)
Jenkins CI/CD Server
       ↓ (build & test)
Docker Container
       ↓ (deploy)
Flask Application
       ↑ (monitor & control)
Streamlit Dashboard
```

## Prerequisites

### Required Software
- Docker Desktop (with Docker Compose)
- Git
- Python 3.11+ (for local testing)
- ngrok (optional, for GitHub webhooks with local Jenkins)

### Required Ports
- 8080 - Jenkins
- 8501 - Streamlit Dashboard
- 5000 - Flask App (Production)
- 5001 - Flask App (Development)
- 5002 - Flask App (Staging)

## Step-by-Step Deployment

### Phase 1: Local Setup (10 minutes)

#### 1.1 Clone Repository

```bash
git clone https://github.com/satishrajv/AI-DevOps-chatbot.git
cd AI-DevOps-chatbot
```

#### 1.2 Run Local Tests

```bash
# Install dependencies
pip install -r requirements.txt

# Run test suite
python test_local.py
```

Expected output: All tests should PASS.

#### 1.3 Start Services

**Option A: Using setup script (recommended)**
```bash
chmod +x setup.sh
./setup.sh
```

**Option B: Manual start**
```bash
# Start Docker Desktop first!

# Build and start services
docker-compose up -d --build

# View logs
docker-compose logs -f
```

Wait 2-3 minutes for Jenkins to fully start.

### Phase 2: Jenkins Configuration (15 minutes)

#### 2.1 Initial Jenkins Setup

1. Get initial admin password:
```bash
docker exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword
```

2. Open http://localhost:8080
3. Paste the password
4. Click "Install suggested plugins"
5. Create admin user (or skip and use admin)
6. Click "Save and Finish"

#### 2.2 Verify Docker in Jenkins

```bash
# Check Docker is accessible from Jenkins
docker exec -u root jenkins docker ps
```

Should show list of running containers.

#### 2.3 Create API Token

1. Click username → **Configure**
2. Scroll to **API Token**
3. Click **Add new Token**
4. Name: `streamlit-access`
5. Click **Generate**
6. Copy the token

#### 2.4 Update Environment Variables

Edit `.env` file:
```bash
JENKINS_USER=admin
JENKINS_TOKEN=<paste-your-token-here>
```

Restart Streamlit to pick up changes:
```bash
docker-compose restart app
```

#### 2.5 Create Pipeline Job

1. Click **New Item**
2. Name: `ai-devops-pipeline`
3. Type: **Pipeline**
4. Click **OK**

Configure the pipeline:

**General:**
- ✅ GitHub project
- Project URL: `https://github.com/satishrajv/AI-DevOps-chatbot/`

**Build Triggers:**
- ✅ GitHub hook trigger for GITScm polling

**Pipeline:**
- Definition: **Pipeline script from SCM**
- SCM: **Git**
- Repository URL: `https://github.com/satishrajv/AI-DevOps-chatbot.git`
- Credentials: (none for public repo)
- Branch: `*/main`
- Script Path: `Jenkinsfile`

Click **Save**.

### Phase 3: Test Pipeline (5 minutes)

#### 3.1 Manual Trigger from Jenkins

1. Open `ai-devops-pipeline` job
2. Click **Build with Parameters**
3. Select:
   - BRANCH: `main`
   - ENVIRONMENT: `development`
4. Click **Build**

Watch the build execute through all stages.

#### 3.2 Trigger from Streamlit Dashboard

1. Open http://localhost:8501
2. Enter Jenkins credentials in sidebar:
   - URL: `http://jenkins:8080` (or `http://localhost:8080`)
   - Username: `admin`
   - Token: (from .env)
3. Go to **Trigger Jobs** tab
4. Job Name: `ai-devops-pipeline`
5. Click **🚀 Trigger Build**

#### 3.3 View Build Logs

In Streamlit:
1. Go to **Build Logs** tab
2. Job Name: `ai-devops-pipeline`
3. Build Number: `lastBuild`
4. Click **📥 Fetch Logs**

You should see the complete console output!

#### 3.4 Verify Deployment

```bash
# Check deployed Flask app
curl http://localhost:5001/health

# Should return:
# {"status":"healthy","service":"flask-app"}
```

### Phase 4: GitHub Webhook (Optional - Auto-trigger)

This enables automatic builds on every push to GitHub.

#### 4.1 Expose Jenkins (Local Development)

Install and run ngrok:
```bash
# Download from https://ngrok.com/download
ngrok http 8080
```

Copy the HTTPS URL (e.g., `https://abc123.ngrok.io`)

#### 4.2 Configure GitHub Webhook

1. Go to https://github.com/satishrajv/AI-DevOps-chatbot/settings/hooks
2. Click **Add webhook**
3. Configure:
   - **Payload URL**: `https://your-ngrok-url/github-webhook/`
   - **Content type**: `application/json`
   - **Secret**: (leave empty)
   - **Events**: Just the push event
   - ✅ Active
4. Click **Add webhook**

#### 4.3 Test Webhook

Make a small change and push:
```bash
echo "# Test webhook" >> README.md
git add README.md
git commit -m "Test webhook trigger"
git push
```

Watch Jenkins automatically start a build!

## Verification Checklist

Use this checklist to verify everything is working:

- [ ] Jenkins accessible at http://localhost:8080
- [ ] Streamlit accessible at http://localhost:8501
- [ ] Flask app accessible at http://localhost:5000
- [ ] Docker containers running: `docker-compose ps`
- [ ] Jenkins can execute Docker: `docker exec jenkins docker ps`
- [ ] Pipeline job exists in Jenkins
- [ ] Can trigger build from Jenkins UI
- [ ] Can trigger build from Streamlit UI
- [ ] Can view logs in Streamlit
- [ ] Deployed Flask app responds to health checks
- [ ] GitHub webhook delivers successfully (if configured)
- [ ] Push to GitHub triggers auto-build (if configured)

## Troubleshooting

### Services Won't Start

```bash
# Check Docker is running
docker ps

# View service logs
docker-compose logs jenkins
docker-compose logs app

# Restart services
docker-compose restart

# Full reset
docker-compose down -v
docker-compose up -d --build
```

### Jenkins Can't Access Docker

```bash
# Fix permissions
docker exec -u root jenkins usermod -aG docker jenkins
docker-compose restart jenkins
```

### Streamlit Can't Connect to Jenkins

1. Check Jenkins URL in sidebar (use `http://jenkins:8080` inside container)
2. Verify API token is correct
3. Test from command line:
```bash
curl -u admin:YOUR_TOKEN http://localhost:8080/api/json
```

### Build Fails

Common issues:

**"Docker not found"**
- Jenkins needs Docker CLI installed
- Check `jenkins.Dockerfile` includes Docker installation
- Restart Jenkins: `docker-compose restart jenkins`

**"Permission denied on docker.sock"**
```bash
docker exec -u root jenkins chmod 666 /var/run/docker.sock
```

**"Port already in use"**
- Another container using the port
- Check: `docker ps`
- Stop conflicting container or change port in docker-compose.yml

### GitHub Webhook Not Working

1. Check webhook delivery in GitHub settings
2. Verify ngrok is running and URL is correct
3. Check Jenkins job has "GitHub hook trigger" enabled
4. Test webhook manually:
```bash
curl -X POST https://your-ngrok-url/github-webhook/
```

## Production Deployment

For production deployment:

### 1. Use External Jenkins Server

Replace `jenkins` service in docker-compose.yml with external URL:
```yaml
environment:
  - JENKINS_URL=https://jenkins.yourcompany.com
```

### 2. Add Docker Registry

For pushing images:

1. Create Docker Hub account
2. Add credentials to .env:
```bash
DOCKER_USER=yourusername
DOCKER_PASS=yourpassword
```

3. Add credentials to Jenkins:
   - Manage Jenkins → Credentials
   - Add Username/Password
   - ID: `docker-hub-credentials`

### 3. Configure SSL/TLS

Use reverse proxy (nginx/traefik) for HTTPS:
```yaml
services:
  nginx:
    image: nginx:alpine
    ports:
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./certs:/etc/nginx/certs
```

### 4. Add Monitoring

Integrate with Prometheus/Grafana:
```yaml
services:
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
```

## Maintenance

### Update Services

```bash
# Pull latest changes
git pull

# Rebuild and restart
docker-compose up -d --build
```

### Backup Jenkins Data

```bash
# Backup Jenkins home
docker cp jenkins:/var/jenkins_home ./jenkins_backup

# Restore
docker cp ./jenkins_backup jenkins:/var/jenkins_home
```

### Clean Up

```bash
# Remove old builds
docker system prune -a

# Remove unused volumes
docker volume prune
```

## Support & Resources

- **GitHub**: https://github.com/satishrajv/AI-DevOps-chatbot
- **Quick Start**: See QUICKSTART.md
- **Main README**: See README.md

## Summary

You now have a complete CI/CD pipeline:

1. **Code Changes** → Push to GitHub
2. **GitHub Webhook** → Triggers Jenkins
3. **Jenkins Pipeline** → Builds, tests, and deploys
4. **Streamlit Dashboard** → Monitors and controls
5. **Flask Application** → Deployed and running

**Next Steps:**
- Customize Jenkinsfile for your needs
- Add more tests to flask_app/test_app.py
- Enhance Streamlit dashboard with metrics
- Set up production deployment
