# Production Setup va Debugging Guide

## Login Masalasi - Tanlov AI Production

### Masalaning Sababi
Production'da `trest / trest2026` bilan login bo'lmayapti:
1. **Backend API javob bermayapti** (Status 000)
2. **CSRF Origin checking failed** xatoligi
3. **Service ishlamayapti yoki noto'g'ri konfiguratsiya**

### Tuzatish Yo'riqnomasi

#### 1. Server'da CSRF va Settings Tekshirish

SSH orqali serverga kirgach:

```bash
# Backend folder'ga kirish
cd /var/www/tanlov/backend

# Virtual environment activate qilish
source venv/bin/activate

# Django settings'ni tekshirish
python manage.py shell << 'EOF'
from django.conf import settings
print("DEBUG:", settings.DEBUG)
print("ALLOWED_HOSTS:", settings.ALLOWED_HOSTS)
print("CSRF_TRUSTED_ORIGINS:", settings.CSRF_TRUSTED_ORIGINS)
print("CORS_ALLOWED_ORIGINS:", settings.CORS_ALLOWED_ORIGINS)
EOF
```

**Kutilgan natija:**
```
DEBUG: False
ALLOWED_HOSTS: ['tanlov.kuprikqurilish.uz']
CSRF_TRUSTED_ORIGINS: ['https://tanlov.kuprikqurilish.uz', ...]
CORS_ALLOWED_ORIGINS: ['https://tanlov.kuprikqurilish.uz', ...]
```

#### 2. Backend Service Status

```bash
# Systemd service status
sudo systemctl status tanlov

# Logs'ni ko'rish
sudo journalctl -u tanlov -n 50 -f

# Agar service ishlamasa
sudo systemctl start tanlov
sudo systemctl enable tanlov
```

#### 3. Nginx Tekshirish

```bash
# Nginx configuration syntax tekshirish
sudo nginx -t

# Logs'ni ko'rish
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# Nginx restart
sudo systemctl reload nginx
```

#### 4. API Health Check (Server'dan)

```bash
# Localhost'dan test (server'da)
curl -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "trest", "password": "trest2026"}'

# HTTPS test (server'dan)
curl -X POST https://tanlov.kuprikqurilish.uz/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "trest", "password": "trest2026"}'
```

#### 5. Database Migration

```bash
cd /var/www/tanlov/backend
source venv/bin/activate

# Migration qilish
python manage.py migrate

# Static files to'plash
python manage.py collectstatic --noinput
```

#### 6. .env File Tekshirish

Production'dagi `.env` faylida:

```bash
sudo cat /var/www/tanlov/backend/.env
```

Quyidagilar bo'lishi kerak:
```env
DEBUG=False
SECRET_KEY=your-secure-key
ALLOWED_HOSTS=tanlov.kuprikqurilish.uz
OPENAI_API_KEY=your-api-key
```

### CSRF Origin Error - Yechim

Agar hali CSRF error chiqayotgan bo'lsa:

**Django settings.py'da (lokal):**
```python
if not DEBUG:
    CSRF_TRUSTED_ORIGINS = [
        "https://tanlov.kuprikqurilish.uz",
        "http://localhost:8000",
    ]
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_SECURE = True
```

**Keyin:**
```bash
git add tanlov_ai/settings.py
git commit -m "fix: add CSRF_TRUSTED_ORIGINS for production"
git push
```

Server'dagi deploy:
```bash
cd /var/www/tanlov/backend
git pull
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart tanlov
```

### Quick Diagnostics Script

Server'da run qilish:
```bash
#!/bin/bash
echo "=== TANLOV AI DIAGNOSTICS ==="
echo ""
echo "1. Service Status:"
sudo systemctl status tanlov --no-pager | head -5
echo ""
echo "2. Recent Errors:"
sudo journalctl -u tanlov -n 10 --no-pager
echo ""
echo "3. Nginx Status:"
sudo systemctl status nginx --no-pager | head -3
echo ""
echo "4. API Health (localhost):"
curl -s http://127.0.0.1:8000/api/stats/ -I | head -1
echo ""
echo "5. Database Connection:"
cd /var/www/tanlov/backend && source venv/bin/activate && python manage.py dbshell < /dev/null 2>&1 | head -3
```

### Common Issues va Yechimlar

