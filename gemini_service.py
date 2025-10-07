#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gemini Service - Integrasi AI Gemini 2.5 Pro untuk analisis transaksi
"""

import os
import json
import base64
import requests
from typing import Dict, Optional, Any
from dotenv import load_dotenv

load_dotenv()

class GeminiService:
    def __init__(self):
        self.api_key = os.getenv('GEMINI_API_KEY')
        self.model = "models/gemini-2.5-pro"
        self.base_url = "https://generativelanguage.googleapis.com/v1beta"
        self.health_status = True
        
        # Master prompt untuk AI
        self.master_prompt = """
Kamu adalah asisten keuangan pribadi digital untuk seorang bos (0811-5302-098) dan bendahara pribadinya (082181151735).
Tugas kamu adalah membaca pesan transaksi, menentukan kategori, dan memberi laporan otomatis.

Kategori:
- Makanan & Minuman: makan, minum, kopi, restoran, snack
- Transportasi: bensin, parkir, tol, gojek, grab, ojek
- Hiburan: hotel, karaoke, spa, pijat
- Pribadi: rokok, parfum, hadiah, baju, sepatu
- Rumah Tangga: sabun, deterjen, tissue, alat rumah
- Keuangan: transfer, top up, kirim dana, tf
- Lainnya: selain di atas

Output HARUS JSON:
{
  "deskripsi": "...",
  "jumlah": 0,
  "tipe": "IN/OUT/INFO",
  "kategori": "...",
  "bukti": "",
  "tanggapan_bot": "..."
}

