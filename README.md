# 🌡️ Gujarat Weather Alert System

A clean, production-ready weather alert system with interactive map, admin panel, and Telegram bot integration for Gujarat, India.

## ✨ Features

### 🌐 Web Application
- **Interactive Map**: Leaflet-based map showing Gujarat districts and talukas
- **Admin Panel**: Secure dashboard for managing alerts
- **Responsive Design**: Works on all devices
- **Real-time Data**: CSV-based location data with 33 districts, 235 talukas

### 🤖 Telegram Bot (@VillaegWarningbot)
- **Location Subscription**: Users choose district → taluka for alerts
- **Interactive Commands**: /start, /subscribe, /unsubscribe, /mystatus, /help
- **24/7 Availability**: Hosted independently for continuous operation

## 🚀 Quick Start

### 1. Web Application
```bash
# Install dependencies
pip install -r requirements.txt

# Start web server
python app.py

# Access at http://localhost:5000
# Admin: admin@weatheralert.com / admin123
```

### 2. Telegram Bot
```bash
# Run bot locally
python simple_bot.py

# Or host on Railway/Heroku
python bot_host.py
```

### 3. Test the Bot
- Open Telegram
- Search: **@VillaegWarningbot**
- Send: `/start`
- Subscribe to your area with `/subscribe`

## 📁 Clean File Structure

```
villagetemp/
├── 🌐 Web App
│   ├── app.py                    # Flask application
│   ├── main.py                   # Firebase entry point
│   └── templates/                # HTML templates with map
│
├── 🤖 Bot Files
│   ├── simple_bot.py             # Local bot testing
│   └── bot_host.py               # Production bot hosting
│
├── 📊 Data & Config
│   ├── merged_village_temperature_data.csv  # Location data
│   ├── .env                      # Environment variables
│   ├── requirements.txt          # Dependencies
│   └── static/                   # Static files
│
└── 🚀 Deployment
    ├── firebase.json             # Firebase config
    ├── app.yaml                  # Google App Engine
    ├── railway.json              # Railway config
    └── Procfile                  # Heroku config
```

## 🌐 Deployment Options

### Option 1: Firebase (Web App)
```bash
firebase deploy
```

### Option 2: Railway (Bot Hosting)
1. Connect GitHub repo to Railway
2. Deploy `bot_host.py`
3. Bot runs 24/7 automatically

### Option 3: Heroku (Bot Hosting)
```bash
git push heroku main
```

## 🗺️ Interactive Map Features

- **District/Taluka Selection**: Dropdown filters
- **Location Search**: Find your area on map
- **Weather Data**: Click locations for information
- **Data Download**: Export displayed data as CSV
- **Responsive Design**: Works on mobile devices

## 🤖 Bot Commands

| Command | Description |
|---------|-------------|
| `/start` | Welcome message and instructions |
| `/subscribe` | Choose district and taluka for alerts |
| `/unsubscribe` | Stop receiving alerts |
| `/mystatus` | Check current subscription |
| `/help` | Get help and usage info |

## 🔧 Configuration

### Environment Variables (.env)
```
TELEGRAM_BOT_TOKEN=8235992714:AAED7tTjm6waV6Ak-L-_LgRz37ZfnuEnE4w
ADMIN_EMAIL=admin@weatheralert.com
ADMIN_PASSWORD=admin123
SECRET_KEY=your-secret-key-here
```

### Data Coverage
- **33 Districts** in Gujarat
- **235 Talukas** monitored
- **72,620 location records**
- Real-time alert targeting

## 🎯 Usage

### For End Users
1. **Find Bot**: Search @VillaegWarningbot on Telegram
2. **Subscribe**: Use `/subscribe` to choose your area
3. **Get Alerts**: Receive weather warnings for your location
4. **Manage**: Use `/mystatus` and `/unsubscribe` as needed

### For Administrators
1. **Access Panel**: Go to your-domain.com/admin
2. **Login**: Use admin credentials
3. **View Map**: Interactive map on homepage
4. **Send Alerts**: Target specific districts/talukas
5. **Monitor**: Check bot status and system stats

## 🔒 Security Features

- ✅ Environment variable configuration
- ✅ Secure admin authentication
- ✅ CSRF protection
- ✅ Input validation
- ✅ Production-ready security headers

## 📱 Mobile Responsive

- ✅ Works on all screen sizes
- ✅ Touch-friendly map controls
- ✅ Optimized for mobile Telegram usage
- ✅ Fast loading and smooth interactions

## 🆘 Support

### Bot Link
**https://t.me/VillaegWarningbot**

### Common Issues
1. **Bot not responding**: Check if bot is hosted and running
2. **Map not loading**: Verify CSV file is in static/ folder
3. **Admin login fails**: Check credentials in .env file

### Getting Help
1. Test bot locally with `python simple_bot.py`
2. Check browser console for web app errors
3. Verify all dependencies are installed
4. Ensure CSV data file is accessible

---

## 🎉 Ready to Deploy!

Your Gujarat Weather Alert System is clean, optimized, and ready for production:

🌐 **Web App**: Interactive map + admin panel  
🤖 **Bot**: @VillaegWarningbot hosted 24/7  
📊 **Data**: 33 districts, 235 talukas  
🚀 **Deployment**: Firebase, Railway, Heroku ready  

**Bot Link**: https://t.me/VillaegWarningbot