from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'participants', views.ParticipantViewSet)
router.register(r'tender-participants', views.TenderParticipantViewSet)
router.register(r'documents', views.ParticipantDocumentViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
