#!/usr/bin/env python3
"""
Monitor subscription system and ensure users are being added properly
"""

import json
import os
import time
from datetime import datetime, timedelta
from shared_data import (
    load_subscribers, get_subscription_stats, validate_and_clean_subscribers
)

def monitor_subscriptions():
    """Monitor subscription activity and health"""
    print(f"🔍 Subscription Monitor - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    try:
        # Get current statistics
        stats = get_subscription_stats()
        
        print(f"📊 Current Status:")
        print(f"   • Total Subscribers: {stats['total_subscribers']}")
        print(f"   • Active Areas: {stats['active_areas']}")
        
        # Check file health
        subscribers_file = 'subscribers.json'
        if os.path.exists(subscribers_file):
            file_size = os.path.getsize(subscribers_file)
            file_modified = datetime.fromtimestamp(os.path.getmtime(subscribers_file))
            
            print(f"\n📁 File Health:")
            print(f"   • File Size: {file_size} bytes")
            print(f"   • Last Modified: {file_modified.strftime('%Y-%m-%d %H:%M:%S')}")
            
            # Check if file was modified recently (within last hour)
            if datetime.now() - file_modified < timedelta(hours=1):
                print(f"   • Recent Activity: ✅ (Modified within last hour)")
            else:
                print(f"   • Recent Activity: ⚠️ (No recent modifications)")
        else:
            print(f"\n📁 File Health: ❌ subscribers.json not found!")
            return
        
        # Load and validate data
        subscribers = load_subscribers()
        
        print(f"\n📋 Subscription Details:")
        if subscribers:
            for area, users in subscribers.items():
                if users:  # Only show areas with subscribers
                    district, taluka = area.split('_', 1)
                    print(f"   • {district}/{taluka}: {len(users)} subscribers")
                    
                    # Show user IDs (first 3 for privacy)
                    user_preview = users[:3]
                    if len(users) > 3:
                        user_preview_str = f"{user_preview}... (+{len(users)-3} more)"
                    else:
                        user_preview_str = str(user_preview)
                    print(f"     Users: {user_preview_str}")
        else:
            print(f"   • No active subscriptions found")
        
        # Check for potential issues
        print(f"\n🔍 Health Checks:")
        
        issues = []
        
        # Check for empty areas
        empty_areas = [k for k, v in subscribers.items() if not v]
        if empty_areas:
            issues.append(f"Empty areas: {len(empty_areas)}")
            print(f"   • Empty Areas: ⚠️ {len(empty_areas)} areas with no subscribers")
        else:
            print(f"   • Empty Areas: ✅ No empty areas")
        
        # Check for duplicate users
        all_users = []
        for users in subscribers.values():
            all_users.extend(users)
        
        unique_users = set(all_users)
        if len(all_users) != len(unique_users):
            duplicates = len(all_users) - len(unique_users)
            issues.append(f"Duplicate users: {duplicates}")
            print(f"   • Duplicate Users: ⚠️ {duplicates} duplicate entries found")
        else:
            print(f"   • Duplicate Users: ✅ No duplicates")
        
        # Check file integrity
        try:
            with open(subscribers_file, 'r') as f:
                json.load(f)
            print(f"   • File Integrity: ✅ Valid JSON")
        except json.JSONDecodeError as e:
            issues.append(f"Corrupted JSON: {str(e)}")
            print(f"   • File Integrity: ❌ JSON Error: {e}")
        except Exception as e:
            issues.append(f"File error: {str(e)}")
            print(f"   • File Integrity: ❌ Error: {e}")
        
        # Auto-fix issues if found
        if issues:
            print(f"\n🔧 Auto-fixing Issues:")
            try:
                cleaned_subscribers = validate_and_clean_subscribers()
                print(f"   • Data cleaned and validated ✅")
                
                # Get new stats
                new_stats = get_subscription_stats()
                print(f"   • New subscriber count: {new_stats['total_subscribers']}")
                print(f"   • New active areas: {new_stats['active_areas']}")
                
            except Exception as e:
                print(f"   • Auto-fix failed: ❌ {e}")
        else:
            print(f"   • System Health: ✅ All checks passed!")
        
        # Show growth metrics if we have historical data
        print(f"\n📈 Growth Metrics:")
        if stats['total_subscribers'] > 0:
            print(f"   • Current Growth: {stats['total_subscribers']} total subscribers")
            print(f"   • Area Coverage: {stats['active_areas']} districts/talukas")
            
            # Calculate average subscribers per area
            if stats['active_areas'] > 0:
                avg_per_area = stats['total_subscribers'] / stats['active_areas']
                print(f"   • Average per Area: {avg_per_area:.1f} subscribers")
        else:
            print(f"   • No subscribers yet - system ready for first users")
        
        print(f"\n" + "=" * 70)
        print(f"✅ Monitoring completed at {datetime.now().strftime('%H:%M:%S')}")
        
        return {
            'status': 'healthy' if not issues else 'issues_found',
            'total_subscribers': stats['total_subscribers'],
            'active_areas': stats['active_areas'],
            'issues': issues
        }
        
    except Exception as e:
        print(f"❌ Monitoring error: {e}")
        return {
            'status': 'error',
            'error': str(e)
        }

def continuous_monitor(interval_minutes=10):
    """Run continuous monitoring"""
    print(f"🚀 Starting continuous subscription monitoring (every {interval_minutes} minutes)")
    print(f"Press Ctrl+C to stop")
    
    try:
        while True:
            result = monitor_subscriptions()
            
            if result['status'] == 'error':
                print(f"⚠️ Error detected - will retry in {interval_minutes} minutes")
            elif result['status'] == 'issues_found':
                print(f"⚠️ Issues found and fixed - monitoring continues")
            else:
                print(f"✅ System healthy - next check in {interval_minutes} minutes")
            
            print(f"\n💤 Sleeping for {interval_minutes} minutes...")
            time.sleep(interval_minutes * 60)
            
    except KeyboardInterrupt:
        print(f"\n🛑 Monitoring stopped by user")
    except Exception as e:
        print(f"\n❌ Monitoring error: {e}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--continuous":
        continuous_monitor()
    else:
        monitor_subscriptions()