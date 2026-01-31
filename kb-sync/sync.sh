#!/bin/bash
#
# KB Sync Wrapper Script for Cron
# Activates virtual environment and runs the sync
#

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Configuration
LOG_FILE="$SCRIPT_DIR/cron.log"
VENV_PATH="$SCRIPT_DIR/venv"
PYTHON_SCRIPT="$SCRIPT_DIR/kb_sync_agent.py"

# Timestamp function
timestamp() {
    date "+%Y-%m-%d %H:%M:%S"
}

# Start logging
echo "========================================" >> "$LOG_FILE"
echo "[$(timestamp)] KB Sync Started" >> "$LOG_FILE"
echo "========================================" >> "$LOG_FILE"

# Check if virtual environment exists
if [ ! -d "$VENV_PATH" ]; then
    echo "[$(timestamp)] ERROR: Virtual environment not found at $VENV_PATH" >> "$LOG_FILE"
    echo "[$(timestamp)] Please run: python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt" >> "$LOG_FILE"
    exit 1
fi

# Activate virtual environment
source "$VENV_PATH/bin/activate"

# Check if activation worked
if [ $? -ne 0 ]; then
    echo "[$(timestamp)] ERROR: Failed to activate virtual environment" >> "$LOG_FILE"
    exit 1
fi

echo "[$(timestamp)] Virtual environment activated" >> "$LOG_FILE"

# Run the sync
python3 "$PYTHON_SCRIPT" >> "$LOG_FILE" 2>&1

# Capture exit code
EXIT_CODE=$?

# Deactivate virtual environment
deactivate

# Log completion
if [ $EXIT_CODE -eq 0 ]; then
    echo "[$(timestamp)] KB Sync Completed Successfully" >> "$LOG_FILE"
else
    echo "[$(timestamp)] KB Sync Failed with exit code $EXIT_CODE" >> "$LOG_FILE"
fi

echo "" >> "$LOG_FILE"

exit $EXIT_CODE
