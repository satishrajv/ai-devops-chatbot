#!/bin/bash
# Setup AWS Secrets Manager for AI DevOps Platform
# Run this script to create IAM role and attach to EC2

echo "=========================================="
echo "AWS Secrets Manager Setup"
echo "=========================================="

# Step 1: Create IAM policy for Secrets Manager access
echo "Step 1: Creating IAM policy..."

aws iam create-policy \
    --policy-name AiDevOpsPlatformSecretsPolicy \
    --policy-document '{
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
}'

# Step 2: Create IAM role for EC2
echo "Step 2: Creating IAM role..."

aws iam create-role \
    --role-name AiDevOpsPlatformRole \
    --assume-role-policy-document '{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "ec2.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}'

# Step 3: Attach policy to role
echo "Step 3: Attaching policy to role..."

# Get your AWS account ID
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

aws iam attach-role-policy \
    --role-name AiDevOpsPlatformRole \
    --policy-arn arn:aws:iam::${ACCOUNT_ID}:policy/AiDevOpsPlatformSecretsPolicy

# Step 4: Create instance profile
echo "Step 4: Creating instance profile..."

aws iam create-instance-profile \
    --instance-profile-name AiDevOpsPlatformInstanceProfile

# Step 5: Add role to instance profile
echo "Step 5: Adding role to instance profile..."

aws iam add-role-to-instance-profile \
    --instance-profile-name AiDevOpsPlatformInstanceProfile \
    --role-name AiDevOpsPlatformRole

# Wait a bit for IAM to propagate
echo "Waiting 10 seconds for IAM to propagate..."
sleep 10

# Step 6: Get EC2 instance ID
echo "Step 6: Finding EC2 instance..."

# Get instance ID by IP
INSTANCE_ID=$(aws ec2 describe-instances \
    --filters "Name=private-ip-address,Values=44.201.162.249" \
    --query 'Reservations[0].Instances[0].InstanceId' \
    --output text)

if [ "$INSTANCE_ID" = "None" ] || [ -z "$INSTANCE_ID" ]; then
    # Try public IP
    INSTANCE_ID=$(aws ec2 describe-instances \
        --filters "Name=ip-address,Values=44.201.162.249" \
        --query 'Reservations[0].Instances[0].InstanceId' \
        --output text)
fi

echo "Found instance: $INSTANCE_ID"

# Step 7: Attach instance profile to EC2
echo "Step 7: Attaching instance profile to EC2..."

aws ec2 associate-iam-instance-profile \
    --instance-id $INSTANCE_ID \
    --iam-instance-profile Name=AiDevOpsPlatformInstanceProfile

echo "=========================================="
echo "✓ Setup complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Create secret in AWS Secrets Manager (see instructions above)"
echo "2. SSH to EC2 and test: aws secretsmanager get-secret-value --secret-id ai-devops-platform/credentials"
echo "3. Update Jenkins to use Jenkinsfile.secrets-manager"
echo ""
