#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bos Upety Bot PRO 24/7 - WhatsApp Financial Management Bot
Main webhook handler untuk menerima pesan dari Fonnte API
"""

import os
import sys
import json
import time
import threading
from datetime import datetime
from flask import Flask, request, jsonify
from dotenv import load_dotenv

# Import custom services
from gemini_service import GeminiService
from sheets_service import SheetsService
from drive_service import DriveService
from scheduler import SchedulerService
from logger_service import LoggerService
from backup_service import BackupService

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Initialize services
gemini = GeminiService()
sheets = SheetsService()
drive = DriveService()
logger = LoggerService()
backup = BackupService()

# Configuration
FONNTE_TOKEN = os.getenv('FONNTE_TOKEN')
ADMIN_NUMBER = os.getenv('ADMIN', '6282181151735')
BOS_NUMBER = os.getenv('BOS', '628115302098')
ALLOWED_NUMBERS = [ADMIN_NUMBER, BOS_NUMBER]

# Global variables
current_balance = 0
transaction_count = 0
error_count = 0

def send_whatsapp_message(phone, message):
    """Kirim pesan WhatsApp via Fonnte API"""
    try:
        import requests
        
        url = "https://api.fonnte.com/send"
        headers = {
            'Authorization': FONNTE_TOKEN
        }
        data = {
            'target': phone,
            'message': message
        }
        
        response = requests.post(url, headers=headers, data=data, timeout=10)
        
        if response.status_code == 200:
            logger.log_info(f"Pesan berhasil dikirim ke {phone}")
            return True
        else:
            logger.log_error(f"Gagal kirim pesan ke {phone}: {response.text}")
            return False
            
    except Exception as e:
        logger.log_error(f"Error kirim WhatsApp: {str(e)}")
        return False

def process_transaction(message_text, sender_phone, media_url=None):
    """Proses transaksi dengan AI dan simpan ke Sheets"""
    global current_balance, transaction_count
    
    try:
        # Analisis dengan Gemini AI
        ai_result = gemini.analyze_transaction(message_text, media_url)
        
        if not ai_result:
            return "❌ Gagal menganalisis transaksi. Coba lagi."
        
        # Simpan ke Google Sheets
        transaction_data = {
            'tanggal': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'deskripsi': ai_result.get('deskripsi', ''),
            'jumlah': ai_result.get('jumlah', 0),
            'tipe': ai_result.get('tipe', 'INFO'),
            'kategori': ai_result.get('kategori', 'Lainnya'),
            'saldo': current_balance,
            'bukti': ai_result.get('bukti', ''),
            'private': 'No'
        }
        
        # Update saldo
        if ai_result.get('tipe') == 'IN':
            current_balance += ai_result.get('jumlah', 0)
        elif ai_result.get('tipe') == 'OUT':
            current_balance -= ai_result.get('jumlah', 0)
        
        transaction_data['saldo'] = current_balance
        
        # Simpan ke Sheets
        success = sheets.save_transaction(transaction_data)
        
        if success:
            transaction_count += 1
            # Backup ke CSV
            backup.save_transaction(transaction_data)
            
            return ai_result.get('tanggapan_bot', '✅ Transaksi berhasil dicatat!')
        else:
            return "❌ Gagal menyimpan transaksi. Coba lagi."
            
    except Exception as e:
        logger.log_error(f"Error proses transaksi: {str(e)}")
        return "❌ Terjadi kesalahan sistem. Coba lagi."

def handle_special_commands(message_text, sender_phone):
    """Handle perintah khusus dari bos/admin"""
    global current_balance
    
    message_lower = message_text.lower()
    
    if 'laporan hari ini' in message_lower or 'laporan' in message_lower:
        return generate_daily_report()
    
    elif 'saldo' in message_lower:
        return f"💰 **SALDO TERKINI**\n\n💵 Rp {current_balance:,}\n📅 {datetime.now().strftime('%d/%m/%Y %H:%M')}"
    
    elif 'help' in message_lower or 'bantuan' in message_lower:
        return """🤖 **BOS UPETY BOT PRO 24/7**

📋 **Cara Penggunaan:**
• Kirim transaksi: "beli rokok 25000"
• Kirim foto nota untuk bukti
• Ketik "laporan" untuk laporan harian
• Ketik "saldo" untuk cek saldo

⏰ **Jadwal Otomatis:**
• 23:50 - Laporan harian
• 06:00 - Reminder saldo
• 00:00 - Laporan performa sistem

