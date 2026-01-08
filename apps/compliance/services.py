import logging
import re
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, date
from decimal import Decimal
from django.utils import timezone
from django.db.models import Q, Count, Avg
from .models import ComplianceRule, ComplianceCheck, ComplianceReport, DocumentCompliance
from apps.tenders.models import Tender, TenderRequirement
from apps.participants.models import TenderParticipant, ParticipantDocument

logger = logging.getLogger(__name__)


class ComplianceChecker:
    """Compliance tekshiruvi xizmati"""
    
    def __init__(self):
        self.orq_684_rules = self._load_orq_684_rules()
        self.default_rules = self._load_default_rules()
    
    def check_tender_compliance(self, tender: Tender) -> Dict[str, Any]:
        """
        Tender uchun compliance tekshiruvi
        """
        try:
            logger.info(f"Tender compliance tekshiruvi boshlandi: {tender.id}")
            
            results = {
                'tender_id': tender.id,
                'compliance_score': 0.0,
                'max_score': 100.0,
                'checks': [],
                'violations': [],
                'warnings': [],
                'status': 'pending',
            }
            
            # O'RQ-684 qoidalari bo'yicha tekshirish
            orq_results = self._check_orq_684_compliance(tender)
            results['checks'].extend(orq_results['checks'])
            results['violations'].extend(orq_results['violations'])
            results['warnings'].extend(orq_results['warnings'])
            
            # Hujjatlar compliance
            doc_results = self._check_document_compliance(tender)
            results['checks'].extend(doc_results['checks'])
            results['violations'].extend(doc_results['violations'])
            
            # Vaqt talablari
            time_results = self._check_time_compliance(tender)
            results['checks'].extend(time_results['checks'])
            results['violations'].extend(time_results['violations'])
            
            # Moliyaviy compliance
            financial_results = self._check_financial_compliance(tender)
            results['checks'].extend(financial_results['checks'])
            results['violations'].extend(financial_results['violations'])
            
            # Umumiy ballni hisoblash
            results['compliance_score'] = self._calculate_compliance_score(results['checks'])
            
            # Statusni aniqlash
            if results['compliance_score'] >= 90:
                results['status'] = 'passed'
            elif results['compliance_score'] >= 70:
                results['status'] = 'warning'
            else:
                results['status'] = 'failed'
            
            logger.info(f"Tender compliance tekshiruvi yakunlandi: Ball {results['compliance_score']}")
            return results
            
        except Exception as e:
            logger.error(f"Tender compliance tekshiruvida xatolik: {str(e)}")
            return {
                'tender_id': tender.id,
                'status': 'error',
                'error': str(e),
            }
    
    def check_participant_compliance(self, tender_participant: TenderParticipant) -> Dict[str, Any]:
        """
        Ishtirokchi uchun compliance tekshiruvi
        """
        try:
            logger.info(f"Ishtirokchi compliance tekshiruvi boshlandi: {tender_participant.id}")
            
            results = {
                'participant_id': tender_participant.id,
                'compliance_score': 0.0,
                'max_score': 100.0,
                'checks': [],
                'violations': [],
                'warnings': [],
                'status': 'pending',
            }
            
            # Hujjatlar mavjudligi
            doc_results = self._check_participant_documents(tender_participant)
            results['checks'].extend(doc_results['checks'])
            results['violations'].extend(doc_results['violations'])
            
            # Malaka talablari
            qual_results = self._check_qualification_compliance(tender_participant)
            results['checks'].extend(qual_results['checks'])
            results['violations'].extend(qual_results['violations'])
            
            # Moliyaviy talablar
            fin_results = self._check_participant_financial_compliance(tender_participant)
            results['checks'].extend(fin_results['checks'])
            results['violations'].extend(fin_results['violations'])
            
            # Texnik compliance
            tech_results = self._check_technical_compliance(tender_participant)
            results['checks'].extend(tech_results['checks'])
            results['violations'].extend(tech_results['violations'])
            
            # Umumiy ballni hisoblash
            results['compliance_score'] = self._calculate_compliance_score(results['checks'])
            
            # Statusni aniqlash
            if results['compliance_score'] >= 85:
                results['status'] = 'passed'
            elif results['compliance_score'] >= 60:
                results['status'] = 'warning'
            else:
                results['status'] = 'failed'
            
            logger.info(f"Ishtirokchi compliance tekshiruvi yakunlandi: Ball {results['compliance_score']}")
            return results
            
        except Exception as e:
            logger.error(f"Ishtirokchi compliance tekshiruvida xatolik: {str(e)}")
            return {
                'participant_id': tender_participant.id,
                'status': 'error',
                'error': str(e),
            }
    
    def _load_orq_684_rules(self) -> List[Dict[str, Any]]:
        """O'RQ-684 qoidalarini yuklash"""
        return [
            {
                'id': 'orq_684_001',
                'name': 'Tender e\'lon qilish muddati',
                'description': 'Tender e\'loni kamida 15 kun oldin e\'lon qilinishi kerak',
                'rule_type': 'time',
                'severity': 'high',
                'check_function': '_check_tender_announcement_period',
                'max_score': 15,
            },
            {
                'id': 'orq_684_002',
                'name': 'Hujjatlar taqdim etish muddati',
                'description': 'Hujjatlarni taqdim etish uchun kamida 10 kun vaqt bo\'lishi kerak',
                'rule_type': 'time',
                'severity': 'high',
                'check_function': '_check_document_submission_period',
                'max_score': 15,
            },
            {
                'id': 'orq_684_003',
                'name': 'Tender shartlarining to\'liqligi',
                'description': 'Tender shartnomasida barcha majburiy shartlar bo\'lishi kerak',
                'rule_type': 'document',
                'severity': 'critical',
                'check_function': '_check_tender_conditions_completeness',
                'max_score': 20,
            },
            {
                'id': 'orq_684_004',
                'name': 'Texnik spetsifikatsiya',
                'description': 'Texnik spetsifikatsiya aniq va o\'lchovli bo\'lishi kerak',
                'rule_type': 'technical',
                'severity': 'high',
                'check_function': '_check_technical_specification',
                'max_score': 15,
            },
            {
                'id': 'orq_684_005',
                'name': 'Baholash mezonlari',
                'description': 'Baholash mezonlari ochiq va obyektiv bo\'lishi kerak',
                'rule_type': 'evaluation',
                'severity': 'high',
                'check_function': '_check_evaluation_criteria',
                'max_score': 20,
            },
            {
                'id': 'orq_684_006',
                'name': 'Shartnoma shartlari',
                'description': 'Shartnoma shartlari qonun hujjatlariga mos kelishi kerak',
                'rule_type': 'legal',
                'severity': 'critical',
                'check_function': '_check_contract_terms',
                'max_score': 15,
            },
        ]
    
    def _load_default_rules(self) -> List[Dict[str, Any]]:
        """Standart compliance qoidalari"""
        return [
            {
                'id': 'def_001',
                'name': 'Byudjet chegaralari',
                'description': 'Tender summasi byudjet chegaralaridan oshmasligi kerak',
                'rule_type': 'financial',
                'severity': 'medium',
                'check_function': '_check_budget_limits',
                'max_score': 10,
            },
            {
                'id': 'def_002',
                'name': 'Kafolat miqdori',
                'description': 'Kafolat miqdori tender summasining 1-5% oralig\'ida bo\'lishi kerak',
                'rule_type': 'financial',
                'severity': 'medium',
                'check_function': '_check_guarantee_amount',
                'max_score': 10,
            },
        ]
    
    def _check_orq_684_compliance(self, tender: Tender) -> Dict[str, Any]:
        """O'RQ-684 ga muvofiqlikni tekshirish"""
        results = {
            'checks': [],
            'violations': [],
            'warnings': [],
        }
        
        for rule in self.orq_684_rules:
            try:
                check_function = getattr(self, rule['check_function'])
                check_result = check_function(tender, rule)
                
                results['checks'].append(check_result)
                
                if check_result['status'] == 'failed':
                    results['violations'].append({
                        'rule_id': rule['id'],
                        'rule_name': rule['name'],
                        'severity': rule['severity'],
                        'description': check_result['description'],
                        'recommendation': check_result.get('recommendation', ''),
                    })
                elif check_result['status'] == 'warning':
                    results['warnings'].append({
                        'rule_id': rule['id'],
                        'rule_name': rule['name'],
                        'description': check_result['description'],
                    })
            
            except Exception as e:
                logger.error(f"O'RQ-684 qoidasini tekshirishda xatolik {rule['id']}: {str(e)}")
                results['checks'].append({
                    'rule_id': rule['id'],
                    'status': 'error',
                    'error': str(e),
                })
        
        return results
    
    def _check_tender_announcement_period(self, tender: Tender, rule: Dict[str, Any]) -> Dict[str, Any]:
        """Tender e\'lon qilish muddatini tekshirish"""
        try:
            if tender.start_date and tender.created_at:
                announcement_period = (tender.start_date - tender.created_at).days
                
                if announcement_period >= 15:
                    return {
                        'rule_id': rule['id'],
                        'status': 'passed',
                        'score': rule['max_score'],
                        'description': f'Tender e\'lon qilish muddati: {announcement_period} kun (talab: 15 kun)',
                    }
                else:
                    return {
                        'rule_id': rule['id'],
                        'status': 'failed',
                        'score': 0,
                        'description': f'Tender e\'lon qilish muddati: {announcement_period} kun (talab: 15 kun)',
                        'recommendation': 'Tender boshlanish sanasini kechiktiring yoki e\'lonni ertaroq qiling',
                    }
            else:
                return {
                    'rule_id': rule['id'],
                    'status': 'warning',
                    'score': rule['max_score'] / 2,
                    'description': 'Tender sanalari aniqlanmadi',
                }
        
        except Exception as e:
            return {
                'rule_id': rule['id'],
                'status': 'error',
                'error': str(e),
            }
    
    def _check_document_submission_period(self, tender: Tender, rule: Dict[str, Any]) -> Dict[str, Any]:
        """Hujjatlarni taqdim etish muddatini tekshirish"""
        try:
            if tender.start_date and tender.end_date:
                submission_period = (tender.end_date - tender.start_date).days
                
                if submission_period >= 10:
                    return {
                        'rule_id': rule['id'],
                        'status': 'passed',
                        'score': rule['max_score'],
                        'description': f'Hujjatlar taqdim etish muddati: {submission_period} kun (talab: 10 kun)',
                    }
                else:
                    return {
                        'rule_id': rule['id'],
                        'status': 'failed',
                        'score': 0,
                        'description': f'Hujjatlar taqdim etish muddati: {submission_period} kun (talab: 10 kun)',
                        'recommendation': 'Tender tugash sanasini kechiktiring',
                    }
            else:
                return {
                    'rule_id': rule['id'],
                    'status': 'warning',
                    'score': rule['max_score'] / 2,
                    'description': 'Tender sanalari aniqlanmadi',
                }
        
        except Exception as e:
            return {
                'rule_id': rule['id'],
                'status': 'error',
                'error': str(e),
            }
    
    def _check_tender_conditions_completeness(self, tender: Tender, rule: Dict[str, Any]) -> Dict[str, Any]:
        """Tender shartlarining to\'liqligini tekshirish"""
        try:
            required_sections = [
                'predmet dogovora',  # Shartnoma predmeti
                'stoimost',  # Narx
                'sroki ispolneniya',  # Bajarish muddatlari
                'kachestvo',  # Sifat talablari
                'garantiya',  # Kafolat
                'usloviya oplati',  # To\'lov shartlari
            ]
            
            # Tender tavsifini tekshirish
            description = (tender.description or '').lower()
            requirements_text = ' '.join([
                req.description.lower() for req in tender.requirements.all()
            ])
            
            full_text = description + ' ' + requirements_text
            
            missing_sections = []
            found_sections = []
            
            for section in required_sections:
                if section in full_text:
                    found_sections.append(section)
                else:
                    missing_sections.append(section)
            
            completeness_score = (len(found_sections) / len(required_sections)) * rule['max_score']
            
            if len(missing_sections) == 0:
                return {
                    'rule_id': rule['id'],
                    'status': 'passed',
                    'score': rule['max_score'],
                    'description': f'Barcha majburiy shartlar mavjud ({len(found_sections)}/{len(required_sections)})',
                }
            elif len(missing_sections) <= 2:
                return {
                    'rule_id': rule['id'],
                    'status': 'warning',
                    'score': completeness_score,
                    'description': f'Ayrim shartlar etishmayapti: {", ".join(missing_sections)}',
                    'recommendation': 'Yo\'q bo\'lgan shartlarni qo\'shing',
                }
            else:
                return {
                    'rule_id': rule['id'],
                    'status': 'failed',
                    'score': completeness_score,
                    'description': f'Ko\'plab shartlar etishmayapti: {", ".join(missing_sections)}',
                    'recommendation': 'Barcha majburiy shartlarni qo\'shing',
                }
        
        except Exception as e:
            return {
                'rule_id': rule['id'],
                'status': 'error',
                'error': str(e),
            }
    
    def _check_technical_specification(self, tender: Tender, rule: Dict[str, Any]) -> Dict[str, Any]:
        """Texnik spetsifikatsiyani tekshirish"""
        try:
            tech_requirements = tender.requirements.filter(requirement_type='technical')
            
            if not tech_requirements.exists():
                return {
                    'rule_id': rule['id'],
                    'status': 'failed',
                    'score': 0,
                    'description': 'Texnik talablar topilmadi',
                    'recommendation': 'Texnik spetsifikatsiyani qo\'shing',
                }
            
            # Texnik talablarning sifatini tekshirish
            quality_score = 0
            total_requirements = tech_requirements.count()
            
            for req in tech_requirements:
                # Tavsifning uzunligi
                if len(req.description) > 50:
                    quality_score += 1
                
                # O\'lchov birliklari borligi
                if any(unit in req.description.lower() for unit in ['kg', 'm', 'sm', 'l', 'sht', 'dona']):
                    quality_score += 1
                
                # Standartlar ko'rsatilganligi
                if any(std in req.description.lower() for std in ['gost', 'iso', 'din', 'astm']):
                    quality_score += 1
            
            max_possible_score = total_requirements * 3
            actual_score = (quality_score / max_possible_score) * rule['max_score'] if max_possible_score > 0 else 0
            
            if actual_score >= rule['max_score'] * 0.8:
                status = 'passed'
            elif actual_score >= rule['max_score'] * 0.5:
                status = 'warning'
            else:
                status = 'failed'
            
            return {
                'rule_id': rule['id'],
                'status': status,
                'score': actual_score,
                'description': f'Texnik talablar sifati: {actual_score:.1f}/{rule["max_score"]}',
                'recommendation': 'Texnik talablarga o\'lchov birliklari va standartlarni qo\'shing' if status != 'passed' else '',
            }
        
        except Exception as e:
            return {
                'rule_id': rule['id'],
                'status': 'error',
                'error': str(e),
            }
    
    def _check_evaluation_criteria(self, tender: Tender, rule: Dict[str, Any]) -> Dict[str, Any]:
        """Baholash mezonlarini tekshirish"""
        try:
            requirements = tender.requirements.all()
            
            if not requirements.exists():
                return {
                    'rule_id': rule['id'],
                    'status': 'failed',
                    'score': 0,
                    'description': 'Baholash mezonlari topilmadi',
                    'recommendation': 'Baholash mezonlarini belgilang',
                }
            
            # Baholash mezonlarining to'g'riligini tekshirish
            total_weight = requirements.aggregate(total=Sum('weight'))['total'] or 0
            
            # Vaznlarning yig'indisi 100 ga yaqin bo'lishi kerak
            if abs(total_weight - 100) <= 10:
                weight_score = rule['max_score']
                weight_status = 'passed'
            elif abs(total_weight - 100) <= 20:
                weight_score = rule['max_score'] * 0.7
                weight_status = 'warning'
            else:
                weight_score = rule['max_score'] * 0.3
                weight_status = 'failed'
            
            # Har bir tur uchun mezonlar borligini tekshirish
            requirement_types = set(requirements.values_list('requirement_type', flat=True))
            required_types = {'technical', 'financial', 'experience'}
            
            missing_types = required_types - requirement_types
            type_score = len(requirement_types & required_types) / len(required_types) * (rule['max_score'] * 0.5)
            
            total_score = (weight_score + type_score) / 2
            
            if weight_status == 'passed' and len(missing_types) == 0:
                status = 'passed'
            elif weight_status == 'warning' or len(missing_types) <= 1:
                status = 'warning'
            else:
                status = 'failed'
            
            return {
                'rule_id': rule['id'],
                'status': status,
                'score': total_score,
                'description': f'Baholash mezonlari: vaznlar yig\'indisi {total_weight}, turlar: {", ".join(requirement_types)}',
                'recommendation': f'Vaznlarni 100 ga yaqinlashtiring va yo\'q bo\'lgan turlarni qo\'shing: {", ".join(missing_types)}' if status != 'passed' else '',
            }
        
        except Exception as e:
            return {
                'rule_id': rule['id'],
                'status': 'error',
                'error': str(e),
            }
    
    def _check_contract_terms(self, tender: Tender, rule: Dict[str, Any]) -> Dict[str, Any]:
        """Shartnoma shartlarini tekshirish"""
        try:
            # Shartnoma shartlarini tekshirish
            description = (tender.description or '').lower()
            
            required_terms = [
                'predmet',  # Predmet
                'stoimost',  # Stoimost
                'sroki',  # Sroki
                'kachestvo',  # Kachestvo
                'otvetstvennost',  # Otvetstvennost
                'porjadok oplati',  # Oplata
                'garantiya',  # Garantiya
            ]
            
            found_terms = []
            missing_terms = []
            
            for term in required_terms:
                if term in description:
                    found_terms.append(term)
                else:
                    missing_terms.append(term)
            
            completeness = len(found_terms) / len(required_terms)
            score = completeness * rule['max_score']
            
            if completeness >= 0.9:
                status = 'passed'
            elif completeness >= 0.7:
                status = 'warning'
            else:
                status = 'failed'
            
            return {
                'rule_id': rule['id'],
                'status': status,
                'score': score,
                'description': f'Shartnoma shartlari: {len(found_terms)}/{len(required_terms)} topildi',
                'recommendation': f'Quyidagi shartlarni qo\'shing: {", ".join(missing_terms)}' if status != 'passed' else '',
            }
        
        except Exception as e:
            return {
                'rule_id': rule['id'],
                'status': 'error',
                'error': str(e),
            }
    
    def _check_document_compliance(self, tender: Tender) -> Dict[str, Any]:
        """Hujjatlar compliance"""
        results = {
            'checks': [],
            'violations': [],
        }
        
        try:
            documents = tender.documents.all()
            
            # Majburiy hujjatlar
            required_docs = ['requirements', 'technical']
            found_docs = set(documents.values_list('document_type', flat=True))
            missing_docs = set(required_docs) - found_docs
            
            if missing_docs:
                results['violations'].append({
                    'rule_id': 'doc_001',
                    'rule_name': 'Majburiy hujjatlar',
                    'severity': 'high',
                    'description': f'Majburiy hujjatlar etishmayapti: {", ".join(missing_docs)}',
                    'recommendation': 'Barcha majburiy hujatlarni yuklang',
                })
            
            # Hujjatlarni qayta ishlash holati
            unprocessed_docs = documents.filter(is_processed=False)
            if unprocessed_docs.exists():
                results['violations'].append({
                    'rule_id': 'doc_002',
                    'rule_name': 'Hujjatlar qayta ishlashi',
                    'severity': 'medium',
                    'description': f'{unprocessed_docs.count()} ta hujjat hali qayta ishlanmagan',
                    'recommendation': 'Hujjatlarni qayta ishlashni boshlang',
                })
        
        except Exception as e:
            logger.error(f'Hujjatlar compliance tekshiruvida xatolik: {str(e)}')
        
        return results
    
    def _check_time_compliance(self, tender: Tender) -> Dict[str, Any]:
        """Vaqt talablarini tekshirish"""
        results = {
            'checks': [],
            'violations': [],
        }
        
        try:
            now = timezone.now()
            
            # Tender muddati o'tmaganligi
            if tender.end_date and tender.end_date < now:
                results['violations'].append({
                    'rule_id': 'time_001',
                    'rule_name': 'Tender muddati',
                    'severity': 'critical',
                    'description': 'Tender muddati o\'tgan',
                    'recommendation': 'Tender muddatini uzaytiring',
                })
            
            # Tender boshlanishiga vaqt borligi
            if tender.start_date and tender.start_date > now:
                days_to_start = (tender.start_date - now).days
                if days_to_start < 7:
                    results['violations'].append({
                        'rule_id': 'time_002',
                        'rule_name': 'Tender boshlanish vaqti',
                        'severity': 'medium',
                        'description': f'Tender {days_to_start} kundan keyin boshlanadi',
                        'recommendation': 'Tayyorgarlikni tezlashtiring',
                    })
        
        except Exception as e:
            logger.error(f'Vaqt compliance tekshiruvida xatolik: {str(e)}')
        
        return results
    
    def _check_financial_compliance(self, tender: Tender) -> Dict[str, Any]:
        """Moliyaviy compliance"""
        results = {
            'checks': [],
            'violations': [],
        }
        
        try:
            # Byudjet chegaralari
            if tender.estimated_budget:
                # Bu yerda tashkilotning byudjet chegaralarini tekshirish kerak
                # Hozircha shartli tekshirish
                if tender.estimated_budget > 1000000000:  # 1 milliard so'mdan yuqori
                    results['violations'].append({
                        'rule_id': 'fin_001',
                        'rule_name': 'Byudjet chegarasi',
                        'severity': 'high',
                        'description': 'Tender summasi yuqori byudjet chegarasidan oshmoqda',
                        'recommendation': 'Tender summasini qayta ko\'rib chiqing',
                    })
        
        except Exception as e:
            logger.error(f'Moliyaviy compliance tekshiruvida xatolik: {str(e)}')
        
        return results
    
    def _check_participant_documents(self, participant: TenderParticipant) -> Dict[str, Any]:
        """Ishtirokchi hujjatlarini tekshirish"""
        results = {
            'checks': [],
            'violations': [],
        }
        
        try:
            documents = participant.documents.all()
            
            # Majburiy hujjatlar
            required_docs = ['proposal', 'financial', 'technical']
            found_docs = set(documents.values_list('document_type', flat=True))
            missing_docs = set(required_docs) - found_docs
            
            if missing_docs:
                results['violations'].append({
                    'rule_id': 'part_doc_001',
                    'rule_name': 'Ishtirokchi majburiy hujjatlari',
                    'severity': 'critical',
                    'description': f'Majburiy hujjatlar etishmayapti: {", ".join(missing_docs)}',
                    'recommendation': 'Barcha majburiy hujjalarni yuklang',
                })
            
            # Hujjatlarni qayta ishlash holati
            unprocessed_docs = documents.filter(is_processed=False)
            if unprocessed_docs.exists():
                results['violations'].append({
                    'rule_id': 'part_doc_002',
                    'rule_name': 'Hujjatlar qayta ishlashi',
                    'severity': 'medium',
                    'description': f'{unprocessed_docs.count()} ta hujjat hali qayta ishlanmagan',
                    'recommendation': 'Hujjatlarni qayta ishlashni kutib turing',
                })
        
        except Exception as e:
            logger.error(f'Ishtirokchi hujjatlari tekshiruvida xatolik: {str(e)}')
        
        return results
    
    def _check_qualification_compliance(self, participant: TenderParticipant) -> Dict[str, Any]:
        """Malaka talablarini tekshirish"""
        results = {
            'checks': [],
            'violations': [],
        }
        
        try:
            # Tajriba talablari
            tender = participant.tender
            experience_requirements = tender.requirements.filter(requirement_type='experience')
            
            for req in experience_requirements:
                if req.is_mandatory:
                    # Bu yerda ishtirokchining tajribasini tekshirish kerak
                    # Hozircha shartli tekshirish
                    if not participant.participant.trust_score or participant.participant.trust_score < 30:
                        results['violations'].append({
                            'rule_id': 'qual_001',
                            'rule_name': 'Tajriba talabi',
                            'severity': 'high',
                            'description': f'Tajriba talabiga javob bermaydi: {req.title}',
                            'recommendation': 'Tajriba hujjatlarini taqdim eting',
                        })
        
        except Exception as e:
            logger.error(f'Malaka compliance tekshiruvida xatolik: {str(e)}')
        
        return results
    
    def _check_participant_financial_compliance(self, participant: TenderParticipant) -> Dict[str, Any]:
        """Ishtirokchi moliyaviy talablarini tekshirish"""
        results = {
            'checks': [],
            'violations': [],
        }
        
        try:
            # Narx taklifi
            if not participant.proposed_price:
                results['violations'].append({
                    'rule_id': 'part_fin_001',
                    'rule_name': 'Narx taklifi',
                    'severity': 'critical',
                    'description': 'Narx taklifi kiritilmagan',
                    'recommendation': 'Narx taklifini kiriting',
                })
            
            # Kafolat miqdori
            tender = participant.tender
            if tender.estimated_budget and participant.proposed_price:
                guarantee_amount = tender.estimated_budget * Decimal('0.03')  # 3%
                # Bu yerda kafolat miqdorini tekshirish kerak
                # Hozircha shartli tekshirish
        
        except Exception as e:
            logger.error(f'Ishtirokchi moliyaviy compliance tekshiruvida xatolik: {str(e)}')
        
        return results
    
    def _check_technical_compliance(self, participant: TenderParticipant) -> Dict[str, Any]:
        """Texnik compliance"""
        results = {
            'checks': [],
            'violations': [],
        }
        
        try:
            # Texnik hujjat mavjudligi
            tech_docs = participant.documents.filter(document_type='technical')
            if not tech_docs.exists():
                results['violations'].append({
                    'rule_id': 'part_tech_001',
                    'rule_name': 'Texnik hujjat',
                    'severity': 'critical',
                    'description': 'Texnik hujjat topilmadi',
                    'recommendation': 'Texnik hujjatni yuklang',
                })
        
        except Exception as e:
            logger.error(f'Texnik compliance tekshiruvida xatolik: {str(e)}')
        
        return results
    
    def _calculate_compliance_score(self, checks: List[Dict[str, Any]]) -> float:
        """Compliance ballini hisoblash"""
        try:
            total_score = 0
            max_score = 0
            
            for check in checks:
                if 'score' in check:
                    total_score += check['score']
                    # Max score ni aniqlash
                    if 'max_score' in check:
                        max_score += check['max_score']
                    else:
                        max_score += 10  # Default max score
            
            if max_score > 0:
                return round((total_score / max_score) * 100, 2)
            else:
                return 0.0
        
        except Exception as e:
            logger.error(f'Compliance ballini hisoblashda xatolik: {str(e)}')
            return 0.0


# Global xizmat
compliance_checker = ComplianceChecker()
