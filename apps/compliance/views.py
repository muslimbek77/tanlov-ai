from rest_framework import viewsets
from .models import ComplianceRule, ComplianceCheck, ComplianceReport, DocumentCompliance, ComplianceTemplate
from .serializers import (
    ComplianceRuleSerializer, ComplianceCheckSerializer, 
    ComplianceReportSerializer, DocumentComplianceSerializer, 
    ComplianceTemplateSerializer
)


class ComplianceRuleViewSet(viewsets.ModelViewSet):
    queryset = ComplianceRule.objects.all()
    serializer_class = ComplianceRuleSerializer


class ComplianceCheckViewSet(viewsets.ModelViewSet):
    queryset = ComplianceCheck.objects.all()
    serializer_class = ComplianceCheckSerializer


class ComplianceReportViewSet(viewsets.ModelViewSet):
    queryset = ComplianceReport.objects.all()
    serializer_class = ComplianceReportSerializer


class DocumentComplianceViewSet(viewsets.ModelViewSet):
    queryset = DocumentCompliance.objects.all()
    serializer_class = DocumentComplianceSerializer


class ComplianceTemplateViewSet(viewsets.ModelViewSet):
    queryset = ComplianceTemplate.objects.all()
    serializer_class = ComplianceTemplateSerializer
