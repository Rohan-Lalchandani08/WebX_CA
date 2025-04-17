import os
import requests
import logging
from datetime import datetime

# OpenWeatherMap API settings
API_KEY = os.environ.get("OPENWEATHER_API_KEY", "")
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

def get_weather_for_city(city_name):
    """
    Get current weather for a city using OpenWeatherMap API
    Returns weather data or None if API request fails
    """
    try:
        params = {
            'q': city_name,
            'appid': API_KEY,
            'units': 'metric'  # Use metric units (Celsius)
        }
        
        # If no API key is provided, return mock data for development
        if not API_KEY:
            logging.warning("No OpenWeatherMap API key provided. Using mock weather data.")
            return {
                'error': 'No API key',
                'mock_data': True,
                'temp': 22,
                'description': 'Sunny with clouds',
                'humidity': 60,
                'wind_speed': 5.1,
                'icon': '04d'
            }
        
        response = requests.get(BASE_URL, params=params)
        
        if response.status_code == 200:
            data = response.json()
            weather = {
                'temp': round(data['main']['temp']),
                'description': data['weather'][0]['description'],
                'humidity': data['main']['humidity'],
                'wind_speed': data['wind']['speed'],
                'icon': data['weather'][0]['icon']
            }
            return weather
        else:
            logging.error(f"Weather API error: {response.status_code}, {response.text}")
            return None
    
    except Exception as e:
        logging.error(f"Error fetching weather data: {str(e)}")
        return None
