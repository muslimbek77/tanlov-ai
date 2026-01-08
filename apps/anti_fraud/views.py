from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import FraudDetection, MetadataAnalysis, PriceAnomalyDetection, SimilarityAnalysis, FraudDetectionRule
from .serializers import (
    FraudDetectionSerializer, MetadataAnalysisSerializer, 
    PriceAnomalyDetectionSerializer, SimilarityAnalysisSerializer, 
    FraudDetectionRuleSerializer
)
from core.llm_engine import llm_engine
import json
import re
import logging

logger = logging.getLogger(__name__)


@api_view(['POST'])
def analyze_fraud(request):
    """
    AI yordamida firibgarlik tahlili
    
    Body:
        - participants: Ishtirokchilar ro'yxati (har birida name, price, documents)
        - tender_info: Tender ma'lumotlari (optional)
    """
    try:
        participants = request.data.get('participants', [])
        tender_info = request.data.get('tender_info', {})
        
        if len(participants) < 2:
            return Response({
                'success': False,
                'error': 'Kamida 2 ta ishtirokchi talab qilinadi'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Ishtirokchilar ma'lumotlarini tayyorlash
        participants_text = ""
        for i, p in enumerate(participants, 1):
            participants_text += f"""
Ishtirokchi #{i}: {p.get('name', 'Noma\'lum')}
- Taklif narxi: {p.get('price', 'Noma\'lum')}
- Hujjatlar: {p.get('documents', 'Noma\'lum')}
- Qo'shimcha: {p.get('details', '')}
"""
        
        # LLM orqali tahlil
        analysis_prompt = f"""
Sen korrupsiya va firibgarlikni aniqlash bo'yicha ekspertsan.
Quyidagi tender ishtirokchilarini CHUQUR tahlil qil va shubhali belgilarni aniqla.

TENDER MA'LUMOTLARI:
{json.dumps(tender_info, ensure_ascii=False, indent=2) if tender_info else 'Mavjud emas'}

ISHTIROKCHILAR:
{participants_text}

QUYIDAGILARNI TEKSHIR:

1. NARX ANOMALIYALARI:
   - G'ayrioddiy past yoki yuqori narxlar
   - O'xshash narxlar (kelishilgan narxlar)
   - Sun'iy yaxlitlangan narxlar
   - Dumping narxlar

2. HUJJAT O'XSHASHLIGI:
   - Bir xil shablonlar
   - Bir xil xatolar
   - Bir xil formatlash
   - Metadata o'xshashligi (yaratilgan vaqt, dastur)

3. KELISHILGAN TAKLIFLAR BELGILARI:
   - Narxlarning ketma-ketligi
   - Bir xil kamchiliklar
   - G'olib oldindan ma'lum bo'lishi
   - Boshqalar ataylab past sifatli

4. BOSHQA XAVFLAR:
   - Soxta kompaniyalar
   - Bog'liq kompaniyalar
   - Manfaatlar to'qnashuvi

JSON FORMAT:
{{
    "overall_risk_level": "low|medium|high|critical",
    "overall_risk_score": 0-100,
    "fraud_indicators": [
        {{
            "type": "price_anomaly|document_similarity|collusion|other",
            "severity": "low|medium|high|critical",
            "title": "Xavf sarlavhasi",
            "description": "Batafsil tavsif",
            "involved_participants": ["Ishtirokchi nomlari"],
            "evidence": "Dalillar",
            "risk_score": 0-100
        }}
    ],
    "price_analysis": {{
        "min_price": "Minimal narx",
        "max_price": "Maksimal narx",
        "average_price": "O'rtacha narx",
        "price_spread": "Narx farqi %",
        "suspicious_prices": ["Shubhali narxlar"],
        "analysis": "Narx tahlili xulosasi"
    }},
    "similarity_analysis": {{
        "document_similarity_score": 0-100,
        "suspicious_patterns": ["Shubhali patternlar"],
        "analysis": "O'xshashlik tahlili xulosasi"
    }},
    "collusion_analysis": {{
        "collusion_probability": 0-100,
        "indicators": ["Kelishilgan taklif belgilari"],
        "analysis": "Kelishilgan takliflar xulosasi"
    }},
    "recommendations": ["Tavsiyalar ro'yxati"],
    "summary": "Umumiy xulosa"
}}
"""
        
        llm_result = llm_engine.generate_response(
            analysis_prompt,
            system_prompt="Sen korrupsiya va firibgarlikni aniqlash bo'yicha yuqori malakali ekspertsan. Tender jarayonlaridagi barcha shubhali belgilarni aniqlay olasan. Faqat JSON formatida javob ber.",
            temperature=0.2
        )
        
        if not llm_result.get('success'):
            return Response({
                'success': False,
                'error': llm_result.get('error', 'LLM xatolik berdi')
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        result = llm_result.get('response', '')
        
        # JSON parse
        try:
            json_match = re.search(r'\{[\s\S]*\}', result)
            if json_match:
                json_str = json_match.group()
                json_str = re.sub(r',\s*}', '}', json_str)
                json_str = re.sub(r',\s*]', ']', json_str)
                json_str = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', json_str)
                analysis = json.loads(json_str)
            else:
                raise ValueError("JSON topilmadi")
        except json.JSONDecodeError as e:
            logger.error(f"JSON parse xatosi: {e}")
            # Fallback
            analysis = {
                "overall_risk_level": "medium",
                "overall_risk_score": 50,
                "fraud_indicators": [],
                "summary": result[:500],
                "recommendations": ["Qo'shimcha tekshiruv talab qilinadi"]
            }
        
        return Response({
            'success': True,
            'analysis': analysis,
            'participants_count': len(participants)
        })
        
    except Exception as e:
        logger.error(f"Fraud tahlilida xatolik: {str(e)}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class FraudDetectionViewSet(viewsets.ModelViewSet):
    queryset = FraudDetection.objects.all()
    serializer_class = FraudDetectionSerializer


class MetadataAnalysisViewSet(viewsets.ModelViewSet):
    queryset = MetadataAnalysis.objects.all()
    serializer_class = MetadataAnalysisSerializer


class PriceAnomalyDetectionViewSet(viewsets.ModelViewSet):
    queryset = PriceAnomalyDetection.objects.all()
    serializer_class = PriceAnomalyDetectionSerializer


class SimilarityAnalysisViewSet(viewsets.ModelViewSet):
    queryset = SimilarityAnalysis.objects.all()
    serializer_class = SimilarityAnalysisSerializer


class FraudDetectionRuleViewSet(viewsets.ModelViewSet):
    queryset = FraudDetectionRule.objects.all()
    serializer_class = FraudDetectionRuleSerializer
