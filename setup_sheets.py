#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Setup Google Sheets untuk Bos Upety Bot PRO 24/7
Script untuk setup awal Google Sheets dengan format yang benar
"""

import os
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

def setup_google_sheets():
    """Setup Google Sheets dengan format yang benar"""
    try:
        print("🔧 Setting up Google Sheets...")
        
        # Setup credentials
        scope = [
            'https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive'
        ]
        
        if os.path.exists('credentials.json'):
            creds = Credentials.from_service_account_file('credentials.json', scopes=scope)
        else:
            print("❌ credentials.json not found!")
            return False
        
        # Initialize client
        client = gspread.authorize(creds)
        
        # Get sheet ID from environment
        sheet_id = os.getenv('SHEET_ID')
        if not sheet_id:
            print("❌ SHEET_ID not found in environment variables!")
            return False
        
        # Open spreadsheet
        spreadsheet = client.open_by_key(sheet_id)
        worksheet = spreadsheet.sheet1
        
        print(f"✅ Connected to spreadsheet: {spreadsheet.title}")
        
        # Clear existing data
        worksheet.clear()
        
        # Setup headers
        headers = ['Tanggal', 'Deskripsi', 'Jumlah', 'Tipe', 'Kategori', 'Saldo', 'Bukti', 'Private']
        worksheet.append_row(headers)
        
        # Format headers
        worksheet.format('A1:H1', {
            'backgroundColor': {'red': 0.2, 'green': 0.6, 'blue': 0.8},
            'textFormat': {'bold': True, 'foregroundColor': {'red': 1, 'green': 1, 'blue': 1}}
        })
        
        # Set column widths
        worksheet.columns_auto_resize(0, 7)
        
        # Add sample data
        sample_data = [
            [
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'Setup Bot - Saldo Awal',
                0,
                'INFO',
                'Lainnya',
                0,
                '',
                'No'
            ]
        ]
        
        for row in sample_data:
            worksheet.append_row(row)
        
        # Format sample row
        worksheet.format('A2:H2', {
            'backgroundColor': {'red': 0.9, 'green': 0.9, 'blue': 0.9}
        })
        
        print("✅ Headers and formatting applied")
        print("✅ Sample data added")
        
        # Create summary sheet
        try:
            # Check if summary sheet exists
            try:
                summary_sheet = spreadsheet.worksheet("Summary")
            except:
                # Create summary sheet
                summary_sheet = spreadsheet.add_worksheet(title="Summary", rows=100, cols=10)
            
            # Setup summary headers
            summary_headers = ['Tanggal', 'Total Pemasukan', 'Total Pengeluaran', 'Saldo Bersih', 'Jumlah Transaksi']
            summary_sheet.clear()
            summary_sheet.append_row(summary_headers)
            
            # Format summary headers
            summary_sheet.format('A1:E1', {
                'backgroundColor': {'red': 0.1, 'green': 0.7, 'blue': 0.1},
                'textFormat': {'bold': True, 'foregroundColor': {'red': 1, 'green': 1, 'blue': 1}}
            })
            
            print("✅ Summary sheet created")
            
        except Exception as e:
            print(f"⚠️ Could not create summary sheet: {str(e)}")
        
        print(f"✅ Google Sheets setup completed!")
        print(f"📊 Sheet URL: {spreadsheet.url}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error setting up Google Sheets: {str(e)}")
        return False

def create_new_sheet():
    """Create new Google Sheet"""
    try:
        print("📝 Creating new Google Sheet...")
        
        # Setup credentials
        scope = [
            'https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive'
        ]
        
        if os.path.exists('credentials.json'):
            creds = Credentials.from_service_account_file('credentials.json', scopes=scope)
        else:
            print("❌ credentials.json not found!")
            return None
        
        # Initialize client
        client = gspread.authorize(creds)
        
        # Create new spreadsheet
        spreadsheet = client.create('Bos Upety Bot - Keuangan')
        
        # Make it accessible to anyone with the link
        spreadsheet.share('', perm_type='anyone', role='reader')
        
        print(f"✅ New spreadsheet created: {spreadsheet.title}")
        print(f"📊 Sheet ID: {spreadsheet.id}")
        print(f"🔗 Sheet URL: {spreadsheet.url}")
        
        # Setup the sheet
        worksheet = spreadsheet.sheet1
        
        # Setup headers
        headers = ['Tanggal', 'Deskripsi', 'Jumlah', 'Tipe', 'Kategori', 'Saldo', 'Bukti', 'Private']
        worksheet.append_row(headers)
        
        # Format headers
        worksheet.format('A1:H1', {
            'backgroundColor': {'red': 0.2, 'green': 0.6, 'blue': 0.8},
            'textFormat': {'bold': True, 'foregroundColor': {'red': 1, 'green': 1, 'blue': 1}}
        })
        
        # Set column widths
        worksheet.columns_auto_resize(0, 7)
        
        print("✅ Headers and formatting applied")
        
        return spreadsheet.id
        
    except Exception as e:
        print(f"❌ Error creating new sheet: {str(e)}")
        return None

def main():
    """Main function"""
    print("🔧 Bos Upety Bot PRO 24/7 - Google Sheets Setup")
    print("=" * 50)
    
    # Check if SHEET_ID exists
    sheet_id = os.getenv('SHEET_ID')
    
    if sheet_id and sheet_id != 'ISI_ID_SHEET_GOOGLE_DISINI':
        print(f"📊 Using existing sheet ID: {sheet_id}")
        success = setup_google_sheets()
    else:
        print("📝 No valid sheet ID found. Creating new sheet...")
        new_sheet_id = create_new_sheet()
        
        if new_sheet_id:
            print(f"\n🎉 New sheet created successfully!")
            print(f"📋 Please update your .env file with:")
            print(f"SHEET_ID={new_sheet_id}")
            success = True
        else:
            success = False
    
    if success:
        print("\n✅ Google Sheets setup completed!")
        print("🤖 Bot is ready to use Google Sheets")
    else:
        print("\n❌ Google Sheets setup failed!")
        print("💡 Please check your credentials and try again")

if __name__ == '__main__':
    main()
