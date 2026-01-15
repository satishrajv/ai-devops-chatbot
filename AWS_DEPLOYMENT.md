# AWS Deployment Guide - Phase 1

Deploy the complete CI/CD pipeline to AWS EC2 with Jenkins and Streamlit.

## Architecture

```
GitHub Repository
    ↓ (webhook)
AWS EC2 Jenkins Server
    ↓ (build & deploy)
AWS EC2 Application Server
    ↓ (running)
Flask App + Streamlit Dashboard
```

## Prerequisites

1. AWS Account with appropriate permissions
2. AWS CLI installed and configured locally
3. SSH key pair for EC2 access
4. Domain name (optional, for production)

## Phase 1: Single EC2 Instance Setup

For initial deployment, we'll run everything on one EC2 instance.

### Step 1: Launch EC2 Instance

**Instance Specifications:**
- **AMI:** Amazon Linux 2023 or Ubuntu 22.04 LTS
- **Instance Type:** t3.medium (2 vCPU, 4GB RAM minimum)
- **Storage:** 30GB gp3
- **Security Group:** Configure inbound rules:
  - SSH (22) - Your IP only
  - HTTP (80) - 0.0.0.0/0
  - HTTPS (443) - 0.0.0.0/0
  - Jenkins (8080) - 0.0.0.0/0 (temporary, restrict later)
  - Streamlit (8501) - 0.0.0.0/0
  - Flask (5000) - 0.0.0.0/0

**Using AWS CLI:**
```bash
# Create security group
aws ec2 create-security-group \
  --group-name ai-devops-sg \
  --description "Security group for AI DevOps Platform"

# Add inbound rules
aws ec2 authorize-security-group-ingress \
  --group-name ai-devops-sg \
  --protocol tcp --port 22 --cidr YOUR_IP/32

aws ec2 authorize-security-group-ingress \
  --group-name ai-devops-sg \
  --protocol tcp --port 8080 --cidr 0.0.0.0/0

aws ec2 authorize-security-group-ingress \
  --group-name ai-devops-sg \
  --protocol tcp --port 8501 --cidr 0.0.0.0/0

aws ec2 authorize-security-group-ingress \
  --group-name ai-devops-sg \
  --protocol tcp --port 5000 --cidr 0.0.0.0/0

# Launch instance
aws ec2 run-instances \
  --image-id ami-XXXXXXXXX \
  --instance-type t3.medium \
  --key-name your-key-pair \
  --security-groups ai-devops-sg \
  --block-device-mappings DeviceName=/dev/xvda,Ebs={VolumeSize=30} \
  --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=ai-devops-server}]'
```

**Using AWS Console:**
1. Go to EC2 Dashboard
2. Click "Launch Instance"
3. Choose Amazon Linux 2023 or Ubuntu 22.04
4. Select t3.medium
5. Configure security group as above
6. Launch and download key pair

### Step 2: Connect to EC2 Instance

```bash
# Get public IP from AWS Console or CLI
export EC2_IP=<your-ec2-public-ip>

# Connect via SSH
ssh -i your-key.pem ec2-user@$EC2_IP
# or for Ubuntu
ssh -i your-key.pem ubuntu@$EC2_IP
```

### Step 3: Install Dependencies on EC2

```bash
# Update system
sudo yum update -y  # Amazon Linux
# or
sudo apt update && sudo apt upgrade -y  # Ubuntu

# Install Docker
sudo yum install docker -y  # Amazon Linux
# or
sudo apt install docker.io -y  # Ubuntu

# Start Docker
sudo systemctl start docker
sudo systemctl enable docker

# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Install Git
sudo yum install git -y  # Amazon Linux
# or
sudo apt install git -y  # Ubuntu

# Verify installations
docker --version
docker-compose --version
git --version
```

### Step 4: Clone Repository on EC2

```bash
# Clone the repository
git clone https://github.com/satishrajv/AI-DevOps-chatbot.git
cd AI-DevOps-chatbot

# Create .env file
cp .env.example .env

# Edit .env with your settings
nano .env
```

