# Storing Jenkins & Docker Logs in AWS S3

## 💰 Cost Comparison

| Solution | Cost | Storage | Search | Retention |
|----------|------|---------|--------|-----------|
| **Splunk** | $150-$2000/GB/year | ✅ | ✅ Excellent | ✅ |
| **S3 + Athena** | $0.023/GB/month | ✅ | ✅ Good | ✅ |
| **CloudWatch** | $0.50/GB ingestion + $0.03/GB storage | ✅ | ⚠️ Limited | ✅ |
| **ELK Stack** | Self-hosted (~$50-200/month) | ✅ | ✅ Excellent | ✅ |

**For small projects: S3 is the best choice! 💰**

**Example:** 10GB logs/month = **$0.23/month in S3** vs **$1,500-20,000/year in Splunk**

---

## 🎯 Solution Overview

### **What We'll Store in S3:**

1. **Jenkins Build Logs** - Every build's console output
2. **Docker Container Logs** - Application runtime logs
3. **Jenkins System Logs** - Jenkins server logs

### **S3 Bucket Structure:**

```
s3://your-company-logs/
├── jenkins/
│   ├── builds/
│   │   ├── 2026/01/17/
│   │   │   ├── build-4-20260117-120000.log
│   │   │   ├── build-5-20260117-130000.log
│   │   │   └── build-6-20260117-140000.log
│   │   └── 2026/01/18/
│   │       └── build-7-20260118-080000.log
│   └── system/
│       └── 2026/01/17/
│           └── jenkins-system-20260117.log
└── docker/
    └── ai-devops-app/
        └── 2026/01/17/
            ├── app-20260117-120000.log
            ├── app-20260117-130000.log
            └── app-20260117-140000.log
```

---

## 📦 Implementation Methods

### **Method 1: Add S3 Upload to Jenkinsfile (Recommended)**

**Add this stage to your Jenkinsfile after "Display Access Info":**

```groovy
stage('Upload Logs to S3') {
    steps {
        script {
            def timestamp = new Date().format('yyyyMMdd-HHmmss')
            def logPath = "/var/lib/jenkins/jobs/ai-devops-pipeline/builds/${BUILD_NUMBER}/log"
            def s3Bucket = "your-company-logs"  // Change this!
            def s3Key = "jenkins/builds/${new Date().format('yyyy/MM/dd')}/build-${BUILD_NUMBER}-${timestamp}.log"

            sh """
                # Upload build log to S3
                aws s3 cp ${logPath} s3://${s3Bucket}/${s3Key}

                # Also upload docker logs
                docker logs ai-devops-app > /tmp/docker-${BUILD_NUMBER}.log 2>&1
                aws s3 cp /tmp/docker-${BUILD_NUMBER}.log s3://${s3Bucket}/docker/ai-devops-app/${new Date().format('yyyy/MM/dd')}/app-${BUILD_NUMBER}-${timestamp}.log
                rm /tmp/docker-${BUILD_NUMBER}.log
            """

            echo "✓ Logs uploaded to S3: s3://${s3Bucket}/${s3Key}"
        }
    }
}
```

**Updated `post` section:**

```groovy
post {
    success {
        echo "✓ Pipeline completed successfully!"
    }
    failure {
        echo "✗ Pipeline failed!"
    }
    always {
        script {
            // Upload logs even if build fails
            def timestamp = new Date().format('yyyyMMdd-HHmmss')
            def s3Bucket = "your-company-logs"
            def buildStatus = currentBuild.result ?: 'SUCCESS'

            sh """
                # Upload Jenkins build log
                aws s3 cp /var/lib/jenkins/jobs/ai-devops-pipeline/builds/${BUILD_NUMBER}/log \
                    s3://${s3Bucket}/jenkins/builds/${new Date().format('yyyy/MM/dd')}/build-${BUILD_NUMBER}-${timestamp}-${buildStatus}.log || true

                # Upload Docker logs if container exists
                docker logs ai-devops-app > /tmp/docker-${BUILD_NUMBER}.log 2>&1 || true
                aws s3 cp /tmp/docker-${BUILD_NUMBER}.log \
                    s3://${s3Bucket}/docker/ai-devops-app/${new Date().format('yyyy/MM/dd')}/app-${BUILD_NUMBER}-${timestamp}.log || true
                rm -f /tmp/docker-${BUILD_NUMBER}.log
            """
        }

        // Cleanup
        sh 'docker image prune -f || true'
    }
}
```

