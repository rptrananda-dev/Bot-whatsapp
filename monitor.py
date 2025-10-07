#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Monitor Script untuk Bos Upety Bot PRO 24/7
Script untuk monitoring kesehatan bot dan performa sistem
"""

import os
import json
import time
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Import services
from logger_service import LoggerService
from backup_service import BackupService
from sheets_service import SheetsService
from gemini_service import GeminiService
from drive_service import DriveService

load_dotenv()

class BotMonitor:
    def __init__(self):
        self.logger = LoggerService()
        self.backup = BackupService()
        self.sheets = SheetsService()
        self.gemini = GeminiService()
        self.drive = DriveService()
        
        # Configuration
        self.bot_url = os.getenv('BOT_URL', 'http://localhost:5000')
        self.admin_number = os.getenv('ADMIN', '6282181151735')
        self.bos_number = os.getenv('BOS', '628115302098')
    
    def check_bot_health(self):
        """Check bot health via ping endpoint"""
        try:
            response = requests.get(f"{self.bot_url}/ping", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'status': 'healthy',
                    'timestamp': data.get('timestamp'),
                    'balance': data.get('balance', 0),
                    'transactions': data.get('transactions', 0),
                    'errors': data.get('errors', 0)
                }
            else:
                return {
                    'status': 'unhealthy',
                    'error': f"HTTP {response.status_code}"
                }
                
        except Exception as e:
            return {
                'status': 'unreachable',
                'error': str(e)
            }
    
    def check_services_health(self):
        """Check health of all services"""
        services = {
            'Google Sheets': self.sheets.is_healthy(),
            'Gemini AI': self.gemini.is_healthy(),
            'Google Drive': self.drive.is_healthy(),
            'Logger': True,  # Logger is always healthy if running
            'Backup': True   # Backup is always healthy if running
        }
        
        return services
    
    def get_system_stats(self):
        """Get system statistics"""
        try:
            # Get backup info
            backup_info = self.backup.get_backup_info()
            
            # Get log stats
            log_stats = self.logger.get_log_stats()
            
            # Get error summary
            error_summary = self.logger.get_error_summary()
            
            # Get sheets info
            sheets_info = self.sheets.get_sheet_info()
            
            # Get drive info
            drive_info = self.drive.get_folder_info()
            
            return {
                'backup': backup_info,
                'logs': log_stats,
                'errors': error_summary,
                'sheets': sheets_info,
                'drive': drive_info,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.log_error(f"Error getting system stats: {str(e)}")
            return {}
    
    def generate_health_report(self):
        """Generate comprehensive health report"""
        try:
            # Check bot health
            bot_health = self.check_bot_health()
            
            # Check services health
            services_health = self.check_services_health()
            
            # Get system stats
            system_stats = self.get_system_stats()
            
            # Calculate overall health score
            health_score = 100
            
            # Deduct for bot issues
            if bot_health['status'] != 'healthy':
                health_score -= 30
            
            # Deduct for service issues
            unhealthy_services = sum(1 for status in services_health.values() if not status)
            health_score -= unhealthy_services * 15
            
            # Deduct for errors
            error_count = system_stats.get('errors', {}).get('total_errors', 0)
            health_score -= min(error_count * 2, 20)
            
            health_score = max(health_score, 0)
            
            # Determine status
            if health_score >= 80:
                status = "HEALTHY"
                status_emoji = "✅"
            elif health_score >= 60:
                status = "WARNING"
                status_emoji = "⚠️"
            elif health_score >= 40:
                status = "CRITICAL"
                status_emoji = "🔴"
            else:
                status = "FAILED"
                status_emoji = "❌"
            
            # Generate report
            report = f"""🏥 **SYSTEM HEALTH REPORT**

📅 {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}

{status_emoji} **OVERALL STATUS:** {status}
🎯 **HEALTH SCORE:** {health_score}/100

🤖 **BOT STATUS:**
• Status: {bot_health['status'].upper()}
• Balance: Rp {bot_health.get('balance', 0):,}
• Transactions: {bot_health.get('transactions', 0)}
• Errors: {bot_health.get('errors', 0)}

🔧 **SERVICES STATUS:**
"""
            
            for service, is_healthy in services_health.items():
                emoji = "✅" if is_healthy else "❌"
                report += f"• {service}: {emoji}\n"
            
            # Add system stats
            if system_stats:
                backup_count = system_stats.get('backup', {}).get('transactions_count', 0)
                error_count = system_stats.get('errors', {}).get('total_errors', 0)
                
                report += f"""
