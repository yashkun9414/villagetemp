#!/usr/bin/env python3
"""
System Startup Script
Starts the fire scheduler and web application
"""

import subprocess
import sys
import time
import logging
import os
from threading import Thread

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_fire_scheduler():
    """Run the fire scheduler in background"""
    logger.info("🔥 Starting Fire Scheduler...")
    try:
        subprocess.run([sys.executable, 'fire_scheduler.py'])
    except Exception as e:
        logger.error(f"❌ Fire scheduler error: {e}")

def run_web_app():
    """Run the web application"""
    logger.info("🌐 Starting Web Application...")
    try:
        subprocess.run([sys.executable, 'app.py'])
    except Exception as e:
        logger.error(f"❌ Web app error: {e}")

def main():
    """Main startup function"""
    logger.info("🚀 Starting Gujarat Weather Alert System...")
    
    # Check if we're in production (Railway/Heroku)
    if os.getenv('RAILWAY_ENVIRONMENT') or os.getenv('DYNO'):
        logger.info("🚂 Production environment detected - starting web app only")
        run_web_app()
    else:
        logger.info("💻 Development environment - starting both services")
        
        # Start fire scheduler in background thread
        scheduler_thread = Thread(target=run_fire_scheduler, daemon=True)
        scheduler_thread.start()
        
        # Give scheduler time to start
        time.sleep(2)
        
        # Start web app (blocking)
        run_web_app()

if __name__ == "__main__":
    main()