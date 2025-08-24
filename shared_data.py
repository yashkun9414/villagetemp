#!/usr/bin/env python3
"""
Shared data system between bot and website
"""

import json
import os
import logging
from datetime import datetime
import asyncio
import requests

logger = logging.getLogger(__name__)

# File to store subscriber data
SUBSCRIBERS_FILE = 'subscribers.json'
ALERTS_FILE = 'pending_alerts.json'

def load_subscribers():
    """Load subscribers from file"""
    try:
        if os.path.exists(SUBSCRIBERS_FILE):
            with open(SUBSCRIBERS_FILE, 'r') as f:
                return json.load(f)
        return {}
    except Exception as e:
        logger.error(f"Error loading subscribers: {e}")
        return {}

def save_subscribers(subscribers):
    """Save subscribers to file with backup and validation"""
    try:
        # Validate data structure
        if not isinstance(subscribers, dict):
            logger.error("Invalid subscribers data structure")
            return False
        
        # Create backup of existing file
        if os.path.exists(SUBSCRIBERS_FILE):
            backup_file = f"{SUBSCRIBERS_FILE}.backup"
            try:
                import shutil
                shutil.copy2(SUBSCRIBERS_FILE, backup_file)
                logger.debug(f"Created backup: {backup_file}")
            except Exception as e:
                logger.warning(f"Could not create backup: {e}")
        
        # Save with atomic write (write to temp file first)
        temp_file = f"{SUBSCRIBERS_FILE}.tmp"
        with open(temp_file, 'w') as f:
            json.dump(subscribers, f, indent=2)
        
        # Move temp file to actual file (atomic operation)
        import shutil
        shutil.move(temp_file, SUBSCRIBERS_FILE)
        
        logger.debug(f"Successfully saved {len(subscribers)} subscription areas")
        return True
        
    except Exception as e:
        logger.error(f"Error saving subscribers: {e}")
        # Clean up temp file if it exists
        temp_file = f"{SUBSCRIBERS_FILE}.tmp"
        if os.path.exists(temp_file):
            try:
                os.remove(temp_file)
            except:
                pass
        return False

def add_subscriber(user_id, district, taluka):
    """Add a subscriber with proper error handling and validation"""
    try:
        # Validate inputs
        if not user_id or not district or not taluka:
            logger.error(f"Invalid subscription data: user_id={user_id}, district={district}, taluka={taluka}")
            return False
        
        # Ensure user_id is integer
        user_id = int(user_id)
        
        subscribers = load_subscribers()
        key = f"{district}_{taluka}"
        
        # Initialize key if it doesn't exist
        if key not in subscribers:
            subscribers[key] = []
            logger.info(f"Created new subscription area: {key}")
        
        # Remove user from other subscriptions (one user can only subscribe to one area)
        removed_from = []
        for sub_key in list(subscribers.keys()):
            if user_id in subscribers[sub_key]:
                subscribers[sub_key].remove(user_id)
                removed_from.append(sub_key)
        
        if removed_from:
            logger.info(f"User {user_id} removed from previous subscriptions: {removed_from}")
        
        # Add to new subscription (check if already exists to avoid duplicates)
        if user_id not in subscribers[key]:
            subscribers[key].append(user_id)
            logger.info(f"User {user_id} added to {key}")
        else:
            logger.info(f"User {user_id} already subscribed to {key}")
        
        # Save with error handling
        if save_subscribers(subscribers):
            logger.info(f"✅ User {user_id} successfully subscribed to {district} -> {taluka}")
            return True
        else:
            logger.error(f"❌ Failed to save subscription for user {user_id}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error adding subscriber {user_id} to {district}/{taluka}: {e}")
        return False

def remove_subscriber(user_id):
    """Remove subscriber from all areas"""
    subscribers = load_subscribers()
    removed = False
    
    for key in list(subscribers.keys()):
        if user_id in subscribers[key]:
            subscribers[key].remove(user_id)
            removed = True
    
    if removed:
        save_subscribers(subscribers)
        logger.info(f"User {user_id} unsubscribed from all areas")
    
    return removed

def get_user_subscription(user_id):
    """Get user's current subscription"""
    subscribers = load_subscribers()
    
    for key, user_list in subscribers.items():
        if user_id in user_list:
            district, taluka = key.split('_', 1)
            return {'district': district, 'taluka': taluka}
    
    return None

def get_subscribers_for_area(district, taluka):
    """Get all subscribers for a specific area"""
    subscribers = load_subscribers()
    key = f"{district}_{taluka}"
    return subscribers.get(key, [])

