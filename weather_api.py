#!/usr/bin/env python3
"""
Real weather data fetcher using Open-Meteo API
"""

import requests
import pandas as pd
import logging
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)

class WeatherAPI:
    def __init__(self):
        self.base_url = "https://api.open-meteo.com/v1/forecast"
        
    def get_weather_data(self, latitude, longitude, location_name=""):
        """Get current weather data for a location"""
        try:
            params = {
                'latitude': latitude,
                'longitude': longitude,
                'current': 'temperature_2m,relative_humidity_2m,wind_speed_10m,weather_code',
                'daily': 'temperature_2m_max,temperature_2m_min,weather_code',
                'timezone': 'Asia/Kolkata',
                'forecast_days': 1
            }
            
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            current = data.get('current', {})
            daily = data.get('daily', {})
            
            weather_info = {
                'location': location_name,
                'latitude': latitude,
                'longitude': longitude,
                'current_temp': current.get('temperature_2m', 0),
                'humidity': current.get('relative_humidity_2m', 0),
                'wind_speed': current.get('wind_speed_10m', 0),
                'weather_code': current.get('weather_code', 0),
                'max_temp': daily.get('temperature_2m_max', [0])[0] if daily.get('temperature_2m_max') else 0,
                'min_temp': daily.get('temperature_2m_min', [0])[0] if daily.get('temperature_2m_min') else 0,
                'timestamp': datetime.now().isoformat(),
                'weather_description': self.get_weather_description(current.get('weather_code', 0))
            }
            
            return weather_info
            
        except Exception as e:
            logger.error(f"Error fetching weather for {location_name}: {e}")
            return None
    
    def get_weather_description(self, weather_code):
        """Convert weather code to description"""
        weather_codes = {
            0: "Clear sky",
            1: "Mainly clear",
            2: "Partly cloudy",
            3: "Overcast",
            45: "Fog",
            48: "Depositing rime fog",
            51: "Light drizzle",
            53: "Moderate drizzle",
            55: "Dense drizzle",
            61: "Slight rain",
            63: "Moderate rain",
            65: "Heavy rain",
            71: "Slight snow",
            73: "Moderate snow",
            75: "Heavy snow",
            77: "Snow grains",
            80: "Slight rain showers",
            81: "Moderate rain showers",
            82: "Violent rain showers",
            85: "Slight snow showers",
            86: "Heavy snow showers",
            95: "Thunderstorm",
            96: "Thunderstorm with slight hail",
            99: "Thunderstorm with heavy hail"
        }
        return weather_codes.get(weather_code, "Unknown")
    
    def check_temperature_alerts(self, weather_data, hot_threshold=40, cold_threshold=5):
        """Check if temperature requires alerts"""
        if not weather_data:
            return None
            
        current_temp = weather_data['current_temp']
        max_temp = weather_data['max_temp']
        min_temp = weather_data['min_temp']
        
        alerts = []
        
        # Hot weather alert
        if current_temp >= hot_threshold or max_temp >= hot_threshold:
            alerts.append({
                'type': 'Hot Weather Alert',
                'severity': 'high' if current_temp >= 45 else 'medium',
                'temperature': current_temp,
                'max_temp': max_temp,
                'message': f"🌡️ HIGH TEMPERATURE: {current_temp}°C (Max: {max_temp}°C) in {weather_data['location']}. Stay hydrated and avoid outdoor activities during peak hours."
            })
        
        # Cold weather alert
        if current_temp <= cold_threshold or min_temp <= cold_threshold:
            alerts.append({
                'type': 'Cold Weather Alert',
                'severity': 'high' if current_temp <= 0 else 'medium',
                'temperature': current_temp,
                'min_temp': min_temp,
                'message': f"🥶 LOW TEMPERATURE: {current_temp}°C (Min: {min_temp}°C) in {weather_data['location']}. Keep warm and protect crops from frost."
            })
        
        return alerts if alerts else None

def get_weather_for_locations():
    """Get weather data for major Gujarat locations"""
    try:
        # Load location data
        df = pd.read_csv('merged_village_temperature_data.csv')
        
        # Get unique district centers (sample some major ones)
        major_locations = [
            {'name': 'Ahmedabad', 'lat': 23.0225, 'lon': 72.5714},
            {'name': 'Surat', 'lat': 21.1702, 'lon': 72.8311},
            {'name': 'Vadodara', 'lat': 22.3072, 'lon': 73.1812},
            {'name': 'Rajkot', 'lat': 22.3039, 'lon': 70.8022},
            {'name': 'Bhavnagar', 'lat': 21.7645, 'lon': 72.1519},
            {'name': 'Jamnagar', 'lat': 22.4707, 'lon': 70.0577},
            {'name': 'Gandhinagar', 'lat': 23.2156, 'lon': 72.6369},
            {'name': 'Anand', 'lat': 22.5645, 'lon': 72.9289}
        ]
        
        weather_api = WeatherAPI()
        weather_data = []
        
        for location in major_locations:
            data = weather_api.get_weather_data(
                location['lat'], 
                location['lon'], 
                location['name']
            )
            if data:
                weather_data.append(data)
        
        return weather_data
        
    except Exception as e:
        logger.error(f"Error getting weather for locations: {e}")
        return []

def get_weather_for_taluka(district, taluka):
    """Get weather data for specific taluka"""
    try:
        df = pd.read_csv('merged_village_temperature_data.csv')
        
        # Find the taluka coordinates
        taluka_data = df[
            (df['District Name'] == district) & 
            (df['Taluka Name'] == taluka)
        ].iloc[0]
        
        if pd.isna(taluka_data['Taluka Latitude']) or pd.isna(taluka_data['Taluka Longitude']):
            return None
            
        lat = float(taluka_data['Taluka Latitude'])
        lon = float(taluka_data['Taluka Longitude'])
        
        weather_api = WeatherAPI()
        return weather_api.get_weather_data(lat, lon, f"{taluka}, {district}")
        
    except Exception as e:
        logger.error(f"Error getting weather for {taluka}, {district}: {e}")
        return None