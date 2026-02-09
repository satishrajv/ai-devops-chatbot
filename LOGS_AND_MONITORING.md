# Logs, Containers & Health Monitoring Guide

## 📁 Where Are Logs Stored?

### **1. Jenkins Logs**

#### **Jenkins Build Logs (Console Output)**

**Location on EC2:**
```bash
/var/lib/jenkins/jobs/ai-devops-pipeline/builds/<BUILD_NUMBER>/log
```

**Examples:**
```bash
# Build #4 logs
/var/lib/jenkins/jobs/ai-devops-pipeline/builds/4/log

# Build #5 logs
/var/lib/jenkins/jobs/ai-devops-pipeline/builds/5/log

# Latest build
/var/lib/jenkins/jobs/ai-devops-pipeline/builds/lastSuccessfulBuild/log
```

**How to view:**
```bash
# SSH to EC2
ssh -i "myec2_jenkins.pem" ubuntu@100.30.102.67

# View specific build log
sudo cat /var/lib/jenkins/jobs/ai-devops-pipeline/builds/4/log

# View last 100 lines
sudo tail -100 /var/lib/jenkins/jobs/ai-devops-pipeline/builds/4/log

# Follow live log (if build is running)
sudo tail -f /var/lib/jenkins/jobs/ai-devops-pipeline/builds/lastBuild/log
```

**Via Web UI:**
```
http://100.30.102.67:8080/job/ai-devops-pipeline/4/console
```

---

#### **Jenkins System Logs**

**Location:**
```bash
/var/log/jenkins/jenkins.log    # Main Jenkins log
```

**What's in it:**
- Jenkins startup/shutdown
- Plugin installations
- System errors
- Job scheduling

**How to view:**
```bash
# View Jenkins system log
sudo tail -f /var/log/jenkins/jenkins.log

# Search for errors
sudo grep ERROR /var/log/jenkins/jenkins.log

# Last 50 lines
sudo tail -50 /var/log/jenkins/jenkins.log
```

**Via Web UI:**
```
http://100.30.102.67:8080/log/all
```

---

### **2. Docker Container Logs**

#### **Application Logs (Flask + Streamlit)**

**Location:**
```
Docker stores logs in:
/var/lib/docker/containers/<container-id>/<container-id>-json.log
```

**How to view (EASIER METHOD):**
```bash
# View all logs from your app container
docker logs ai-devops-app

# Follow logs in real-time
docker logs -f ai-devops-app

# Last 100 lines
docker logs --tail 100 ai-devops-app

# Logs from last hour
docker logs --since 1h ai-devops-app

# Logs with timestamps
docker logs -t ai-devops-app
```

**What you'll see:**
```
Starting Flask backend on port 5000...
 * Serving Flask app 'app'
 * Running on http://0.0.0.0:5000

Starting Streamlit frontend on port 8501...
  You can now view your Streamlit app in your browser.
  Network URL: http://0.0.0.0:8501
```

---

#### **Docker Daemon Logs**

**Location:**
```bash
# Ubuntu/Debian
/var/log/docker.log

# Check with journalctl
sudo journalctl -u docker.service
```

**How to view:**
```bash
# Docker service logs
sudo journalctl -u docker.service -f

# Last 100 lines
sudo journalctl -u docker.service -n 100
```

---

## 🗑️ What Happens to Deleted Containers?

### **When You Run: `docker rm ai-devops-app`**

**What gets deleted:**
- ✅ Container filesystem (all changes inside container)
- ✅ Container processes
- ✅ Container metadata

**What stays:**
- ✅ Docker image (ai-devops-app:7 still exists)
- ✅ Docker volumes (if you had any)
- ✅ Container logs (until you run `docker system prune`)

---

### **Container Lifecycle:**

```
1. BUILD (docker build)
   ↓
   Creates: Docker Image (ai-devops-app:7)
   Size: ~500MB
   Location: /var/lib/docker/overlay2/

2. RUN (docker run)
   ↓
   Creates: Docker Container (ai-devops-app)
   Status: Running
   Logs: /var/lib/docker/containers/.../xxx.log

3. STOP (docker stop)
   ↓
   Container: Still exists (stopped)
   Status: Exited
   Logs: Still available

4. REMOVE (docker rm)
   ↓
   Container: DELETED
   Logs: Deleted (unless backed up)
   Image: STILL EXISTS

5. IMAGE REMOVE (docker rmi)
   ↓
   Image: DELETED
   Size freed: ~500MB
```

---

### **Example from Your Pipeline:**

