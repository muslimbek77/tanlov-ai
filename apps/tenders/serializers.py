from rest_framework import serializers
from .models import Tender, TenderDocument, TenderRequirement


class TenderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tender
        fields = '__all__'


class TenderDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = TenderDocument
        fields = '__all__'


class TenderRequirementSerializer(serializers.ModelSerializer):
    class Meta:
        model = TenderRequirement
        fields = '__all__'
