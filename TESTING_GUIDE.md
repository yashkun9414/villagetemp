# 🧪 Testing Guide - Bot Alert System

## ✅ Bot Status: WORKING
The bot connection is verified and working:
- **Bot Name**: Village Warning
- **Username**: @VillaegWarningbot
- **Status**: Active and responding

## 🔧 How to Test the Alert System

### Step 1: Subscribe to Bot
1. Go to https://t.me/VillaegWarningbot
2. Send `/start` to the bot
3. Send `/subscribe`
4. Choose **AHMEDABAD**
5. Choose **Bavla**
6. Confirm subscription

### Step 2: Test Demo Alert
After subscribing, run this command:
```bash
python send_demo_alert.py
```

This will send a demo temperature alert to all Bavla, Ahmedabad subscribers.

### Step 3: Test Website Integration
1. Login to website dashboard
2. Go to "Send Custom Alert"
3. Choose **AHMEDABAD** → **Bavla**
4. Type a test message
5. Send alert
6. Check Telegram for the message

## 🧪 Manual Testing Commands

### Test Bot Connection
```bash
python -c "import requests; import os; from dotenv import load_dotenv; load_dotenv(); token=os.getenv('TELEGRAM_BOT_TOKEN'); r=requests.get(f'https://api.telegram.org/bot{token}/getMe'); print('Bot:', r.json()['result']['username'])"
```

### Check Subscribers
```bash
python -c "from shared_data import get_subscribers_for_area; subs = get_subscribers_for_area('AHMEDABAD', 'Bavla'); print(f'Subscribers: {len(subs)}')"
```

### Send Test Message
```bash
python send_demo_alert.py
```

## 📱 Expected Results

### If Working Correctly:
- Bot responds to `/start` with welcome message
- Subscription process works smoothly
- Demo alert appears in Telegram
- Website alerts reach subscribers

### If Not Working:
- Bot doesn't respond → Check bot deployment
- No alerts received → Check subscription status
- Error messages → Check logs and user IDs

## 🔍 Troubleshooting

### Bot Not Responding
- Check if bot is deployed correctly
- Verify bot token in environment variables
- Check Railway/Heroku logs

### No Alerts Received
- Ensure you subscribed to correct district/taluka
- Check if bot has permission to send messages
- Verify user started the bot with `/start`

### Website Alerts Not Working
- Check if both bot and website are deployed
- Verify shared data system is working
- Check subscriber count in dashboard

## 🎯 Test Checklist

- [ ] Bot responds to `/start`
- [ ] Subscription process works
- [ ] `/weather` command shows data
- [ ] Demo alert script sends message
- [ ] Website dashboard shows subscribers
- [ ] Website alerts reach Telegram
- [ ] Real weather data displays

## 📞 Ready to Test!

The system is ready for testing. Follow the steps above and let me know:
1. Did you receive the bot's welcome message?
2. Did the subscription process work?
3. Did you receive the demo alert?
4. Did website alerts reach your Telegram?

Your feedback will help confirm everything is working correctly! 🚀