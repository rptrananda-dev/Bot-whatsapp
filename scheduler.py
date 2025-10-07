#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Scheduler Service - Laporan otomatis dan reminder saldo
"""

import os
import time
import threading
import schedule
from datetime import datetime, timedelta
from typing import Dict, Any
from dotenv import load_dotenv

# Import services
from sheets_service import SheetsService
from gemini_service import GeminiService
from logger_service import LoggerService

load_dotenv()

class SchedulerService:
    def __init__(self):
        self.sheets = SheetsService()
        self.gemini = GeminiService()
        self.logger = LoggerService()
        self.running = False
        self.thread = None
        
        # Configuration
        self.admin_number = os.getenv('ADMIN', '6282181151735')
        self.bos_number = os.getenv('BOS', '628115302098')
        
        # Setup schedules
        self._setup_schedules()
    
    def _setup_schedules(self):
        """Setup scheduled tasks"""
        # Daily report at 23:50
        schedule.every().day.at("23:50").do(self._send_daily_report)
        
        # Morning balance reminder at 06:00
        schedule.every().day.at("06:00").do(self._send_balance_reminder)
        
        # System performance report at 00:00
        schedule.every().day.at("00:00").do(self._send_system_report)
        
        # Weekly backup every Sunday at 01:00
        schedule.every().sunday.at("01:00").do(self._weekly_backup)
        
        # Monthly insights every 1st at 08:00
        schedule.every().month.do(self._send_monthly_insights)
        
        print("✅ Schedules configured")
    
    def start(self):
        """Start the scheduler"""
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._run_scheduler, daemon=True)
            self.thread.start()
            self.logger.log_info("🕐 Scheduler started")
    
    def stop(self):
        """Stop the scheduler"""
        self.running = False
        if self.thread:
            self.thread.join()
        self.logger.log_info("⏹️ Scheduler stopped")
    
    def _run_scheduler(self):
        """Run the scheduler loop"""
        while self.running:
            try:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
            except Exception as e:
                self.logger.log_error(f"Scheduler error: {str(e)}")
                time.sleep(60)
    
    def _send_daily_report(self):
        """Send daily report to bos and admin"""
        try:
            today = datetime.now().strftime('%Y-%m-%d')
            transactions = self.sheets.get_daily_transactions(today)
            
            if not transactions:
                message = f"""📊 **LAPORAN HARIAN**
                
📅 {today}
💰 Saldo: Rp {self.sheets.get_current_balance():,}
📝 Tidak ada transaksi hari ini

🤖 Bot berjalan normal 24/7"""
            else:
                total_income = sum(t.get('jumlah', 0) for t in transactions if t.get('tipe') == 'IN')
                total_expense = sum(t.get('jumlah', 0) for t in transactions if t.get('tipe') == 'OUT')
                
                message = f"""📊 **LAPORAN HARIAN**
                
📅 {today}
💰 Saldo: Rp {self.sheets.get_current_balance():,}

📈 **PEMASUKAN:** Rp {total_income:,}
📉 **PENGELUARAN:** Rp {total_expense:,}
📝 **TOTAL TRANSAKSI:** {len(transactions)}

🔍 **TRANSAKSI TERBARU:**
"""
                
                # Show last 5 transactions
                for i, trans in enumerate(transactions[-5:], 1):
                    emoji = "📈" if trans.get('tipe') == 'IN' else "📉"
                    message += f"{i}. {emoji} {trans.get('deskripsi', '')} - Rp {trans.get('jumlah', 0):,}\n"
                
                # Add AI insights
                insights = self.gemini.get_insights(transactions)
                if insights:
                    message += f"\n{insights}"
            
            # Send to both numbers
            self._send_whatsapp_message(self.bos_number, message)
            self._send_whatsapp_message(self.admin_number, message)
            
            self.logger.log_info("📊 Daily report sent")
            
        except Exception as e:
            self.logger.log_error(f"Error sending daily report: {str(e)}")
    
    def _send_balance_reminder(self):
        """Send morning balance reminder"""
        try:
            current_balance = self.sheets.get_current_balance()
            today = datetime.now().strftime('%d/%m/%Y')
            
            message = f"""🌅 **REMINDER SALDO PAGI**

💰 **Saldo Terkini:** Rp {current_balance:,}
📅 {today}

💡 **Tips Hari Ini:**
• Catat semua transaksi dengan detail
• Kirim foto bukti untuk transaksi penting
• Ketik "laporan" untuk cek laporan harian

🤖 Bos Upety Bot PRO 24/7 siap melayani!"""
            
            # Send to both numbers
            self._send_whatsapp_message(self.bos_number, message)
            self._send_whatsapp_message(self.admin_number, message)
            
            self.logger.log_info("🌅 Balance reminder sent")
            
        except Exception as e:
            self.logger.log_error(f"Error sending balance reminder: {str(e)}")
    
    def _send_system_report(self):
        """Send system performance report"""
        try:
            # Get system stats
            recent_transactions = self.sheets.get_recent_transactions(100)
            total_transactions = len(recent_transactions)
            
            # Calculate stats
            today = datetime.now().strftime('%Y-%m-%d')
            daily_transactions = self.sheets.get_daily_transactions(today)
            
            # Get error count from logs
            error_count = self._get_error_count_today()
            
            message = f"""🤖 **LAPORAN PERFORMA SISTEM**

📅 {datetime.now().strftime('%d/%m/%Y %H:%M')}

📊 **STATISTIK:**
• Total Transaksi: {total_transactions}
• Transaksi Hari Ini: {len(daily_transactions)}
• Error Count: {error_count}
• Saldo Terkini: Rp {self.sheets.get_current_balance():,}