### Step 5: Update docker-compose for AWS

Create `docker-compose.aws.yml`:

```yaml
version: '3.8'

services:
  app:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: ai-devops-app
    restart: unless-stopped
    ports:
      - "5000:5000"
      - "8501:8501"
    environment:
      - ENVIRONMENT=production
      - JENKINS_URL=http://jenkins:8080
      - JENKINS_USER=${JENKINS_USER:-admin}
      - JENKINS_TOKEN=${JENKINS_TOKEN:-}
    networks:
      - devops-network
    depends_on:
      - jenkins

  jenkins:
    build:
      context: .
      dockerfile: jenkins.Dockerfile
    container_name: jenkins
    restart: unless-stopped
    privileged: true
    user: root
    ports:
      - "8080:8080"
      - "50000:50000"
    volumes:
      - jenkins_home:/var/jenkins_home
      - /var/run/docker.sock:/var/run/docker.sock
    environment:
      - JAVA_OPTS=-Dhudson.security.csrf.GlobalCrumbIssuerConfiguration.DISABLE_CSRF_PROTECTION=true
    networks:
      - devops-network

volumes:
  jenkins_home:

networks:
  devops-network:
    driver: bridge
```

### Step 6: Start Services on AWS

```bash
# Build and start services
docker-compose -f docker-compose.aws.yml up -d --build

# Monitor logs
docker-compose -f docker-compose.aws.yml logs -f

# Check status
docker-compose -f docker-compose.aws.yml ps
```

### Step 7: Configure Jenkins on AWS

```bash
# Get Jenkins initial password
docker exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword
```

Access Jenkins:
- URL: `http://<your-ec2-public-ip>:8080`
- Follow setup wizard
- Install suggested plugins
- Create admin user
- Generate API token

### Step 8: Configure GitHub Webhook for AWS

1. Go to GitHub repository settings
2. Navigate to Webhooks → Add webhook
3. Configure:
   - **Payload URL:** `http://<your-ec2-public-ip>:8080/github-webhook/`
   - **Content type:** `application/json`
   - **Events:** Push events
4. Save webhook

### Step 9: Access Streamlit Dashboard

- URL: `http://<your-ec2-public-ip>:8501`
- Configure Jenkins credentials in sidebar
- Test triggering builds

## Optional: Use Elastic IP

To avoid IP changes on instance restart:

```bash
# Allocate Elastic IP
aws ec2 allocate-address --domain vpc

# Associate with instance
aws ec2 associate-address \
  --instance-id i-XXXXXXXXX \
  --allocation-id eipalloc-XXXXXXXXX
```

## Optional: Setup Domain with Route 53

```bash
# Create hosted zone
aws route53 create-hosted-zone --name yourdomain.com

# Add A records pointing to your EC2 IP
# jenkins.yourdomain.com → EC2_IP:8080
# app.yourdomain.com → EC2_IP:8501
```

## Optional: Add SSL/TLS with Nginx

Install Nginx as reverse proxy:

```bash
sudo yum install nginx -y  # Amazon Linux
sudo systemctl start nginx
sudo systemctl enable nginx

# Install certbot for Let's Encrypt
sudo yum install certbot python3-certbot-nginx -y

# Get SSL certificate
sudo certbot --nginx -d jenkins.yourdomain.com -d app.yourdomain.com
```

## Automated Deployment Script

Create `deploy-to-aws.sh`:

