#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Logger Service - Logging dan recovery system
"""

import os
import json
import time
import traceback
from datetime import datetime
from typing import Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()

class LoggerService:
    def __init__(self):
        self.log_dir = "logs"
        self.max_log_size = 10 * 1024 * 1024  # 10MB
        self.max_log_files = 5
        
        # Create log directory
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)
        
        # Log files
        self.info_log = os.path.join(self.log_dir, "info.log")
        self.error_log = os.path.join(self.log_dir, "error.log")
        self.warning_log = os.path.join(self.log_dir, "warning.log")
        self.debug_log = os.path.join(self.log_dir, "debug.log")
        
        # Error tracking
        self.error_count = 0
        self.last_error_time = None
        
        # Initialize
        self._cleanup_old_logs()
        self.log_info("🚀 Logger Service initialized")
    
    def _get_timestamp(self) -> str:
        """Get formatted timestamp"""
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    def _write_log(self, log_file: str, level: str, message: str, exception: Optional[Exception] = None):
        """Write log entry to file"""
        try:
            timestamp = self._get_timestamp()
            log_entry = f"[{timestamp}] [{level}] {message}\n"
            
            if exception:
                log_entry += f"Exception: {str(exception)}\n"
                log_entry += f"Traceback: {traceback.format_exc()}\n"
            
            # Write to file
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(log_entry)
            
            # Check file size and rotate if needed
            self._rotate_log_if_needed(log_file)
            
        except Exception as e:
            print(f"Error writing to log file: {str(e)}")
    
    def _rotate_log_if_needed(self, log_file: str):
        """Rotate log file if it's too large"""
        try:
            if os.path.exists(log_file) and os.path.getsize(log_file) > self.max_log_size:
                # Create backup
                backup_file = f"{log_file}.{int(time.time())}"
                os.rename(log_file, backup_file)
                
                # Clean up old backups
                self._cleanup_old_logs()
                
        except Exception as e:
            print(f"Error rotating log file: {str(e)}")
    
    def _cleanup_old_logs(self):
        """Clean up old log files"""
        try:
            log_files = []
            for file in os.listdir(self.log_dir):
                if file.endswith('.log') or file.endswith('.log.'):
                    log_files.append(os.path.join(self.log_dir, file))
            
            # Sort by modification time
            log_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
            
            # Keep only max_log_files
            for old_file in log_files[self.max_log_files:]:
                try:
                    os.remove(old_file)
                except:
                    pass
                    
        except Exception as e:
            print(f"Error cleaning up old logs: {str(e)}")
    
    def log_info(self, message: str):
        """Log info message"""
        self._write_log(self.info_log, "INFO", message)
        print(f"ℹ️ {message}")
    
    def log_error(self, message: str, exception: Optional[Exception] = None):
        """Log error message"""
        self.error_count += 1
        self.last_error_time = datetime.now()
        
        self._write_log(self.error_log, "ERROR", message, exception)
        print(f"❌ {message}")
        
        # Save error to recovery file
        self._save_error_for_recovery(message, exception)
    
    def log_warning(self, message: str):
        """Log warning message"""
        self._write_log(self.warning_log, "WARNING", message)
        print(f"⚠️ {message}")
    
    def log_debug(self, message: str):
        """Log debug message"""
        self._write_log(self.debug_log, "DEBUG", message)
        print(f"🐛 {message}")
    
    def _save_error_for_recovery(self, message: str, exception: Optional[Exception] = None):
        """Save error information for recovery analysis"""
        try:
            error_data = {
                'timestamp': self._get_timestamp(),
                'message': message,
                'exception': str(exception) if exception else None,
                'traceback': traceback.format_exc() if exception else None,
                'error_count': self.error_count
            }
            
            recovery_file = os.path.join(self.log_dir, "recovery.json")
            
            # Load existing errors
            errors = []
            if os.path.exists(recovery_file):
                try:
                    with open(recovery_file, 'r', encoding='utf-8') as f:
                        errors = json.load(f)
                except:
                    errors = []
            
            # Add new error
            errors.append(error_data)
            
            # Keep only last 100 errors
            if len(errors) > 100:
                errors = errors[-100:]
            
            # Save back
            with open(recovery_file, 'w', encoding='utf-8') as f:
                json.dump(errors, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"Error saving error for recovery: {str(e)}")
    
    def get_error_summary(self) -> Dict[str, Any]:
        """Get error summary for monitoring"""
        try:
            recovery_file = os.path.join(self.log_dir, "recovery.json")
            
            if not os.path.exists(recovery_file):
                return {
                    'total_errors': 0,
                    'recent_errors': [],
                    'last_error_time': None
                }
            
            with open(recovery_file, 'r', encoding='utf-8') as f:
                errors = json.load(f)
            
            # Get recent errors (last 24 hours)
            recent_errors = []
            cutoff_time = datetime.now().timestamp() - (24 * 60 * 60)
            
            for error in errors[-10:]:  # Last 10 errors
                try:
                    error_time = datetime.strptime(error['timestamp'], '%Y-%m-%d %H:%M:%S').timestamp()
                    if error_time > cutoff_time:
                        recent_errors.append(error)
                except:
                    pass
            
            return {
                'total_errors': len(errors),
                'recent_errors': recent_errors,
                'last_error_time': self.last_error_time.isoformat() if self.last_error_time else None,
                'error_count': self.error_count
            }
            
        except Exception as e:
            print(f"Error getting error summary: {str(e)}")
            return {
                'total_errors': 0,
                'recent_errors': [],
                'last_error_time': None,
                'error_count': self.error_count
            }
    
    def get_log_stats(self) -> Dict[str, Any]:
        """Get log file statistics"""
        try:
            stats = {}
            
            for log_type in ['info', 'error', 'warning', 'debug']:
                log_file = getattr(self, f"{log_type}_log")
                
                if os.path.exists(log_file):
                    size = os.path.getsize(log_file)
                    mtime = os.path.getmtime(log_file)
                    
                    stats[log_type] = {
                        'size': size,
                        'size_mb': round(size / (1024 * 1024), 2),
                        'last_modified': datetime.fromtimestamp(mtime).isoformat(),
                        'exists': True
                    }
                else:
                    stats[log_type] = {
                        'size': 0,
                        'size_mb': 0,
                        'last_modified': None,
                        'exists': False
                    }
            
            return stats
            
        except Exception as e:
            print(f"Error getting log stats: {str(e)}")
            return {}
    
    def clear_logs(self, log_type: str = 'all'):
        """Clear log files"""
        try:
            if log_type == 'all':
                log_files = [self.info_log, self.error_log, self.warning_log, self.debug_log]
            else:
                log_file = getattr(self, f"{log_type}_log", None)
                log_files = [log_file] if log_file else []
            
            for log_file in log_files:
                if os.path.exists(log_file):
                    with open(log_file, 'w', encoding='utf-8') as f:
                        f.write("")
            
            self.log_info(f"Cleared {log_type} logs")
            
        except Exception as e:
            self.log_error(f"Error clearing logs: {str(e)}")
    
    def export_logs(self, output_file: str = None) -> str:
        """Export all logs to a single file"""
        try:
            if not output_file:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                output_file = os.path.join(self.log_dir, f"exported_logs_{timestamp}.txt")
            
            with open(output_file, 'w', encoding='utf-8') as outfile:
                outfile.write("=== BOS UPETY BOT LOGS EXPORT ===\n")
                outfile.write(f"Export Date: {self._get_timestamp()}\n\n")
                
                # Export each log type
                for log_type in ['info', 'error', 'warning', 'debug']:
                    log_file = getattr(self, f"{log_type}_log")
                    
                    if os.path.exists(log_file):
                        outfile.write(f"=== {log_type.upper()} LOGS ===\n")
                        
                        with open(log_file, 'r', encoding='utf-8') as infile:
                            outfile.write(infile.read())
                        
                        outfile.write("\n\n")
            
            self.log_info(f"Logs exported to: {output_file}")
            return output_file
            
        except Exception as e:
            self.log_error(f"Error exporting logs: {str(e)}")
            return ""
    
    def monitor_system_health(self) -> Dict[str, Any]:
        """Monitor system health based on logs"""
        try:
            error_summary = self.get_error_summary()
            log_stats = self.get_log_stats()
            
            # Calculate health score
            health_score = 100
            
            # Deduct points for errors
            if error_summary['total_errors'] > 0:
                health_score -= min(error_summary['total_errors'] * 2, 50)
            
            # Deduct points for recent errors
            recent_error_count = len(error_summary['recent_errors'])
            if recent_error_count > 0:
                health_score -= min(recent_error_count * 5, 30)
            
            # Check log file sizes
            for log_type, stats in log_stats.items():
                if stats['size_mb'] > 50:  # If any log is over 50MB
                    health_score -= 10
            
            health_score = max(health_score, 0)
            
            # Determine health status
            if health_score >= 80:
                status = "HEALTHY"
            elif health_score >= 60:
                status = "WARNING"
            elif health_score >= 40:
                status = "CRITICAL"
            else:
                status = "FAILED"
            
            return {
                'health_score': health_score,
                'status': status,
                'error_summary': error_summary,
                'log_stats': log_stats,
                'recommendations': self._get_health_recommendations(health_score, error_summary)
            }
            
        except Exception as e:
            self.log_error(f"Error monitoring system health: {str(e)}")
            return {
                'health_score': 0,
                'status': 'UNKNOWN',
                'error_summary': {},
                'log_stats': {},
                'recommendations': ['System health check failed']
            }
    
    def _get_health_recommendations(self, health_score: int, error_summary: Dict) -> list:
        """Get health recommendations based on current status"""
        recommendations = []
        
        if health_score < 80:
            recommendations.append("Monitor error logs more closely")
        
        if error_summary['total_errors'] > 10:
            recommendations.append("High error count detected - check system stability")
        
        if len(error_summary['recent_errors']) > 5:
            recommendations.append("Recent errors detected - investigate immediately")
        
        if health_score < 40:
            recommendations.append("System health critical - consider restart")
        
        if not recommendations:
            recommendations.append("System running normally")
        
        return recommendations
    
    def create_health_report(self) -> str:
        """Create a comprehensive health report"""
        try:
            health_data = self.monitor_system_health()
            error_summary = health_data['error_summary']
            log_stats = health_data['log_stats']
            
            report = f"""🏥 **SYSTEM HEALTH REPORT**

📅 {self._get_timestamp()}

🎯 **HEALTH SCORE:** {health_data['health_score']}/100
📊 **STATUS:** {health_data['status']}

📈 **ERROR SUMMARY:**
• Total Errors: {error_summary['total_errors']}
• Recent Errors (24h): {len(error_summary['recent_errors'])}
• Last Error: {error_summary['last_error_time'] or 'None'}

📁 **LOG STATS:**
"""
            
            for log_type, stats in log_stats.items():
                status_emoji = "✅" if stats['exists'] else "❌"
                report += f"• {log_type.title()}: {status_emoji} {stats['size_mb']}MB\n"
            
            report += f"""
💡 **RECOMMENDATIONS:**
"""
            
            for rec in health_data['recommendations']:
                report += f"• {rec}\n"
            
            return report
            
        except Exception as e:
            self.log_error(f"Error creating health report: {str(e)}")
            return "❌ Failed to create health report"
