#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Script untuk Bos Upety Bot PRO 24/7
Script untuk testing semua fitur bot
"""

import os
import json
import time
from datetime import datetime
from dotenv import load_dotenv

# Load environment
load_dotenv()

def test_environment():
    """Test environment variables"""
    print("🔍 Testing Environment Variables...")
    
    required_vars = [
        'FONNTE_TOKEN',
        'GEMINI_API_KEY', 
        'ADMIN',
        'BOS',
        'SHEET_ID'
    ]
    
    all_good = True
    for var in required_vars:
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: {'*' * 10}...{value[-4:]}")
        else:
            print(f"❌ {var}: NOT SET")
            all_good = False
    
    return all_good

def test_gemini_service():
    """Test Gemini AI service"""
    print("\n🧠 Testing Gemini AI Service...")
    
    try:
        from gemini_service import GeminiService
        
        gemini = GeminiService()
        
        # Test simple transaction
        test_message = "beli rokok 25000"
        result = gemini.analyze_transaction(test_message)
        
        if result:
            print("✅ Gemini AI working")
            print(f"   Input: {test_message}")
            print(f"   Output: {result.get('tanggapan_bot', 'No response')}")
            return True
        else:
            print("❌ Gemini AI failed")
            return False
            
    except Exception as e:
        print(f"❌ Gemini AI error: {str(e)}")
        return False

def test_sheets_service():
    """Test Google Sheets service"""
    print("\n📊 Testing Google Sheets Service...")
    
    try:
        from sheets_service import SheetsService
        
        sheets = SheetsService()
        
        if sheets.is_healthy():
            print("✅ Google Sheets connected")
            
            # Test get current balance
            balance = sheets.get_current_balance()
            print(f"   Current balance: Rp {balance:,}")
            
            return True
        else:
            print("❌ Google Sheets connection failed")
            return False
            
    except Exception as e:
        print(f"❌ Google Sheets error: {str(e)}")
        return False

def test_drive_service():
    """Test Google Drive service"""
    print("\n📁 Testing Google Drive Service...")
    
    try:
        from drive_service import DriveService
        
        drive = DriveService()
        
        if drive.is_healthy():
            print("✅ Google Drive connected")
            
            # Get folder info
            folder_info = drive.get_folder_info()
            if folder_info:
                print(f"   Folder: {folder_info.get('name', 'Unknown')}")
                print(f"   Files: {folder_info.get('file_count', 0)}")
            
            return True
        else:
            print("❌ Google Drive connection failed")
            return False
            
    except Exception as e:
        print(f"❌ Google Drive error: {str(e)}")
        return False

def test_logger_service():
    """Test Logger service"""
    print("\n📝 Testing Logger Service...")
    
    try:
        from logger_service import LoggerService
        
        logger = LoggerService()
        
        # Test logging
        logger.log_info("Test info message")
        logger.log_warning("Test warning message")
        logger.log_error("Test error message")
        
        # Get health info
        health = logger.monitor_system_health()
        
        print("✅ Logger service working")
        print(f"   Health score: {health.get('health_score', 0)}/100")
        print(f"   Status: {health.get('status', 'Unknown')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Logger service error: {str(e)}")
        return False

def test_backup_service():
    """Test Backup service"""
    print("\n💾 Testing Backup Service...")
    
    try:
        from backup_service import BackupService
        
        backup = BackupService()
        
        # Test backup info
        info = backup.get_backup_info()
        
        print("✅ Backup service working")
        print(f"   Transactions: {info.get('transactions_count', 0)}")
        print(f"   Backup files: {len(info.get('backup_files', []))}")
        
        return True
        
    except Exception as e:
        print(f"❌ Backup service error: {str(e)}")
        return False

def test_whatsapp_send():
    """Test WhatsApp sending"""
    print("\n📱 Testing WhatsApp Send...")
    
    try:
        import requests
        
        fonnte_token = os.getenv('FONNTE_TOKEN')
        admin_number = os.getenv('ADMIN')
        
        if not fonnte_token or not admin_number:
            print("❌ Fonnte token or admin number not set")
            return False
        
        # Test message
        test_message = f"🤖 Test Bot - {datetime.now().strftime('%H:%M:%S')}"
        
        url = "https://api.fonnte.com/send"
        headers = {'Authorization': fonnte_token}
        data = {
            'target': admin_number,
            'message': test_message
        }
        
        response = requests.post(url, headers=headers, data=data, timeout=10)
        
        if response.status_code == 200:
            print("✅ WhatsApp send working")
            print(f"   Message sent to: {admin_number}")
            return True
        else:
            print(f"❌ WhatsApp send failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ WhatsApp send error: {str(e)}")
        return False

def test_full_transaction():
    """Test full transaction flow"""
    print("\n🔄 Testing Full Transaction Flow...")
    
    try:
        from gemini_service import GeminiService
        from sheets_service import SheetsService
        from backup_service import BackupService
        
        gemini = GeminiService()
        sheets = SheetsService()
        backup = BackupService()
        
        # Test transaction
        test_message = "test transaksi 10000"
        
        # Step 1: AI Analysis
        ai_result = gemini.analyze_transaction(test_message)
        if not ai_result:
            print("❌ AI analysis failed")
            return False
        
        print("✅ AI analysis successful")
        
        # Step 2: Prepare transaction data
        transaction_data = {
            'tanggal': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'deskripsi': ai_result.get('deskripsi', ''),
            'jumlah': ai_result.get('jumlah', 0),
            'tipe': ai_result.get('tipe', 'INFO'),
            'kategori': ai_result.get('kategori', 'Lainnya'),
            'saldo': 100000,  # Test saldo
            'bukti': ai_result.get('bukti', ''),
            'private': 'No'
        }
        
        # Step 3: Save to Sheets (if available)
        if sheets.is_healthy():
            sheets_success = sheets.save_transaction(transaction_data)
            if sheets_success:
                print("✅ Google Sheets save successful")
            else:
                print("⚠️ Google Sheets save failed")
        
        # Step 4: Save to backup
        backup_success = backup.save_transaction(transaction_data)
        if backup_success:
            print("✅ Local backup save successful")
        else:
            print("❌ Local backup save failed")
            return False
        
        print("✅ Full transaction flow test completed")
        return True
        
    except Exception as e:
        print(f"❌ Full transaction flow error: {str(e)}")
        return False

def main():
    """Main test function"""
    print("🧪 Bos Upety Bot PRO 24/7 - Test Suite")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    tests = [
        ("Environment Variables", test_environment),
        ("Gemini AI Service", test_gemini_service),
        ("Google Sheets Service", test_sheets_service),
        ("Google Drive Service", test_drive_service),
        ("Logger Service", test_logger_service),
        ("Backup Service", test_backup_service),
        ("WhatsApp Send", test_whatsapp_send),
        ("Full Transaction Flow", test_full_transaction)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} crashed: {str(e)}")
            results.append((test_name, False))
        
        time.sleep(1)  # Small delay between tests
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Bot is ready to deploy.")
    else:
        print("⚠️ Some tests failed. Please check the issues above.")
    
    return passed == total

if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)
