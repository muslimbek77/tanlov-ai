#!/usr/bin/env python
"""
Production serverda yangi foydalanuvchi yaratish uchun script.

Ishlatish:
    python manage.py shell < create_user.py
    
Yoki:
    python manage.py shell
    >>> exec(open('create_user.py').read())
"""

from apps.users.models import User, UserRole

# Yangi foydalanuvchi ma'lumotlari
USERNAME = 'user'
PASSWORD = 'Bek12345'
ROLE = UserRole.OPERATOR  # 'admin', 'operator', 'viewer'
EMAIL = 'user@example.com'
FIRST_NAME = 'User'
LAST_NAME = 'Operator'

# Mavjud bo'lsa o'chirish (ixtiyoriy)
existing = User.objects.filter(username=USERNAME).first()
if existing:
    print(f"Mavjud foydalanuvchi topildi: {existing.username}")
    existing.set_password(PASSWORD)
    existing.role = ROLE
    existing.is_active = True
    existing.save()
    print(f"Parol yangilandi va faollashtirildi!")
else:
    # Yangi yaratish
    user = User.objects.create_user(
        username=USERNAME,
        email=EMAIL,
        password=PASSWORD,
        first_name=FIRST_NAME,
        last_name=LAST_NAME,
        role=ROLE,
        is_active=True
    )
    print(f"Yangi foydalanuvchi yaratildi: {user.username}")

print(f"""
========================================
Foydalanuvchi ma'lumotlari:
  Login: {USERNAME}
  Parol: {PASSWORD}
  Rol: {ROLE}
========================================
""")
