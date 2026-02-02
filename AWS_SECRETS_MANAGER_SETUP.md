# AWS Secrets Manager Setup Guide

This guide shows how to use AWS Secrets Manager to manage all credentials instead of Jenkins Credentials.

## Benefits

✅ **Centralized**: All credentials in one place
✅ **Secure**: Encrypted at rest, IAM-controlled access
✅ **Auditable**: CloudTrail logs who accessed what
✅ **Rotatable**: Automatic credential rotation support
✅ **Cost-effective**: ~$0.40/month per secret

---

## Step 1: Create Secret in AWS Secrets Manager

### Via AWS Console:

1. Go to: https://console.aws.amazon.com/secretsmanager/
2. Click **"Store a new secret"**
3. Select **"Other type of secret"**
4. Click **"Plaintext"** tab
5. Paste this JSON (replace with your actual values):

```json
{
  "OPENAI_API_KEY": "sk-proj-your-openai-key-here",
  "WEAVIATE_URL": "https://your-cluster.weaviate.cloud",
  "WEAVIATE_API_KEY": "your-weaviate-api-key",
  "AWS_ACCESS_KEY_ID": "your-aws-access-key-for-s3",
  "AWS_SECRET_ACCESS_KEY": "your-aws-secret-key-for-s3",
  "JENKINS_USER": "admin",
  "JENKINS_TOKEN": "your-jenkins-api-token"
}
```

6. Click **Next**
7. Secret name: `ai-devops-platform/credentials`
8. Description: `Credentials for AI DevOps Platform`
9. Click **Next** → **Next** → **Store**

### Via AWS CLI:

```bash
aws secretsmanager create-secret \
    --name ai-devops-platform/credentials \
    --description "Credentials for AI DevOps Platform" \
    --secret-string '{
  "OPENAI_API_KEY": "sk-proj-your-key",
  "WEAVIATE_URL": "https://your-cluster.weaviate.cloud",
  "WEAVIATE_API_KEY": "your-weaviate-key",
  "AWS_ACCESS_KEY_ID": "your-aws-key",
  "AWS_SECRET_ACCESS_KEY": "your-aws-secret",
  "JENKINS_USER": "admin",
  "JENKINS_TOKEN": "your-jenkins-token"
}' \
    --region us-east-1
```

---

## Step 2: Grant EC2 Instance Access to Secrets Manager

Your EC2 instance needs permission to read the secret.

### Option A: Create IAM Role (Recommended)

1. Go to: https://console.aws.amazon.com/iam/
2. Click **Roles** → **Create role**
3. Select **AWS service** → **EC2** → **Next**
4. Click **Create policy** (opens new tab)
5. Click **JSON** tab and paste:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "secretsmanager:GetSecretValue",
        "secretsmanager:DescribeSecret"
      ],
      "Resource": "arn:aws:secretsmanager:us-east-1:*:secret:ai-devops-platform/credentials-*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:GetObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::jenkins-logs-aidevops-2026/*",
        "arn:aws:s3:::jenkins-kb/*"
      ]
    }
  ]
}
```

6. Click **Next** → Name: `AiDevOpsPlatformPolicy` → **Create policy**
7. Go back to the role creation tab, click refresh, search for `AiDevOpsPlatformPolicy`
8. Select it → **Next**
9. Role name: `AiDevOpsPlatformRole` → **Create role**

### Attach Role to EC2 Instance:

1. Go to: https://console.aws.amazon.com/ec2/
2. Select your EC2 instance (44.201.162.249)
3. Click **Actions** → **Security** → **Modify IAM role**
4. Select `AiDevOpsPlatformRole`
5. Click **Update IAM role**

---

## Step 3: Update Jenkins Pipeline

Replace your current `Jenkinsfile.ec2-simple` with the new `Jenkinsfile.secrets-manager`:

```bash
# On your EC2 instance or locally
cd /path/to/AI-DevOps-chatbot
cp Jenkinsfile.secrets-manager Jenkinsfile.ec2-simple
git add Jenkinsfile.ec2-simple
git commit -m "Switch to AWS Secrets Manager"
git push origin main
```

Or simply rename in Jenkins:
1. In Jenkins, go to your job configuration
2. Change **Script Path** from `Jenkinsfile.ec2-simple` to `Jenkinsfile.secrets-manager`
3. Save

---

## Step 4: Update Dockerfile

The Dockerfile needs to include the secrets fetching script. Add this line:

```dockerfile
# Copy scripts
COPY scripts/ ./scripts/
```

Make sure `scripts/fetch_secrets.py` exists in your repo.

---

## Step 5: Test the Setup

### Test 1: Verify EC2 Can Access Secret

SSH into your EC2 instance and run:

```bash
aws secretsmanager get-secret-value \
    --secret-id ai-devops-platform/credentials \
    --region us-east-1
