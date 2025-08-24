#!/usr/bin/env python3
"""
Test deployment readiness for Gujarat Weather Alert System
"""

import os
import sys
import logging
import json

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_deployment_readiness():
    """Test if the system is ready for deployment"""
    print("🚀 Testing Deployment Readiness")
    print("=" * 60)
    
    all_tests_passed = True
    
    try:
        # Test 1: Flask App Health Check
        print("1️⃣ Testing Flask App Health Check...")
        from app import app
        
        with app.test_client() as client:
            # Test health endpoint
            response = client.get('/health')
            if response.status_code == 200:
                health_data = response.get_json()
                print(f"   ✅ Health endpoint: {health_data['status']}")
            else:
                print(f"   ❌ Health endpoint failed: {response.status_code}")
                all_tests_passed = False
            
            # Test index endpoint
            response = client.get('/')
            if response.status_code == 200:
                print("   ✅ Index endpoint working")
            else:
                print(f"   ❌ Index endpoint failed: {response.status_code}")
                all_tests_passed = False
        
        # Test 2: Template Rendering
        print("\n2️⃣ Testing Template Rendering...")
        try:
            with app.test_client() as client:
                # Test login page (should not require auth)
                response = client.get('/login')
                if response.status_code == 200:
                    print("   ✅ Login template renders correctly")
                else:
                    print(f"   ❌ Login template error: {response.status_code}")
                    all_tests_passed = False
        except Exception as e:
            print(f"   ❌ Template rendering error: {e}")
            all_tests_passed = False
        
        # Test 3: WSGI Application
        print("\n3️⃣ Testing WSGI Application...")
        try:
            from wsgi import application
            print("   ✅ WSGI application loads successfully")
        except Exception as e:
            print(f"   ❌ WSGI application error: {e}")
            all_tests_passed = False
        
        # Test 4: Required Files
        print("\n4️⃣ Testing Required Files...")
        required_files = [
            'app.py',
            'wsgi.py',
            'shared_data.py',
            'translations.py',
            'requirements.txt',
            'Procfile',
            'templates/base.html',
            'templates/index.html',
            'templates/login.html'
        ]
        
        for file_path in required_files:
            if os.path.exists(file_path):
                print(f"   ✅ {file_path}")
            else:
                print(f"   ❌ Missing: {file_path}")
                all_tests_passed = False
        
        # Test 5: Environment Variables
        print("\n5️⃣ Testing Environment Variables...")
        env_vars = {
            'SECRET_KEY': 'Flask secret key',
            'ADMIN_EMAIL': 'Admin email',
            'ADMIN_PASSWORD': 'Admin password'
        }
        
        for var, description in env_vars.items():
            value = os.getenv(var)
            if value:
                print(f"   ✅ {var}: configured")
            else:
                print(f"   ⚠️ {var}: not set ({description})")
                # Don't fail for missing env vars as they might be set in deployment
        
        # Test 6: Dependencies
        print("\n6️⃣ Testing Dependencies...")
        try:
            import flask
            import pandas
            import requests
            print("   ✅ Core dependencies available")
            
            # Gunicorn is only needed in production
            try:
                import gunicorn
                print("   ✅ Gunicorn available")
            except ImportError:
                print("   ⚠️ Gunicorn not installed locally (will be installed in production)")
                
        except ImportError as e:
            print(f"   ❌ Missing core dependency: {e}")
            all_tests_passed = False
        
        # Test 7: Data Files
        print("\n7️⃣ Testing Data Files...")
        data_files = [
            'merged_village_temperature_data.csv',
            'static/gujarat_fire_history.csv'
        ]
        
        for data_file in data_files:
            if os.path.exists(data_file):
                print(f"   ✅ {data_file}")
            else:
                print(f"   ⚠️ {data_file}: not found (may be loaded from alternative location)")
        
        # Test 8: Subscription System
        print("\n8️⃣ Testing Subscription System...")
        try:
            from shared_data import load_subscribers, get_subscription_stats
            stats = get_subscription_stats()
            print(f"   ✅ Subscription system: {stats['total_subscribers']} subscribers")
        except Exception as e:
            print(f"   ❌ Subscription system error: {e}")
            all_tests_passed = False
        
        # Test 9: Bot Integration
        print("\n9️⃣ Testing Bot Integration...")
        try:
            from shared_data import queue_alert, get_pending_alerts
            # Test alert queueing (don't actually send)
            test_result = queue_alert("TEST", "TEST", "Test message", "test")
            if test_result:
                print("   ✅ Alert queueing system working")
                # Clean up test alert
                try:
                    alerts = get_pending_alerts()
                    # Remove test alerts
                    import json
                    if os.path.exists('pending_alerts.json'):
                        with open('pending_alerts.json', 'r') as f:
                            all_alerts = json.load(f)
                        # Filter out test alerts
                        filtered_alerts = [a for a in all_alerts if a.get('type') != 'test']
                        with open('pending_alerts.json', 'w') as f:
                            json.dump(filtered_alerts, f, indent=2)
                except:
                    pass
            else:
                print("   ❌ Alert queueing system failed")
                all_tests_passed = False
        except Exception as e:
            print(f"   ❌ Bot integration error: {e}")
            all_tests_passed = False
        
        # Test 10: Production Configuration
        print("\n🔟 Testing Production Configuration...")
        
        # Check Procfile
        if os.path.exists('Procfile'):
            with open('Procfile', 'r') as f:
                procfile_content = f.read().strip()
            if 'gunicorn' in procfile_content and 'wsgi:application' in procfile_content:
                print("   ✅ Procfile configured for production")
            else:
                print(f"   ⚠️ Procfile content: {procfile_content}")
        else:
            print("   ❌ Procfile missing")
            all_tests_passed = False
        
        # Check requirements.txt
        if os.path.exists('requirements.txt'):
            with open('requirements.txt', 'r') as f:
                requirements = f.read()
            if 'gunicorn' in requirements and 'flask' in requirements:
                print("   ✅ Requirements.txt includes production dependencies")
            else:
                print("   ⚠️ Requirements.txt may be missing production dependencies")
        
        print("\n" + "=" * 60)
        
        if all_tests_passed:
            print("✅ ALL TESTS PASSED - DEPLOYMENT READY!")
            print("\n🚀 Deployment Instructions:")
            print("1. Ensure environment variables are set in deployment platform")
            print("2. Use the /health endpoint for healthchecks")
            print("3. The app will run on the PORT environment variable")
            print("4. Gunicorn will serve the app via wsgi:application")
            print("\n📋 Healthcheck Configuration:")
            print("   Path: /health")
            print("   Expected: 200 status with JSON response")
            print("   Timeout: 120 seconds (configured in Procfile)")
        else:
            print("❌ SOME TESTS FAILED - REVIEW ISSUES BEFORE DEPLOYMENT")
        
        return all_tests_passed
        
    except Exception as e:
        print(f"\n❌ Deployment readiness test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_deployment_readiness()
    sys.exit(0 if success else 1)