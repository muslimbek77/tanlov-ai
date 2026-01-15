#!/bin/bash

# Production uchun frontend build qilish

echo "🚀 Production frontend build boshlanmoqda..."

cd frontend

# Node modules o'rnatish
echo "📦 Dependencies o'rnatilmoqda..."
npm install

# Production build
echo "🔨 Production build qilinmoqda..."
npm run build

echo "✅ Build tayyor! frontend/dist papkasida joylashgan."
echo ""
echo "Serverga yuklash uchun:"
echo "  scp -r frontend/dist/* user@tanlov.kuprikqurilish.uz:/var/www/tanlov/frontend/dist/"
