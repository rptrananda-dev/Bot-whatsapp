#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Backup Service - Backup lokal ke CSV dan recovery system
"""

import os
import csv
import json
import time
import shutil
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv

load_dotenv()

class BackupService:
    def __init__(self):
        self.backup_dir = "backups"
        self.max_backup_files = 30  # Keep 30 days of backups
        self.backup_interval = 24 * 60 * 60  # 24 hours in seconds
        
        # Create backup directory
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir)
        
        # Backup files
        self.transactions_file = os.path.join(self.backup_dir, "transactions.csv")
        self.config_file = os.path.join(self.backup_dir, "config.json")
        self.last_backup_file = os.path.join(self.backup_dir, "last_backup.json")
        
        # Initialize backup system
        self._initialize_backup_system()
    
    def _initialize_backup_system(self):
        """Initialize backup system"""
        try:
            # Create initial backup files if they don't exist
            if not os.path.exists(self.transactions_file):
                self._create_initial_transactions_file()
            
            if not os.path.exists(self.config_file):
                self._create_initial_config_file()
            
            if not os.path.exists(self.last_backup_file):
                self._create_initial_last_backup_file()
            
            print("✅ Backup system initialized")
            
        except Exception as e:
            print(f"❌ Error initializing backup system: {str(e)}")
    
    def _create_initial_transactions_file(self):
        """Create initial transactions CSV file"""
        try:
            headers = ['Tanggal', 'Deskripsi', 'Jumlah', 'Tipe', 'Kategori', 'Saldo', 'Bukti', 'Private']
            
            with open(self.transactions_file, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(headers)
            
            print("✅ Initial transactions file created")
            
        except Exception as e:
            print(f"❌ Error creating initial transactions file: {str(e)}")
    
    def _create_initial_config_file(self):
        """Create initial config file"""
        try:
            config = {
                'backup_created': datetime.now().isoformat(),
                'version': '1.0',
                'settings': {
                    'max_backup_files': self.max_backup_files,
                    'backup_interval': self.backup_interval
                }
            }
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            print("✅ Initial config file created")
            
        except Exception as e:
            print(f"❌ Error creating initial config file: {str(e)}")
    
    def _create_initial_last_backup_file(self):
        """Create initial last backup file"""
        try:
            last_backup = {
                'timestamp': datetime.now().isoformat(),
                'type': 'initial',
                'status': 'success'
            }
            
            with open(self.last_backup_file, 'w', encoding='utf-8') as f:
                json.dump(last_backup, f, indent=2, ensure_ascii=False)
            
            print("✅ Initial last backup file created")
            
        except Exception as e:
            print(f"❌ Error creating initial last backup file: {str(e)}")
    
    def save_transaction(self, transaction_data: Dict[str, Any]) -> bool:
        """
        Save transaction to local CSV backup
        
        Args:
            transaction_data: Transaction data to save
            
        Returns:
            bool: True if successful
        """
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
            
            # Append to CSV file
            with open(self.transactions_file, 'a', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(row_data)
            
            print(f"✅ Transaction backed up locally: {transaction_data.get('deskripsi', '')}")
            return True
            
        except Exception as e:
            print(f"❌ Error saving transaction backup: {str(e)}")
            return False
    
    def get_transactions(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get transactions from local backup
        
        Args:
            limit: Maximum number of transactions to return
            
        Returns:
            List of transactions
        """
        try:
            transactions = []
            
            if not os.path.exists(self.transactions_file):
                return transactions
            
            with open(self.transactions_file, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                
                for row in reader:
                    transaction = {
                        'tanggal': row.get('Tanggal', ''),
                        'deskripsi': row.get('Deskripsi', ''),
                        'jumlah': int(row.get('Jumlah', 0)),
                        'tipe': row.get('Tipe', 'INFO'),
                        'kategori': row.get('Kategori', 'Lainnya'),
                        'saldo': int(row.get('Saldo', 0)),
                        'bukti': row.get('Bukti', ''),
                        'private': row.get('Private', 'No')
                    }
                    transactions.append(transaction)
            
            # Return limited results if specified
            if limit:
                return transactions[-limit:]
            
            return transactions
            
        except Exception as e:
            print(f"❌ Error getting transactions from backup: {str(e)}")
            return []
    
    def get_current_balance(self) -> int:
        """
        Get current balance from local backup
        
        Returns:
            int: Current balance
        """
        try:
            transactions = self.get_transactions()
            
            if transactions:
                return transactions[-1].get('saldo', 0)
            
            return 0
            
        except Exception as e:
            print(f"❌ Error getting current balance from backup: {str(e)}")
            return 0
    
    def create_full_backup(self) -> str:
        """
        Create a full backup with timestamp
        
        Returns:
            str: Backup filename
        """
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_filename = f"full_backup_{timestamp}.csv"
            backup_path = os.path.join(self.backup_dir, backup_filename)
            
            # Copy current transactions file
            if os.path.exists(self.transactions_file):
                shutil.copy2(self.transactions_file, backup_path)
                
                # Update last backup info
                self._update_last_backup_info('full', 'success', backup_filename)
                
                print(f"✅ Full backup created: {backup_filename}")
                return backup_filename
            else:
                print("❌ No transactions file to backup")
                return ""
                
        except Exception as e:
            print(f"❌ Error creating full backup: {str(e)}")
            self._update_last_backup_info('full', 'failed', '')
            return ""
    
    def restore_from_backup(self, backup_filename: str) -> bool:
        """
        Restore from a backup file
        
        Args:
            backup_filename: Name of backup file to restore
            
        Returns:
            bool: True if successful
        """
        try:
            backup_path = os.path.join(self.backup_dir, backup_filename)
            
            if not os.path.exists(backup_path):
                print(f"❌ Backup file not found: {backup_filename}")
                return False
            
            # Create backup of current file
            current_backup = f"restore_backup_{int(time.time())}.csv"
            if os.path.exists(self.transactions_file):
                shutil.copy2(self.transactions_file, os.path.join(self.backup_dir, current_backup))
            
            # Restore from backup
            shutil.copy2(backup_path, self.transactions_file)
            
            print(f"✅ Restored from backup: {backup_filename}")
            return True
            
        except Exception as e:
            print(f"❌ Error restoring from backup: {str(e)}")
            return False
    
    def cleanup_old_backups(self) -> int:
        """
        Clean up old backup files
        
        Returns:
            int: Number of files cleaned up
        """
        try:
            cleaned_count = 0
            
            # Get all backup files
            backup_files = []
            for file in os.listdir(self.backup_dir):
                if file.startswith('full_backup_') and file.endswith('.csv'):
                    file_path = os.path.join(self.backup_dir, file)
                    backup_files.append((file, os.path.getmtime(file_path)))
            
            # Sort by modification time (newest first)
            backup_files.sort(key=lambda x: x[1], reverse=True)
            
            # Keep only max_backup_files
            for file, _ in backup_files[self.max_backup_files:]:
                try:
                    os.remove(os.path.join(self.backup_dir, file))
                    cleaned_count += 1
                except:
                    pass
            
            if cleaned_count > 0:
                print(f"✅ Cleaned up {cleaned_count} old backup files")
            
            return cleaned_count
            
        except Exception as e:
            print(f"❌ Error cleaning up old backups: {str(e)}")
            return 0
    
    def _update_last_backup_info(self, backup_type: str, status: str, filename: str):
        """Update last backup information"""
        try:
            last_backup = {
                'timestamp': datetime.now().isoformat(),
                'type': backup_type,
                'status': status,
                'filename': filename
            }
            
            with open(self.last_backup_file, 'w', encoding='utf-8') as f:
                json.dump(last_backup, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"❌ Error updating last backup info: {str(e)}")
    
    def get_backup_info(self) -> Dict[str, Any]:
        """
        Get backup system information
        
        Returns:
            Dict: Backup information
        """
        try:
            info = {
                'backup_dir': self.backup_dir,
                'transactions_file': self.transactions_file,
                'transactions_count': 0,
                'backup_files': [],
                'last_backup': {},
                'disk_usage': {}
            }
            
            # Get transactions count
            transactions = self.get_transactions()
            info['transactions_count'] = len(transactions)
            
            # Get backup files
            if os.path.exists(self.backup_dir):
                for file in os.listdir(self.backup_dir):
                    if file.endswith('.csv'):
                        file_path = os.path.join(self.backup_dir, file)
                        file_size = os.path.getsize(file_path)
                        file_mtime = os.path.getmtime(file_path)
                        
                        info['backup_files'].append({
                            'filename': file,
                            'size': file_size,
                            'size_mb': round(file_size / (1024 * 1024), 2),
                            'modified': datetime.fromtimestamp(file_mtime).isoformat()
                        })
            
            # Get last backup info
            if os.path.exists(self.last_backup_file):
                with open(self.last_backup_file, 'r', encoding='utf-8') as f:
                    info['last_backup'] = json.load(f)
            
            # Get disk usage
            if os.path.exists(self.backup_dir):
                total_size = 0
                for root, dirs, files in os.walk(self.backup_dir):
                    for file in files:
                        total_size += os.path.getsize(os.path.join(root, file))
                
                info['disk_usage'] = {
                    'total_size': total_size,
                    'total_size_mb': round(total_size / (1024 * 1024), 2)
                }
            
            return info
            
        except Exception as e:
            print(f"❌ Error getting backup info: {str(e)}")
            return {}
    
    def export_to_excel(self, filename: str = None) -> str:
        """
        Export transactions to Excel format
        
        Args:
            filename: Output filename (optional)
            
        Returns:
            str: Output filename
        """
        try:
            if not filename:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"transactions_export_{timestamp}.xlsx"
            
            transactions = self.get_transactions()
            
            if not transactions:
                print("❌ No transactions to export")
                return ""
            
            # Try to use openpyxl if available
            try:
                from openpyxl import Workbook
                
                wb = Workbook()
                ws = wb.active
                ws.title = "Transactions"
                
                # Add headers
                headers = ['Tanggal', 'Deskripsi', 'Jumlah', 'Tipe', 'Kategori', 'Saldo', 'Bukti', 'Private']
                ws.append(headers)
                
                # Add data
                for trans in transactions:
                    row = [
                        trans.get('tanggal', ''),
                        trans.get('deskripsi', ''),
                        trans.get('jumlah', 0),
                        trans.get('tipe', 'INFO'),
                        trans.get('kategori', 'Lainnya'),
                        trans.get('saldo', 0),
                        trans.get('bukti', ''),
                        trans.get('private', 'No')
                    ]
                    ws.append(row)
                
                # Save file
                output_path = os.path.join(self.backup_dir, filename)
                wb.save(output_path)
                
                print(f"✅ Exported to Excel: {filename}")
                return filename
                
            except ImportError:
                print("❌ openpyxl not available, falling back to CSV")
                return self.export_to_csv(filename.replace('.xlsx', '.csv'))
                
        except Exception as e:
            print(f"❌ Error exporting to Excel: {str(e)}")
            return ""
    
    def export_to_csv(self, filename: str = None) -> str:
        """
        Export transactions to CSV format
        
        Args:
            filename: Output filename (optional)
            
        Returns:
            str: Output filename
        """
        try:
            if not filename:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"transactions_export_{timestamp}.csv"
            
            transactions = self.get_transactions()
            
            if not transactions:
                print("❌ No transactions to export")
                return ""
            
            output_path = os.path.join(self.backup_dir, filename)
            
            with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
                if transactions:
                    fieldnames = transactions[0].keys()
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(transactions)
            
            print(f"✅ Exported to CSV: {filename}")
            return filename
            
        except Exception as e:
            print(f"❌ Error exporting to CSV: {str(e)}")
            return ""
    
    def sync_with_sheets(self, sheets_service) -> Dict[str, Any]:
        """
        Sync local backup with Google Sheets
        
        Args:
            sheets_service: SheetsService instance
            
        Returns:
            Dict: Sync results
        """
        try:
            results = {
                'local_count': 0,
                'sheets_count': 0,
                'synced': 0,
                'errors': 0
            }
            
            # Get local transactions
            local_transactions = self.get_transactions()
            results['local_count'] = len(local_transactions)
            
            # Get sheets transactions
            sheets_transactions = sheets_service.get_recent_transactions(1000)
            results['sheets_count'] = len(sheets_transactions)
            
            # Find missing transactions in local backup
            local_descriptions = {t['deskripsi'] + t['tanggal'] for t in local_transactions}
            
            for sheet_trans in sheets_transactions:
                sheet_key = sheet_trans['deskripsi'] + sheet_trans['tanggal']
                
                if sheet_key not in local_descriptions:
                    # Save missing transaction to local backup
                    if self.save_transaction(sheet_trans):
                        results['synced'] += 1
                    else:
                        results['errors'] += 1
            
            print(f"✅ Sync completed: {results['synced']} synced, {results['errors']} errors")
            return results
            
        except Exception as e:
            print(f"❌ Error syncing with sheets: {str(e)}")
            return {
                'local_count': 0,
                'sheets_count': 0,
                'synced': 0,
                'errors': 1
            }
    
    def is_backup_needed(self) -> bool:
        """
        Check if backup is needed based on time interval
        
        Returns:
            bool: True if backup is needed
        """
        try:
            if not os.path.exists(self.last_backup_file):
                return True
            
            with open(self.last_backup_file, 'r', encoding='utf-8') as f:
                last_backup = json.load(f)
            
            last_backup_time = datetime.fromisoformat(last_backup['timestamp'])
            time_diff = datetime.now() - last_backup_time
            
            return time_diff.total_seconds() > self.backup_interval
            
        except Exception as e:
            print(f"❌ Error checking if backup needed: {str(e)}")
            return True