```bash
#!/bin/bash

EC2_IP="<your-ec2-ip>"
KEY_FILE="your-key.pem"
EC2_USER="ec2-user"  # or ubuntu

echo "Deploying to AWS EC2: $EC2_IP"

# Copy files to EC2
scp -i $KEY_FILE -r \
  docker-compose.aws.yml \
  Dockerfile \
  jenkins.Dockerfile \
  flask_app \
  streamlit_app \
  Jenkinsfile \
  requirements.txt \
  start.sh \
  .env \
  $EC2_USER@$EC2_IP:~/AI-DevOps-chatbot/

# Deploy on EC2
ssh -i $KEY_FILE $EC2_USER@$EC2_IP << 'EOF'
  cd ~/AI-DevOps-chatbot
  docker-compose -f docker-compose.aws.yml down
  docker-compose -f docker-compose.aws.yml up -d --build
  docker-compose -f docker-compose.aws.yml ps
EOF

echo "Deployment complete!"
echo "Jenkins: http://$EC2_IP:8080"
echo "Streamlit: http://$EC2_IP:8501"
echo "Flask: http://$EC2_IP:5000"
```

## Monitoring and Maintenance

### View Logs
```bash
# All services
docker-compose -f docker-compose.aws.yml logs -f

# Specific service
docker logs jenkins -f
docker logs ai-devops-app -f
```

### Restart Services
```bash
docker-compose -f docker-compose.aws.yml restart
```

### Update Application
```bash
cd ~/AI-DevOps-chatbot
git pull origin main
docker-compose -f docker-compose.aws.yml up -d --build
```

### Backup Jenkins Data
```bash
# Backup Jenkins volume
docker run --rm \
  -v ai-devops-chatbot_jenkins_home:/data \
  -v $(pwd):/backup \
  alpine tar czf /backup/jenkins-backup-$(date +%Y%m%d).tar.gz /data

# Upload to S3
aws s3 cp jenkins-backup-*.tar.gz s3://your-backup-bucket/
```

## Cost Estimation (AWS)

**Monthly costs (approximate):**
- EC2 t3.medium: ~$30/month
- EBS 30GB: ~$3/month
- Elastic IP: Free (if attached)
- Data transfer: ~$5-10/month
- **Total: ~$40-45/month**

## Testing the AWS Deployment

```bash
# Test Jenkins
curl http://<ec2-ip>:8080

# Test Streamlit
curl http://<ec2-ip>:8501

# Test Flask
curl http://<ec2-ip>:5000/health

# Trigger build via Streamlit dashboard
# Push code to GitHub and verify webhook triggers build
```

## Security Best Practices

1. **Restrict Jenkins Access:**
   ```bash
   # Only allow access from your IP
   aws ec2 authorize-security-group-ingress \
     --group-name ai-devops-sg \
     --protocol tcp --port 8080 --cidr YOUR_IP/32
   ```

2. **Use IAM Roles:** Attach IAM role to EC2 for AWS API access

3. **Enable CloudWatch:** Monitor logs and metrics

4. **Automated Backups:** Schedule Jenkins data backups to S3

5. **Update Security Groups:** Remove 0.0.0.0/0 access after testing

## Troubleshooting

### Can't connect to EC2
- Verify security group allows SSH from your IP
- Check instance is running
- Verify key file permissions: `chmod 400 your-key.pem`

### Docker permission denied
```bash
sudo usermod -aG docker $USER
newgrp docker
```

### Services won't start
```bash
# Check Docker
sudo systemctl status docker

# Check logs
docker-compose -f docker-compose.aws.yml logs
```

### Out of disk space
```bash
# Clean up Docker
docker system prune -a -f
```

## Phase 2 Preview: Kubernetes on AWS EKS

Coming next:
- Migrate to Amazon EKS
- Kubernetes manifests
- Helm charts
- Auto-scaling
- LoadBalancer with ALB
- Persistent volumes with EBS

See `KUBERNETES_DEPLOYMENT.md` (to be created in Phase 2)

## Summary

You now have:
- ✅ Jenkins running on AWS EC2
- ✅ Streamlit dashboard on AWS
- ✅ Flask app deployed on AWS
- ✅ GitHub webhooks triggering AWS builds
- ✅ Complete CI/CD pipeline in AWS cloud

All your code is deployed to AWS Linux and accessible via public IP addresses.
