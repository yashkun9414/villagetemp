#!/usr/bin/env python3
"""
Real NASA MODIS Fire Data Fetcher for Gujarat Weather Alert System
Downloads and processes real fire data from NASA FIRMS
Run this daily via cron job or scheduled task
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import requests
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_location_data():
    """Load location data from CSV"""
    try:
        df = pd.read_csv('merged_village_temperature_data.csv')
        return df
    except Exception as e:
        logger.error(f"Error loading location data: {e}")
        return pd.DataFrame()

def fetch_nasa_fire_data():
    """Fetch real fire data from NASA MODIS"""
    logger.info("🛰️ Fetching real fire data from NASA MODIS...")
    
    try:
        # NASA FIRMS MODIS data URL (last 24 hours)
        url = "https://firms.modaps.eosdis.nasa.gov/data/active_fire/c6/csv/MODIS_C6_1_Global_24h.csv"
        
        logger.info(f"📡 Downloading from: {url}")
        df = pd.read_csv(url)
        logger.info(f"✅ Downloaded {len(df)} global fire records")
        
        return df
        
    except Exception as e:
        logger.error(f"❌ Error fetching NASA fire data: {e}")
        logger.info("🔄 Trying alternative data source...")
        
        # Try 7-day data as fallback
        try:
            url_7day = "https://firms.modaps.eosdis.nasa.gov/data/active_fire/c6/csv/MODIS_C6_1_Global_7d.csv"
            logger.info(f"📡 Downloading 7-day data from: {url_7day}")
            df = pd.read_csv(url_7day)
            logger.info(f"✅ Downloaded {len(df)} global fire records (7-day)")
            return df
        except Exception as e2:
            logger.error(f"❌ Error fetching 7-day data: {e2}")
            return pd.DataFrame()

def filter_gujarat_fires(global_df):
    """Filter fire data for Gujarat region"""
    if global_df.empty:
        return pd.DataFrame()
    
    logger.info("🔍 Filtering for Gujarat region...")
    
    # Gujarat bounding box coordinates (more precise)
    lat_min, lat_max = 20.1, 24.7
    lon_min, lon_max = 68.2, 74.4
    
    # Filter for Gujarat region
    gujarat_df = global_df[
        (global_df['latitude'] >= lat_min) & 
        (global_df['latitude'] <= lat_max) &
        (global_df['longitude'] >= lon_min) & 
        (global_df['longitude'] <= lon_max)
    ]
    
    logger.info(f"🔥 Found {len(gujarat_df)} fire incidents in Gujarat region")
    
    # Filter for today's date only (real-time data)
    today = datetime.now().strftime('%Y-%m-%d')
    if 'acq_date' in gujarat_df.columns:
        gujarat_df['acq_date'] = pd.to_datetime(gujarat_df['acq_date']).dt.strftime('%Y-%m-%d')
        today_fires = gujarat_df[gujarat_df['acq_date'] == today]
        logger.info(f"📅 Today's fires ({today}): {len(today_fires)}")
        gujarat_df = today_fires
    
    # Filter high-confidence detections (≥70% for more inclusive detection)
    if not gujarat_df.empty:
        high_confidence = gujarat_df[gujarat_df['confidence'] >= 70]
        logger.info(f"⚠️ High confidence fires (≥70%): {len(high_confidence)}")
    
    return gujarat_df

def map_fires_to_districts(fire_df, location_df):
    """Map fire coordinates to districts and talukas"""
    if fire_df.empty or location_df.empty:
        return fire_df
    
    logger.info("📍 Mapping fires to districts and talukas...")
    
    # Add district and taluka columns
    fire_df = fire_df.copy()
    fire_df['district'] = 'Unknown'
    fire_df['taluka'] = 'Unknown'
    
    # Get unique locations with coordinates
    locations = location_df[['District Name', 'Taluka Name', 'Taluka Latitude', 'Taluka Longitude']].dropna()
    
    for idx, fire in fire_df.iterrows():
        fire_lat = fire['latitude']
        fire_lon = fire['longitude']
        
        # Find closest district/taluka (within reasonable distance)
        min_distance = float('inf')
        closest_district = 'Unknown'
        closest_taluka = 'Unknown'
        
        for _, location in locations.iterrows():
            loc_lat = float(location['Taluka Latitude'])
            loc_lon = float(location['Taluka Longitude'])
            
            # Calculate approximate distance (simple Euclidean)
            distance = ((fire_lat - loc_lat) ** 2 + (fire_lon - loc_lon) ** 2) ** 0.5
            
            # If within ~0.5 degrees (~55km), consider it close
            if distance < 0.5 and distance < min_distance:
                min_distance = distance
                closest_district = location['District Name']
                closest_taluka = location['Taluka Name']
        
        fire_df.at[idx, 'district'] = closest_district
        fire_df.at[idx, 'taluka'] = closest_taluka
    
    # Count mapped fires
    mapped_fires = len(fire_df[fire_df['district'] != 'Unknown'])
    logger.info(f"📊 Mapped {mapped_fires}/{len(fire_df)} fires to districts/talukas")
    
    return fire_df

def process_fire_data(fire_df):
    """Process and clean fire data"""
    if fire_df.empty:
        return fire_df
    
    logger.info("🔧 Processing fire data...")
    
    # Rename columns to match our format
    processed_df = fire_df.copy()
    
    # Add additional fields based on MODIS data
    if 'type' in processed_df.columns:
        processed_df['fire_type'] = processed_df['type'].map({
            0: 'Vegetation',
            1: 'Active Fire',
            2: 'Other',
            3: 'Other'
        }).fillna('Vegetation')
    else:
        processed_df['fire_type'] = 'Vegetation'  # Default type
    
    processed_df['severity'] = processed_df['confidence'].apply(
        lambda x: 'High' if x >= 90 else 'Medium' if x >= 70 else 'Low'
    )
    
    # Estimate area affected based on brightness and confidence
    if 'bright_ti4' in processed_df.columns:
        processed_df['area_affected'] = (processed_df['bright_ti4'] / 100 * processed_df['confidence'] / 100).round(2)
    else:
        processed_df['area_affected'] = (processed_df['confidence'] / 10).round(2)
    
    processed_df['source'] = 'NASA MODIS'
    
    # Ensure date format
    if 'acq_date' in processed_df.columns:
        processed_df['acq_date'] = pd.to_datetime(processed_df['acq_date']).dt.strftime('%Y-%m-%d')
    
    # Select relevant columns
    columns_to_keep = [
        'acq_date', 'acq_time', 'latitude', 'longitude', 'confidence',
        'district', 'taluka', 'fire_type', 'severity', 'area_affected', 'source'
    ]
    
    # Keep only columns that exist
    available_columns = [col for col in columns_to_keep if col in processed_df.columns]
    processed_df = processed_df[available_columns]
    
    logger.info(f"✅ Processed {len(processed_df)} fire records")
    return processed_df

def update_fire_history():
    """Update the fire history CSV file with real NASA data"""
    logger.info("🔥 Starting NASA fire data update...")
    
    # Load location data
    location_df = load_location_data()
    if location_df.empty:
        logger.error("❌ Could not load location data")
        return False
    
    # Fetch NASA fire data
    global_fire_df = fetch_nasa_fire_data()
    if global_fire_df.empty:
        logger.error("❌ Could not fetch NASA fire data")
        return False
    
    # Filter for Gujarat
    gujarat_fire_df = filter_gujarat_fires(global_fire_df)
    
    # Load existing fire history
    fire_history_file = 'gujarat_fire_history.csv'
    static_file = 'static/gujarat_fire_history.csv'
    
    if gujarat_fire_df.empty:
        logger.info("ℹ️ No fire incidents found in Gujarat region today")
        
        # Update existing file to remove old test data and keep only recent real data
        if os.path.exists(fire_history_file):
            try:
                existing_df = pd.read_csv(fire_history_file)
                
                # Keep only data from last 30 days and real NASA MODIS data
                from datetime import datetime, timedelta
                thirty_days_ago = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
                
                # Filter for recent data and real NASA sources
                recent_df = existing_df[
                    (existing_df['acq_date'] >= thirty_days_ago) & 
                    (existing_df['source'] == 'NASA MODIS')
                ]
                
                logger.info(f"📊 Cleaned fire history: {len(recent_df)} recent records")
                
                # Save cleaned data
                recent_df.to_csv(fire_history_file, index=False)
                if os.path.exists('static'):
                    recent_df.to_csv(static_file, index=False)
                
            except Exception as e:
                logger.error(f"❌ Error cleaning fire data: {e}")
        
        return True
    
    # Map to districts/talukas
    mapped_fire_df = map_fires_to_districts(gujarat_fire_df, location_df)
    
    # Process the data
    processed_fire_df = process_fire_data(mapped_fire_df)
    
    if os.path.exists(fire_history_file):
        try:
            existing_df = pd.read_csv(fire_history_file)
            logger.info(f"📊 Loaded {len(existing_df)} existing fire records")
            
            # Remove today's data from existing (to avoid duplicates)
            today = datetime.now().strftime('%Y-%m-%d')
            existing_df = existing_df[existing_df['acq_date'] != today]
            
            # Keep only recent data (last 30 days)
            from datetime import timedelta
            thirty_days_ago = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
            existing_df = existing_df[existing_df['acq_date'] >= thirty_days_ago]
            
            # Combine with new data
            combined_df = pd.concat([existing_df, processed_fire_df], ignore_index=True)
                
        except Exception as e:
            logger.error(f"❌ Error reading existing fire data: {e}")
            combined_df = processed_fire_df
    else:
        combined_df = processed_fire_df
    
    # Save updated data
    try:
        combined_df.to_csv(fire_history_file, index=False)
        logger.info(f"✅ Fire history updated: {len(combined_df)} total records")
        
        # Also save to static folder for web access
        if os.path.exists('static'):
            combined_df.to_csv(static_file, index=False)
            logger.info(f"✅ Fire history copied to static folder")
        
        # Log today's incidents
        today = datetime.now().strftime('%Y-%m-%d')
        today_incidents = combined_df[combined_df['acq_date'] == today]
        logger.info(f"🔥 Today's incidents: {len(today_incidents)}")
        
        if len(today_incidents) > 0:
            high_confidence = today_incidents[today_incidents['confidence'] >= 70]
            logger.info(f"⚠️ High confidence incidents today: {len(high_confidence)}")
            
            # Show some examples
            for _, incident in high_confidence.head(3).iterrows():
                logger.info(f"   🔥 {incident.get('district', 'Unknown')} → {incident.get('taluka', 'Unknown')} ({incident.get('confidence', 'N/A')}%)")
        else:
            logger.info("✅ No fire incidents detected in Gujarat today")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error saving fire data: {e}")
        return False

def get_fire_alerts():
    """Get current fire alerts for high-risk areas"""
    try:
        df = pd.read_csv('gujarat_fire_history.csv')
        
        # Get incidents from last 24 hours
        yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        recent_fires = df[df['acq_date'] >= yesterday]
        
        # High confidence fires
        high_risk_fires = recent_fires[recent_fires['confidence'] >= 80]
        
        alerts = []
        for _, fire in high_risk_fires.iterrows():
            alert = {
                'district': fire.get('district', 'Unknown'),
                'taluka': fire.get('taluka', 'Unknown'),
                'message': f"🔥 Fire Alert: {fire.get('fire_type', 'Fire')} detected in {fire.get('taluka', 'Unknown')}, {fire.get('district', 'Unknown')}. Confidence: {fire.get('confidence', 'N/A')}%. Area affected: {fire.get('area_affected', 'N/A')} hectares. Please exercise caution.",
                'severity': fire.get('severity', 'Unknown'),
                'confidence': fire.get('confidence', 0)
            }
            alerts.append(alert)
        
        return alerts
        
    except Exception as e:
        logger.error(f"Error getting fire alerts: {e}")
        return []

def main():
    """Main function to run NASA fire data update"""
    print("🛰️ NASA MODIS Fire Data Fetcher for Gujarat")
    print("=" * 50)
    
    success = update_fire_history()
    
    if success:
        print("✅ NASA fire data update completed successfully!")
        
        # Show current alerts
        alerts = get_fire_alerts()
        if alerts:
            print(f"\n🚨 Current Fire Alerts: {len(alerts)}")
            for alert in alerts[:3]:  # Show first 3
                print(f"   📍 {alert['district']} → {alert['taluka']} ({alert['confidence']}% confidence)")
        else:
            print("\n✅ No high-risk fire alerts currently")
    else:
        print("❌ NASA fire data update failed!")
    
    print("=" * 50)

if __name__ == "__main__":
    main()