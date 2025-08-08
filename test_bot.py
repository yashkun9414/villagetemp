#!/usr/bin/env python3
"""
Test script to verify bot functionality
"""

import os
from dotenv import load_dotenv

load_dotenv()

def test_bot_setup():
    """Test bot configuration"""
    print("🧪 Testing Bot Setup...")
    
    # Check token
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    if token:
        print(f"✅ Bot token found: {token[:10]}...")
    else:
        print("❌ Bot token missing!")
        return False
    
    # Test imports
    try:
        import bot_host
        print("✅ Bot code imports successfully")
    except Exception as e:
        print(f"❌ Bot import failed: {e}")
        return False
    
    # Test data loading
    try:
        bot_host.load_data()
        print("✅ Data loading works")
    except Exception as e:
        print(f"❌ Data loading failed: {e}")
        return False
    
    # Test weather API
    try:
        from weather_api import get_weather_for_locations
        weather_data = get_weather_for_locations()
        if weather_data:
            print(f"✅ Weather API works - got data for {len(weather_data)} locations")
        else:
            print("⚠️ Weather API returned no data")
    except Exception as e:
        print(f"❌ Weather API failed: {e}")
    
    print("\n🎉 Bot setup test completed!")
    return True

if __name__ == "__main__":
    test_bot_setup()