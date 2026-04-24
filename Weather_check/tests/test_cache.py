import pytest
from unittest.mock import MagicMock
from app.weather_service import WeatherService
from flask import Flask
import time

@pytest.fixture
def app():
    app = Flask(__name__)
    app.config['WEATHER_API_KEY'] = 'test-key'
    app.config['WEATHER_API_URL'] = 'https://api.openweathermap.org/data/2.5'
    app.config['CACHE_TIMEOUT'] = 600
    return app

def test_get_weather_caching(app, mocker):
    with app.app_context():
        # Clear cache before test
        WeatherService._cache = {}

        mock_current_resp = MagicMock()
        mock_current_resp.status_code = 200
        mock_current_resp.json.return_value = {
            "name": "London",
            "sys": {"country": "GB"},
            "main": {"temp": 15, "feels_like": 14, "humidity": 80, "pressure": 1012},
            "wind": {"speed": 5},
            "clouds": {"all": 75},
            "weather": [{"description": "cloudy", "icon": "04d", "main": "Clouds"}],
            "visibility": 10000
        }

        mock_forecast_resp = MagicMock()
        mock_forecast_resp.status_code = 200
        mock_forecast_resp.json.return_value = {
            "list": []
        }

        mock_get = mocker.patch('requests.get')
        mock_get.side_effect = [mock_current_resp, mock_forecast_resp]

        # First call - should call requests.get
        result1 = WeatherService.get_weather('London')
        assert mock_get.call_count == 2

        # Second call - should return from cache
        result2 = WeatherService.get_weather('London')
        assert mock_get.call_count == 2
        assert result1 == result2

def test_get_weather_cache_expiration(app, mocker):
    with app.app_context():
        WeatherService._cache = {}
        app.config['CACHE_TIMEOUT'] = 1 # 1 second timeout

        mock_current_resp = MagicMock()
        mock_current_resp.status_code = 200
        mock_current_resp.json.return_value = {
            "name": "London", "sys": {"country": "GB"},
            "main": {"temp": 15, "feels_like": 14, "humidity": 80, "pressure": 1012},
            "wind": {"speed": 5}, "clouds": {"all": 75},
            "weather": [{"description": "cloudy", "icon": "04d", "main": "Clouds"}],
            "visibility": 10000
        }

        mock_forecast_resp = MagicMock()
        mock_forecast_resp.status_code = 200
        mock_forecast_resp.json.return_value = {"list": []}

        mock_get = mocker.patch('requests.get')
        mock_get.side_effect = [
            mock_current_resp, mock_forecast_resp, # First call
            mock_current_resp, mock_forecast_resp  # Second call after expiration
        ]

        # First call
        WeatherService.get_weather('London')
        assert mock_get.call_count == 2

        # Wait for expiration
        time.sleep(1.1)

        # Second call - should call requests.get again
        WeatherService.get_weather('London')
        assert mock_get.call_count == 4
