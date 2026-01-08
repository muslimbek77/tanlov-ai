from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'compliance-rules', views.ComplianceRuleViewSet)
router.register(r'compliance-checks', views.ComplianceCheckViewSet)
router.register(r'compliance-reports', views.ComplianceReportViewSet)
router.register(r'document-compliances', views.DocumentComplianceViewSet)
router.register(r'compliance-templates', views.ComplianceTemplateViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
