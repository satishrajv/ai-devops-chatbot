# Complete Code Flow & Architecture Explanation

## 🚀 What Happens When Jenkins Builds Your Code

### **Step 1: Jenkins Pipeline Starts** (`Jenkinsfile.ec2-simple`)

When you push code to GitHub or Jenkins polls every 5 minutes:

```
GitHub (code push)
    ↓
Jenkins detects change
    ↓
Reads Jenkinsfile.ec2-simple
    ↓
Executes pipeline stages sequentially
```

### **Step 2: Pipeline Stages Execution**

#### **Stage 1: Checkout**
- **What it does**: Downloads your code from GitHub
- **Where**: `/var/lib/jenkins/workspace/ai-devops-pipeline/`
- **Files fetched**: All your Python files, Dockerfile, requirements.txt

#### **Stage 2: Build Info**
- **What it does**: Checks Docker and Python versions
- **Purpose**: Verify build environment is ready

#### **Stage 3: Verify Code**
- **What it does**: Checks if required files exist
- **Files checked**:
  - `Dockerfile` ✓
  - `requirements.txt` ✓
  - `flask_app/app.py` ✓
  - `streamlit_app/app.py` ✓

#### **Stage 4: Build Docker Image**
- **What it does**: Creates a Docker container with your apps
- **Docker reads**: `Dockerfile` (line by line)
- **Result**: Image named `ai-devops-app:4` (or build number)

#### **Stage 5: Stop Old Containers**
- **What it does**: Stops any running old version
- **Why**: So we can replace it with the new version

#### **Stage 6: Deploy Application**
- **What it does**: Runs new container with both apps
- **Container starts**: Executes `start.sh`

#### **Stage 7: Health Check**
- **What it does**: Verifies Flask is responding
- **URL checked**: `http://localhost:5000/health`

---

## 🐳 Docker Build Process (`Dockerfile`)

When Docker builds your image, it executes these steps **in order**:

### **Line-by-Line Dockerfile Execution:**

```dockerfile
FROM python:3.11-slim                    # Step 1: Download Python base image
WORKDIR /app                             # Step 2: Create /app directory

COPY requirements.txt .                  # Step 3: Copy requirements file
RUN pip install --no-cache-dir -r requirements.txt  # Step 4: Install ALL Python packages
                                         # This installs: Flask, Streamlit, requests, etc.

COPY flask_app/ ./flask_app/            # Step 5: Copy Flask app code
COPY streamlit_app/ ./streamlit_app/    # Step 6: Copy Streamlit app code
COPY start.sh .                         # Step 7: Copy startup script

RUN chmod +x start.sh                   # Step 8: Make start.sh executable

ENV FLASK_PORT=5000                     # Step 9: Set environment variables
ENV STREAMLIT_PORT=8501
ENV ENVIRONMENT=development
ENV JENKINS_URL=http://localhost:8080

EXPOSE 5000 8501                        # Step 10: Declare ports

CMD ["./start.sh"]                      # Step 11: Define what runs when container starts
```

**Result**: Docker image contains:
- Python 3.11
- All dependencies (Flask, Streamlit, etc.)
- Your Flask app code
- Your Streamlit app code
- Startup script

---

## 🎬 Container Startup (`start.sh`)

When Docker runs the container, it executes `start.sh`:

### **Execution Order:**

```bash
#!/bin/bash

# FIRST: Start Flask backend in background
echo "Starting Flask backend on port 5000..."
cd /app/flask_app && python app.py &
# The '&' means "run in background and continue"

# SECOND: Start Streamlit frontend (runs in foreground)
echo "Starting Streamlit frontend on port 8501..."
cd /app/streamlit_app && streamlit run app.py --server.port=8501 --server.address=0.0.0.0
# This keeps running (foreground process keeps container alive)
```

**Key Points:**
1. Flask starts FIRST (in background)
2. Streamlit starts SECOND (in foreground)
3. Container stays alive as long as Streamlit is running
4. Both apps run simultaneously in the same container