Contoh:
Input: "beli rokok 25000"
Output: {
  "deskripsi": "beli rokok",
  "jumlah": 25000,
  "tipe": "OUT",
  "kategori": "Pribadi",
  "bukti": "",
  "tanggapan_bot": "✅ Dicatat: beli rokok\\n💸 Rp25.000\\n📂 Kategori: Pribadi"
}
"""
    
    def analyze_transaction(self, message_text: str, media_url: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Analisis transaksi menggunakan Gemini AI
        
        Args:
            message_text: Teks pesan transaksi
            media_url: URL media (foto nota) jika ada
            
        Returns:
            Dict hasil analisis atau None jika gagal
        """
        try:
            # Retry mechanism
            for attempt in range(3):
                try:
                    if media_url:
                        return self._analyze_with_image(message_text, media_url)
                    else:
                        return self._analyze_text_only(message_text)
                        
                except Exception as e:
                    if attempt == 2:  # Last attempt
                        self.health_status = False
                        raise e
                    time.sleep(1)  # Wait before retry
                    
        except Exception as e:
            print(f"Error analyze transaction: {str(e)}")
            return None
    
    def _analyze_text_only(self, message_text: str) -> Optional[Dict[str, Any]]:
        """Analisis teks saja tanpa gambar"""
        try:
            url = f"{self.base_url}/{self.model}:generateContent"
            headers = {
                'Content-Type': 'application/json',
            }
            
            payload = {
                "contents": [{
                    "parts": [{
                        "text": f"{self.master_prompt}\n\nPesan transaksi: {message_text}"
                    }]
                }],
                "generationConfig": {
                    "temperature": 0.1,
                    "topK": 1,
                    "topP": 0.8,
                    "maxOutputTokens": 1024,
                }
            }
            
            response = requests.post(
                f"{url}?key={self.api_key}",
                headers=headers,
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result['candidates'][0]['content']['parts'][0]['text']
                
                # Parse JSON response
                try:
                    # Extract JSON from response
                    json_start = content.find('{')
                    json_end = content.rfind('}') + 1
                    
                    if json_start != -1 and json_end != -1:
                        json_str = content[json_start:json_end]
                        parsed_result = json.loads(json_str)
                        
                        # Validate required fields
                        required_fields = ['deskripsi', 'jumlah', 'tipe', 'kategori', 'tanggapan_bot']
                        if all(field in parsed_result for field in required_fields):
                            self.health_status = True
                            return parsed_result
                    
                    # Fallback parsing
                    return self._fallback_parse(message_text, content)
                    
                except json.JSONDecodeError:
                    return self._fallback_parse(message_text, content)
            else:
                print(f"Gemini API error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"Error in text analysis: {str(e)}")
            return None
    
    def _analyze_with_image(self, message_text: str, media_url: str) -> Optional[Dict[str, Any]]:
        """Analisis dengan gambar (multimodal)"""
        try:
            # Download image
            image_data = self._download_image(media_url)
            if not image_data:
                return self._analyze_text_only(message_text)
            
            # Encode image to base64
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            
            url = f"{self.base_url}/{self.model}:generateContent"
            headers = {
                'Content-Type': 'application/json',
            }
            
            payload = {
                "contents": [{
                    "parts": [
                        {
                            "text": f"{self.master_prompt}\n\nPesan transaksi: {message_text}\n\nAnalisis juga gambar nota yang dikirim."
                        },
                        {
                            "inline_data": {
                                "mime_type": "image/jpeg",
                                "data": image_base64
                            }
                        }
                    ]
                }],
                "generationConfig": {
                    "temperature": 0.1,
                    "topK": 1,
                    "topP": 0.8,
                    "maxOutputTokens": 1024,
                }
            }
            
            response = requests.post(
                f"{url}?key={self.api_key}",
                headers=headers,
                json=payload,
                timeout=15
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result['candidates'][0]['content']['parts'][0]['text']
                
                # Parse JSON response
                try:
                    json_start = content.find('{')
                    json_end = content.rfind('}') + 1
                    
                    if json_start != -1 and json_end != -1:
                        json_str = content[json_start:json_end]
                        parsed_result = json.loads(json_str)
                        
                        # Add media URL to bukti
                        parsed_result['bukti'] = media_url
                        
                        required_fields = ['deskripsi', 'jumlah', 'tipe', 'kategori', 'tanggapan_bot']
                        if all(field in parsed_result for field in required_fields):
                            self.health_status = True
                            return parsed_result
                    
                    return self._fallback_parse(message_text, content)
                    
                except json.JSONDecodeError:
                    return self._fallback_parse(message_text, content)
            else:
                print(f"Gemini API error with image: {response.status_code} - {response.text}")
                return self._analyze_text_only(message_text)
                
        except Exception as e:
            print(f"Error in image analysis: {str(e)}")
            return self._analyze_text_only(message_text)
    
    def _download_image(self, url: str) -> Optional[bytes]:
        """Download image from URL"""
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                return response.content
            return None
        except Exception as e:
            print(f"Error downloading image: {str(e)}")
            return None
    
    def _fallback_parse(self, message_text: str, ai_response: str) -> Dict[str, Any]:
        """Fallback parsing jika JSON parsing gagal"""
        try:
            # Simple keyword-based parsing
            message_lower = message_text.lower()
            
            # Extract amount
            import re
            amounts = re.findall(r'\d+', message_text)
            amount = int(amounts[-1]) if amounts else 0
            
            # Determine type
            if any(word in message_lower for word in ['tf', 'transfer', 'terima', 'dari', 'masuk']):
                tipe = 'IN'
            elif any(word in message_lower for word in ['beli', 'bayar', 'keluar', 'habis']):
                tipe = 'OUT'
            else:
                tipe = 'INFO'
            
            # Determine category
            if any(word in message_lower for word in ['makan', 'minum', 'kopi', 'restoran', 'snack']):
                kategori = 'Makanan & Minuman'
            elif any(word in message_lower for word in ['bensin', 'parkir', 'tol', 'gojek', 'grab', 'ojek']):
                kategori = 'Transportasi'
            elif any(word in message_lower for word in ['hotel', 'karaoke', 'spa', 'pijat']):
                kategori = 'Hiburan'
            elif any(word in message_lower for word in ['rokok', 'parfum', 'hadiah', 'baju', 'sepatu']):
                kategori = 'Pribadi'
            elif any(word in message_lower for word in ['sabun', 'deterjen', 'tissue', 'rumah']):
                kategori = 'Rumah Tangga'
            elif any(word in message_lower for word in ['transfer', 'top up', 'kirim', 'tf']):
                kategori = 'Keuangan'
            else:
                kategori = 'Lainnya'
            
            return {
                'deskripsi': message_text,
                'jumlah': amount,
                'tipe': tipe,
                'kategori': kategori,
                'bukti': '',
                'tanggapan_bot': f"✅ Dicatat: {message_text}\n💸 Rp{amount:,}\n📂 Kategori: {kategori}"
            }
            
        except Exception as e:
            print(f"Error in fallback parse: {str(e)}")
            return {
                'deskripsi': message_text,
                'jumlah': 0,
                'tipe': 'INFO',
                'kategori': 'Lainnya',
                'bukti': '',
                'tanggapan_bot': f"✅ Dicatat: {message_text}"
            }
    
    def is_healthy(self) -> bool:
        """Check if service is healthy"""
        return self.health_status
    
    def get_insights(self, transactions: list) -> str:
        """Generate AI insights dari transaksi"""
        try:
            if not transactions:
                return "📊 Belum ada data transaksi untuk dianalisis."
            
            # Prepare data for analysis
            total_income = sum(t.get('jumlah', 0) for t in transactions if t.get('tipe') == 'IN')
            total_expense = sum(t.get('jumlah', 0) for t in transactions if t.get('tipe') == 'OUT')
            
            # Category analysis
            categories = {}
            for t in transactions:
                cat = t.get('kategori', 'Lainnya')
                categories[cat] = categories.get(cat, 0) + t.get('jumlah', 0)
            
            top_category = max(categories.items(), key=lambda x: x[1]) if categories else ('Tidak ada', 0)
            
            insights = f"""🤖 **AI INSIGHTS**

📈 **Analisis Tren:**
• Total Pemasukan: Rp {total_income:,}
• Total Pengeluaran: Rp {total_expense:,}
• Saldo Bersih: Rp {total_income - total_expense:,}

🏆 **Kategori Terbanyak:**
• {top_category[0]}: Rp {top_category[1]:,}

💡 **Saran:**
"""
            
            if total_expense > total_income:
                insights += "• ⚠️ Pengeluaran melebihi pemasukan. Perlu kontrol keuangan.\n"
            
            if top_category[0] == 'Pribadi' and top_category[1] > total_expense * 0.3:
                insights += "• 💸 Pengeluaran pribadi cukup tinggi. Pertimbangkan prioritas.\n"
            
            if total_income > 0:
                insights += "• ✅ Ada pemasukan yang baik. Pertahankan cash flow positif.\n"
            
            return insights
            
        except Exception as e:
            print(f"Error generating insights: {str(e)}")
            return "❌ Gagal membuat AI insights."

# Import time untuk retry mechanism
import time
