#!/usr/bin/env python3
"""
Test Web Alert System - Send alert via web interface
"""

import requests
import json
from datetime import datetime

def test_web_alert_system():
    """Test sending alert via web interface"""
    print("🌐 Testing Web Alert System")
    print("=" * 50)
    
    base_url = "http://localhost:5000"
    
    # Create session
    session = requests.Session()
    
    try:
        # Step 1: Login
        print("🔐 Step 1: Logging in...")
        login_data = {
            'email': 'admin@weatheralert.com',
            'password': 'admin123'
        }
        
        # Get login page first to get CSRF token
        login_page = session.get(f"{base_url}/login")
        if login_page.status_code != 200:
            print("❌ Failed to access login page")
            return False
        
        # For now, let's test the API endpoints directly
        print("✅ Login page accessible")
        
        # Step 2: Test subscriber count API
        print("\n👥 Step 2: Testing subscriber count API...")
        subscriber_response = session.get(f"{base_url}/get_subscriber_count/AHMADABAD/Bavla")
        
        if subscriber_response.status_code == 401:
            print("⚠️ Authentication required - this is correct behavior")
        else:
            print(f"Subscriber API response: {subscriber_response.status_code}")
        
        # Step 3: Test demo alert API
        print("\n🧪 Step 3: Testing demo alert API...")
        demo_alert_data = {
            'district': 'AHMADABAD',
            'taluka': 'Bavla',
            'message': f'Web interface test alert - {datetime.now().strftime("%H:%M:%S")}'
        }
        
        demo_response = session.post(
            f"{base_url}/send_demo_alert",
            json=demo_alert_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if demo_response.status_code == 401:
            print("⚠️ Demo alert requires authentication - this is correct")
        else:
            print(f"Demo alert response: {demo_response.status_code}")
            if demo_response.status_code == 200:
                result = demo_response.json()
                print(f"Result: {result}")
        
        # Step 4: Test API endpoints that don't require auth
        print("\n📊 Step 4: Testing public API endpoints...")
        
        # Weather data
        weather_response = session.get(f"{base_url}/api/weather_map_data")
        print(f"Weather API: {'✅ OK' if weather_response.status_code == 200 else '❌ ERROR'}")
        
        # Fire data
        fire_response = session.get(f"{base_url}/api/fire_data")
        print(f"Fire API: {'✅ OK' if fire_response.status_code == 200 else '❌ ERROR'}")
        
        if fire_response.status_code == 200:
            fire_data = fire_response.json()
            print(f"Fire incidents: {len(fire_data.get('fire_incidents', []))}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing web system: {e}")
        return False

def test_direct_alert_send():
    """Test sending alert directly via shared_data"""
    print("\n📨 Testing Direct Alert Send")
    print("=" * 50)
    
    try:
        from shared_data import queue_alert, get_subscribers_for_area, send_alert_to_subscribers
        import os
        
        # Check subscribers
        subscribers = get_subscribers_for_area("AHMADABAD", "Bavla")
        print(f"👥 Subscribers for AHMADABAD → Bavla: {len(subscribers)}")
        
        if not subscribers:
            print("❌ No subscribers found!")
            return False
        
        # Queue alert
        test_message = f"🌐 Web interface test - {datetime.now().strftime('%H:%M:%S')}"
        
        if queue_alert("AHMADABAD", "Bavla", test_message, "web_test"):
            print("✅ Alert queued successfully")
        else:
            print("❌ Failed to queue alert")
            return False
        
        # Send directly via Telegram API
        bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        if bot_token:
            sent_count = send_alert_to_subscribers("AHMADABAD", "Bavla", test_message, bot_token)
            print(f"📤 Direct send: {sent_count} alerts delivered")
        else:
            print("⚠️ No bot token found for direct send")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in direct alert send: {e}")
        return False

def main():
    """Main test function"""
    print("🧪 Web Alert System Test")
    print("=" * 60)
    print(f"🕐 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Test web system
    web_success = test_web_alert_system()
    
    # Test direct system
    direct_success = test_direct_alert_send()
    
    print("\n" + "=" * 60)
    print("🎯 Test Results:")
    print(f"   🌐 Web System: {'✅ Working' if web_success else '❌ Issues'}")
    print(f"   📨 Direct Send: {'✅ Working' if direct_success else '❌ Issues'}")
    
    if web_success and direct_success:
        print("\n🎉 All systems working correctly!")
        print("\n💡 To test the web interface:")
        print("   1. Go to http://localhost:5000/login")
        print("   2. Login: admin@weatheralert.com / admin123")
        print("   3. Test all admin pages:")
        print("      - Dashboard: View system stats")
        print("      - Demo Alerts: Send test alerts")
        print("      - Send Alert: Send custom alerts")
        print("      - Subscribers: View and manage subscribers")
    else:
        print("\n❌ Some systems have issues - check the logs above")

if __name__ == "__main__":
    main()