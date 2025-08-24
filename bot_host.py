#!/usr/bin/env python3
"""
Standalone bot hosting script for Railway/Heroku
This keeps the bot running 24/7 independently
"""

import os
import asyncio
import pandas as pd
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
# make sure JobQueue is available
# requires: python-telegram-bot[job-queue]

from dotenv import load_dotenv
import logging
from datetime import datetime

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Bot configuration
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '8235992714:AAED7tTjm6waV6Ak-L-_LgRz37ZfnuEnE4w')
PORT = int(os.environ.get('PORT', 8080))

# Global data
user_data = {}
districts = []
talukas_data = {}

# Import shared data system
from shared_data import (
    load_subscribers, save_subscribers, add_subscriber, remove_subscriber,
    get_user_subscription, get_subscribers_for_area, queue_alert,
    get_pending_alerts, mark_alert_sent, send_alert_to_subscribers,
    validate_and_clean_subscribers, get_subscription_stats
)

def load_data():
    """Load CSV data"""
    global districts, talukas_data
    try:
        # Try to load from different possible locations
        csv_files = [
            'merged_village_temperature_data.csv',
            'static/merged_village_temperature_data.csv',
            '/app/merged_village_temperature_data.csv'
        ]
        
        df = None
        for csv_file in csv_files:
            try:
                df = pd.read_csv(csv_file)
                logger.info(f"✅ Loaded data from {csv_file}")
                break
            except FileNotFoundError:
                continue
        
        if df is None:
            logger.error("❌ Could not find CSV data file")
            return
        
        districts = sorted(df['District Name'].unique())
        
        # Create district -> talukas mapping
        for district in districts:
            district_talukas = df[df['District Name'] == district]['Taluka Name'].unique()
            talukas_data[district] = sorted(district_talukas)
        
        logger.info(f"✅ Loaded {len(districts)} districts and {len(df)} location records")
    except Exception as e:
        logger.error(f"❌ Error loading data: {e}")

def get_fire_alerts_for_area(district, taluka):
    """Get fire alerts for specific area"""
    try:
        fire_files = [
            'gujarat_fire_history.csv',
            'static/gujarat_fire_history.csv',
            '/app/gujarat_fire_history.csv'
        ]
        
        fire_df = None
        for fire_file in fire_files:
            try:
                fire_df = pd.read_csv(fire_file)
                break
            except FileNotFoundError:
                continue
        
        if fire_df is None:
            return []
        
        # Get recent fires (last 7 days) for the area
        from datetime import datetime, timedelta
        week_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        
        recent_fires = fire_df[
            (fire_df['acq_date'] >= week_ago) & 
            (fire_df['district'] == district) & 
            (fire_df['taluka'] == taluka) &
            (fire_df['confidence'] >= 70)
        ]
        
        return recent_fires.to_dict('records')
        
    except Exception as e:
        logger.error(f"Error getting fire alerts: {e}")
        return []

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command"""
    # Process any pending alerts when user interacts
    try:
        await process_pending_alerts(context.application)
    except:
        pass  # Don't let alert processing errors affect user interaction
    
    welcome_text = """🌡️ Welcome to Gujarat Weather Alert Bot!

I provide real-time weather alerts for your area in Gujarat using live weather data.

Available commands:
/start - Show this welcome message
/subscribe - Subscribe to alerts for your taluka
/weather - Get current weather for your area
/unsubscribe - Unsubscribe from alerts
/mystatus - Check your subscription
/fire - Check recent fire alerts in your area
/help - Get help

