from rest_framework import serializers
from .models import ComplianceRule, ComplianceCheck, ComplianceReport, DocumentCompliance, ComplianceTemplate


class ComplianceRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = ComplianceRule
        fields = '__all__'


class ComplianceCheckSerializer(serializers.ModelSerializer):
    class Meta:
        model = ComplianceCheck
        fields = '__all__'


class ComplianceReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = ComplianceReport
        fields = '__all__'


class DocumentComplianceSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentCompliance
        fields = '__all__'


class ComplianceTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ComplianceTemplate
        fields = '__all__'
