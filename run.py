#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bos Upety Bot PRO 24/7 - Main Runner
Simple script to run the bot with error handling
"""

import os
import sys
import time
from datetime import datetime

def check_requirements():
    """Check if all required files exist"""
    required_files = [
        'main.py',
        'gemini_service.py',
        'sheets_service.py',
        'drive_service.py',
        'scheduler.py',
        'logger_service.py',
        'backup_service.py',
        'requirements.txt'
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print("❌ Missing required files:")
        for file in missing_files:
            print(f"   - {file}")
        return False
    
    return True

def check_environment():
    """Check environment variables"""
    required_env = [
        'FONNTE_TOKEN',
        'GEMINI_API_KEY',
        'ADMIN',
        'BOS',
        'SHEET_ID'
    ]
    
    missing_env = []
    for env in required_env:
        if not os.getenv(env):
            missing_env.append(env)
    
    if missing_env:
        print("❌ Missing environment variables:")
        for env in missing_env:
            print(f"   - {env}")
        print("\n💡 Please check your .env file or environment variables")
        return False
    
    return True

def main():
    """Main function"""
    print("🤖 Bos Upety Bot PRO 24/7 - Starting...")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    # Check requirements
    if not check_requirements():
        print("\n❌ Requirements check failed!")
        sys.exit(1)
    
    print("✅ All required files found")
    
    # Check environment
    if not check_environment():
        print("\n❌ Environment check failed!")
        sys.exit(1)
    
    print("✅ Environment variables configured")
    
    # Check credentials
    if not os.path.exists('credentials.json'):
        print("⚠️  credentials.json not found!")
        print("💡 Please upload your Google service account credentials")
        print("   You can continue without it, but Google services won't work")
    
    print("\n🚀 Starting bot...")
    print("=" * 50)
    
    try:
        # Import and run main
        from main import main as bot_main
        bot_main()
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Bot stopped by user")
        sys.exit(0)
        
    except Exception as e:
        print(f"\n❌ Fatal error: {str(e)}")
        print("🔄 Attempting restart in 5 seconds...")
        
        time.sleep(5)
        
        # Restart
        os.execv(sys.executable, ['python'] + sys.argv)

if __name__ == '__main__':
    main()
