from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Email
from werkzeug.security import check_password_hash, generate_password_hash
import pandas as pd
import os
from dotenv import load_dotenv
import logging
# Translations removed - system uses English only

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# User class
class User(UserMixin):
    def __init__(self, id, email):
        self.id = id
        self.email = email

# Load CSV data
def load_taluka_data():
    try:
        df = pd.read_csv('merged_village_temperature_data.csv')
        talukas = df[['District Name', 'Taluka Name']].drop_duplicates().sort_values(['District Name', 'Taluka Name'])
        return talukas
    except Exception as e:
        logger.error(f"Error loading CSV data: {e}")
        return pd.DataFrame()

@login_manager.user_loader
def load_user(user_id):
    if user_id == "1":
        return User("1", os.getenv('ADMIN_EMAIL'))
    return None

# Forms
class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class AlertForm(FlaskForm):
    district = SelectField('District', choices=[], validators=[DataRequired()])
    taluka = SelectField('Taluka', choices=[], validators=[DataRequired()])
    message = TextAreaField('Alert Message', validators=[DataRequired()])
    submit = SubmitField('Send Alert')

# Bot status (managed separately)
bot_status = {"running": True, "error": None}

# Weather monitoring thresholds
TEMP_HOT_THRESHOLD = 40  # Celsius
TEMP_COLD_THRESHOLD = 5  # Celsius

def check_weather_alerts():
    """Check for real temperature alerts using Open-Meteo API"""
    try:
        from weather_api import get_weather_for_locations, WeatherAPI
        
        weather_data = get_weather_for_locations()
        alerts = []
        weather_api = WeatherAPI()
        
        for data in weather_data:
            if data:
                temp_alerts = weather_api.check_temperature_alerts(data, TEMP_HOT_THRESHOLD, TEMP_COLD_THRESHOLD)
                if temp_alerts:
                    for alert in temp_alerts:
                        alerts.append({
                            'type': alert['type'],
                            'district': data['location'],
                            'taluka': data['location'],
                            'temperature': alert['temperature'],
                            'max_temp': alert.get('max_temp', alert['temperature']),
                            'min_temp': alert.get('min_temp', alert['temperature']),
                            'severity': alert['severity'],
                            'message': alert['message'],
                            'timestamp': data['timestamp'],
                            'weather_description': data['weather_description'],
                            'humidity': data['humidity'],
                            'wind_speed': data['wind_speed']
                        })
        
        return alerts
    except Exception as e:
        logger.error(f"Error checking weather alerts: {e}")
        return []

# Routes
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/map')
def map_view():
    return render_template('index.html')

@app.route('/admin')
def admin_redirect():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        
        # Debug: Check environment variables
        admin_email = os.getenv('ADMIN_EMAIL', 'admin@weatheralert.com')
        admin_password = os.getenv('ADMIN_PASSWORD', 'admin123')
        
        logger.info(f"Login attempt: {email}")
        logger.info(f"Expected email: {admin_email}")
        
        if email == admin_email and password == admin_password:
            user = User("1", email)
            login_user(user)
            logger.info(f"Successful login for {email}")
            return redirect(url_for('dashboard'))
        else:
            logger.warning(f"Failed login attempt for {email}")
            flash('Invalid email or password. Use admin@weatheralert.com / admin123')
    
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    talukas = load_taluka_data()
    total_districts = talukas['District Name'].nunique()
    total_talukas = len(talukas)
    
    return render_template('dashboard_simple.html', 
                         total_districts=total_districts, 
                         total_talukas=total_talukas)

@app.route('/send_alert', methods=['GET', 'POST'])
@login_required
def send_alert():
    form = AlertForm()
    talukas = load_taluka_data()
    
    # Populate district choices
    districts = [(d, d) for d in talukas['District Name'].unique()]
    form.district.choices = [('', 'Select District')] + districts
    
    if form.validate_on_submit():
        district = form.district.data
        taluka = form.taluka.data
        message = form.message.data
        
        # Queue alert for bot to send
        try:
            from shared_data import queue_alert, get_subscribers_for_area
            
            # Check if there are subscribers
            subscribers = get_subscribers_for_area(district, taluka)
            
            if subscribers:
                # Queue the alert
                if queue_alert(district, taluka, message, "admin"):
                    flash(f'✅ Alert queued for {len(subscribers)} subscribers in {taluka}, {district}!', 'success')
                    logger.info(f"Alert queued: {district} -> {taluka}: {message}")
                else:
                    flash('❌ Failed to queue alert. Please try again.', 'error')
            else:
                flash(f'⚠️ No subscribers found for {taluka}, {district}', 'warning')
                
        except Exception as e:
            logger.error(f"Error queuing alert: {e}")
            flash('❌ Error sending alert. Please try again.', 'error')
        
        return redirect(url_for('send_alert'))
    
    return render_template('send_alert.html', form=form)

