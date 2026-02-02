#!/bin/bash
#
# Deployment Script for EC2
# Deploys KB Sync system to EC2 and sets up cron job
#

set -e  # Exit on error

echo "==========================================="
echo "  KB SYNC DEPLOYMENT TO EC2"
echo "==========================================="
echo ""

# Configuration
EC2_HOST="ubuntu@44.201.162.249"
PEM_FILE="C:/Users/Yashvi/myec2_jenkins.pem"
REMOTE_DIR="/home/ubuntu/kb-sync"
CRON_SCHEDULE="*/5 * * * *"  # Every 5 minutes

echo "[1/6] Checking PEM file..."
if [ ! -f "$PEM_FILE" ]; then
    echo "ERROR: PEM file not found at $PEM_FILE"
    exit 1
fi
echo "    Found: $PEM_FILE"

echo ""
echo "[2/6] Creating remote directory..."
ssh -i "$PEM_FILE" "$EC2_HOST" "mkdir -p $REMOTE_DIR"
echo "    Created: $REMOTE_DIR"

echo ""
echo "[3/6] Uploading files to EC2..."
scp -i "$PEM_FILE" -r \
    kb_sync_agent.py \
    agents/ \
    config/ \
    utils/ \
    requirements.txt \
    sync.sh \
    .env \
    "$EC2_HOST:$REMOTE_DIR/"
echo "    Files uploaded successfully"

echo ""
echo "[4/6] Setting up Python environment on EC2..."
ssh -i "$PEM_FILE" "$EC2_HOST" << 'ENDSSH'
cd /home/ubuntu/kb-sync

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "    Installing Python 3..."
    sudo apt-get update
    sudo apt-get install -y python3 python3-pip python3-venv
fi

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "    Creating virtual environment..."
    python3 -m venv venv
fi

# Activate and install dependencies
echo "    Installing dependencies..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
deactivate

# Make sync script executable
chmod +x sync.sh

echo "    Python environment ready"
ENDSSH

echo ""
echo "[5/6] Setting up cron job..."
ssh -i "$PEM_FILE" "$EC2_HOST" << ENDSSH
# Remove existing kb-sync cron jobs
crontab -l 2>/dev/null | grep -v 'kb-sync/sync.sh' | crontab -

# Add new cron job
(crontab -l 2>/dev/null; echo "$CRON_SCHEDULE cd $REMOTE_DIR && ./sync.sh") | crontab -

echo "    Cron job configured: $CRON_SCHEDULE"
crontab -l | grep kb-sync
ENDSSH

echo ""
echo "[6/6] Testing initial sync..."
ssh -i "$PEM_FILE" "$EC2_HOST" "cd $REMOTE_DIR && ./sync.sh"
echo "    Initial sync completed"

echo ""
echo "==========================================="
echo "  DEPLOYMENT SUCCESSFUL"
echo "==========================================="
echo ""
echo "System Details:"
echo "  - Remote Directory: $REMOTE_DIR"
echo "  - Cron Schedule: $CRON_SCHEDULE (every 5 minutes)"
echo "  - Log File: $REMOTE_DIR/cron.log"
echo "  - Sync Script: $REMOTE_DIR/sync.sh"
echo ""
echo "Useful Commands:"
echo "  - View logs: ssh -i \"$PEM_FILE\" $EC2_HOST 'tail -f $REMOTE_DIR/cron.log'"
echo "  - Manual sync: ssh -i \"$PEM_FILE\" $EC2_HOST 'cd $REMOTE_DIR && ./sync.sh'"
echo "  - Check cron: ssh -i \"$PEM_FILE\" $EC2_HOST 'crontab -l | grep kb-sync'"
echo ""
