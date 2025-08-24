#!/usr/bin/env python3
"""
Test Railway deployment compatibility
"""

import os
import sys
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_railway_deployment():
    """Test Railway deployment compatibility"""
    print("🚂 Testing Railway Deployment Compatibility")
    print("=" * 60)
    
    all_tests_passed = True
    
    try:
        # Test 1: Environment Variables
        print("1️⃣ Testing Environment Variables...")
        
        # Simulate Railway environment
        os.environ['PORT'] = '8080'  # Railway typically uses 8080
        
        required_vars = ['SECRET_KEY', 'ADMIN_EMAIL', 'ADMIN_PASSWORD']
        for var in required_vars:
            if os.getenv(var):
                print(f"   ✅ {var}: configured")
            else:
                print(f"   ⚠️ {var}: not set (should be configured in Railway)")
        
        # Test 2: App Startup
        print("\n2️⃣ Testing App Startup...")
        try:
            from app import app
            print("   ✅ Flask app imports successfully")
            
            # Test with Railway-like environment
            with app.test_client() as client:
                # Test health endpoint
                response = client.get('/health')
                if response.status_code == 200:
                    health_data = response.get_json()
                    print(f"   ✅ Health endpoint: {health_data['status']}")
                    
                    # Check test results
                    tests = health_data.get('tests', {})
                    for test_name, result in tests.items():
                        if result:
                            print(f"   ✅ {test_name}")
                        else:
                            print(f"   ⚠️ {test_name}: failed")
                else:
                    print(f"   ❌ Health endpoint failed: {response.status_code}")
                    all_tests_passed = False
                
                # Test debug endpoint
                response = client.get('/debug')
                if response.status_code == 200:
                    debug_data = response.get_json()
                    print("   ✅ Debug endpoint working")
                    
                    # Check file system
                    fs_checks = debug_data.get('file_system', {})
                    critical_files = ['templates_exists', 'static_exists', 'shared_data_exists']
                    for check in critical_files:
                        if fs_checks.get(check):
                            print(f"   ✅ {check}")
                        else:
                            print(f"   ❌ {check}: missing")
                            all_tests_passed = False
                else:
                    print(f"   ❌ Debug endpoint failed: {response.status_code}")
        
        except Exception as e:
            print(f"   ❌ App startup failed: {e}")
            all_tests_passed = False
        
        # Test 3: WSGI Compatibility
        print("\n3️⃣ Testing WSGI Compatibility...")
        try:
            from wsgi import application
            print("   ✅ WSGI application loads")
            
            # Test WSGI app directly
            from werkzeug.test import Client
            from werkzeug.wrappers import Response
            
            client = Client(application, Response)
            response = client.get('/health')
            if response.status_code == 200:
                print("   ✅ WSGI app responds to requests")
            else:
                print(f"   ❌ WSGI app failed: {response.status_code}")
                all_tests_passed = False
                
        except Exception as e:
            print(f"   ❌ WSGI compatibility failed: {e}")
            all_tests_passed = False
        
        # Test 4: Error Handling
        print("\n4️⃣ Testing Error Handling...")
        try:
            with app.test_client() as client:
                # Test 404 handling
                response = client.get('/nonexistent-page')
                if response.status_code == 404:
                    print("   ✅ 404 error handling works")
                else:
                    print(f"   ⚠️ 404 handling: {response.status_code}")
                
                # Test index route (should not crash)
                response = client.get('/')
                if response.status_code in [200, 302]:
                    print("   ✅ Index route handles requests")
                else:
                    print(f"   ❌ Index route failed: {response.status_code}")
                    all_tests_passed = False
                
                # Test login route
                response = client.get('/login')
                if response.status_code == 200:
                    print("   ✅ Login route works")
                else:
                    print(f"   ❌ Login route failed: {response.status_code}")
                    all_tests_passed = False
                    
        except Exception as e:
            print(f"   ❌ Error handling test failed: {e}")
            all_tests_passed = False
        
        # Test 5: Production Configuration
        print("\n5️⃣ Testing Production Configuration...")
        
        # Check Procfile
        if os.path.exists('Procfile'):
            with open('Procfile', 'r') as f:
                procfile = f.read().strip()
            if 'gunicorn' in procfile and 'wsgi:application' in procfile:
                print("   ✅ Procfile configured for Railway")
            else:
                print(f"   ❌ Procfile issue: {procfile}")
                all_tests_passed = False
        else:
            print("   ❌ Procfile missing")
            all_tests_passed = False
        
        # Check requirements.txt
        if os.path.exists('requirements.txt'):
            with open('requirements.txt', 'r') as f:
                requirements = f.read()
            required_packages = ['flask', 'gunicorn', 'pandas']
            missing_packages = []
            for package in required_packages:
                if package not in requirements.lower():
                    missing_packages.append(package)
            
            if not missing_packages:
                print("   ✅ All required packages in requirements.txt")
            else:
                print(f"   ❌ Missing packages: {missing_packages}")
                all_tests_passed = False
        else:
            print("   ❌ requirements.txt missing")
            all_tests_passed = False
        
        print("\n" + "=" * 60)
        
        if all_tests_passed:
            print("✅ RAILWAY DEPLOYMENT READY!")
            print("\n🚂 Railway Deployment Instructions:")
            print("1. Connect your GitHub repository to Railway")
            print("2. Set environment variables in Railway dashboard:")
            print("   - SECRET_KEY=your-secret-key")
            print("   - ADMIN_EMAIL=admin@weatheralert.com")
            print("   - ADMIN_PASSWORD=your-admin-password")
            print("3. Railway will automatically use the Procfile")
            print("4. Health check endpoint: /health")
            print("5. Debug endpoint: /debug (remove in production)")
            print("\n🔗 Expected URLs:")
            print("   - Main site: https://your-app.up.railway.app/")
            print("   - Health check: https://your-app.up.railway.app/health")
            print("   - Admin login: https://your-app.up.railway.app/login")
        else:
            print("❌ RAILWAY DEPLOYMENT ISSUES FOUND")
            print("Please fix the issues above before deploying to Railway")
        
        return all_tests_passed
        
    except Exception as e:
        print(f"\n❌ Railway deployment test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_railway_deployment()
    sys.exit(0 if success else 1)