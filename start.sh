#!/bin/bash
# Bos Upety Bot PRO 24/7 - Startup Script

echo "🤖 Starting Bos Upety Bot PRO 24/7..."
echo "📅 $(date)"

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Check environment variables
echo "🔍 Checking environment variables..."
if [ -z "$FONNTE_TOKEN" ]; then
    echo "⚠️ FONNTE_TOKEN not set"
fi

if [ -z "$GEMINI_API_KEY" ]; then
    echo "⚠️ GEMINI_API_KEY not set"
fi

if [ -z "$SHEET_ID" ]; then
    echo "⚠️ SHEET_ID not set"
fi

# Start the bot
echo "🚀 Starting bot..."
python main.py