---

### **Method 2: Separate Cron Job (Simpler, No Jenkinsfile Changes)**

Create a script on EC2 that runs daily:

**Script: `/usr/local/bin/upload-logs-to-s3.sh`**

```bash
#!/bin/bash
# Upload Jenkins and Docker logs to S3
# Run daily via cron: 0 3 * * * /usr/local/bin/upload-logs-to-s3.sh

S3_BUCKET="your-company-logs"  # Change this!
DATE=$(date +%Y/%m/%d)
TIMESTAMP=$(date +%Y%m%d-%H%M%S)

echo "Starting log upload to S3..."

# 1. Upload Jenkins build logs (last 7 days)
echo "Uploading Jenkins build logs..."
find /var/lib/jenkins/jobs/ai-devops-pipeline/builds/ -name "log" -mtime -7 | while read logfile; do
    BUILD_NUM=$(basename $(dirname $logfile))
    aws s3 cp "$logfile" "s3://$S3_BUCKET/jenkins/builds/$DATE/build-$BUILD_NUM-$TIMESTAMP.log"
done

# 2. Upload Jenkins system logs
echo "Uploading Jenkins system logs..."
aws s3 cp /var/log/jenkins/jenkins.log "s3://$S3_BUCKET/jenkins/system/$DATE/jenkins-system-$TIMESTAMP.log"

# 3. Upload Docker logs
echo "Uploading Docker container logs..."
docker logs ai-devops-app > /tmp/docker-app-$TIMESTAMP.log 2>&1
aws s3 cp /tmp/docker-app-$TIMESTAMP.log "s3://$S3_BUCKET/docker/ai-devops-app/$DATE/app-$TIMESTAMP.log"
rm /tmp/docker-app-$TIMESTAMP.log

# 4. Optional: Delete local logs older than 7 days
echo "Cleaning up old local logs..."
find /var/lib/jenkins/jobs/ai-devops-pipeline/builds/ -type d -mtime +7 -exec rm -rf {} \; 2>/dev/null || true

echo "✓ Log upload complete!"
echo "View logs at: https://s3.console.aws.amazon.com/s3/buckets/$S3_BUCKET"
```

**Make it executable:**
```bash
chmod +x /usr/local/bin/upload-logs-to-s3.sh
```

**Add to cron (runs daily at 3 AM):**
```bash
# Edit crontab
crontab -e

# Add this line:
0 3 * * * /usr/local/bin/upload-logs-to-s3.sh >> /var/log/s3-upload.log 2>&1
```

---

### **Method 3: Docker Log Driver (Real-time streaming)**

**Configure Docker to send logs directly to S3:**

This requires AWS CloudWatch Logs as intermediate (not direct to S3).

**Update docker run command in Jenkinsfile:**

```groovy
sh """
    docker run -d \
        --name ai-devops-app \
        --log-driver=awslogs \
        --log-opt awslogs-region=us-east-1 \
        --log-opt awslogs-group=/aws/docker/ai-devops-app \
        --log-opt awslogs-stream=build-${BUILD_NUMBER} \
        -p 5000:5000 \
        -p 8501:8501 \
        ${DOCKER_IMAGE}:${DOCKER_TAG}
"""
```

Then use **CloudWatch Logs to S3 export** (automated by AWS).

---

## 🔧 Setup: AWS S3 Bucket & Permissions

### **Step 1: Create S3 Bucket**

```bash
# Create S3 bucket
aws s3 mb s3://your-company-logs --region us-east-1

# Enable versioning (optional, for safety)
aws s3api put-bucket-versioning \
    --bucket your-company-logs \
    --versioning-configuration Status=Enabled

# Set lifecycle policy (auto-delete old logs after 90 days)
aws s3api put-bucket-lifecycle-configuration \
    --bucket your-company-logs \
    --lifecycle-configuration file://lifecycle.json
```

**lifecycle.json:**
```json
{
  "Rules": [
    {
      "Id": "DeleteOldLogs",
      "Status": "Enabled",
      "Filter": {},
      "Expiration": {
        "Days": 90
      },
      "Transitions": [
        {
          "Days": 30,
          "StorageClass": "STANDARD_IA"
        },
        {
          "Days": 60,
          "StorageClass": "GLACIER"
        }
      ]
    }
  ]
}
```

