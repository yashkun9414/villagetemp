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
    """Save subscribers to file"""
    try:
        with open(SUBSCRIBERS_FILE, 'w') as f:
            json.dump(subscribers, f, indent=2)
        return True
    except Exception as e:
        logger.error(f"Error saving subscribers: {e}")
        return False

def add_subscriber(user_id, district, taluka):
    """Add a subscriber"""
    subscribers = load_subscribers()
    key = f"{district}_{taluka}"
    
    if key not in subscribers:
        subscribers[key] = []
    
    # Remove user from other subscriptions
    for sub_key in list(subscribers.keys()):
        if user_id in subscribers[sub_key]:
            subscribers[sub_key].remove(user_id)
    
    # Add to new subscription
    if user_id not in subscribers[key]:
        subscribers[key].append(user_id)
    
    save_subscribers(subscribers)
    logger.info(f"User {user_id} subscribed to {district} -> {taluka}")
    return True

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

def send_alert_to_subscribers(district, taluka, message, bot_token):
    """Send alert to all subscribers of an area"""
    try:
        subscribers = get_subscribers_for_area(district, taluka)
        
        if not subscribers:
            logger.info(f"No subscribers for {district} -> {taluka}")
            return 0
        
        sent_count = 0
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
                    logger.error(f"Failed to send alert to user {user_id}: {response.text}")
                    
            except Exception as e:
                logger.error(f"Error sending alert to user {user_id}: {e}")
        
        logger.info(f"Alert sent to {sent_count}/{len(subscribers)} subscribers in {district} -> {taluka}")
        return sent_count
        
    except Exception as e:
        logger.error(f"Error sending alert to subscribers: {e}")
        return 0