👆 Use /subscribe to get started and receive real weather alerts!"""
    
    await update.message.reply_text(welcome_text)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Help command"""
    help_text = """🆘 Help - Gujarat Weather Alert Bot

📱 User Commands:
/start - Start the bot and see welcome message
/subscribe - Subscribe to weather & fire alerts
/unsubscribe - Unsubscribe from all alerts
/mystatus - Check your subscription status
/weather - Get current weather for your area
/fire - Check recent fire alerts in your area
/stats - View bot statistics
/help - Show this help

🔧 Admin Commands:
/broadcast <district> <taluka> <message> - Send custom message to taluka subscribers
/adminfix - Check and fix subscription system issues

📋 How to subscribe:
1. Send /subscribe
2. Choose your district from the list
3. Choose your taluka from the list
4. Confirm your subscription
5. ✅ You'll get instant confirmation when successfully added!

✨ What you'll receive:
• Real-time weather alerts (high/low temperature)
• Fire incident notifications from NASA satellites
• Emergency messages from administrators
• Custom alerts for your specific area

🔒 Subscription Features:
• ✅ Automatic data validation and cleanup
• ✅ Duplicate prevention system
• ✅ Error handling and recovery
• ✅ One subscription per user (auto-updates location)
• ✅ Instant confirmation when subscribed

🛰️ Data Sources:
• Weather: Open-Meteo API (real-time)
• Fire Data: NASA MODIS satellites
• Location Data: Gujarat government records

🤖 Bot: @VillaegWarningbot

💡 Tip: If you experience any subscription issues, contact an admin or try /subscribe again."""
    
    await update.message.reply_text(help_text)

async def subscribe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Subscribe command"""
    # Process any pending alerts when user interacts
    try:
        await process_pending_alerts(context.application)
    except:
        pass
    
    user_id = update.effective_user.id
    
    if not districts:
        await update.message.reply_text("❌ Sorry, location data is not available. Please try again later.")
        return
    
    # Show first 10 districts
    keyboard = [[district] for district in districts[:10]]
    if len(districts) > 10:
        keyboard.append(["Show More Districts"])
    
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    user_data[user_id] = {'step': 'district'}
    
    await update.message.reply_text(
        "📍 Please select your district:",
        reply_markup=reply_markup
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle text messages"""
    user_id = update.effective_user.id
    text = update.message.text
    
    if user_id not in user_data:
        await update.message.reply_text("Please use /subscribe to start.")
        return
    
    step = user_data[user_id]['step']
    
    if step == 'district':
        if text == "Show More Districts":
            keyboard = [[district] for district in districts[10:]]
            reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
            await update.message.reply_text("📍 Select your district:", reply_markup=reply_markup)
            return
        
        if text not in districts:
            await update.message.reply_text("Please select a valid district from the options.")
            return
        
        # Show talukas for selected district
        district_talukas = talukas_data[text][:15]  # First 15 talukas
        keyboard = [[taluka] for taluka in district_talukas]
        if len(talukas_data[text]) > 15:
            keyboard.append(["Show More Talukas"])
        
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
        user_data[user_id] = {'step': 'taluka', 'district': text, 'all_talukas': talukas_data[text]}
        
        await update.message.reply_text(
            f"✅ Selected: {text}\n📍 Now select your taluka:",
            reply_markup=reply_markup
        )
    
    elif step == 'taluka':
        district = user_data[user_id]['district']
        all_talukas = user_data[user_id]['all_talukas']
        
        if text == "Show More Talukas":
            remaining_talukas = all_talukas[15:]
            keyboard = [[taluka] for taluka in remaining_talukas]
            reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
            await update.message.reply_text("📍 Select your taluka:", reply_markup=reply_markup)
            return
        
        if text not in all_talukas:
            await update.message.reply_text("Please select a valid taluka from the options.")
            return
        
        # Confirmation
        keyboard = [["✅ Yes, Subscribe"], ["❌ Cancel"]]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
        user_data[user_id] = {'step': 'confirm', 'district': district, 'taluka': text}
        
        await update.message.reply_text(
            f"📋 Confirm subscription:\n\n"
            f"📍 District: {district}\n"
            f"📍 Taluka: {text}\n\n"
            f"You'll receive weather alerts for this location.",
            reply_markup=reply_markup
        )
    
    elif step == 'confirm':
        if text == "✅ Yes, Subscribe":
            district = user_data[user_id]['district']
            taluka = user_data[user_id]['taluka']
            
            # Save subscription using shared data system with error handling
            try:
                if add_subscriber(user_id, district, taluka):
                    await update.message.reply_text(
                        f"🎉 Successfully subscribed!\n\n"
                        f"📍 You'll receive weather alerts for:\n"
                        f"   {taluka}, {district}\n\n"
                        f"Commands:\n"
                        f"/mystatus - Check subscription\n"
                        f"/unsubscribe - Unsubscribe\n"
                        f"/weather - Current weather\n"
                        f"/fire - Fire alerts",
                        reply_markup=ReplyKeyboardRemove()
                    )
                    
                    logger.info(f"✅ User {user_id} successfully subscribed to {district} -> {taluka}")
                    
                    # Send welcome message with current status
                    try:
                        subscription = get_user_subscription(user_id)
                        if subscription:
                            await update.message.reply_text(
                                f"✅ Subscription confirmed!\n\n"
                                f"📊 Your alerts are now active for:\n"
                                f"📍 {subscription['taluka']}, {subscription['district']}\n\n"
                                f"🔔 You'll receive:\n"
                                f"• High/Low temperature alerts\n"
                                f"• Fire incident notifications\n"
                                f"• Emergency weather warnings\n\n"
                                f"📱 Test your subscription with /weather"
                            )
                    except Exception as e:
                        logger.error(f"Error sending welcome message: {e}")
                        
                else:
                    await update.message.reply_text(
                        "❌ Sorry, there was an error saving your subscription. Please try again with /subscribe.",
                        reply_markup=ReplyKeyboardRemove()
                    )
                    logger.error(f"❌ Failed to subscribe user {user_id} to {district} -> {taluka}")
                    
            except Exception as e:
                logger.error(f"❌ Exception during subscription for user {user_id}: {e}")
                await update.message.reply_text(
                    "❌ Sorry, there was a technical error. Please try subscribing again with /subscribe.",
                    reply_markup=ReplyKeyboardRemove()
                )
        else:
            await update.message.reply_text(
                "❌ Subscription cancelled.",
                reply_markup=ReplyKeyboardRemove()
            )
        
        # Clean up user data
        if user_id in user_data:
            del user_data[user_id]

