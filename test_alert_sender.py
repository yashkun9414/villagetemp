#!/usr/bin/env python3
"""
Command Line Alert Sender - Test Telegram Alert System
Usage: python test_alert_sender.py <district> <taluka> <message>
Example: python test_alert_sender.py AHMADABAD Bavla "Test alert message"
"""

import sys
import os
from datetime import datetime
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def send_test_alert(district, taluka, message):
    """Send a test alert to subscribers"""
    try:
        from shared_data import get_subscribers_for_area, queue_alert, send_alert_to_subscribers
        
        print(f"🧪 Testing Alert System")
        print(f"=" * 50)
        print(f"📍 Target: {taluka}, {district}")
        print(f"💬 Message: {message}")
        print(f"🕐 Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Check subscribers
        subscribers = get_subscribers_for_area(district, taluka)
        print(f"👥 Subscribers found: {len(subscribers)}")
        
        if not subscribers:
            print("❌ No subscribers found for this area!")
            print("💡 Ask users to subscribe using /subscribe command on @VillaegWarningbot")
            return False
        
        # Show subscriber IDs
        print(f"📱 Subscriber IDs: {subscribers}")
        print()
        
        # Get bot token
        bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        if not bot_token:
            print("❌ TELEGRAM_BOT_TOKEN not found in environment variables!")
            return False
        
        print(f"🤖 Bot token found: {bot_token[:10]}...")
        print()
        
        # Method 1: Queue alert (for bot to process)
        print("📨 Method 1: Queuing alert for bot processing...")
        if queue_alert(district, taluka, f"🧪 CMD TEST ALERT:\n\n{message}", "test"):
            print("✅ Alert queued successfully!")
        else:
            print("❌ Failed to queue alert!")
        
        print()
        
        # Method 2: Send directly via Telegram API
        print("📤 Method 2: Sending directly via Telegram API...")
        sent_count = send_alert_to_subscribers(district, taluka, f"🧪 DIRECT TEST ALERT:\n\n{message}", bot_token)
        
        if sent_count > 0:
            print(f"✅ Alert sent directly to {sent_count} subscribers!")
        else:
            print("❌ Failed to send alert directly!")
        
        print()
        print("=" * 50)
        print("🎯 Test Results:")
        print(f"   📊 Subscribers: {len(subscribers)}")
        print(f"   📨 Queued: {'✅' if queue_alert else '❌'}")
        print(f"   📤 Direct Send: {'✅' if sent_count > 0 else '❌'}")
        print()
        print("💡 Check your Telegram to see if you received the alerts!")
        
        return sent_count > 0
        
    except Exception as e:
        print(f"❌ Error sending test alert: {e}")
        logger.error(f"Error in send_test_alert: {e}")
        return False

def show_all_subscribers():
    """Show all current subscribers"""
    try:
        from shared_data import load_subscribers
        
        subscribers = load_subscribers()
        
        print(f"👥 All Subscribers")
        print(f"=" * 50)
        
        if not subscribers:
            print("❌ No subscribers found!")
            return
        
        total_users = 0
        for key, users in subscribers.items():
            if users:
                district, taluka = key.split('_', 1)
                print(f"📍 {district} → {taluka}: {len(users)} subscribers")
                print(f"   User IDs: {users}")
                total_users += len(users)
        
        print(f"\n📊 Total: {total_users} subscribers across {len([k for k, v in subscribers.items() if v])} areas")
        
    except Exception as e:
        print(f"❌ Error loading subscribers: {e}")

def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("🧪 Gujarat Weather Alert - Command Line Test Tool")
        print("=" * 60)
        print()
        print("Usage:")
        print("  python test_alert_sender.py <district> <taluka> <message>")
        print("  python test_alert_sender.py list")
        print()
        print("Examples:")
        print("  python test_alert_sender.py AHMADABAD Bavla 'Test alert from command line'")
        print("  python test_alert_sender.py RAJKOT Gondal 'Emergency weather alert test'")
        print("  python test_alert_sender.py list")
        print()
        print("Available Districts: AHMADABAD, RAJKOT, SURAT, BANASKANTHA, VALSAD, etc.")
        return
    
    if sys.argv[1].lower() == 'list':
        show_all_subscribers()
        return
    
    if len(sys.argv) < 4:
        print("❌ Error: Please provide district, taluka, and message")
        print("Usage: python test_alert_sender.py <district> <taluka> <message>")
        return
    
    district = sys.argv[1].upper()
    taluka = sys.argv[2]
    message = ' '.join(sys.argv[3:])
    
    # Send test alert
    success = send_test_alert(district, taluka, message)
    
    if success:
        print("🎉 Test completed successfully!")
    else:
        print("❌ Test failed - check the logs above")

if __name__ == "__main__":
    main()