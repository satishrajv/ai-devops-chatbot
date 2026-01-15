# AWS Quick Start - Deploy in 15 Minutes

Get your CI/CD pipeline running on AWS in 3 simple methods.

## Method 1: Automated with Terraform (Recommended)

**Time: 10 minutes**

### Prerequisites
- AWS CLI configured (`aws configure`)
- Terraform installed
- SSH key pair in AWS

### Steps

```bash
# 1. Navigate to terraform directory
cd terraform

# 2. Copy and edit variables
cp terraform.tfvars.example terraform.tfvars
nano terraform.tfvars
# Update: key_name and allowed_ssh_cidr

# 3. Initialize Terraform
terraform init

# 4. Review plan
terraform plan

# 5. Deploy
terraform apply -auto-approve

# 6. Get outputs
terraform output
```

**Done!** Terraform will output all URLs and SSH command.

### Connect and Start Services

```bash
# SSH to instance (use command from terraform output)
ssh -i your-key.pem ec2-user@<PUBLIC_IP>

# Navigate to project
cd AI-DevOps-chatbot

# Edit .env file
nano .env
# Add Jenkins credentials (will be generated after first start)

# Start services
docker-compose -f docker-compose.aws.yml up -d --build

# Get Jenkins password
docker exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword
```

## Method 2: Manual EC2 Setup

**Time: 15 minutes**

### Step 1: Launch EC2 Instance

**Using AWS Console:**
1. Go to EC2 Dashboard
2. Click "Launch Instance"
3. Choose:
   - Name: `ai-devops-platform`
   - AMI: Amazon Linux 2023
   - Instance type: t3.medium
   - Key pair: Select or create
   - Security group: Create with ports 22, 8080, 8501, 5000
   - Storage: 30GB gp3
4. Launch instance

**Using AWS CLI:**
```bash
# Create key pair (if needed)
aws ec2 create-key-pair \
  --key-name ai-devops-key \
  --query 'KeyMaterial' \
  --output text > ai-devops-key.pem
chmod 400 ai-devops-key.pem

# Create security group
aws ec2 create-security-group \
  --group-name ai-devops-sg \
  --description "AI DevOps Platform"

# Get security group ID
SG_ID=$(aws ec2 describe-security-groups \
  --group-names ai-devops-sg \
  --query 'SecurityGroups[0].GroupId' \
  --output text)

# Add rules
aws ec2 authorize-security-group-ingress --group-id $SG_ID --protocol tcp --port 22 --cidr 0.0.0.0/0
aws ec2 authorize-security-group-ingress --group-id $SG_ID --protocol tcp --port 8080 --cidr 0.0.0.0/0
aws ec2 authorize-security-group-ingress --group-id $SG_ID --protocol tcp --port 8501 --cidr 0.0.0.0/0
aws ec2 authorize-security-group-ingress --group-id $SG_ID --protocol tcp --port 5000 --cidr 0.0.0.0/0

# Launch instance
aws ec2 run-instances \
  --image-id $(aws ec2 describe-images --owners amazon \
    --filters "Name=name,Values=al2023-ami-*-x86_64" \
    --query 'Images | sort_by(@, &CreationDate) | [-1].ImageId' \
    --output text) \
  --instance-type t3.medium \
  --key-name ai-devops-key \
  --security-group-ids $SG_ID \
  --block-device-mappings DeviceName=/dev/xvda,Ebs={VolumeSize=30,VolumeType=gp3} \
  --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=ai-devops-platform}]'
```

### Step 2: Get Instance IP

```bash
# Get public IP
aws ec2 describe-instances \
  --filters "Name=tag:Name,Values=ai-devops-platform" "Name=instance-state-name,Values=running" \
  --query 'Reservations[0].Instances[0].PublicIpAddress' \
  --output text
```

### Step 3: Setup EC2

```bash
# Connect to EC2
ssh -i ai-devops-key.pem ec2-user@<PUBLIC_IP>

# Download and run setup script
curl -o setup-ec2.sh https://raw.githubusercontent.com/satishrajv/AI-DevOps-chatbot/main/setup-ec2.sh
chmod +x setup-ec2.sh
./setup-ec2.sh

# Start services
cd ~/AI-DevOps-chatbot
nano .env  # Edit configuration
docker-compose -f docker-compose.aws.yml up -d --build
```

## Method 3: Deploy from Local Machine

**Time: 5 minutes (if EC2 already exists)**

### Prerequisites
- EC2 instance running
- SSH key file
- AWS CLI configured (optional)

### Steps

```bash
# 1. Set environment variables
export EC2_IP=<your-ec2-public-ip>
export KEY_FILE=your-key.pem
export EC2_USER=ec2-user  # or ubuntu

# 2. Run deployment script
./deploy-to-aws.sh

# 3. Access services
# Jenkins:   http://<EC2_IP>:8080
# Streamlit: http://<EC2_IP>:8501
# Flask:     http://<EC2_IP>:5000
```

## Post-Deployment Configuration

### 1. Configure Jenkins

```bash
# Get initial password
ssh -i your-key.pem ec2-user@<EC2_IP> \
  'docker exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword'
```

Access Jenkins: `http://<EC2_IP>:8080`
- Paste password
- Install suggested plugins
- Create admin user
- Generate API token (User → Configure → API Token)

