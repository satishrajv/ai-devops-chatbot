#!/bin/bash
#
# Local Testing Script (Windows Git Bash Compatible)
# Tests KB sync system on local machine before EC2 deployment
#

echo "==========================================="
echo "  KB SYNC LOCAL TEST"
echo "==========================================="
echo ""

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "[1/4] Checking Python installation..."
if ! command -v python &> /dev/null && ! command -v python3 &> /dev/null; then
    echo "ERROR: Python not found. Please install Python 3.8 or higher"
    exit 1
fi

# Use python3 if available, otherwise python
PYTHON_CMD="python3"
if ! command -v python3 &> /dev/null; then
    PYTHON_CMD="python"
fi

echo "    Found: $($PYTHON_CMD --version)"

echo ""
echo "[2/4] Checking .env file..."
if [ ! -f ".env" ]; then
    echo "ERROR: .env file not found"
    echo "Please copy .env.template to .env and fill in your credentials"
    exit 1
fi
echo "    Found: .env"

echo ""
echo "[3/4] Installing dependencies..."
if [ ! -d "venv" ]; then
    echo "    Creating virtual environment..."
    $PYTHON_CMD -m venv venv
fi

# Activate virtual environment (Windows Git Bash)
if [ -f "venv/Scripts/activate" ]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi

echo "    Installing requirements..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

echo ""
echo "[4/4] Running KB sync..."
echo ""
$PYTHON_CMD kb_sync_agent.py

# Capture exit code
EXIT_CODE=$?

# Deactivate
deactivate

echo ""
echo "==========================================="
if [ $EXIT_CODE -eq 0 ]; then
    echo "  TEST SUCCESSFUL"
else
    echo "  TEST FAILED (Exit Code: $EXIT_CODE)"
fi
echo "==========================================="
echo ""
echo "Check kb_sync.log for detailed logs"
echo ""

exit $EXIT_CODE
