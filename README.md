# 🤖 Bos Upety Bot PRO 24/7

Bot WhatsApp untuk mengelola keuangan pribadi bos dengan sistem otomatis dan aman menggunakan AI Gemini 2.5 Pro.

## 🎯 Fitur Utama

- ✅ **Integrasi WhatsApp** via Fonnte API
- 🧠 **AI Gemini 2.5 Pro** untuk klasifikasi transaksi otomatis
- 📊 **Google Sheets** untuk penyimpanan data
- 📁 **Google Drive** untuk upload foto bukti
- ⏰ **Laporan Otomatis** setiap hari jam 23:50
- 💰 **Reminder Saldo** setiap pagi jam 06:00
- 🔄 **Auto Recovery** dan backup data
- 🕐 **Aktif 24/7** nonstop

## 📋 Nomor yang Diizinkan

- **ADMIN (Bendahara):** 082181151735
- **BOS:** 08115302098

## 🚀 Cara Deployment di Replit

### 1. Persiapan

1. **Buka [Replit.com](https://replit.com)**
2. **Buat project baru** → pilih **Python**
3. **Upload semua file** dari project ini

### 2. Setup Environment Variables

Di Replit, buka tab **Secrets** dan tambahkan:

```
FONNTE_TOKEN=your_fonnte_token_here
GEMINI_API_KEY=your_gemini_api_key_here
ADMIN=6282181151735
BOS=628115302098
SHEET_ID=your_google_sheets_id_here
```

### 3. Setup Google Credentials

1. **Buat Google Cloud Project** di [console.cloud.google.com](https://console.cloud.google.com)
2. **Enable APIs:**
   - Google Sheets API
   - Google Drive API
3. **Buat Service Account** dan download `credentials.json`
4. **Upload `credentials.json`** ke Replit
5. **Share Google Sheets** dengan email service account

### 4. Install Dependencies

Di Replit console, jalankan:
```bash
pip install -r requirements.txt
```

### 5. Setup Fonnte Webhook

1. **Buka [Fonnte.com](https://fonnte.com)**
2. **Masuk ke dashboard**
3. **Pilih menu Webhook**
4. **Set Webhook URL:** `https://your-repl-name.repl.co/webhook`
5. **Save**

### 6. Setup UptimeRobot

1. **Buka [UptimeRobot.com](https://uptimerobot.com)**
2. **Add New Monitor**
3. **URL:** `https://your-repl-name.repl.co/ping`
4. **Interval:** 5 minutes
5. **Save**

### 7. Run Bot

Klik **Run** di Replit. Bot akan aktif 24/7!

## 📱 Cara Penggunaan

### Kirim Transaksi
```
beli rokok 25000
tf dari bos 1000000
bayar parkir 5000
```

### Kirim Foto Bukti
Kirim foto nota/struk, bot akan otomatis upload ke Google Drive.

### Perintah Khusus
- `laporan` - Laporan harian
- `saldo` - Cek saldo terkini
- `help` - Bantuan

## 🕐 Jadwal Otomatis

| Waktu | Aktivitas |
|-------|-----------|
| 23:50 | Laporan harian ke bos & admin |
| 06:00 | Reminder saldo pagi |
| 00:00 | Laporan performa sistem |
| Minggu 01:00 | Backup mingguan |
| Tanggal 1, 08:00 | Laporan bulanan |

## 🏗️ Struktur Project

```
bos-upety-bot/
├── main.py                # Webhook utama
├── gemini_service.py      # Integrasi Gemini AI
├── sheets_service.py      # Integrasi Google Sheets
├── drive_service.py       # Upload ke Google Drive
├── scheduler.py           # Laporan otomatis
├── logger_service.py      # Logging & Recovery
├── backup_service.py      # Backup lokal
├── requirements.txt       # Dependencies
├── config.env            # Template konfigurasi
└── README.md             # Dokumentasi
```

## 🔧 API Endpoints

- `POST /webhook` - Webhook Fonnte
- `GET /ping` - Health check (UptimeRobot)
- `GET /status` - Status bot

## 🛡️ Keamanan

- ✅ Hanya nomor terdaftar yang bisa akses
- ✅ Retry otomatis 3x untuk setiap API
- ✅ Timeout 10 detik per request
- ✅ Log error ke file & Sheets
- ✅ Backup otomatis ke CSV
- ✅ Auto restart jika error fatal

## 📊 Monitoring

### Health Check
- URL: `https://your-repl-name.repl.co/ping`
- Response: JSON dengan status bot

### Logs
- Info: `logs/info.log`
- Error: `logs/error.log`
- Warning: `logs/warning.log`
- Debug: `logs/debug.log`

### Backup
- Lokal: `backups/transactions.csv`
- Google Sheets: Otomatis sync
- Google Drive: Folder "Bos Upety Bot Bukti"

## 🚨 Troubleshooting

### Bot Tidak Merespon
1. Cek logs di Replit console
2. Cek status di `/ping`
3. Restart bot di Replit

### Error Google Sheets
1. Cek `credentials.json` sudah benar
2. Cek Sheets sudah di-share ke service account
3. Cek SHEET_ID di environment variables

### Error Gemini AI
1. Cek GEMINI_API_KEY valid
2. Cek quota API Gemini
3. Cek koneksi internet

### Error Fonnte
1. Cek FONNTE_TOKEN valid
2. Cek webhook URL sudah benar
3. Cek nomor sudah terdaftar di Fonnte

## 📞 Support

Jika ada masalah:
1. Cek logs di Replit console
2. Cek status bot di `/status`
3. Restart bot jika perlu

## 🎉 Hasil Akhir

Bot WhatsApp "Bos Upety Bot PRO 24/7" akan:
- ✅ Menerima pesan otomatis dari WhatsApp
- ✅ Mengklasifikasi transaksi pakai AI Gemini 2.5 Pro
- ✅ Menyimpan data ke Google Sheets
- ✅ Upload bukti ke Google Drive
- ✅ Kirim laporan otomatis tiap malam
- ✅ Kirim saldo pagi harinya
- ✅ Auto recovery & restart kalau error
- ✅ Aktif terus 24 jam tanpa henti
- ✅ Bisa dijalankan langsung dari warnet 💪

---

**Dibuat dengan ❤️ untuk Bos Upety**