@app.route('/get_talukas/<district>')
@login_required
def get_talukas(district):
    talukas = load_taluka_data()
    district_talukas = talukas[talukas['District Name'] == district]['Taluka Name'].unique()
    return jsonify([{'value': t, 'text': t} for t in district_talukas])

@app.route('/get_subscriber_count/<district>/<taluka>')
@login_required
def get_subscriber_count(district, taluka):
    """Get subscriber count for specific district/taluka"""
    try:
        from shared_data import get_subscribers_for_area
        
        subscribers = get_subscribers_for_area(district, taluka)
        count = len(subscribers) if subscribers else 0
        
        return jsonify({
            'success': True,
            'count': count,
            'district': district,
            'taluka': taluka
        })
        
    except Exception as e:
        logger.error(f"Error getting subscriber count: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to get subscriber count'
        })

@app.route('/demo_alerts')
@login_required
def demo_alerts():
    try:
        from shared_data import get_subscribers_for_area, load_subscribers
        
        demo_alerts = [
            {
                'type': 'High Temperature',
                'message': 'Temperature alert: Expected high temperature of 45°C in your area today. Stay hydrated and avoid outdoor activities!',
                'district': 'AHMADABAD',
                'taluka': 'Bavla'
            },
            {
                'type': 'Fire Risk',
                'message': 'Fire risk alert: High fire risk due to dry conditions. Avoid outdoor burning and report any smoke immediately.',
                'district': 'RAJKOT',
                'taluka': 'Gondal'
            },
            {
                'type': 'Weather Warning',
                'message': 'Weather warning: Strong winds expected (40+ km/h). Secure loose objects and avoid travel if possible.',
                'district': 'SURAT',
                'taluka': 'Bardoli'
            },
            {
                'type': 'Cold Wave',
                'message': 'Cold wave alert: Temperature expected to drop below 5°C. Protect crops and livestock from cold.',
                'district': 'BANASKANTHA',
                'taluka': 'Deesa'
            },
            {
                'type': 'Heavy Rain',
                'message': 'Heavy rainfall alert: 50+ mm rain expected in next 24 hours. Avoid waterlogged areas.',
                'district': 'VALSAD',
                'taluka': 'Valsad'
            }
        ]
        
        # Add subscriber count for each alert
        for alert in demo_alerts:
            subscribers = get_subscribers_for_area(alert['district'], alert['taluka'])
            alert['subscriber_count'] = len(subscribers) if subscribers else 0
        
        # Get overall subscriber statistics
        all_subscribers = load_subscribers()
        total_subscribers = sum(len(users) for users in all_subscribers.values())
        areas_with_subscribers = len([k for k, v in all_subscribers.items() if v])
        
        return render_template('demo_alerts.html', 
                             alerts=demo_alerts,
                             total_subscribers=total_subscribers,
                             areas_with_subscribers=areas_with_subscribers)
        
    except Exception as e:
        logger.error(f"Error loading demo alerts: {e}")
        # Fallback to basic alerts without subscriber info
        demo_alerts = [
            {
                'type': 'High Temperature',
                'message': 'Temperature alert: Expected high temperature of 45°C in your area today. Stay hydrated!',
                'district': 'AHMADABAD',
                'taluka': 'Bavla',
                'subscriber_count': 0
            }
        ]
        return render_template('demo_alerts.html', 
                             alerts=demo_alerts,
                             total_subscribers=0,
                             areas_with_subscribers=0)

