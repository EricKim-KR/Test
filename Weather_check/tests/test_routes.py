import pytest
from app import create_app
from unittest.mock import patch

@pytest.fixture
def client():
    app = create_app('testing')
    with app.test_client() as client:
        yield client

def test_index_get(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b'Weather Check' in response.data
    assert b'Enter a city name above to get started!' in response.data

@patch('app.weather_service.WeatherService.get_weather')
def test_index_post_success(mock_get_weather, client):
    mock_get_weather.return_value = {
        'current': {
            'city': 'London',
            'country': 'GB',
            'temperature': 15,
            'description': 'cloudy',
            'icon': '04d',
            'feels_like': 14,
            'humidity': 80,
            'pressure': 1012,
            'wind_speed': 5,
            'clouds': 75,
            'visibility': 10000
        },
        'forecast': []
    }

    response = client.post('/', data={'city': 'London'})
    assert response.status_code == 200
    assert b'London, GB' in response.data
    assert b'15' in response.data
    assert b'Cloudy' in response.data

@patch('app.weather_service.WeatherService.get_weather')
def test_index_post_error(mock_get_weather, client):
    mock_get_weather.return_value = {'error': 'City not found'}

    response = client.post('/', data={'city': 'UnknownCity'})
    assert response.status_code == 200
    assert b'City not found' in response.data

def test_api_weather_success(client):
    with patch('app.weather_service.WeatherService.get_weather') as mock_get_weather:
        mock_get_weather.return_value = {'city': 'London'}
        response = client.get('/api/weather/London')
        assert response.status_code == 200
        assert response.json == {'city': 'London'}

def test_api_weather_error(client):
    with patch('app.weather_service.WeatherService.get_weather') as mock_get_weather:
        mock_get_weather.return_value = {'error': 'Some error'}
        response = client.get('/api/weather/London')
        assert response.status_code == 400
        assert response.json == {'error': 'Some error'}
