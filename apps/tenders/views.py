from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Tender, TenderDocument, TenderRequirement
from .serializers import TenderSerializer, TenderDocumentSerializer, TenderRequirementSerializer


class TenderViewSet(viewsets.ModelViewSet):
    queryset = Tender.objects.all()
    serializer_class = TenderSerializer
    
    @action(detail=True, methods=['post'])
    def upload_document(self, request, pk=None):
        """Tender hujjatini yuklash"""
        tender = self.get_object()
        serializer = TenderDocumentSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save(tender=tender)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def process_tender(self, request, pk=None):
        """Tenderni qayta ishlash"""
        tender = self.get_object()
        
        # Bu yerda tender qayta ishlash logikasi bo'ladi
        # Hozircha mock response
        return Response({
            'status': 'processing',
            'tender_id': tender.id,
            'message': 'Tender qayta ishlash boshlandi'
        })


class TenderDocumentViewSet(viewsets.ModelViewSet):
    queryset = TenderDocument.objects.all()
    serializer_class = TenderDocumentSerializer


class TenderRequirementViewSet(viewsets.ModelViewSet):
    queryset = TenderRequirement.objects.all()
    serializer_class = TenderRequirementSerializer
