#!/usr/bin/env python3
"""
Firebase Functions entry point for Gujarat Weather Alert System
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import the Flask app
from app import app, initialize_bot

# Initialize the Telegram bot on startup
initialize_bot()

# This is the entry point for Firebase Functions
if __name__ == "__main__":
    # For local development
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
else:
    # For Firebase Functions
    # The app object will be used by the Firebase Functions runtime
    pass