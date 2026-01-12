# Tanlov AI - Avtomatlashtirilgan Tender Tahlil Tizimi

<p align="center">
  <img src="frontend/public/kqlogo.png" alt="Tanlov AI Logo" width="200"/>
</p>

"Ko'pkapqurilish" AJ uchun davlat xaridlari jarayonida inson omilini kamaytirish va eng yaxshi taklifni (Best Value for Money) matematik va mantiqiy asoslangan holda tanlash uchun AI asoslangan tizim.

## 🎯 Asosiy Imkoniyatlar

### ✅ Joriy imkoniyatlar
- **Tender Tahlili** - AI yordamida tender hujjatlarini avtomatik tahlil qilish
- **Ishtirokchilarni Baholash** - Har bir ishtirokchini tender talablariga mosligi bo'yicha baholash
- **Reyting Tizimi** - Ishtirokchilarni solishtirish va g'olibni aniqlash
- **PDF/Excel Hisobot** - Tahlil natijalarini PDF va Excel formatida yuklab olish
- **Bazaga Saqlash** - Barcha tahlillar tarixini saqlash va ko'rish
- **JWT Autentifikatsiya** - Xavfsiz token asosidagi kirish
- **Role-based Access** - Admin, Operator, Viewer rollari
- **Audit Log** - Barcha amallarni kuzatish va qayd qilish
- **Ko'p tilli qo'llab-quvvatlash** - O'zbek va Rus tillarida interfeys
- **Qorong'u/Yorug' mavzu** - Foydalanuvchi xohishiga ko'ra tema tanlash

## 🚀 Texnologik Stek

### Backend
- **Framework**: Django 5.0.1 + Django REST Framework
- **Autentifikatsiya**: JWT (Simple JWT)
- **Ma'lumotlar bazasi**: SQLite (development) / PostgreSQL (production)
- **AI Engine**: OpenAI GPT-4o-mini
- **PDF**: ReportLab
- **Excel**: XlsxWriter + Pandas

### Frontend
- **Framework**: React 18 + TypeScript
- **Build Tool**: Vite
- **UI**: Tailwind CSS + Custom Components
- **State**: React Context API
- **Routing**: React Router v6

## 📦 O'rnatish

### Talablar
- Python 3.11+
- Node.js 18+
- OpenAI API kaliti

### Backend o'rnatish
```bash
# Virtual muhit yaratish
python -m venv venv
source venv/bin/activate  # Linux/Mac

# Dependensiyalarni o'rnatish
pip install -r requirements.txt

# Migratsiyalarni yuritish
python manage.py migrate

# Admin foydalanuvchi yaratish (birinchi marta)
python manage.py createsuperuser

# Serverni ishga tushirish
python manage.py runserver 8000
```

### Frontend o'rnatish
```bash
cd frontend
npm install
npm run dev
```

### Environment sozlamalari
`.env` faylida sozlang:

```env
# Django
SECRET_KEY=your-secret-key
DEBUG=True

# OpenAI
OPENAI_API_KEY=your-openai-api-key-here
OPENAI_MODEL=gpt-4o-mini

# PostgreSQL (ixtiyoriy - production uchun)
# DB_ENGINE=postgresql
# DB_NAME=tanlov_ai
# DB_USER=postgres
# DB_PASSWORD=password
# DB_HOST=localhost
# DB_PORT=5432
```

## 🔐 Kirish

Tizimga kirish uchun:
- **Login**: `trest`
- **Parol**: `trest2026`
- **Rol**: Administrator

### Foydalanuvchi rollari
| Rol | Tahlil qilish | Ko'rish | Foydalanuvchilarni boshqarish |
|-----|---------------|---------|------------------------------|
| Admin | ✅ | ✅ | ✅ |
| Operator | ✅ | ✅ | ❌ |
| Viewer | ❌ | ✅ | ❌ |

## 📊 Foydalanish

### 1. Tender Tahlili
1. "Tender Tahlili" sahifasiga o'ting
2. Tender hujjatini yuklang (PDF, DOCX yoki TXT)
3. "Tahlil Qilish" tugmasini bosing
4. AI tender talablarini avtomatik aniqlaydi

### 2. Ishtirokchilarni Baholash
1. Tender tahlilidan so'ng, ishtirokchilar qismiga o'ting
2. Har bir ishtirokchi nomini kiriting va hujjat yuklang
3. "Tahlil Qilish" tugmasini bosing
4. AI barcha ishtirokchilarni tahlil qilib, reyting tuzadi

### 3. Natijalarni Yuklab Olish
- **PDF** - Batafsil hisobot
- **Excel** - Jadval formatida

## 🎨 Interfeys

- **Bosh sahifa** - Statistika va tezkor amallar
- **Tender Tahlili** - Asosiy tahlil jarayoni
- **Sozlamalar** - Tizim sozlamalari (til, tema, tahlil parametrlari)

