import requests
import time
from flask import current_app
from concurrent.futures import ThreadPoolExecutor

class WeatherService:
    """Service for fetching weather data from OpenWeatherMap API"""
    
    _cache = {}
    _session = requests.Session()
    
    # 한글 도시명 → 영문 도시명 매핑
    KOREAN_CITY_MAP = {
        '서울': 'Seoul',
        '부산': 'Busan',
        '대구': 'Daegu',
        '인천': 'Incheon',
        '광주': 'Gwangju',
        '대전': 'Daejeon',
        '울산': 'Ulsan',
        '경기': 'Gyeonggi',
        '강원': 'Gangwon',
        '충북': 'North Chungcheong',
        '충남': 'South Chungcheong',
        '전북': 'North Jeolla',
        '전남': 'South Jeolla',
        '경북': 'North Gyeongsang',
        '경남': 'South Gyeongsang',
        '제주': 'Jeju',
        '도쿄': 'Tokyo',
        '교토': 'Kyoto',
        '오사카': 'Osaka',
        '뉴욕': 'New York',
        '로스앤젤레스': 'Los Angeles',
        '런던': 'London',
        '파리': 'Paris',
        '도쿄': 'Tokyo',
        '베이징': 'Beijing',
        '상하이': 'Shanghai',
        '홍콩': 'Hong Kong',
        '싱가포르': 'Singapore',
        '방콕': 'Bangkok',
        '뉴델리': 'New Delhi',
        '뭄바이': 'Mumbai',
        '더블린': 'Dublin',
        '베를린': 'Berlin',
        '마드리드': 'Madrid',
        '로마': 'Rome',
        '암스테르담': 'Amsterdam',
        '뮌헨': 'Munich',
        '취리히': 'Zurich',
        '바르셀로나': 'Barcelona',
        '리스본': 'Lisbon',
        '아테네': 'Athens',
        '이스탄불': 'Istanbul',
        '두바이': 'Dubai',
        '카이로': 'Cairo',
        '케이프타운': 'Cape Town',
        '시드니': 'Sydney',
        '멜버른': 'Melbourne',
        '오클랜드': 'Auckland',
        '토론토': 'Toronto',
        '밴쿠버': 'Vancouver',
        '멕시코시티': 'Mexico City',
        '상파울루': 'Sao Paulo',
        '부에노스아이레스': 'Buenos Aires',
    }

    @staticmethod
    def convert_korean_to_english(city_name):
        """
        Convert Korean city name to English
        
        Args:
            city_name (str): City name in Korean or English
            
        Returns:
            tuple: (english_name, korean_display_name)
        """
        city_name = city_name.strip()
        
        # Check if input is Korean
        if WeatherService._is_korean(city_name):
            english_name = WeatherService.KOREAN_CITY_MAP.get(city_name)
            if english_name:
                return english_name, city_name
            else:
                return city_name, city_name
        
        # If English, try to find Korean equivalent for display
        korean_name = None
        for korean, english in WeatherService.KOREAN_CITY_MAP.items():
            if english.lower() == city_name.lower():
                korean_name = korean
                break
        
        return city_name, korean_name
    
    @staticmethod
    def _is_korean(text):
        """Check if text contains Korean characters"""
        for char in text:
            if ord(char) >= 0xAC00 and ord(char) <= 0xD7A3:
                return True
        return False

    @staticmethod
    def get_weather(city, original_city=None):
        """
        Fetch current weather and 5-day forecast for a city
        
        Args:
            city (str): City name (English or Korean)
            original_city (str): Original city name for display (Korean)
            
        Returns:
            dict: Weather data or error dict
        """
        # Convert Korean to English if needed
        if WeatherService._is_korean(city):
            english_city, korean_city = WeatherService.convert_korean_to_english(city)
            if original_city is None:
                original_city = korean_city
            city = english_city
        
        city_lower = city.lower().strip()

        # Check cache
        cache_timeout = current_app.config.get('CACHE_TIMEOUT', 600)
        if city_lower in WeatherService._cache:
            data, timestamp = WeatherService._cache[city_lower]
            if time.time() - timestamp < cache_timeout:
                return data

        try:
            api_key = current_app.config.get('WEATHER_API_KEY')
            base_url = current_app.config.get('WEATHER_API_URL')
            
            if not api_key:
                return {'error': 'API 키가 설정되지 않았습니다'}
            
            # Use ThreadPoolExecutor to parallelize API calls
            # Extract current_app config before entering threads
            with ThreadPoolExecutor(max_workers=2) as executor:
                future_current = executor.submit(
                    WeatherService._get_current_weather,
                    city, api_key, base_url, original_city
                )
                future_forecast = executor.submit(
                    WeatherService._get_forecast,
                    city, api_key, base_url
                )

                current_weather = future_current.result()
                if 'error' in current_weather:
                    return current_weather

                forecast = future_forecast.result()
                if 'error' in forecast:
                    return forecast
            
            result = {
                'current': current_weather,
                'forecast': forecast
            }

            # Update cache
            WeatherService._cache[city_lower] = (result, time.time())

            return result
        
        except Exception as e:
            return {'error': f'오류 발생: {str(e)}'}
    
    @staticmethod
    def _get_current_weather(city, api_key, base_url, original_city=None):
        """Fetch current weather data"""
        url = f'{base_url}/weather'
        params = {
            'q': city,
            'appid': api_key,
            'units': 'metric'  # Celsius
        }
        
        try:
            # Use session for connection pooling
            response = WeatherService._session.get(url, params=params, timeout=5)
            response.raise_for_status()
            data = response.json()
            
            # Use original Korean city name if provided
            city_display = original_city if original_city else data['name']
            
            return {
                'city': city_display,
                'city_en': data['name'],
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
                return {'error': '도시를 찾을 수 없습니다. 도시명 철자를 확인하세요.'}
            if response.status_code == 401:
                return {'error': 'API 키가 유효하지 않습니다. 설정을 확인하세요.'}
            return {'error': f'날씨 API 오류: {response.status_code}'}
        except requests.exceptions.Timeout:
            return {'error': '요청 시간 초과. 다시 시도하세요.'}
        except Exception as e:
            return {'error': f'현재 날씨 조회 오류: {str(e)}'}
    
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
            # Use session for connection pooling
            response = WeatherService._session.get(url, params=params, timeout=5)
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
                return {'error': 'API 키가 유효하지 않습니다. 설정을 확인하세요.'}
            return {'error': '예보 조회 오류'}
        except requests.exceptions.Timeout:
            return {'error': '요청 시간 초과'}
        except Exception as e:
            return {'error': f'예보 조회 오류: {str(e)}'}
