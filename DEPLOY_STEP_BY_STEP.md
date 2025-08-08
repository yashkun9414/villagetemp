# 🚀 Step-by-Step Deployment Guide

## 📋 What We're Deploying:
1. **🌐 Web App** - Interactive map + admin panel
2. **🤖 Telegram Bot** - @VillaegWarningbot (24/7)
3. **🛰️ NASA Fire Data** - Automatic daily updates

---

## 🌐 STEP 1: Deploy Web App (5 minutes)

### Option A: Firebase (Recommended)

#### 1.1 Install Firebase CLI
```bash
# Install Node.js first (if not installed)
# Download from: https://nodejs.org

# Install Firebase CLI
npm install -g firebase-tools
```

#### 1.2 Login to Firebase
```bash
firebase login
```
- Opens browser
- Sign in with Google account
- Allow Firebase CLI access

#### 1.3 Initialize Firebase Project
```bash
# In your project folder
firebase init

# Select:
# - Hosting: Configure files for Firebase Hosting
# - Use existing project or create new one
# - Public directory: . (current directory)
# - Single-page app: No
# - Overwrite index.html: No
```

#### 1.4 Deploy
```bash
firebase deploy
```

#### 1.5 Your Web App is Live! 🎉
- URL: `https://your-project-id.web.app`
- Admin: `https://your-project-id.web.app/admin`
- Login: `admin@weatheralert.com` / `admin123`

### Option B: Vercel (Alternative)

#### 1.1 Install Vercel CLI
```bash
npm install -g vercel
```

#### 1.2 Deploy
```bash
vercel
```
- Follow prompts
- Connect to GitHub (optional)
- Your app is live!

---

## 🤖 STEP 2: Deploy Telegram Bot (5 minutes)

### Option A: Railway (Recommended - Free $5/month)

#### 2.1 Prepare Your Code
Make sure these files exist:
- ✅ `bot_host.py` (main bot file)
- ✅ `requirements.txt` (dependencies)
- ✅ `Procfile` (should contain: `web: python bot_host.py`)

#### 2.2 Push to GitHub
```bash
# If not already on GitHub:
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/yourusername/your-repo.git
git push -u origin main
```