---

## 🐍 Python Code Execution Order

### **1. Flask App (`flask_app/app.py`) - Starts FIRST**

```python
from flask import Flask, jsonify, request
import os

app = Flask(__name__)  # Create Flask application

# Define API endpoints
@app.route('/')
def home():
    return jsonify({
        "message": "Welcome to AI DevOps Platform",
        "version": "1.0.0",
        "status": "running"
    })

@app.route('/health')
def health():
    return jsonify({
        "status": "healthy",
        "service": "flask-app"
    })

@app.route('/api/info')
def info():
    return jsonify({
        "app_name": "AI DevOps Flask App",
        "environment": os.getenv("ENVIRONMENT", "development"),
        "build_number": os.getenv("BUILD_NUMBER", "local")
    })

@app.route('/api/echo', methods=['POST'])
def echo():
    data = request.get_json() or {}
    return jsonify({
        "received": data,
        "status": "success"
    })

# THIS IS THE ENTRY POINT
if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('ENVIRONMENT', 'development') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug)
    # Starts Flask web server on port 5000
```

**What Flask Does:**
- Creates a REST API backend
- Provides endpoints: `/`, `/health`, `/api/info`, `/api/echo`
- Listens on port 5000
- Responds to HTTP requests with JSON

---

### **2. Streamlit App (`streamlit_app/app.py`) - Starts SECOND**

```python
import streamlit as st
import requests
from requests.auth import HTTPBasicAuth
import os

# Page configuration - RUNS FIRST
st.set_page_config(
    page_title="AI DevOps Platform",
    page_icon="🚀",
    layout="wide"
)

# Sidebar configuration
st.sidebar.title("Jenkins Configuration")
jenkins_url = st.sidebar.text_input("Jenkins URL", ...)
jenkins_user = st.sidebar.text_input("Jenkins Username", ...)
jenkins_token = st.sidebar.text_input("Jenkins API Token", type="password", ...)

# Main content
st.title("🚀 AI DevOps Platform")
st.markdown("### Trigger and Monitor Jenkins CI/CD Pipelines - 5 minutes")

# Functions to interact with Jenkins
def trigger_job(job_name, parameters=None):
    # Calls Jenkins API to start a build
    ...

def get_job_status(job_name):
    # Calls Jenkins API to get build status
    ...

def get_build_log(job_name, build_number):
    # Calls Jenkins API to fetch build logs
    ...

# Create tabs for different features
tab1, tab2, tab3, tab4 = st.tabs(["🎯 Trigger Jobs", "📊 Job Status", "📋 All Jobs", "📝 Build Logs"])

# Each tab has interactive buttons and forms
with tab1:
    # Trigger Jenkins jobs
    if st.button("🚀 Trigger Build"):
        result = trigger_job(job_name, parameters)
        st.success("Job triggered!")

with tab2:
    # Check job status
    if st.button("🔄 Refresh Status"):
        status = get_job_status(job_name)
        st.metric("Build Number", status['number'])

# ... more tabs ...
```

**What Streamlit Does:**
- Creates interactive web dashboard
- Connects to Jenkins API
- Allows triggering builds
- Shows build status and logs
- Listens on port 8501
- Provides UI for Jenkins interaction

---

## 🔄 Complete Request Flow

### **When User Accesses Flask (http://100.30.102.67:5000/health):**

```
User Browser
    ↓ HTTP GET /health
Docker Container (ai-devops-app)
    ↓
Flask App (running on port 5000)
    ↓ Executes health() function
    ↓
Returns JSON: {"status": "healthy", "service": "flask-app"}
    ↓
User sees: JSON response
```

### **When User Accesses Streamlit (http://100.30.102.67:8501):**

