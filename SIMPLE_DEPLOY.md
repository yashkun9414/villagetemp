# 🚀 Simple Deployment Guide

## ✅ Your Bot Token: `8235992714:AAED7tTjm6waV6Ak-L-_LgRz37ZfnuEnE4w`

## Step 1: Deploy Bot to Railway (Easiest)

### 1.1 Push to GitHub
```bash
git add .
git commit -m "Ready for deployment"
git push origin main
```

### 1.2 Deploy on Railway
1. Go to [railway.app](https://railway.app)
2. Click "Start a New Project"
3. Choose "Deploy from GitHub repo"
4. Select your repository: `amyashpal/villagetemp`
5. Railway will auto-deploy

### 1.3 Set Environment Variables in Railway
In Railway dashboard, add these variables:
- `TELEGRAM_BOT_TOKEN` = `8235992714:AAED7tTjm6waV6Ak-L-_LgRz37ZfnuEnE4w`
- `ADMIN_EMAIL` = `admin@weatheralert.com`
- `ADMIN_PASSWORD` = `admin123`
- `SECRET_KEY` = `village-alert-secret-key-2024`

### 1.4 Set Start Command
In Railway settings, set start command to: `python bot_host.py`

## Step 2: Deploy Website (Separate Project)

### 2.1 Create New Railway Project
1. Go to railway.app
2. Create another new project from same GitHub repo
3. Set start command to: `python app.py`
4. Add same environment variables

## Alternative: Heroku Deployment

### Bot Deployment
```bash
# Create Heroku app for bot
heroku create your-bot-name

# Set environment variables
heroku config:set TELEGRAM_BOT_TOKEN=8235992714:AAED7tTjm6waV6Ak-L-_LgRz37ZfnuEnE4w
heroku config:set ADMIN_EMAIL=admin@weatheralert.com
heroku config:set ADMIN_PASSWORD=admin123
heroku config:set SECRET_KEY=village-alert-secret-key-2024

# Deploy
git push heroku main
```

### Website Deployment
```bash
# Create Heroku app for website
heroku create your-website-name

# Set same environment variables
heroku config:set SECRET_KEY=village-alert-secret-key-2024
heroku config:set ADMIN_EMAIL=admin@weatheralert.com
heroku config:set ADMIN_PASSWORD=admin123

# Deploy
git push heroku main
```

## 🧪 Test Bot Locally First
```bash
python bot_host.py
```

## 🌐 Test Website Locally
```bash
python app.py
```

## ✅ Your Bot Link
After deployment, your bot will be available at:
**https://t.me/VillaegWarningbot**

## 🔧 Troubleshooting
- If bot doesn't respond: Check environment variables
- If website doesn't load: Check start command is `python app.py`
- If data missing: Ensure CSV files are in repository