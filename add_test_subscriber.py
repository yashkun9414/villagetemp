#!/usr/bin/env python3
"""
Add Test Subscriber - For testing alert system
Usage: python add_test_subscriber.py <user_id> <district> <taluka>
"""

import sys
from datetime import datetime

def add_test_subscriber(user_id, district, taluka):
    """Add a test subscriber"""
    try:
        from shared_data import add_subscriber, get_subscribers_for_area
        
        print(f"👤 Adding Test Subscriber")
        print(f"=" * 40)
        print(f"🆔 User ID: {user_id}")
        print(f"📍 Location: {taluka}, {district}")
        print(f"🕐 Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Add subscriber
        if add_subscriber(user_id, district, taluka):
            print("✅ Subscriber added successfully!")
            
            # Verify
            subscribers = get_subscribers_for_area(district, taluka)
            print(f"📊 Total subscribers in {taluka}, {district}: {len(subscribers)}")
            print(f"👥 Subscriber list: {subscribers}")
            
            return True
        else:
            print("❌ Failed to add subscriber!")
            return False
            
    except Exception as e:
        print(f"❌ Error adding subscriber: {e}")
        return False

def show_current_subscribers():
    """Show current subscribers"""
    try:
        from shared_data import load_subscribers
        
        subscribers = load_subscribers()
        
        print(f"👥 Current Subscribers")
        print(f"=" * 40)
        
        if not subscribers:
            print("❌ No subscribers found!")
            return
        
        for key, users in subscribers.items():
            if users:
                district, taluka = key.split('_', 1)
                print(f"📍 {district} → {taluka}: {users}")
        
    except Exception as e:
        print(f"❌ Error loading subscribers: {e}")

def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("👤 Add Test Subscriber Tool")
        print("=" * 40)
        print()
        print("Usage:")
        print("  python add_test_subscriber.py <user_id> <district> <taluka>")
        print("  python add_test_subscriber.py list")
        print()
        print("Examples:")
        print("  python add_test_subscriber.py 123456789 AHMADABAD Bavla")
        print("  python add_test_subscriber.py 987654321 RAJKOT Gondal")
        print("  python add_test_subscriber.py list")
        print()
        return
    
    if sys.argv[1].lower() == 'list':
        show_current_subscribers()
        return
    
    if len(sys.argv) < 4:
        print("❌ Error: Please provide user_id, district, and taluka")
        print("Usage: python add_test_subscriber.py <user_id> <district> <taluka>")
        return
    
    user_id = sys.argv[1]
    district = sys.argv[2].upper()
    taluka = sys.argv[3]
    
    # Add subscriber
    success = add_test_subscriber(user_id, district, taluka)
    
    if success:
        print("\n🎉 Test subscriber added successfully!")
        print("💡 Now you can test sending alerts using:")
        print(f"   python test_alert_sender.py {district} {taluka} 'Test message'")
    else:
        print("\n❌ Failed to add test subscriber")

if __name__ == "__main__":
    main()