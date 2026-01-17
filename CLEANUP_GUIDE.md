# File Cleanup Guide

## 📁 Files Analysis

### ✅ **KEEP - Essential Files (Currently Used)**

| File | Purpose | Used By |
|------|---------|---------|
| `Jenkinsfile.ec2-simple` | Active Jenkins pipeline | Jenkins (EC2) |
| `Dockerfile` | Builds Docker image | Jenkins + Docker |
| `start.sh` | Starts Flask + Streamlit | Docker container |
| `requirements.txt` | Python dependencies | Docker build |
| `flask_app/app.py` | Flask API backend | Container runtime |
| `streamlit_app/app.py` | Streamlit dashboard | Container runtime |
| `.env` | Environment variables | Local development |
| `.gitignore` | Git ignore rules | Git |
| `README.md` | Main documentation | GitHub/Users |
| `JENKINS_SETUP_GUIDE.md` | Setup instructions | Users |
| `CODE_FLOW_EXPLAINED.md` | Code flow explanation | Users (NEW) |

### ❌ **DELETE - Obsolete/Unused Files**

| File | Why Delete | Safe to Remove? |
|------|------------|-----------------|
| `Jenkinsfile` | Old version, using `Jenkinsfile.ec2-simple` now | ✅ YES |
| `docker-compose.yml` | Not used on EC2, using manual docker run | ✅ YES |
| `docker-compose.aws.yml` | Not used, using manual docker run | ✅ YES |
| `test_local.py` | Local testing only, not in production | ✅ YES |
| `flask_app/test_app.py` | Test file, not used in pipeline | ✅ YES |
| `setup.sh` | Old setup script, not needed | ✅ YES |
| `setup-ec2.sh` | Already setup, not needed anymore | ⚠️ MAYBE (keep for re-setup) |
| `deploy-to-aws.sh` | Manual deployment, using Jenkins now | ⚠️ MAYBE (backup method) |

### 📚 **CONSOLIDATE - Too Many Documentation Files**

| File | Content | Recommendation |
|------|---------|----------------|
| `AWS_DEPLOYMENT.md` | Detailed AWS setup | ⚠️ Redundant with AWS_QUICKSTART.md |
| `AWS_QUICKSTART.md` | Quick AWS setup | ✅ KEEP (concise) |
| `DEPLOYMENT.md` | Local Docker deployment | ❌ DELETE (using EC2 now) |
| `QUICKSTART.md` | Local quick start | ❌ DELETE (using EC2 now) |
| `TESTING.md` | Testing guide | ❌ DELETE (outdated) |
| `TEST_NOW.md` | Test instructions | ❌ DELETE (outdated) |
| `JENKINS_SETUP_GUIDE.md` | Jenkins setup (EC2) | ✅ KEEP (essential) |
| `CODE_FLOW_EXPLAINED.md` | Code explanation | ✅ KEEP (NEW, essential) |

### 🔧 **OPTIONAL - Keep for Reference**

| File | Purpose | Keep? |
|------|---------|-------|
| `update-security-group.sh` | AWS security group setup | ✅ YES (useful for troubleshooting) |
| `.env.example` | Example environment file | ✅ YES (template) |

---

## 🗑️ Recommended Cleanup Actions

### **Action 1: Delete Obsolete Files**

Safe to delete immediately:
```bash
rm Jenkinsfile                  # Old Jenkins pipeline
rm docker-compose.yml           # Not used
rm docker-compose.aws.yml       # Not used
rm test_local.py                # Test file
rm flask_app/test_app.py        # Test file
rm setup.sh                     # Old setup
rm DEPLOYMENT.md                # Outdated
rm QUICKSTART.md                # Outdated
rm TESTING.md                   # Outdated
rm TEST_NOW.md                  # Outdated
```

### **Action 2: Consolidate Documentation**

Delete redundant docs:
```bash
rm AWS_DEPLOYMENT.md            # Keep AWS_QUICKSTART.md instead
```

### **Action 3: Keep for Backup (Optional)**

