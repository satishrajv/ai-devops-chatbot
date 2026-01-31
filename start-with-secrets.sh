#!/bin/bash

echo "=========================================="
echo "AI DevOps Platform - Starting with AWS Secrets Manager"
echo "=========================================="

# Fetch secrets from AWS Secrets Manager and export as environment variables
echo "✓ Fetching credentials from AWS Secrets Manager..."
eval $(python3 /app/scripts/fetch_secrets.py)

if [ $? -ne 0 ]; then
    echo "❌ Failed to fetch secrets from AWS Secrets Manager"
    echo "   Make sure:"
    echo "   1. EC2 instance has IAM role with secretsmanager:GetSecretValue permission"
    echo "   2. Secret 'ai-devops-platform/credentials' exists in Secrets Manager"
    exit 1
fi

echo "✓ Credentials loaded successfully"

# Verify required environment variables are set
required_vars=("OPENAI_API_KEY" "WEAVIATE_URL" "WEAVIATE_API_KEY" "JENKINS_USER" "JENKINS_TOKEN")
missing_vars=()

for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        missing_vars+=("$var")
    fi
done

if [ ${#missing_vars[@]} -ne 0 ]; then
    echo "❌ Missing required environment variables: ${missing_vars[*]}"
    exit 1
fi

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

echo "=========================================="
echo "✓ All services started successfully"
echo "  Flask API: http://localhost:5000"
echo "  Streamlit UI: http://localhost:8501"
echo "=========================================="

# Keep container alive by following Streamlit logs
wait $STREAMLIT_PID
