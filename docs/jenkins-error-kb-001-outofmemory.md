# Jenkins Error Knowledge Base - Document 001

## ERROR-001: Docker Container OutOfMemoryError

---

### 📋 Metadata

| Field | Value |
|-------|-------|
| **Error ID** | ERROR-001 |
| **Error Name** | Docker Container OutOfMemoryError |
| **Category** | Container Resource Management |
| **Severity** | 🔴 High |
| **First Seen** | 2026-01-15 |
| **Last Occurrence** | 2026-01-18 |
| **Frequency** | 2-3 times per week |
| **Document Version** | 1.0 |
| **Created By** | DevOps Team |
| **Last Updated** | 2026-01-19 |

---

### 🎯 Quick Summary

**What happens**: Docker container crashes shortly after deployment due to insufficient memory allocation.

**Impact**: Complete application downtime, build marked as FAILURE, rollback required.

**Quick Fix**: Increase container memory limit from 2GB to 4GB in Jenkinsfile.

**Time to Resolve**: 5-10 minutes (quick fix), 2-4 hours (root cause fix)

---

### 🔍 Symptoms

When this error occurs, you will observe:

- ✅ Build **succeeds** up to the "Deploy Application" stage
- ❌ Container **starts** but crashes within 10-30 seconds
- ❌ Docker logs show memory allocation failures
- ❌ Application becomes **unresponsive** immediately
- ❌ Health checks **fail** at `http://100.30.102.67:5000/health`
- ❌ Streamlit UI unreachable at `http://100.30.102.67:8501`
- ❌ Previous container stopped, new container fails to stay running

**Build Status in Jenkins**: 🔴 FAILURE (at Health Check stage)

---

### 💬 Error Messages

You will see one or more of these error messages in the logs:

#### Python Applications:
```
Exception in thread "main" OSError: [Errno 12] Cannot allocate memory
```

```
MemoryError: Unable to allocate array with shape (10000, 10000) and data type float64
```

```
docker: Error response from daemon: OCI runtime create failed:
container_linux.go:380: starting container process caused:
exec: "python": cannot allocate memory: unknown.
```

#### Java Applications:
```
Exception in thread "main" java.lang.OutOfMemoryError: Java heap space
    at java.util.Arrays.copyOf(Arrays.java:3332)
    at java.lang.AbstractStringBuilder.ensureCapacityInternal(AbstractStringBuilder.java:124)
```

#### Docker Logs:
```
Killed
OOMKilled: true
ExitCode: 137
```

#### Jenkins Console Output:
```
[Pipeline] sh
+ curl -f http://localhost:5000/health
curl: (7) Failed to connect to localhost port 5000: Connection refused
✗ Flask app health check failed
```

---

### 🔬 Root Cause Analysis

#### Primary Causes

**1. Container Memory Limit Too Low** (Most Common)
- Docker container has **2GB** memory limit by default
- Application requires **3-4GB** to run properly
- Container gets killed by OOM (Out Of Memory) killer when limit exceeded

**2. Memory Leak in Application Code**
- Code doesn't release memory after use
- Variables/objects accumulate in memory over time
- Common in image processing, data parsing, caching

**3. Large File/Data Processing**
- Processing images larger than available memory
- Loading entire datasets into RAM instead of streaming
- Batch operations without chunking

**4. Insufficient JVM Heap (Java Apps)**
- Default Java heap settings too small
- No explicit `-Xmx` configuration
- Garbage collection overhead

**5. Resource Exhaustion on EC2 Host**
- Multiple containers competing for memory
- EC2 instance running out of available RAM
- Background processes consuming resources

#### Common Triggers

- ✅ Recent code changes adding memory-intensive operations
- ✅ Increased payload sizes (larger images, bigger datasets)
- ✅ New dependencies with higher memory footprint
- ✅ Multiple builds/containers running simultaneously
- ✅ Dependency version updates (especially ML libraries)

---

### 💥 Impact

#### Immediate Impact
- **Application Availability**: 🔴 100% downtime
- **User Experience**: Complete service outage
- **API Endpoints**: All endpoints unreachable (Flask on port 5000)
- **UI Dashboard**: Streamlit UI down (port 8501)

#### Business Impact
- **CI/CD Pipeline**: Blocks all subsequent deployments
- **Development Team**: Cannot deploy new features/fixes
- **Build Status**: Jenkins build marked as FAILURE
- **Rollback Required**: Must revert to previous working container

#### Affected Components
- Flask backend application
- Streamlit frontend dashboard
- Docker container runtime
- Jenkins health check validation

---

### 🛠️ Resolution Steps

#### Option 1: Quick Fix (5 minutes - Immediate Recovery)

**Step 1**: Update Jenkinsfile to increase memory limit

Edit `Jenkinsfile.ec2-simple` at line 82-91:

