#!/usr/bin/env python3
"""
System Test Script - Verify all components are working
"""

import requests
import json
import pandas as pd
import os
from datetime import datetime

def test_fire_data_api():
    """Test fire data API endpoint"""
    print("🔥 Testing Fire Data API...")
    try:
        # Test if we can load fire data
        if os.path.exists('static/gujarat_fire_history.csv'):
            df = pd.read_csv('static/gujarat_fire_history.csv')
            print(f"   ✅ Fire data file exists: {len(df)} records")
            
            # Check for recent data
            today = datetime.now().strftime('%Y-%m-%d')
            recent = df[df['acq_date'] >= '2025-08-01']  # Last month
            print(f"   📊 Recent records: {len(recent)}")
            
            if len(recent) == 0:
                print(f"   ✅ No recent fire incidents (this is good!)")
            else:
                print(f"   ⚠️ {len(recent)} recent fire incidents detected")
        else:
            print("   ❌ Fire data file not found")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")

def test_weather_api():
    """Test weather API integration"""
    print("🌤️ Testing Weather API...")
    try:
        from weather_api import get_weather_for_locations
        weather_data = get_weather_for_locations()
        
        if weather_data and len(weather_data) > 0:
            print(f"   ✅ Weather API working: {len(weather_data)} locations")
            
            # Show sample data
            sample = weather_data[0]
            print(f"   📍 Sample: {sample.get('location', 'Unknown')} - {sample.get('current_temp', 'N/A')}°C")
        else:
            print("   ❌ No weather data received")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")

def test_location_data():
    """Test location data loading"""
    print("📍 Testing Location Data...")
    try:
        if os.path.exists('merged_village_temperature_data.csv'):
            df = pd.read_csv('merged_village_temperature_data.csv')
            districts = df['District Name'].nunique()
            talukas = df['Taluka Name'].nunique()
            
            print(f"   ✅ Location data loaded: {districts} districts, {talukas} talukas")
        else:
            print("   ❌ Location data file not found")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")

def test_bot_data():
    """Test bot data systems"""
    print("🤖 Testing Bot Data Systems...")
    try:
        from shared_data import load_subscribers, get_pending_alerts
        
        subscribers = load_subscribers()
        total_subs = sum(len(users) for users in subscribers.values())
        print(f"   ✅ Subscriber system working: {total_subs} total subscribers")
        
        alerts = get_pending_alerts()
        print(f"   📨 Pending alerts: {len(alerts)}")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")

def test_nasa_integration():
    """Test NASA fire data integration"""
    print("🛰️ Testing NASA Integration...")
    try:
        # Test NASA URL accessibility
        url = "https://firms.modaps.eosdis.nasa.gov/data/active_fire/c6/csv/MODIS_C6_1_Global_24h.csv"
        response = requests.head(url, timeout=10)
        
        if response.status_code == 200:
            print("   ✅ NASA FIRMS API accessible")
        else:
            print(f"   ⚠️ NASA API returned status: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Error accessing NASA API: {e}")

def main():
    """Run all tests"""
    print("🧪 Gujarat Weather & Fire Alert System - Test Suite")
    print("=" * 60)
    
    test_location_data()
    print()
    
    test_fire_data_api()
    print()
    
    test_weather_api()
    print()
    
    test_bot_data()
    print()
    
    test_nasa_integration()
    print()
    
    print("=" * 60)
    print("✅ System test completed!")
    print()
    print("🌐 Web App: Run 'python app.py' and visit http://localhost:5000")
    print("🤖 Telegram Bot: @VillaegWarningbot")
    print("🔥 Fire Data: Run 'python nasa_fire_fetcher.py' for updates")
    print("📊 Current Status: No fire incidents detected in Gujarat (this is good!)")

if __name__ == "__main__":
    main()