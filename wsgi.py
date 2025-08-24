#!/usr/bin/env python3
"""
WSGI entry point for Gujarat Weather Alert System
"""

import os
import sys
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

try:
    from app import app
    
    # Ensure the app is configured properly
    if not app.config.get('SECRET_KEY'):
        app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'fallback-secret-key')
    
    logger.info("✅ Gujarat Weather Alert System WSGI app loaded successfully")
    
    # This is what Gunicorn will use
    application = app
    
except Exception as e:
    logger.error(f"❌ Failed to load WSGI app: {e}")
    import traceback
    traceback.print_exc()
    raise

if __name__ == "__main__":
    # For direct execution (development)
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)