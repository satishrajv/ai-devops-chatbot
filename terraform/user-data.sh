#!/bin/bash

# User data script for EC2 instance initialization

# Update system
yum update -y

# Install Docker
yum install docker -y
systemctl start docker
systemctl enable docker
usermod -aG docker ec2-user

# Install Docker Compose
DOCKER_COMPOSE_VERSION=$(curl -s https://api.github.com/repos/docker/compose/releases/latest | grep 'tag_name' | cut -d\" -f4)
curl -L "https://github.com/docker/compose/releases/download/${DOCKER_COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Install Git and utilities
yum install git htop vim curl wget -y

# Clone repository
cd /home/ec2-user
git clone https://github.com/satishrajv/AI-DevOps-chatbot.git
chown -R ec2-user:ec2-user /home/ec2-user/AI-DevOps-chatbot

# Create .env file
cd /home/ec2-user/AI-DevOps-chatbot
cp .env.example .env
chown ec2-user:ec2-user .env

# Note: Services are not automatically started
# User needs to configure .env and start manually
echo "Setup complete. Services can be started with: docker-compose -f docker-compose.aws.yml up -d" > /home/ec2-user/SETUP_COMPLETE.txt