📊 **SYSTEM STATS:**
• Backup Transactions: {backup_count}
• Total Errors: {error_count}
• Log Files: {len(system_stats.get('logs', {}))}
"""
            
            # Add recommendations
            recommendations = []
            if health_score < 80:
                recommendations.append("Monitor system more closely")
            if unhealthy_services > 0:
                recommendations.append("Check unhealthy services")
            if error_count > 10:
                recommendations.append("High error count - investigate")
            if bot_health['status'] != 'healthy':
                recommendations.append("Bot health issues detected")
            
            if recommendations:
                report += f"""
💡 **RECOMMENDATIONS:**
"""
                for rec in recommendations:
                    report += f"• {rec}\n"
            
            return report
            
        except Exception as e:
            self.logger.log_error(f"Error generating health report: {str(e)}")
            return f"❌ Failed to generate health report: {str(e)}"
    
    def send_alert(self, message, level="warning"):
        """Send alert via WhatsApp"""
        try:
            import requests
            
            fonnte_token = os.getenv('FONNTE_TOKEN')
            if not fonnte_token:
                return False
            
            # Add timestamp and level
            timestamp = datetime.now().strftime('%H:%M:%S')
            alert_message = f"🚨 **{level.upper()} ALERT**\n\n{message}\n\n⏰ {timestamp}"
            
            # Send to admin
            url = "https://api.fonnte.com/send"
            headers = {'Authorization': fonnte_token}
            data = {
                'target': self.admin_number,
                'message': alert_message
            }
            
            response = requests.post(url, headers=headers, data=data, timeout=10)
            
            if response.status_code == 200:
                self.logger.log_info(f"Alert sent to admin: {level}")
                return True
            else:
                self.logger.log_error(f"Failed to send alert: {response.text}")
                return False
                
        except Exception as e:
            self.logger.log_error(f"Error sending alert: {str(e)}")
            return False
    
    def check_and_alert(self):
        """Check system and send alerts if needed"""
        try:
            # Check bot health
            bot_health = self.check_bot_health()
            
            # Check services
            services_health = self.check_services_health()
            
            # Get error summary
            error_summary = self.logger.get_error_summary()
            
            alerts = []
            
            # Bot health alerts
            if bot_health['status'] != 'healthy':
                alerts.append(f"Bot is {bot_health['status']}: {bot_health.get('error', 'Unknown error')}")
            
            # Service health alerts
            unhealthy_services = [name for name, status in services_health.items() if not status]
            if unhealthy_services:
                alerts.append(f"Unhealthy services: {', '.join(unhealthy_services)}")
            
            # Error count alerts
            recent_errors = len(error_summary.get('recent_errors', []))
            if recent_errors > 5:
                alerts.append(f"High error count: {recent_errors} errors in last 24h")
            
            # Send alerts
            if alerts:
                alert_message = "\\n".join(alerts)
                self.send_alert(alert_message, "critical")
            
            return len(alerts)
            
        except Exception as e:
            self.logger.log_error(f"Error in check and alert: {str(e)}")
            return 0
    
    def run_monitoring_cycle(self):
        """Run one monitoring cycle"""
        try:
            self.logger.log_info("🔍 Running monitoring cycle...")
            
            # Check and alert
            alert_count = self.check_and_alert()
            
            # Generate health report
            health_report = self.generate_health_report()
            
            # Log health report
            self.logger.log_info(f"Health monitoring completed. Alerts: {alert_count}")
            
            return {
                'timestamp': datetime.now().isoformat(),
                'alerts': alert_count,
                'health_report': health_report
            }
            
        except Exception as e:
            self.logger.log_error(f"Error in monitoring cycle: {str(e)}")
            return None

def main():
    """Main monitoring function"""
    print("🔍 Bos Upety Bot PRO 24/7 - System Monitor")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    monitor = BotMonitor()
    
    # Run monitoring cycle
    result = monitor.run_monitoring_cycle()
    
    if result:
        print("✅ Monitoring cycle completed")
        print(f"🚨 Alerts sent: {result['alerts']}")
        
        # Print health report
        print("\n" + result['health_report'])
    else:
        print("❌ Monitoring cycle failed")

if __name__ == '__main__':
    main()
