#!/usr/bin/env python3
"""
Test script to verify the subscription system works properly
"""

import json
import os
from shared_data import (
    add_subscriber, remove_subscriber, get_user_subscription,
    get_subscribers_for_area, validate_and_clean_subscribers,
    get_subscription_stats, load_subscribers, save_subscribers
)

def test_subscription_system():
    """Test the subscription system thoroughly"""
    print("🧪 Testing Gujarat Weather Alert Subscription System")
    print("=" * 60)
    
    # Test 1: Add new subscribers
    print("\n1️⃣ Testing Add Subscribers:")
    test_users = [
        (12345, "AHMADABAD", "Bavla"),
        (67890, "AHMADABAD", "Bavla"),  # Same area
        (11111, "ANAND", "Anand"),      # Different area
        (22222, "SURAT", "Surat"),      # Another area
        (12345, "SURAT", "Bardoli"),    # User changing subscription
    ]
    
    for user_id, district, taluka in test_users:
        result = add_subscriber(user_id, district, taluka)
        print(f"   User {user_id} -> {district}/{taluka}: {'✅' if result else '❌'}")
    
    # Test 2: Check subscriptions
    print("\n2️⃣ Testing Get Subscriptions:")
    for user_id, _, _ in test_users:
        subscription = get_user_subscription(user_id)
        if subscription:
            print(f"   User {user_id}: {subscription['district']}/{subscription['taluka']} ✅")
        else:
            print(f"   User {user_id}: No subscription ❌")
    
    # Test 3: Get subscribers for areas
    print("\n3️⃣ Testing Get Subscribers by Area:")
    test_areas = [
        ("AHMADABAD", "Bavla"),
        ("ANAND", "Anand"),
        ("SURAT", "Surat"),
        ("SURAT", "Bardoli"),
    ]
    
    for district, taluka in test_areas:
        subscribers = get_subscribers_for_area(district, taluka)
        print(f"   {district}/{taluka}: {len(subscribers)} subscribers {subscribers}")
    
    # Test 4: Test data validation
    print("\n4️⃣ Testing Data Validation:")
    cleaned_data = validate_and_clean_subscribers()
    print(f"   Data cleaned successfully: {len(cleaned_data)} areas")
    
    # Test 5: Get statistics
    print("\n5️⃣ Testing Statistics:")
    stats = get_subscription_stats()
    print(f"   Total subscribers: {stats['total_subscribers']}")
    print(f"   Active areas: {stats['active_areas']}")
    
    # Test 6: Test file operations
    print("\n6️⃣ Testing File Operations:")
    try:
        # Load current data
        current_data = load_subscribers()
        print(f"   Load subscribers: ✅ ({len(current_data)} areas)")
        
        # Save data
        save_result = save_subscribers(current_data)
        print(f"   Save subscribers: {'✅' if save_result else '❌'}")
        
        # Check file exists and is valid JSON
        if os.path.exists('subscribers.json'):
            with open('subscribers.json', 'r') as f:
                json.load(f)
            print(f"   File integrity: ✅")
        else:
            print(f"   File integrity: ❌")
            
    except Exception as e:
        print(f"   File operations: ❌ {e}")
    
    # Test 7: Test edge cases
    print("\n7️⃣ Testing Edge Cases:")
    
    # Invalid user ID
    result = add_subscriber(None, "AHMADABAD", "Bavla")
    print(f"   Invalid user ID: {'✅' if not result else '❌'}")
    
    # Empty district
    result = add_subscriber(99999, "", "Bavla")
    print(f"   Empty district: {'✅' if not result else '❌'}")
    
    # Empty taluka
    result = add_subscriber(99999, "AHMADABAD", "")
    print(f"   Empty taluka: {'✅' if not result else '❌'}")
    
    # Test 8: Test unsubscribe
    print("\n8️⃣ Testing Unsubscribe:")
    result = remove_subscriber(12345)
    print(f"   Remove user 12345: {'✅' if result else '❌'}")
    
    # Check if user is really removed
    subscription = get_user_subscription(12345)
    print(f"   User 12345 removed: {'✅' if not subscription else '❌'}")
    
    # Final statistics
    print("\n📊 Final Statistics:")
    final_stats = get_subscription_stats()
    print(f"   Total subscribers: {final_stats['total_subscribers']}")
    print(f"   Active areas: {final_stats['active_areas']}")
    
    print("\n" + "=" * 60)
    print("✅ Subscription system test completed!")
    
    # Show current subscriber data
    print("\n📋 Current Subscriber Data:")
    current_subscribers = load_subscribers()
    for area, users in current_subscribers.items():
        if users:
            district, taluka = area.split('_', 1)
            print(f"   {district}/{taluka}: {users}")

if __name__ == "__main__":
    test_subscription_system()