```bash
# Stage 5: Stop Old Containers
docker stop ai-devops-app     # Container still exists (stopped)
docker rm ai-devops-app       # Container deleted (logs gone)

# Stage 6: Deploy Application
docker run -d --name ai-devops-app ai-devops-app:7
# New container created (fresh logs)

# Post stage: Cleanup
docker image prune -f
# Removes old unused images (frees disk space)
```

---

## 📊 How to Check Running Containers

### **Command 1: List Running Containers**

```bash
docker ps
```

**Output:**
```
CONTAINER ID   IMAGE              STATUS        PORTS                    NAMES
b1a1b5f119e7   ai-devops-app:7    Up 2 hours    0.0.0.0:5000->5000/tcp   ai-devops-app
                                                 0.0.0.0:8501->8501/tcp
```

**What it shows:**
- Container ID
- Image used
- How long it's been running
- Ports exposed
- Container name

---

### **Command 2: List ALL Containers (Including Stopped)**

```bash
docker ps -a
```

**Output:**
```
CONTAINER ID   IMAGE              STATUS                    NAMES
b1a1b5f119e7   ai-devops-app:7    Up 2 hours               ai-devops-app
a2b3c4d5e6f7   ai-devops-app:6    Exited (0) 2 hours ago   ai-devops-app-old
```

Shows stopped containers too (if not removed).

---

### **Command 3: Count Running Containers**

```bash
# Count all running containers
docker ps -q | wc -l

# Count your specific app containers
docker ps | grep ai-devops-app | wc -l
```

---

### **Command 4: Detailed Container Info**

```bash
# Full details about container
docker inspect ai-devops-app

# Just get status
docker inspect ai-devops-app | grep Status

# Get IP address
docker inspect ai-devops-app | grep IPAddress

# Get restart count
docker inspect ai-devops-app | grep RestartCount
```

---

## 🏥 Health Check for Containers

### **Method 1: Docker Native Health Check**

**In your Dockerfile (NOT currently implemented):**
```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:5000/health || exit 1
```

**Check health status:**
```bash
docker ps
# Shows: (healthy) or (unhealthy) in STATUS column

docker inspect ai-devops-app | grep Health -A 10
```

---

### **Method 2: Manual Health Checks (What You're Using Now)**

**From EC2:**
```bash
# Check Flask health endpoint
curl http://localhost:5000/health

# Expected response:
{"status":"healthy","service":"flask-app"}

# Check if container is running
docker ps | grep ai-devops-app

# Check if ports are listening
sudo netstat -tulpn | grep 5000
sudo netstat -tulpn | grep 8501
```

**From browser:**
```
http://100.30.102.67:5000/health
http://100.30.102.67:5000/api/info
http://100.30.102.67:8501
```

---

### **Method 3: Container Stats (CPU, Memory, etc.)**

```bash
# Real-time stats for all containers
docker stats

# Stats for specific container
docker stats ai-devops-app

# One-time stats (not continuous)
docker stats --no-stream ai-devops-app
```

**Output:**
```
CONTAINER ID   NAME            CPU %   MEM USAGE / LIMIT   NET I/O
b1a1b5f119e7   ai-devops-app   0.5%    250MB / 4GB         1.2MB / 800KB
```

---

### **Method 4: Check Container Processes**

```bash
# See processes running inside container
docker top ai-devops-app
```

**Output:**
```
PID    USER    COMMAND
1234   root    /bin/bash ./start.sh
1235   root    python app.py
1236   root    streamlit run app.py
```

---

### **Method 5: Check Container Logs for Errors**

```bash
# Look for errors in logs
docker logs ai-devops-app | grep -i error

# Look for startup success messages
docker logs ai-devops-app | grep -i "running\|started"

# Check last 20 lines
docker logs --tail 20 ai-devops-app
```

---

## 🔍 Complete Container Monitoring Script

**Save this as `monitor-containers.sh` on EC2:**

```bash
#!/bin/bash
# Container Monitoring Script

echo "================================================"
echo "🐳 Docker Container Health Check"
echo "================================================"
echo ""

# Check if container is running
echo "1. Container Status:"
docker ps --filter "name=ai-devops-app" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
echo ""

# Check container health
echo "2. Health Check:"
curl -s http://localhost:5000/health | jq . || echo "❌ Health check failed"
echo ""

# Check resource usage
echo "3. Resource Usage:"
docker stats --no-stream ai-devops-app
echo ""

# Check logs for errors
echo "4. Recent Errors (last 10):"
docker logs --tail 100 ai-devops-app 2>&1 | grep -i error | tail -10 || echo "✅ No errors found"
echo ""

# Check running processes
echo "5. Running Processes:"
docker top ai-devops-app
echo ""

# Check disk usage
echo "6. Docker Disk Usage:"
docker system df
echo ""

echo "================================================"
echo "✅ Health check complete!"
echo "================================================"
```

