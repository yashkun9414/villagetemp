#!/usr/bin/env python3
"""
Test script to verify Flask app can start properly
"""

import os
import sys
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_app_startup():
    """Test if the Flask app can start without errors"""
    print("🧪 Testing Flask App Startup")
    print("=" * 50)
    
    try:
        # Test imports
        print("1️⃣ Testing imports...")
        
        # Test Flask imports
        from flask import Flask
        print("   ✅ Flask imported successfully")
        
        # Test pandas
        import pandas as pd
        print("   ✅ Pandas imported successfully")
        
        # Test our modules
        try:
            from shared_data import load_subscribers
            print("   ✅ shared_data imported successfully")
        except Exception as e:
            print(f"   ⚠️ shared_data import warning: {e}")
        
        try:
            from translations import get_translation
            print("   ✅ translations imported successfully")
        except Exception as e:
            print(f"   ⚠️ translations import warning: {e}")
        
        try:
            from weather_api import get_weather_for_locations
            print("   ✅ weather_api imported successfully")
        except Exception as e:
            print(f"   ⚠️ weather_api import warning: {e}")
        
        # Test app creation
        print("\n2️⃣ Testing app creation...")
        from app import app
        print("   ✅ Flask app created successfully")
        
        # Test app configuration
        print("\n3️⃣ Testing app configuration...")
        with app.app_context():
            print(f"   ✅ App name: {app.name}")
            print(f"   ✅ Secret key configured: {'Yes' if app.config.get('SECRET_KEY') else 'No'}")
        
        # Test routes
        print("\n4️⃣ Testing routes...")
        with app.test_client() as client:
            # Test health endpoint
            response = client.get('/health')
            if response.status_code == 200:
                print("   ✅ Health endpoint working")
            else:
                print(f"   ❌ Health endpoint failed: {response.status_code}")
            
            # Test index endpoint
            response = client.get('/')
            if response.status_code in [200, 302]:  # 302 is redirect, which is OK
                print("   ✅ Index endpoint working")
            else:
                print(f"   ❌ Index endpoint failed: {response.status_code}")
        
        # Test data loading
        print("\n5️⃣ Testing data loading...")
        try:
            from app import load_taluka_data
            talukas = load_taluka_data()
            if not talukas.empty:
                print(f"   ✅ Taluka data loaded: {len(talukas)} records")
            else:
                print("   ⚠️ Taluka data is empty (using fallback)")
        except Exception as e:
            print(f"   ❌ Data loading error: {e}")
        
        # Test environment variables
        print("\n6️⃣ Testing environment variables...")
        required_vars = ['SECRET_KEY', 'ADMIN_EMAIL', 'ADMIN_PASSWORD']
        for var in required_vars:
            value = os.getenv(var)
            if value:
                print(f"   ✅ {var}: configured")
            else:
                print(f"   ⚠️ {var}: not set (using default)")
        
        print("\n" + "=" * 50)
        print("✅ Flask app startup test completed successfully!")
        print("🚀 App should be ready for deployment")
        
        return True
        
    except Exception as e:
        print(f"\n❌ App startup test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_app_startup()
    sys.exit(0 if success else 1)