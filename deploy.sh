#!/bin/bash

# Tanlov AI - Quick Deploy Script
# Bu script frontend build qiladi va serverga yuklaydi

set -e  # Stop on error

echo "🚀 Tanlov AI Deploy boshlanmoqda..."
echo ""

# 1. Frontend build
echo "📦 Frontend build qilinmoqda..."
cd frontend
npm run build
cd ..
echo "✅ Build tayyor!"
echo ""

# 2. Server ma'lumotlari
read -p "Server username (default: www-data): " SERVER_USER
SERVER_USER=${SERVER_USER:-www-data}

read -p "Server address (default: tanlov.kuprikqurilish.uz): " SERVER_HOST
SERVER_HOST=${SERVER_HOST:-tanlov.kuprikqurilish.uz}

read -p "Server path (default: /var/www/tanlov): " SERVER_PATH
SERVER_PATH=${SERVER_PATH:-/var/www/tanlov}

echo ""
echo "📤 Serverga yuklash..."
echo "   Server: $SERVER_USER@$SERVER_HOST"
echo "   Path: $SERVER_PATH"
echo ""

# 3. Upload frontend files
rsync -avz --delete \
  frontend/dist/ \
  $SERVER_USER@$SERVER_HOST:$SERVER_PATH/frontend/

echo ""
echo "🔄 Service qayta ishga tushirilmoqda..."

# 4. Restart services (optional)
read -p "Service restart qilasizmi? (y/n): " RESTART
if [ "$RESTART" = "y" ]; then
  ssh $SERVER_USER@$SERVER_HOST "sudo systemctl restart tanlov && sudo systemctl reload nginx"
  echo "✅ Services restarted!"
fi

echo ""
echo "✅ Deploy muvaffaqiyatli yakunlandi!"
echo "🌐 Site: https://$SERVER_HOST"
echo ""
