from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'participants', views.ParticipantViewSet, basename='participant')
router.register(r'tender-participants', views.TenderParticipantViewSet, basename='tenderparticipant')
router.register(r'documents', views.ParticipantDocumentViewSet, basename='participantdocument')

urlpatterns = [
    path('', include(router.urls)),
]
