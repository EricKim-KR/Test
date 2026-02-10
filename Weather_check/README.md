# Weather Check

A Flask web application that displays current weather and 5-day forecast for any city in the world.

## Features

- 🌤️ **Current Weather**: Display temperature, humidity, wind speed, pressure, cloudiness, and visibility
- 📅 **5-Day Forecast**: Get upcoming weather forecasts with temperature ranges and conditions
- 🎨 **Weather Icons**: Beautiful weather icons from OpenWeatherMap
- 📱 **Responsive Design**: Works seamlessly on desktop, tablet, and mobile devices
- ⚡ **Real-time Data**: Fetches live weather data from OpenWeatherMap API

## Prerequisites

- Python 3.8+
- pip (Python package manager)

## Installation

1. **Clone or navigate to the project directory**:
   ```bash
   cd Weather_check
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment**:
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

5. **Get an OpenWeatherMap API key**:
   - Visit [OpenWeatherMap](https://openweathermap.org/api)
   - Sign up for a free account
   - Generate an API key from your account dashboard

6. **Configure environment variables**:
   - Edit the `.env` file and replace `your_openweathermap_api_key_here` with your actual API key:
     ```
     WEATHER_API_KEY=your_actual_api_key_here
     ```

## Running the Application

1. **Make sure virtual environment is activated**

2. **Run the Flask app**:
   ```bash
   python run.py
   ```

3. **Open your browser** and navigate to:
   ```
   http://localhost:5000
   ```

4. **Start checking weather**:
   - Enter a city name in the search box
   - Click "Search" or press Enter
   - View the current weather and 5-day forecast

## Project Structure

```
Weather_check/
├── app/
│   ├── __init__.py          # Flask app factory
│   ├── routes.py            # Route handlers
│   ├── weather_service.py   # Weather API integration
│   ├── templates/
│   │   └── index.html       # Main template
│   └── static/
│       └── css/
│           └── style.css    # Stylesheet
├── config.py                # Configuration settings
├── run.py                   # Entry point
├── requirements.txt         # Python dependencies
├── .env                     # Environment variables
└── README.md               # This file
```

## API Endpoints

### Web Interface
- `GET /` - Main page with weather search form
- `POST /` - Submit city search

### REST API
- `GET /api/weather/<city>` - Get weather data for a city (JSON response)

## Configuration

Edit `config.py` to modify settings:
- `SECRET_KEY`: Flask session secret key
- `WEATHER_API_KEY`: OpenWeatherMap API key (loaded from `.env`)
- `WEATHER_API_URL`: OpenWeatherMap API base URL
- `CACHE_TIMEOUT`: Cache duration in seconds

## Troubleshooting

### "City not found" error
- Check spelling of the city name
- Try using a larger city name
- Use format like "City, Country" (e.g., "London, UK")

### "API key not configured" error
- Ensure `.env` file has your OpenWeatherMap API key
- Application needs to be restarted after updating `.env`

### Slow response time
- This is normal for the first request
- OpenWeatherMap API may have rate limits on free tier (~1000 calls/day)
- Consider implementing caching in production

## Technologies Used

- **Flask** - Python web framework
- **Requests** - HTTP library for API calls
- **OpenWeatherMap API** - Weather data provider
- **HTML/CSS** - Frontend

## License

MIT License - Feel free to use this project for personal or educational purposes.

## Notes

- The free tier of OpenWeatherMap allows ~1000 API calls per day
- Weather data is fetched on-demand (no caching in this version)
- Icons are loaded from OpenWeatherMap CDN

## Future Enhancements

- Add caching to reduce API calls
- Implement user favorite cities
- Add weather alerts
- Support for multiple languages
- Detailed historical weather data
