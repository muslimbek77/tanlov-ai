from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'tenders', views.TenderViewSet, basename='tender')
router.register(r'documents', views.TenderDocumentViewSet, basename='tenderdocument')
router.register(r'requirements', views.TenderRequirementViewSet, basename='tenderrequirement')

urlpatterns = [
    path('', include(router.urls)),
]
