from celery import shared_task
from django.utils import timezone
import logging
from typing import Dict, Any
from .services import anti_fraud_analyzer
from .models import FraudDetection, MetadataAnalysis, PriceAnomalyDetection, SimilarityAnalysis
from apps.tenders.models import Tender

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def analyze_tender_fraud(self, tender_id: int) -> Dict[str, Any]:
    """
    Tender uchun korrupsiya tahlilini amalga oshirish (asinxron)
    """
    try:
        tender = Tender.objects.get(id=tender_id)
        logger.info(f"Asinxron korrupsiya tahlili boshlandi: {tender_id}")
        
        # Korrupsiya tahlilini amalga oshirish
        results = anti_fraud_analyzer.analyze_tender_fraud_risks(tender)
        
        if 'error' in results:
            logger.error(f"Korrupsiya tahlilida xatolik: {results['error']}")
            return {
                'status': 'error',
                'tender_id': tender_id,
                'error': results['error'],
            }
        
        # Natijalarni saqlash
        saved_detections = []
        for detection_data in results['detections']:
            detection = FraudDetection.objects.create(
                tender=tender,
                detection_type=detection_data['detection_type'],
                severity=detection_data['severity'],
                title=detection_data.get('title', f"{detection_data['detection_type']} aniqlandi"),
                description=detection_data['description'],
                risk_score=detection_data['risk_score'],
                detection_data=detection_data.get('evidence', {}),
                evidence=detection_data.get('evidence', {})
            )
            
            # Ishtirokchilarni qo'shish
            if 'involved_participants' in detection_data:
                from apps.participants.models import TenderParticipant
                participants = TenderParticipant.objects.filter(
                    id__in=detection_data['involved_participants']
                )
                detection.involved_participants.set(participants)
            
            saved_detections.append(detection.id)
        
        logger.info(f"Asinxron korrupsiya tahlili yakunlandi: {tender_id}, {len(saved_detections)} ta xavf topildi")
        return {
            'status': 'success',
            'tender_id': tender_id,
            'total_risk_score': results['total_risk_score'],
            'risk_level': results['risk_level'],
            'detections_count': len(saved_detections),
            'saved_detection_ids': saved_detections,
        }
    
    except Tender.DoesNotExist:
        logger.error(f"Tender topilmadi: {tender_id}")
        return {
            'status': 'error',
            'tender_id': tender_id,
            'error': 'Tender topilmadi',
        }
    
    except Exception as e:
        logger.error(f"Asinxron korrupsiya tahlilida xatolik: {str(e)}")
        if self.request.retries < self.max_retries:
            return self.retry(countdown=60 * (self.request.retries + 1))
        
        return {
            'status': 'error',
            'tender_id': tender_id,
            'error': str(e),
        }


@shared_task(bind=True, max_retries=2)
def analyze_metadata_similarity(self, participant_ids: list) -> Dict[str, Any]:
    """
    Ishtirokchilar metadata o'xshashligini tahlil qilish
    """
    try:
        from apps.participants.models import TenderParticipant
        
        participants = TenderParticipant.objects.filter(id__in=participant_ids)
        logger.info(f"Metadata o'xshashligi tahlili boshlandi: {len(participants)} ta ishtirokchi")
        
        # Metadata tahlilini amalga oshirish
        results = anti_fraud_analyzer._analyze_metadata_similarity(participants)
        
        # Natijalarni saqlash
        saved_analyses = []
        for detection in results['detections']:
            # Bu yerda metadata tahlilini saqlash logikasi
            # Hozircha faqat log qilamiz
            logger.info(f"Metadata o'xshashligi aniqlandi: {detection['description']}")
        
        logger.info(f"Metadata o'xshashligi tahlili yakunlandi: {len(saved_analyses)} ta")
        return {
            'status': 'success',
            'analyzed_count': len(participants),
            'detections_count': len(results['detections']),
            'risk_score': results['risk_score'],
        }
    
    except Exception as e:
        logger.error(f"Metadata o'xshashligi tahlilida xatolik: {str(e)}")
        if self.request.retries < self.max_retries:
            return self.retry(countdown=30 * (self.request.retries + 1))
        
        return {
            'status': 'error',
            'error': str(e),
        }


@shared_task
def batch_analyze_active_tenders():
    """
    Faol tenderlarni paketlab tahlil qilish
    """
    try:
        # Faol tenderlarni topish
        active_tenders = Tender.objects.filter(
            status='active',
            end_date__gt=timezone.now()
        )
        
        analyzed_count = 0
        for tender in active_tenders:
            # Korrupsiya tahlilini boshlash
            analyze_tender_fraud.delay(tender.id)
            analyzed_count += 1
        
        logger.info(f"{analyzed_count} ta faol tender uchun korrupsiya tahlili boshlandi")
        return {
            'status': 'success',
            'analyzed_count': analyzed_count,
            'total_active': active_tenders.count(),
        }
    
    except Exception as e:
        logger.error(f"Faol tenderlarni paket tahlilida xatolik: {str(e)}")
        return {
            'status': 'error',
            'error': str(e),
        }


@shared_task
def cleanup_old_fraud_detections():
    """
    Eski korrupsiya aniqlashlarini tozalash
    """
    try:
        # 90 kundan oldin yaratilgan va hal qilingan yozuvlarni topish
        cutoff_date = timezone.now() - timezone.timedelta(days=90)
        
        old_detections = FraudDetection.objects.filter(
            created_at__lt=cutoff_date,
            status__in=['resolved', 'false_positive']
        )
        
        count = old_detections.count()
        
        # Bu yerda arxivlash yoki tozalash logikasi bo'lishi mumkin
        logger.info(f"{count} ta eski korrupsiya aniqlashi topildi (90 kun oldin)")
        
        return {
            'status': 'success',
            'cleaned_count': count,
            'cutoff_date': cutoff_date.isoformat(),
        }
    
    except Exception as e:
        logger.error(f"Eski korrupsiya aniqlashlarini tozalashda xatolik: {str(e)}")
        return {
            'status': 'error',
            'error': str(e),
        }
