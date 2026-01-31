#!/bin/bash

echo "=========================================="
echo "Starting AI DevOps Platform"
echo "=========================================="

# Start Flask backend in background
echo "✓ Starting Flask API on port 5000..."
cd /app/flask_app && python app.py &
FLASK_PID=$!

# Wait for Flask to start
sleep 3

# Start Streamlit frontend with kb-rag integrated
echo "✓ Starting Streamlit Dashboard on port 8501..."
echo "  (Includes RAG Chatbot functionality)"
cd /app/streamlit_app && streamlit run app.py \
    --server.port=8501 \
    --server.address=0.0.0.0 \
    --server.headless=true \
    --server.enableCORS=false &
STREAMLIT_PID=$!

# Wait for Streamlit to start
sleep 5

echo "=========================================="
echo "✓ All services started successfully!"
echo "=========================================="
echo "Flask API:          Port 5000"
echo "Streamlit Dashboard: Port 8501"
echo "RAG Chatbot:        Integrated in Streamlit"
echo "=========================================="
echo "PIDs: Flask=$FLASK_PID, Streamlit=$STREAMLIT_PID"
echo "=========================================="

# Note: kb-sync runs as a scheduled job via Jenkins or cron
# It's not a continuously running service

# Keep container alive by following Streamlit logs
wait $STREAMLIT_PID