**What this does:**
- Day 0-30: Standard storage ($0.023/GB/month)
- Day 30-60: Infrequent Access ($0.0125/GB/month)
- Day 60-90: Glacier ($0.004/GB/month)
- Day 90+: Deleted automatically

---

### **Step 2: EC2 IAM Role (Grant S3 Access)**

**Option A: Attach IAM Role to EC2 (Recommended)**

1. **Create IAM Policy:**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:GetObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::your-company-logs/*",
        "arn:aws:s3:::your-company-logs"
      ]
    }
  ]
}
```

2. **Create IAM Role:**
```bash
aws iam create-role --role-name EC2-Jenkins-S3-Logs \
    --assume-role-policy-document file://trust-policy.json

aws iam put-role-policy --role-name EC2-Jenkins-S3-Logs \
    --policy-name S3LogsAccess \
    --policy-document file://s3-policy.json
```

3. **Attach to EC2:**
```bash
aws ec2 associate-iam-instance-profile \
    --instance-id i-YOUR-INSTANCE-ID \
    --iam-instance-profile Name=EC2-Jenkins-S3-Logs
```

**Option B: Use AWS CLI with Credentials (Less secure)**

```bash
# Configure AWS CLI on EC2
aws configure
# Enter: Access Key, Secret Key, Region
```

---

## 📊 Query Logs with AWS Athena

### **Setup Athena for Log Analysis:**

**Create Athena Table:**

```sql
CREATE EXTERNAL TABLE jenkins_logs (
    log_line STRING
)
PARTITIONED BY (
    year STRING,
    month STRING,
    day STRING
)
ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.lazy.LazySimpleSerDe'
LOCATION 's3://your-company-logs/jenkins/builds/';

-- Add partitions
MSCK REPAIR TABLE jenkins_logs;
```

**Query Examples:**

```sql
-- Find all failed builds
SELECT * FROM jenkins_logs
WHERE log_line LIKE '%FAILURE%'
AND year = '2026' AND month = '01' AND day = '17';

-- Count errors by date
SELECT year, month, day, COUNT(*) as error_count
FROM jenkins_logs
WHERE log_line LIKE '%ERROR%'
GROUP BY year, month, day
ORDER BY year DESC, month DESC, day DESC;

-- Find builds that took > 5 minutes
SELECT * FROM jenkins_logs
WHERE log_line LIKE '%Pipeline completed in%'
AND log_line LIKE '%[5-9] min%';

-- Search for specific error
SELECT * FROM jenkins_logs
WHERE log_line LIKE '%Docker build failed%';
```

**Cost:** ~$5 per TB scanned (very cheap for log searches!)

---

## 🔍 View & Download Logs

### **Via AWS CLI:**

```bash
# List all logs for a date
aws s3 ls s3://your-company-logs/jenkins/builds/2026/01/17/

# Download specific build log
aws s3 cp s3://your-company-logs/jenkins/builds/2026/01/17/build-4-20260117-120000.log ./

# Download all logs for a day
aws s3 sync s3://your-company-logs/jenkins/builds/2026/01/17/ ./logs/

# View log directly (without download)
aws s3 cp s3://your-company-logs/jenkins/builds/2026/01/17/build-4-20260117-120000.log - | less
```

### **Via AWS Console:**

```
1. Go to: https://s3.console.aws.amazon.com/s3/buckets/your-company-logs
2. Navigate: jenkins/builds/2026/01/17/
3. Click on log file
4. Click "Download" or "Open"
```

### **Via S3 Select (Query logs without download):**

```bash
# Search for errors in a log file
aws s3api select-object-content \
    --bucket your-company-logs \
    --key jenkins/builds/2026/01/17/build-4-20260117-120000.log \
    --expression "SELECT * FROM s3object s WHERE s._1 LIKE '%ERROR%'" \
    --expression-type SQL \
    --input-serialization '{"CSV": {}, "CompressionType": "NONE"}' \
    --output-serialization '{"CSV": {}}' \
    output.txt
```

---

## 📈 Monitoring & Alerts

### **Setup S3 Event Notifications:**

**Get notified when logs are uploaded:**

```bash
# Create SNS topic
aws sns create-topic --name log-uploads

# Subscribe your email
aws sns subscribe --topic-arn arn:aws:sns:us-east-1:123456789:log-uploads \
    --protocol email \
    --notification-endpoint your-email@company.com

# Configure S3 to send notification
aws s3api put-bucket-notification-configuration \
    --bucket your-company-logs \
    --notification-configuration file://notification.json
```

**notification.json:**
```json
{
  "TopicConfigurations": [
    {
      "TopicArn": "arn:aws:sns:us-east-1:123456789:log-uploads",
      "Events": ["s3:ObjectCreated:*"],
      "Filter": {
        "Key": {
          "FilterRules": [
            {
              "Name": "suffix",
              "Value": ".log"
            }
          ]
        }
      }
    }
  ]
}
```

---

## 💡 Complete Example: Updated Jenkinsfile

**Add S3 logging to your existing Jenkinsfile:**

```groovy
// Add environment variable
environment {
    DOCKER_IMAGE = 'ai-devops-app'
    DOCKER_TAG = "${BUILD_NUMBER}"
    S3_BUCKET = 'your-company-logs'  // Add this
}

// Add stage before "post" section
stage('Upload Logs to S3') {
    steps {
        script {
            def timestamp = new Date().format('yyyyMMdd-HHmmss')
            def dateFolder = new Date().format('yyyy/MM/dd')

            sh """
                # Upload Jenkins build log
                sudo aws s3 cp /var/lib/jenkins/jobs/ai-devops-pipeline/builds/${BUILD_NUMBER}/log \
                    s3://${S3_BUCKET}/jenkins/builds/${dateFolder}/build-${BUILD_NUMBER}-${timestamp}.log

                # Upload Docker logs
                docker logs ai-devops-app > /tmp/docker-${BUILD_NUMBER}.log 2>&1
                aws s3 cp /tmp/docker-${BUILD_NUMBER}.log \
                    s3://${S3_BUCKET}/docker/ai-devops-app/${dateFolder}/app-${BUILD_NUMBER}-${timestamp}.log
                rm /tmp/docker-${BUILD_NUMBER}.log

                echo "✓ Logs uploaded to s3://${S3_BUCKET}/"
            """
        }
    }
}
```

---

## 🎯 Quick Start: Minimal Setup

**1. Create S3 Bucket:**
```bash
aws s3 mb s3://my-jenkins-logs
```

**2. Create Upload Script on EC2:**
```bash
cat > /home/ubuntu/upload-logs.sh << 'EOF'
#!/bin/bash
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
aws s3 cp /var/log/jenkins/jenkins.log s3://my-jenkins-logs/jenkins-$TIMESTAMP.log
docker logs ai-devops-app > /tmp/docker-$TIMESTAMP.log 2>&1
aws s3 cp /tmp/docker-$TIMESTAMP.log s3://my-jenkins-logs/docker-$TIMESTAMP.log
rm /tmp/docker-$TIMESTAMP.log
EOF

chmod +x /home/ubuntu/upload-logs.sh
```

**3. Run Daily:**
```bash
crontab -e
# Add: 0 3 * * * /home/ubuntu/upload-logs.sh
```

**Done!** Logs now stored in S3 every day at 3 AM.

---

## ✅ Summary: S3 vs Splunk

| Feature | S3 + Athena | Splunk |
|---------|-------------|--------|
| **Cost (10GB/month)** | $0.23/month | $125-1667/month |
| **Cost (100GB/month)** | $2.30/month | $1,250-16,667/month |
| **Setup** | DIY (30 min) | Enterprise (days) |
| **Search** | Athena SQL | Advanced GUI |
| **Real-time** | No (batch) | Yes |
| **Retention** | Unlimited (cheap) | Expensive |
| **Best for** | Small-medium teams | Large enterprises |

**For your project: S3 is perfect! 💰**

---

## 📝 Next Steps

1. ✅ Create S3 bucket
2. ✅ Attach IAM role to EC2
3. ✅ Choose Method 1 (Jenkinsfile) or Method 2 (Cron)
4. ✅ Test log upload
5. ✅ Setup Athena for searching (optional)
6. ✅ Configure lifecycle policy (auto-delete old logs)

**Would you like me to create the updated Jenkinsfile with S3 logging?**
