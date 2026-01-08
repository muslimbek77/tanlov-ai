from rest_framework import serializers
from .models import FraudDetection, MetadataAnalysis, PriceAnomalyDetection, SimilarityAnalysis, FraudDetectionRule


class FraudDetectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = FraudDetection
        fields = '__all__'


class MetadataAnalysisSerializer(serializers.ModelSerializer):
    class Meta:
        model = MetadataAnalysis
        fields = '__all__'


class PriceAnomalyDetectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PriceAnomalyDetection
        fields = '__all__'


class SimilarityAnalysisSerializer(serializers.ModelSerializer):
    class Meta:
        model = SimilarityAnalysis
        fields = '__all__'


class FraudDetectionRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = FraudDetectionRule
        fields = '__all__'
