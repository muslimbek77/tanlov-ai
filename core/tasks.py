from celery import shared_task
from django.core.files.base import ContentFile
from django.utils import timezone
import logging
from typing import Dict, Any
from .services import document_processor, embedding_service
from apps.tenders.models import Tender, TenderDocument, TenderRequirement
from apps.participants.models import TenderParticipant, ParticipantDocument

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def process_tender_document(self, document_id: int) -> Dict[str, Any]:
    """
    Tender hujjatini qayta ishlash
    """
    try:
        document = TenderDocument.objects.get(id=document_id)
        logger.info(f"Tender hujjatini qayta ishlash boshlandi: {document.id}")
        
        # Hujjatni qayta ishlash
        result = document_processor.process_document(document.file.path)
        
        if result['processing_status'] == 'success':
            # Matnni saqlash
            document.extracted_text = result['text_content']
            document.is_processed = True
            
            # Metadata yangilash
            metadata = result['metadata']
            document.file_size = metadata.get('file_size', document.file_size)
            document.file_type = metadata.get('file_type', document.file_type)
            document.page_count = metadata.get('page_count')
            
            document.save()
            
            # Vektor embeddinglar yaratish
            if embedding_service.model_type:
                content_chunks = result['vector_data']['content_chunks']
                metadata_chunks = result['vector_data']['metadata_chunks']
                all_chunks = content_chunks + metadata_chunks
                
                embeddings = embedding_service.create_embeddings(all_chunks)
                
                # Vektorlarni saqlash (bu yerda vektor ma'lumotlar bazasiga yoziladi)
                # Hozircha faqat log qilamiz
                logger.info(f"Vektorlar yaratildi: {len(embeddings)} ta")
            
            # Tender talablarini avtomatik ajratish
            if document.document_type == 'requirements':
                extract_tender_requirements.delay(document.tender.id, result['structured_data'])
            
            logger.info(f"Tender hujjati muvaffaqiyatli qayta ishlindi: {document.id}")
            return {
                'status': 'success',
                'document_id': document_id,
                'processed_text_length': len(result['text_content']),
                'chunks_created': len(all_chunks) if embedding_service.model_type else 0,
            }
        
        else:
            logger.error(f"Hujjatni qayta ishlashda xatolik: {result.get('error')}")
            return {
                'status': 'error',
                'document_id': document_id,
                'error': result.get('error'),
            }
    
    except TenderDocument.DoesNotExist:
        logger.error(f"Tender hujjati topilmadi: {document_id}")
        return {
            'status': 'error',
            'document_id': document_id,
            'error': 'Hujjat topilmadi',
        }
    
    except Exception as e:
        logger.error(f"Tender hujjatini qayta ishlashda xatolik: {str(e)}")
        if self.request.retries < self.max_retries:
            return self.retry(countdown=60 * (self.request.retries + 1))
        
        return {
            'status': 'error',
            'document_id': document_id,
            'error': str(e),
        }


@shared_task(bind=True, max_retries=3)
def process_participant_document(self, document_id: int) -> Dict[str, Any]:
    """
    Ishtirokchi hujjatini qayta ishlash
    """
    try:
        document = ParticipantDocument.objects.get(id=document_id)
        logger.info(f"Ishtirokchi hujjatini qayta ishlash boshlandi: {document.id}")
        
        # Hujjatni qayta ishlash
        result = document_processor.process_document(document.file.path)
        
        if result['processing_status'] == 'success':
            # Matnni saqlash
            document.extracted_text = result['text_content']
            document.is_processed = True
            
            # Metadata yangilash
            metadata = result['metadata']
            document.file_size = metadata.get('file_size', document.file_size)
            document.file_type = metadata.get('file_type', document.file_type)
            document.page_count = metadata.get('page_count')
            
            # Audit metadata
            document.created_by_software = metadata.get('creator', '')
            document.creation_date = timezone.now()
            if metadata.get('creation_date'):
                try:
                    from datetime import datetime
                    document.creation_date = datetime.fromisoformat(metadata['creation_date'].replace('D:', ''))
                except:
                    pass
            
            document.save()
            
            # Vektor embeddinglar yaratish
            if embedding_service.model_type:
                content_chunks = result['vector_data']['content_chunks']
                metadata_chunks = result['vector_data']['metadata_chunks']
                all_chunks = content_chunks + metadata_chunks
                
                embeddings = embedding_service.create_embeddings(all_chunks)
                logger.info(f"Vektorlar yaratildi: {len(embeddings)} ta")
            
            logger.info(f"Ishtirokchi hujjati muvaffaqiyatli qayta ishlindi: {document.id}")
            return {
                'status': 'success',
                'document_id': document_id,
                'processed_text_length': len(result['text_content']),
                'chunks_created': len(all_chunks) if embedding_service.model_type else 0,
            }
        
        else:
            logger.error(f"Hujjatni qayta ishlashda xatolik: {result.get('error')}")
            return {
                'status': 'error',
                'document_id': document_id,
                'error': result.get('error'),
            }
    
    except ParticipantDocument.DoesNotExist:
        logger.error(f"Ishtirokchi hujjati topilmadi: {document_id}")
        return {
            'status': 'error',
            'document_id': document_id,
            'error': 'Hujjat topilmadi',
        }
    
    except Exception as e:
        logger.error(f"Ishtirokchi hujjatini qayta ishlashda xatolik: {str(e)}")
        if self.request.retries < self.max_retries:
            return self.retry(countdown=60 * (self.request.retries + 1))
        
        return {
            'status': 'error',
            'document_id': document_id,
            'error': str(e),
        }