🔄 **Status:** Aktif 24/7"""
    
    return None

def generate_daily_report():
    """Generate laporan harian"""
    try:
        today = datetime.now().strftime('%Y-%m-%d')
        transactions = sheets.get_daily_transactions(today)
        
        if not transactions:
            return f"📊 **LAPORAN HARIAN**\n\n📅 {today}\n💰 Saldo: Rp {current_balance:,}\n📝 Tidak ada transaksi hari ini"
        
        total_income = sum(t.get('jumlah', 0) for t in transactions if t.get('tipe') == 'IN')
        total_expense = sum(t.get('jumlah', 0) for t in transactions if t.get('tipe') == 'OUT')
        
        report = f"""📊 **LAPORAN HARIAN**
        
📅 {today}
💰 Saldo: Rp {current_balance:,}

📈 **PEMASUKAN:** Rp {total_income:,}
📉 **PENGELUARAN:** Rp {total_expense:,}
📝 **TOTAL TRANSAKSI:** {len(transactions)}

🔍 **TRANSAKSI TERBARU:**
"""
        
        # Tampilkan 5 transaksi terakhir
        for i, trans in enumerate(transactions[-5:], 1):
            emoji = "📈" if trans.get('tipe') == 'IN' else "📉"
            report += f"{i}. {emoji} {trans.get('deskripsi', '')} - Rp {trans.get('jumlah', 0):,}\n"
        
        return report
        
    except Exception as e:
        logger.log_error(f"Error generate laporan: {str(e)}")
        return "❌ Gagal membuat laporan. Coba lagi."

@app.route('/webhook', methods=['POST'])
def webhook():
    """Webhook utama untuk menerima pesan dari Fonnte"""
    global error_count
    
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'status': 'error', 'message': 'No data received'}), 400
        
        # Extract message data
        sender_phone = data.get('sender', '').replace('+', '')
        message_text = data.get('message', '')
        media_url = data.get('media_url')
        
        logger.log_info(f"Pesan diterima dari {sender_phone}: {message_text[:50]}...")
        
        # Cek apakah nomor diizinkan
        if sender_phone not in ALLOWED_NUMBERS:
            logger.log_warning(f"Akses ditolak dari nomor: {sender_phone}")
            send_whatsapp_message(sender_phone, "❌ Akses ditolak. Nomor tidak terdaftar.")
            return jsonify({'status': 'rejected'}), 403
        
        # Handle perintah khusus
        special_response = handle_special_commands(message_text, sender_phone)
        if special_response:
            send_whatsapp_message(sender_phone, special_response)
            return jsonify({'status': 'success'})
        
        # Proses transaksi
        if message_text.strip():
            response = process_transaction(message_text, sender_phone, media_url)
            send_whatsapp_message(sender_phone, response)
        
        return jsonify({'status': 'success'})
        
    except Exception as e:
        error_count += 1
        logger.log_error(f"Error webhook: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/ping', methods=['GET'])
def ping():
    """Health check endpoint untuk UptimeRobot"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'balance': current_balance,
        'transactions': transaction_count,
        'errors': error_count
    })

@app.route('/status', methods=['GET'])
def status():
    """Status endpoint untuk monitoring"""
    return jsonify({
        'bot_name': 'Bos Upety Bot PRO 24/7',
        'status': 'active',
        'uptime': time.time(),
        'current_balance': current_balance,
        'total_transactions': transaction_count,
        'error_count': error_count,
        'allowed_numbers': ALLOWED_NUMBERS,
        'services': {
            'gemini': gemini.is_healthy(),
            'sheets': sheets.is_healthy(),
            'drive': drive.is_healthy()
        }
    })

def auto_restart_on_error():
    """Auto restart jika terjadi error fatal"""
    try:
        while True:
            time.sleep(300)  # Check setiap 5 menit
            
            # Jika error count terlalu tinggi, restart
            if error_count > 50:
                logger.log_error("Error count terlalu tinggi, melakukan restart...")
                os.execv(sys.executable, ['python'] + sys.argv)
                
    except Exception as e:
        logger.log_error(f"Error di auto restart: {str(e)}")

def main():
    """Main function"""
    try:
        logger.log_info("🚀 Bos Upety Bot PRO 24/7 starting...")
        
        # Start scheduler
        scheduler = SchedulerService()
        scheduler.start()
        
        # Start auto restart thread
        restart_thread = threading.Thread(target=auto_restart_on_error, daemon=True)
        restart_thread.start()
        
        # Load initial balance
        global current_balance
        current_balance = sheets.get_current_balance()
        
        logger.log_info(f"✅ Bot started successfully. Current balance: Rp {current_balance:,}")
        
        # Start Flask app
        app.run(host='0.0.0.0', port=5000, debug=False)
        
    except Exception as e:
        logger.log_error(f"Fatal error starting bot: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()