🔧 **STATUS LAYANAN:**
• Google Sheets: {'✅' if self.sheets.is_healthy() else '❌'}
• Gemini AI: {'✅' if self.gemini.is_healthy() else '❌'}
• Scheduler: {'✅' if self.running else '❌'}

🕐 **JADWAL OTOMATIS:**
• 23:50 - Laporan Harian
• 06:00 - Reminder Saldo
• 00:00 - Laporan Performa (ini)

🤖 Bot berjalan normal 24/7"""
            
            # Send to admin only
            self._send_whatsapp_message(self.admin_number, message)
            
            self.logger.log_info("🤖 System report sent")
            
        except Exception as e:
            self.logger.log_error(f"Error sending system report: {str(e)}")
    
    def _send_monthly_insights(self):
        """Send monthly insights and summary"""
        try:
            now = datetime.now()
            last_month = now - timedelta(days=30)
            
            # Get monthly summary
            monthly_data = self.sheets.get_monthly_summary(now.year, now.month)
            
            if not monthly_data:
                return
            
            message = f"""📈 **LAPORAN BULANAN**

📅 {now.strftime('%B %Y')}

💰 **RINGKASAN KEUANGAN:**
• Total Pemasukan: Rp {monthly_data.get('total_income', 0):,}
• Total Pengeluaran: Rp {monthly_data.get('total_expense', 0):,}
• Saldo Bersih: Rp {monthly_data.get('net_balance', 0):,}
• Total Transaksi: {monthly_data.get('total_transactions', 0)}

🏆 **KATEGORI TERBANYAK:**
"""
            
            # Show top 3 categories
            categories = monthly_data.get('categories', {})
            sorted_categories = sorted(categories.items(), key=lambda x: x[1], reverse=True)
            
            for i, (category, amount) in enumerate(sorted_categories[:3], 1):
                message += f"{i}. {category}: Rp {amount:,}\n"
            
            # Add AI insights
            transactions = monthly_data.get('transactions', [])
            insights = self.gemini.get_insights(transactions)
            if insights:
                message += f"\n{insights}"
            
            # Send to both numbers
            self._send_whatsapp_message(self.bos_number, message)
            self._send_whatsapp_message(self.admin_number, message)
            
            self.logger.log_info("📈 Monthly insights sent")
            
        except Exception as e:
            self.logger.log_error(f"Error sending monthly insights: {str(e)}")
    
    def _weekly_backup(self):
        """Perform weekly backup"""
        try:
            # Backup to CSV
            backup_filename = f"weekly_backup_{datetime.now().strftime('%Y%m%d')}.csv"
            success = self.sheets.backup_to_csv(backup_filename)
            
            if success:
                self.logger.log_info(f"📦 Weekly backup completed: {backup_filename}")
            else:
                self.logger.log_error("❌ Weekly backup failed")
                
        except Exception as e:
            self.logger.log_error(f"Error in weekly backup: {str(e)}")
    
    def _get_error_count_today(self) -> int:
        """Get error count for today"""
        try:
            # This would typically read from log files
            # For now, return 0 as placeholder
            return 0
        except Exception as e:
            self.logger.log_error(f"Error getting error count: {str(e)}")
            return 0
    
    def _send_whatsapp_message(self, phone: str, message: str) -> bool:
        """Send WhatsApp message via Fonnte API"""
        try:
            import requests
            
            fonnte_token = os.getenv('FONNTE_TOKEN')
            if not fonnte_token:
                self.logger.log_error("FONNTE_TOKEN not found")
                return False
            
            url = "https://api.fonnte.com/send"
            headers = {
                'Authorization': fonnte_token
            }
            data = {
                'target': phone,
                'message': message
            }
            
            response = requests.post(url, headers=headers, data=data, timeout=10)
            
            if response.status_code == 200:
                self.logger.log_info(f"✅ Message sent to {phone}")
                return True
            else:
                self.logger.log_error(f"❌ Failed to send message to {phone}: {response.text}")
                return False
                
        except Exception as e:
            self.logger.log_error(f"Error sending WhatsApp message: {str(e)}")
            return False
    
    def get_schedule_info(self) -> Dict[str, Any]:
        """Get schedule information"""
        return {
            'running': self.running,
            'schedules': [
                {'task': 'Daily Report', 'time': '23:50', 'enabled': True},
                {'task': 'Balance Reminder', 'time': '06:00', 'enabled': True},
                {'task': 'System Report', 'time': '00:00', 'enabled': True},
                {'task': 'Weekly Backup', 'time': 'Sunday 01:00', 'enabled': True},
                {'task': 'Monthly Insights', 'time': '1st 08:00', 'enabled': True}
            ],
            'next_run': str(schedule.next_run()) if schedule.jobs else None
        }
    
    def run_manual_task(self, task_name: str) -> bool:
        """Run a scheduled task manually"""
        try:
            if task_name == 'daily_report':
                self._send_daily_report()
                return True
            elif task_name == 'balance_reminder':
                self._send_balance_reminder()
                return True
            elif task_name == 'system_report':
                self._send_system_report()
                return True
            elif task_name == 'weekly_backup':
                self._weekly_backup()
                return True
            elif task_name == 'monthly_insights':
                self._send_monthly_insights()
                return True
            else:
                self.logger.log_error(f"Unknown task: {task_name}")
                return False
                
        except Exception as e:
            self.logger.log_error(f"Error running manual task {task_name}: {str(e)}")
            return False