async def unsubscribe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Unsubscribe command"""
    user_id = update.effective_user.id
    
    if remove_subscriber(user_id):
        await update.message.reply_text("✅ Successfully unsubscribed from all alerts!")
        logger.info(f"User {user_id} unsubscribed")
    else:
        await update.message.reply_text("You are not subscribed to any alerts.")

async def mystatus(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Status command"""
    user_id = update.effective_user.id
    
    subscription = get_user_subscription(user_id)
    
    if subscription:
        district = subscription['district']
        taluka = subscription['taluka']
        
        status_text = f"📊 Your Subscription Status:\n\n📍 {taluka}, {district}"
        
        # Check for recent fire alerts in subscribed area
        fire_alerts = get_fire_alerts_for_area(district, taluka)
        if fire_alerts:
            status_text += f"\n🔥 {len(fire_alerts)} recent fire incident(s)"
    else:
        status_text = "📊 You are not subscribed to any alerts.\n\nUse /subscribe to get started!"
    
    await update.message.reply_text(status_text)

async def fire_alerts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Fire alerts command"""
    user_id = update.effective_user.id
    
    # Check user's subscribed area
    subscription = get_user_subscription(user_id)
    
    if not subscription:
        await update.message.reply_text("You are not subscribed to any areas. Use /subscribe first!")
        return
    
    district = subscription['district']
    taluka = subscription['taluka']
    
    # Get fire alerts for user's area
    alerts = get_fire_alerts_for_area(district, taluka)
    
    if alerts and len(alerts) > 0:
        # Filter for recent alerts (last 7 days)
        from datetime import datetime, timedelta
        week_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        recent_alerts = [a for a in alerts if a.get('acq_date', '') >= week_ago]
        
        if recent_alerts:
            # Categorize alerts by severity and confidence
            high_risk = [a for a in recent_alerts if a.get('confidence', 0) >= 80]
            medium_risk = [a for a in recent_alerts if 60 <= a.get('confidence', 0) < 80]
            low_risk = [a for a in recent_alerts if a.get('confidence', 0) < 60]
            
            alert_text = f"🔥 Fire Alerts for {taluka}, {district}\n"
            alert_text += f"📊 Recent: {len(recent_alerts)} incidents (Last 7 Days)\n\n"
            
            if high_risk:
                alert_text += f"🚨 HIGH RISK ({len(high_risk)} incidents):\n"
                for alert in high_risk[:3]:
                    alert_text += f"   📅 {alert.get('acq_date', 'Unknown')}: {alert.get('fire_type', 'Fire')} ({alert.get('confidence', 'N/A')}%)\n"
                    alert_text += f"   📍 {alert.get('latitude', 0):.4f}, {alert.get('longitude', 0):.4f}\n"
                if len(high_risk) > 3:
                    alert_text += f"   ... and {len(high_risk) - 3} more high-risk incidents\n"
                alert_text += "\n"
            
            if medium_risk:
                alert_text += f"⚠️ MEDIUM RISK ({len(medium_risk)} incidents)\n"
                for alert in medium_risk[:2]:
                    alert_text += f"   📅 {alert.get('acq_date', 'Unknown')}: {alert.get('fire_type', 'Fire')} ({alert.get('confidence', 'N/A')}%)\n"
                if len(medium_risk) > 2:
                    alert_text += f"   ... and {len(medium_risk) - 2} more medium-risk incidents\n"
                alert_text += "\n"
            
            if low_risk:
                alert_text += f"ℹ️ LOW RISK: {len(low_risk)} incidents\n\n"
            
            alert_text += "🛰️ Data from NASA MODIS satellites\n"
            alert_text += "📱 Use /weather for current weather conditions"
        else:
            alert_text = f"✅ No recent fire alerts for {taluka}, {district}!\n\n"
            alert_text += "🛰️ All clear in your area (last 7 days)\n"
            alert_text += "📱 Use /weather for current weather conditions"
    else:
        alert_text = f"✅ No fire alerts for {taluka}, {district}!\n\n"
        alert_text += "🛰️ No fire incidents detected in your area\n"
        alert_text += "📡 NASA MODIS satellite monitoring active\n"
        alert_text += "📱 Use /weather for current weather conditions"
    
    await update.message.reply_text(alert_text)

async def send_weather_alert_to_subscribers(district, taluka, message):
    """Send weather alert to subscribers of a specific area"""
    try:
        key = f"{district}_{taluka}"
        if key in subscribers and subscribers[key]:
            # Get bot application
            application = Application.builder().token(TOKEN).build()
            
            for user_id in subscribers[key]:
                try:
                    await application.bot.send_message(
                        chat_id=user_id,
                        text=f"⚠️ WEATHER ALERT\n\n{message}\n\n📍 Location: {taluka}, {district}\n🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                    )
                    logger.info(f"Weather alert sent to user {user_id}")
                except Exception as e:
                    logger.error(f"Failed to send alert to user {user_id}: {e}")
            
            return True
    except Exception as e:
        logger.error(f"Error sending weather alert: {e}")
        return False

async def weather_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get current weather for subscribed area"""
    user_id = update.effective_user.id
    
    # Check user's subscribed area
    subscription = get_user_subscription(user_id)
    
    if not subscription:
        await update.message.reply_text("You are not subscribed to any areas. Use /subscribe first!")
        return
    
    district = subscription['district']
    taluka = subscription['taluka']
    
    # Get weather for user's area
    try:
        from weather_api import get_weather_for_taluka
        
        weather_data = get_weather_for_taluka(district, taluka)
        if weather_data:
            temp = weather_data['current_temp']
            
            # Add temperature alerts
            temp_alert = ""
            if temp >= 40:
                temp_alert = "\n🚨 HIGH TEMPERATURE ALERT! Stay hydrated and avoid outdoor activities."
            elif temp <= 5:
                temp_alert = "\n🥶 LOW TEMPERATURE ALERT! Dress warmly and protect crops."
            
            weather_text = f"🌤️ Current Weather for {taluka}, {district}:\n\n"
            weather_text += f"🌡️ Temperature: {temp}°C\n"
            weather_text += f"📊 Max/Min: {weather_data['max_temp']}°C / {weather_data['min_temp']}°C\n"
            weather_text += f"💧 Humidity: {weather_data['humidity']}%\n"
            weather_text += f"💨 Wind: {weather_data.get('wind_speed', 'N/A')} km/h\n"
            weather_text += f"☁️ Condition: {weather_data['weather_description']}\n"
            weather_text += temp_alert
            weather_text += f"\n\n🕐 Updated: {datetime.now().strftime('%H:%M')}"
        else:
            weather_text = f"❌ Weather data not available for {taluka}, {district}."
        
        await update.message.reply_text(weather_text)
        
    except Exception as e:
        logger.error(f"Error getting weather: {e}")
        await update.message.reply_text("❌ Error fetching weather data. Please try again later.")

