#!/usr/bin/env python3
"""
Check Alert Queue - View pending and sent alerts
"""

import json
import os
from datetime import datetime

def check_alert_queue():
    """Check the current alert queue"""
    try:
        from shared_data import get_pending_alerts
        
        print(f"📨 Alert Queue Status")
        print(f"=" * 40)
        print(f"🕐 Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Check pending alerts
        pending = get_pending_alerts()
        print(f"⏳ Pending Alerts: {len(pending)}")
        
        if pending:
            for i, alert in enumerate(pending, 1):
                print(f"   {i}. {alert['district']} → {alert['taluka']}")
                print(f"      Type: {alert['type']}")
                print(f"      Time: {alert['timestamp']}")
                print(f"      Message: {alert['message'][:50]}...")
                print()
        
        # Check all alerts (including sent)
        if os.path.exists('pending_alerts.json'):
            with open('pending_alerts.json', 'r') as f:
                all_alerts = json.load(f)
            
            sent_alerts = [a for a in all_alerts if a.get('sent', False)]
            print(f"✅ Sent Alerts: {len(sent_alerts)}")
            
            if sent_alerts:
                print("   Recent sent alerts:")
                for alert in sent_alerts[-3:]:  # Show last 3
                    print(f"   - {alert['district']} → {alert['taluka']} ({alert.get('sent_at', 'Unknown time')})")
        
        print()
        print(f"📊 Total Alerts: {len(all_alerts) if 'all_alerts' in locals() else 0}")
        
    except Exception as e:
        print(f"❌ Error checking alert queue: {e}")

def clear_sent_alerts():
    """Clear sent alerts from queue"""
    try:
        if os.path.exists('pending_alerts.json'):
            with open('pending_alerts.json', 'r') as f:
                all_alerts = json.load(f)
            
            # Keep only pending alerts
            pending_alerts = [a for a in all_alerts if not a.get('sent', False)]
            
            with open('pending_alerts.json', 'w') as f:
                json.dump(pending_alerts, f, indent=2)
            
            print(f"✅ Cleared sent alerts. {len(pending_alerts)} pending alerts remain.")
        else:
            print("❌ No alert queue file found.")
            
    except Exception as e:
        print(f"❌ Error clearing sent alerts: {e}")

def main():
    """Main function"""
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'clear':
        clear_sent_alerts()
    else:
        check_alert_queue()
        print()
        print("💡 Commands:")
        print("   python check_alert_queue.py        - Check queue status")
        print("   python check_alert_queue.py clear  - Clear sent alerts")

if __name__ == "__main__":
    main()