import json
import pytest
from unittest.mock import patch

def test_index(client):
    """Test the index page."""
    response = client.get('/')
    assert response.status_code == 200

def test_health_check(client):
    """Test the health check API."""
    response = client.get('/api/health')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'healthy'
    assert 'timestamp' in data

@patch('app.crawl_properties')
def test_search_properties_success(mock_crawl, client):
    """Test successful property search."""
    mock_crawl.return_value = [
        {
            "name": "테스트 아파트",
            "price": "10억",
            "trade_type": "매매",
            "info": "84/110㎡",
            "description": "좋은 아파트",
            "type": "아파트"
        }
    ]

    search_data = {
        "city": "서울시",
        "district": "강남구",
        "dong": "개포동",
        "propertyTypes": ["APT"],
        "tradeType": "all",
        "minPrice": 10,
        "maxPrice": 50
    }

    response = client.post(
        '/api/search',
        data=json.dumps(search_data),
        content_type='application/json'
    )

    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] is True
    assert data['count'] == 1
    assert data['data'][0]['name'] == "테스트 아파트"
    assert 'timestamp' in data

def test_search_properties_missing_params(client):
    """Test search API with missing required parameters."""
    search_data = {
        "city": "",
        "district": ""
    }

    response = client.post(
        '/api/search',
        data=json.dumps(search_data),
        content_type='application/json'
    )

    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data

def test_not_found(client):
    """Test 404 error handler."""
    response = client.get('/non-existent-route')
    assert response.status_code == 404
    data = json.loads(response.data)
    assert data['error'] == 'Not found'
