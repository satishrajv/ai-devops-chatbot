# Jenkins EC2 Setup Guide - Simple Version

Complete guide to set up your Jenkins pipeline on EC2 using the simplified Jenkinsfile.

## 📋 Prerequisites Checklist

- ✅ EC2 Instance running (35.174.138.165)
- ✅ Jenkins installed and accessible (http://35.174.138.165:8080)
- ✅ Docker installed on EC2
- ✅ SSH access configured
- ✅ GitHub repository: https://github.com/satishrajv/AI-DevOps-chatbot.git

## 🚀 Quick Start (5 Steps)

### Step 1: Update Security Group Ports

Your EC2 needs ports 5000 and 8501 open for Flask and Streamlit.

**Option A: Using AWS CLI (from your local machine)**
```bash
# Make script executable
chmod +x update-security-group.sh

# Run the script
./update-security-group.sh
```

**Option B: Using AWS Console**
1. Go to EC2 Dashboard → Security Groups
2. Select security group: `sg-0c56c1da72e818832`
3. Click "Edit inbound rules"
4. Add rules:
   - Type: Custom TCP, Port: 5000, Source: 0.0.0.0/0, Description: Flask App
   - Type: Custom TCP, Port: 8501, Source: 0.0.0.0/0, Description: Streamlit
5. Save rules

**Option C: Using AWS CLI Direct Commands**
```bash
# Add Flask port (5000)
aws ec2 authorize-security-group-ingress \
  --group-id sg-0c56c1da72e818832 \
  --protocol tcp \
  --port 5000 \
  --cidr 0.0.0.0/0 \
  --region us-east-1

# Add Streamlit port (8501)
aws ec2 authorize-security-group-ingress \
  --group-id sg-0c56c1da72e818832 \
  --protocol tcp \
  --port 8501 \
  --cidr 0.0.0.0/0 \
  --region us-east-1
```

### Step 2: Verify Docker on EC2

SSH into your EC2 and verify Docker is working:

```bash
ssh -i "myec2_jenkins.pem" ubuntu@35.174.138.165

# Check Docker
docker --version
docker ps

# Check Jenkins can use Docker
sudo -u jenkins docker ps

# If the last command fails, run:
sudo usermod -aG docker jenkins
sudo systemctl restart jenkins
```

### Step 3: Create Jenkins Pipeline Job

1. **Open Jenkins**: http://35.174.138.165:8080
2. **Login** with your admin credentials
3. **Click "New Item"**
4. **Job Configuration:**
   - Enter name: `ai-devops-pipeline`
   - Select: **Pipeline**
   - Click OK

5. **Configure Pipeline:**

   **General Section:**
   - ✅ Check "GitHub project"
   - Project URL: `https://github.com/satishrajv/AI-DevOps-chatbot/`

   **Build Triggers:**
   - ✅ Check "Poll SCM"
   - Schedule: `H/5 * * * *`
   - (This checks GitHub every 5 minutes for changes)

   **Pipeline Section:**
   - Definition: **Pipeline script from SCM**
   - SCM: **Git**
   - Repository URL: `https://github.com/satishrajv/AI-DevOps-chatbot.git`
   - Credentials: *(Leave as "none" for public repo)*
   - Branch Specifier: `*/main`
   - Script Path: `Jenkinsfile.ec2-simple`

6. **Click "Save"**

### Step 4: Test the Pipeline

1. **Trigger First Build:**
   - Click "Build Now" on the job page
   - Watch the build in real-time by clicking on the build number (#1)
   - Click "Console Output" to see logs

2. **Expected Pipeline Stages:**
   - ✓ Checkout
   - ✓ Build Info
   - ✓ Install Dependencies
   - ✓ Lint
   - ✓ Test
   - ✓ Build Docker Image
   - ✓ Stop Old Containers
   - ✓ Deploy Application
   - ✓ Health Check
   - ✓ Display Access Info

3. **First Build Will Take ~3-5 minutes:**
   - Downloads Python dependencies
   - Builds Docker image
   - Deploys application

### Step 5: Verify Deployment

Once the build succeeds, verify your applications are running:

```bash
# Check from EC2
ssh -i "myec2_jenkins.pem" ubuntu@35.174.138.165

# Verify container is running
docker ps | grep ai-devops-app

# Check Flask health
curl http://localhost:5000/health

# Check logs
docker logs ai-devops-app
```

**Access from your browser:**
- Jenkins: http://35.174.138.165:8080
- Flask App: http://35.174.138.165:5000
- Flask Health: http://35.174.138.165:5000/health
- Flask API Info: http://35.174.138.165:5000/api/info
- Streamlit Dashboard: http://35.174.138.165:8501

## 🔄 Automatic Builds

Your pipeline is now configured to automatically build when you push to GitHub:

1. **Make a code change:**
```bash
# On your local machine
cd AI-DevOps-chatbot
echo "# Test" >> README.md
git add README.md
git commit -m "Test auto-build"
git push origin main
```

2. **Wait ~5 minutes** (Poll SCM interval)
3. **Jenkins will automatically:**
   - Detect the change
   - Trigger a new build
   - Deploy the updated application

## 📊 Monitoring Your Pipeline

### View Build History
- Go to Jenkins job page
- See list of all builds with status
- Green = Success, Red = Failure

### View Build Logs
- Click on any build number
- Click "Console Output"
- See full pipeline execution logs

### Check Application Logs
```bash
ssh -i "myec2_jenkins.pem" ubuntu@35.174.138.165
docker logs -f ai-devops-app
```

## 🔧 Troubleshooting

### Build Fails at "Build Docker Image" Stage

**Error:** `permission denied while trying to connect to Docker daemon`

**Solution:**
```bash
ssh -i "myec2_jenkins.pem" ubuntu@35.174.138.165
sudo usermod -aG docker jenkins
sudo systemctl restart jenkins
```

### Build Fails at "Health Check" Stage

**Error:** `Flask app health check failed`

**Solution:**
```bash
# Check container logs
docker logs ai-devops-app

# Check if container is running
docker ps -a | grep ai-devops-app

# Restart container manually
docker restart ai-devops-app

# Check Flask app directly
curl http://localhost:5000/health
```

### Port Already in Use

**Error:** `Bind for 0.0.0.0:5000 failed: port is already allocated`

**Solution:**
```bash
# Find what's using the port
sudo netstat -tulpn | grep 5000

# Stop old container
docker stop ai-devops-app
docker rm ai-devops-app

# Re-run build
```

### Poll SCM Not Working

**Check Jenkins System Log:**
1. Go to Jenkins → Manage Jenkins → System Log
2. Look for SCM polling errors
3. Verify GitHub is accessible from EC2:
```bash
ssh -i "myec2_jenkins.pem" ubuntu@35.174.138.165
curl -I https://github.com/satishrajv/AI-DevOps-chatbot.git
```

## 🎯 Next Steps

### Enable Webhooks (Optional - Instant Builds)

Instead of polling every 5 minutes, GitHub can trigger builds instantly:

1. **Generate Jenkins API Token:**
   - Jenkins → User → Configure
   - API Token → Add new Token
   - Copy token

2. **Configure GitHub Webhook:**
   - Go to: https://github.com/satishrajv/AI-DevOps-chatbot/settings/hooks
   - Add webhook
   - Payload URL: `http://35.174.138.165:8080/github-webhook/`
   - Content type: `application/json`
   - Events: Push events
   - Save

3. **Update Jenkins Job:**
   - Remove "Poll SCM" trigger
   - Add "GitHub hook trigger for GITScm polling"

### Add Notifications

Configure build notifications (email, Slack, etc.):
- Jenkins → Manage Jenkins → Configure System
- Add notification plugins
- Configure in pipeline post section

### Monitor with Streamlit Dashboard

Your Streamlit dashboard can monitor Jenkins:
1. Open: http://35.174.138.165:8501
2. Configure Jenkins credentials in sidebar:
   - URL: http://localhost:8080
   - Username: (your Jenkins user)
   - Token: (generate API token)
3. View and trigger jobs from dashboard

## 📝 File Reference

- **Jenkinsfile.ec2-simple**: The pipeline script (in your repo)
- **Dockerfile**: Builds Flask + Streamlit container
- **start.sh**: Starts both services in container
- **requirements.txt**: Python dependencies

## ✅ Success Checklist

After completing this guide, you should have:
- ✅ Jenkins pipeline job created
- ✅ Automatic builds on GitHub push (every 5 min polling)
- ✅ Flask app deployed and accessible
- ✅ Streamlit dashboard deployed and accessible
- ✅ Health checks passing
- ✅ Build history visible in Jenkins

## 🆘 Need Help?

Common issues and solutions:
1. **Docker permission denied** → Add jenkins to docker group
2. **Port not accessible** → Check security group rules
3. **Build fails at lint** → Ignore for now (won't stop deployment)
4. **Container exits immediately** → Check logs: `docker logs ai-devops-app`
5. **Poll SCM not triggering** → Verify GitHub is accessible

---

**You're now ready to use Jenkins CI/CD with GitHub on AWS! 🚀**
