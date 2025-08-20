# 🚀 Deployment Guide - Gujarat Weather & Fire Alert System

This guide covers deploying the enhanced system with NASA fire data integration and automated scheduling.

## 📋 Pre-deployment Checklist

### Required Environment Variables
```env
# Core Application
SECRET_KEY=your-secret-key-here
ADMIN_EMAIL=admin@weatheralert.com
ADMIN_PASSWORD=secure-admin-password

# Telegram Bot
TELEGRAM_BOT_TOKEN=your-bot-token-from-botfather
ADMIN_TELEGRAM_ID=your-telegram-user-id

# Optional
RAILWAY_ENVIRONMENT=true  # For Railway deployment
DYNO=true                 # For Heroku deployment
```

### Required Files
- ✅ `merged_village_temperature_data.csv` (location data)
- ✅ `gujarat_fire_history.csv` (will be created automatically)
- ✅ `subscribers.json` (will be created automatically)
- ✅ `pending_alerts.json` (will be created automatically)

## 🌐 Web Application Deployment

### Option 1: Railway (Recommended)
```bash
# 1. Connect GitHub repository to Railway
# 2. Set environment variables in Railway dashboard
# 3. Deploy automatically

# Railway will use Procfile:
web: gunicorn app:app --bind 0.0.0.0:$PORT
```

### Option 2: Heroku
```bash
# 1. Create Heroku app
heroku create your-app-name

# 2. Set environment variables
heroku config:set SECRET_KEY=your-secret-key
heroku config:set ADMIN_EMAIL=admin@weatheralert.com
heroku config:set ADMIN_PASSWORD=secure-password

# 3. Deploy
git push heroku main
```

### Option 3: Google Cloud Run
```bash
# 1. Build container
gcloud builds submit --tag gcr.io/PROJECT-ID/weather-alert

# 2. Deploy
gcloud run deploy --image gcr.io/PROJECT-ID/weather-alert --platform managed
```

## 🤖 Telegram Bot Deployment

### Option 1: Railway (Separate Service)
```bash
# 1. Create new Railway service
# 2. Use Procfile.bot:
bot: python bot_host.py

# 3. Set same environment variables as web app
# 4. Deploy bot service
```

### Option 2: Heroku (Separate App)
```bash
# 1. Create separate Heroku app for bot
heroku create your-bot-name

# 2. Set environment variables
heroku config:set TELEGRAM_BOT_TOKEN=your-token
heroku config:set ADMIN_TELEGRAM_ID=your-id

# 3. Use Procfile.bot and deploy
git push heroku-bot main
```

### Option 3: VPS/Server
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run bot with systemd service
sudo systemctl enable weather-bot
sudo systemctl start weather-bot
```

## 🔥 Fire Data Automation

### Option 1: Cron Job (Linux/Mac)
```bash
# Add to crontab (crontab -e)
0 6,18 * * * cd /path/to/project && python nasa_fire_fetcher.py
```

### Option 2: Windows Task Scheduler
```powershell
# Create scheduled task to run nasa_fire_fetcher.py twice daily
schtasks /create /tn "NASA Fire Fetch" /tr "python C:\path\to\nasa_fire_fetcher.py" /sc daily /st 06:00
```

### Option 3: Cloud Scheduler (Google Cloud)
```yaml
# cloud-scheduler.yaml
name: nasa-fire-fetch
schedule: "0 6,18 * * *"
target:
  httpTarget:
    uri: https://your-app.com/api/fetch-fire-data
    httpMethod: POST
