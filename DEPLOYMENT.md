# Deployment Guide - Tanlov AI

## Production Deploy qilish yo'riqnomasi

### 1. Frontend Build va Deploy

#### Lokal build qilish
```bash
# Frontend papkasiga kirish
cd frontend

# Dependencies o'rnatish
npm install

# Production build
npm run build
```

Build `frontend/dist/` papkasida yaratiladi.

#### Serverga yuklash

**Agar Nginx ishlatayotgan bo'lsangiz:**
```bash
# Build fayllarini serverga yuklash
scp -r frontend/dist/* user@tanlov.kuprikqurilish.uz:/var/www/tanlov/frontend/

# Yoki rsync bilan (tezroq)
rsync -avz --delete frontend/dist/ user@tanlov.kuprikqurilish.uz:/var/www/tanlov/frontend/
```

**Nginx konfiguratsiyasi** (`/etc/nginx/sites-available/tanlov`):
```nginx
server {
    listen 80;
    server_name tanlov.kuprikqurilish.uz;
    
    # SSL uchun (Let's Encrypt)
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name tanlov.kuprikqurilish.uz;
    
    ssl_certificate /etc/letsencrypt/live/tanlov.kuprikqurilish.uz/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/tanlov.kuprikqurilish.uz/privkey.pem;
    
    # Frontend (React SPA)
    location / {
        root /var/www/tanlov/frontend;
        try_files $uri $uri/ /index.html;
        
        # Cache static assets
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }
    
    # Backend API
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support (agar kerak bo'lsa)
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
    
    # Django admin
    location /admin/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # Static files (Django)
    location /static/ {
        alias /var/www/tanlov/staticfiles/;
    }
    
    # Media files
    location /media/ {
        alias /var/www/tanlov/media/;
    }
}
```

Nginx qayta yuklash:
```bash
sudo nginx -t
sudo systemctl reload nginx
```

### 2. Environment Variables

Frontend `.env.production` faylida:
```env
VITE_API_BASE_URL=https://tanlov.kuprikqurilish.uz/api
```

Backend `.env` faylida:
```env
DEBUG=False
ALLOWED_HOSTS=tanlov.kuprikqurilish.uz
CORS_ALLOWED_ORIGINS=https://tanlov.kuprikqurilish.uz
OPENAI_API_KEY=your-api-key
SECRET_KEY=your-secret-key
```

### 3. Backend Deploy

#### Gunicorn bilan ishlatish
```bash
# Gunicorn o'rnatish
pip install gunicorn

# Ishga tushirish
gunicorn tanlov_ai.wsgi:application --bind 0.0.0.0:8000 --workers 4
```

#### Systemd service (`/etc/systemd/system/tanlov.service`):
```ini
[Unit]
Description=Tanlov AI Django Application
After=network.target

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/var/www/tanlov
Environment="PATH=/var/www/tanlov/venv/bin"
ExecStart=/var/www/tanlov/venv/bin/gunicorn \
    --workers 4 \
    --bind 127.0.0.1:8000 \
    --access-logfile /var/www/tanlov/logs/access.log \
    --error-logfile /var/www/tanlov/logs/error.log \
    tanlov_ai.wsgi:application
    
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Service ishga tushirish:
```bash
sudo systemctl daemon-reload
sudo systemctl enable tanlov
sudo systemctl start tanlov
sudo systemctl status tanlov
```

### 4. SSL Sertifikat (Let's Encrypt)

```bash
# Certbot o'rnatish
sudo apt install certbot python3-certbot-nginx

# Sertifikat olish
sudo certbot --nginx -d tanlov.kuprikqurilish.uz

# Avtomatik yangilanish
sudo certbot renew --dry-run
```

### 5. Deployment Checklist

- [ ] Frontend build qilindi (`npm run build`)
- [ ] Build fayllari serverga yuklandi
- [ ] `.env.production` to'g'ri konfiguratsiya qilindi
- [ ] Nginx konfiguratsiya fayli yaratildi
- [ ] SSL sertifikat o'rnatildi
- [ ] Backend service ishga tushirildi
- [ ] Static files to'plandi (`python manage.py collectstatic`)
- [ ] Database migration qilindi (`python manage.py migrate`)
- [ ] CORS settings to'g'rilandi
- [ ] ALLOWED_HOSTS yangilandi
- [ ] DEBUG=False qilindi

### 6. Monitoring va Logs

**Nginx logs:**
```bash
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
```

**Django logs:**
```bash
tail -f /var/www/tanlov/logs/access.log
tail -f /var/www/tanlov/logs/error.log
```

**Service status:**
```bash
sudo systemctl status tanlov
journalctl -u tanlov -f
```

### 7. Quick Deploy Script

`deploy.sh` yaratish:
```bash
#!/bin/bash

echo "🚀 Deploying Tanlov AI..."

# Frontend build
echo "📦 Building frontend..."
cd frontend
npm run build
cd ..

# Upload to server
echo "📤 Uploading to server..."
rsync -avz --delete frontend/dist/ user@tanlov.kuprikqurilish.uz:/var/www/tanlov/frontend/

# Restart services
echo "🔄 Restarting services..."
ssh user@tanlov.kuprikqurilish.uz "sudo systemctl restart tanlov && sudo systemctl reload nginx"

echo "✅ Deployment complete!"
```

Ishlatish:
```bash
chmod +x deploy.sh
./deploy.sh
```

## Troubleshooting

### API 404 xatosi
- Nginx konfiguratsiyasida `proxy_pass` to'g'ri ekanligini tekshiring
- Backend service ishlab turganligini tekshiring: `sudo systemctl status tanlov`

### CORS xatosi
- `settings.py` da `CORS_ALLOWED_ORIGINS` to'g'ri sozlanganligini tekshiring
- Frontend `VITE_API_BASE_URL` to'g'ri ekanligini tekshiring

### Static files yuklanmayapti
- `python manage.py collectstatic` buyrug'ini ishga tushiring
- Nginx `static/` location to'g'ri konfiguratsiya qilinganligini tekshiring
