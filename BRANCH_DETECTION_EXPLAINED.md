# How Jenkins Detects Changes in Main Branch

## 🎯 Quick Answer

**Branch detection is specified in TWO places:**

1. **Jenkins UI Configuration** (one-time setup) - Which branch to monitor
2. **Jenkinsfile** (in your code) - Which branch to checkout and build

**Both must match for it to work correctly!**

---

## 📍 Configuration Locations

### **Location 1: Jenkins Job Configuration (UI)**

**Where:** Jenkins Web UI → Job Settings

**When set:** When you created the job (one time)

**What you configured:**

```yaml
Job Type: Pipeline
Definition: Pipeline script from SCM
SCM: Git
Repository URL: https://github.com/satishrajv/AI-DevOps-chatbot.git
Branch Specifier: */main                    ← MONITORS main branch
Script Path: Jenkinsfile.ec2-simple
```

**Purpose:**
- ✅ Tells Jenkins **which branch to poll** for changes
- ✅ Tells Jenkins **which branch to read Jenkinsfile** from
- ✅ Stored in Jenkins server (not in your code)

---

### **Location 2: Jenkinsfile.ec2-simple (Your Code)**

**Where:** Your GitHub repository

**When changed:** Every time you modify the Jenkinsfile

**What's configured:**

```groovy
// Line 10: How often to check
triggers {
    pollSCM('H */5 * * *')  // Check GitHub every 5 hours
}

// Line 19: Which branch to checkout
stage('Checkout') {
    steps {
        checkout([
            $class: 'GitSCM',
            branches: [[name: "*/main"]],  ← CHECKOUTS main branch
            userRemoteConfigs: [[url: 'https://github.com/satishrajv/AI-DevOps-chatbot.git']]
        ])
    }
}
```

**Purpose:**
- ✅ Tells Jenkins **which branch to checkout** when building
- ✅ Tells Jenkins **how often to poll** for changes
- ✅ Defines **what to do** when changes detected
- ✅ Version controlled in Git

---

## 🔄 How They Work Together

### **Step-by-Step Flow:**

```
┌─────────────────────────────────────────────────────────┐
│ Step 1: Jenkins uses UI config to know what to monitor │
│ Config: "Monitor repository main branch"               │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│ Step 2: Jenkinsfile triggers section runs              │
│ Line 10: pollSCM('H */5 * * *')                        │
│ "Check GitHub every 5 hours"                            │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│ Step 3: Jenkins polls GitHub                            │
│ Command: git ls-remote refs/heads/main                  │
│ Checks: Latest commit hash on main branch               │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│ Step 4: New commit detected on main!                    │
│ Last built: 9c675a0                                      │
│ Current:    902e60e  ← NEW!                             │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│ Step 5: Jenkins reads Jenkinsfile from main branch      │
│ UI Config tells it: "Read Jenkinsfile.ec2-simple"      │
│ From branch: main                                        │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│ Step 6: Execute Jenkinsfile stages                      │
│ Line 19: checkout branches: [[name: "*/main"]]         │
│ Downloads code from main branch                         │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│ Step 7: Build, test, deploy from main branch code       │
└─────────────────────────────────────────────────────────┘
```

---

## 🤔 What If Branches Don't Match?

### **Scenario 1: UI monitors `main`, Jenkinsfile checks out `dev`**

```
Jenkins UI Config: Branch Specifier: */main
Jenkinsfile Line 19: branches: [[name: "*/dev"]]
```

**What happens:**
1. ✅ Jenkins polls `main` branch for changes
2. ✅ Detects commit on `main`
3. ✅ Reads Jenkinsfile from `main`
4. ❌ But Jenkinsfile says checkout `dev`!
5. ❌ **BUILD USES CODE FROM DEV, NOT MAIN!**

**Problem:** You pushed to `main`, but build uses `dev` code (confusing!)

---

### **Scenario 2: UI monitors `dev`, Jenkinsfile checks out `main`**

```
Jenkins UI Config: Branch Specifier: */dev
Jenkinsfile Line 19: branches: [[name: "*/main"]]
```

**What happens:**
1. ✅ Jenkins polls `dev` branch for changes
2. ❌ You push to `main` - Jenkins doesn't detect it!
3. ❌ No build triggered

**Problem:** Changes to `main` are ignored!

---

## ✅ Best Practice: Keep Them in Sync

**Always match:**
```
Jenkins UI Config: Branch Specifier: */main
Jenkinsfile Line 19: branches: [[name: "*/main"]]
                                              ^^^^
                                         MUST MATCH!
```

---

## 📝 What Must Be in Jenkinsfile vs UI?

### **Must Be in Jenkinsfile (Version Controlled):**

```groovy
✅ triggers { pollSCM('...') }        // Polling schedule
✅ environment { ... }                 // Environment variables
✅ stages { ... }                      // Build steps
✅ checkout branches                   // Which branch to build
✅ Docker build commands               // What to build
✅ Deployment steps                    // How to deploy
✅ Health checks                       // How to verify
✅ Post actions                        // Cleanup
```

