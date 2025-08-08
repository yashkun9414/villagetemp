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
from telegram.error import TelegramError
from dotenv import load_dotenv
import logging

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
    get_pending_alerts, mark_alert_sent, send_alert_to_subscribers
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

Commands:
/start - Start the bot
/subscribe - Subscribe to weather alerts
/unsubscribe - Unsubscribe from alerts
/mystatus - Check subscription status
/weather - Get current weather for your area
/fire - Check recent fire alerts in your area
/help - Show this help

How to subscribe:
1. Send /subscribe
2. Choose your district
3. Choose your taluka
4. Confirm subscription

You'll get real-time weather alerts for your selected area!"""
    
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
            
            # Save subscription using shared data system
            add_subscriber(user_id, district, taluka)
            
            await update.message.reply_text(
                f"🎉 Successfully subscribed!\n\n"
                f"📍 You'll receive weather alerts for:\n"
                f"   {taluka}, {district}\n\n"
                f"Commands:\n"
                f"/mystatus - Check subscription\n"
                f"/unsubscribe - Unsubscribe",
                reply_markup=ReplyKeyboardRemove()
            )
            
            logger.info(f"User {user_id} subscribed to {district} -> {taluka}")
        else:
            await update.message.reply_text(
                "❌ Subscription cancelled.",
                reply_markup=ReplyKeyboardRemove()
            )
        
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
    user_areas = [(district, taluka)]
    
    # Get fire alerts for user's areas
    all_alerts = []
    for district, taluka in user_areas:
        alerts = get_fire_alerts_for_area(district, taluka)
        for alert in alerts:
            confidence = alert.get('confidence', 'N/A')
            fire_type = alert.get('fire_type', 'Fire')
            date = alert.get('acq_date', 'Unknown')
            all_alerts.append(f"🔥 {date}: {fire_type} in {district} → {taluka} ({confidence}%)")
    
    if all_alerts:
        alert_text = "🔥 Recent Fire Alerts (Last 7 Days):\n\n" + "\n".join(all_alerts[:10])
        if len(all_alerts) > 10:
            alert_text += f"\n\n... and {len(all_alerts) - 10} more incidents"
        alert_text += "\n\n⚠️ Data from NASA MODIS satellites"
    else:
        alert_text = "✅ No recent fire alerts in your subscribed areas!\n\n🛰️ Data from NASA MODIS satellites"
    
    await update.message.reply_text(alert_text)

async def send_weather_alert_to_subscribers(district, taluka, message):
    """Send weather alert to subscribers of a specific area"""
    try:
        subscribers = get_subscribers_for_area(district, taluka)
        
        if not subscribers:
            logger.warning(f"No subscribers found for {taluka}, {district}")
            return {
                'success': False,
                'sent': 0,
                'failed': 0,
                'error': 'No subscribers found'
            }

        sent = 0
        failed = 0
        application = context.application

        for user_id in subscribers:
            try:
                alert_message = f"""🚨 *WEATHER ALERT*
                
📍 *Location:* {taluka}, {district}
⚠️ *Alert:* {message}

_Stay safe and follow local authorities' guidance._"""

                await application.bot.send_message(
                    chat_id=user_id,
                    text=alert_message,
                    parse_mode='Markdown'
                )
                sent += 1
                logger.info(f"Alert sent successfully to user {user_id}")
                
            except TelegramError as te:
                failed += 1
                logger.error(f"Telegram error sending to {user_id}: {te}")
                if "user not found" in str(te).lower():
                    remove_subscriber(user_id)
                    logger.info(f"Removed inactive user {user_id}")
            
            except Exception as e:
                failed += 1
                logger.error(f"Failed sending to {user_id}: {e}")

        result = {
            'success': sent > 0,
            'sent': sent,
            'failed': failed,
            'total': len(subscribers)
        }
        
        logger.info(f"Alert sending complete: {result}")
        return result

    except Exception as e:
        logger.error(f"Critical error in send_weather_alert: {e}")
        return {
            'success': False,
            'sent': 0,
            'failed': 0,
            'error': str(e)
        }

async def process_pending_alerts(context):
    """Process pending alerts from queue"""
    try:
        pending = get_pending_alerts()
        logger.info(f"Processing {len(pending)} pending alerts")

        for alert in pending:
            result = await send_weather_alert_to_subscribers(
                alert['district'],
                alert['taluka'],
                alert['message']
            )
            
            if result['success']:
                mark_alert_sent(alert['id'])
                logger.info(f"Alert {alert['id']} processed successfully")
            else:
                logger.warning(f"Alert {alert['id']} failed: {result}")

    except Exception as e:
        logger.error(f"Error processing alerts: {e}")

def main():
    """Run the bot"""
    logger.info("🚀 Starting Gujarat Weather Alert Bot...")
    logger.info("🤖 Bot Username: @VillaegWarningbot")
    logger.info("🔗 Bot Link: https://t.me/VillaegWarningbot")
    
    # Load data
    load_data()
    
    # Create application
    application = Application.builder().token(TOKEN).build()
    
    # Add job queue for periodic alert processing
    job_queue = application.job_queue
    job_queue.run_repeating(process_pending_alerts, interval=60, first=10)
    
    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("subscribe", subscribe))
    application.add_handler(CommandHandler("unsubscribe", unsubscribe))
    application.add_handler(CommandHandler("mystatus", mystatus))
    application.add_handler(CommandHandler("weather", weather_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Start the bot
    if os.environ.get('ENVIRONMENT') == 'production':
        application.run_webhook(
            listen="0.0.0.0",
            port=PORT,
            url_path=TOKEN,
            webhook_url=f"https://{os.getenv('APP_NAME')}.herokuapp.com/{TOKEN}"
        )
    else:
        application.run_polling()

if __name__ == '__main__':
    main()

async def weather_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get current weather for user's subscribed area"""
    try:
        user_id = update.effective_user.id
        subscription = get_user_subscription(user_id)
        
        if not subscription:
            await update.message.reply_text(
                "❌ You're not subscribed to any area.\n"
                "Use /subscribe to set up your location first!"
            )
            return

        district = subscription['district']
        taluka = subscription['taluka']

        # Get weather data for the location
        try:
            weather_data = get_weather_data(district, taluka)
            
            if weather_data:
                weather_msg = f"""🌡️ *Current Weather*
                
📍 *Location:* {taluka}, {district}
🌡️ *Temperature:* {weather_data['temp']}°C
💧 *Humidity:* {weather_data['humidity']}%
🌪️ *Wind:* {weather_data['wind_speed']} km/h

_Last updated: {weather_data['timestamp']}_"""
                
                await update.message.reply_text(
                    weather_msg,
                    parse_mode='Markdown'
                )
            else:
                await update.message.reply_text(
                    "⚠️ Weather data currently unavailable for your area.\n"
                    "Please try again later."
                )
                
        except Exception as e:
            logger.error(f"Error fetching weather data: {e}")
            await update.message.reply_text(
                "😔 Sorry, there was an error getting weather data.\n"
                "Please try again later."
            )
            
    except Exception as e:
        logger.error(f"Error in weather command: {e}")
        await update.message.reply_text(
            "❌ An error occurred. Please try again later."
        )

def get_weather_data(district, taluka):
    """Get weather data for location from data source"""
    try:
        # Implement your weather data fetching logic here
        # This is a placeholder implementation
        return {
            'temp': 32,
            'humidity': 65,
            'wind_speed': 12,
            'timestamp': 'Just now'
        }
    except Exception as e:
        logger.error(f"Error getting weather data: {e}")
        return None