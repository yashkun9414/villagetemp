# 🌐 Website Deployment Guide

## ✅ Template Error Fixed
The Jinja2 template syntax error has been fixed and the website is ready for deployment.

## 🚀 Deploy Website Now

### Option 1: Railway (Recommended)

1. **Go to Railway**
   - Visit [railway.app](https://railway.app)
   - Click "Start a New Project"

2. **Deploy from GitHub**
   - Choose "Deploy from GitHub repo"
   - Select: `amyashpal/villagetemp`
   - Railway will automatically detect it's a Python app

3. **Configure Settings**
   - **Start Command**: `python app.py`
   - **Port**: Railway will auto-detect (Flask uses PORT environment variable)

4. **Add Environment Variables**
   In Railway dashboard, add these variables:
   ```
   SECRET_KEY=village-alert-secret-key-2024
   ADMIN_EMAIL=admin@weatheralert.com
   ADMIN_PASSWORD=admin123
   ```

5. **Deploy**
   - Railway will automatically build and deploy
   - You'll get a URL like: `https://your-project-name.railway.app`

### Option 2: Heroku

1. **Create Heroku App**
   ```bash
   heroku create your-website-name
   ```

2. **Set Environment Variables**
   ```bash
   heroku config:set SECRET_KEY=village-alert-secret-key-2024
   heroku config:set ADMIN_EMAIL=admin@weatheralert.com
   heroku config:set ADMIN_PASSWORD=admin123
   ```

3. **Deploy**
   ```bash
   git push heroku main
   ```

## 🧪 Test Website Features

After deployment, test these features:

### 1. Homepage
- Visit your website URL
- Check the interactive map loads
- Verify district/taluka dropdowns work

### 2. Admin Panel
- Go to `/admin` or click "Admin Panel"
- Login with:
  - **Email**: `admin@weatheralert.com`
  - **Password**: `admin123`

### 3. Dashboard Features
- Send test alerts
- Check bot status
- View demo alerts

### 4. Static Files
- Verify CSS/JS loads properly
- Check map functionality
- Test responsive design

## 🔧 Troubleshooting

### Website Won't Load
- Check start command is `python app.py`
- Verify environment variables are set
- Check logs in hosting platform

### Admin Login Issues
- Verify `ADMIN_EMAIL` and `ADMIN_PASSWORD` environment variables
- Check `SECRET_KEY` is set

### Map Not Working
- Ensure CSV files are in the repository
- Check static files are being served
- Verify JavaScript console for errors

### Template Errors
- All template syntax errors have been fixed
- If you see Jinja2 errors, check template files

## 📊 Website Features

Your deployed website includes:

- **Interactive Map**: Shows Gujarat districts and talukas
- **Weather Data**: 72,620+ location records
- **Admin Panel**: Send alerts and manage system
- **Responsive Design**: Works on mobile and desktop
- **Bot Integration**: Links to your Telegram bot

## 🎉 Success!

Once deployed, your website will be live and users can:
- View weather data on interactive map
- Access admin panel for alerts
- Link to your Telegram bot
- Download location data

Your bot: https://t.me/VillaegWarningbot
Your website: [Your Railway/Heroku URL]