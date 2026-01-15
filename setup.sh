#!/bin/bash

echo "======================================"
echo "AI DevOps Platform - Setup Script"
echo "======================================"
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "Error: Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if docker-compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "Error: docker-compose is not installed. Please install docker-compose first."
    exit 1
fi

echo "Step 1: Creating .env file..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "Created .env file. Please edit it with your Jenkins credentials."
else
    echo ".env file already exists."
fi

echo ""
echo "Step 2: Building and starting Docker containers..."
docker-compose up -d --build

echo ""
echo "Step 3: Waiting for Jenkins to start (this may take 2-3 minutes)..."
sleep 30

# Wait for Jenkins to be ready
echo "Checking Jenkins status..."
until curl -s http://localhost:8080 > /dev/null; do
    echo "Waiting for Jenkins..."
    sleep 5
done

echo ""
echo "======================================"
echo "Setup Complete!"
echo "======================================"
echo ""
echo "Services are running at:"
echo "  - Jenkins:   http://localhost:8080"
echo "  - Streamlit: http://localhost:8501"
echo "  - Flask:     http://localhost:5000"
echo ""
echo "Next Steps:"
echo "1. Get Jenkins initial admin password:"
echo "   docker exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword"
echo ""
echo "2. Open Jenkins at http://localhost:8080 and complete setup"
echo ""
echo "3. Create Jenkins API token:"
echo "   - Go to User Menu → Configure → API Token"
echo "   - Generate a new token and add it to .env file"
echo ""
echo "4. Create Jenkins pipeline job:"
echo "   - Name: ai-devops-pipeline"
echo "   - Type: Pipeline"
echo "   - Pipeline from SCM: Git"
echo "   - Repository: https://github.com/satishrajv/AI-DevOps-chatbot.git"
echo "   - Script Path: Jenkinsfile"
echo ""
echo "5. Open Streamlit dashboard at http://localhost:8501"
echo ""
echo "======================================"