**How to use:**
```bash
# Make executable
chmod +x monitor-containers.sh

# Run it
./monitor-containers.sh
```

---

## 📝 Quick Reference Commands

### **Container Management:**

```bash
# List running containers
docker ps

# List all containers
docker ps -a

# Start stopped container
docker start ai-devops-app

# Stop running container
docker stop ai-devops-app

# Restart container
docker restart ai-devops-app

# Remove container
docker rm ai-devops-app

# Force remove running container
docker rm -f ai-devops-app
```

---

### **Container Logs:**

```bash
# View all logs
docker logs ai-devops-app

# Follow logs (live)
docker logs -f ai-devops-app

# Last 100 lines
docker logs --tail 100 ai-devops-app

# Logs since 1 hour ago
docker logs --since 1h ai-devops-app

# Logs with timestamps
docker logs -t ai-devops-app

# Save logs to file
docker logs ai-devops-app > app-logs.txt
```

---

### **Container Health:**

```bash
# Check if container is running
docker ps | grep ai-devops-app

# Test health endpoint
curl http://localhost:5000/health

# Check resource usage
docker stats ai-devops-app

# Inspect full details
docker inspect ai-devops-app

# Check processes
docker top ai-devops-app

# Execute command inside container
docker exec ai-devops-app ps aux
```

---

### **Jenkins Logs:**

```bash
# View build log (on EC2)
sudo cat /var/lib/jenkins/jobs/ai-devops-pipeline/builds/4/log

# Follow live build log
sudo tail -f /var/lib/jenkins/jobs/ai-devops-pipeline/builds/lastBuild/log

# View Jenkins system log
sudo tail -f /var/log/jenkins/jenkins.log

# Via browser
# http://100.30.102.67:8080/job/ai-devops-pipeline/4/console
```

---

## 🚨 Troubleshooting Scenarios

### **Container Not Running:**

```bash
# Check if container exists
docker ps -a | grep ai-devops-app

# If exited, check why
docker logs ai-devops-app

# Check exit code
docker inspect ai-devops-app | grep ExitCode

# Try to start it
docker start ai-devops-app
```

---

### **Container Running but App Not Accessible:**

```bash
# Check ports
docker ps | grep ai-devops-app
# Should show: 0.0.0.0:5000->5000/tcp

# Test from EC2
curl http://localhost:5000/health

# Check if port is listening
sudo netstat -tulpn | grep 5000

# Check firewall/security group
# AWS Console → EC2 → Security Groups
```

---

### **High CPU/Memory Usage:**

```bash
# Check resource usage
docker stats ai-devops-app

# If too high, restart container
docker restart ai-devops-app

# Check for memory leaks in logs
docker logs ai-devops-app | grep -i "memory\|oom"
```

---

### **Logs Growing Too Large:**

```bash
# Check log size
du -sh /var/lib/docker/containers/*/

# Rotate logs (add to Dockerfile or docker run)
docker run --log-opt max-size=10m --log-opt max-file=3 ...

# Clear old logs manually
sudo truncate -s 0 /var/lib/docker/containers/<container-id>/<container-id>-json.log
```

---

## 📊 Monitoring Dashboard (Optional)

### **Create a Simple Status Page:**

**Save as `status.sh`:**
```bash
#!/bin/bash
watch -n 5 '
  echo "=== Container Status ==="
  docker ps
  echo ""
  echo "=== Resource Usage ==="
  docker stats --no-stream
  echo ""
  echo "=== Recent Logs ==="
  docker logs --tail 5 ai-devops-app
'
```

**Run:** `./status.sh` (updates every 5 seconds)

---

## 🎯 Summary

### **Where Logs Are Stored:**

| Type | Location | Command |
|------|----------|---------|
| Jenkins Build Logs | `/var/lib/jenkins/jobs/.../builds/<#>/log` | Via browser or `sudo cat` |
| Jenkins System Log | `/var/log/jenkins/jenkins.log` | `sudo tail -f` |
| Container Logs | Managed by Docker | `docker logs ai-devops-app` |
| Docker System Logs | `/var/log/docker.log` | `sudo journalctl -u docker` |

### **Container Management:**

| Task | Command |
|------|---------|
| List running | `docker ps` |
| List all | `docker ps -a` |
| View logs | `docker logs ai-devops-app` |
| Health check | `curl http://localhost:5000/health` |
| Resource usage | `docker stats ai-devops-app` |
| Process list | `docker top ai-devops-app` |

### **What Happens on Delete:**

```
docker stop  → Container stopped (logs kept)
docker rm    → Container deleted (logs deleted)
docker rmi   → Image deleted (space freed)
```

---

**You now know how to monitor everything! 🎉**
