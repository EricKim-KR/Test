import pytest
from unittest.mock import patch, MagicMock
from app.weather_service import WeatherService
from flask import Flask
import time

@pytest.fixture
def app():
    app = Flask(__name__)
    app.config['WEATHER_API_KEY'] = 'fake_key'
    app.config['WEATHER_API_URL'] = 'http://api.fake.com'
    app.config['CACHE_TIMEOUT'] = 600
    return app

def test_get_weather_cache(app):
    with app.app_context():
        # Clear cache before test
        WeatherService._cache = {}

        mock_current = {'city': 'London', 'temperature': 20}
        mock_forecast = [{'date': '2023-01-01', 'temp_max': 22, 'temp_min': 18}]

        with patch.object(WeatherService, '_get_current_weather', return_value=mock_current) as mock_curr_method:
            with patch.object(WeatherService, '_get_forecast', return_value=mock_forecast) as mock_fore_method:

                # First call - should call API
                result1 = WeatherService.get_weather('London')
                assert result1['current'] == mock_current
                assert mock_curr_method.call_count == 1

                # Second call - should use cache
                result2 = WeatherService.get_weather('London')
                assert result2 == result1
                assert mock_curr_method.call_count == 1

                # Third call with different city - should call API
                WeatherService.get_weather('Paris')
                assert mock_curr_method.call_count == 2

def test_get_weather_parallel_calls(app):
    with app.app_context():
        WeatherService._cache = {}

        with patch.object(WeatherService, '_get_current_weather', return_value={'city': 'London'}) as mock_curr:
            with patch.object(WeatherService, '_get_forecast', return_value=[]) as mock_fore:
                WeatherService.get_weather('London')

                assert mock_curr.called
                assert mock_fore.called
