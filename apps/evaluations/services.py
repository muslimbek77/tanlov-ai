import logging
import json
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from decimal import Decimal
from django.utils import timezone
from django.db.models import Q, Count, Avg, Sum, F
from django.db.models.functions import Rank
from .models import Evaluation, ParticipantScore, ScoreDetail, EvaluationLog
from apps.tenders.models import Tender, TenderRequirement
from apps.participants.models import TenderParticipant
from apps.compliance.services import compliance_checker
from apps.anti_fraud.services import anti_fraud_analyzer

logger = logging.getLogger(__name__)


class ScoringEngine:
    """100 ballik baholash tizimi"""
    
    def __init__(self):
        self.scoring_weights = {
            'compliance': 0.25,      # 25 ball
            'financial': 0.20,       # 20 ball
            'technical': 0.30,       # 30 ball
            'experience': 0.15,       # 15 ball
            'price': 0.10,           # 10 ball
        }
        
        self.risk_penalties = {
            'low': 0.0,
            'medium': -5.0,
            'high': -15.0,
            'critical': -30.0,
        }
    
    def evaluate_tender_participants(self, tender: Tender, evaluator_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Tender ishtirokchilarini baholash
        """
        try:
            logger.info(f"Tender baholash boshlandi: {tender.id}")
            
            # Baholash yaratish
            evaluation = Evaluation.objects.create(
                tender=tender,
                evaluator_id=evaluator_id,
                status='in_progress',
                started_at=timezone.now(),
                total_participants=tender.participants.count()
            )
            
            participants = tender.participants.all()
            results = {
                'evaluation_id': evaluation.id,
                'tender_id': tender.id,
                'participants_scores': [],
                'summary': {
                    'total_participants': len(participants),
                    'qualified_count': 0,
                    'disqualified_count': 0,
                    'average_score': 0.0,
                    'winner_id': None,
                },
                'ranking': [],
            }
            
            participant_scores = []
            
            # Har bir ishtirokchi uchun ballarni hisoblash
            for participant in participants:
                score_result = self._calculate_participant_score(participant, evaluation)
                participant_scores.append(score_result)
                
                # Log qilish
                EvaluationLog.objects.create(
                    evaluation=evaluation,
                    log_type='info',
                    message=f"Ishtirokchi baholandi: {participant.participant.company_name}",
                    details={'participant_id': participant.id, 'total_score': score_result['total_score']},
                    agent_name='ScoringEngine',
                    agent_type='scoring'
                )
            
            # Reytinqni aniqlash
            ranked_scores = sorted(participant_scores, key=lambda x: x['total_score'], reverse=True)
            
            for rank, score_data in enumerate(ranked_scores, 1):
                score_data['rank'] = rank
                
                # G'olibni aniqlash (faqat saralanganlar orasida)
                if score_data['is_qualified'] and not results['summary']['winner_id']:
                    results['summary']['winner_id'] = score_data['participant_id']
                    score_data['is_winner'] = True
                else:
                    score_data['is_winner'] = False
            
            # Umumiy statistika
            qualified_scores = [s['total_score'] for s in participant_scores if s['is_qualified']]
            
            results['summary']['qualified_count'] = len(qualified_scores)
            results['summary']['disqualified_count'] = len(participant_scores) - len(qualified_scores)
            results['summary']['average_score'] = sum(qualified_scores) / len(qualified_scores) if qualified_scores else 0.0
            results['participants_scores'] = participant_scores
            results['ranking'] = ranked_scores
            
            # Baholashni yakunlash
            evaluation.status = 'completed'
            evaluation.completed_at = timezone.now()
            evaluation.qualified_participants = results['summary']['qualified_count']
            evaluation.disqualified_participants = results['summary']['disqualified_count']
            evaluation.save()
            
            logger.info(f"Tender baholash yakunlandi: {evaluation.id}")
            return results
            
        except Exception as e:
            logger.error(f"Tender baholashda xatolik: {str(e)}")
            if 'evaluation' in locals():
                evaluation.status = 'failed'
                evaluation.save()
            
            return {
                'tender_id': tender.id,
                'status': 'error',
                'error': str(e),
            }
    
    def _calculate_participant_score(self, participant: TenderParticipant, evaluation: Evaluation) -> Dict[str, Any]:
        """
        Ishtirokchi ballini hisoblash
        """
        try:
            logger.info(f"Ishtirokchi balli hisoblanmoqda: {participant.id}")
            
            # Boshlang'ich ballar
            scores = {
                'compliance': 0.0,
                'financial': 0.0,
                'technical': 0.0,
                'experience': 0.0,
                'price': 0.0,
            }
            
            # Compliance balli
            compliance_result = compliance_checker.check_participant_compliance(participant)
            scores['compliance'] = compliance_result.get('compliance_score', 0.0)
            
            # Moliyaviy ball
            financial_result = self._calculate_financial_score(participant)
            scores['financial'] = financial_result['score']
            
            # Texnik ball
            technical_result = self._calculate_technical_score(participant)
            scores['technical'] = technical_result['score']
            
            # Tajriba balli
            experience_result = self._calculate_experience_score(participant)
            scores['experience'] = experience_result['score']
            
            # Narx balli
            price_result = self._calculate_price_score(participant)
            scores['price'] = price_result['score']
            
            # Vaznli jami ball
            total_score = 0.0
            for category, score in scores.items():
                weight = self.scoring_weights[category]
                total_score += score * weight
            
            # Xavf jarimalari
            fraud_analysis = anti_fraud_analyzer.analyze_tender_fraud_risks(participant.tender)
            participant_risk = fraud_analysis.get('participants_risk', {}).get(participant.id, {})
            risk_level = participant_risk.get('risk_level', 'low')
            risk_penalty = self.risk_penalties.get(risk_level, 0.0)
            
            total_score += risk_penalty
            total_score = max(0.0, min(100.0, total_score))  # 0-100 oralig'ida
            
            # Saralash holati
            is_qualified = total_score >= 60 and risk_level != 'critical'
            
            # ParticipantScore yaratish
            participant_score = ParticipantScore.objects.create(
                evaluation=evaluation,
                tender_participant=participant,
                total_score=Decimal(str(total_score)),
                compliance_score=Decimal(str(scores['compliance'])),
                financial_score=Decimal(str(scores['financial'])),
                technical_score=Decimal(str(scores['technical'])),
                experience_score=Decimal(str(scores['experience'])),
                risk_level=risk_level,
                risk_score=Decimal(str(abs(risk_penalty))),
                red_flags=participant_risk.get('detection_types', []),
                score_reasoning=self._generate_score_reasoning(scores, risk_penalty, is_qualified),
                risk_reasoning=self._generate_risk_reasoning(participant_risk),
                is_winner=False
            )
            
            # Tafsilot yozuvlarini yaratish
            self._create_score_details(participant_score, scores, {
                'compliance': compliance_result,
                'financial': financial_result,
                'technical': technical_result,
                'experience': experience_result,
                'price': price_result,
            })
            
            result = {
                'participant_id': participant.id,
                'company_name': participant.participant.company_name,
                'total_score': round(total_score, 2),
                'scores': {k: round(v, 2) for k, v in scores.items()},
                'risk_level': risk_level,
                'risk_penalty': risk_penalty,
                'is_qualified': is_qualified,
                'rank': None,  # Keyinroq to'ldiriladi
                'is_winner': False,  # Keyinroq to'ldiriladi
                'score_details': {
                    'compliance_breakdown': compliance_result.get('checks', []),
                    'financial_breakdown': financial_result.get('breakdown', {}),
                    'technical_breakdown': technical_result.get('breakdown', {}),
                    'experience_breakdown': experience_result.get('breakdown', {}),
                    'price_breakdown': price_result.get('breakdown', {}),
                }
            }
            
            logger.info(f"Ishtirokchi balli hisoblandi: {participant.id} - {total_score}")
            return result
            
        except Exception as e:
            logger.error(f"Ishtirokchi ballini hisoblashda xatolik: {str(e)}")
            return {
                'participant_id': participant.id,
                'total_score': 0.0,
                'error': str(e),
            }
    
    def _calculate_financial_score(self, participant: TenderParticipant) -> Dict[str, Any]:
        """Moliyaviy ballni hisoblash"""
        try:
            score = 0.0
            breakdown = {}
            
            # Narx taklifi mavjudligi
            if not participant.proposed_price:
                return {
                    'score': 0.0,
                    'breakdown': {'error': 'Narx taklifi mavjud emas'}
                }
            
            tender = participant.tender
            
            # 1. Narxning raqobatbardoshligi (40%)
            if tender.estimated_budget:
                price_ratio = float(participant.proposed_price) / float(tender.estimated_budget)
                
                if price_ratio <= 0.8:
                    price_score = 40.0
                elif price_ratio <= 0.9:
                    price_score = 35.0
                elif price_ratio <= 1.0:
                    price_score = 30.0
                elif price_ratio <= 1.1:
                    price_score = 20.0
                else:
                    price_score = 10.0
                
                score += price_score
                breakdown['price_competitiveness'] = {
                    'score': price_score,
                    'price_ratio': price_ratio,
                    'proposed_price': float(participant.proposed_price),
                    'estimated_budget': float(tender.estimated_budget)
                }
            
            # 2. To'lov shartlari (20%)
            # Bu yerda to'lov grafikini tekshirish kerak
            payment_score = 20.0  # Default
            breakdown['payment_terms'] = {
                'score': payment_score,
                'note': 'To\'lov shartlari standart'
            }
            score += payment_score
            
            # 3. Kafolat miqdori (20%)
            if tender.estimated_budget:
                expected_guarantee = float(tender.estimated_budget) * 0.03  # 3%
                # Bu yerda haqiqiy kafolat miqdorini tekshirish kerak
                guarantee_score = 20.0  # Default
                breakdown['guarantee_amount'] = {
                    'score': guarantee_score,
                    'expected': expected_guarantee,
                    'note': 'Kafolat miqdori qabul qilindi'
                }
                score += guarantee_score
            
            # 4. Moliyaviy barqarorlik (20%)
            trust_score = float(participant.participant.trust_score or 50)
            financial_stability_score = (trust_score / 100) * 20
            breakdown['financial_stability'] = {
                'score': financial_stability_score,
                'trust_score': trust_score
            }
            score += financial_stability_score
            
            return {
                'score': score,
                'breakdown': breakdown
            }
            
        except Exception as e:
            logger.error(f"Moliyaviy ballni hisoblashda xatolik: {str(e)}")
            return {
                'score': 0.0,
                'breakdown': {'error': str(e)}
            }
    
    def _calculate_technical_score(self, participant: TenderParticipant) -> Dict[str, Any]:
        """Texnik ballni hisoblash"""
        try:
            score = 0.0
            breakdown = {}
            
            tender = participant.tender
            technical_requirements = tender.requirements.filter(requirement_type='technical')
            
            if not technical_requirements.exists():
                return {
                    'score': 50.0,  # Default
                    'breakdown': {'note': 'Texnik talablar mavjud emas'}
                }
            
            # 1. Texnik talablarga muvofiqlik (60%)
            requirement_scores = []
            total_weight = technical_requirements.aggregate(total=Sum('weight'))['total'] or 0
            
            for req in technical_requirements:
                # Bu yerda talabning qanoatlantirilish darajasini tekshirish kerak
                # Hozircha ishtirokchining ishonch reytingiga asoslanamiz
                trust_score = float(participant.participant.trust_score or 50)
                
                if req.is_mandatory:
                    req_score = (trust_score / 100) * req.max_score
                else:
                    req_score = min((trust_score / 100) * req.max_score, req.max_score)
                
                requirement_scores.append({
                    'requirement_id': req.id,
                    'requirement_title': req.title,
                    'score': req_score,
                    'max_score': float(req.max_score),
                    'weight': float(req.weight),
                    'mandatory': req.is_mandatory
                })
            
            # Vaznli o'rtacha
            if total_weight > 0:
                weighted_score = sum(r['score'] * r['weight'] for r in requirement_scores) / total_weight
                technical_compliance_score = min(weighted_score, 60.0)
            else:
                technical_compliance_score = 30.0
            
            score += technical_compliance_score
            breakdown['technical_compliance'] = {
                'score': technical_compliance_score,
                'requirement_scores': requirement_scores,
                'total_weight': total_weight
            }
            
            # 2. Hujjatlar sifati (20%)
            tech_docs = participant.documents.filter(document_type='technical')
            if tech_docs.exists():
                doc_quality_score = 20.0
                breakdown['document_quality'] = {
                    'score': doc_quality_score,
                    'document_count': tech_docs.count(),
                    'processed_count': tech_docs.filter(is_processed=True).count()
                }
            else:
                doc_quality_score = 0.0
                breakdown['document_quality'] = {
                    'score': doc_quality_score,
                    'note': 'Texnik hujjatlar topilmadi'
                }
            
            score += doc_quality_score
            
            # 3. Yetkazib berish muddati (20%)
            if participant.delivery_time:
                # Qisqaroq muddat yuqori ball
                if participant.delivery_time <= 30:
                    delivery_score = 20.0
                elif participant.delivery_time <= 60:
                    delivery_score = 15.0
                elif participant.delivery_time <= 90:
                    delivery_score = 10.0
                else:
                    delivery_score = 5.0
                
                breakdown['delivery_time'] = {
                    'score': delivery_score,
                    'days': participant.delivery_time
                }
            else:
                delivery_score = 0.0
                breakdown['delivery_time'] = {
                    'score': delivery_score,
                    'note': 'Yetkazib berish muddati ko\'rsatilmagan'
                }
            
            score += delivery_score
            
            return {
                'score': score,
                'breakdown': breakdown
            }
            
        except Exception as e:
            logger.error(f"Texnik ballni hisoblashda xatolik: {str(e)}")
            return {
                'score': 0.0,
                'breakdown': {'error': str(e)}
            }
    
    def _calculate_experience_score(self, participant: TenderParticipant) -> Dict[str, Any]:
        """Tajriba ballini hisoblash"""
        try:
            score = 0.0
            breakdown = {}
            
            # 1. Kompaniya ishonch reytingi (40%)
            trust_score = float(participant.participant.trust_score or 50)
            reputation_score = (trust_score / 100) * 40
            breakdown['reputation'] = {
                'score': reputation_score,
                'trust_score': trust_score
            }
            score += reputation_score
            
            # 2. Shu turdagi loyihalardagi tajriba (30%)
            # Bu yerda kompaniyaning o'tgan loyihalarini tekshirish kerak
            # Hozircha taxminiy
            experience_score = 25.0  # Default
            breakdown['relevant_experience'] = {
                'score': experience_score,
                'note': 'Tajriba ma\'lumotlari to\'ldirilmagan'
            }
            score += experience_score
            
            # 3. Kafolat muddati (20%)
            if participant.warranty_period:
                if participant.warranty_period >= 24:
                    warranty_score = 20.0
                elif participant.warranty_period >= 12:
                    warranty_score = 15.0
                elif participant.warranty_period >= 6:
                    warranty_score = 10.0
                else:
                    warranty_score = 5.0
                
                breakdown['warranty_period'] = {
                    'score': warranty_score,
                    'months': participant.warranty_period
                }
            else:
                warranty_score = 0.0
                breakdown['warranty_period'] = {
                    'score': warranty_score,
                    'note': 'Kafolat muddati ko\'rsatilmagan'
                }
            
            score += warranty_score
            
            # 4. Sertifikatlar va litsenziyalar (10%)
            # Bu yerda sertifikatlarni tekshirish kerak
            certification_score = 10.0  # Default
            breakdown['certifications'] = {
                'score': certification_score,
                'note': 'Sertifikatlar tekshirilmagan'
            }
            score += certification_score
            
            return {
                'score': score,
                'breakdown': breakdown
            }
            
        except Exception as e:
            logger.error(f"Tajriba ballini hisoblashda xatolik: {str(e)}")
            return {
                'score': 0.0,
                'breakdown': {'error': str(e)}
            }
    
    def _calculate_price_score(self, participant: TenderParticipant) -> Dict[str, Any]:
        """Narx ballini hisoblash"""
        try:
            score = 0.0
            breakdown = {}
            
            if not participant.proposed_price:
                return {
                    'score': 0.0,
                    'breakdown': {'error': 'Narx taklifi mavjud emas'}
                }
            
            tender = participant.tender
            
            # 1. Narxning optimalligi (70%)
            if tender.estimated_budget:
                price_ratio = float(participant.proposed_price) / float(tender.estimated_budget)
                
                # Eng yaxshi narx - byudjetning 80-90%
                if 0.8 <= price_ratio <= 0.9:
                    price_score = 70.0
                elif 0.7 <= price_ratio < 0.8:
                    price_score = 60.0
                elif 0.9 < price_ratio <= 1.0:
                    price_score = 50.0
                elif price_ratio < 0.7:
                    price_score = 40.0  # Juda past narx - shubhali
                elif 1.0 < price_ratio <= 1.1:
                    price_score = 30.0
                else:
                    price_score = 10.0
                
                breakdown['price_optimality'] = {
                    'score': price_score,
                    'price_ratio': price_ratio,
                    'proposed_price': float(participant.proposed_price),
                    'estimated_budget': float(tender.estimated_budget)
                }
            else:
                price_score = 35.0  # Default
                breakdown['price_optimality'] = {
                    'score': price_score,
                    'note': 'Byudjet ma\'lumoti mavjud emas'
                }
            
            score += price_score
            
            # 2. Narxning shaffofligi (30%)
            # Bu yerda narx tarkibining tafsilotlarini tekshirish kerak
            transparency_score = 25.0  # Default
            breakdown['price_transparency'] = {
                'score': transparency_score,
                'note': 'Narx tafsilotlari tekshirilmagan'
            }
            score += transparency_score
            
            return {
                'score': score,
                'breakdown': breakdown
            }
            
        except Exception as e:
            logger.error(f"Narx ballini hisoblashda xatolik: {str(e)}")
            return {
                'score': 0.0,
                'breakdown': {'error': str(e)}
            }
    
    def _generate_score_reasoning(self, scores: Dict[str, float], risk_penalty: float, is_qualified: bool) -> str:
        """Ball berish sabablarini generatsiya qilish"""
        reasoning_parts = []
        
        # Eng yuqori va eng past ballar
        max_category = max(scores, key=scores.get)
        min_category = min(scores, key=scores.get)
        
        reasoning_parts.append(f"Eng yuqori ball: {max_category} ({scores[max_category]:.1f})")
        reasoning_parts.append(f"Eng past ball: {min_category} ({scores[min_category]:.1f})")
        
        # Kategoriyalar bo'yicha izohlar
        if scores['compliance'] >= 80:
            reasoning_parts.append("Compliance talablariga to'liq javob beradi")
        elif scores['compliance'] >= 60:
            reasoning_parts.append("Compliance talablariga qisman javob beradi")
        else:
            reasoning_parts.append("Compliance talablarida kamchiliklar bor")
        
        if scores['financial'] >= 80:
            reasoning_parts.append("Moliyaviy taklif juda qulay")
        elif scores['financial'] >= 60:
            reasoning_parts.append("Moliyaviy taklif qabul qilinadi")
        else:
            reasoning_parts.append("Moliyaviy taklifda muammolar bor")
        
        if scores['technical'] >= 80:
            reasoning_parts.append("Texnik ko'nikmalari yuqori")
        elif scores['technical'] >= 60:
            reasoning_parts.append("Texnik ko'nikmalari qoniqarli")
        else:
            reasoning_parts.append("Texnik ko'nikmalari yetarli emas")
        
        # Xavf jarimasi
        if risk_penalty < 0:
            reasoning_parts.append(f"Xavf sababli {abs(risk_penalty):.1f} ball ayirildi")
        
        # Saralash holati
        if is_qualified:
            reasoning_parts.append("Saralashdan o'tdi")
        else:
            reasoning_parts.append("Saralashdan o'tmadi")
        
        return ". ".join(reasoning_parts) + "."
    
    def _generate_risk_reasoning(self, participant_risk: Dict[str, Any]) -> str:
        """Xavf sabablarini generatsiya qilish"""
        if not participant_risk:
            return "Xavf omillari aniqlanmadi"
        
        reasoning_parts = []
        risk_level = participant_risk.get('risk_level', 'low')
        detection_types = participant_risk.get('detection_types', [])
        
        reasoning_parts.append(f"Xavf darajasi: {risk_level}")
        
        if detection_types:
            reasoning_parts.append(f"Aniqlangan xavf turlari: {', '.join(detection_types)}")
        
        if risk_level == 'critical':
            reasoning_parts.append("Tanqidiy xavf - qo'shimcha tekshirish talab qilinadi")
        elif risk_level == 'high':
            reasoning_parts.append("Yuqori xavf - ehtiyot chorasi ko'rish kerak")
        elif risk_level == 'medium':
            reasoning_parts.append("O'rta xavf - diqqat bilan kuzatish lozim")
        
        return ". ".join(reasoning_parts) + "."
    
    def _create_score_details(self, participant_score: ParticipantScore, scores: Dict[str, float], breakdowns: Dict[str, Any]):
        """Ball tafsilotlarini yaratish"""
        try:
            # Compliance tafsilotlari
            ScoreDetail.objects.create(
                participant_score=participant_score,
                score_type='compliance',
                max_score=25.0,
                achieved_score=Decimal(str(scores['compliance'])),
                percentage=Decimal(str(scores['compliance'])),
                analysis=breakdowns['compliance'].get('compliance_score', 0),
                reasoning=f"Compliance tekshiruvi natijasi: {scores['compliance']:.1f} ball"
            )
            
            # Moliyaviy tafsilotlar
            ScoreDetail.objects.create(
                participant_score=participant_score,
                score_type='financial',
                max_score=20.0,
                achieved_score=Decimal(str(scores['financial'])),
                percentage=Decimal(str(scores['financial'])),
                analysis=json.dumps(breakdowns['financial'].get('breakdown', {})),
                reasoning=f"Moliyaviy baholash natijasi: {scores['financial']:.1f} ball"
            )
            
            # Texnik tafsilotlar
            ScoreDetail.objects.create(
                participant_score=participant_score,
                score_type='technical',
                max_score=30.0,
                achieved_score=Decimal(str(scores['technical'])),
                percentage=Decimal(str(scores['technical'])),
                analysis=json.dumps(breakdowns['technical'].get('breakdown', {})),
                reasoning=f"Texnik baholash natijasi: {scores['technical']:.1f} ball"
            )
            
            # Tajriba tafsilotlari
            ScoreDetail.objects.create(
                participant_score=participant_score,
                score_type='experience',
                max_score=15.0,
                achieved_score=Decimal(str(scores['experience'])),
                percentage=Decimal(str(scores['experience'])),
                analysis=json.dumps(breakdowns['experience'].get('breakdown', {})),
                reasoning=f"Tajriba baholash natijasi: {scores['experience']:.1f} ball"
            )
            
            # Narx tafsilotlari
            ScoreDetail.objects.create(
                participant_score=participant_score,
                score_type='price',
                max_score=10.0,
                achieved_score=Decimal(str(scores['price'])),
                percentage=Decimal(str(scores['price'])),
                analysis=json.dumps(breakdowns['price'].get('breakdown', {})),
                reasoning=f"Narx baholash natijasi: {scores['price']:.1f} ball"
            )
            
        except Exception as e:
            logger.error(f"Ball tafsilotlarini yaratishda xatolik: {str(e)}")
    
    def get_evaluation_results(self, evaluation_id: int) -> Dict[str, Any]:
        """Baholash natijalarini olish"""
        try:
            evaluation = Evaluation.objects.get(id=evaluation_id)
            
            participant_scores = evaluation.participant_scores.all().order_by('-total_score')
            
            results = {
                'evaluation': {
                    'id': evaluation.id,
                    'tender_id': evaluation.tender.id,
                    'tender_title': evaluation.tender.title,
                    'status': evaluation.status,
                    'started_at': evaluation.started_at.isoformat() if evaluation.started_at else None,
                    'completed_at': evaluation.completed_at.isoformat() if evaluation.completed_at else None,
                    'total_participants': evaluation.total_participants,
                    'qualified_participants': evaluation.qualified_participants,
                    'disqualified_participants': evaluation.disqualified_participants,
                },
                'participants': [],
                'summary': {
                    'average_score': 0.0,
                    'highest_score': 0.0,
                    'lowest_score': 100.0,
                    'winner': None,
                }
            }
            
            scores = []
            for score in participant_scores:
                participant_data = {
                    'participant_id': score.tender_participant.id,
                    'company_name': score.tender_participant.participant.company_name,
                    'total_score': float(score.total_score),
                    'rank': score.rank,
                    'is_winner': score.is_winner,
                    'is_qualified': score.total_score >= 60 and score.risk_level != 'critical',
                    'scores': {
                        'compliance': float(score.compliance_score),
                        'financial': float(score.financial_score),
                        'technical': float(score.technical_score),
                        'experience': float(score.experience_score),
                    },
                    'risk_level': score.risk_level,
                    'risk_score': float(score.risk_score),
                    'red_flags': score.red_flags,
                    'reasoning': score.score_reasoning,
                }
                
                results['participants'].append(participant_data)
                scores.append(float(score.total_score))
            
            if scores:
                results['summary']['average_score'] = sum(scores) / len(scores)
                results['summary']['highest_score'] = max(scores)
                results['summary']['lowest_score'] = min(scores)
            
            # G'olibni topish
            winner = participant_scores.filter(is_winner=True).first()
            if winner:
                results['summary']['winner'] = {
                    'participant_id': winner.tender_participant.id,
                    'company_name': winner.tender_participant.participant.company_name,
                    'total_score': float(winner.total_score),
                }
            
            return results
            
        except Evaluation.DoesNotExist:
            return {
                'error': 'Baholash topilmadi',
                'evaluation_id': evaluation_id,
            }
        except Exception as e:
            logger.error(f"Baholash natijalarini olishda xatolik: {str(e)}")
            return {
                'error': str(e),
                'evaluation_id': evaluation_id,
            }


# Global xizmat
scoring_engine = ScoringEngine()
