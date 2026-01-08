from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from django.db import connection
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView


def health_check(request):
    """API Health check endpoint"""
    try:
        # Database connection test
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        db_status = "healthy"
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"
    
    return JsonResponse({
        "status": "ok",
        "database": db_status,
        "version": "1.0.0",
    })


def dashboard_stats(request):
    """Dashboard statistikasi"""
    from apps.tenders.models import Tender
    from apps.participants.models import Participant, TenderParticipant
    from apps.evaluations.models import Evaluation
    from apps.anti_fraud.models import FraudDetection
    from apps.compliance.models import ComplianceCheck
    
    try:
        total_tenders = Tender.objects.count()
        active_tenders = Tender.objects.filter(status='active').count()
        total_participants = Participant.objects.count()
        tender_participants = TenderParticipant.objects.count()
        total_evaluations = Evaluation.objects.count()
        fraud_detections = FraudDetection.objects.count()
        high_risk_frauds = FraudDetection.objects.filter(severity__in=['high', 'critical']).count()
        compliance_checks = ComplianceCheck.objects.count()
        compliance_passed = ComplianceCheck.objects.filter(status='passed').count()
        
        return JsonResponse({
            "success": True,
            "stats": {
                "total_tenders": total_tenders,
                "active_tenders": active_tenders,
                "total_participants": total_participants,
                "tender_participants": tender_participants,
                "total_evaluations": total_evaluations,
                "fraud_detections": fraud_detections,
                "high_risk_frauds": high_risk_frauds,
                "compliance_checks": compliance_checks,
                "compliance_passed": compliance_passed,
            }
        })
    except Exception as e:
        return JsonResponse({
            "success": False,
            "error": str(e),
            "stats": {
                "total_tenders": 0,
                "active_tenders": 0,
                "total_participants": 0,
                "tender_participants": 0,
                "total_evaluations": 0,
                "fraud_detections": 0,
                "high_risk_frauds": 0,
                "compliance_checks": 0,
                "compliance_passed": 0,
            }
        })


def api_info(request):
    """API umumiy ma'lumotlar"""
    return JsonResponse({
        "name": "Tanlov AI API",
        "version": "1.0.0",
        "description": "Davlat xaridlari uchun AI asosida multi-agent tizimi",
        "endpoints": {
            "health": "/api/health/",
            "docs": "/api/docs/",
            "schema": "/api/schema/",
            "tenders": "/api/tenders/",
            "participants": "/api/participants/",
            "evaluations": "/api/evaluations/",
            "anti_fraud": "/api/anti-fraud/",
            "compliance": "/api/compliance/",
        }
    })


def system_status(request):
    """Tizim holati"""
    from core.llm_engine import llm_engine
    import os
    
    # LLM provayderlari holati
    llm_status = llm_engine.get_status() if hasattr(llm_engine, 'get_status') else {}
    
    # OpenAI kaliti mavjudligi
    openai_key = os.getenv('OPENAI_API_KEY', '')
    openai_configured = bool(openai_key and len(openai_key) > 10)
    
    return JsonResponse({
        "success": True,
        "backend": True,
        "database": True,
        "llm": {
            "openai": {
                "configured": openai_configured,
                "model": os.getenv('OPENAI_MODEL', 'gpt-4o'),
            },
            "ollama": {
                "configured": False,
                "available": False,
            },
            "active_provider": "openai" if openai_configured else None
        },
        "version": "1.0.0"
    })


urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Health check va API info
    path('api/health/', health_check, name='health-check'),
    path('api/stats/', dashboard_stats, name='dashboard-stats'),
    path('api/status/', system_status, name='system-status'),
    path('api/', api_info, name='api-info'),
    
    # OpenAPI Schema va Dokumentatsiya
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    
    # App URLlar
    path('api/tenders/', include('apps.tenders.urls')),
    path('api/participants/', include('apps.participants.urls')),
    path('api/evaluations/', include('apps.evaluations.urls')),
    path('api/anti-fraud/', include('apps.anti_fraud.urls')),
    path('api/compliance/', include('apps.compliance.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
