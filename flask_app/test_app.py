"""
Tests for Flask Application
"""

import pytest
from app import app


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_home(client):
    response = client.get('/')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'running'
    assert 'version' in data


def test_health(client):
    response = client.get('/health')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'healthy'


def test_info(client):
    response = client.get('/api/info')
    assert response.status_code == 200
    data = response.get_json()
    assert 'app_name' in data
    assert 'environment' in data


def test_echo(client):
    test_data = {'message': 'hello'}
    response = client.post('/api/echo', json=test_data)
    assert response.status_code == 200
    data = response.get_json()
    assert data['received'] == test_data
    assert data['status'] == 'success'
