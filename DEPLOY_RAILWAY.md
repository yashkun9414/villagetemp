# 🚀 Railway Deployment Guide

## 🤖 Deploy Bot

### Step 1: Create Bot Project
1. Go to [railway.app](https://railway.app)
2. **New Project** → **Deploy from GitHub repo**
3. Select: `amyashpal/villagetemp`
4. **Settings** → **Deploy**
5. **Start Command**: `python bot_host.py`

### Step 2: Set Environment Variables
Add these in Railway dashboard:
```
TELEGRAM_BOT_TOKEN=8235992714:AAED7tTjm6waV6Ak-L-_LgRz37ZfnuEnE4w
```

### Step 3: Deploy
Click **Deploy** - bot will be live at https://t.me/VillaegWarningbot

## 🌐 Deploy Website (Separate Project)

### Step 1: Create Website Project
1. **New Project** → **Deploy from GitHub repo**
2. Select: `amyashpal/villagetemp`
3. **Start Command**: `python app.py`

### Step 2: Set Environment Variables
```
SECRET_KEY=village-alert-secret-key-2024
ADMIN_EMAIL=admin@weatheralert.com
ADMIN_PASSWORD=admin123
```

## ✅ Test System
1. **Bot**: Go to https://t.me/VillaegWarningbot → Send `/start`
2. **Website**: Login with admin@weatheralert.com / admin123
3. **Alerts**: Subscribe to area via bot, send alert via website

## 🔧 Files Used
- **Bot**: `bot_host.py`, `shared_data.py`, `weather_api.py`
- **Website**: `app.py`, `templates/`, `shared_data.py`
- **Data**: `merged_village_temperature_data.csv`, `subscribers.json`

Bot processes alerts when users interact - no job queue needed!