**Why in Jenkinsfile?**
- ✅ Version controlled (track changes)
- ✅ Same across all environments
- ✅ Developers can modify via pull requests
- ✅ Reviewed in code reviews

---

### **Must Be in Jenkins UI (Server Configuration):**

```yaml
✅ Repository URL                     # Which GitHub repo
✅ Branch Specifier                   # Which branch to monitor
✅ Script Path                        # Which Jenkinsfile to use
✅ Credentials                        # GitHub access tokens
✅ Job name                          # Jenkins job name
✅ Build triggers (checkbox)          # Enable/disable polling
```

**Why in UI?**
- ✅ Server-specific settings
- ✅ Security (credentials not in code)
- ✅ One-time setup per Jenkins server
- ✅ Can differ per environment (dev/prod Jenkins)

---

## 🔍 How to Check Your Current Configuration

### **Check Jenkins UI Config:**

1. Go to: http://100.30.102.67:8080/job/ai-devops-pipeline/configure
2. Scroll to **Pipeline** section
3. Look for:
   - **Repository URL:** Should show your GitHub URL
   - **Branch Specifier:** Should show `*/main`
   - **Script Path:** Should show `Jenkinsfile.ec2-simple`

### **Check Jenkinsfile Config:**

```bash
# View your Jenkinsfile
cat Jenkinsfile.ec2-simple | grep -A 3 "branches:"

# Should show:
# branches: [[name: "*/main"]],
```

---

## 🎯 What Triggers a Build?

**For a build to trigger automatically, ALL must be true:**

1. ✅ `pollSCM` is configured in Jenkinsfile (Line 10)
2. ✅ Jenkins UI has "Build Triggers" enabled
3. ✅ New commit exists on monitored branch (`main`)
4. ✅ Polling interval has passed (5 hours)
5. ✅ Jenkins can reach GitHub

**Any missing → No automatic build!**

---

## 💡 Can You Monitor Multiple Branches?

**Yes! Here's how:**

### **Option 1: Monitor Multiple Branches (Same Job)**

**Jenkinsfile:**
```groovy
checkout([
    $class: 'GitSCM',
    branches: [[name: "*/main"], [name: "*/develop"]],  // Multiple branches
    userRemoteConfigs: [[url: 'https://github.com/satishrajv/AI-DevOps-chatbot.git']]
])
```

**Jenkins UI:**
```
Branch Specifier: */main */develop
```

**Result:** Builds trigger for changes on EITHER `main` OR `develop`

---

### **Option 2: Separate Jobs per Branch**

**Better approach for production:**

```
Job 1: ai-devops-pipeline-main
  - Branch Specifier: */main
  - Jenkinsfile: branches: [[name: "*/main"]]

Job 2: ai-devops-pipeline-dev
  - Branch Specifier: */develop
  - Jenkinsfile: branches: [[name: "*/develop"]]
```

**Benefit:** Different environments, different pipelines

---

## 📊 Summary Table

| Configuration | Location | Purpose | Changeable Via |
|--------------|----------|---------|----------------|
| Repository URL | Jenkins UI | Which repo to monitor | UI only |
| Branch Specifier (monitoring) | Jenkins UI | Which branch to poll | UI only |
| Script Path | Jenkins UI | Which Jenkinsfile to read | UI only |
| pollSCM schedule | Jenkinsfile Line 10 | How often to check | Git commit |
| checkout branch | Jenkinsfile Line 19 | Which branch to build | Git commit |
| Build stages | Jenkinsfile Lines 13+ | What to do | Git commit |

---

## ✅ Your Current Setup (Correct!)

**Jenkins UI:**
```
Repository: https://github.com/satishrajv/AI-DevOps-chatbot.git
Branch Specifier: */main
Script Path: Jenkinsfile.ec2-simple
```

**Jenkinsfile.ec2-simple:**
```groovy
Line 10: pollSCM('H */5 * * *')           // Check every 5 hours
Line 19: branches: [[name: "*/main"]]     // Checkout main branch
```

**Result:**
- ✅ Jenkins monitors `main` branch
- ✅ Polls every 5 hours for changes
- ✅ Checkouts and builds from `main`
- ✅ Everything matches! Perfect! 🎉

---

## 🚀 Key Takeaways

1. **Two configurations work together:**
   - Jenkins UI: **Which** branch to monitor
   - Jenkinsfile: **How** to build it

2. **pollSCM in Jenkinsfile controls:**
   - Polling frequency (5 hours)
   - When to check for changes

3. **Branch must match in both places:**
   - UI: `*/main`
   - Jenkinsfile: `*/main`

4. **Not everything goes in Jenkinsfile:**
   - Build logic → Jenkinsfile ✅
   - Repository/credentials → Jenkins UI ✅

5. **Jenkinsfile is version controlled:**
   - Changes tracked in Git
   - Reviewed in PRs
   - Consistent across environments

---

**Your setup is correctly configured to detect changes in the `main` branch!** 🎊