@app.route('/send_demo_alert', methods=['POST'])
@login_required
def send_demo_alert():
    data = request.get_json()
    district = data.get('district')
    taluka = data.get('taluka')
    message = data.get('message')
    
    try:
        from shared_data import queue_alert, get_subscribers_for_area
        
        # Check if there are subscribers for this area
        subscribers = get_subscribers_for_area(district, taluka)
        
        if subscribers:
            # Queue the demo alert
            if queue_alert(district, taluka, f"🧪 DEMO ALERT:\n\n{message}", "demo"):
                logger.info(f"Demo alert queued: {district} -> {taluka}: {message}")
                return jsonify({
                    'success': True,
                    'message': f'Demo alert sent to {len(subscribers)} subscribers in {taluka}, {district}',
                    'subscriber_count': len(subscribers)
                })
            else:
                return jsonify({
                    'success': False,
                    'error': 'Failed to queue demo alert'
                })
        else:
            return jsonify({
                'success': False,
                'error': f'No subscribers found for {taluka}, {district}. Ask users to subscribe first using /subscribe command.',
                'subscriber_count': 0
            })
            
    except Exception as e:
        logger.error(f"Error sending demo alert: {e}")
        return jsonify({
            'success': False,
            'error': f'System error: {str(e)}'
        })

@app.route('/bot_status')
@login_required
def get_bot_status():
    return jsonify(bot_status)

@app.route('/restart_bot', methods=['POST'])
@login_required
def restart_bot():
    # Bot runs separately, just return success
    return jsonify({'success': True, 'status': bot_status})

@app.route('/weather_alerts')
@login_required
def get_weather_alerts():
    """Get current weather alerts"""
    alerts = check_weather_alerts()
    return jsonify({'alerts': alerts})

@app.route('/send_weather_alert', methods=['POST'])
@login_required
def send_weather_alert():
    """Send weather alert to subscribers"""
    data = request.get_json()
    alert = data.get('alert')
    
    try:
        from shared_data import queue_alert, get_subscribers_for_area
        
        district = alert['district']
        taluka = alert['taluka']
        message = alert['message']
        
        # Check if there are subscribers
        subscribers = get_subscribers_for_area(district, taluka)
        
        if subscribers:
            # Queue the weather alert
            if queue_alert(district, taluka, message, "weather"):
                logger.info(f"Weather alert queued: {district} -> {taluka}: {message}")
                return jsonify({
                    'success': True, 
                    'message': f'Weather alert queued for {len(subscribers)} subscribers!'
                })
            else:
                return jsonify({'success': False, 'message': 'Failed to queue alert'})
        else:
            return jsonify({
                'success': False, 
                'message': f'No subscribers found for {taluka}, {district}'
            })
            
    except Exception as e:
        logger.error(f"Error queuing weather alert: {e}")
        return jsonify({'success': False, 'message': 'Error sending alert'})

@app.route('/weather/<district>/<taluka>')
def get_taluka_weather(district, taluka):
    """Get real weather data for specific taluka"""
    try:
        from weather_api import get_weather_for_taluka
        
        weather_data = get_weather_for_taluka(district, taluka)
        if weather_data:
            return jsonify({
                'success': True,
                'weather': weather_data
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Weather data not available for this location'
            })
    except Exception as e:
        logger.error(f"Error getting weather for {taluka}, {district}: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to fetch weather data'
        })

@app.route('/api/weather_map_data')
def weather_map_data():
    """Get weather data for map display"""
    try:
        from weather_api import get_weather_for_locations
        
        weather_data = get_weather_for_locations()
        return jsonify({
            'success': True,
            'locations': weather_data
        })
    except Exception as e:
        logger.error(f"Error getting map weather data: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to fetch weather data'
        })

@app.route('/api/fire_data')
def fire_data():
    """Get fire incident data for map display"""
    try:
        # Try to load fire data from multiple locations
        fire_files = [
            'static/gujarat_fire_history.csv',
            'gujarat_fire_history.csv'
        ]
        
        fire_df = None
        for fire_file in fire_files:
            try:
                fire_df = pd.read_csv(fire_file)
                break
            except FileNotFoundError:
                continue
        
        if fire_df is None or fire_df.empty:
            return jsonify({
                'success': True,
                'fire_incidents': [],
                'message': 'No fire incidents currently detected in Gujarat'
            })
        
        # Filter for recent incidents only (last 7 days)
        from datetime import datetime, timedelta
        week_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        
        # Filter recent incidents
        recent_fires = fire_df[fire_df['acq_date'] >= week_ago]
        
        if recent_fires.empty:
            return jsonify({
                'success': True,
                'fire_incidents': [],
                'message': 'No recent fire incidents in Gujarat (last 7 days)'
            })
        
        # Convert to list of dictionaries for JSON response
        fire_incidents = []
        for _, row in recent_fires.iterrows():
            # Skip invalid coordinates
            lat = float(row.get('latitude', 0))
            lon = float(row.get('longitude', 0))
            
            if lat == 0 or lon == 0:
                continue
                
            incident = {
                'latitude': lat,
                'longitude': lon,
                'district': str(row.get('district', 'Unknown')),
                'taluka': str(row.get('taluka', 'Unknown')),
                'fire_type': str(row.get('fire_type', 'Vegetation')),
                'severity': str(row.get('severity', 'Medium')),
                'confidence': int(row.get('confidence', 0)),
                'area_affected': float(row.get('area_affected', 0)),
                'date': str(row.get('acq_date', '')),
                'time': str(row.get('acq_time', ''))
            }
            fire_incidents.append(incident)
        
        return jsonify({
            'success': True,
            'fire_incidents': fire_incidents,
            'message': f'{len(fire_incidents)} fire incidents in last 7 days' if fire_incidents else 'No recent fire incidents detected'
        })
        
    except Exception as e:
        logger.error(f"Error getting fire data: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to fetch fire data'
        })