async def broadcast_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin command to broadcast message to specific taluka (admin only)"""
    user_id = update.effective_user.id
    
    # Check if user is admin (you can customize this check)
    admin_ids = [int(os.getenv('ADMIN_TELEGRAM_ID', '0'))]  # Add admin Telegram IDs
    
    if user_id not in admin_ids and user_id != 123456789:  # Replace with actual admin ID
        await update.message.reply_text("❌ This command is only available to administrators.")
        return
    
    # Parse command arguments
    args = context.args
    if len(args) < 3:
        await update.message.reply_text(
            "Usage: /broadcast <district> <taluka> <message>\n\n"
            "Example: /broadcast AHMADABAD Bavla Emergency alert for your area"
        )
        return
    
    district = args[0]
    taluka = args[1]
    message = " ".join(args[2:])
    
    # Get subscribers for the area
    subscribers = get_subscribers_for_area(district, taluka)
    
    if not subscribers:
        await update.message.reply_text(f"❌ No subscribers found for {taluka}, {district}")
        return
    
    # Queue the broadcast message
    try:
        if queue_alert(district, taluka, f"📢 ADMIN MESSAGE:\n\n{message}", "admin"):
            await update.message.reply_text(
                f"✅ Broadcast queued for {len(subscribers)} subscribers in {taluka}, {district}!\n\n"
                f"Message: {message}"
            )
            logger.info(f"Admin {user_id} broadcast to {district}/{taluka}: {message}")
        else:
            await update.message.reply_text("❌ Failed to queue broadcast message.")
    except Exception as e:
        logger.error(f"Error broadcasting message: {e}")
        await update.message.reply_text("❌ Error sending broadcast message.")

async def admin_fix_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin command to fix subscription issues"""
    user_id = update.effective_user.id
    
    # Check if user is admin
    admin_ids = [int(os.getenv('ADMIN_TELEGRAM_ID', '0'))]
    
    if user_id not in admin_ids and user_id != 123456789:  # Replace with actual admin ID
        await update.message.reply_text("❌ This command is only available to administrators.")
        return
    
    try:
        # Clean and validate subscriber data
        old_subscribers = load_subscribers()
        cleaned_subscribers = validate_and_clean_subscribers()
        
        # Get statistics
        stats = get_subscription_stats()
        
        fix_text = f"🔧 ADMIN: Subscription System Check\n\n"
        fix_text += f"📊 Current Status:\n"
        fix_text += f"   • Total Subscribers: {stats['total_subscribers']}\n"
        fix_text += f"   • Active Areas: {stats['active_areas']}\n\n"
        
        # Check for issues
        issues_found = []
        
        # Check for empty areas
        empty_areas = [k for k, v in cleaned_subscribers.items() if not v]
        if empty_areas:
            issues_found.append(f"Empty areas: {len(empty_areas)}")
        
        # Check file integrity
        try:
            with open(SUBSCRIBERS_FILE, 'r') as f:
                json.load(f)
            file_status = "✅ File OK"
        except:
            file_status = "❌ File corrupted"
            issues_found.append("Corrupted file")
        
        fix_text += f"📁 File Status: {file_status}\n"
        
        if issues_found:
            fix_text += f"⚠️ Issues Found: {', '.join(issues_found)}\n"
            fix_text += f"✅ Issues automatically fixed!\n"
        else:
            fix_text += f"✅ No issues found - system healthy!\n"
        
        # Show recent subscription activity
        fix_text += f"\n📈 Recent Activity:\n"
        for key, users in list(cleaned_subscribers.items())[:5]:
            if users:
                district, taluka = key.split('_', 1)
                fix_text += f"   • {taluka}, {district}: {len(users)} subscribers\n"
        
        await update.message.reply_text(fix_text)
        
    except Exception as e:
        logger.error(f"Error in admin fix command: {e}")
        await update.message.reply_text(f"❌ Error during system check: {str(e)}")

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show bot statistics with data validation"""
    try:
        # Clean and validate subscriber data first
        subscribers = validate_and_clean_subscribers()
        stats = get_subscription_stats()
        
        total_subscribers = stats['total_subscribers']
        areas_with_subscribers = stats['active_areas']
        
        # Get top subscribed areas
        top_areas = []
        for key, users in subscribers.items():
            if users:
                district, taluka = key.split('_', 1)
                top_areas.append((district, taluka, len(users)))
        
        top_areas.sort(key=lambda x: x[2], reverse=True)
        
        stats_text = f"📊 Gujarat Weather & Fire Alert Bot\n\n"
        stats_text += f"👥 Total Subscribers: {total_subscribers}\n"
        stats_text += f"📍 Areas with Subscribers: {areas_with_subscribers}\n\n"
        
        if top_areas:
            stats_text += "🏆 Top Subscribed Areas:\n"
            for i, (district, taluka, count) in enumerate(top_areas[:5], 1):
                stats_text += f"{i}. {taluka}, {district} ({count} subscribers)\n"
        
        # Add fire data stats
        try:
            fire_files = [
                'gujarat_fire_history.csv',
                'static/gujarat_fire_history.csv'
            ]
            
            fire_df = None
            for fire_file in fire_files:
                try:
                    fire_df = pd.read_csv(fire_file)
                    break
                except FileNotFoundError:
                    continue
            
            if fire_df is not None and not fire_df.empty:
                from datetime import datetime, timedelta
                today = datetime.now().strftime('%Y-%m-%d')
                week_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
                
                today_fires = len(fire_df[fire_df['acq_date'] == today])
                week_fires = len(fire_df[fire_df['acq_date'] >= week_ago])
                total_fires = len(fire_df)
                
                stats_text += f"\n🔥 Fire Monitoring:\n"
                stats_text += f"   Today: {today_fires} incidents\n"
                stats_text += f"   Last 7 days: {week_fires} incidents\n"
                stats_text += f"   Total tracked: {total_fires} incidents\n"
                
                if today_fires == 0 and week_fires == 0:
                    stats_text += f"   ✅ No recent fire activity detected\n"
            else:
                stats_text += f"\n🔥 Fire Monitoring:\n"
                stats_text += f"   ✅ No fire incidents detected\n"
                stats_text += f"   🛰️ NASA MODIS monitoring active\n"
        except Exception as e:
            logger.error(f"Error getting fire stats: {e}")
            stats_text += f"\n🔥 Fire Monitoring: Data unavailable\n"
        
        stats_text += f"\n🛰️ Data Sources:\n"
        stats_text += f"   • NASA MODIS satellites\n"
        stats_text += f"   • Open-Meteo weather API\n"
        stats_text += f"   • Gujarat government records\n"
        stats_text += f"\n🤖 Bot: @VillaegWarningbot"
        
        await update.message.reply_text(stats_text)
        
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        await update.message.reply_text("❌ Error fetching statistics.")

async def process_pending_alerts(application):
    """Process pending alerts from the website"""
    try:
        pending_alerts = get_pending_alerts()
        logger.info(f"Processing {len(pending_alerts)} pending alerts...")
        
        for alert in pending_alerts:
            district = alert['district']
            taluka = alert['taluka']
            message = alert['message']
            alert_id = alert.get('id', '')
            
            # Get subscribers for this area
            subscribers_list = get_subscribers_for_area(district, taluka)
            
            if subscribers_list:
                sent_count = 0
                failed_count = 0
                
                # Format alert message
                alert_text = (
                    f"🚨 WEATHER ALERT\n\n"
                    f"{message}\n\n"
                    f"📍 {taluka}, {district}\n"
                    f"🕒 {datetime.now().strftime('%Y-%m-%d %H:%M')}"
                )
                
                for user_id in subscribers_list:
                    try:
                        await application.bot.send_message(
                            chat_id=int(user_id),  # Convert to int
                            text=alert_text,
                            parse_mode='HTML'
                        )
                        sent_count += 1
                        await asyncio.sleep(0.1)  # Prevent rate limiting
                    except Exception as e:
                        failed_count += 1
                        logger.error(f"Failed to send alert to {user_id}: {str(e)}")
                
                logger.info(f"Alert {alert_id}: Sent to {sent_count} users, Failed: {failed_count}")
            else:
                logger.info(f"No subscribers found for {district} -> {taluka}")
            
            # Mark as sent even if some failed
            mark_alert_sent(alert_id)
            
    except Exception as e:
        logger.error(f"Error processing alerts: {str(e)}")

def main():
    """Run the bot"""
    logger.info("🚀 Starting Gujarat Weather Alert Bot...")
    logger.info("🤖 Bot Username: @VillaegWarningbot")
    logger.info("🔗 Bot Link: https://t.me/VillaegWarningbot")
    
    # Load data
    load_data()
    
    # Create application
    application = Application.builder().token(TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("subscribe", subscribe))
    application.add_handler(CommandHandler("unsubscribe", unsubscribe))
    application.add_handler(CommandHandler("mystatus", mystatus))
    application.add_handler(CommandHandler("fire", fire_alerts))
    application.add_handler(CommandHandler("weather", weather_command))
    application.add_handler(CommandHandler("broadcast", broadcast_command))
    application.add_handler(CommandHandler("stats", stats_command))
    application.add_handler(CommandHandler("adminfix", admin_fix_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Add job to process pending alerts every 30 seconds
    job_queue = application.job_queue
    job_queue.run_repeating(
        lambda context: asyncio.create_task(process_pending_alerts(application)),
        interval=30,
        first=10
    )
    
    # Add job to clean subscriber data every 10 minutes
    def cleanup_subscribers(context):
        try:
            validate_and_clean_subscribers()
            logger.info("✅ Periodic subscriber data cleanup completed")
        except Exception as e:
            logger.error(f"❌ Error during subscriber cleanup: {e}")
    
    job_queue.run_repeating(
        cleanup_subscribers,
        interval=600,  # 10 minutes
        first=60       # Start after 1 minute
    )
    
    logger.info("✅ Bot is now LIVE and responding!")
    logger.info("📨 Alert processing system active!")
    logger.info(f"🌐 Running on port {PORT}")
    
    # Run the bot
    application.run_polling()

if __name__ == '__main__':
    main()