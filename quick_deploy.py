#!/usr/bin/env python3
"""
Quick Deployment Helper for Gujarat Weather Alert System
"""

import os
import subprocess
import sys
import webbrowser

def print_header(title):
    print("\n" + "="*60)
    print(f"🚀 {title}")
    print("="*60)

def print_step(step, description):
    print(f"\n📋 STEP {step}: {description}")
    print("-" * 40)

def run_command(command, description):
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} - Success!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - Failed!")
        print(f"Error: {e.stderr}")
        return False

def check_file_exists(filename):
    if os.path.exists(filename):
        print(f"✅ {filename} - Found")
        return True
    else:
        print(f"❌ {filename} - Missing")
        return False

def main():
    print_header("Gujarat Weather Alert System - Quick Deploy")
    
    print("🎯 This script will help you deploy:")
    print("   🌐 Web App (Firebase)")
    print("   🤖 Telegram Bot (Railway)")
    print("   🛰️ NASA Fire Data (GitHub Actions)")
    
    # Check prerequisites
    print_step(1, "Checking Prerequisites")
    
    required_files = [
        'app.py',
        'bot_host.py', 
        'requirements.txt',
        'merged_village_temperature_data.csv',
        '.env'
    ]
    
    all_files_exist = True
    for file in required_files:
        if not check_file_exists(file):
            all_files_exist = False
    
    if not all_files_exist:
        print("\n❌ Missing required files. Please ensure all files are present.")
        return
    
    print("\n✅ All required files found!")
    
    # Test NASA fire data
    print_step(2, "Testing NASA Fire Data")
    if run_command("python nasa_fire_fetcher.py", "Testing NASA fire data fetcher"):
        print("✅ NASA fire data system working!")
    
    # Test bot locally
    print_step(3, "Testing Bot Code")
    try:
        import bot_host
        print("✅ Bot code imports successfully")
    except Exception as e:
        print(f"❌ Bot import failed: {e}")
    
    # Deployment options
    print_step(4, "Deployment Options")
    
    print("\n🌐 WEB APP DEPLOYMENT:")
    print("Option 1: Firebase (Recommended)")
    print("   1. Install: npm install -g firebase-tools")
    print("   2. Login: firebase login")
    print("   3. Deploy: firebase deploy")
    
    print("\n🤖 BOT DEPLOYMENT:")
    print("Option 1: Railway (Recommended - $5/month)")
    print("   1. Push code to GitHub")
    print("   2. Go to: https://railway.app")
    print("   3. New Project → Deploy from GitHub repo")
    print("   4. Add environment variable: TELEGRAM_BOT_TOKEN")
    
    print("\n🛰️ FIRE DATA:")
    print("✅ Already configured! GitHub Actions will run automatically.")
    
    # Interactive deployment
    print_step(5, "Interactive Deployment")
    
    while True:
        print("\nWhat would you like to do?")
        print("1. 🌐 Deploy Web App (Firebase)")
        print("2. 📤 Push to GitHub (for bot deployment)")
        print("3. 🧪 Test NASA Fire Data")
        print("4. 🤖 Test Bot Locally")
        print("5. 📖 Open Deployment Guide")
        print("6. 🌍 Open Railway.app")
        print("7. 📱 Open Telegram Bot")
        print("8. ❌ Exit")
        
        choice = input("\nEnter your choice (1-8): ").strip()
        
        if choice == "1":
            print("\n🌐 Deploying to Firebase...")
            if run_command("firebase --version", "Checking Firebase CLI"):
                if run_command("firebase deploy", "Deploying to Firebase"):
                    print("🎉 Web app deployed successfully!")
                    print("📱 Your app should be live at your Firebase URL")
                else:
                    print("💡 Try: firebase login first, then firebase init")
            else:
                print("💡 Install Firebase CLI: npm install -g firebase-tools")
        
        elif choice == "2":
            print("\n📤 Pushing to GitHub...")
            if run_command("git status", "Checking git status"):
                run_command("git add .", "Adding files")
                run_command('git commit -m "Deploy ready"', "Committing changes")
                if run_command("git push", "Pushing to GitHub"):
                    print("🎉 Code pushed to GitHub!")
                    print("📱 Now go to railway.app to deploy your bot")
                else:
                    print("💡 Set up GitHub remote first:")
                    print("   git remote add origin https://github.com/yourusername/your-repo.git")
        
        elif choice == "3":
            print("\n🛰️ Testing NASA Fire Data...")
            run_command("python nasa_fire_fetcher.py", "Fetching NASA fire data")
        
        elif choice == "4":
            print("\n🤖 Testing Bot Locally...")
            print("⚠️  This will start the bot locally. Press Ctrl+C to stop.")
            input("Press Enter to continue or Ctrl+C to cancel...")
            try:
                run_command("python bot_host.py", "Starting bot locally")
            except KeyboardInterrupt:
                print("\n🛑 Bot stopped")
        
        elif choice == "5":
            print("\n📖 Opening deployment guide...")
            if os.path.exists("DEPLOY_STEP_BY_STEP.md"):
                if sys.platform.startswith('win'):
                    os.startfile("DEPLOY_STEP_BY_STEP.md")
                else:
                    subprocess.run(["open", "DEPLOY_STEP_BY_STEP.md"])
            else:
                print("📖 Deployment guide: DEPLOY_STEP_BY_STEP.md")
        
        elif choice == "6":
            print("\n🌍 Opening Railway.app...")
            webbrowser.open("https://railway.app")
        
        elif choice == "7":
            print("\n📱 Opening Telegram Bot...")
            webbrowser.open("https://t.me/VillaegWarningbot")
        
        elif choice == "8":
            break
        
        else:
            print("❌ Invalid choice. Please select 1-8.")
    
    print_header("Deployment Complete!")
    print("🎉 Your Gujarat Weather Alert System is ready!")
    print("\n📱 Next Steps:")
    print("   1. Deploy web app: firebase deploy")
    print("   2. Deploy bot: Push to GitHub → Railway.app")
    print("   3. Test everything works")
    print("   4. Share @VillaegWarningbot with users")
    print("\n🌟 Your system will help protect the people of Gujarat!")

if __name__ == "__main__":
    main()