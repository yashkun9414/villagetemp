#!/usr/bin/env python3
"""
Complete Alert System Test
Tests all aspects of the alert system
"""

import os
import sys
import time
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_complete_system():
    """Test the complete alert system"""
    print("🧪 Complete Alert System Test")
    print("=" * 60)
    print(f"🕐 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Test 1: Check subscribers
    print("📋 Test 1: Checking Subscribers")
    print("-" * 30)
    
    try:
        from shared_data import load_subscribers, get_subscribers_for_area
        
        subscribers = load_subscribers()
        total_subscribers = sum(len(users) for users in subscribers.values())
        
        print(f"👥 Total subscribers: {total_subscribers}")
        
        # Check AHMADABAD Bavla specifically
        bavla_subscribers = get_subscribers_for_area("AHMADABAD", "Bavla")
        print(f"📍 AHMADABAD → Bavla subscribers: {len(bavla_subscribers)}")
        
        if bavla_subscribers:
            print(f"   User IDs: {bavla_subscribers}")
            print("✅ Test 1 PASSED: Subscribers found")
        else:
            print("❌ Test 1 FAILED: No subscribers found")
            return False
            
    except Exception as e:
        print(f"❌ Test 1 ERROR: {e}")
        return False
    
    print()
    
    # Test 2: Queue Alert
    print("📋 Test 2: Queuing Alert")
    print("-" * 30)
    
    try:
        from shared_data import queue_alert
        
        test_message = f"🧪 COMPLETE TEST ALERT - {datetime.now().strftime('%H:%M:%S')}"
        
        if queue_alert("AHMADABAD", "Bavla", test_message, "complete_test"):
            print("✅ Test 2 PASSED: Alert queued successfully")
        else:
            print("❌ Test 2 FAILED: Failed to queue alert")
            return False
            
    except Exception as e:
        print(f"❌ Test 2 ERROR: {e}")
        return False
    
    print()
    
    # Test 3: Direct Telegram Send
    print("📋 Test 3: Direct Telegram Send")
    print("-" * 30)
    
    try:
        from shared_data import send_alert_to_subscribers
        
        bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        if not bot_token:
            print("❌ Test 3 FAILED: No bot token found")
            return False
        
        test_message = f"🧪 DIRECT SEND TEST - {datetime.now().strftime('%H:%M:%S')}"
        sent_count = send_alert_to_subscribers("AHMADABAD", "Bavla", test_message, bot_token)
        
        if sent_count > 0:
            print(f"✅ Test 3 PASSED: Alert sent to {sent_count} subscribers")
        else:
            print("❌ Test 3 FAILED: No alerts sent")
            return False
            
    except Exception as e:
        print(f"❌ Test 3 ERROR: {e}")
        return False
    
    print()
    
    # Test 4: Check Alert Queue
    print("📋 Test 4: Checking Alert Queue")
    print("-" * 30)
    
    try:
        from shared_data import get_pending_alerts
        
        pending = get_pending_alerts()
        print(f"⏳ Pending alerts: {len(pending)}")
        
        # Show recent alerts for AHMADABAD Bavla
        bavla_alerts = [a for a in pending if a['district'] == 'AHMADABAD' and a['taluka'] == 'Bavla']
        print(f"📍 AHMADABAD → Bavla pending: {len(bavla_alerts)}")
        
        if bavla_alerts:
            print("   Recent alerts:")
            for alert in bavla_alerts[-2:]:  # Show last 2
                print(f"   - {alert['type']}: {alert['message'][:40]}...")
        
        print("✅ Test 4 PASSED: Queue checked successfully")
        
    except Exception as e:
        print(f"❌ Test 4 ERROR: {e}")
        return False
    
    print()
    
    # Test 5: Bot Token Validation
    print("📋 Test 5: Bot Token Validation")
    print("-" * 30)
    
    try:
        import requests
        
        bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        url = f"https://api.telegram.org/bot{bot_token}/getMe"
        
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            bot_info = response.json()
            if bot_info.get('ok'):
                bot_username = bot_info['result']['username']
                print(f"🤖 Bot username: @{bot_username}")
                print("✅ Test 5 PASSED: Bot token is valid")
            else:
                print("❌ Test 5 FAILED: Bot token invalid")
                return False
        else:
            print(f"❌ Test 5 FAILED: API returned {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Test 5 ERROR: {e}")
        return False
    
    print()
    
    # Summary
    print("🎯 Test Summary")
    print("=" * 60)
    print("✅ All tests PASSED!")
    print()
    print("📊 Results:")
    print(f"   👥 Subscribers: {len(bavla_subscribers)} in AHMADABAD → Bavla")
    print(f"   📨 Alerts queued: ✅")
    print(f"   📤 Direct send: ✅ ({sent_count} delivered)")
    print(f"   🤖 Bot status: ✅ (@{bot_username})")
    print()
    print("💡 What to check:")
    print("   1. Check your Telegram for the test messages")
    print("   2. You should have received 2 alerts:")
    print("      - One from direct send (immediate)")
    print("      - One from queue (when bot processes it)")
    print()
    print("🚀 Alert system is working correctly!")
    
    return True

def main():
    """Main function"""
    success = test_complete_system()
    
    if success:
        print("\n🎉 SUCCESS: Alert system is fully operational!")
        print("💬 Please confirm if you received the test alerts on Telegram")
    else:
        print("\n❌ FAILURE: Alert system has issues")
        print("🔧 Check the error messages above")

if __name__ == "__main__":
    main()