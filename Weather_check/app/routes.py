from flask import Blueprint, render_template, request, jsonify
from app.weather_service import WeatherService

weather_bp = Blueprint('weather', __name__)

@weather_bp.route('/', methods=['GET', 'POST'])
def index():
    """Homepage - display weather search form and results"""
    weather_data = None
    error = None
    city_searched = None
    
    if request.method == 'POST':
        city = request.form.get('city', '').strip()
        city_searched = city
        
        if not city:
            error = '도시명을 입력해주세요.'
        else:
            # Fetch weather data (handles Korean to English conversion)
            result = WeatherService.get_weather(city)
            
            if 'error' in result:
                error = result['error']
            else:
                weather_data = result
    
    return render_template('index.html', 
                         weather_data=weather_data, 
                         error=error,
                         city_searched=city_searched)

@weather_bp.route('/api/weather/<city>')
def api_weather(city):
    """API endpoint for fetching weather data"""
    if not city:
        return jsonify({'error': '도시명이 필요합니다'}), 400
    
    result = WeatherService.get_weather(city)
    
    if 'error' in result:
        return jsonify(result), 400
    
    return jsonify(result), 200