#### 2.3 Deploy on Railway
1. **Go to [railway.app](https://railway.app)**
2. **Click "Start a New Project"**
3. **Select "Deploy from GitHub repo"**
4. **Sign in with GitHub**
5. **Select your repository**
6. **Railway automatically:**
   - Detects Python
   - Installs requirements.txt
   - Runs bot_host.py
   - Keeps bot online 24/7

#### 2.4 Set Environment Variables
1. **In Railway dashboard, click your project**
2. **Go to "Variables" tab**
3. **Add these variables:**
   ```
   TELEGRAM_BOT_TOKEN=8235992714:AAED7tTjm6waV6Ak-L-_LgRz37ZfnuEnE4w
   PORT=8080
   ```

#### 2.5 Your Bot is Live! 🎉
- Bot: `@VillaegWarningbot`
- Link: `https://t.me/VillaegWarningbot`
- Status: Running 24/7

### Option B: Heroku (Alternative - $7/month)

#### 2.1 Install Heroku CLI
Download from: https://devcenter.heroku.com/articles/heroku-cli

#### 2.2 Deploy
```bash
# Login
heroku login

# Create app
heroku create your-bot-name

# Set environment variables
heroku config:set TELEGRAM_BOT_TOKEN=8235992714:AAED7tTjm6waV6Ak-L-_LgRz37ZfnuEnE4w

# Deploy
git push heroku main
```

---

## 🛰️ STEP 3: Setup NASA Fire Data (2 minutes)

### 3.1 GitHub Actions (Already Configured!)
The system automatically:
- Runs daily at 6 AM UTC
- Downloads NASA fire data
- Updates your repository
- No manual work needed!

### 3.2 Manual Test (Optional)
```bash
# Test NASA fire data locally
python nasa_fire_fetcher.py

# Should show:
# ✅ Downloaded X global fire records
# 🔥 Found X fire incidents in Gujarat
```

### 3.3 Manual Trigger (If Needed)
1. Go to your GitHub repository
2. Click "Actions" tab
3. Select "Daily NASA Fire Data Update"
4. Click "Run workflow"

---

## 🧪 STEP 4: Test Everything (3 minutes)

### 4.1 Test Web App
1. **Visit your Firebase URL**
2. **Check map loads with Gujarat data**
3. **Test admin login:**
   - Go to `/admin`
   - Email: `admin@weatheralert.com`
   - Password: `admin123`
4. **Verify mobile responsiveness**

### 4.2 Test Telegram Bot
1. **Open Telegram**
2. **Search: `@VillaegWarningbot`**
3. **Send: `/start`**
4. **Should get welcome message immediately**
5. **Test commands:**
   - `/subscribe` - Choose district/taluka
   - `/fire` - Check fire alerts
   - `/mystatus` - Check subscription
   - `/help` - Get help

### 4.3 Test Fire Data Integration
1. **Subscribe to an area via bot**
2. **Use `/fire` command**
3. **Should show NASA fire data**
4. **Check web app shows fire incidents on map**

---

## ✅ STEP 5: Verification Checklist

### Web App ✅
- [ ] Loads at your deployed URL
- [ ] Interactive map displays Gujarat
- [ ] Admin panel login works
- [ ] Fire data visible on map
- [ ] Mobile responsive

### Telegram Bot ✅
- [ ] @VillaegWarningbot responds instantly
- [ ] All commands work (/start, /subscribe, /fire, etc.)
- [ ] Users can subscribe to locations
- [ ] Fire alerts show real NASA data
- [ ] Bot stays online 24/7

### NASA Fire Data ✅
- [ ] `gujarat_fire_history.csv` exists
- [ ] Contains real NASA fire incidents
- [ ] GitHub Actions runs daily
- [ ] Bot shows fire alerts
- [ ] Web app displays fire data

---

## 🎯 STEP 6: Share with Users

### For End Users:
**Telegram Bot**: https://t.me/VillaegWarningbot

**Instructions for users:**
1. Search `@VillaegWarningbot` on Telegram
2. Send `/start` to begin
3. Use `/subscribe` to choose your area
4. Get weather and fire alerts automatically
5. Use `/fire` to check recent fire incidents

### For Administrators:
**Web App**: Your Firebase/Vercel URL
**Admin Panel**: Your-URL/admin
**Login**: admin@weatheralert.com / admin123

---

## 🔧 STEP 7: Troubleshooting

### Web App Not Loading:
```bash
# Check Firebase deployment
firebase hosting:channel:list

# Redeploy if needed
firebase deploy
```

### Bot Not Responding:
```bash
# Check Railway logs
# Go to Railway dashboard → Your project → Deployments → View logs

# Test bot token
curl https://api.telegram.org/bot8235992714:AAED7tTjm6waV6Ak-L-_LgRz37ZfnuEnE4w/getMe
```

### Fire Data Not Updating:
```bash
# Check GitHub Actions
# Go to GitHub → Actions → View workflow runs

# Manual trigger if needed
# Actions → Daily NASA Fire Data Update → Run workflow
```

---

## 💰 STEP 8: Cost Summary

### Free Options:
- **Firebase**: Free tier (sufficient for small apps)
- **GitHub Actions**: Free for public repositories
- **NASA Data**: Free (public data)

### Paid Options:
- **Railway**: $5/month (for bot hosting)
- **Heroku**: $7/month (alternative for bot)

### Recommended Setup: ~$5/month
- Web App: Firebase (Free)
- Bot: Railway ($5/month)
- Fire Data: GitHub Actions (Free)

---

## 🎉 STEP 9: Success!

### You Now Have:
🌐 **Live Web App** with interactive Gujarat map  
🤖 **24/7 Telegram Bot** with fire alerts  
🛰️ **Real NASA Fire Data** updated daily  
📱 **Mobile-Friendly** interface  
⚡ **Production-Ready** system  

### Live URLs:
- **Web App**: `https://your-project.web.app`
- **Bot**: `https://t.me/VillaegWarningbot`
- **Admin**: `https://your-project.web.app/admin`

### Your system is now serving the Gujarat community with:
- Real-time weather alerts
- NASA satellite fire data
- Location-based notifications
- 24/7 availability

**Congratulations! Your Gujarat Weather Alert System is live!** 🌡️🔥🛰️

---

## 📞 STEP 10: Support

### If You Need Help:
1. **Check the logs** in Railway/Firebase dashboard
2. **Test locally** first: `python bot_host.py`
3. **Verify environment variables** are set correctly
4. **Check GitHub Actions** for fire data updates

### Common Issues:
- **Bot not responding**: Check Railway environment variables
- **Map not loading**: Ensure CSV files are in static folder
- **Admin login fails**: Verify credentials in .env file
- **Fire data missing**: Check GitHub Actions workflow

**Your system is now ready to protect the people of Gujarat!** 🛡️👥