```

**Expected output**: JSON with your credentials (proves IAM role works)

### Test 2: Test Secret Fetching Script

```bash
cd /path/to/AI-DevOps-chatbot
python3 scripts/fetch_secrets.py
```

**Expected output**: Export statements like:
```bash
export OPENAI_API_KEY="sk-proj-..."
export WEAVIATE_URL="https://..."
...
```

### Test 3: Deploy via Jenkins

1. Go to: http://44.201.162.249:8080
2. Click **Build Now**
3. Watch **Console Output**
4. Look for: `✓ Credentials loaded successfully`

---

## Comparison: Jenkins Credentials vs AWS Secrets Manager

| Feature | Jenkins Credentials | AWS Secrets Manager |
|---------|-------------------|-------------------|
| **Storage** | Jenkins server only | AWS-wide (any service can access) |
| **Encryption** | Jenkins master key | AWS KMS |
| **Audit Logs** | Limited | Full CloudTrail logging |
| **Rotation** | Manual | Automatic (supports Lambda rotation) |
| **Access Control** | Jenkins users | IAM policies (fine-grained) |
| **Cost** | Free (included) | ~$0.40/month per secret |
| **Backup** | Jenkins backup | AWS-managed redundancy |
| **Multi-region** | No | Yes |

---

## Other Credential Management Options

### Option 2: HashiCorp Vault

**Best for**: Large enterprises, multi-cloud environments

**Pros**:
- Platform-agnostic (works with any cloud)
- Dynamic secrets (generates credentials on-demand)
- Advanced features (secret versioning, leasing, renewal)

**Cons**:
- Requires separate Vault server setup
- More complex configuration
- Additional maintenance overhead

**Setup**:
```bash
# Install Vault
curl -fsSL https://apt.releases.hashicorp.com/gpg | sudo apt-key add -
sudo apt-add-repository "deb [arch=amd64] https://apt.releases.hashicorp.com $(lsb_release -cs) main"
sudo apt-get update && sudo apt-get install vault

# Start Vault server
vault server -dev

# Store secret
vault kv put secret/ai-devops-platform \
    openai_api_key="sk-proj-..." \
    weaviate_url="https://..." \
    weaviate_api_key="..."

# Fetch in your app
vault kv get -format=json secret/ai-devops-platform
```

---

### Option 3: AWS Parameter Store (SSM)

**Best for**: Simple use cases, cost-conscious projects

**Pros**:
- **FREE** for standard parameters (up to 10,000)
- Integrated with AWS Systems Manager
- Good for non-sensitive config + secrets

**Cons**:
- No automatic rotation
- 4KB size limit per parameter
- Less features than Secrets Manager

**Setup**:
```bash
# Store secrets (one per parameter)
aws ssm put-parameter \
    --name /ai-devops-platform/openai-api-key \
    --value "sk-proj-your-key" \
    --type SecureString

aws ssm put-parameter \
    --name /ai-devops-platform/weaviate-url \
    --value "https://your-cluster.weaviate.cloud" \
    --type String

