#!/bin/bash

# Production server'da trest user'ni reset qilish
# SSH orqali serverga kirgach, bu script'ni run qiling

BACKEND_PATH=${1:-/var/www/tanlov/backend}

echo "🔧 Production User Reset Script"
echo "Backend path: $BACKEND_PATH"
echo ""

cd "$BACKEND_PATH" || exit 1

# Virtual environment activate
source venv/bin/activate

echo "1️⃣ Database'ni tekshirish..."
python manage.py shell << 'SHELL_EOF'
from apps.users.models import User

user = User.objects.filter(username='trest').first()
if user:
    print(f"✅ User mavjud: {user.username}")
else:
    print("❌ User topilmadi - yaratmoqda...")
SHELL_EOF

echo ""
echo "2️⃣ User'ni qayta yaratish..."
python manage.py shell << 'SHELL_EOF'
from apps.users.models import User

# Eski user'ni o'chirish
User.objects.filter(username='trest').delete()
print("✅ Eski user o'chirildi")

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
print(f"✅ Yangi user yaratildi: {user.username}")
print(f"   Email: {user.email}")
print(f"   Role: {user.role}")
SHELL_EOF

echo ""
echo "3️⃣ User tekshirish..."
python manage.py shell << 'SHELL_EOF'
from django.contrib.auth import authenticate

user = authenticate(username='trest', password='trest2026')
if user:
    print(f"✅ Password to'g'ri! User login qilishi mumkin.")
else:
    print(f"❌ Password hali ham noto'g'ri!")
SHELL_EOF

echo ""
echo "4️⃣ Database migration..."
python manage.py migrate --noinput

echo ""
echo "5️⃣ Static files..."
python manage.py collectstatic --noinput --clear

echo ""
echo "✅ TAYYOR! Backend restart qiling:"
echo "   sudo systemctl restart tanlov"