## 📈 Baholash Tizimi

Ishtirokchilar quyidagi mezonlar bo'yicha baholanadi:
- **Tender talablariga moslik** - Majburiy va qo'shimcha talablar
- **Narx tahlili** - Taklif narxi va uning adekvatligi
- **Xavf darajasi** - Past, O'rta, Yuqori

## 🔍 API Endpointlar

### Autentifikatsiya
| Endpoint | Method | Tavsif |
|----------|--------|--------|
| `/api/auth/login/` | POST | JWT token olish |
| `/api/auth/token/refresh/` | POST | Token yangilash |
| `/api/auth/logout/` | POST | Chiqish |
| `/api/auth/me/` | GET | Joriy foydalanuvchi |
| `/api/auth/users/` | GET/POST | Foydalanuvchilar (Admin) |
| `/api/auth/audit-logs/` | GET | Audit loglar (Admin) |

### Tahlil
| Endpoint | Method | Tavsif |
|----------|--------|--------|
| `/api/evaluations/analyze-tender/` | POST | Tender tahlili |
| `/api/evaluations/analyze-participant/` | POST | Ishtirokchi tahlili |
| `/api/evaluations/compare-participants/` | POST | Solishtirish |
| `/api/evaluations/save-result/` | POST | Natijani saqlash |
| `/api/evaluations/history/` | GET | Tahlillar tarixi |
| `/api/evaluations/dashboard-stats/` | GET | Dashboard statistikasi |
| `/api/evaluations/chart-data/` | GET | Grafik ma'lumotlari |
| `/api/evaluations/download-excel/` | POST | Excel yuklab olish |
| `/api/evaluations/download-csv/` | POST | CSV yuklab olish |
| `/api/evaluations/export-pdf/` | POST | PDF yuklab olish |

## 📁 Loyiha Strukturasi

```
tanlov-ai/
├── apps/                    # Django ilovalari
│   ├── users/               # Foydalanuvchilar va JWT
│   ├── evaluations/         # Baholash moduli (asosiy)
│   ├── compliance/          # Compliance moduli
│   ├── participants/        # Ishtirokchilar
│   └── tenders/             # Tenderlar
├── core/                    # Asosiy xizmatlar
│   ├── llm_engine.py        # LLM integratsiya
│   └── tender_analyzer.py   # Tender tahlil xizmati
├── frontend/                # React frontend
│   ├── src/
│   │   ├── components/      # UI komponentlar
│   │   ├── context/         # React Context (Theme, Auth)
│   │   └── pages/           # Sahifalar
│   └── public/              # Statik fayllar
├── tests/                   # Unit testlar
├── tanlov_ai/               # Django sozlamalari
├── docker-compose.yml       # Production Docker
├── docker-compose.dev.yml   # Development Docker
└── requirements.txt         # Python dependensiyalar
```

## 🧪 Testlar

```bash
# Testlarni ishga tushirish
pytest

# Coverage bilan
pytest --cov=apps
```

## 🐳 Docker

### Development
```bash
docker-compose -f docker-compose.dev.yml up
```

### Production
```bash
docker-compose up -d
```

## 🚀 Ishga tushirish

### Development
```bash
# Backend (terminal 1)
source venv/bin/activate
python manage.py runserver 8000

# Frontend (terminal 2)
cd frontend
npm run dev
```

Frontend: http://localhost:5175
Backend API: http://localhost:8000/api/
API Docs: http://localhost:8000/api/docs/

## 💡 Kelajakdagi Imkoniyatlar

### 🤖 AI Yaxshilash
- [ ] O'zbek tilidagi hujjatlarni yaxshiroq qayta ishlash
- [ ] Rasm va jadvallarni OCR orqali o'qish
- [ ] Shartlarni kategoriyalarga ajratish

### 📱 Interfeys
- [ ] Dashboard'da grafiklar (Chart.js)
- [ ] Email bildirishnomalar
- [ ] Real-time yangilanishlar (WebSocket)

### 🔧 Texnik
- [ ] Redis cache
- [ ] Celery background tasks
- [ ] Kompaniyalar reytingi (oldingi tenderlar asosida)

## 📄 Litsenziya

Bu loyiha MIT litsenziyasi ostida tarqatiladi.

## 📞 Aloqa

- **Tashkilot**: "Ko'pkapqurilish" AJ
- **Loyiha**: Tanlov AI - Tender Tahlil Tizimi
- **Versiya**: 2.0.0

---

<p align="center">
  <strong>Tanlov AI</strong> - O'zbekistonning AI asoslangan tender tahlil tizimi! 🇺🇿
</p>

---

<p align="center">
  <strong>Tanlov AI</strong> - O'zbekistonning AI asoslangan tender tahlil tizimi! 🇺🇿
</p>
