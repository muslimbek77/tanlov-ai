#!/bin/bash

# Production server'da database initialize qilish
# Foydalanish: ./init_production_db.sh /var/www/tanlov/backend

BACKEND_PATH=${1:-/var/www/tanlov/backend}

echo "🚀 Production Database Initialize"
echo "Path: $BACKEND_PATH"
echo ""

if [ ! -d "$BACKEND_PATH" ]; then
    echo "❌ Path topilmadi: $BACKEND_PATH"
    exit 1
fi

cd "$BACKEND_PATH"

# Virtual environment activate
source venv/bin/activate

echo "1️⃣ Migration qilinmoqda..."
python manage.py migrate --noinput

echo ""
echo "2️⃣ trest user tekshirilmoqda..."
python manage.py shell << 'SHELL_EOF'
from apps.users.models import User

user = User.objects.filter(username='trest').first()
if user:
    print(f"   ✅ User mavjud: {user.username}")
else:
    print(f"   ❌ User topilmadi - yaratmoqda...")
SHELL_EOF

echo ""
echo "3️⃣ trest user yaratilmoqda..."
python manage.py shell << 'SHELL_EOF'
from apps.users.models import User
from django.contrib.auth import authenticate

# Eski user'ni o'chirish (agar mavjud bo'lsa)
User.objects.filter(username='trest').delete()

# Yangi user yaratish
user = User.objects.create_user(
    username='trest',
    email='trest@example.com',
    password='trest2026',
    first_name='Test',
    last_name='User',
    role='admin',
    is_staff=True,
    is_superuser=True
)
print(f"   ✅ User yaratildi: {user.username}")
print(f"      Email: {user.email}")
print(f"      Role: {user.role}")
print(f"      Password: trest2026")

# Parol tekshirish
auth_user = authenticate(username='trest', password='trest2026')
if auth_user:
    print(f"   ✅ Password to'g'ri!")
else:
    print(f"   ❌ Password xatoligi!")
SHELL_EOF

echo ""
echo "4️⃣ Static files to'plash..."
python manage.py collectstatic --noinput --clear

echo ""
echo "✅ TAYYOR!"
echo ""
echo "Keying qilish:"
echo "  sudo systemctl restart tanlov"
echo ""
echo "Test qilish:"
echo "  curl -X POST https://tanlov.kuprikqurilish.uz/api/auth/login/ \\"
echo "    -H 'Content-Type: application/json' \\"
echo "    -d '{\"username\": \"trest\", \"password\": \"trest2026\"}'"