### 2. Update .env File

```bash
# SSH to EC2
ssh -i your-key.pem ec2-user@<EC2_IP>

# Edit .env
cd ~/AI-DevOps-chatbot
nano .env

# Add:
JENKINS_USER=admin
JENKINS_TOKEN=<your-token>

# Restart services
docker-compose -f docker-compose.aws.yml restart app
```

### 3. Create Jenkins Pipeline Job

1. Open Jenkins
2. New Item → `ai-devops-pipeline` → Pipeline
3. Pipeline from SCM:
   - SCM: Git
   - Repository: https://github.com/satishrajv/AI-DevOps-chatbot.git
   - Branch: main
   - Script Path: Jenkinsfile
4. Save

### 4. Configure GitHub Webhook

1. Go to GitHub repository settings
2. Webhooks → Add webhook
3. Payload URL: `http://<EC2_IP>:8080/github-webhook/`
4. Content type: application/json
5. Events: Push events
6. Add webhook

### 5. Test the Pipeline

**Via Streamlit:**
1. Open: `http://<EC2_IP>:8501`
2. Configure Jenkins credentials in sidebar
3. Trigger Jobs tab → Trigger Build
4. Build Logs tab → View logs

**Via GitHub:**
```bash
echo "# Test" >> README.md
git add README.md
git commit -m "Test AWS pipeline"
git push
```

Watch build start automatically in Jenkins!

## Accessing Services

| Service | URL | Purpose |
|---------|-----|---------|
| Jenkins | http://\<EC2_IP\>:8080 | CI/CD server |
| Streamlit | http://\<EC2_IP\>:8501 | Dashboard |
| Flask | http://\<EC2_IP\>:5000 | Application API |

## Common Commands

```bash
# SSH to EC2
ssh -i your-key.pem ec2-user@<EC2_IP>

# View logs
docker-compose -f docker-compose.aws.yml logs -f

# Restart services
docker-compose -f docker-compose.aws.yml restart

# Update application
cd ~/AI-DevOps-chatbot
git pull
docker-compose -f docker-compose.aws.yml up -d --build

# Stop services
docker-compose -f docker-compose.aws.yml down

# Check container status
docker ps
```

## Optional: Add Domain Name

### Using Route 53

```bash
# Create hosted zone
aws route53 create-hosted-zone --name yourdomain.com --caller-reference $(date +%s)

# Add A record
aws route53 change-resource-record-sets \
  --hosted-zone-id Z1234567890ABC \
  --change-batch '{
    "Changes": [{
      "Action": "CREATE",
      "ResourceRecordSet": {
        "Name": "jenkins.yourdomain.com",
        "Type": "A",
        "TTL": 300,
        "ResourceRecords": [{"Value": "<EC2_IP>"}]
      }
    }]
  }'
```

### Add SSL with Nginx

```bash
# On EC2 instance
sudo yum install nginx certbot python3-certbot-nginx -y
sudo systemctl start nginx
sudo certbot --nginx -d jenkins.yourdomain.com -d app.yourdomain.com
```

## Cost Breakdown

**Monthly AWS costs:**
- EC2 t3.medium: ~$30
- EBS 30GB gp3: ~$3
- Elastic IP: Free (when attached)
- Data transfer: ~$5
- **Total: ~$40/month**

**Savings tips:**
- Use t3a.medium (AMD): ~$25/month
- Stop instance when not in use
- Use Reserved Instance: ~$20/month (1-year commitment)

## Troubleshooting

### Can't connect to EC2
```bash
# Check instance is running
aws ec2 describe-instances --filters "Name=tag:Name,Values=ai-devops-platform"

# Check security group
aws ec2 describe-security-groups --group-names ai-devops-sg

# Verify key permissions
chmod 400 your-key.pem
```

### Services not accessible
```bash
# Check containers
docker ps

# Check logs
docker-compose -f docker-compose.aws.yml logs

# Restart
docker-compose -f docker-compose.aws.yml restart
```

### Out of memory
```bash
# Upgrade to t3.large
aws ec2 modify-instance-attribute \
  --instance-id i-XXXXXXXXX \
  --instance-type t3.large

# Or add swap
sudo dd if=/dev/zero of=/swapfile bs=1G count=4
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

## Cleanup

### Using Terraform
```bash
cd terraform
terraform destroy -auto-approve
```

### Manual Cleanup
```bash
# Terminate instance
aws ec2 terminate-instances --instance-ids i-XXXXXXXXX

# Delete security group
aws ec2 delete-security-group --group-name ai-devops-sg

# Release Elastic IP (if allocated)
aws ec2 release-address --allocation-id eipalloc-XXXXXXXXX
```

## Next Steps

1. ✅ Pipeline running on AWS
2. 🔄 Configure GitHub webhooks
3. 🔒 Restrict security groups to your IP
4. 🌐 Add domain name (optional)
5. 🔐 Add SSL certificate (optional)
6. 📊 Set up CloudWatch monitoring
7. 🚀 Plan migration to Kubernetes (Phase 2)

## Support

- Full Documentation: [AWS_DEPLOYMENT.md](AWS_DEPLOYMENT.md)
- Terraform Details: [terraform/README.md](terraform/README.md)
- Kubernetes (Phase 2): Coming soon

---

**You're now running the complete CI/CD pipeline on AWS!** 🎉
