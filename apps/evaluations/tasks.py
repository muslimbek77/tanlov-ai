from celery import shared_task
from django.utils import timezone
import logging
from typing import Dict, Any
from .services import scoring_engine
from .models import Evaluation, EvaluationLog
from apps.tenders.models import Tender

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def evaluate_tender_participants(self, tender_id: int, evaluator_id: int = None) -> Dict[str, Any]:
    """
    Tender ishtirokchilarini baholash (asinxron)
    """
    try:
        tender = Tender.objects.get(id=tender_id)
        logger.info(f"Asinxron tender baholash boshlandi: {tender_id}")
        
        # Baholashni amalga oshirish
        results = scoring_engine.evaluate_tender_participants(tender, evaluator_id)
        
        if 'error' in results:
            logger.error(f"Tender baholashda xatolik: {results['error']}")
            return {
                'status': 'error',
                'tender_id': tender_id,
                'error': results['error'],
            }
        
        logger.info(f"Asinxron tender baholash yakunlandi: {tender_id}")
        return {
            'status': 'success',
            'tender_id': tender_id,
            'evaluation_id': results['evaluation_id'],
            'total_participants': results['summary']['total_participants'],
            'qualified_count': results['summary']['qualified_count'],
        }
    
    except Tender.DoesNotExist:
        logger.error(f"Tender topilmadi: {tender_id}")
        return {
            'status': 'error',
            'tender_id': tender_id,
            'error': 'Tender topilmadi',
        }
    
    except Exception as e:
        logger.error(f"Asinxron tender baholashda xatolik: {str(e)}")
        if self.request.retries < self.max_retries:
            return self.retry(countdown=60 * (self.request.retries + 1))
        
        return {
            'status': 'error',
            'tender_id': tender_id,
            'error': str(e),
        }


@shared_task(bind=True, max_retries=2)
def generate_evaluation_report(self, evaluation_id: int) -> Dict[str, Any]:
    """
    Baholash hisobotini generatsiya qilish
    """
    try:
        evaluation = Evaluation.objects.get(id=evaluation_id)
        logger.info(f"Baholash hisoboti generatsiyasi boshlandi: {evaluation_id}")
        
        # Baholash natijalarini olish
        results = scoring_engine.get_evaluation_results(evaluation_id)
        
        if 'error' in results:
            logger.error(f"Baholash hisobotini generatsiyada xatolik: {results['error']}")
            return {
                'status': 'error',
                'evaluation_id': evaluation_id,
                'error': results['error'],
            }
        
        # Log qilish
        EvaluationLog.objects.create(
            evaluation=evaluation,
            log_type='info',
            message='Baholash hisoboti generatsiya qilindi',
            details={'report_generated': True},
            agent_name='EvaluationTask',
            agent_type='reporting'
        )
        
        logger.info(f"Baholash hisoboti generatsiyasi yakunlandi: {evaluation_id}")
        return {
            'status': 'success',
            'evaluation_id': evaluation_id,
            'report_data': results,
        }
    
    except Evaluation.DoesNotExist:
        logger.error(f"Baholash topilmadi: {evaluation_id}")
        return {
            'status': 'error',
            'evaluation_id': evaluation_id,
            'error': 'Baholash topilmadi',
        }
    
    except Exception as e:
        logger.error(f"Baholash hisobotini generatsiyada xatolik: {str(e)}")
        if self.request.retries < self.max_retries:
            return self.retry(countdown=30 * (self.request.retries + 1))
        
        return {
            'status': 'error',
            'evaluation_id': evaluation_id,
            'error': str(e),
        }


@shared_task
def cleanup_completed_evaluations():
    """
    Yakunlangan baholashlarni tozalash
    """
    try:
        # 30 kundan oldin yakunlangan baholashlarni topish
        cutoff_date = timezone.now() - timezone.timedelta(days=30)
        
        old_evaluations = Evaluation.objects.filter(
            completed_at__lt=cutoff_date,
            status='completed'
        )
        
        count = old_evaluations.count()
        
        # Bu yerda arxivlash yoki tozalash logikasi bo'lishi mumkin
        # Hozircha faqat log qilamiz
        logger.info(f"{count} ta eski baholash topildi (30 kun oldin)")
        
        return {
            'status': 'success',
            'cleaned_count': count,
            'cutoff_date': cutoff_date.isoformat(),
        }
    
    except Exception as e:
        logger.error(f"Eski baholashlarni tozalashda xatolik: {str(e)}")
        return {
            'status': 'error',
            'error': str(e),
        }


@shared_task
def check_pending_evaluations():
    """
    Kutilayotgan baholashlarni tekshirish
    """
    try:
        pending_evaluations = Evaluation.objects.filter(status='pending')
        
        for evaluation in pending_evaluations:
            # Avtomatik ravishda baholashni boshlash
            evaluate_tender_participants.delay(
                evaluation.tender.id,
                evaluation.evaluator_id
            )
        
        count = pending_evaluations.count()
        logger.info(f"{count} ta kutilayotgan baholash topildi va boshlandi")
        
        return {
            'status': 'success',
            'started_count': count,
        }
    
    except Exception as e:
        logger.error(f"Kutilayotgan baholashlarni tekshirishda xatolik: {str(e)}")
        return {
            'status': 'error',
            'error': str(e),
        }
