#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Maintenance Script untuk Bos Upety Bot PRO 24/7
Script untuk maintenance, cleanup, dan optimasi sistem
"""

import os
import json
import time
import shutil
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Import services
from logger_service import LoggerService
from backup_service import BackupService
from sheets_service import SheetsService
from drive_service import DriveService

load_dotenv()

class BotMaintenance:
    def __init__(self):
        self.logger = LoggerService()
        self.backup = BackupService()
        self.sheets = SheetsService()
        self.drive = DriveService()
        
        # Maintenance settings
        self.max_log_age_days = 30
        self.max_backup_age_days = 90
        self.max_drive_files = 1000
        self.cleanup_threshold_mb = 100  # Cleanup if logs > 100MB
    
    def cleanup_logs(self):
        """Clean up old log files"""
        try:
            print("🧹 Cleaning up log files...")
            
            log_dir = "logs"
            if not os.path.exists(log_dir):
                print("   No logs directory found")
                return 0
            
            cleaned_count = 0
            cutoff_date = datetime.now() - timedelta(days=self.max_log_age_days)
            
            for file in os.listdir(log_dir):
                file_path = os.path.join(log_dir, file)
                
                if os.path.isfile(file_path):
                    file_mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
                    
                    if file_mtime < cutoff_date:
                        try:
                            os.remove(file_path)
                            cleaned_count += 1
                            print(f"   Removed: {file}")
                        except Exception as e:
                            print(f"   Error removing {file}: {str(e)}")
            
            print(f"✅ Cleaned up {cleaned_count} old log files")
            return cleaned_count
            
        except Exception as e:
            print(f"❌ Error cleaning logs: {str(e)}")
            return 0
    
    def cleanup_backups(self):
        """Clean up old backup files"""
        try:
            print("🧹 Cleaning up backup files...")
            
            cleaned_count = self.backup.cleanup_old_backups()
            print(f"✅ Cleaned up {cleaned_count} old backup files")
            return cleaned_count
            
        except Exception as e:
            print(f"❌ Error cleaning backups: {str(e)}")
            return 0
    
    def cleanup_drive_files(self):
        """Clean up old files in Google Drive"""
        try:
            print("🧹 Cleaning up Google Drive files...")
            
            if not self.drive.is_healthy():
                print("   Google Drive not available")
                return 0
            
            # Clean up files older than 90 days
            cleaned_count = self.drive.cleanup_old_files(days=90)
            print(f"✅ Cleaned up {cleaned_count} old Drive files")
            return cleaned_count
            
        except Exception as e:
            print(f"❌ Error cleaning Drive files: {str(e)}")
            return 0
    
    def optimize_logs(self):
        """Optimize log files by rotating large ones"""
        try:
            print("⚡ Optimizing log files...")
            
            log_dir = "logs"
            if not os.path.exists(log_dir):
                return 0
            
            optimized_count = 0
            
            for file in os.listdir(log_dir):
                if file.endswith('.log'):
                    file_path = os.path.join(log_dir, file)
                    file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
                    
                    if file_size_mb > 10:  # If log file > 10MB
                        # Rotate the log file
                        timestamp = int(time.time())
                        new_name = f"{file}.{timestamp}"
                        shutil.move(file_path, os.path.join(log_dir, new_name))
                        
                        # Create new empty log file
                        with open(file_path, 'w') as f:
                            f.write("")
                        
                        optimized_count += 1
                        print(f"   Rotated: {file} ({file_size_mb:.1f}MB)")
            
            print(f"✅ Optimized {optimized_count} log files")
            return optimized_count
            
        except Exception as e:
            print(f"❌ Error optimizing logs: {str(e)}")
            return 0
    
    def backup_system_data(self):
        """Create system data backup"""
        try:
            print("💾 Creating system data backup...")
            
            # Create backup directory with timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_dir = f"system_backup_{timestamp}"
            
            if not os.path.exists(backup_dir):
                os.makedirs(backup_dir)
            
            # Backup important files
            files_to_backup = [
                'logs',
                'backups',
                'config.env'
            ]
            
            backed_up = 0
            for item in files_to_backup:
                if os.path.exists(item):
                    if os.path.isdir(item):
                        shutil.copytree(item, os.path.join(backup_dir, item))
                    else:
                        shutil.copy2(item, os.path.join(backup_dir, item))
                    backed_up += 1
            
            # Create backup info
            backup_info = {
                'timestamp': datetime.now().isoformat(),
                'backup_type': 'system_maintenance',
                'files_backed_up': backed_up,
                'backup_size_mb': self._get_dir_size_mb(backup_dir)
            }
            
            with open(os.path.join(backup_dir, 'backup_info.json'), 'w') as f:
                json.dump(backup_info, f, indent=2)
            
            print(f"✅ System backup created: {backup_dir}")
            return backup_dir
            
        except Exception as e:
            print(f"❌ Error creating system backup: {str(e)}")
            return None
    
    def _get_dir_size_mb(self, directory):
        """Get directory size in MB"""
        try:
            total_size = 0
            for root, dirs, files in os.walk(directory):
                for file in files:
                    total_size += os.path.getsize(os.path.join(root, file))
            return round(total_size / (1024 * 1024), 2)
        except:
            return 0
    
    def check_disk_space(self):
        """Check available disk space"""
        try:
            print("💽 Checking disk space...")
            
            # Get current directory disk usage
            total, used, free = shutil.disk_usage('.')
            
            total_gb = total / (1024**3)
            used_gb = used / (1024**3)
            free_gb = free / (1024**3)
            usage_percent = (used / total) * 100
            
            print(f"   Total: {total_gb:.1f} GB")
            print(f"   Used: {used_gb:.1f} GB ({usage_percent:.1f}%)")
            print(f"   Free: {free_gb:.1f} GB")
            
            # Alert if disk space is low
            if free_gb < 1:  # Less than 1GB free
                print("⚠️ WARNING: Low disk space!")
                return False
            elif usage_percent > 80:  # More than 80% used
                print("⚠️ WARNING: High disk usage!")
                return False
            
            print("✅ Disk space OK")
            return True
            
        except Exception as e:
            print(f"❌ Error checking disk space: {str(e)}")
            return False
    
    def optimize_database(self):
        """Optimize database/backup files"""
        try:
            print("⚡ Optimizing database...")
            
            # Get backup info
            backup_info = self.backup.get_backup_info()
            
            # Check if backup needs optimization
            transactions_count = backup_info.get('transactions_count', 0)
            
            if transactions_count > 1000:
                # Create optimized backup
                optimized_file = self.backup.export_to_csv("optimized_backup.csv")
                if optimized_file:
                    print(f"✅ Created optimized backup: {optimized_file}")
                    return True
            
            print("✅ Database optimization not needed")
            return True
            
        except Exception as e:
            print(f"❌ Error optimizing database: {str(e)}")
            return False
    
    def run_full_maintenance(self):
        """Run full maintenance cycle"""
        try:
            print("🔧 Bos Upety Bot PRO 24/7 - Full Maintenance")
            print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("=" * 60)
            
            results = {
                'timestamp': datetime.now().isoformat(),
                'logs_cleaned': 0,
                'backups_cleaned': 0,
                'drive_files_cleaned': 0,
                'logs_optimized': 0,
                'system_backup': None,
                'disk_space_ok': False,
                'database_optimized': False
            }
            
            # Check disk space first
            results['disk_space_ok'] = self.check_disk_space()
            
            # Cleanup operations
            results['logs_cleaned'] = self.cleanup_logs()
            results['backups_cleaned'] = self.cleanup_backups()
            results['drive_files_cleaned'] = self.cleanup_drive_files()
            
            # Optimization operations
            results['logs_optimized'] = self.optimize_logs()
            results['database_optimized'] = self.optimize_database()
            
            # Create system backup
            results['system_backup'] = self.backup_system_data()
            
            # Log maintenance results
            self.logger.log_info(f"Maintenance completed: {results}")
            
            # Print summary
            print("\n" + "=" * 60)
            print("📊 MAINTENANCE SUMMARY")
            print("=" * 60)
            print(f"✅ Logs cleaned: {results['logs_cleaned']}")
            print(f"✅ Backups cleaned: {results['backups_cleaned']}")
            print(f"✅ Drive files cleaned: {results['drive_files_cleaned']}")
            print(f"✅ Logs optimized: {results['logs_optimized']}")
            print(f"✅ Database optimized: {results['database_optimized']}")
            print(f"✅ System backup: {results['system_backup'] or 'Failed'}")
            print(f"✅ Disk space: {'OK' if results['disk_space_ok'] else 'WARNING'}")
            
            return results
            
        except Exception as e:
            self.logger.log_error(f"Error in full maintenance: {str(e)}")
            return None
    
    def run_quick_maintenance(self):
        """Run quick maintenance (cleanup only)"""
        try:
            print("⚡ Quick Maintenance - Cleanup Only")
            print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("=" * 40)
            
            # Quick cleanup
            logs_cleaned = self.cleanup_logs()
            backups_cleaned = self.cleanup_backups()
            
            print(f"\n✅ Quick maintenance completed:")
            print(f"   Logs cleaned: {logs_cleaned}")
            print(f"   Backups cleaned: {backups_cleaned}")
            
            return {
                'logs_cleaned': logs_cleaned,
                'backups_cleaned': backups_cleaned,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.log_error(f"Error in quick maintenance: {str(e)}")
            return None

def main():
    """Main maintenance function"""
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'quick':
        # Quick maintenance
        maintenance = BotMaintenance()
        result = maintenance.run_quick_maintenance()
    else:
        # Full maintenance
        maintenance = BotMaintenance()
        result = maintenance.run_full_maintenance()
    
    if result:
        print("\n🎉 Maintenance completed successfully!")
    else:
        print("\n❌ Maintenance failed!")

if __name__ == '__main__':
    main()
