# Tanlov AI - Avtomatlashtirilgan Tender Tahlil Tizimi

<p align="center">
  <img src="frontend/public/kqlogo.png" alt="Tanlov AI Logo" width="200"/>
</p>

"Ko'pkapqurilish" AJ uchun davlat xaridlari jarayonida inson omilini kamaytirish, korrupsiya xavfini aniqlash va eng yaxshi taklifni (Best Value for Money) matematik va mantiqiy asoslangan holda tanlash uchun Avtomatlashtirilgan AI tizimi.

## 🎯 Asosiy Imkoniyatlar

- **Tender Tahlili** - AI yordamida tender hujjatlarini avtomatik tahlil qilish
- **Ishtirokchilarni Baholash** - Har bir ishtirokchini tender talablariga mosligi bo'yicha baholash
- **Anti-Fraud Tizimi** - Korrupsiya va firibgarlik belgilarini avtomatik aniqlash
- **Ko'p tilli qo'llab-quvvatlash** - O'zbek va Rus tillarida interfeys
- **Qorong'u/Yorug' mavzu** - Foydalanuvchi xohishiga ko'ra tema tanlash

## 🏗️ Arxitektura

Tizim quyidagi asosiy modullardan iborat:

1. **Tender Tahlili** - PDF/DOCX/TXT formatidagi tender shartlarini AI orqali tahlil qilish
2. **Ishtirokchilar Baholash** - Takliflarni tender talablariga mosligini tekshirish va ball berish
3. **Anti-Fraud** - Narx anomaliyalari, hujjat o'xshashligi va kelishilgan takliflarni aniqlash
4. **Tarix** - Barcha tahlillar tarixi va natijalarini saqlash

## 🚀 Texnologik Stek

### Backend
- **Framework**: Django 5.0.1 + Django REST Framework
- **Ma'lumotlar bazasi**: SQLite (development) / PostgreSQL (production)
- **AI Engine**: OpenAI GPT-4o-mini

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
# venv\Scripts\activate  # Windows

# Dependensiyalarni o'rnatish
pip install -r requirements.txt

# Migratsiyalarni yuritish
python manage.py migrate

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
`simple_settings.py` faylida OpenAI API kalitini sozlang:

```python
OPENAI_API_KEY = "your-openai-api-key-here"
```

## 🔐 Kirish

Tizimga kirish uchun:
- **Login**: `trest`
- **Parol**: `trest2026`

## 📊 Foydalanish

### 1. Tender Tahlili
1. "Tender Tahlili" sahifasiga o'ting
2. Tender hujjatini yuklang (PDF, DOCX yoki TXT)
3. "Tender Tahlil Qilish" tugmasini bosing
4. AI tender talablarini avtomatik aniqlaydi

### 2. Ishtirokchilarni Baholash
1. Tender tahlilidan so'ng, ishtirokchilar bo'limiga o'ting
2. Har bir ishtirokchi uchun hujjat yuklang
3. "Ishtirokchilarni Baholash" tugmasini bosing
4. AI barcha ishtirokchilarni tahlil qilib, reyting tuzadi

### 3. Anti-Fraud Tahlili
1. "Anti-Fraud" sahifasiga o'ting
2. Tender va ishtirokchilar ma'lumotlarini kiriting
3. AI quyidagilarni tekshiradi:
   - Narx anomaliyalari
   - Hujjat o'xshashligi
   - Kelishilgan takliflar

## 🎨 Interfeys

- **Bosh sahifa** - Statistika va tezkor amallar
- **Tender Tahlili** - Asosiy tahlil jarayoni
- **Tarix** - O'tgan tahlillar ro'yxati
- **Anti-Fraud** - Korrupsiyaga qarshi tekshiruv
- **Sozlamalar** - Tizim sozlamalari

### Til o'zgartirish
Header'dagi til tugmasini bosing (UZ/RU)

### Tema o'zgartirish
Header'dagi quyosh/oy tugmasini bosing

## 📈 Baholash Tizimi

Ishtirokchilar quyidagi mezonlar bo'yicha baholanadi:
- **Tender talablariga moslik** - Majburiy va qo'shimcha talablar
- **Narx tahlili** - Taklif narxi va uning adekvatligi
- **Xavf darajasi** - Past, O'rta, Yuqori

## 🔍 API Endpointlar

- `GET /api/stats/` - Statistika
- `POST /api/evaluations/analyze-tender/` - Tender tahlili
- `POST /api/evaluations/analyze-participant/` - Ishtirokchi tahlili
- `POST /api/evaluations/compare-participants/` - Ishtirokchilarni solishtirish
- `POST /api/anti-fraud/analyze/` - Anti-fraud tahlili

## 🔒 Xavfsizlik

- Session-based autentifikatsiya
- CORS sozlamalari
- Input validatsiya
- SQL Injection himoyasi (Django ORM)

## 📁 Loyiha Strukturasi

```
tanlov-ai/
├── apps/                    # Django ilovalari
│   ├── evaluations/         # Baholash moduli
│   ├── anti_fraud/          # Anti-fraud moduli
│   ├── compliance/          # Compliance moduli
│   ├── participants/        # Ishtirokchilar
│   └── tenders/             # Tenderlar
├── core/                    # Asosiy xizmatlar
│   ├── agents.py            # AI agentlar
│   ├── llm_engine.py        # LLM integratsiya
│   └── services.py          # Umumiy xizmatlar
├── frontend/                # React frontend
│   ├── src/
│   │   ├── components/      # UI komponentlar
│   │   ├── context/         # React Context
│   │   ├── pages/           # Sahifalar
│   │   └── store/           # Redux (qo'shimcha)
│   └── public/              # Statik fayllar
├── tanlov_ai/               # Django sozlamalari
└── requirements.txt         # Python dependensiyalar
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

### Production
```bash
# Backend
gunicorn tanlov_ai.wsgi:application --bind 0.0.0.0:8000

# Frontend
npm run build
# Build fayllarini Nginx orqali serve qilish
```

## 📄 Litsenziya

Bu loyiha MIT litsenziyasi ostida tarqatiladi.

## 📞 Aloqa

- **Tashkilot**: "Ko'pkapqurilish" AJ
- **Loyiha**: Tanlov AI - Tender Tahlil Tizimi

---

<p align="center">
  <strong>Tanlov AI</strong> - O'zbekistonning AI asoslangan tender tahlil tizimi! 🇺🇿
</p>