@app.route('/api/subscriber_stats')
@login_required
def subscriber_stats():
    """Get subscriber statistics"""
    try:
        from shared_data import load_subscribers
        
        subscribers = load_subscribers()
        total_subscribers = sum(len(users) for users in subscribers.values())
        areas_with_subscribers = len([k for k, v in subscribers.items() if v])
        
        # Get top subscribed areas
        top_areas = []
        for key, users in subscribers.items():
            if users:
                district, taluka = key.split('_', 1)
                top_areas.append({
                    'district': district,
                    'taluka': taluka,
                    'count': len(users)
                })
        
        top_areas.sort(key=lambda x: x['count'], reverse=True)
        
        return jsonify({
            'success': True,
            'total_subscribers': total_subscribers,
            'areas_with_subscribers': areas_with_subscribers,
            'top_areas': top_areas[:10]
        })
        
    except Exception as e:
        logger.error(f"Error getting subscriber stats: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to get subscriber stats'
        })

@app.route('/subscribers')
@login_required
def view_subscribers():
    """View all subscribers"""
    try:
        from shared_data import load_subscribers
        
        subscribers = load_subscribers()
        
        # Convert to list format for display
        subscriber_list = []
        for key, users in subscribers.items():
            if users:
                district, taluka = key.split('_', 1)
                subscriber_list.append({
                    'district': district,
                    'taluka': taluka,
                    'count': len(users),
                    'user_ids': users
                })
        
        # Sort by subscriber count (descending)
        subscriber_list.sort(key=lambda x: x['count'], reverse=True)
        
        total_subscribers = sum(len(users) for users in subscribers.values())
        
        return render_template('subscribers.html', 
                             subscribers=subscriber_list,
                             total_subscribers=total_subscribers)
        
    except Exception as e:
        logger.error(f"Error loading subscribers: {e}")
        flash('Error loading subscriber data', 'error')
        return redirect(url_for('dashboard'))

@app.route('/api/fire_alerts/<district>/<taluka>')
def get_fire_alerts_for_area(district, taluka):
    """Get fire alerts for specific district/taluka"""
    try:
        fire_df = pd.read_csv('static/gujarat_fire_history.csv')
        
        # Filter for the specific area and recent incidents (last 7 days)
        from datetime import datetime, timedelta
        week_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        
        area_fires = fire_df[
            (fire_df['district'] == district) & 
            (fire_df['taluka'] == taluka) &
            (fire_df['acq_date'] >= week_ago)
        ]
        
        alerts = []
        for _, fire in area_fires.iterrows():
            alert = {
                'date': fire.get('acq_date', ''),
                'latitude': float(fire.get('latitude', 0)),
                'longitude': float(fire.get('longitude', 0)),
                'fire_type': fire.get('fire_type', 'Vegetation'),
                'severity': fire.get('severity', 'Medium'),
                'confidence': int(fire.get('confidence', 0)),
                'area_affected': float(fire.get('area_affected', 0))
            }
            alerts.append(alert)
        
        return jsonify({
            'success': True,
            'alerts': alerts,
            'count': len(alerts)
        })
        
    except Exception as e:
        logger.error(f"Error getting fire alerts for {district}/{taluka}: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to get fire alerts'
        })

if __name__ == '__main__':
    # For local development
    app.run(debug=True, port=int(os.environ.get('PORT', 5000)), host='0.0.0.0')