from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'tenders', views.TenderViewSet)
router.register(r'documents', views.TenderDocumentViewSet)
router.register(r'requirements', views.TenderRequirementViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
