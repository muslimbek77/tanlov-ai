from rest_framework import serializers
from .models import Participant, TenderParticipant, ParticipantDocument


class ParticipantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Participant
        fields = '__all__'


class TenderParticipantSerializer(serializers.ModelSerializer):
    class Meta:
        model = TenderParticipant
        fields = '__all__'


class ParticipantDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParticipantDocument
        fields = '__all__'
