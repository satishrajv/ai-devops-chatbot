# 🚀 AI DevOps Platform

**Production-ready AI-powered DevOps platform with Jenkins monitoring, RAG chatbot, and knowledge base management.**

**Deploy to EC2 in 10 minutes** | **Uses Weaviate Cloud** | **All-in-One Container**

---

## ⚡ Quick Start - EC2 Deployment (Your Setup)

Deploy all 4 apps to your **existing EC2 instance** `100.30.102.67`:

```bash
# 1. Configure Jenkins credentials (5 secrets)
# 2. Push code
git add .
git commit -m "Deploy full stack to EC2"
git push origin main

# 3. Jenkins auto-deploys
# Access: http://100.30.102.67:8501
```

**What you get**:
- ✅ Flask API (port 5000)
- ✅ Streamlit Dashboard (port 8501)
- ✅ RAG Chatbot (integrated in Streamlit)
- ✅ KB Sync agent (scheduled via Jenkins)
- ✅ Weaviate Cloud connection

**Cost**: $0 EC2 (existing) + $25/month Weaviate + $10-50 OpenAI = **~$35-75/month**

📚 **Complete Guide**: [EC2_SETUP_GUIDE.md](EC2_SETUP_GUIDE.md) | [DEPLOYMENT_SUMMARY.md](DEPLOYMENT_SUMMARY.md)

---

## 📖 What This Platform Does

A Streamlit-based dashboard to trigger and monitor Jenkins CI/CD pipelines, featuring an intelligent RAG (Retrieval-Augmented Generation) chatbot for DevOps troubleshooting.

**Live on your EC2**: http://100.30.102.67:8501

## Project Structure

```
AI-DevOps-chatbot/
├── flask_app/              # Sample Flask application
│   ├── app.py
│   ├── requirements.txt
│   └── Dockerfile
├── streamlit_app/          # Streamlit dashboard
│   ├── app.py
│   ├── requirements.txt
│   └── Dockerfile
├── docker-compose.yml      # Full stack orchestration
├── Jenkinsfile            # CI/CD pipeline definition
├── .env.example           # Environment variables template
└── README.md
```

## Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/satishrajv/AI-DevOps-chatbot.git
cd AI-DevOps-chatbot
```

### 2. Set Up Environment Variables

```bash
cp .env.example .env
# Edit .env with your Jenkins credentials
```

### 3. Start All Services

```bash
docker-compose up -d
```

This starts:
- **Jenkins**: http://localhost:8080
- **Streamlit Dashboard**: http://localhost:8501
- **Flask App**: http://localhost:5000

## Jenkins Setup

### Initial Configuration

1. Access Jenkins at http://localhost:8080
2. Get the initial admin password:
   ```bash
   docker exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword
   ```
3. Install suggested plugins
4. Create an admin user

### Generate API Token

1. Go to **User Menu** → **Configure**
2. Under **API Token**, click **Add new Token**
3. Name it `streamlit-access` and click **Generate**
4. Copy the token to your `.env` file

### Create the Pipeline Job

1. Click **New Item**
2. Enter name: `ai-devops-pipeline`
3. Select **Pipeline** and click OK
4. Under **Pipeline**:
   - Definition: **Pipeline script from SCM**
   - SCM: **Git**
   - Repository URL: `https://github.com/satishrajv/AI-DevOps-chatbot.git`
   - Branch: `*/main`
   - Script Path: `Jenkinsfile`
5. Click **Save**

---

## GitHub Webhook Setup

To trigger Jenkins builds automatically on code push:

### Prerequisites

- Jenkins must be accessible from the internet (use ngrok for local testing)
- GitHub repository admin access

### Step 1: Install Jenkins Plugins

1. Go to **Manage Jenkins** → **Manage Plugins**
2. Install these plugins:
   - GitHub Plugin
   - GitHub Integration Plugin

### Step 2: Configure Jenkins for GitHub

1. Go to **Manage Jenkins** → **Configure System**
2. Find **GitHub** section
3. Add GitHub Server:
   - Name: `GitHub`
   - API URL: `https://api.github.com`
   - Credentials: Add GitHub Personal Access Token (with `repo` and `admin:repo_hook` scopes)

### Step 3: Expose Jenkins (Local Development)

For local Jenkins, use ngrok:

```bash
# Install ngrok
ngrok http 8080
```

Note the HTTPS URL (e.g., `https://abc123.ngrok.io`)

### Step 4: Configure GitHub Webhook

1. Go to your GitHub repository: https://github.com/satishrajv/AI-DevOps-chatbot
2. Navigate to **Settings** → **Webhooks** → **Add webhook**
3. Configure:
   - **Payload URL**: `https://your-jenkins-url/github-webhook/`
     - Local: `https://abc123.ngrok.io/github-webhook/`
     - Production: `https://jenkins.yourdomain.com/github-webhook/`
   - **Content type**: `application/json`
   - **Secret**: (optional) Add a secret for security
   - **Events**: Select **Just the push event** or **Let me select individual events**
     - Recommended events: Push, Pull Request

4. Click **Add webhook**

### Step 5: Enable Webhook in Jenkins Job

1. Open your Jenkins job (`ai-devops-pipeline`)
2. Click **Configure**
3. Under **Build Triggers**, check:
   - **GitHub hook trigger for GITScm polling**
4. Click **Save**

### Step 6: Verify Webhook

1. In GitHub, go to **Settings** → **Webhooks**
2. Click on your webhook
3. Check **Recent Deliveries** for successful pings
4. Push a commit to trigger a build

### Troubleshooting Webhooks

| Issue | Solution |
|-------|----------|
| Webhook shows red X | Check payload URL and Jenkins accessibility |
| 403 Forbidden | Ensure CSRF is configured for webhooks |
| No build triggered | Verify "GitHub hook trigger" is enabled |
| Connection timeout | Check firewall/ngrok configuration |

#### Enable CSRF for Webhooks

1. Go to **Manage Jenkins** → **Configure Global Security**
2. Under **CSRF Protection**, ensure it's enabled
3. Add webhook URL to allowed origins if needed

---

## Using the Streamlit Dashboard

1. Open http://localhost:8501
2. Enter Jenkins credentials in the sidebar
3. Use the tabs to:
   - **Trigger Jobs**: Start builds with optional parameters
   - **Job Status**: Check build results
   - **All Jobs**: View and trigger any Jenkins job

## API Endpoints (Flask App)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Welcome message |
| `/health` | GET | Health check |
| `/api/info` | GET | App information |
| `/api/echo` | POST | Echo JSON payload |

## Development

### Run Flask App Locally

```bash
cd flask_app
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

### Run Streamlit Locally

```bash
cd streamlit_app
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

## Pipeline Stages

The Jenkinsfile defines these stages:

1. **Checkout** - Clone repository
2. **Install Dependencies** - Set up Python environment
3. **Lint** - Run flake8 checks
4. **Test** - Verify app imports
5. **Build Docker Image** - Create container image
6. **Push to Registry** - Upload to Docker Hub (staging/production)
7. **Deploy** - Run container based on environment
8. **Health Check** - Verify deployment

## License

MIT License
