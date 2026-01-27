# Tanlov AI - Delete Endpoint va Token Refresh Fix

## Muammolar va Yechimlar

### 1. Delete Endpoint Muammosi
**Muammo**: `api/evaluations/history/1/delete/` endpoint ishlamayapti, autentifikatsiya yo'q edi

**Yechim**:
- [apps/evaluations/analysis_views.py](apps/evaluations/analysis_views.py#L1298) da `delete_analysis_result` funksiyasiga `@permission_classes([IsAuthenticated])` qo'shildi
- Duplicate `@api_view` decoratorlar olib tashlandi
- User-specific deletion check qo'shildi (foydalanuvchi o'zining natijalaritagina o'chira oladi)

### 2. JWT Token Refresh Muammosi
**Muammo**: Access token 12 soatda amal qilardi va refresh token sistemasi to'g'ri ishlamayapti

**Backend Yechim**:
- [tanlov_ai/settings.py](tanlov_ai/settings.py#L157) da `ACCESS_TOKEN_LIFETIME` 12 soatdan 2 soatga qisqartirdi
- `ROTATE_REFRESH_TOKENS` va `BLACKLIST_AFTER_ROTATION` ni faollashtirdi

### 3. Frontend Token Refresh
**Yechim**:
- [frontend/src/lib/api-client.ts](frontend/src/lib/api-client.ts) - Yangi Axios interceptor yaratildi
  - Request interceptor: Har bir so'rovga access token qo'shadi
  - Response interceptor: 401 xatolikda token refresh qiladi va so'rovni qaytadan yuboradi
  - Token queue sistema: Multiple so'rovlar bir vaqtda refresh qilsa ham xato bo'lmasligi uchun

- [frontend/src/pages/TenderAnalysis.tsx](frontend/src/pages/TenderAnalysis.tsx#L288) da `deleteSavedResult` funksiyasini yangilandi
  - Authorization header qo'shildi
  - Token refresh logic qo'shildi
  - Retry mechanism qo'shildi

- [frontend/src/pages/AnalysisHistory.tsx](frontend/src/pages/AnalysisHistory.tsx#L195) da `deleteResult` funksiyasini yangilandi
  - Butun delete API integration yangilandi
  - Token refresh va retry logic qo'shildi

### 4. Authentication va User Ownership
**Yechim**:
- [apps/evaluations/models.py](apps/evaluations/models.py#L159) da `TenderAnalysisResult` modeliga `user` field qo'shildi
- [apps/evaluations/migrations/0003_tenderanalysisresult_user.py](apps/evaluations/migrations/0003_tenderanalysisresult_user.py) migration yaratildi va applied

### 5. API Endpoints Authentication
Quyidagi endpointlarga authentication qo'shildi:
- `save_analysis_result` - `@permission_classes([IsAuthenticated])`
- `get_analysis_history` - User-specific filtering
- `get_analysis_detail` - User ownership check
- `delete_analysis_result` - `@permission_classes([IsAuthenticated])`

## Database Migration
```bash
# Migration yaratildi va applied
python manage.py makemigrations evaluations
python manage.py migrate evaluations
```

## Testing

### Backend Test
```bash
# 1. Login qiling va access token oling
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "user", "password": "password"}'

# 2. Delete so'rovi yuboring
curl -X POST http://localhost:8000/api/evaluations/history/1/delete/ \
  -H "Authorization: Bearer {access_token}" \
  -H "Content-Type: application/json"

# 3. Token refresh qilish
curl -X POST http://localhost:8000/api/auth/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{"refresh": "{refresh_token}"}'
```

### Frontend Test
1. Login qiling
2. Tender tahlili save qiling
3. History sahifasida o'chirish tugmasini bosing
4. Token 2 soatdan ko'p bo'lsa, refresh avtomatik ishlaydi

## Token Lifecycle
1. **Login**: access_token (2 soat) + refresh_token (7 kun) oladi
2. **During Usage**: 
   - Access token tugaganda 401 xatolik oladi
   - Frontend refresh token orqali yangi access token oladi
   - So'rov qaytadan yuboriladi
3. **Refresh Token Rotation**: Har bir refresh qilishda yangi refresh token ham oladi

## Security Features
✅ User-specific data access (har foydalanuvchi faqat o'zining datalarini ko'radi)
✅ Token expiration (2 soat + 7 kun)
✅ Token rotation (har refresh qilishda yangi token)
✅ Token blacklist (logout bo'lganda)
✅ 401 handling (frontend avtomatik refresh qiladi)
