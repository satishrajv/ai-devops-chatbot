#!/bin/bash
# Script to update AWS Security Group for AI DevOps Platform
# Adds rules for Flask (5000) and Streamlit (8501) if not already present

SECURITY_GROUP_ID="sg-0c56c1da72e818832"
AWS_REGION="us-east-1"

echo "🔒 Updating Security Group: $SECURITY_GROUP_ID"
echo "================================================"

# Function to check if a port rule exists
check_port() {
    local port=$1
    aws ec2 describe-security-groups \
        --group-ids $SECURITY_GROUP_ID \
        --region $AWS_REGION \
        --query "SecurityGroups[0].IpPermissions[?FromPort==\`$port\`]" \
        --output text 2>/dev/null
}

# Function to add inbound rule
add_port() {
    local port=$1
    local description=$2

    echo "Adding rule for port $port..."
    aws ec2 authorize-security-group-ingress \
        --group-id $SECURITY_GROUP_ID \
        --protocol tcp \
        --port $port \
        --cidr 0.0.0.0/0 \
        --region $AWS_REGION \
        --no-cli-pager 2>/dev/null

    if [ $? -eq 0 ]; then
        echo "✓ Port $port opened successfully ($description)"
    else
        echo "⚠ Port $port may already be open or failed to add"
    fi
}

# Check and add Flask port (5000)
echo ""
echo "Checking port 5000 (Flask App)..."
if [ -z "$(check_port 5000)" ]; then
    add_port 5000 "Flask Application"
else
    echo "✓ Port 5000 is already open"
fi

# Check and add Streamlit port (8501)
echo ""
echo "Checking port 8501 (Streamlit)..."
if [ -z "$(check_port 8501)" ]; then
    add_port 8501 "Streamlit Dashboard"
else
    echo "✓ Port 8501 is already open"
fi

echo ""
echo "================================================"
echo "✓ Security group update complete!"
echo ""
echo "Current security group rules:"
aws ec2 describe-security-groups \
    --group-ids $SECURITY_GROUP_ID \
    --region $AWS_REGION \
    --query 'SecurityGroups[0].IpPermissions[*].[FromPort,ToPort,IpProtocol,IpRanges[0].CidrIp]' \
    --output table

echo ""
echo "Your applications should now be accessible at:"
echo "  Jenkins:   http://35.174.138.165:8080"
echo "  Flask:     http://35.174.138.165:5000"
echo "  Streamlit: http://35.174.138.165:8501"
