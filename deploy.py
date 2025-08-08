#!/usr/bin/env python3
"""
Simple deployment script for Village Alert System
"""

import os
import subprocess
import sys

def run_cmd(cmd, desc):
    """Run command and return success status"""
    print(f"🔄 {desc}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {desc} - Success!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {desc} - Failed!")
        if e.stderr:
            print(f"Error: {e.stderr}")
        return False

def check_env():
    """Check if .env file exists and is not tracked"""
    if not os.path.exists('.env'):
        print("❌ .env file not found!")
        print("Create .env with:")
        print("TELEGRAM_BOT_TOKEN=your_token")
        print("ADMIN_EMAIL=your_email")
        print("ADMIN_PASSWORD=your_password")
        print("SECRET_KEY=your_secret")
        return False
    
    # Check if .env is tracked by git
    result = subprocess.run("git ls-files .env", shell=True, capture_output=True, text=True)
    if result.stdout.strip():
        print("⚠️  .env is tracked by git - removing for security...")
        run_cmd("git rm --cached .env", "Removing .env from git")
        run_cmd('git commit -m "Remove .env for security"', "Committing removal")
    
    print("✅ Environment file secure")
    return True

def deploy_bot():
    """Deploy bot to Railway"""
    print("\n🤖 DEPLOYING BOT")
    print("=" * 30)
    
    if not run_cmd("railway --version", "Checking Railway CLI"):
        print("Install Railway CLI: npm install -g @railway/cli")
        return False
    
    # Create railway.json for bot
    with open('railway.json', 'w') as f:
        f.write('''{
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "python bot_host.py",
    "restartPolicyType": "ON_FAILURE"
  }
}''')
    
    if run_cmd("railway login", "Logging into Railway"):
        bot_name = input("Enter bot project name (e.g., village-bot): ").strip() or "village-bot"
        if run_cmd(f"railway init --name {bot_name}", "Creating bot project"):
            print("\n⚠️  IMPORTANT: Set these environment variables in Railway dashboard:")
            print("- TELEGRAM_BOT_TOKEN")
            print("- ADMIN_EMAIL")
            print("- ADMIN_PASSWORD") 
            print("- SECRET_KEY")
            input("\nPress Enter after setting environment variables...")
            return run_cmd("railway up", "Deploying bot")
    return False

def deploy_website():
    """Deploy website to Railway"""
    print("\n🌐 DEPLOYING WEBSITE")
    print("=" * 30)
    
    # Create railway.json for website
    with open('railway.json', 'w') as f:
        f.write('''{
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "python app.py",
    "healthcheckPath": "/",
    "restartPolicyType": "ON_FAILURE"
  }
}''')
    
    web_name = input("Enter website project name (e.g., village-web): ").strip() or "village-web"
    if run_cmd(f"railway init --name {web_name}", "Creating website project"):
        print("\n⚠️  IMPORTANT: Set these environment variables in Railway dashboard:")
        print("- SECRET_KEY")
        print("- ADMIN_EMAIL")
        print("- ADMIN_PASSWORD")
        input("\nPress Enter after setting environment variables...")
        return run_cmd("railway up", "Deploying website")
    return False

def main():
    print("🚀 Village Alert System - Simple Deploy")
    print("=" * 50)
    
    if not check_env():
        sys.exit(1)
    
    print("\nWhat do you want to deploy?")
    print("1. Bot only")
    print("2. Website only")
    print("3. Both")
    
    choice = input("Enter choice (1-3): ").strip()
    
    success = False
    
    if choice in ['1', '3']:
        success = deploy_bot() or success
    
    if choice in ['2', '3']:
        success = deploy_website() or success
    
    if success:
        print("\n🎉 Deployment completed!")
        print("📖 Check DEPLOY.md for detailed instructions")
    else:
        print("\n❌ Deployment failed")
        print("📖 Check DEPLOY.md for troubleshooting")

if __name__ == "__main__":
    main()