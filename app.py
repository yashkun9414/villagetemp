from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Email
from werkzeug.security import check_password_hash, generate_password_hash
import pandas as pd
import os
from dotenv import load_dotenv
import logging

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
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
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
        
        # Alert functionality (bot runs separately)
        flash(f'Alert would be sent to {taluka}, {district}: {message}')
        logger.info(f"Alert request: {district} -> {taluka}: {message}")
        
        return redirect(url_for('send_alert'))
    
    return render_template('send_alert.html', form=form)

@app.route('/get_talukas/<district>')
@login_required
def get_talukas(district):
    talukas = load_taluka_data()
    district_talukas = talukas[talukas['District Name'] == district]['Taluka Name'].unique()
    return jsonify([{'value': t, 'text': t} for t in district_talukas])

@app.route('/demo_alerts')
@login_required
def demo_alerts():
    demo_alerts = [
        {
            'type': 'High Temperature',
            'message': 'Temperature alert: Expected high temperature of 45°C in your area today. Stay hydrated!',
            'district': 'AHMADABAD',
            'taluka': 'Bavla'
        },
        {
            'type': 'Fire Risk',
            'message': 'Fire risk alert: High fire risk due to dry conditions. Avoid outdoor burning.',
            'district': 'RAJKOT',
            'taluka': 'Gondal'
        },
        {
            'type': 'Weather Warning',
            'message': 'Weather warning: Strong winds expected. Secure loose objects.',
            'district': 'SURAT',
            'taluka': 'Bardoli'
        }
    ]
    return render_template('demo_alerts.html', alerts=demo_alerts)

@app.route('/send_demo_alert', methods=['POST'])
@login_required
def send_demo_alert():
    data = request.get_json()
    district = data.get('district')
    taluka = data.get('taluka')
    message = data.get('message')
    
    # Log the demo alert (bot runs separately)
    logger.info(f"Demo alert: {district} -> {taluka}: {message}")
    
    # Simulate success for demo
    return jsonify({'success': True})

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
    
    # Log the alert (bot runs separately)
    logger.info(f"Weather alert sent: {alert['district']} -> {alert['taluka']}: {alert['message']}")
    
    # In a real implementation, this would send to the bot
    return jsonify({'success': True, 'message': 'Weather alert sent successfully'})

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

if __name__ == '__main__':
    # For local development
    app.run(debug=True, port=int(os.environ.get('PORT', 5000)), host='0.0.0.0')