@shared_task(bind=True)
def extract_tender_requirements(self, tender_id: int, structured_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Tender talablarini avtomatik ajratish
    """
    try:
        tender = Tender.objects.get(id=tender_id)
        logger.info(f"Talablarni ajratish boshlandi: Tender {tender_id}")
        
        requirements_extracted = 0
        
        for section in structured_data.get('sections', []):
            title = section['title'].lower()
            content = ' '.join(section['content'])
            
            # Turli xil talab turlarini aniqlash
            if any(keyword in title for keyword in ['texnik', 'technical', 'технический']):
                # Texnik talablar
                requirements = _extract_requirements_from_text(content, 'technical')
                for req in requirements:
                    TenderRequirement.objects.create(
                        tender=tender,
                        title=req['title'],
                        description=req['description'],
                        requirement_type='technical',
                        weight=1.0,
                        max_score=10.0,
                        is_mandatory=req.get('mandatory', False)
                    )
                    requirements_extracted += 1
            
            elif any(keyword in title for keyword in ['moliyaviy', 'financial', 'финансовый']):
                # Moliyaviy talablar
                requirements = _extract_requirements_from_text(content, 'financial')
                for req in requirements:
                    TenderRequirement.objects.create(
                        tender=tender,
                        title=req['title'],
                        description=req['description'],
                        requirement_type='financial',
                        weight=1.5,
                        max_score=15.0,
                        is_mandatory=req.get('mandatory', False)
                    )
                    requirements_extracted += 1
            
            elif any(keyword in title for keyword in ['tajriba', 'experience', 'опыт']):
                # Tajriba talablari
                requirements = _extract_requirements_from_text(content, 'experience')
                for req in requirements:
                    TenderRequirement.objects.create(
                        tender=tender,
                        title=req['title'],
                        description=req['description'],
                        requirement_type='experience',
                        weight=2.0,
                        max_score=20.0,
                        is_mandatory=req.get('mandatory', True)
                    )
                    requirements_extracted += 1
        
        logger.info(f"{requirements_extracted} ta talab ajratildi")
        return {
            'status': 'success',
            'tender_id': tender_id,
            'requirements_extracted': requirements_extracted,
        }
    
    except Tender.DoesNotExist:
        logger.error(f"Tender topilmadi: {tender_id}")
        return {
            'status': 'error',
            'tender_id': tender_id,
            'error': 'Tender topilmadi',
        }
    
    except Exception as e:
        logger.error(f"Talablarni ajratishda xatolik: {str(e)}")
        return {
            'status': 'error',
            'tender_id': tender_id,
            'error': str(e),
        }


def _extract_requirements_from_text(text: str, requirement_type: str) -> list:
    """
    Matndan talablarni ajratish
    """
    requirements = []
    
    # Oddiy qoidalar asosida talablarni ajratish
    import re
    
    # Raqamlangan ro'yxatlarni topish
    numbered_items = re.findall(r'^\d+\.?\s*(.+?)(?=\n\d+\.|\n\n|\Z)', text, re.MULTILINE | re.DOTALL)
    
    for item in numbered_items:
        item = item.strip()
        if len(item) > 10:  # Juda qisqa elementlarni e'tiborsiz qoldirish
            # Sarlavha va tavsifni ajratish
            lines = item.split('\n')
            title = lines[0].strip()
            description = '\n'.join(lines[1:]).strip() if len(lines) > 1 else ''
            
            # Majburiylikni aniqlash
            mandatory = any(keyword in title.lower() for keyword in [
                'majburiy', 'majbur', 'обязательно', 'required', 'must'
            ])
            
            requirements.append({
                'title': title,
                'description': description,
                'mandatory': mandatory,
            })
    
    # Agar raqamlangan ro'yxat bo'lmasa, butun matnni bitta talab sifatida qo'shish
    if not requirements and len(text.strip()) > 50:
        requirements.append({
            'title': f"{requirement_type.title()} talabi",
            'description': text.strip(),
            'mandatory': requirement_type in ['experience', 'legal'],
        })
    
    return requirements


@shared_task(bind=True)
def batch_process_documents(self, document_ids: list, document_type: str = 'tender') -> Dict[str, Any]:
    """
    Hujjatlarni paketlab qayta ishlash
    """
    results = {
        'total': len(document_ids),
        'successful': 0,
        'failed': 0,
        'errors': [],
    }
    
    for doc_id in document_ids:
        try:
            if document_type == 'tender':
                result = process_tender_document(doc_id)
            else:
                result = process_participant_document(doc_id)
            
            if result.get('status') == 'success':
                results['successful'] += 1
            else:
                results['failed'] += 1
                results['errors'].append({
                    'document_id': doc_id,
                    'error': result.get('error', 'Noma\'lum xatolik'),
                })
        
        except Exception as e:
            results['failed'] += 1
            results['errors'].append({
                'document_id': doc_id,
                'error': str(e),
            })
    
    logger.info(f"Paket qayta ishlash yakunlandi: {results['successful']}/{results['total']} muvaffaqiyatli")
    return results
