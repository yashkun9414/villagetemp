#!/usr/bin/env python3
"""
Start Flask App and Test Admin Pages
"""

import os
import sys
import time
from datetime import datetime

def test_subscriber_system():
    """Test the subscriber system"""
    print("👥 Testing Subscriber System")
    print("=" * 40)
    
    try:
        from shared_data import load_subscribers, get_subscribers_for_area, add_subscriber
        
        # Load current subscribers
        subscribers = load_subscribers()
        print(f"📊 Current subscribers: {subscribers}")
        
        total_subs = sum(len(users) for users in subscribers.values())
        print(f"📈 Total subscribers: {total_subs}")
        
        # Test specific areas
        test_areas = [
            ("AHMADABAD", "Bavla"),
            ("RAJKOT", "Gondal"),
            ("SURAT", "Bardoli")
        ]
        
        for district, taluka in test_areas:
            subs = get_subscribers_for_area(district, taluka)
            print(f"📍 {district} → {taluka}: {len(subs)} subscribers")
            if subs:
                print(f"   User IDs: {subs}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing subscriber system: {e}")
        return False

def test_alert_system():
    """Test the alert system"""
    print("\n📨 Testing Alert System")
    print("=" * 40)
    
    try:
        from shared_data import queue_alert, get_pending_alerts
        
        # Queue a test alert
        test_message = f"🧪 System test alert - {datetime.now().strftime('%H:%M:%S')}"
        
        if queue_alert("AHMADABAD", "Bavla", test_message, "system_test"):
            print("✅ Alert queued successfully")
        else:
            print("❌ Failed to queue alert")
            return False
        
        # Check pending alerts
        pending = get_pending_alerts()
        print(f"⏳ Pending alerts: {len(pending)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing alert system: {e}")
        return False

def check_required_files():
    """Check if all required files exist"""
    print("📁 Checking Required Files")
    print("=" * 40)
    
    required_files = [
        'app.py',
        'shared_data.py',
        'templates/base.html',
        'templates/dashboard_simple.html',
        'templates/demo_alerts.html',
        'templates/send_alert.html',
        'templates/subscribers.html',
        'templates/login.html',
        'merged_village_temperature_data.csv'
    ]
    
    all_exist = True
    
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - MISSING!")
            all_exist = False
    
    return all_exist

def start_flask_app():
    """Start the Flask application"""
    print("\n🚀 Starting Flask Application")
    print("=" * 40)
    
    try:
        from app import app
        
        print("📱 Flask app imported successfully")
        print("🌐 Starting server on http://localhost:5000")
        print()
        print("📋 Available Admin Pages:")
        print("   🏠 Dashboard:     http://localhost:5000/dashboard")
        print("   📨 Send Alert:    http://localhost:5000/send_alert")
        print("   🧪 Demo Alerts:   http://localhost:5000/demo_alerts")
        print("   👥 Subscribers:   http://localhost:5000/subscribers")
        print("   🔐 Login:         http://localhost:5000/login")
        print()
        print("🔑 Login Credentials:")
        print("   Email:    admin@weatheralert.com")
        print("   Password: admin123")
        print()
        print("⚠️ Press Ctrl+C to stop the server")
        print("=" * 40)
        
        # Start the Flask app
        app.run(debug=True, host='0.0.0.0', port=5000)
        
    except Exception as e:
        print(f"❌ Error starting Flask app: {e}")
        return False

def main():
    """Main function"""
    print("🧪 Gujarat Weather Alert System - Admin Test")
    print("=" * 60)
    print(f"🕐 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Check files
    if not check_required_files():
        print("\n❌ Missing required files! Please check the file structure.")
        return
    
    # Test subscriber system
    if not test_subscriber_system():
        print("\n❌ Subscriber system test failed!")
        return
    
    # Test alert system
    if not test_alert_system():
        print("\n❌ Alert system test failed!")
        return
    
    print("\n✅ All systems working correctly!")
    print("\n🚀 Starting Flask application...")
    
    # Start Flask app
    start_flask_app()

if __name__ == "__main__":
    main()