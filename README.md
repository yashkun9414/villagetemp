
---

# Gujarat Weather & Fire Alert System

Real-time weather monitoring and fire alerts for Gujarat with NASA satellite data and Telegram notifications.

## Key Features

* Fire detection (NASA MODIS)
* Interactive map (weather stations + fire incidents)
* Telegram bot notifications
* Mobile-friendly UI
* Coverage for 33 districts and 235 talukas

## Quick Start

### Web App

```bash
pip install -r requirements.txt
python app.py
# open http://localhost:5000
```

### Telegram Bot

```bash
python simple_bot.py   # local test
python bot_host.py     # production
```

Bot link: [https://t.me/VillaegWarningbot](https://t.me/VillaegWarningbot)


## Bot Commands

| Command      | Description      |
| ------------ | ---------------- |
| /start       | Welcome & help   |
| /subscribe   | Choose your area |
| /weather     | Current weather  |
| /fire        | Fire alerts      |
| /stats       | Usage statistics |
| /unsubscribe | Stop alerts      |

## Deployment 

### Railway

* Connect GitHub
* Set start command to `python bot_host.py`
* Deploy


## Configuration

Create a `.env` file:

```env
TELEGRAM_BOT_TOKEN=your_token_here
ADMIN_EMAIL=admin@weatheralert.com
ADMIN_PASSWORD=admin123
```

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
* NASA satellite integration

## Support

* Bot: [https://t.me/VillaegWarningbot](https://t.me/VillaegWarningbot)
* Check hosting/logs for issues
* Optimized for mobile and fast loading

---