**BEFORE:**
```groovy
sh """
    docker run -d \
        --name ai-devops-app \
        --restart unless-stopped \
        -p 5000:5000 \
        -p 8501:8501 \
        -e ENVIRONMENT=production \
        -e BUILD_NUMBER=${BUILD_NUMBER} \
        ai-devops-app:${BUILD_NUMBER}
"""
```

**AFTER:**
```groovy
sh """
    docker run -d \
        --name ai-devops-app \
        --restart unless-stopped \
        --memory="4g" \
        --memory-swap="4g" \
        -p 5000:5000 \
        -p 8501:8501 \
        -e ENVIRONMENT=production \
        -e BUILD_NUMBER=${BUILD_NUMBER} \
        ai-devops-app:${BUILD_NUMBER}
"""
```

**Step 2**: Commit and push changes

```bash
git add Jenkinsfile.ec2-simple
git commit -m "Fix: Increase container memory limit to 4GB to resolve OOM errors"
git push origin main
```

**Step 3**: Trigger new Jenkins build

Go to http://100.30.102.67:8080 and click "Build Now"

**Expected Result**: ✅ Build succeeds, application runs normally

---

#### Option 2: Root Cause Fix (2-4 hours - Long-term Solution)

**For Python Applications:**

**Step 1**: Profile memory usage to find the culprit

Add to your Python code:
```python
import tracemalloc

# Start tracking
tracemalloc.start()

# Your application code here
# ...

# Take snapshot
snapshot = tracemalloc.take_snapshot()
top_stats = snapshot.statistics('lineno')

print("[ Top 10 Memory Consumers ]")
for stat in top_stats[:10]:
    print(stat)
```

**Step 2**: Optimize memory-heavy operations

**Example 1: Image Processing**
```python
# ❌ BEFORE (loads entire 4K image into memory)
from PIL import Image

def process_image(file_path):
    image = Image.open(file_path)  # Loads full resolution
    # Process entire image
    return image

# ✅ AFTER (resize before processing)
from PIL import Image

def process_image(file_path):
    with Image.open(file_path) as img:
        # Resize to reasonable dimensions first
        img.thumbnail((1920, 1080))
        img.save('output.jpg', optimize=True)
    return 'output.jpg'
```

**Example 2: Large File Processing**
```python
# ❌ BEFORE (loads entire file into memory)
with open('large_file.csv', 'r') as f:
    data = f.read()  # Loads entire file
    process(data)

# ✅ AFTER (process line by line)
with open('large_file.csv', 'r') as f:
    for line in f:  # Reads one line at a time
        process(line)
```

**Example 3: Data Caching**
```python
# ❌ BEFORE (unlimited cache)
cache = {}

def get_data(key):
    if key not in cache:
        cache[key] = expensive_operation(key)  # Cache grows forever
    return cache[key]

# ✅ AFTER (limited cache with LRU)
from functools import lru_cache

@lru_cache(maxsize=100)  # Only cache 100 items
def get_data(key):
    return expensive_operation(key)
```

**Step 3**: Test memory usage locally

```bash
# Monitor memory while running
docker stats

# Run with memory limit to test
docker run --memory="2g" ai-devops-app:latest
```

---

**For Java Applications:**

**Step 1**: Set explicit JVM heap size

Update `Dockerfile`:
```dockerfile
# Add JVM options
ENV JAVA_OPTS="-Xms512m -Xmx2g -XX:+UseG1GC"

# Update CMD to use options
CMD java $JAVA_OPTS -jar app.jar
```

**Step 2**: Enable GC logging
```dockerfile
ENV JAVA_OPTS="-Xms512m -Xmx2g -XX:+PrintGCDetails -XX:+PrintGCDateStamps"
```

**Step 3**: Profile with VisualVM or JProfiler

---

### 🛡️ Prevention Strategies

#### 1. Monitoring & Alerting

**Add Resource Monitoring to Jenkinsfile:**

Add this stage before deployment (around line 75):
```groovy
stage('Pre-Deploy Resource Check') {
    steps {
        echo 'Checking system resources...'
        sh '''
            echo "=== Memory Status ==="
            free -h
            echo ""
            echo "=== Running Containers ==="
            docker stats --no-stream
            echo ""
            echo "=== Disk Usage ==="
            df -h
        '''
    }
}
```

**Set up CloudWatch Alarms:**
```bash
aws cloudwatch put-metric-alarm \
    --alarm-name jenkins-ec2-high-memory \
    --alarm-description "Alert when EC2 memory usage exceeds 80%" \
    --metric-name MemoryUtilization \
    --namespace AWS/EC2 \
    --statistic Average \
    --period 300 \
    --threshold 80 \
    --comparison-operator GreaterThanThreshold \
    --evaluation-periods 2
```

#### 2. Best Practices Checklist

**Code Review Guidelines:**
- [ ] Large file operations use streaming/chunking
- [ ] Database connections properly closed after use
- [ ] Image processing resizes before loading into memory
- [ ] Caching has size limits (use LRU cache)
- [ ] Memory-intensive operations have try-finally blocks
- [ ] No global variables accumulating data
- [ ] Batch processing uses pagination

