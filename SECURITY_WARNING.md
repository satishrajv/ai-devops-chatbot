# 🔒 SECURITY WARNING - CRITICAL ACTION REQUIRED

## ⚠️ Exposed Credentials Detected

During the folder structure review, **real credentials were found committed to the repository**. This is a **CRITICAL SECURITY ISSUE** that requires immediate action.

---

## 🚨 Affected Files

### 1. `/kb-sync/.env` - **CRITICAL**
**Status**: Contains real AWS keys, OpenAI API key, and Weaviate credentials

**Immediate Actions Required**:
```bash
# 1. Remove from git tracking (but keep local file)
git rm --cached kb-sync/.env

# 2. Add to .gitignore (already done)
echo "kb-sync/.env" >> .gitignore

# 3. Rotate ALL exposed credentials immediately:
#    - AWS Access Keys (IAM console)
#    - OpenAI API Key (OpenAI dashboard)
#    - Weaviate API Key (Weaviate console)

# 4. Copy .env.example to .env and fill with NEW credentials
cp kb-sync/.env.example kb-sync/.env
```

### 2. `/streamlit_app/app.py` - **FIXED**
**Status**: ✅ Fixed - Now uses environment variables

**Previous Issue**: Jenkins credentials were hardcoded at lines 23-26
- Jenkins URL: `http://100.30.102.67:8080`
- Jenkins User: `admin`
- Jenkins Token: `0b94639151854a66bf03c6467e5a7101`

**Action Required**: Rotate Jenkins API token
```bash
# 1. Log into Jenkins at http://100.30.102.67:8080
# 2. Go to User > Configure > API Token
# 3. Revoke token: 0b94639151854a66bf03c6467e5a7101
# 4. Generate new token
# 5. Set in environment variables (see below)
```

---

## 🛡️ Secure Setup Guide

### For kb-sync System

```bash
cd C:/code/AI-DevOps-chatbot/kb-sync

# 1. Copy example file
cp .env.example .env

# 2. Edit .env with your NEW credentials (use vi, nano, or notepad)
nano .env

# 3. Verify .env is in .gitignore
git check-ignore .env  # Should output: .env
```

### For Streamlit App

```bash
cd C:/code/AI-DevOps-chatbot/streamlit_app

# 1. Copy example file
cp .env.example .env

# 2. Edit .env with your credentials
nano .env

# 3. Set the following:
JENKINS_URL=http://100.30.102.67:8080
JENKINS_USER=admin
JENKINS_TOKEN=<your_new_jenkins_token_here>
OPENAI_API_KEY=<your_openai_api_key>
WEAVIATE_URL=<your_weaviate_url>
WEAVIATE_API_KEY=<your_weaviate_key>
```

### For kb-rag System

```bash
cd C:/code/AI-DevOps-chatbot/kb-rag

# Already has .env.template, just copy it
cp .env.template .env

# Edit with your credentials
nano .env
```

---

## 🔐 Credential Rotation Checklist

### AWS Credentials
- [ ] Go to AWS IAM Console
- [ ] Navigate to Security Credentials
- [ ] Find access key: `<exposed_key_id>`
- [ ] Click "Make Inactive" then "Delete"
- [ ] Generate new access key
- [ ] Update `kb-sync/.env` with new key

### OpenAI API Key
- [ ] Go to https://platform.openai.com/api-keys
- [ ] Find and revoke exposed key
- [ ] Generate new key
- [ ] Update both `kb-sync/.env` and `streamlit_app/.env`

### Weaviate API Key
- [ ] Log into Weaviate Console
- [ ] Navigate to API Keys
- [ ] Revoke exposed key
- [ ] Generate new key
- [ ] Update both `kb-sync/.env` and `streamlit_app/.env`

### Jenkins API Token
- [ ] Log into Jenkins: http://100.30.102.67:8080
- [ ] Go to User (admin) > Configure
- [ ] Navigate to API Token section
- [ ] Revoke token: `0b94639151854a66bf03c6467e5a7101`
- [ ] Generate new token
- [ ] Update `streamlit_app/.env`

---

## 📋 Git Repository Cleanup

### Remove sensitive files from git history

```bash
cd C:/code/AI-DevOps-chatbot

# 1. Remove .env from tracking (keep local file)
git rm --cached kb-sync/.env
git rm --cached streamlit_app/.env 2>/dev/null || true

# 2. Commit the removal
git add .gitignore
git commit -m "security: Remove .env files from git tracking and update .gitignore"

# 3. Check status
git status  # Should not show any .env files

# 4. Verify .env files are ignored
git check-ignore kb-sync/.env
git check-ignore streamlit_app/.env
```

**⚠️ IMPORTANT**: Removing files from current commits does NOT remove them from git history. If this is a public repository or shared with others, consider:

1. **Rewriting git history** (advanced, can break collaborators' repos):
```bash
# Use BFG Repo-Cleaner or git filter-branch
# See: https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository
```

2. **If hosted on GitHub/GitLab**: Contact support to purge cache
3. **Consider rotating ALL credentials** as a precaution

---

## 🎯 Prevention Measures

### Updated .gitignore
The `.gitignore` file has been updated to prevent future credential leaks:

```gitignore
# Environment files - NEVER commit these!
.env
.env.local
.env.*.local
*.env
*/.env
kb-sync/.env
streamlit_app/.env
kb-rag/.env
```

### Pre-commit Hook (Recommended)

Install a pre-commit hook to prevent accidental commits:

```bash
# Install pre-commit
pip install pre-commit

# Create .pre-commit-config.yaml
cat > .pre-commit-config.yaml << 'EOF'
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: detect-private-key
      - id: check-added-large-files
      - id: detect-aws-credentials
  - repo: https://github.com/Yelp/detect-secrets
    rev: v1.4.0
    hooks:
      - id: detect-secrets
        args: ['--baseline', '.secrets.baseline']
EOF

# Install the hooks
pre-commit install

# Test
pre-commit run --all-files
```

### Environment Variable Best Practices

1. **Never commit .env files** - Use .env.example instead
2. **Use placeholder values** in .env.example
3. **Document all required variables** in README
4. **Rotate credentials regularly** (every 90 days)
5. **Use different credentials** for dev/staging/prod
6. **Enable MFA** on all cloud accounts
7. **Use secrets management** (AWS Secrets Manager, HashiCorp Vault) for production

---

## 📚 Documentation Updates

### Updated Files

| File | Action | Status |
|------|--------|--------|
| `streamlit_app/app.py` | Removed hardcoded credentials | ✅ Fixed |
| `streamlit_app/.env.example` | Created template | ✅ New |
| `.gitignore` | Enhanced with comprehensive patterns | ✅ Updated |
| `kb-sync/.env.example` | Copied from config/.env.template | ✅ New |
| `SECURITY_WARNING.md` | Created this document | ✅ New |

### How to Use Environment Variables

**Before** (insecure):
```python
jenkins_url = "http://100.30.102.67:8080"
jenkins_user = "admin"
jenkins_token = "0b94639151854a66bf03c6467e5a7101"
```

**After** (secure):
```python
import os
from dotenv import load_dotenv

load_dotenv()  # Load from .env file

jenkins_url = os.getenv("JENKINS_URL")
jenkins_user = os.getenv("JENKINS_USER")
jenkins_token = os.getenv("JENKINS_TOKEN")

if not all([jenkins_url, jenkins_user, jenkins_token]):
    raise ValueError("Missing required Jenkins credentials in environment variables")
```

---

## 🚀 Running Applications Securely

### Streamlit App

```bash
cd streamlit_app

# Option 1: Using .env file (recommended for local dev)
cp .env.example .env
# Edit .env with your credentials
streamlit run app.py

# Option 2: Using environment variables (recommended for production)
export JENKINS_URL="http://100.30.102.67:8080"
export JENKINS_USER="admin"
export JENKINS_TOKEN="your_new_token_here"
export OPENAI_API_KEY="your_key_here"
streamlit run app.py
```

### KB-Sync System

```bash
cd kb-sync

# Copy and edit .env
cp .env.example .env
nano .env

# Run the sync
python kb_sync_agent.py
```

### Docker Deployment

```dockerfile
# Never include .env in Docker images
# Use --env-file or docker-compose environment

docker run -d \
  --env-file .env \
  your-app-image
```

Or with docker-compose:
```yaml
services:
  app:
    image: your-app
    env_file:
      - .env  # .env is NOT in the image, just mounted at runtime
```

---

## 📞 Incident Response

If credentials were already exposed in a public repository:

### Immediate (within 1 hour)
- [ ] Rotate ALL exposed credentials
- [ ] Remove .env files from git tracking
- [ ] Update .gitignore
- [ ] Check access logs for unauthorized use (AWS CloudTrail, OpenAI usage logs)

### Short-term (within 24 hours)
- [ ] Audit all resources for unauthorized changes
- [ ] Review security groups and access policies
- [ ] Enable CloudWatch alarms for unusual activity
- [ ] Document the incident
- [ ] Notify stakeholders if breach detected

### Long-term (within 1 week)
- [ ] Implement pre-commit hooks
- [ ] Set up secrets scanning in CI/CD
- [ ] Review and update security policies
- [ ] Schedule regular security audits
- [ ] Consider BFG Repo-Cleaner for git history cleanup

---

## ✅ Verification Steps

After implementing fixes:

```bash
# 1. Verify .env files are not tracked
git ls-files | grep "\.env$"  # Should return nothing

# 2. Verify .env files are ignored
git check-ignore */\.env  # Should list all .env locations

# 3. Verify no hardcoded credentials in code
grep -r "api.*key.*=" --include="*.py" --exclude-dir=venv
grep -r "token.*=" --include="*.py" --exclude-dir=venv

# 4. Test application with environment variables
cd streamlit_app
streamlit run app.py  # Should fail if .env not set
# Then create .env and try again

# 5. Verify credentials work
# Test Jenkins API connection
# Test OpenAI API connection
# Test Weaviate connection
```

---

## 🎓 Security Training Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [GitHub Security Best Practices](https://docs.github.com/en/code-security)
- [AWS Security Best Practices](https://aws.amazon.com/security/best-practices/)
- [Secrets Management Guide](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html)

---

## 📌 Summary

**What Was Fixed**:
- ✅ Removed hardcoded Jenkins credentials from `streamlit_app/app.py`
- ✅ Created `.env.example` files for all applications
- ✅ Enhanced `.gitignore` to prevent future credential leaks
- ✅ Documented security issue and remediation steps

**What You Must Do**:
1. **IMMEDIATELY**: Rotate all exposed credentials (AWS, OpenAI, Weaviate, Jenkins)
2. Remove `.env` files from git tracking
3. Create local `.env` files with NEW credentials
4. Test all applications with new credentials
5. Consider implementing pre-commit hooks

**Prevention**:
- Never commit `.env` files
- Always use `.env.example` with placeholder values
- Use environment variables in code, not hardcoded values
- Rotate credentials regularly
- Enable MFA on all accounts

---

🔒 **Security is everyone's responsibility. Stay vigilant!**
