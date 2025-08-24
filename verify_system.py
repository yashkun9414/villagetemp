#!/usr/bin/env python3
"""
System Verification Script
Verifies all core features work after cleanup
"""

import os
import sys
import pandas as pd
from datetime import datetime

def test_data_files():
    """Test that required data files exist"""
    print("📁 Testing Data Files...")
    
    required_files = [
        'merged_village_temperature_data.csv',
        'requirements.txt',
        'app.py',
        'bot_host.py',
        'shared_data.py',
        'weather_api.py',
        'nasa_fire_fetcher.py'
    ]
    
    missing_files = []
    for file in required_files:
        if os.path.exists(file):
            print(f"   ✅ {file}")
        else:
            print(f"   ❌ {file} - MISSING")
            missing_files.append(file)
    
    return len(missing_files) == 0

def test_location_data():
    """Test location data loading"""
    print("\n📍 Testing Location Data...")
    
    try:
        df = pd.read_csv('merged_village_temperature_data.csv')
        districts = df['District Name'].nunique()
        talukas = df['Taluka Name'].nunique()
        
        print(f"   ✅ Loaded {len(df)} locations")
        print(f"   ✅ {districts} districts, {talukas} talukas")
        return True
    except Exception as e:
        print(f"   ❌ Error loading location data: {e}")
        return False

def test_imports():
    """Test that all core modules import correctly"""
    print("\n🔧 Testing Module Imports...")
    
    modules = [
        ('app', 'Flask web application'),
        ('bot_host', 'Telegram bot'),
        ('shared_data', 'Alert system'),
        ('weather_api', 'Weather data'),
        ('nasa_fire_fetcher', 'Fire data')
    ]
    
    failed_imports = []
    for module, description in modules:
        try:
            __import__(module)
            print(f"   ✅ {module} - {description}")
        except Exception as e:
            print(f"   ❌ {module} - {description}: {e}")
            failed_imports.append(module)
    
    return len(failed_imports) == 0

def test_flask_app():
    """Test Flask app functionality"""
    print("\n🌐 Testing Flask App...")
    
    try:
        import app
        flask_app = app.app
        
        with flask_app.test_client() as client:
            # Test home route
            response = client.get('/')
            if response.status_code == 200:
                print("   ✅ Home route working")
            else:
                print(f"   ❌ Home route failed: {response.status_code}")
                return False
            
            # Test API routes
            response = client.get('/api/weather_map_data')
            if response.status_code == 200:
                print("   ✅ Weather API endpoint working")
            else:
                print(f"   ⚠️ Weather API endpoint: {response.status_code}")
            
            response = client.get('/api/fire_data')
            if response.status_code == 200:
                print("   ✅ Fire data API endpoint working")
            else:
                print(f"   ⚠️ Fire data API endpoint: {response.status_code}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Flask app test error: {e}")
        return False

def test_subscriber_system():
    """Test subscriber system functionality"""
    print("\n👥 Testing Subscriber System...")
    
    try:
        from shared_data import add_subscriber, get_user_subscription, remove_subscriber
        
        # Test add subscriber
        test_user_id = 999999
        result = add_subscriber(test_user_id, "AHMADABAD", "Bavla")
        if result:
            print("   ✅ Add subscriber works")
        else:
            print("   ❌ Add subscriber failed")
            return False
        
        # Test get subscription
        subscription = get_user_subscription(test_user_id)
        if subscription and subscription['district'] == "AHMADABAD":
            print("   ✅ Get subscription works")
        else:
            print("   ❌ Get subscription failed")
            return False
        
        # Test remove subscriber
        result = remove_subscriber(test_user_id)
        if result:
            print("   ✅ Remove subscriber works")
        else:
            print("   ❌ Remove subscriber failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"   ❌ Subscriber system error: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Gujarat Weather & Fire Alert System - Verification")
    print("=" * 60)
    print(f"🕐 Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    tests = [
        ("Data Files", test_data_files),
        ("Location Data", test_location_data),
        ("Module Imports", test_imports),
        ("Flask App", test_flask_app),
        ("Subscriber System", test_subscriber_system)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")
    
    print("\n" + "=" * 60)
    print(f"🎯 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED - System is ready!")
        print("\n🚀 Ready to deploy:")
        print("   • Web App: python app.py")
        print("   • Bot: python bot_host.py")
        print("   • Combined: python main.py")
        print("\n🌐 Access:")
        print("   • Web Dashboard: http://localhost:5000")
        print("   • Telegram Bot: https://t.me/VillaegWarningbot")
    else:
        print("⚠️ Some tests failed - check the errors above")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)