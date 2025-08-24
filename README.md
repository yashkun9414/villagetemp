# Gujarat Weather & Fire Alert System

<div align="center">
  <img src="https://cdn-icons-png.flaticon.com/64/1163/1163661.png" alt="Weather" width="48" height="48">
  <img src="https://cdn-icons-png.flaticon.com/64/785/785116.png" alt="Fire" width="48" height="48">
  <img src="https://cdn-icons-png.flaticon.com/64/2111/2111644.png" alt="Telegram" width="48" height="48">
</div>

Real-time weather monitoring and fire alerts for Gujarat with NASA satellite data and Telegram notifications.

## Tech Stack

### Languages
![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=flat&logo=javascript&logoColor=black)
![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=flat&logo=html5&logoColor=white)
![CSS3](https://img.shields.io/badge/CSS3-1572B6?style=flat&logo=css3&logoColor=white)

### Frameworks & Libraries
![Flask](https://img.shields.io/badge/Flask-000000?style=flat&logo=flask&logoColor=white)
![Bootstrap](https://img.shields.io/badge/Bootstrap-7952B3?style=flat&logo=bootstrap&logoColor=white)
![Leaflet](https://img.shields.io/badge/Leaflet-199900?style=flat&logo=leaflet&logoColor=white)

### Services & APIs
![NASA MODIS](https://img.shields.io/badge/NASA_MODIS-0B3D91?style=flat&logo=nasa&logoColor=white)
![Telegram Bot API](https://img.shields.io/badge/Telegram_Bot-26A5E4?style=flat&logo=telegram&logoColor=white)
![Openmeteo API](https://img.shields.io/badge/Openmeteo_API-FA6E1E?style=flat&logo=weather&logoColor=white)

### Infrastructure
![Railway](https://img.shields.io/badge/Railway-0B0D0E?style=flat&logo=railway&logoColor=white)


---
## Key Features

* Fire detection (NASA MODIS)
* Interactive map (weather stations + fire incidents)
* Telegram bot notifications
* Mobile-friendly UI
* Coverage for 33 districts and 235 talukas

---

## Quick Start

### Web App

```bash
pip install -r requirements.txt
python app.py
# Open http://localhost:5000
```

### Telegram Bot

```bash
python simple_bot.py   # Local testing
python bot_host.py     # Production deployment
```

Bot link: [https://t.me/VillaegWarningbot](https://t.me/VillaegWarningbot)

---

## Bot Commands

| Command | Description |
|---------|-------------|
| `/start` | Welcome & help |
| `/subscribe` | Choose your area |
| `/weather` | Current weather |
| `/fire` | Fire alerts |
| `/stats` | Usage statistics |
| `/unsubscribe` | Stop alerts |

---

## Deployment

### Railway

* Connect GitHub repository
* Set start command: `python bot_host.py`
* Deploy instantly

---

## Configuration

Create a `.env` file:

```env

# Copy this file to .env and fill in your actual values
# NEVER commit the actual .env file to Git!

# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=your_bot_token_here

# Admin Panel Configuration
ADMIN_EMAIL=your_admin_email@example.com
ADMIN_PASSWORD=your_secure_password_here

# Application Security
SECRET_KEY=your_very_long_random_secret_key_here

# Optional: Port configuration
PORT=5000
```

## Dependencies

### Python Requirements
```
Flask==2.3.3
requests==2.31.0
python-telegram-bot==20.5
sqlite3
folium==0.14.0
python-dotenv==1.0.0
```

### External Services
- **NASA FIRMS API** - Real-time fire detection data
- **Openmeteo API** - Current weather conditions
- **Telegram Bot API** - Messaging and notifications
- **Railway** - Cloud hosting platform

## Usage

### For Users

1. Open [https://t.me/VillaegWarningbot](https://t.me/VillaegWarningbot)
2. Send `/start`
3. Use `/subscribe` to select your area
4. Use `/weather` and `/fire` for updates

### For Admins

1. Visit `/admin`
2. Sign in with admin credentials
3. Review the interactive map
4. Send targeted alerts

## Security

* Environment variables
* Admin authentication
* Input validation
* CSRF protection

## Coverage

* 33 districts (Gujarat)
* 235 talukas monitored
* 72,620 locations tracked
* NASA satellite data integration

## Support

* Bot: [https://t.me/VillaegWarningbot](https://t.me/VillaegWarningbot)
* Check hosting/logs for issues
