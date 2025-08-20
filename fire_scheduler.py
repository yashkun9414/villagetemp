#!/usr/bin/env python3
"""
Fire Data Scheduler - Automates daily NASA fire data fetching
Runs nasa_fire_fetcher.py once daily and handles alerts
"""

import schedule
import time
import subprocess
import logging
from datetime import datetime
import os
import sys

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('fire_scheduler.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def run_nasa_fire_fetch():
    """Run the NASA fire data fetcher"""
    logger.info("🛰️ Starting scheduled NASA fire data fetch...")
    
    try:
        # Run the NASA fire fetcher
        result = subprocess.run([
            sys.executable, 'nasa_fire_fetcher.py'
        ], capture_output=True, text=True, timeout=300)  # 5 minute timeout
        
        if result.returncode == 0:
            logger.info("✅ NASA fire data fetch completed successfully")
            logger.info(f"Output: {result.stdout}")
            
            # Check for new fire alerts and send notifications
            send_fire_alerts()
            
        else:
            logger.error(f"❌ NASA fire data fetch failed with return code {result.returncode}")
            logger.error(f"Error: {result.stderr}")
            
    except subprocess.TimeoutExpired:
        logger.error("⏰ NASA fire data fetch timed out after 5 minutes")
    except Exception as e:
        logger.error(f"❌ Error running NASA fire fetch: {e}")

def send_fire_alerts():
    """Send fire alerts to subscribers"""
    try:
        from nasa_fire_fetcher import get_fire_alerts
        from shared_data import queue_alert, get_subscribers_for_area
        
        # Get current fire alerts
        fire_alerts = get_fire_alerts()
        
        if not fire_alerts:
            logger.info("✅ No fire alerts to send")
            return
        
        logger.info(f"🔥 Processing {len(fire_alerts)} fire alerts...")
        
        alerts_sent = 0
        for alert in fire_alerts:
            district = alert['district']
            taluka = alert['taluka']
            message = alert['message']
            
            # Check if there are subscribers for this area
            subscribers = get_subscribers_for_area(district, taluka)
            
            if subscribers:
                # Queue the fire alert
                if queue_alert(district, taluka, message, "fire"):
                    alerts_sent += 1
                    logger.info(f"🚨 Fire alert queued for {district} → {taluka} ({len(subscribers)} subscribers)")
        
        logger.info(f"✅ Queued {alerts_sent} fire alerts for delivery")
        
    except Exception as e:
        logger.error(f"❌ Error sending fire alerts: {e}")

def health_check():
    """Perform health check"""
    logger.info("💓 Scheduler health check - System running normally")
    
    # Check if fire data file exists and is recent
    fire_file = 'static/gujarat_fire_history.csv'
    if os.path.exists(fire_file):
        file_age = time.time() - os.path.getmtime(fire_file)
        hours_old = file_age / 3600
        logger.info(f"📊 Fire data file is {hours_old:.1f} hours old")
        
        if hours_old > 25:  # More than 25 hours old
            logger.warning("⚠️ Fire data file is more than 25 hours old - may need manual update")
    else:
        logger.warning("⚠️ Fire data file not found")

def main():
    """Main scheduler function"""
    logger.info("🚀 Starting Fire Data Scheduler...")
    logger.info("📅 Schedule: NASA fire data fetch daily at 06:00 and 18:00")
    logger.info("💓 Health check every 6 hours")
    
    # Schedule NASA fire data fetch twice daily
    schedule.every().day.at("06:00").do(run_nasa_fire_fetch)
    schedule.every().day.at("18:00").do(run_nasa_fire_fetch)
    
    # Schedule health checks
    schedule.every(6).hours.do(health_check)
    
    # Run initial fetch if fire data is missing or old
    fire_file = 'static/gujarat_fire_history.csv'
    if not os.path.exists(fire_file):
        logger.info("🔄 Fire data file missing - running initial fetch...")
        run_nasa_fire_fetch()
    else:
        file_age = time.time() - os.path.getmtime(fire_file)
        if file_age > 86400:  # More than 24 hours old
            logger.info("🔄 Fire data file is old - running initial fetch...")
            run_nasa_fire_fetch()
    
    logger.info("✅ Scheduler is now running...")
    
    # Keep the scheduler running
    while True:
        try:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            logger.info("🛑 Scheduler stopped by user")
            break
        except Exception as e:
            logger.error(f"❌ Scheduler error: {e}")
            time.sleep(300)  # Wait 5 minutes before retrying

if __name__ == "__main__":
    main()