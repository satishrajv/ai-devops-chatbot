"""
Sample Flask Application for AI DevOps Platform
This is the application that will be deployed via the CI/CD pipeline
"""

from flask import Flask, jsonify, request
import os

app = Flask(__name__)


@app.route('/')
def home():
    return jsonify({
        "message": "Welcome to AI DevOps Platform",
        "version": "1.0.0",
        "status": "running"
    })


@app.route('/health')
def health():
    return jsonify({
        "status": "healthy",
        "service": "flask-app"
    })


@app.route('/api/info')
def info():
    return jsonify({
        "app_name": "AI DevOps Flask App",
        "environment": os.getenv("ENVIRONMENT", "development"),
        "build_number": os.getenv("BUILD_NUMBER", "local")
    })


@app.route('/api/echo', methods=['POST'])
def echo():
    data = request.get_json() or {}
    return jsonify({
        "received": data,
        "status": "success"
    })


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('ENVIRONMENT', 'development') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug)
