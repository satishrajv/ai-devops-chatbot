#!/bin/bash

# AWS Deployment Script for AI DevOps Platform
# This script deploys the application to AWS EC2

set -e

# Configuration - UPDATE THESE VALUES
EC2_IP="${EC2_IP:-}"
KEY_FILE="${KEY_FILE:-your-key.pem}"
EC2_USER="${EC2_USER:-ec2-user}"  # or ubuntu for Ubuntu AMI

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Functions
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}→ $1${NC}"
}

check_prerequisites() {
    print_info "Checking prerequisites..."

    if [ -z "$EC2_IP" ]; then
        print_error "EC2_IP environment variable not set"
        echo "Usage: EC2_IP=your-ip KEY_FILE=your-key.pem ./deploy-to-aws.sh"
        exit 1
    fi

    if [ ! -f "$KEY_FILE" ]; then
        print_error "Key file not found: $KEY_FILE"
        exit 1
    fi

    if [ ! -f ".env" ]; then
        print_error ".env file not found. Copy from .env.example"
        exit 1
    fi

    print_success "Prerequisites check passed"
}

test_connection() {
    print_info "Testing SSH connection to $EC2_USER@$EC2_IP..."

    if ssh -i "$KEY_FILE" -o ConnectTimeout=10 -o StrictHostKeyChecking=no "$EC2_USER@$EC2_IP" "echo 'Connection successful'" > /dev/null 2>&1; then
        print_success "SSH connection successful"
    else
        print_error "Cannot connect to EC2 instance"
        exit 1
    fi
}

create_remote_directory() {
    print_info "Creating remote directory..."
    ssh -i "$KEY_FILE" "$EC2_USER@$EC2_IP" "mkdir -p ~/AI-DevOps-chatbot"
    print_success "Remote directory created"
}

copy_files() {
    print_info "Copying files to EC2..."

    # Create temporary directory for deployment
    TEMP_DIR=$(mktemp -d)

    # Copy necessary files
    cp docker-compose.aws.yml "$TEMP_DIR/"
    cp Dockerfile "$TEMP_DIR/"
    cp jenkins.Dockerfile "$TEMP_DIR/"
    cp Jenkinsfile "$TEMP_DIR/"
    cp requirements.txt "$TEMP_DIR/"
    cp start.sh "$TEMP_DIR/"
    cp .env "$TEMP_DIR/"
    cp -r flask_app "$TEMP_DIR/"
    cp -r streamlit_app "$TEMP_DIR/"

    # Copy to EC2
    scp -i "$KEY_FILE" -r "$TEMP_DIR"/* "$EC2_USER@$EC2_IP:~/AI-DevOps-chatbot/"

    # Cleanup
    rm -rf "$TEMP_DIR"

    print_success "Files copied to EC2"
}

deploy_application() {
    print_info "Deploying application on EC2..."

    ssh -i "$KEY_FILE" "$EC2_USER@$EC2_IP" << 'ENDSSH'
        cd ~/AI-DevOps-chatbot

        # Stop existing containers
        echo "Stopping existing containers..."
        docker-compose -f docker-compose.aws.yml down || true

        # Build and start new containers
        echo "Building and starting containers..."
        docker-compose -f docker-compose.aws.yml up -d --build

        # Wait for services to start
        echo "Waiting for services to start..."
        sleep 30

        # Check status
        echo "Container status:"
        docker-compose -f docker-compose.aws.yml ps
ENDSSH

    print_success "Application deployed"
}

verify_deployment() {
    print_info "Verifying deployment..."

    # Wait a bit more for services to be fully ready
    sleep 10

    # Test Flask
    if curl -s -f "http://$EC2_IP:5000/health" > /dev/null; then
        print_success "Flask app is running"
    else
        print_error "Flask app is not responding"
    fi

    # Test Streamlit
    if curl -s "http://$EC2_IP:8501" > /dev/null; then
        print_success "Streamlit dashboard is running"
    else
        print_error "Streamlit is not responding"
    fi

    # Test Jenkins
    if curl -s "http://$EC2_IP:8080" > /dev/null; then
        print_success "Jenkins is running"
    else
        print_error "Jenkins is not responding"
    fi
}

show_access_info() {
    echo ""
    echo "========================================="
    echo "  Deployment Complete!"
    echo "========================================="
    echo ""
    echo "Access your services at:"
    echo ""
    echo "  Jenkins:   http://$EC2_IP:8080"
    echo "  Streamlit: http://$EC2_IP:8501"
    echo "  Flask API: http://$EC2_IP:5000"
    echo ""
    echo "To get Jenkins initial password:"
    echo "  ssh -i $KEY_FILE $EC2_USER@$EC2_IP 'docker exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword'"
    echo ""
    echo "To view logs:"
    echo "  ssh -i $KEY_FILE $EC2_USER@$EC2_IP 'cd ~/AI-DevOps-chatbot && docker-compose -f docker-compose.aws.yml logs -f'"
    echo ""
    echo "========================================="
}

# Main execution
main() {
    echo "========================================="
    echo "  AWS Deployment - AI DevOps Platform"
    echo "========================================="
    echo ""

    check_prerequisites
    test_connection
    create_remote_directory
    copy_files
    deploy_application
    verify_deployment
    show_access_info
}

# Run main function
main
