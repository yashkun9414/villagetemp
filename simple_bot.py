#!/usr/bin/env python3
"""
Simple standalone Telegram bot for testing
This will make @VillaegWarningbot respond immediately
"""

import os
import asyncio
import pandas as pd
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv

load_dotenv()

# Bot token
TOKEN = "8235992714:AAED7tTjm6waV6Ak-L-_LgRz37ZfnuEnE4w"

# Global data
subscribers = {}
user_data = {}
districts = []
talukas_data = {}

def load_data():
    """Load CSV data"""
    global districts, talukas_data
    try:
        df = pd.read_csv('merged_village_temperature_data.csv')
        districts = sorted(df['District Name'].unique())
        
        # Create district -> talukas mapping
        for district in districts:
            district_talukas = df[df['District Name'] == district]['Taluka Name'].unique()
            talukas_data[district] = sorted(district_talukas)
        
        print(f"✅ Loaded {len(districts)} districts and {len(df)} location records")
    except Exception as e:
        print(f"❌ Error loading data: {e}")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command"""
    welcome_text = """🌡️ Welcome to Gujarat Weather Alert Bot!

I help you get weather alerts for your area in Gujarat.

Available commands:
/start - Show this welcome message
/subscribe - Subscribe to alerts for your taluka
/unsubscribe - Unsubscribe from alerts
/mystatus - Check your subscription
/help - Get help

👆 Use /subscribe to get started!"""
    
    await update.message.reply_text(welcome_text)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Help command"""
    help_text = """🆘 Help - Gujarat Weather Alert Bot

Commands:
/start - Start the bot
/subscribe - Subscribe to weather alerts
/unsubscribe - Unsubscribe from alerts
/mystatus - Check subscription status
/help - Show this help

How to subscribe:
1. Send /subscribe
2. Choose your district
3. Choose your taluka
4. Confirm subscription

You'll get weather alerts for your selected area!"""
    
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
            
            # Save subscription
            key = f"{district}_{taluka}"
            if key not in subscribers:
                subscribers[key] = []
            
            # Remove from other subscriptions
            for sub_key in list(subscribers.keys()):
                if user_id in subscribers[sub_key]:
                    subscribers[sub_key].remove(user_id)
            
            subscribers[key].append(user_id)
            
            await update.message.reply_text(
                f"🎉 Successfully subscribed!\n\n"
                f"📍 You'll receive weather alerts for:\n"
                f"   {taluka}, {district}\n\n"
                f"Commands:\n"
                f"/mystatus - Check subscription\n"
                f"/unsubscribe - Unsubscribe",
                reply_markup=ReplyKeyboardRemove()
            )
        else:
            await update.message.reply_text(
                "❌ Subscription cancelled.",
                reply_markup=ReplyKeyboardRemove()
            )
        
        del user_data[user_id]

async def unsubscribe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Unsubscribe command"""
    user_id = update.effective_user.id
    
    unsubscribed = False
    for key in list(subscribers.keys()):
        if user_id in subscribers[key]:
            subscribers[key].remove(user_id)
            unsubscribed = True
    
    if unsubscribed:
        await update.message.reply_text("✅ Successfully unsubscribed from all alerts!")
    else:
        await update.message.reply_text("You are not subscribed to any alerts.")

async def mystatus(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Status command"""
    user_id = update.effective_user.id
    
    subscribed_to = []
    for key, user_list in subscribers.items():
        if user_id in user_list:
            district, taluka = key.split('_', 1)
            subscribed_to.append(f"📍 {taluka}, {district}")
    
    if subscribed_to:
        status_text = "📊 Your Subscription Status:\n\n" + "\n".join(subscribed_to)
    else:
        status_text = "📊 You are not subscribed to any alerts.\n\nUse /subscribe to get started!"
    
    await update.message.reply_text(status_text)

def main():
    """Run the bot"""
    print("🚀 Starting Gujarat Weather Alert Bot...")
    print("=" * 50)
    print("🤖 Bot Username: @VillaegWarningbot")
    print("🔗 Bot Link: https://t.me/VillaegWarningbot")
    print("=" * 50)
    
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
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("✅ Bot is now LIVE and responding!")
    print("📱 Go to Telegram and message @VillaegWarningbot")
    print("🛑 Press Ctrl+C to stop")
    print("=" * 50)
    
    # Run the bot
    application.run_polling()

if __name__ == '__main__':
    main()