```

### Option 4: Railway Cron (if supported)
```bash
# Use Railway's cron addon or external service like cron-job.org
# URL to trigger: https://your-app.com/api/fetch-fire-data
```

## 📊 Database Setup (Optional)

### SQLite (Default)
- No setup required
- Files created automatically
- Good for small to medium deployments

### PostgreSQL (Production)
```python
# Update shared_data.py to use PostgreSQL
import psycopg2
DATABASE_URL = os.getenv('DATABASE_URL')
```

### MongoDB (Alternative)
```python
# Update shared_data.py to use MongoDB
import pymongo
MONGODB_URI = os.getenv('MONGODB_URI')
```

## 🔧 Configuration Examples

### Railway Configuration
```json
{
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "gunicorn app:app --bind 0.0.0.0:$PORT",
    "healthcheckPath": "/",
    "healthcheckTimeout": 100
  }
}
```

### Heroku Configuration
```json
{
  "name": "gujarat-weather-alert",
  "description": "Weather and Fire Alert System for Gujarat",
  "repository": "https://github.com/yourusername/gujarat-weather-alert",
  "keywords": ["weather", "fire", "alerts", "telegram", "gujarat"],
  "env": {
    "SECRET_KEY": {
      "description": "Secret key for Flask application"
    },
    "TELEGRAM_BOT_TOKEN": {
      "description": "Telegram bot token from BotFather"
    }
  },
  "formation": {
    "web": {
      "quantity": 1,
      "size": "basic"
    }
  },
  "addons": [
    "heroku-postgresql:hobby-dev"
  ]
}
```

### Docker Configuration
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 5000
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:5000"]
```

## 🚨 Monitoring & Alerts

### Health Checks
```python
# Add to app.py
@app.route('/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'fire_data_age': get_fire_data_age(),
        'bot_status': check_bot_status()
    })
```

### Log Monitoring
```bash
# Railway logs
railway logs

# Heroku logs
heroku logs --tail

# Local logs
tail -f fire_scheduler.log
```

### Uptime Monitoring
- Use services like UptimeRobot, Pingdom, or StatusCake
- Monitor both web app and bot endpoints
- Set up alerts for downtime

## 🔒 Security Considerations

### Environment Variables
- Never commit `.env` files
- Use platform-specific secret management
- Rotate tokens regularly

### API Rate Limits
- NASA FIRMS: No strict limits, but be respectful
- Telegram Bot API: 30 messages/second
- Open-Meteo: 10,000 requests/day free

### Data Privacy
- Store minimal user data
- Implement data retention policies
- Provide user data deletion options

## 📈 Scaling Considerations

### High Traffic
- Use Redis for caching
- Implement database connection pooling
- Consider CDN for static files

### Multiple Regions
- Deploy in multiple regions
- Use load balancers
- Implement data replication

### Performance Optimization
- Optimize CSV loading
- Cache weather data
- Use async processing for alerts

## 🛠️ Troubleshooting

### Common Issues

#### Bot Not Responding
```bash
# Check bot token
python -c "import requests; print(requests.get('https://api.telegram.org/bot{TOKEN}/getMe').json())"

# Check bot hosting
curl https://your-bot-service.com/health
```

#### Fire Data Not Updating
```bash
# Manual fire data fetch
python nasa_fire_fetcher.py

# Check NASA FIRMS availability
curl "https://firms.modaps.eosdis.nasa.gov/data/active_fire/c6/csv/MODIS_C6_1_Global_24h.csv"
```

#### Map Not Loading
- Check CSV file accessibility
- Verify static file serving
- Check browser console for errors

### Debug Mode
```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Run with debug
python app.py --debug
```

## 📞 Support

### Documentation
- Main README.md
- Code comments
- API documentation

### Community
- GitHub Issues
- Telegram bot help: `/help`
- Admin dashboard support

### Professional Support
- Custom deployment assistance
- Feature development
- System optimization

---

## ✅ Deployment Checklist

- [ ] Environment variables configured
- [ ] CSV data files uploaded
- [ ] Web application deployed and accessible
- [ ] Telegram bot deployed and responding
- [ ] Fire data automation configured
- [ ] Health checks implemented
- [ ] Monitoring set up
- [ ] Security measures in place
- [ ] Documentation updated
- [ ] Team trained on system usage

**🎉 Your Gujarat Weather & Fire Alert System is ready for production!**