If you want backup deployment methods:
```bash
# Keep these (can delete later if never used):
# - setup-ec2.sh
# - deploy-to-aws.sh
```

---

## 📊 Before vs After

### **Before Cleanup: 25+ files**
- Multiple Jenkinsfiles (confusing)
- 6 documentation files (redundant)
- Test files not used
- Docker compose files not used
- Old setup scripts

### **After Cleanup: 15 essential files**
```
AI-DevOps-chatbot/
├── .env                           # Environment variables
├── .env.example                   # Template
├── .gitignore                     # Git ignore
├── Dockerfile                     # Docker build
├── Jenkinsfile.ec2-simple         # Active pipeline
├── requirements.txt               # Python deps
├── start.sh                       # Container startup
├── README.md                      # Main docs
├── JENKINS_SETUP_GUIDE.md         # Setup guide
├── CODE_FLOW_EXPLAINED.md         # Code explanation (NEW)
├── AWS_QUICKSTART.md              # AWS setup
├── update-security-group.sh       # AWS helper
├── flask_app/
│   └── app.py                     # Flask backend
├── streamlit_app/
│   └── app.py                     # Streamlit frontend
└── terraform/                     # (if using Terraform)
```

---

## ✅ Final File Structure (Essential Only)

```
AI-DevOps-chatbot/
│
├── 🐍 Python Application Files
│   ├── flask_app/
│   │   └── app.py                 # Flask REST API
│   └── streamlit_app/
│       └── app.py                 # Streamlit Dashboard
│
├── 🐳 Docker & Deployment
│   ├── Dockerfile                 # Docker image definition
│   ├── start.sh                   # Container startup script
│   └── requirements.txt           # Python dependencies
│
├── 🔧 Jenkins CI/CD
│   └── Jenkinsfile.ec2-simple     # Jenkins pipeline (ACTIVE)
│
├── 📚 Documentation
│   ├── README.md                  # Main documentation
│   ├── JENKINS_SETUP_GUIDE.md     # Jenkins setup
│   ├── CODE_FLOW_EXPLAINED.md     # Code flow (NEW)
│   └── AWS_QUICKSTART.md          # AWS deployment
│
├── 🛠️ Utilities
│   └── update-security-group.sh   # AWS security helper
│
└── ⚙️ Configuration
    ├── .env                       # Environment variables (local)
    ├── .env.example               # Template
    └── .gitignore                 # Git ignore rules
```

---

## 🚀 Cleanup Commands

Execute this to clean up your repository:

```bash
# Navigate to repo
cd /c/code/AI-DevOps-chatbot

# Delete obsolete files
git rm Jenkinsfile
git rm docker-compose.yml
git rm docker-compose.aws.yml
git rm test_local.py
git rm flask_app/test_app.py
git rm setup.sh
git rm DEPLOYMENT.md
git rm QUICKSTART.md
git rm TESTING.md
git rm TEST_NOW.md
git rm AWS_DEPLOYMENT.md

# Commit cleanup
git commit -m "Clean up obsolete files

- Remove old Jenkinsfile (using Jenkinsfile.ec2-simple now)
- Remove unused docker-compose files
- Remove test files not in pipeline
- Remove outdated documentation
- Consolidate to essential files only

Keeping only:
- Active pipeline: Jenkinsfile.ec2-simple
- Essential docs: README, JENKINS_SETUP_GUIDE, CODE_FLOW_EXPLAINED
- AWS docs: AWS_QUICKSTART.md
- Active code: flask_app/app.py, streamlit_app/app.py
"

# Push cleanup
git push origin main
```

---

## ⚠️ Important Notes

1. **Backup First**: Before deleting, ensure Jenkins Build #4 or #5 is working
2. **Active Pipeline**: `Jenkinsfile.ec2-simple` is your ACTIVE pipeline
3. **Don't Delete**: `.env` (contains your secrets, in .gitignore)
4. **Tests**: Removed test files since they're not in your Jenkins pipeline

---

This cleanup will make your repository cleaner and easier to understand! 🎉