```
User Browser
    ↓ HTTP GET /
Docker Container (ai-devops-app)
    ↓
Streamlit App (running on port 8501)
    ↓ Renders Python code as HTML
    ↓
Shows interactive dashboard with forms/buttons
    ↓
User clicks "Trigger Build"
    ↓
Streamlit calls trigger_job() function
    ↓
Function makes HTTP request to Jenkins API
    ↓
Jenkins starts build
    ↓
Streamlit shows success message
```

---

## 📦 Dependencies (`requirements.txt`)

**What gets installed in Docker:**

```txt
# Line 1 (commented out)
Flask==3.0.0          # Web framework for REST API
gunicorn==21.2.0      # Production WSGI server (not used in start.sh)

# Streamlit and dependencies
streamlit==1.29.0     # Web dashboard framework
requests==2.31.0      # HTTP library for API calls to Jenkins
```

**These are installed DURING Docker build (Step 4 of Dockerfile)**

---

## 🗂️ File Dependency Map

```
Jenkinsfile.ec2-simple (Jenkins reads this FIRST)
    ↓ Triggers Docker build
    ↓
Dockerfile (Docker reads this SECOND)
    ↓ Copies and uses
    ↓
requirements.txt (Docker installs packages THIRD)
    ↓
    ↓ Docker copies Python files
    ↓
flask_app/app.py (Python file - not executed yet)
streamlit_app/app.py (Python file - not executed yet)
    ↓
    ↓ Docker copies startup script
    ↓
start.sh (FOURTH - executed when container starts)
    ↓ Runs Python files
    ↓
flask_app/app.py (FIFTH - Flask starts in background)
streamlit_app/app.py (SIXTH - Streamlit starts in foreground)
```

---

## 🎯 Summary: What Runs When?

### **Build Time (Jenkins Pipeline):**
1. ✅ Jenkins reads `Jenkinsfile.ec2-simple`
2. ✅ Docker reads `Dockerfile`
3. ✅ pip installs packages from `requirements.txt`
4. ✅ Docker copies all Python files (but doesn't run them)
5. ✅ Docker creates image

### **Runtime (Container Starts):**
1. ✅ Container executes `start.sh`
2. ✅ `start.sh` runs `flask_app/app.py` (background)
3. ✅ `start.sh` runs `streamlit_app/app.py` (foreground)
4. ✅ Both apps now running and accepting requests

### **User Interaction:**
- User visits Flask: http://100.30.102.67:5000 → Flask handles request
- User visits Streamlit: http://100.30.102.67:8501 → Streamlit handles request
- Streamlit can call Jenkins API to trigger builds
- Jenkins builds run this entire cycle again!

---

## 🔑 Key Concepts

**1. Background vs Foreground:**
- Flask runs in background (`&` symbol in start.sh)
- Streamlit runs in foreground (keeps container alive)
- If Streamlit crashes, container stops

**2. Port Mapping:**
- Container port 5000 → EC2 port 5000 (Flask)
- Container port 8501 → EC2 port 8501 (Streamlit)
- EC2 port 8080 → Jenkins (not in container)

**3. Environment Variables:**
- Set in Dockerfile: `ENV FLASK_PORT=5000`
- Overridden in Jenkins: `-e BUILD_NUMBER=4`
- Read in Python: `os.getenv("BUILD_NUMBER")`

**4. Docker Layers:**
- Each Dockerfile step creates a layer
- Layers are cached for faster rebuilds
- Changing code only rebuilds affected layers

---

## ❓ Common Questions

**Q: Which Python file runs first?**
A: `flask_app/app.py` (started by start.sh with `&`)

**Q: How does Streamlit talk to Jenkins?**
A: Uses Python `requests` library to call Jenkins REST API

**Q: Where does the code run?**
A: Inside Docker container on EC2 instance

**Q: What keeps the container running?**
A: Streamlit running in foreground (last command in start.sh)

**Q: How does Jenkins know when to build?**
A: Polls GitHub every 5 minutes (set in Jenkinsfile: `pollSCM('H/5 * * * *')`)

---

**This is your complete CI/CD flow from code push to running application!** 🚀