**Dockerfile Guidelines:**
- [ ] Always set explicit memory limits
- [ ] Use multi-stage builds to reduce image size
- [ ] Clean up temporary files in same RUN command
- [ ] Use .dockerignore to exclude unnecessary files
- [ ] Specify resource constraints in docker-compose/Jenkinsfile

**Testing Guidelines:**
- [ ] Load test with production-sized datasets
- [ ] Profile memory usage during CI/CD
- [ ] Test container with production memory limits
- [ ] Monitor memory during stress tests

#### 3. Automated Detection

Add memory check to health endpoint (`flask_app/app.py`):
```python
import psutil

@app.route('/health')
def health():
    memory = psutil.virtual_memory()
    return jsonify({
        "status": "healthy" if memory.percent < 90 else "warning",
        "service": "flask-app",
        "memory_usage_percent": memory.percent,
        "memory_available_mb": memory.available / (1024 * 1024)
    })
```

---

### 🔗 Related Errors

- **ERROR-002**: Container CPU Throttling
- **ERROR-005**: Docker Build OOM Killed During Image Creation
- **ERROR-007**: Python Process Killed - Signal 9
- **ERROR-012**: JVM GC Overhead Limit Exceeded
- **ERROR-018**: EC2 Instance Out of Memory

---

### 📊 Real-World Examples

#### Example 1: Build #10 (2026-01-18)

**Context**: First occurrence after adding image upload feature

**Jenkins Console Output:**
```
[Pipeline] stage
[Pipeline] { (Deploy Application)
[Pipeline] sh
+ docker run -d --name ai-devops-app -p 5000:5000 -p 8501:8501 ai-devops-app:10
ed55a2550e48f218c8e575d5d282fd294836c7f0e1be5e050465ce31d89099f2
[Pipeline] sleep
Sleeping for 10 sec
[Pipeline] sh
+ curl -f http://localhost:5000/health
curl: (7) Failed to connect to localhost port 5000: Connection refused
[Pipeline] error
✗ Flask app health check failed
```

**Docker Logs:**
```bash
$ docker logs ai-devops-app
Loading application...
Initializing Streamlit...
Loading image processor...
OSError: [Errno 12] Cannot allocate memory
Killed
```

**Memory Stats:**
```
Container: ai-devops-app
Memory Usage: 1987MB / 2048MB (97%)
Status: OOMKilled
Exit Code: 137
```

**Resolution**: Increased memory limit to 4GB, build #11 succeeded

---

#### Example 2: Build #52 (2026-01-15)

**Context**: Added new ML model for image classification

**Error:**
```python
Exception in Image Processing:
  File "app.py", line 45, in process_upload
    model = load_model('classifier.h5')  # 2.8GB model file
MemoryError: Unable to allocate 2.8 GiB for array
```

**Root Cause**: TensorFlow model file larger than available container memory

**Fix Applied**:
1. Switched to quantized model (500MB instead of 2.8GB)
2. Implemented lazy loading (load model only when needed)
3. Increased container memory to 4GB

---

### 🏷️ Tags

`jenkins` `docker` `memory` `outofmemory` `oom` `container` `deployment` `python` `java` `resource-management` `devops` `troubleshooting` `ec2` `kubernetes`

---

### 📚 Additional Resources

#### Official Documentation
- [Docker Memory Limits](https://docs.docker.com/config/containers/resource_constraints/)
- [Python tracemalloc Documentation](https://docs.python.org/3/library/tracemalloc.html)
- [Java JVM Memory Settings](https://docs.oracle.com/javase/8/docs/technotes/guides/vm/gctuning/)

#### Internal Resources
- Project Repository: https://github.com/satishrajv/AI-DevOps-chatbot
- Jenkins Dashboard: http://100.30.102.67:8080
- S3 Logs: s3://jenkins-logs-aidevops-2026/jenkins/failures/

#### Tools
- Memory profiling: `tracemalloc` (Python), `VisualVM` (Java)
- Monitoring: `docker stats`, `htop`, CloudWatch
- Log analysis: AWS Athena queries on S3 logs

---

### 📝 Change Log

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0 | 2026-01-19 | Initial document creation | DevOps Team |

---

### ✅ Document Review Checklist

Before marking this document as complete, verify:

- [ ] All sections filled out completely
- [ ] Error messages are exact copies from logs
- [ ] Resolution steps tested and verified
- [ ] Code examples are functional
- [ ] Related errors identified and linked
- [ ] Tags are comprehensive for search
- [ ] Real-world examples include build numbers
- [ ] Prevention strategies are actionable
- [ ] Document metadata is accurate

---

**Document Status**: ✅ Ready for Review

**Next Steps**:
1. Review this document
2. Test resolution steps on test environment
3. Approve and add to Weaviate knowledge base
4. Create template for future error documents
