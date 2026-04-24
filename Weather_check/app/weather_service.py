import requests
import time
from flask import current_app

class WeatherService:
    """Service for fetching weather data from OpenWeatherMap API"""
    
    _cache = {}

    @staticmethod
    def get_weather(city):
        """
        Fetch current weather and 5-day forecast for a city
        
        Args:
            city (str): City name
            
        Returns:
            dict: Weather data or error dict
        """
        city = city.lower().strip()

        # Check cache
        cache_timeout = current_app.config.get('CACHE_TIMEOUT', 600)
        if city in WeatherService._cache:
            data, timestamp = WeatherService._cache[city]
            if time.time() - timestamp < cache_timeout:
                return data

        try:
            api_key = current_app.config.get('WEATHER_API_KEY')
            base_url = current_app.config.get('WEATHER_API_URL')
            
            if not api_key:
                return {'error': 'API key not configured'}
            
            # Get current weather and forecast
            current_weather = WeatherService._get_current_weather(city, api_key, base_url)
            if 'error' in current_weather:
                return current_weather
            
            forecast = WeatherService._get_forecast(city, api_key, base_url)
            if 'error' in forecast:
                return forecast
            
            result = {
                'current': current_weather,
                'forecast': forecast
            }

            # Update cache
            WeatherService._cache[city] = (result, time.time())

            return result
        
        except Exception as e:
            return {'error': f'An error occurred: {str(e)}'}
    
    @staticmethod
    def _get_current_weather(city, api_key, base_url):
        """Fetch current weather data"""
        url = f'{base_url}/weather'
        params = {
            'q': city,
            'appid': api_key,
            'units': 'metric'  # Celsius
        }
        
        try:
            response = requests.get(url, params=params, timeout=5)
            response.raise_for_status()
            data = response.json()
            
            return {
                'city': data['name'],
                'country': data['sys']['country'],
                'temperature': round(data['main']['temp']),
                'feels_like': round(data['main']['feels_like']),
                'humidity': data['main']['humidity'],
                'pressure': data['main']['pressure'],
                'wind_speed': round(data['wind']['speed'], 1),
                'clouds': data['clouds']['all'],
                'description': data['weather'][0]['description'],
                'icon': data['weather'][0]['icon'],
                'main': data['weather'][0]['main'],
                'visibility': data['visibility']
            }
        
        except requests.exceptions.HTTPError as e:
            if response.status_code == 404:
                return {'error': 'City not found. Please check the spelling and try again.'}
            if response.status_code == 401:
                return {'error': 'Invalid API key. Please check your configuration.'}
            return {'error': f'Weather API error: {response.status_code}'}
        except requests.exceptions.Timeout:
            return {'error': 'Request timed out. Please try again.'}
        except Exception as e:
            return {'error': f'Error fetching current weather: {str(e)}'}
    
    @staticmethod
    def _get_forecast(city, api_key, base_url):
        """Fetch 5-day forecast data"""
        url = f'{base_url}/forecast'
        params = {
            'q': city,
            'appid': api_key,
            'units': 'metric'
        }
        
        try:
            response = requests.get(url, params=params, timeout=5)
            response.raise_for_status()
            data = response.json()
            
            # Process forecast data - group by day
            forecast_list = []
            seen_days = set()
            
            for item in data['list']:
                # Get date from the timestamp
                dt_txt = item['dt_txt']
                date_only = dt_txt.split()[0]
                
                # Take one forecast per day (noon time)
                if date_only not in seen_days and '12:00' in dt_txt:
                    seen_days.add(date_only)
                    forecast_list.append({
                        'date': date_only,
                        'temp_max': round(item['main']['temp_max']),
                        'temp_min': round(item['main']['temp_min']),
                        'description': item['weather'][0]['description'],
                        'icon': item['weather'][0]['icon'],
                        'humidity': item['main']['humidity'],
                        'wind_speed': round(item['wind']['speed'], 1)
                    })
            
            return forecast_list[:5]  # Return 5-day forecast
        
        except requests.exceptions.HTTPError as e:
            if response.status_code == 401:
                return {'error': 'Invalid API key. Please check your configuration.'}
            return {'error': 'Error fetching forecast'}
        except requests.exceptions.Timeout:
            return {'error': 'Request timed out'}
        except Exception as e:
            return {'error': f'Error fetching forecast: {str(e)}'}
