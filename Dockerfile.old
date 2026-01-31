FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY flask_app/ ./flask_app/
COPY streamlit_app/ ./streamlit_app/
COPY start.sh .
RUN chmod +x start.sh

# Environment variables
ENV FLASK_PORT=5000
ENV STREAMLIT_PORT=8501
ENV ENVIRONMENT=development
ENV JENKINS_URL=http://localhost:8080
ENV JENKINS_USER=""
ENV JENKINS_TOKEN=""

# Expose both ports
EXPOSE 5000 8501

# Start both services
CMD ["./start.sh"]
