import pytest
from unittest.mock import MagicMock
from app.weather_service import WeatherService
from flask import Flask
import requests

@pytest.fixture
def app():
    app = Flask(__name__)
    app.config['WEATHER_API_KEY'] = 'test-key'
    app.config['WEATHER_API_URL'] = 'https://api.openweathermap.org/data/2.5'
    return app

def test_get_weather_success(app, mocker):
    with app.app_context():
        # Clear cache
        WeatherService._cache = {}

        mock_current_resp = MagicMock()
        mock_current_resp.json.return_value = {
            "name": "London",
            "sys": {"country": "GB"},
            "main": {"temp": 15.5, "feels_like": 14.2, "humidity": 80, "pressure": 1012},
            "wind": {"speed": 5.1},
            "clouds": {"all": 75},
            "weather": [{"description": "broken clouds", "icon": "04d", "main": "Clouds"}],
            "visibility": 10000
        }
        mock_current_resp.status_code = 200
        mock_current_resp.raise_for_status.return_value = None

        mock_forecast_resp = MagicMock()
        mock_forecast_resp.json.return_value = {
            "list": [
                {
                    "dt_txt": "2023-10-27 12:00:00",
                    "main": {"temp_max": 18, "temp_min": 12, "humidity": 70},
                    "weather": [{"description": "clear sky", "icon": "01d"}],
                    "wind": {"speed": 3.5}
                }
            ]
        }
        mock_forecast_resp.status_code = 200
        mock_forecast_resp.raise_for_status.return_value = None

        def side_effect(url, params=None, timeout=None):
            if url.endswith('/weather'):
                return mock_current_resp
            elif url.endswith('/forecast'):
                return mock_forecast_resp
            return None

        mocker.patch('requests.get', side_effect=side_effect)

        result = WeatherService.get_weather('London')

        assert 'error' not in result
        assert result['current']['city'] == 'London'
        assert result['current']['temperature'] == 16
        assert len(result['forecast']) == 1
        assert result['forecast'][0]['temp_max'] == 18

def test_get_weather_city_not_found(app, mocker):
    with app.app_context():
        WeatherService._cache = {}
        mock_resp = MagicMock()
        mock_resp.status_code = 404
        mock_resp.raise_for_status.side_effect = requests.exceptions.HTTPError(response=mock_resp)

        mocker.patch('requests.get', return_value=mock_resp)

        result = WeatherService.get_weather('InvalidCity')

        assert 'error' in result
        assert 'City not found' in result['error']

def test_get_weather_no_api_key(app):
    with app.app_context():
        WeatherService._cache = {}
        app.config['WEATHER_API_KEY'] = ''
        result = WeatherService.get_weather('London')
        assert result['error'] == 'API key not configured'

def test_get_weather_timeout(app, mocker):
    with app.app_context():
        WeatherService._cache = {}
        mocker.patch('requests.get', side_effect=requests.exceptions.Timeout())

        result = WeatherService.get_weather('London')

        assert 'error' in result
        assert 'timed out' in result['error']

def test_get_weather_invalid_api_key(app, mocker):
    with app.app_context():
        WeatherService._cache = {}
        mock_resp = MagicMock()
        mock_resp.status_code = 401
        mock_resp.raise_for_status.side_effect = requests.exceptions.HTTPError(response=mock_resp)

        mocker.patch('requests.get', return_value=mock_resp)

        result = WeatherService.get_weather('London')

        assert 'error' in result
        assert 'Invalid API key' in result['error']
