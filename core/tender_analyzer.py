"""
Tender va Ishtirokchilar Tahlil Xizmati

Bu modul tender shartnomasini tahlil qiladi va ishtirokchilarni 
tender talablariga mosligini baholaydi.
"""

import logging
import json
import re
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from decimal import Decimal
from .llm_engine import llm_engine

logger = logging.getLogger(__name__)


def _normalize_language(raw_language: Optional[str]) -> str:
    lang = (raw_language or 'uz_latn').strip().lower()
    if lang in ['uz', 'uz-latn', 'uz_uz']:
        return 'uz_latn'
    if lang in ['uz-cyrl', 'uz_cyrl', 'uz-cyrl-uz']:
        return 'uz_cyrl'
    if lang in ['ru', 'ru-ru', 'rus']:
        return 'ru'
    return lang


def _is_uzbek(lang: str) -> bool:
    return _normalize_language(lang).startswith('uz')


@dataclass
class TenderRequirement:
    """Tender talabi"""
    id: str
    category: str  # technical, financial, legal, experience, document
    title: str
    description: str
    is_mandatory: bool
    weight: float  # 0-1 orasida vazn
    evaluation_criteria: str = ''  # Baholash mezonlari
    

@dataclass
class ParticipantScore:
    """Ishtirokchi bahosi"""
    requirement_id: str
    score: float  # 0-100
    matches: bool
    reason: str
    details: str


@dataclass
class ParticipantAnalysis:
    """Ishtirokchi tahlili natijasi"""
    participant_name: str
    total_score: float
    match_percentage: float
    scores: List[ParticipantScore]
    strengths: List[str]
    weaknesses: List[str]
    price_analysis: Dict[str, Any]
    recommendation: str
    risk_level: str  # low, medium, high
    rank: int = 0