def queue_alert(district, taluka, message, alert_type="custom"):
    """Queue an alert to be sent to subscribers"""
    try:
        # Load existing alerts
        alerts = []
        if os.path.exists(ALERTS_FILE):
            with open(ALERTS_FILE, 'r') as f:
                alerts = json.load(f)
        
        # Add new alert
        alert = {
            'id': f"{datetime.now().timestamp()}",
            'district': district,
            'taluka': taluka,
            'message': message,
            'type': alert_type,
            'timestamp': datetime.now().isoformat(),
            'sent': False
        }
        
        alerts.append(alert)
        
        # Save alerts
        with open(ALERTS_FILE, 'w') as f:
            json.dump(alerts, f, indent=2)
        
        logger.info(f"Alert queued for {district} -> {taluka}: {message}")
        return True
        
    except Exception as e:
        logger.error(f"Error queuing alert: {e}")
        return False

def get_pending_alerts():
    """Get all pending alerts"""
    try:
        if os.path.exists(ALERTS_FILE):
            with open(ALERTS_FILE, 'r') as f:
                alerts = json.load(f)
            return [alert for alert in alerts if not alert.get('sent', False)]
        return []
    except Exception as e:
        logger.error(f"Error getting pending alerts: {e}")
        return []

def mark_alert_sent(alert_id):
    """Mark an alert as sent"""
    try:
        if os.path.exists(ALERTS_FILE):
            with open(ALERTS_FILE, 'r') as f:
                alerts = json.load(f)
            
            for alert in alerts:
                if alert['id'] == alert_id:
                    alert['sent'] = True
                    alert['sent_at'] = datetime.now().isoformat()
            
            with open(ALERTS_FILE, 'w') as f:
                json.dump(alerts, f, indent=2)
            
            return True
    except Exception as e:
        logger.error(f"Error marking alert as sent: {e}")
        return False

async def send_telegram_message(bot_token, chat_id, message):
    """Send message via Telegram Bot API"""
    try:
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        data = {
            'chat_id': chat_id,
            'text': message,
            'parse_mode': 'HTML'
        }
        
        response = requests.post(url, data=data, timeout=10)
        response.raise_for_status()
        
        return True
    except Exception as e:
        logger.error(f"Error sending Telegram message to {chat_id}: {e}")
        return False

def validate_and_clean_subscribers():
    """Validate and clean subscriber data"""
    try:
        subscribers = load_subscribers()
        cleaned = False
        
        # Remove empty subscription areas
        empty_keys = [key for key, users in subscribers.items() if not users]
        for key in empty_keys:
            del subscribers[key]
            cleaned = True
            logger.info(f"Removed empty subscription area: {key}")
        
        # Remove duplicate user IDs within same area
        for key, users in subscribers.items():
            if users:
                original_count = len(users)
                # Convert to set to remove duplicates, then back to list
                unique_users = list(set(users))
                if len(unique_users) != original_count:
                    subscribers[key] = unique_users
                    cleaned = True
                    logger.info(f"Removed {original_count - len(unique_users)} duplicate users from {key}")
        
        # Save if any cleaning was done
        if cleaned:
            save_subscribers(subscribers)
            logger.info("✅ Subscriber data cleaned and saved")
        
        return subscribers
        
    except Exception as e:
        logger.error(f"Error validating subscribers: {e}")
        return load_subscribers()

def get_subscription_stats():
    """Get subscription statistics"""
    try:
        subscribers = load_subscribers()
        total_subscribers = sum(len(users) for users in subscribers.values())
        active_areas = len([k for k, v in subscribers.items() if v])
        
        return {
            'total_subscribers': total_subscribers,
            'active_areas': active_areas,
            'areas': subscribers
        }
    except Exception as e:
        logger.error(f"Error getting subscription stats: {e}")
        return {'total_subscribers': 0, 'active_areas': 0, 'areas': {}}

def send_alert_to_subscribers(district, taluka, message, bot_token):
    """Send alert to all subscribers of an area"""
    try:
        subscribers = get_subscribers_for_area(district, taluka)
        
        if not subscribers:
            logger.info(f"No subscribers for {district} -> {taluka}")
            return 0
        
        sent_count = 0
        failed_count = 0
        alert_text = f"⚠️ WEATHER ALERT\n\n{message}\n\n📍 Location: {taluka}, {district}\n🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        for user_id in subscribers:
            try:
                # Use requests to send via Telegram API
                url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
                data = {
                    'chat_id': user_id,
                    'text': alert_text
                }
                
                response = requests.post(url, data=data, timeout=10)
                if response.status_code == 200:
                    sent_count += 1
                    logger.info(f"Alert sent to user {user_id}")
                else:
                    failed_count += 1
                    logger.error(f"Failed to send alert to user {user_id}: {response.text}")
                    
            except Exception as e:
                failed_count += 1
                logger.error(f"Error sending alert to user {user_id}: {e}")
        
        logger.info(f"Alert sent to {sent_count}/{len(subscribers)} subscribers in {district} -> {taluka} (Failed: {failed_count})")
        return sent_count
        
    except Exception as e:
        logger.error(f"Error sending alert to subscribers: {e}")
        return 0