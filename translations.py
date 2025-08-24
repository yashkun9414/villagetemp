#!/usr/bin/env python3
"""
Translation system for Gujarat Weather Alert System
"""

def get_translation(key, language='en'):
    """Get translation for a key in specified language"""
    translations = {
        'en': {
            'welcome': 'Welcome to Gujarat Weather Alert System',
            'temperature_alert': 'Temperature Alert',
            'fire_alert': 'Fire Alert',
            'weather_warning': 'Weather Warning',
            'high_temperature': 'High Temperature',
            'low_temperature': 'Low Temperature',
            'subscribe': 'Subscribe',
            'unsubscribe': 'Unsubscribe',
            'status': 'Status',
            'alerts': 'Alerts'
        },
        'gu': {
            'welcome': 'ગુજરાત હવામાન ચેતવણી સિસ્ટમમાં આપનું સ્વાગત છે',
            'temperature_alert': 'તાપમાન ચેતવણી',
            'fire_alert': 'આગ ચેતવણી',
            'weather_warning': 'હવામાન ચેતવણી',
            'high_temperature': 'ઊંચું તાપમાન',
            'low_temperature': 'નીચું તાપમાન',
            'subscribe': 'સબ્સ્ક્રાઇબ કરો',
            'unsubscribe': 'અનસબ્સ્ક્રાઇબ કરો',
            'status': 'સ્થિતિ',
            'alerts': 'ચેતવણીઓ'
        },
        'hi': {
            'welcome': 'गुजरात मौसम चेतावनी प्रणाली में आपका स्वागत है',
            'temperature_alert': 'तापमान चेतावनी',
            'fire_alert': 'आग चेतावनी',
            'weather_warning': 'मौसम चेतावनी',
            'high_temperature': 'उच्च तापमान',
            'low_temperature': 'कम तापमान',
            'subscribe': 'सब्सक्राइब करें',
            'unsubscribe': 'अनसब्सक्राइब करें',
            'status': 'स्थिति',
            'alerts': 'चेतावनियां'
        }
    }
    
    return translations.get(language, {}).get(key, key)

def get_all_translations():
    """Get all available translations"""
    return {
        'en': 'English',
        'gu': 'ગુજરાતી',
        'hi': 'हिंदी'
    }

def get_location_translation(location, language='en'):
    """Get location name in specified language"""
    # For now, return the location as-is
    # This can be expanded with actual translations
    return location

def get_language_name(language_code):
    """Get language name from code"""
    languages = {
        'en': 'English',
        'gu': 'Gujarati',
        'hi': 'Hindi'
    }
    return languages.get(language_code, 'English')