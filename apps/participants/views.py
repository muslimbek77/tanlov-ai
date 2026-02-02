from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Participant, TenderParticipant, ParticipantDocument
from .serializers import ParticipantSerializer, TenderParticipantSerializer, ParticipantDocumentSerializer


class ParticipantViewSet(viewsets.ModelViewSet):
    queryset = Participant.objects.all()  # Ishtirokchilar umumiy ma'lumot - barchaga ko'rinadi
    serializer_class = ParticipantSerializer
    permission_classes = [IsAuthenticated]


class TenderParticipantViewSet(viewsets.ModelViewSet):
    serializer_class = TenderParticipantSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Faqat joriy foydalanuvchining tenderlaridagi ishtirokchilar"""
        return TenderParticipant.objects.filter(tender__created_by=self.request.user)


class ParticipantDocumentViewSet(viewsets.ModelViewSet):
    serializer_class = ParticipantDocumentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Faqat joriy foydalanuvchining tenderlaridagi ishtirokchi hujjatlari"""
        return ParticipantDocument.objects.filter(
            tender_participant__tender__created_by=self.request.user
        )
