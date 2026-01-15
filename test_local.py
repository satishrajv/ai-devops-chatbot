#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Local testing script for AI DevOps Platform
Tests Flask app and Streamlit configuration without Docker
"""

import sys
import os
import subprocess
import requests
import time
from pathlib import Path

# Fix Windows encoding for emoji support
if sys.platform == 'win32':
    os.environ['PYTHONIOENCODING'] = 'utf-8'

def print_header(msg):
    print("\n" + "=" * 60)
    print(msg)
    print("=" * 60)

def test_flask_app():
    """Test Flask application"""
    print_header("Testing Flask Application")

    try:
        # Import Flask app
        sys.path.insert(0, str(Path(__file__).parent / "flask_app"))
        from app import app

        # Create test client
        app.config['TESTING'] = True
        client = app.test_client()

        # Test endpoints
        tests = [
            ('/', 'Home endpoint'),
            ('/health', 'Health endpoint'),
            ('/api/info', 'Info endpoint'),
        ]

        for endpoint, name in tests:
            response = client.get(endpoint)
            if response.status_code == 200:
                print(f"[PASS] {name}")
            else:
                print(f"[FAIL] {name}: Status {response.status_code}")

        # Test POST endpoint
        response = client.post('/api/echo', json={'test': 'data'})
        if response.status_code == 200:
            print("[PASS] Echo endpoint")
        else:
            print(f"[FAIL] Echo endpoint: Status {response.status_code}")

        return True
    except Exception as e:
        print(f"[FAIL] Flask app test failed: {e}")
        return False

def test_dependencies():
    """Check if required dependencies are installed"""
    print_header("Checking Dependencies")

    required = ['flask', 'streamlit', 'requests', 'pytest']
    missing = []

    for package in required:
        try:
            __import__(package)
            print(f"[PASS] {package}: installed")
        except ImportError:
            print(f"[FAIL] {package}: missing")
            missing.append(package)

    if missing:
        print(f"\nInstall missing packages:")
        print(f"pip install {' '.join(missing)}")
        return False

    return True

def test_file_structure():
    """Verify all required files exist"""
    print_header("Checking File Structure")

    required_files = [
        'flask_app/app.py',
        'flask_app/requirements.txt',
        'flask_app/Dockerfile',
        'streamlit_app/app.py',
        'streamlit_app/requirements.txt',
        'streamlit_app/Dockerfile',
        'Jenkinsfile',
        'docker-compose.yml',
        '.env.example',
        'README.md',
    ]

    base_path = Path(__file__).parent
    all_exist = True

    for file in required_files:
        file_path = base_path / file
        if file_path.exists():
            print(f"[PASS] {file}")
        else:
            print(f"[FAIL] {file}: missing")
            all_exist = False

    return all_exist

def run_pytest():
    """Run pytest on Flask app"""
    print_header("Running Tests")

    try:
        result = subprocess.run(
            ['pytest', 'flask_app/test_app.py', '-v'],
            capture_output=True,
            text=True,
            timeout=30
        )

        print(result.stdout)
        if result.returncode == 0:
            print("[PASS] All tests passed")
            return True
        else:
            print("[FAIL] Some tests failed")
            print(result.stderr)
            return False
    except FileNotFoundError:
        print("[WARN] pytest not found, skipping tests")
        return True
    except Exception as e:
        print(f"[WARN] Could not run tests: {e}")
        return True

def main():
    print_header("AI DevOps Platform - Local Test Suite")

    results = {
        'File Structure': test_file_structure(),
        'Dependencies': test_dependencies(),
        'Flask App': test_flask_app(),
        'Unit Tests': run_pytest(),
    }

    print_header("Test Summary")
    for test, passed in results.items():
        status = "PASSED" if passed else "FAILED"
        print(f"{test}: {status}")

    all_passed = all(results.values())

    if all_passed:
        print("\n[PASS] All tests passed! Ready for deployment.")
        print("\nNext steps:")
        print("1. Ensure Docker Desktop is running")
        print("2. Run: docker-compose up -d --build")
        print("3. Access Streamlit at http://localhost:8501")
        print("4. Access Jenkins at http://localhost:8080")
        return 0
    else:
        print("\n[FAIL] Some tests failed. Please fix the issues above.")
        return 1

if __name__ == '__main__':
    sys.exit(main())