| Masala | Sababi | Yechim |
|--------|--------|--------|
| Status 000 | Backend ishlamayapti | `sudo systemctl start tanlov` |
| 502 Bad Gateway | Gunicorn socket xatoligi | `sudo systemctl restart tanlov` |
| ERR_TOO_MANY_REDIRECTS | SSL redirect loop | Nginx'da `X-Forwarded-Proto` set qilish |
| CSRF failed | Origins matchlanmadi | CSRF_TRUSTED_ORIGINS tekshirish |
| 403 Forbidden | Authentication xatoligi | User mavjudligi tekshirish |
| 500 Internal Server | Django error | Logs'ni ko'rish: `journalctl -u tanlov` |

### Frontend Test

Browser'da:
1. `https://tanlov.kuprikqurilish.uz` ga kirgach
2. F12 → Network tab → login request qilish
3. POST `/api/auth/login/` javobini ko'rish
4. Status code va response body'ni tekshirish

### Debug Mode (Temporary)

Agar PRODUCTION'da hali muhim xatoliklar bo'lsa:

```bash
# Server'da .env'ni edit qilish
sudo nano /var/www/tanlov/backend/.env

# DEBUG=True qilish (VAQTINCHA!)
DEBUG=True

# Service restart
sudo systemctl restart tanlov

# Logs'ni ko'rish - error messages ko'rinadi
sudo journalctl -u tanlov -f

# DEBUG=False qayta qilish!
DEBUG=False
sudo systemctl restart tanlov
```

### Login Masalasi - Password Noto'g'ri

**Sabab**: Production database'da user'ning password hash'i boshqacha yoki user mavjud emas

**Tez Yechim - Server'da Shell:**

```bash
cd /var/www/tanlov/backend
source venv/bin/activate

# 1. Mavjud userlarni ko'rish
python manage.py shell << 'EOF'
from apps.users.models import User
users = User.objects.all()
for u in users:
    print(f"  - {u.username} ({u.email})")
EOF

# 2. AGAR USER TOPILMASA - User yaratish
python manage.py shell << 'EOF'
from apps.users.models import User

User.objects.filter(username='trest').delete()

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
print(f"✅ User created: {user.username}")
EOF

# 3. AGAR USER MAVJUD LEKIN PAROL NOTO'G'RI - Reset qilish
python manage.py changepassword trest
# Yoki shell'da:
python manage.py shell << 'EOF'
from apps.users.models import User
user = User.objects.get(username='trest')
user.set_password('trest2026')
user.save()
print(f"✅ Password reset")
EOF

# 4. Service restart
sudo systemctl restart tanlov
```

**Automatic Script'dan foydalanish:**

Lokal'dagi `init_production_db.sh` ni server'ga copy qilish:

```bash
# Lokal'dagi tanlov-ai folder'dan
scp init_production_db.sh user@tanlov.kuprikqurilish.uz:/tmp/

# Server'da run qilish
ssh user@tanlov.kuprikqurilish.uz
chmod +x /tmp/init_production_db.sh
/tmp/init_production_db.sh /var/www/tanlov/backend
```

**Test:**
```bash
curl -X POST https://tanlov.kuprikqurilish.uz/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "trest", "password": "trest2026"}'
```

---

**Mukhim**: Production'da test qilish uchun:
```bash
curl -X POST https://tanlov.kuprikqurilish.uz/api/auth/login/ \
  -H "Content-Type: application/json" \
  -H "X-CSRFToken: $(csrf_token)" \
  -d '{"username": "trest", "password": "trest2026"}'
```

### ERR_TOO_MANY_REDIRECTS - Tuzatish

**Sabab**: SECURE_SSL_REDIRECT + Nginx HTTPS redirect cheksiz loop yaratadi

**Yechim 1 - Django'da (Recommended):**
```python
# tanlov_ai/settings.py
if not DEBUG:
    # SECURE_SSL_REDIRECT = True  # COMMENT QA'LING - Nginx buni hal qiladi!
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
```

**Yechim 2 - Nginx'da:**

```nginx
# /etc/nginx/sites-available/tanlov

location /api/ {
    proxy_pass http://127.0.0.1:8000;
    
    # MUHIM: Proxy headers Django'ya HTTPS deb biltirbilsin
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;  # $scheme = https yoki http
    proxy_set_header X-Forwarded-Host $server_name;
    
    # Redirect'dan oshirish
    proxy_redirect off;
}
```

**Server'da qilish kerak:**
```bash
cd /var/www/tanlov/backend
git pull
python manage.py collectstatic --noinput
sudo systemctl restart tanlov
sudo nginx -t
sudo systemctl reload nginx
```

**Test:**
```bash
curl -v https://tanlov.kuprikqurilish.uz/api/stats/
```

Natija: `301` yoki `302` bo'lmasa, cheksiz redirect yo'q!
