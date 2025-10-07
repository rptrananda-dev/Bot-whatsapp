#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Google Sheets Service - Integrasi Google Sheets untuk menyimpan transaksi
"""

import os
import json
import time
from typing import Dict, List, Optional, Any
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv

load_dotenv()

class SheetsService:
    def __init__(self):
        self.sheet_id = os.getenv('SHEET_ID')
        self.health_status = True
        self.worksheet = None
        self.client = None
        
        # Initialize Google Sheets connection
        self._initialize_connection()
    
    def _initialize_connection(self):
        """Initialize Google Sheets connection"""
        try:
            # Setup credentials
            scope = [
                'https://spreadsheets.google.com/feeds',
                'https://www.googleapis.com/auth/drive'
            ]
            
            # Try to load credentials from file
            if os.path.exists('credentials.json'):
                creds = Credentials.from_service_account_file('credentials.json', scopes=scope)
            else:
                # Fallback: try environment variable
                creds_json = os.getenv('GOOGLE_CREDENTIALS_JSON')
                if creds_json:
                    creds = Credentials.from_service_account_info(json.loads(creds_json), scopes=scope)
                else:
                    raise Exception("No credentials found")
            
            # Initialize client
            self.client = gspread.authorize(creds)
            
            # Open spreadsheet
            if self.sheet_id:
                spreadsheet = self.client.open_by_key(self.sheet_id)
                self.worksheet = spreadsheet.sheet1
                
                # Setup headers if not exists
                self._setup_headers()
                
                self.health_status = True
                print("✅ Google Sheets connected successfully")
            else:
                raise Exception("SHEET_ID not found in environment")
                
        except Exception as e:
            self.health_status = False
            print(f"❌ Error connecting to Google Sheets: {str(e)}")
    
    def _setup_headers(self):
        """Setup headers in the spreadsheet"""
        try:
            if not self.worksheet:
                return
            
            # Check if headers exist
            headers = self.worksheet.row_values(1)
            expected_headers = ['Tanggal', 'Deskripsi', 'Jumlah', 'Tipe', 'Kategori', 'Saldo', 'Bukti', 'Private']
            
            if not headers or headers != expected_headers:
                # Clear first row and add headers
                self.worksheet.clear()
                self.worksheet.append_row(expected_headers)
                
                # Format headers
                self.worksheet.format('A1:H1', {
                    'backgroundColor': {'red': 0.2, 'green': 0.6, 'blue': 0.8},
                    'textFormat': {'bold': True, 'foregroundColor': {'red': 1, 'green': 1, 'blue': 1}}
                })
                
                print("✅ Headers setup completed")
                
        except Exception as e:
            print(f"Error setting up headers: {str(e)}")
    
    def save_transaction(self, transaction_data: Dict[str, Any]) -> bool:
        """
        Simpan transaksi ke Google Sheets
        
        Args:
            transaction_data: Data transaksi
            
        Returns:
            bool: True jika berhasil, False jika gagal
        """
        try:
            if not self.worksheet:
                self._initialize_connection()
                if not self.worksheet:
                    return False
            
            # Retry mechanism
            for attempt in range(3):
                try:
                    # Prepare row data
                    row_data = [
                        transaction_data.get('tanggal', ''),
                        transaction_data.get('deskripsi', ''),
                        transaction_data.get('jumlah', 0),
                        transaction_data.get('tipe', 'INFO'),
                        transaction_data.get('kategori', 'Lainnya'),
                        transaction_data.get('saldo', 0),
                        transaction_data.get('bukti', ''),
                        transaction_data.get('private', 'No')
                    ]
                    
                    # Append row
                    self.worksheet.append_row(row_data)
                    
                    # Auto-resize columns
                    self.worksheet.columns_auto_resize(0, 7)
                    
                    self.health_status = True
                    print(f"✅ Transaction saved to Sheets: {transaction_data.get('deskripsi', '')}")
                    return True
                    
                except Exception as e:
                    if attempt == 2:  # Last attempt
                        self.health_status = False
                        raise e
                    time.sleep(1)  # Wait before retry
                    
        except Exception as e:
            self.health_status = False
            print(f"❌ Error saving transaction: {str(e)}")
            return False
    
    def get_daily_transactions(self, date: str) -> List[Dict[str, Any]]:
        """
        Ambil transaksi harian
        
        Args:
            date: Tanggal dalam format YYYY-MM-DD
            
        Returns:
            List transaksi harian
        """
        try:
            if not self.worksheet:
                return []
            
            # Get all records
            records = self.worksheet.get_all_records()
            
            # Filter by date
            daily_transactions = []
            for record in records:
                if record.get('Tanggal', '').startswith(date):
                    daily_transactions.append({
                        'tanggal': record.get('Tanggal', ''),
                        'deskripsi': record.get('Deskripsi', ''),
                        'jumlah': int(record.get('Jumlah', 0)),
                        'tipe': record.get('Tipe', 'INFO'),
                        'kategori': record.get('Kategori', 'Lainnya'),
                        'saldo': int(record.get('Saldo', 0)),
                        'bukti': record.get('Bukti', ''),
                        'private': record.get('Private', 'No')
                    })
            
            return daily_transactions
            
        except Exception as e:
            print(f"Error getting daily transactions: {str(e)}")
            return []
    
    def get_current_balance(self) -> int:
        """
        Ambil saldo terbaru dari transaksi terakhir
        
        Returns:
            int: Saldo terbaru
        """
        try:
            if not self.worksheet:
                return 0
            
            # Get all records
            records = self.worksheet.get_all_records()
            
            if records:
                # Get last transaction's balance
                last_record = records[-1]
                return int(last_record.get('Saldo', 0))
            
            return 0
            
        except Exception as e:
            print(f"Error getting current balance: {str(e)}")
            return 0
    
    def get_monthly_summary(self, year: int, month: int) -> Dict[str, Any]:
        """
        Ambil ringkasan bulanan
        
        Args:
            year: Tahun
            month: Bulan (1-12)
            
        Returns:
            Dict ringkasan bulanan
        """
        try:
            if not self.worksheet:
                return {}
            
            # Get all records
            records = self.worksheet.get_all_records()
            
            # Filter by month/year
            monthly_transactions = []
            for record in records:
                tanggal = record.get('Tanggal', '')
                if tanggal:
                    try:
                        record_date = datetime.strptime(tanggal.split()[0], '%Y-%m-%d')
                        if record_date.year == year and record_date.month == month:
                            monthly_transactions.append(record)
                    except:
                        continue
            
            # Calculate summary
            total_income = sum(int(t.get('Jumlah', 0)) for t in monthly_transactions if t.get('Tipe') == 'IN')
            total_expense = sum(int(t.get('Jumlah', 0)) for t in monthly_transactions if t.get('Tipe') == 'OUT')
            
            # Category breakdown
            categories = {}
            for t in monthly_transactions:
                cat = t.get('Kategori', 'Lainnya')
                amount = int(t.get('Jumlah', 0))
                if t.get('Tipe') == 'OUT':  # Only count expenses for categories
                    categories[cat] = categories.get(cat, 0) + amount
            
            return {
                'total_transactions': len(monthly_transactions),
                'total_income': total_income,
                'total_expense': total_expense,
                'net_balance': total_income - total_expense,
                'categories': categories,
                'transactions': monthly_transactions
            }
            
        except Exception as e:
            print(f"Error getting monthly summary: {str(e)}")
            return {}
    
    def get_recent_transactions(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Ambil transaksi terbaru
        
        Args:
            limit: Jumlah transaksi terbaru
            
        Returns:
            List transaksi terbaru
        """
        try:
            if not self.worksheet:
                return []
            
            # Get all records
            records = self.worksheet.get_all_records()
            
            # Get last N records
            recent = records[-limit:] if len(records) > limit else records
            
            # Convert to standard format
            recent_transactions = []
            for record in recent:
                recent_transactions.append({
                    'tanggal': record.get('Tanggal', ''),
                    'deskripsi': record.get('Deskripsi', ''),
                    'jumlah': int(record.get('Jumlah', 0)),
                    'tipe': record.get('Tipe', 'INFO'),
                    'kategori': record.get('Kategori', 'Lainnya'),
                    'saldo': int(record.get('Saldo', 0)),
                    'bukti': record.get('Bukti', ''),
                    'private': record.get('Private', 'No')
                })
            
            return recent_transactions
            
        except Exception as e:
            print(f"Error getting recent transactions: {str(e)}")
            return []
    
    def backup_to_csv(self, filename: str = None) -> bool:
        """
        Backup data ke CSV
        
        Args:
            filename: Nama file CSV (optional)
            
        Returns:
            bool: True jika berhasil
        """
        try:
            if not self.worksheet:
                return False
            
            if not filename:
                filename = f"backup_transactions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            
            # Get all records
            records = self.worksheet.get_all_records()
            
            # Write to CSV
            import csv
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                if records:
                    fieldnames = records[0].keys()
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(records)
            
            print(f"✅ Backup saved to {filename}")
            return True
            
        except Exception as e:
            print(f"Error backing up to CSV: {str(e)}")
            return False
    
    def is_healthy(self) -> bool:
        """Check if service is healthy"""
        return self.health_status
    
    def reconnect(self) -> bool:
        """Reconnect to Google Sheets"""
        try:
            self._initialize_connection()
            return self.health_status
        except Exception as e:
            print(f"Error reconnecting: {str(e)}")
            return False
    
    def get_sheet_info(self) -> Dict[str, Any]:
        """Get spreadsheet information"""
        try:
            if not self.worksheet:
                return {}
            
            return {
                'title': self.worksheet.spreadsheet.title,
                'url': self.worksheet.spreadsheet.url,
                'row_count': self.worksheet.row_count,
                'col_count': self.worksheet.col_count,
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"Error getting sheet info: {str(e)}")
            return {}