class TenderAnalyzer:
    """Tender tahlil xizmati"""
    
    def __init__(self):
        self.tender_requirements: List[TenderRequirement] = []
        self.tender_info: Dict[str, Any] = {}
    
    def restore_tender_analysis(self, tender_data: Dict[str, Any]) -> bool:
        """
        Frontend'dan kelgan tender tahlilini tiklash
        
        Args:
            tender_data: Frontend'dan kelgan tender tahlili
            
        Returns:
            Muvaffaqiyatli tiklanganmi
        """
        try:
            logger.info("Tender tahlilini tiklash boshlandi")
            
            # Tender info
            self.tender_info = {
                'tender_purpose': tender_data.get('tender_purpose', tender_data.get('purpose', '')),
                'tender_type': tender_data.get('tender_type', tender_data.get('type', '')),
            }
            
            # Talablarni tiklash
            requirements = tender_data.get('requirements', [])
            self.tender_requirements = []
            
            for i, req in enumerate(requirements):
                if isinstance(req, dict):
                    self.tender_requirements.append(TenderRequirement(
                        id=req.get('id', f'REQ_{i+1}'),
                        title=req.get('title', req.get('description', '')),
                        description=req.get('description', req.get('title', '')),
                        category=req.get('category', 'general'),
                        is_mandatory=req.get('is_mandatory', req.get('mandatory', True)),
                        weight=req.get('weight', 10),
                        evaluation_criteria=req.get('evaluation_criteria', req.get('criteria', ''))
                    ))
            
            logger.info(f"Tender tahlili tiklandi: {len(self.tender_requirements)} talab")
            return True
            
        except Exception as e:
            logger.error(f"Tender tahlilini tiklashda xatolik: {e}")
            return False
    
    def analyze_tender_document(self, tender_text: str, tender_metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Tender shartnomasini tahlil qilish
        
        Args:
            tender_text: Tender shartnoma matni
            tender_metadata: Qo'shimcha ma'lumotlar (raqam, sana, byudjet)
        
        Returns:
            Tender tahlili natijalari
        """
        try:
            logger.info("Tender shartnomasini tahlil qilish boshlandi")

            lang = _normalize_language((tender_metadata or {}).get('language'))
            if lang == 'ru':
                lang_instruction = 'Ответь на русском языке. '
                system_prompt = 'Ты эксперт по государственным закупкам. Анализируй тендерные документы глубоко и всесторонне. Возвращай только JSON.'
            elif lang == 'uz_cyrl':
                lang_instruction = 'Жавобни ўзбек тилида (кирилл) бер. '
                system_prompt = "Сен Ўзбекистон давлат харидлари бўйича юқори малакали экспертсан. Тендер ҳужжатларини ҳар тарафлама чуқур таҳлил қиласан. Фақат JSON форматда жавоб бер."
            else:
                lang_instruction = "Javobni o'zbek tilida (lotin) ber. "
                system_prompt = "Sen O'zbekiston davlat xaridlari bo'yicha yuqori malakali ekspertsan. Tender hujjatlarini har taraflama chuqur tahlil qilasan. Faqat JSON formatida javob ber."
            
            # LLM orqali tender tahlili
            analysis_prompt = f"""
{lang_instruction}
Sen tender tahlili bo'yicha yuqori malakali ekspertsan. 
Quyidagi tender shartnomasini HAR TARAFLAMA CHUQUR tahlil qil.

TENDER SHARTNOMASI:
{tender_text[:10000]}

VAZIFA - QUYIDAGILARNI BATAFSIL ANIQLA:

1. TENDER ASOSIY MA'LUMOTLARI:
   - Tender maqsadi va mohiyati
   - Tender turi va kategoriyasi
   - Byudjet va moliyaviy shartlar
   - Muddatlar va vaqt jadvali
   - Loyiha joylashuvi (lokatsiya)

2. BARCHA TALABLARNI ANIQLASH:
   - Texnik talablar
   - Moliyaviy talablar
   - Huquqiy talablar
   - Tajriba talablari
   - Hujjat talablari
   - Sifat talablari
   - Xavfsizlik talablari
   - Kadrlar talablari

3. HAR BIR TALAB UCHUN:
   - Majburiy yoki ixtiyoriy
   - Vazn koeffitsienti (0.1-1.0)
   - Baholash mezoni
   - Minimal va maksimal qiymatlar

4. MAXSUS SHARTLAR:
   - Lokatsiya talablari
   - Mahalliy ishtirok talablari
   - Subpudratchi shartlari
   - Kafolat talablari
   - Sug'urta talablari

JSON FORMAT (faqat JSON qaytar, boshqa matn yo'q):
{{
    "tender_purpose": "Tender maqsadi batafsil",
    "tender_type": "qurilish|xizmat|tovar|aralash",
    "tender_category": "Tender kategoriyasi",
    "project_location": "Loyiha joylashuvi",
    "estimated_budget": "Taxminiy byudjet",
    "budget_range": {{
        "min": "Minimal summa",
        "max": "Maksimal summa"
    }},
    "timeline": {{
        "submission_deadline": "Topshirish muddati",
        "project_start": "Loyiha boshlanishi",
        "project_end": "Loyiha tugashi",
        "total_duration": "Umumiy muddat"
    }},
    "requirements": [
        {{
            "id": "REQ001",
            "category": "technical|financial|legal|experience|document|quality|safety|personnel",
            "title": "Talab nomi",
            "description": "Batafsil tavsif",
            "is_mandatory": true|false,
            "weight": 0.1-1.0,
            "min_value": "Minimal qiymat (agar mavjud)",
            "evaluation_method": "Baholash usuli"
        }}
    ],
    "location_requirements": {{
        "project_region": "Loyiha mintaqasi",
        "local_presence_required": true|false,
        "proximity_preference": "Yaqinlik afzalligi",
        "logistics_requirements": "Logistika talablari"
    }},
    "experience_requirements": {{
        "min_years": "Minimal yillar",
        "similar_projects": "O'xshash loyihalar soni",
        "min_project_value": "Minimal loyiha qiymati",
        "sector_experience": "Soha tajribasi"
    }},
    "financial_requirements": {{
        "min_turnover": "Minimal aylanma",
        "bank_guarantee": "Bank kafolati",
        "insurance_required": true|false,
        "payment_terms": "To'lov shartlari"
    }},
    "evaluation_criteria": [
        {{
            "name": "Baholash mezoni",
            "weight": 0.1-1.0,
            "description": "Mezon tavsifi",
            "scoring_method": "Ballar berish usuli"
        }}
    ],
    "special_conditions": ["Maxsus shartlar"],
    "key_conditions": ["Asosiy shartlar"],
    "warnings": ["Diqqat talab qiladigan jihatlar"],
    "hidden_requirements": ["Yashirin yoki bilvosita talablar"],
    "disqualification_criteria": ["Rad etish mezonlari"]
}}
"""
            
            llm_result = llm_engine.generate_response(
                analysis_prompt,
                system_prompt=system_prompt,
                temperature=0.2
            )
            
            # LLM natijasini tekshirish
            if not llm_result.get('success'):
                raise ValueError(llm_result.get('error', 'LLM xatolik berdi'))
            
            result = llm_result.get('response', '')
            
            # JSON ni parse qilish - yaxshilangan
            try:
                # JSON ni topish
                json_match = re.search(r'\{[\s\S]*\}', result)
                if json_match:
                    json_str = json_match.group()
                    # JSON ni tozalash
                    json_str = re.sub(r',\s*}', '}', json_str)  # Trailing comma
                    json_str = re.sub(r',\s*]', ']', json_str)  # Trailing comma in array
                    json_str = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', json_str)  # Control characters
                    analysis = json.loads(json_str)
                else:
                    raise ValueError("JSON topilmadi")
            except json.JSONDecodeError as e:
                logger.error(f"JSON parse xatosi: {e}")
                # Qayta urinish - soddalashtirilgan prompt bilan
                retry_prompt = f"""
Quyidagi tender hujjatini tahlil qil. FAQAT ODDIY JSON qaytar:

{tender_text[:5000]}

JSON:
{{
    "tender_purpose": "maqsad",
    "tender_type": "qurilish|xizmat|tovar",
    "estimated_budget": "summa",
    "deadline": "muddat",
    "requirements": [
        {{"id": "REQ001", "category": "experience", "title": "talab", "description": "tavsif", "is_mandatory": true, "weight": 0.5}}
    ]
}}
"""
                retry_result = llm_engine.generate_response(retry_prompt, temperature=0.1)
                if retry_result.get('success'):
                    try:
                        retry_json = re.search(r'\{[\s\S]*\}', retry_result.get('response', ''))
                        if retry_json:
                            analysis = json.loads(retry_json.group())
                        else:
                            analysis = self._fallback_tender_analysis(tender_text)
                    except:
                        analysis = self._fallback_tender_analysis(tender_text)
                else:
                    analysis = self._fallback_tender_analysis(tender_text)
            
            # Talablarni saqlash
            self.tender_requirements = []
            for req in analysis.get('requirements', []):
                self.tender_requirements.append(TenderRequirement(
                    id=req.get('id', f"REQ{len(self.tender_requirements)+1:03d}"),
                    category=req.get('category', 'other'),
                    title=req.get('title', ''),
                    description=req.get('description', ''),
                    is_mandatory=req.get('is_mandatory', False),
                    weight=float(req.get('weight', 0.5))
                ))
            
            # Metadata qo'shish
            if tender_metadata:
                analysis['metadata'] = tender_metadata
            
            analysis['requirements_count'] = len(self.tender_requirements)
            analysis['mandatory_count'] = sum(1 for r in self.tender_requirements if r.is_mandatory)
            
            self.tender_info = analysis
            
            logger.info(f"Tender tahlili yakunlandi. {len(self.tender_requirements)} ta talab aniqlandi.")
            
            return {
                'success': True,
                'analysis': analysis
            }
            
        except Exception as e:
            logger.error(f"Tender tahlilida xatolik: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def analyze_participant(
        self, 
        participant_name: str,
        participant_text: str, 
        participant_metadata: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Ishtirokchi hujjatlarini tender talablariga mosligini tahlil qilish
        
        Args:
            participant_name: Ishtirokchi nomi
            participant_text: Ishtirokchi hujjatlari matni
            participant_metadata: Qo'shimcha ma'lumotlar
        
        Returns:
            Ishtirokchi tahlili natijalari
        """
        try:
            logger.info(f"Ishtirokchi tahlili boshlandi: {participant_name}")

            lang = _normalize_language((participant_metadata or {}).get('language'))
            if lang == 'ru':
                lang_instruction = 'Ответь на русском языке. '
                system_prompt = 'Ты эксперт по государственным закупкам. Оценивай участников справедливо и детально. Возвращай только JSON.'
            elif lang == 'uz_cyrl':
                lang_instruction = 'Жавобни ўзбек тилида (кирилл) бер. '
                system_prompt = "Сен Ўзбекистон давлат харидлари бўйича экспертсан. Иштирокчиларни адолатли баҳолайсан. Фақат JSON форматда жавоб бер."
            else:
                lang_instruction = "Javobni o'zbek tilida (lotin) ber. "
                system_prompt = "Sen O'zbekiston davlat xaridlari bo'yicha ekspertsan. Ishtirokchilarni adolatli baholaysan. Faqat JSON formatida javob ber."
            
            if not self.tender_requirements:
                return {
                    'success': False,
                    'error': 'Avval tender shartnomasini tahlil qilish kerak'
                }
            
            # Talablar ro'yxatini tayyorlash
            requirements_text = "\n".join([
                f"- {req.id}: {req.title} ({req.category}) - {'Majburiy' if req.is_mandatory else 'Ixtiyoriy'} - Vazn: {req.weight}"
                for req in self.tender_requirements
            ])
            
            # LLM orqali tahlil
            default_purpose = "Nomalum"
            analysis_prompt = f"""
{lang_instruction}
Sen tender ishtirokchilarini HAR TARAFLAMA baholash bo'yicha ekspertsan. 
DIQQAT: Barcha jihatlarni CHUQUR tahlil qil, hech narsa e'tibordan chetda qolmasin!

TENDER TALABLARI:
{requirements_text}

TENDER MAQSADI:
{self.tender_info.get('tender_purpose', default_purpose)}

ISHTIROKCHI HUJJATLARI:
{participant_text[:8000]}

VAZIFA - QUYIDAGILARNI BATAFSIL TAHLIL QIL:

1. TAJRIBA TAHLILI:
   - Sohadagi umumiy tajriba (yillar)
   - O'xshash loyihalar soni va hajmi
   - Muvaffaqiyatli yakunlangan loyihalar
   - Referenslar va tavsiyalar
   - Xodimlar malakasi va tajribasi

2. LOKATSIYA TAHLILI:
   - Kompaniya joylashuvi
   - Tender joyi bilan masofa
   - Mintaqaviy tajriba
   - Logistika imkoniyatlari
   - Mahalliy bozor bilimi

3. XIZMAT TAKLIFLARI TAHLILI:
   - Taklif etilgan xizmatlar to'liq ro'yxati
   - Qo'shimcha xizmatlar va bonuslar
   - Kafolat shartlari
   - Texnik yordam va support
   - Vaqt jadvali va muddatlar
   - Innovatsion yondashuvlar

4. MOLIYAVIY TAHLIL:
   - Taklif narxi batafsil
   - Narx tarkibi va shaffoflik
   - To'lov shartlari
   - Moliyaviy barqarorlik
   - Bozor narxi bilan solishtirish
   - Yashirin xarajatlar tahlili

5. TEXNIK IMKONIYATLAR:
   - Uskunalar va texnika
   - Sertifikatlar va litsenziyalar
   - Sifat nazorati tizimlari
   - Xavfsizlik standartlari
   - Ekologik muvofiqlik

6. RISKLAR TAHLILI:
   - Moliyaviy risklar
   - Operatsion risklar
   - Muddatlarni buzish xavfi
   - Sifat risklari
   - Huquqiy risklar

JSON FORMAT (faqat JSON qaytar):
{{
    "participant_name": "{participant_name}",
    "overall_match_percentage": 0-100 orasida foiz,
    "scores": [
        {{
            "requirement_id": "REQ001",
            "score": 0-100,
            "matches": true|false,
            "reason": "Baholash sababi",
            "details": "Batafsil tushuntirish"
        }}
    ],
    "experience_analysis": {{
        "years_in_business": "Yillar soni",
        "similar_projects_count": "O'xshash loyihalar soni",
        "successful_projects": "Muvaffaqiyatli loyihalar",
        "team_qualification": "Jamoa malakasi",
        "references_quality": "Referenslar sifati (past/o'rta/yuqori)",
        "experience_score": 0-100
    }},
    "location_analysis": {{
        "company_location": "Kompaniya joylashuvi",
        "distance_to_project": "Loyiha joyigacha masofa",
        "regional_experience": "Mintaqaviy tajriba",
        "logistics_capability": "Logistika imkoniyati",
        "local_market_knowledge": "Mahalliy bozor bilimi",
        "location_score": 0-100
    }},
    "service_offer_analysis": {{
        "main_services": ["Asosiy xizmatlar"],
        "additional_services": ["Qo'shimcha xizmatlar"],
        "warranty_terms": "Kafolat shartlari",
        "support_quality": "Texnik yordam sifati",
        "timeline_feasibility": "Muddat realligi",
        "innovation_level": "Innovatsiya darajasi",
        "service_score": 0-100
    }},
    "financial_analysis": {{
        "proposed_price": "Taklif etilgan narx",
        "price_breakdown": "Narx tarkibi",
        "payment_terms": "To'lov shartlari",
        "financial_stability": "Moliyaviy barqarorlik",
        "market_comparison": "Bozor bilan solishtirish",
        "hidden_costs_risk": "Yashirin xarajatlar xavfi",
        "price_adequacy": "past|mos|yuqori",
        "price_score": 0-100
    }},
    "technical_capabilities": {{
        "equipment_quality": "Uskunalar sifati",
        "certifications": ["Sertifikatlar ro'yxati"],
        "quality_systems": ["Sifat tizimlari"],
        "safety_standards": "Xavfsizlik standartlari",
        "environmental_compliance": "Ekologik muvofiqlik",
        "technical_score": 0-100
    }},
    "risk_assessment": {{
        "financial_risk": "past|o'rta|yuqori",
        "operational_risk": "past|o'rta|yuqori",
        "timeline_risk": "past|o'rta|yuqori",
        "quality_risk": "past|o'rta|yuqori",
        "legal_risk": "past|o'rta|yuqori",
        "overall_risk": "low|medium|high",
        "risk_mitigation": ["Risk kamaytirish choralari"]
    }},
    "strengths": ["Har bir ustunlik batafsil"],
    "weaknesses": ["Har bir kamchilik batafsil"],
    "minor_advantages": ["Kichik ustunliklar"],
    "minor_disadvantages": ["Kichik kamchiliklar"],
    "recommendation": "Batafsil tavsiya",
    "final_verdict": "Tender uchun tavsiya etiladi/Shartli tavsiya/Tavsiya etilmaydi",
    "improvement_suggestions": ["Yaxshilash uchun tavsiyalar"],
    "disqualification_reasons": ["Agar bo'lsa, rad etish sabablari"]
}}
"""
            
            llm_result = llm_engine.generate_response(
                analysis_prompt,
                system_prompt=system_prompt,
                temperature=0.3
            )
            
            # LLM natijasini tekshirish
            if not llm_result.get('success'):
                raise ValueError(llm_result.get('error', 'LLM xatolik berdi'))
            
            result = llm_result.get('response', '')
            
            # JSON ni parse qilish - yaxshilangan
            try:
                json_match = re.search(r'\{[\s\S]*\}', result)
                if json_match:
                    json_str = json_match.group()
                    # JSON ni tozalash
                    json_str = re.sub(r',\s*}', '}', json_str)
                    json_str = re.sub(r',\s*]', ']', json_str)
                    json_str = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', json_str)
                    analysis = json.loads(json_str)
                else:
                    raise ValueError("JSON topilmadi")
            except json.JSONDecodeError as e:
                logger.error(f"JSON parse xatosi: {e}")
                # Qayta urinish - soddalashtirilgan prompt
                retry_prompt = f"""
Ishtirokchi: {participant_name}
Ma'lumotlar: {participant_text[:3000]}

ODDIY JSON qaytar:
{{
    "participant_name": "{participant_name}",
    "overall_match_percentage": 0-100,
    "experience_score": 0-100,
    "location_score": 0-100,
    "service_score": 0-100,
    "price_score": 0-100,
    "technical_score": 0-100,
    "risk_level": "low|medium|high",
    "strengths": ["ustunlik1"],
    "weaknesses": ["kamchilik1"],
    "recommendation": "tavsiya",
    "final_verdict": "tavsiya etiladi|shartli|tavsiya etilmaydi"
}}
"""
                retry_result = llm_engine.generate_response(retry_prompt, temperature=0.1)
                if retry_result.get('success'):
                    try:
                        retry_json = re.search(r'\{[\s\S]*\}', retry_result.get('response', ''))
                        if retry_json:
                            simple_analysis = json.loads(retry_json.group())
                            # To'liq formatga o'tkazish
                            analysis = {
                                'participant_name': simple_analysis.get('participant_name', participant_name),
                                'overall_match_percentage': simple_analysis.get('overall_match_percentage', 50),
                                'scores': [],
                                'experience_analysis': {'experience_score': simple_analysis.get('experience_score', 50)},
                                'location_analysis': {'location_score': simple_analysis.get('location_score', 50)},
                                'service_offer_analysis': {'service_score': simple_analysis.get('service_score', 50)},
                                'financial_analysis': {'price_score': simple_analysis.get('price_score', 50)},
                                'technical_capabilities': {'technical_score': simple_analysis.get('technical_score', 50)},
                                'risk_assessment': {'overall_risk': simple_analysis.get('risk_level', 'medium')},
                                'strengths': simple_analysis.get('strengths', []),
                                'weaknesses': simple_analysis.get('weaknesses', []),
                                'recommendation': simple_analysis.get('recommendation', ''),
                                'final_verdict': simple_analysis.get('final_verdict', ''),
                                'risk_level': simple_analysis.get('risk_level', 'medium')
                            }
                        else:
                            analysis = self._fallback_participant_analysis(participant_name, participant_text)
                    except:
                        analysis = self._fallback_participant_analysis(participant_name, participant_text)
                else:
                    analysis = self._fallback_participant_analysis(participant_name, participant_text)
            
            # Umumiy ballni hisoblash - analysis ham uzatiladi
            total_score = self._calculate_weighted_score(analysis.get('scores', []), analysis)
            analysis['total_weighted_score'] = total_score
            
            # Metadata qo'shish
            if participant_metadata:
                analysis['metadata'] = participant_metadata
            
            logger.info(f"Ishtirokchi tahlili yakunlandi: {participant_name}, Ball: {total_score:.1f}%")
            
            return {
                'success': True,
                'analysis': analysis
            }
            
        except Exception as e:
            logger.error(f"Ishtirokchi tahlilida xatolik: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def compare_participants(self, participants: List[Dict[str, Any]], language: str = 'uz_latn') -> Dict[str, Any]:
        # Kamida 2 ta ishtirokchi bo'lishi shart
        language = _normalize_language(language)
        if len(participants) < 2:
            error_msg = (
                "Reyting yaratish uchun kamida 2 ta ishtirokchi kerak. Hozircha {} ta tahlil qilingan. Yana ishtirokchi qo'shing.".format(len(participants))
                if _is_uzbek(language) else
                "Для создания рейтинга нужно минимум 2 участника. Сейчас только {}. Добавьте еще участника.".format(len(participants))
            )
            return {
                'success': False,
                'error': error_msg
            }
        """
        Barcha ishtirokchilarni solishtirish va reyting tuzish
        
        Args:
            participants: Ishtirokchilar tahlillari ro'yxati
            language: Til (uz yoki ru)
        
        Returns:
            Solishtirish natijalari va reyting
        """
        try:
            logger.info(f"{len(participants)} ta ishtirokchini solishtirish")
            
            # Balllar bo'yicha saralash
            sorted_participants = sorted(
                participants, 
                key=lambda x: x.get('total_weighted_score', 0), 
                reverse=True
            )
            
            # Reyting qo'shish
            for i, p in enumerate(sorted_participants, 1):
                p['rank'] = i
            
            # G'olib va tavsiya
            winner = sorted_participants[0] if sorted_participants else None
            
            # Solishtirma jadval - BATAFSIL
            comparison_table = []
            for p in sorted_participants:
                comparison_table.append({
                    'rank': p.get('rank'),
                    'name': p.get('participant_name'),
                    'score': p.get('total_weighted_score', 0),
                    'match_percentage': p.get('overall_match_percentage', 0),
                    'experience_score': p.get('experience_analysis', {}).get('experience_score', 0),
                    'location_score': p.get('location_analysis', {}).get('location_score', 0),
                    'service_score': p.get('service_offer_analysis', {}).get('service_score', 0),
                    'financial_score': p.get('financial_analysis', {}).get('price_score', 0),
                    'technical_score': p.get('technical_capabilities', {}).get('technical_score', 0),
                    'risk_level': p.get('risk_assessment', {}).get('overall_risk', p.get('risk_level', 'unknown')),
                    'strengths': p.get('strengths', [])[:3],
                    'weaknesses': p.get('weaknesses', [])[:3],
                    'recommendation': p.get('recommendation', '')[:150],
                    'final_verdict': p.get('final_verdict', '')
                })
            
            # Tahlil xulosa - til bo'yicha
            if language == 'ru':
                summary_prompt = f"""
Ты эксперт и арбитр по тендерам. Сравни следующих участников ВСЕСТОРОННЕ и напиши ПОДРОБНОЕ заключение.

АНАЛИЗ УЧАСТНИКОВ:
{json.dumps(comparison_table, ensure_ascii=False, indent=2)}

НАПИШИ ПОДРОБНОЕ ЗАКЛЮЧЕНИЕ:

1. ОСНОВАНИЯ ОБЩЕГО РЕЙТИНГА:
   - Почему именно такой порядок
   - Основные различия каждого участника

2. АНАЛИЗ ПОБЕДИТЕЛЯ:
   - Почему на первом месте
   - Его основные преимущества
   - Потенциальные риски

3. ДРУГИЕ УЧАСТНИКИ:
   - Сильные стороны каждого
   - Слабые стороны каждого
   - Возможности для улучшения

4. СРАВНЕНИЕ:
   - По опыту
   - По цене
   - По качеству
   - По местоположению

5. ИТОГОВАЯ РЕКОМЕНДАЦИЯ:
   - Кого следует выбрать
   - На каких условиях
   - С какими предупреждениями

6. АЛЬТЕРНАТИВНЫЙ ВАРИАНТ:
   - Если победитель откажется, кто следующий
   - Почему
"""
                system_prompt = "Ты высококвалифицированный эксперт и арбитр по государственным закупкам. Пиши всестороннее, справедливое и подробное заключение на русском языке."
            elif language == 'uz_cyrl':
                summary_prompt = f"""
Сен тендер эксперти ва ҳаккамсан. Қуйидаги иштирокчиларни ҲАР ТАРАФЛАМА солиштир ва БАТАФСИЛ хулоса ёз.

ИШТИРОКЧИЛАР ТАҲЛИЛИ:
{json.dumps(comparison_table, ensure_ascii=False, indent=2)}

БАТАФСИЛ ХУЛОСА ЁЗ:

1. УМУМИЙ РЕЙТИНГ АСОСЛАРИ:
   - Нима учун айнан шу тартибда жойлаштирилди
   - Ҳар бир иштирокчининг асосий фарқлари

2. ҒОЛИБ ТАҲЛИЛИ:
   - Нима учун биринчи ўринда
   - Унинг асосий устунликлари
   - Потенциал рисклари

3. БОШҚА ИШТИРОКЧИЛАР:
   - Ҳар бирининг кучли томонлари
   - Ҳар бирининг заиф томонлари
   - Яхшилаш имкониятлари

4. ТАҚҚОСЛАШ:
   - Таҗриба бўйича солиштириш
   - Нарҳ бўйича солиштириш
   - Сифат бўйича солиштириш
   - Локация бўйича солиштириш

5. ЯКУНИЙ ТАВСИЯ:
   - Ким танланиши керак
   - Қандай шартлар билан
   - Қандай огоҳлантиришлар билан

6. АЛТЕРНАТИВ ВАРИАНТ:
   - Агар ғолиб рад этса, ким кейинги
   - Нима учун
"""
                system_prompt = "Сен Ўзбекистон давлат харидлари бўйича юқори малакали эксперт ва ҳакамсан. Ҳар тарафлама, адолатли ва батафсил хулоса ёз (ўзбек кирилл)."
            else:
                summary_prompt = f"""
Sen tender eksperti va hakamsan. Quyidagi ishtirokchilarni HAR TARAFLAMA solishtir va BATAFSIL xulosa yoz.

ISHTIROKCHILAR TAHLILI:
{json.dumps(comparison_table, ensure_ascii=False, indent=2)}

BATAFSIL XULOSA YOZ:

1. UMUMIY REYTING ASOSLARI:
   - Nima uchun aynan shu tartibda joylashtirildi
   - Har bir ishtirokchining asosiy farqlari

2. G'OLIB TAHLILI:
   - Nima uchun birinchi o'rinda
   - Uning asosiy ustunliklari
   - Potentsial risklari

3. BOSHQA ISHTIROKCHILAR:
   - Har birining kuchli tomonlari
   - Har birining zaif tomonlari
   - Yaxshilash imkoniyatlari

4. TAQQOSLASH:
   - Tajriba bo'yicha solishtirish
   - Narx bo'yicha solishtirish
   - Sifat bo'yicha solishtirish
   - Lokatsiya bo'yicha solishtirish

5. YAKUNIY TAVSIYA:
   - Kim tanlanishi kerak
   - Qanday shartlar bilan
   - Qanday ogohlantirishlar bilan

6. ALTERNATIV VARIANT:
   - Agar g'olib rad etsa, kim keyingi
   - Nima uchun
"""
                system_prompt = "Sen O'zbekiston davlat xaridlari bo'yicha yuqori malakali ekspert va hakamsan. Har taraflama, adolatli va batafsil xulosa yoz."
            
            summary_result = llm_engine.generate_response(
                summary_prompt,
                system_prompt=system_prompt,
                temperature=0.3
            )
            
            if language == 'ru':
                no_summary = 'Заключение не подготовлено'
            elif language == 'uz_cyrl':
                no_summary = 'Хулоса тайёрланмади'
            else:
                no_summary = 'Xulosa tayyorlanmadi'
            summary = summary_result.get('response', '') if summary_result.get('success') else no_summary
            
            return {
                'success': True,
                'ranking': sorted_participants,
                'comparison_table': comparison_table,
                'winner': winner,
                'summary': summary,
                'total_participants': len(participants),
                'analysis_depth': 'comprehensive'
            }
            
        except Exception as e:
            logger.error(f"Ishtirokchilar solishtirishda xatolik: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _calculate_weighted_score(self, scores: List[Dict[str, Any]], analysis: Dict[str, Any] = None) -> float:
        """Vaznli ballni hisoblash - turli manbalardan"""
        # Avval scores massividan hisoblashga urinish
        if scores:
            total_weight = 0
            weighted_sum = 0
            
            for score in scores:
                req_id = score.get('requirement_id', '')
                req = next((r for r in self.tender_requirements if r.id == req_id), None)
                
                weight = req.weight if req else 0.5
                score_value = float(score.get('score', 0))
                
                weighted_sum += score_value * weight
                total_weight += weight
            
            if total_weight > 0:
                return weighted_sum / total_weight
        
        # Agar scores bo'sh bo'lsa, analysis dan turli balllarni olish
        if analysis:
            component_scores = []
            
            # Tajriba balli
            exp_score = analysis.get('experience_analysis', {}).get('experience_score', 0)
            if exp_score: component_scores.append(exp_score)
            
            # Joylashuv balli
            loc_score = analysis.get('location_analysis', {}).get('location_score', 0)
            if loc_score: component_scores.append(loc_score)
            
            # Xizmat balli
            srv_score = analysis.get('service_offer_analysis', {}).get('service_score', 0)
            if srv_score: component_scores.append(srv_score)
            
            # Narx balli
            price_score = analysis.get('financial_analysis', {}).get('price_score', 0)
            if price_score: component_scores.append(price_score)
            
            # Texnik balli
            tech_score = analysis.get('technical_capabilities', {}).get('technical_score', 0)
            if tech_score: component_scores.append(tech_score)
            
            # Overall match percentage
            overall = analysis.get('overall_match_percentage', 0)
            if overall: component_scores.append(overall)
            
            if component_scores:
                return sum(component_scores) / len(component_scores)
        
        return 0
    
    def _fallback_tender_analysis(self, tender_text: str) -> Dict[str, Any]:
        """Fallback tender tahlili"""
        return {
            'tender_purpose': 'Tahlil qilinmadi',
            'tender_type': 'unknown',
            'requirements': [
                {
                    'id': 'REQ001',
                    'category': 'general',
                    'title': 'Umumiy talablar',
                    'description': tender_text[:500],
                    'is_mandatory': True,
                    'weight': 1.0
                }
            ],
            'evaluation_criteria': [],
            'key_conditions': [],
            'warnings': ['Avtomatik tahlil amalga oshmadi']
        }
    
    def _smart_fallback_tender_analysis(self, tender_text: str) -> Dict[str, Any]:
        """Aqlli fallback tender tahlili - matndan avtomatik talablarni ajratib olish"""
        requirements = []
        
        # Raqamli talablarni topish (1. 2. 3. yoki 1) 2) 3))
        numbered_pattern = r'(?:^|\n)\s*(\d+)[.\)]\s*([^\n]+)'
        matches = re.findall(numbered_pattern, tender_text)
        
        categories = {
            'tajriba': 'experience',
            'yil': 'experience',
            'loyiha': 'experience',
            'sertifikat': 'document',
            'iso': 'document',
            'litsenziya': 'document',
            'guvohnoma': 'document',
            'byudjet': 'financial',
            'narx': 'financial',
            'summa': 'financial',
            'moliya': 'financial',
            'kafolat': 'financial',
            'bank': 'financial',
            'muddat': 'technical',
            'oy': 'technical',
            'kun': 'technical',
            'texnik': 'technical',
            'sifat': 'quality',
            'xavfsizlik': 'safety',
            'xodim': 'personnel',
            'kadr': 'personnel',
            'malaka': 'personnel',
            'joylashuv': 'location',
            'manzil': 'location',
            'hudud': 'location',
            'viloyat': 'location',
            'shahar': 'location'
        }
        
        for i, (num, text) in enumerate(matches, 1):
            text = text.strip()
            if len(text) > 10:  # Minimal uzunlik
                # Kategoriyani aniqlash
                category = 'general'
                text_lower = text.lower()
                for keyword, cat in categories.items():
                    if keyword in text_lower:
                        category = cat
                        break
                
                requirements.append({
                    'id': f'REQ{i:03d}',
                    'category': category,
                    'title': text[:50] + ('...' if len(text) > 50 else ''),
                    'description': text,
                    'is_mandatory': True,
                    'weight': 0.5
                })
        
        # Agar raqamli talablar topilmasa, kalit so'zlarni izlash
        if not requirements:
            keywords = ['talab', 'shart', 'kerak', 'bo\'lishi', 'ega', 'minimal', 'kamida']
            sentences = re.split(r'[.!?]', tender_text)
            for i, sentence in enumerate(sentences, 1):
                sentence = sentence.strip()
                if any(kw in sentence.lower() for kw in keywords) and len(sentence) > 20:
                    requirements.append({
                        'id': f'REQ{i:03d}',
                        'category': 'general',
                        'title': sentence[:50] + ('...' if len(sentence) > 50 else ''),
                        'description': sentence,
                        'is_mandatory': True,
                        'weight': 0.5
                    })
                if len(requirements) >= 10:
                    break
        
        # Byudjet va muddatni topish
        budget_match = re.search(r'(\d{1,3}(?:[,.\s]\d{3})*)\s*(?:USD|so\'m|dollar|sum)', tender_text, re.IGNORECASE)
        deadline_match = re.search(r'(\d+)\s*(?:oy|kun|yil|month|day|year)', tender_text, re.IGNORECASE)
        
        return {
            'tender_purpose': tender_text[:200] + '...' if len(tender_text) > 200 else tender_text,
            'tender_type': 'qurilish' if 'qurilish' in tender_text.lower() else 'xizmat' if 'xizmat' in tender_text.lower() else 'tovar',
            'estimated_budget': budget_match.group(0) if budget_match else 'Aniqlanmadi',
            'deadline': deadline_match.group(0) if deadline_match else 'Aniqlanmadi',
            'requirements': requirements if requirements else [{
                'id': 'REQ001',
                'category': 'general',
                'title': 'Umumiy talablar',
                'description': tender_text[:500],
                'is_mandatory': True,
                'weight': 1.0
            }],
            'evaluation_criteria': [],
            'key_conditions': [],
            'warnings': ['Avtomatik tahlil - LLM javob bermadi, regex bilan tahlil qilindi']
        }
    
    def _fallback_tender_analysis(self, tender_text: str) -> Dict[str, Any]:
        """Fallback tender tahlili"""
        return self._smart_fallback_tender_analysis(tender_text)
    
    def _fallback_participant_analysis(self, name: str, text: str) -> Dict[str, Any]:
        """Fallback ishtirokchi tahlili"""
        # Matndan ma'lumotlarni ajratib olish
        experience_match = re.search(r'(\d+)\s*(?:yil|year)', text, re.IGNORECASE)
        price_match = re.search(r'(\d{1,3}(?:[,.\s]\d{3})*)\s*(?:USD|so\'m|dollar|sum)', text, re.IGNORECASE)
        
        return {
            'participant_name': name,
            'overall_match_percentage': 50,
            'scores': [],
            'experience_analysis': {
                'years_in_business': experience_match.group(1) if experience_match else 'Aniqlanmadi',
                'experience_score': 50
            },
            'location_analysis': {
                'location_score': 50
            },
            'service_offer_analysis': {
                'service_score': 50
            },
            'financial_analysis': {
                'proposed_price': price_match.group(0) if price_match else 'Aniqlanmadi',
                'price_adequacy': 'unknown',
                'price_score': 50
            },
            'technical_capabilities': {
                'technical_score': 50
            },
            'risk_assessment': {
                'overall_risk': 'medium'
            },
            'strengths': [],
            'weaknesses': ['Avtomatik tahlil amalga oshmadi - qo\'lda tekshirish talab etiladi'],
            'minor_advantages': [],
            'minor_disadvantages': [],
            'recommendation': 'Qo\'lda tekshirish talab etiladi',
            'final_verdict': 'Qo\'shimcha tekshiruv zarur',
            'risk_level': 'medium'
        }
    
    def get_tender_requirements(self) -> List[Dict[str, Any]]:
        """Tender talablarini olish"""
        return [asdict(req) for req in self.tender_requirements]
    
    def get_tender_info(self) -> Dict[str, Any]:
        """Tender ma'lumotlarini olish"""
        return self.tender_info


# Global instance
tender_analyzer = TenderAnalyzer()
