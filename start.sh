#!/bin/bash

# Start Flask backend in background
echo "Starting Flask backend on port 5000..."
cd /app/flask_app && python app.py &

# Start Streamlit frontend
echo "Starting Streamlit frontend on port 8501..."
cd /app/streamlit_app && streamlit run app.py --server.port=8501 --server.address=0.0.0.0