# Fetch in your app
aws ssm get-parameter \
    --name /ai-devops-platform/openai-api-key \
    --with-decryption \
    --query 'Parameter.Value' \
    --output text
```

**Python Example**:
```python
import boto3

ssm = boto3.client('ssm', region_name='us-east-1')

def get_parameter(name: str) -> str:
    response = ssm.get_parameter(Name=name, WithDecryption=True)
    return response['Parameter']['Value']

openai_key = get_parameter('/ai-devops-platform/openai-api-key')
```

---

### Option 4: Environment Variables (.env file)

**Best for**: Local development only

**Pros**:
- Simple and fast for testing
- No external dependencies

**Cons**:
- ❌ Not secure for production
- ❌ Easy to accidentally commit to Git
- ❌ No audit trail
- ❌ Hard to rotate

**Setup**:
```bash
# .env file
OPENAI_API_KEY=sk-proj-your-key
WEAVIATE_URL=https://your-cluster.weaviate.cloud
WEAVIATE_API_KEY=your-key

# Load in app (Python)
from dotenv import load_dotenv
load_dotenv()
```

---

## Recommendation

**For your setup (EC2 + Jenkins + AWS):**

1. **Production**: Use **AWS Secrets Manager** ✅
   - You're already on AWS
   - Simple integration with EC2 IAM roles
   - Built-in encryption and audit logging
   - Worth the $0.40/month for security

2. **Development/Testing**: Use **AWS Parameter Store** (free tier)
   - Free for standard parameters
   - Good enough for dev/staging environments

3. **Avoid**:
   - ❌ Jenkins Credentials (limited to Jenkins only)
   - ❌ .env files in production (security risk)

---

## Migration Checklist

- [ ] Create secret in AWS Secrets Manager
- [ ] Create IAM role with SecretsManager permissions
- [ ] Attach IAM role to EC2 instance
- [ ] Test secret access from EC2
- [ ] Copy `Jenkinsfile.secrets-manager` to `Jenkinsfile.ec2-simple`
- [ ] Update Dockerfile to include `scripts/` directory
- [ ] Push changes to GitHub
- [ ] Trigger Jenkins build
- [ ] Verify deployment succeeds
- [ ] Test Flask API and Streamlit UI
- [ ] Remove old Jenkins credentials (optional cleanup)

---

## Troubleshooting

### Error: "Access Denied" when fetching secret

**Cause**: EC2 instance doesn't have IAM role or role lacks permissions

**Fix**:
1. Verify IAM role is attached to EC2:
   ```bash
   aws sts get-caller-identity
   ```
2. Check role has `secretsmanager:GetSecretValue` permission
3. Verify secret ARN matches in policy

### Error: "Secret not found"

**Cause**: Secret name mismatch

**Fix**:
1. List all secrets:
   ```bash
   aws secretsmanager list-secrets --region us-east-1
   ```
2. Verify secret name is exactly: `ai-devops-platform/credentials`

### Error: "Invalid JSON in secret"

**Cause**: Malformed JSON in secret value

**Fix**:
1. Validate JSON at https://jsonlint.com/
2. Update secret:
   ```bash
   aws secretsmanager update-secret \
       --secret-id ai-devops-platform/credentials \
       --secret-string '{"OPENAI_API_KEY":"sk-..."}'
   ```

---

## Cost Estimate

| Service | Usage | Monthly Cost |
|---------|-------|-------------|
| AWS Secrets Manager | 1 secret | $0.40 |
| API Calls | ~1,000/month | $0.05 |
| **Total** | | **~$0.45/month** |

**Note**: Parameter Store would be **FREE** for the same workload.

---

## Next Steps

1. Choose your preferred option (Secrets Manager recommended)
2. Follow the setup steps above
3. Test locally first
4. Deploy to production
5. Remove old Jenkins credentials for cleanup

Need help? Check the troubleshooting section or ask!
