#!/usr/bin/env python3
"""
Send demo alert to Ahmedabad Bavla subscribers
"""

import os
from dotenv import load_dotenv
from shared_data import queue_alert, get_subscribers_for_area
import requests
from datetime import datetime

load_dotenv()

def send_demo_alert_ahmedabad_bavla():
    """Send demo alert to Ahmedabad Bavla subscribers"""
    
    print("🚀 Sending Demo Alert to Ahmedabad → Bavla")
    print("=" * 50)
    
    # Configuration
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN', '8235992714:AAED7tTjm6waV6Ak-L-_LgRz37ZfnuEnE4w')
    district = "AHMEDABAD"
    taluka = "Bavla"
    
    # Demo message
    demo_message = """🌡️ HIGH TEMPERATURE ALERT

Temperature: 43°C expected in Bavla today!

⚠️ SAFETY MEASURES:
• Stay indoors during 11 AM - 4 PM
• Drink plenty of water
• Wear light colored clothes
• Avoid outdoor activities

🏥 Emergency: Call 108 if feeling unwell

This is a DEMO alert to test the system."""
    
    # Queue the alert instead of sending directly
    print("📝 Queuing demo alert...")
    if queue_alert(district, taluka, demo_message, "demo"):
        print("✅ Demo alert queued successfully!")
        print("\n📱 The alert will be sent when:")
        print("   1. Users interact with the bot (send any command)")
        print("   2. Or when the bot processes pending alerts")
        print("\n🧪 To test:")
        print("   1. Subscribe to AHMEDABAD → Bavla via bot")
        print("   2. Send /start or any command to the bot")
        print("   3. You should receive the demo alert!")
    else:
        print("❌ Failed to queue demo alert")
    
    # Also show current subscribers
    subscribers = get_subscribers_for_area(district, taluka)
    print(f"\n📊 Current subscribers for {district} → {taluka}: {len(subscribers)}")
    
    if not subscribers:
        print("⚠️ No subscribers found!")
        print("\nTo test the system:")
        print("1. Go to https://t.me/VillaegWarningbot")
        print("2. Send /subscribe")
        print("3. Choose AHMEDABAD → Bavla")
        print("4. Send /start to trigger alert processing")
    else:
        print(f"📱 Subscriber IDs: {subscribers}")
        print("✅ Alert queued and will be sent when users interact with bot")

if __name__ == "__main__":
    send_demo_alert_ahmedabad_bavla()