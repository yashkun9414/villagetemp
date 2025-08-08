# 🚀 Quick Start - Deploy in 5 Minutes

## ✅ Security Fixed
Your .env file is now secure and won't be committed to git.

## 📁 Your Project Structure
```
villagetemp/
├── app.py              # Website (Flask app)
├── bot_host.py         # Telegram bot
├── nasa_fire_fetcher.py # Fire data fetcher
├── requirements.txt    # Dependencies
├── .env               # Your secrets (LOCAL ONLY)
├── deploy.py          # Simple deployment script
└── DEPLOY.md          # Detailed guide
```

## 🎯 Deploy Now

### Step 1: Create .env file (if missing)
```bash
TELEGRAM_BOT_TOKEN=your_bot_token_here
ADMIN_EMAIL=your_admin_email
ADMIN_PASSWORD=your_secure_password
SECRET_KEY=your_secret_key_here
```

### Step 2: Run deployment script
```bash
python deploy.py
```

### Step 3: Choose what to deploy
- Option 1: Bot only
- Option 2: Website only  
- Option 3: Both

## 🔧 Manual Deployment

### Deploy Bot to Railway
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and deploy
railway login
railway init --name your-bot-name
railway up
```

### Deploy Website to Railway
```bash
# Create separate project
railway init --name your-website-name
railway up
```

## ⚠️ Important
After deployment, set environment variables in Railway dashboard:
- TELEGRAM_BOT_TOKEN
- ADMIN_EMAIL
- ADMIN_PASSWORD
- SECRET_KEY

## 🧪 Test
1. Send `/start` to your Telegram bot
2. Visit your website URL
3. Try sending a test alert

## 📖 Need Help?
Check `DEPLOY.md` for detailed instructions and troubleshooting.