#!/bin/bash

# EC2 Instance Setup Script
# Run this script ON the EC2 instance after SSH connection

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "========================================="
echo "  Setting up AI DevOps Platform on EC2"
echo "========================================="
echo ""

# Detect OS
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$ID
else
    echo "Cannot detect OS"
    exit 1
fi

echo -e "${YELLOW}→ Detected OS: $OS${NC}"

# Update system
echo -e "${YELLOW}→ Updating system...${NC}"
if [ "$OS" = "amzn" ] || [ "$OS" = "rhel" ]; then
    sudo yum update -y
elif [ "$OS" = "ubuntu" ]; then
    sudo apt update && sudo apt upgrade -y
fi
echo -e "${GREEN}✓ System updated${NC}"

# Install Docker
echo -e "${YELLOW}→ Installing Docker...${NC}"
if [ "$OS" = "amzn" ] || [ "$OS" = "rhel" ]; then
    sudo yum install docker -y
elif [ "$OS" = "ubuntu" ]; then
    sudo apt install docker.io -y
fi

sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker $USER
echo -e "${GREEN}✓ Docker installed${NC}"

# Install Docker Compose
echo -e "${YELLOW}→ Installing Docker Compose...${NC}"
DOCKER_COMPOSE_VERSION=$(curl -s https://api.github.com/repos/docker/compose/releases/latest | grep 'tag_name' | cut -d\" -f4)
sudo curl -L "https://github.com/docker/compose/releases/download/${DOCKER_COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
echo -e "${GREEN}✓ Docker Compose installed${NC}"

# Install Git
echo -e "${YELLOW}→ Installing Git...${NC}"
if [ "$OS" = "amzn" ] || [ "$OS" = "rhel" ]; then
    sudo yum install git -y
elif [ "$OS" = "ubuntu" ]; then
    sudo apt install git -y
fi
echo -e "${GREEN}✓ Git installed${NC}"

# Install useful utilities
echo -e "${YELLOW}→ Installing utilities...${NC}"
if [ "$OS" = "amzn" ] || [ "$OS" = "rhel" ]; then
    sudo yum install htop vim curl wget -y
elif [ "$OS" = "ubuntu" ]; then
    sudo apt install htop vim curl wget -y
fi
echo -e "${GREEN}✓ Utilities installed${NC}"

# Configure firewall (if applicable)
echo -e "${YELLOW}→ Configuring firewall...${NC}"
if command -v firewall-cmd &> /dev/null; then
    sudo firewall-cmd --permanent --add-port=8080/tcp
    sudo firewall-cmd --permanent --add-port=8501/tcp
    sudo firewall-cmd --permanent --add-port=5000/tcp
    sudo firewall-cmd --reload
    echo -e "${GREEN}✓ Firewall configured${NC}"
elif command -v ufw &> /dev/null; then
    sudo ufw allow 8080/tcp
    sudo ufw allow 8501/tcp
    sudo ufw allow 5000/tcp
    sudo ufw --force enable
    echo -e "${GREEN}✓ Firewall configured${NC}"
else
    echo -e "${YELLOW}! No firewall detected, using AWS Security Groups${NC}"
fi

# Clone repository
echo -e "${YELLOW}→ Cloning repository...${NC}"
if [ ! -d "AI-DevOps-chatbot" ]; then
    git clone https://github.com/satishrajv/AI-DevOps-chatbot.git
    cd AI-DevOps-chatbot
    cp .env.example .env
    echo -e "${GREEN}✓ Repository cloned${NC}"
else
    echo -e "${YELLOW}! Repository already exists${NC}"
    cd AI-DevOps-chatbot
    git pull origin main
fi

# Display versions
echo ""
echo "========================================="
echo "  Installation Complete!"
echo "========================================="
echo ""
echo "Installed versions:"
docker --version
docker-compose --version
git --version
echo ""
echo "Next steps:"
echo "1. Edit .env file with your configuration:"
echo "   nano ~/AI-DevOps-chatbot/.env"
echo ""
echo "2. Start the services:"
echo "   cd ~/AI-DevOps-chatbot"
echo "   docker-compose -f docker-compose.aws.yml up -d --build"
echo ""
echo "3. Get Jenkins password:"
echo "   docker exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword"
echo ""
echo "4. Access services:"
echo "   Jenkins:   http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4):8080"
echo "   Streamlit: http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4):8501"
echo "   Flask:     http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4):5000"
echo ""
echo "========================================="
