# Village Alert System - Deployment Guide

## 🚨 SECURITY FIRST
Your .env file has been removed from git tracking. **NEVER commit .env files!**

## Step 1: Prepare Your Environment

### Create .env file (locally only)
```
TELEGRAM_BOT_TOKEN=your_bot_token_here
ADMIN_EMAIL=your_admin_email
ADMIN_PASSWORD=your_secure_password
SECRET_KEY=your_secret_key_here
```

## Step 2: Deploy the Bot

### Option A: Railway (Recommended - Free tier available)

1. **Install Railway CLI**
   ```bash
   npm install -g @railway/cli
   ```

2. **Deploy Bot**
   ```bash
   railway login
   railway init
   railway up
   ```

3. **Set Environment Variables in Railway Dashboard**
   - Go to your Railway project dashboard
   - Add these variables:
     - `TELEGRAM_BOT_TOKEN`
     - `ADMIN_EMAIL`
     - `ADMIN_PASSWORD`
     - `SECRET_KEY`

4. **Set Start Command**
   - In Railway dashboard, set start command to: `python bot_host.py`

### Option B: Heroku

1. **Create Heroku App**
   ```bash
   heroku create your-bot-name
   ```

2. **Set Environment Variables**
   ```bash
   heroku config:set TELEGRAM_BOT_TOKEN=your_token
   heroku config:set ADMIN_EMAIL=your_email
   heroku config:set ADMIN_PASSWORD=your_password
   heroku config:set SECRET_KEY=your_secret
   ```

3. **Deploy**
   ```bash
   git push heroku main
   ```

## Step 3: Deploy the Website

### Option A: Railway (Separate Project)

1. **Create New Railway Project**
   ```bash
   railway init
   railway up
   ```

2. **Set Environment Variables**
   - `SECRET_KEY`
   - `ADMIN_EMAIL`
   - `ADMIN_PASSWORD`

3. **Set Start Command**
   - In Railway dashboard: `python app.py`

### Option B: Vercel (Free)

1. **Install Vercel CLI**
   ```bash
   npm install -g vercel
   ```

2. **Deploy**
   ```bash
   vercel
   ```

3. **Add Environment Variables in Vercel Dashboard**

## Step 4: Test Everything

1. **Test Bot**: Send `/start` to your Telegram bot
2. **Test Website**: Visit your deployed URL
3. **Test Alerts**: Try sending a test alert

## Quick Commands

```bash
# Remove .env from git (already done)
git rm --cached .env
git commit -m "Remove .env from version control"

# Deploy to Railway
railway login && railway up

# Deploy to Heroku
git push heroku main
```

## Troubleshooting

- **Bot not responding**: Check environment variables are set correctly
- **Website not loading**: Verify all dependencies in requirements.txt
- **Database errors**: Check if you need to set up a database connection

## Security Checklist

- [ ] .env file not in git
- [ ] Strong passwords used
- [ ] Environment variables set in hosting platform
- [ ] HTTPS enabled on website
- [ ] Bot token kept secure