from rest_framework import viewsets
from .models import Participant, TenderParticipant, ParticipantDocument
from .serializers import ParticipantSerializer, TenderParticipantSerializer, ParticipantDocumentSerializer


class ParticipantViewSet(viewsets.ModelViewSet):
    queryset = Participant.objects.all()
    serializer_class = ParticipantSerializer


class TenderParticipantViewSet(viewsets.ModelViewSet):
    queryset = TenderParticipant.objects.all()
    serializer_class = TenderParticipantSerializer


class ParticipantDocumentViewSet(viewsets.ModelViewSet):
    queryset = ParticipantDocument.objects.all()
    serializer_class = ParticipantDocumentSerializer
