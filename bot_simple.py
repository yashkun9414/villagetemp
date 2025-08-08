#!/usr/bin/env python3
"""
Simple bot without job queue - works immediately
"""

import os
import asyncio
import pandas as pd
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
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

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command"""
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
    else:
        status_text = "📊 You are not subscribed to any alerts.\n\nUse /subscribe to get started!"
    
    await update.message.reply_text(status_text)

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
            weather_text = f"🌤️ Current Weather for {taluka}, {district}:\n\n"
            weather_text += f"🌡️ Temperature: {weather_data['current_temp']}°C\n"
            weather_text += f"📊 Max/Min: {weather_data['max_temp']}°C / {weather_data['min_temp']}°C\n"
            weather_text += f"💧 Humidity: {weather_data['humidity']}%\n"
            weather_text += f"☁️ Condition: {weather_data['weather_description']}\n"
        else:
            weather_text = "❌ Weather data not available for your subscribed area."
        
        await update.message.reply_text(weather_text)
        
    except Exception as e:
        logger.error(f"Error getting weather: {e}")
        await update.message.reply_text("❌ Error fetching weather data. Please try again later.")

def main():
    """Run the bot"""
    logger.info("🚀 Starting Gujarat Weather Alert Bot (Simple Version)...")
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
    application.add_handler(CommandHandler("weather", weather_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    logger.info("✅ Bot is now LIVE and responding!")
    logger.info("📨 Note: Alerts from website will be processed when users interact with bot")
    logger.info(f"🌐 Running on port {PORT}")
    
    # Run the bot
    application.run_polling()

if __name__ == '__main__':
    main()