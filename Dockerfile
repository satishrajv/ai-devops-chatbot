FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy all requirements files
COPY flask_app/requirements.txt ./flask_app_requirements.txt
COPY streamlit_app/requirements.txt ./streamlit_app_requirements.txt
COPY kb-rag/requirements.txt ./kb_rag_requirements.txt
COPY kb-sync/requirements.txt ./kb_sync_requirements.txt

# Install all dependencies
RUN pip install --no-cache-dir -r flask_app_requirements.txt && \
    pip install --no-cache-dir -r streamlit_app_requirements.txt && \
    pip install --no-cache-dir -r kb_rag_requirements.txt && \
    pip install --no-cache-dir -r kb_sync_requirements.txt

# Copy application code
COPY flask_app/ ./flask_app/
COPY streamlit_app/ ./streamlit_app/
COPY kb-rag/ ./kb-rag/
COPY kb-sync/ ./kb-sync/
COPY docs/ ./docs/
COPY scripts/ ./scripts/
COPY start.sh .
COPY start-with-secrets.sh .
RUN chmod +x start.sh start-with-secrets.sh

# Environment variables - Jenkins
ENV JENKINS_URL=http://localhost:8080
ENV JENKINS_USER=""
ENV JENKINS_TOKEN=""

# Environment variables - OpenAI
ENV OPENAI_API_KEY=""

# Environment variables - Weaviate Cloud
ENV WEAVIATE_URL=""
ENV WEAVIATE_API_KEY=""
ENV WEAVIATE_COLLECTION_NAME="JenkinsKnowledgeBase"

# Environment variables - AWS (for kb-sync)
ENV AWS_ACCESS_KEY_ID=""
ENV AWS_SECRET_ACCESS_KEY=""
ENV AWS_REGION="us-east-1"
ENV S3_KB_BUCKET="jenkins-kb"

# Environment variables - App settings
ENV FLASK_PORT=5000
ENV STREAMLIT_PORT=8501
ENV ENVIRONMENT=production

# Expose all ports
EXPOSE 5000 8501

# Start all services (with AWS Secrets Manager)
CMD ["./start-with-secrets.sh"]
