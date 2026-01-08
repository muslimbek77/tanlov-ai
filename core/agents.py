import logging
from typing import Dict, List, Any, Optional
from crewai import Agent, Task, Crew
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from .llm_engine import llm_engine

logger = logging.getLogger(__name__)


class DocumentAnalysisTool(BaseTool):
    """Hujjat tahlili uchun tool"""
    name: str = "document_analysis"
    description: str = "Hujjatni tahlil qilish va uning mohiyatini aniqlash"
    
    def _run(self, document_text: str, analysis_type: str = "general") -> str:
        """Hujjatni tahlil qilish"""
        try:
            result = llm_engine.analyze_document(document_text, analysis_type)
            if result['success']:
                return str(result['analysis'])
            else:
                return f"Tahlil xatoligi: {result.get('error', 'Noma\'lum xatolik')}"
        except Exception as e:
            logger.error(f"DocumentAnalysisTool da xatolik: {str(e)}")
            return f"Tool xatoligi: {str(e)}"


class ComplianceCheckTool(BaseTool):
    """Compliance tekshiruvi uchun tool"""
    name: str = "compliance_check"
    description: str = "Hujjatning O'RQ-684 va boshqa normativ hujjatlarga muvofiqligini tekshirish"
    
    def _run(self, document_text: str, regulation_type: str = "orq_684") -> str:
        """Compliance tekshiruvi"""
        try:
            result = llm_engine.analyze_document(document_text, 'compliance')
            if result['success']:
                return str(result['analysis'])
            else:
                return f"Compliance tekshiruvi xatoligi: {result.get('error', 'Noma\'lum xatolik')}"
        except Exception as e:
            logger.error(f"ComplianceCheckTool da xatolik: {str(e)}")
            return f"Tool xatoligi: {str(e)}"


class FraudDetectionTool(BaseTool):
    """Korrupsiya aniqlash uchun tool"""
    name: str = "fraud_detection"
    description: str = "Hujjatda korrupsiya xavflarini aniqlash"
    
    def _run(self, document_text: str) -> str:
        """Korrupsiya aniqlash"""
        try:
            result = llm_engine.analyze_document(document_text, 'fraud')
            if result['success']:
                return str(result['analysis'])
            else:
                return f"Korrupsiya aniqlash xatoligi: {result.get('error', 'Noma\'lum xatolik')}"
        except Exception as e:
            logger.error(f"FraudDetectionTool da xatolik: {str(e)}")
            return f"Tool xatoligi: {str(e)}"


class TechnicalAnalysisTool(BaseTool):
    """Texnik tahlil uchun tool"""
    name: str = "technical_analysis"
    description: str = "Texnik hujjatni tahlil qilish va uning sifatini baholash"
    
    def _run(self, document_text: str) -> str:
        """Texnik tahlil"""
        try:
            result = llm_engine.analyze_document(document_text, 'technical')
            if result['success']:
                return str(result['analysis'])
            else:
                return f"Texnik tahlil xatoligi: {result.get('error', 'Noma\'lum xatolik')}"
        except Exception as e:
            logger.error(f"TechnicalAnalysisTool da xatolik: {str(e)}")
            return f"Tool xatoligi: {str(e)}"


class DocumentComparisonTool(BaseTool):
    """Hujjat solishtirish uchun tool"""
    name: str = "document_comparison"
    description: str = "Ikki hujjatni solishtirish va ularning o'xshashligini aniqlash"
    
    def _run(self, doc1_text: str, doc2_text: str) -> str:
        """Hujjat solishtirish"""
        try:
            result = llm_engine.compare_documents(doc1_text, doc2_text)
            if result['success']:
                return str(result['comparison'])
            else:
                return f"Solishtirish xatoligi: {result.get('error', 'Noma\'lum xatolik')}"
        except Exception as e:
            logger.error(f"DocumentComparisonTool da xatolik: {str(e)}")
            return f"Tool xatoligi: {str(e)}"


class TenderAnalysisAgents:
    """Tender tahlili uchun agentlar"""
    
    def __init__(self):
        self.tools = [
            DocumentAnalysisTool(),
            ComplianceCheckTool(),
            FraudDetectionTool(),
            TechnicalAnalysisTool(),
            DocumentComparisonTool(),
        ]
        
        # LLM provayderini olish
        llm_provider = None
        if llm_engine.providers:
            # Birinchi mavjud bo'lgan provayderni olish
            provider_name, provider = llm_engine.providers[0]
            
            # LangChain uchun provayderni sozlash
            if provider_name == 'openai':
                from langchain_openai import ChatOpenAI
                llm_provider = ChatOpenAI(
                    model=provider.model,
                    api_key=provider.api_key,
                    temperature=0.3
                )
            elif provider_name == 'ollama':
                from langchain_community.llms import Ollama
                llm_provider = Ollama(
                    model=provider.model,
                    base_url=provider.base_url,
                    temperature=0.3
                )
        
        self.llm = llm_provider
        
        # Agentlarni yaratish
        self.auditor = self._create_auditor_agent()
        self.economist = self._create_economist_agent()
        self.technical_expert = self._create_technical_expert_agent()
        self.compliance_officer = self._create_compliance_officer_agent()
        self.fraud_investigator = self._create_fraud_investigator_agent()
    
    def _create_auditor_agent(self) -> Agent:
        """Auditor agentini yaratish"""
        return Agent(
            role='Tender Auditori',
            goal='Tender hujjatlarini komprehensiv tekshirish va audit qilish',
            backstory="""Siz tajribali auditor bo'lib, tender hujjatlaridagi barcha 
            noaniqliklarni, xavflarni va muammolarni aniqlay olasiz. O'zbekiston 
            Respublikasining davlat xaridlari to'g'risini chuqur bilasiz.""",
            verbose=True,
            allow_delegation=False,
            tools=self.tools,
            llm=self.llm
        )
    
    def _create_economist_agent(self) -> Agent:
        """Iqtisodchi agentini yaratish"""
        return Agent(
            role='Iqtisodchi Ekspert',
            goal='Tender narxlarini bozor qiymati bilan solishtirish va iqtisodiy samaradorlikni baholash',
            backstory="""Siz iqtisodchi bo'lib, narxlarning adilligini, byudjet 
            samaradorligini va bozor qiymatlarini tahlil qilishda chuqur tajribaga egasiz. 
            Qurilish materiallari bozori bilan tanishsiz.""",
            verbose=True,
            allow_delegation=False,
            tools=[DocumentAnalysisTool(), DocumentComparisonTool()],
            llm=self.llm
        )
    
    def _create_technical_expert_agent(self) -> Agent:
            """Texnik ekspert agentini yaratish"""
            return Agent(
                role='Texnik Ekspert',
                goal='Texnik spetsifikatsiyalarni tahlil qilish va ularning bajarilishi mumkinligini baholash',
                backstory="""Siz qurilish sohasida tajribali texnik ekspertsiz. 
                Qurilish normativlari, materiallarning texnik xususiyatlari va 
                qurilish texnologiyalari bo'yicha chuqur bilimlarga egasiz.""",
                verbose=True,
                allow_delegation=False,
                tools=[TechnicalAnalysisTool(), DocumentAnalysisTool()],
                llm=self.llm
            )
    
    def _create_compliance_officer_agent(self) -> Agent:
        """Compliance ofitseri agentini yaratish"""
        return Agent(
            role='Compliance Ofitseri',
            goal='Tender hujjatlarining O\'RQ-684 va boshqa normativ hujjatlarga muvofiqligini tekshirish',
            backstory="""Siz compliance bo'yicha ekspertsiz. O'zbekiston Respublikasining 
            "Davlat xaridlari to'g'risi" (O'RQ-684), qurilish kodeksi va boshqa 
            normativ hujjatlarni chuqur bilasiz.""",
            verbose=True,
            allow_delegation=False,
            tools=[ComplianceCheckTool(), DocumentAnalysisTool()],
            llm=self.llm
        )
    
    def _create_fraud_investigator(self) -> Agent:
        """Korrupsiya tergovchisi agentini yaratish"""
        return Agent(
            role='Korrupsiya Tergovchisi',
            goal='Tender jarayonida korrupsiya xavflarini aniqlash va tekshirish',
            backstory="""Siz korrupsiyaga qarshi kurash bo'yicha tajribali 
            tergovchisiz. Tenderlarda sodir bo'lishi mumkin bo'lgan korrupsiya 
            sxemalarini, narx manipulyatsiyalarini va boshqa xavfli belgilarni 
            aniqlay olasiz.""",
            verbose=True,
            allow_delegation=False,
            tools=[FraudDetectionTool(), DocumentComparisonTool(), DocumentAnalysisTool()],
            llm=self.llm
        )
    
    def create_tender_analysis_crew(self, tender_data: Dict[str, Any]) -> Crew:
        """Tender tahlili uchun crew yaratish"""
        
        # Vazifalarni yaratish
        audit_task = Task(
            description=f"""
            Tender hujjatlarini komprehensiv audit qiling:
            
            Tender ma'lumotlari:
            - Tender raqami: {tender_data.get('tender_number', 'Noma\'lum')}
            - Tashkilot: {tender_data.get('organization', 'Noma\'lum')}
            - Taxminiy byudjet: {tender_data.get('estimated_budget', 'Noma\'lum')}
            - Boshlanish sanasi: {tender_data.get('start_date', 'Noma\'lum')}
            - Tugash sanasi: {tender_data.get('end_date', 'Noma\'lum')}
            
            Quyidagilarga e'tibor bering:
            1. Hujjatlar to'liqligi
            2. Shartlarning aniqligi
            3. Vaqt talablariga rioya etilishi
            4. Potensial xavflar
            5. Umumiy sifat bahosi
            
            Batafsil hisobot tayyorlang.
            """,
            agent=self.auditor,
            expected_output="Tender audit bo'yicha batafsil hisobot"
        )
        
        compliance_task = Task(
            description=f"""
            Tender hujjatlarining O'RQ-684 ga muvofiqligini tekshiring:
            
            Quyidagi talablarga rioya etilishini tekshiring:
            1. Tender e'lon qilish muddati (kamida 15 kun)
            2. Hujjatlarni taqdim etish muddati (kamida 10 kun)
            3. Texnik spetsifikatsiyaning to'liqligi
            4. Baholash mezonlarining ochiqligi
            5. Shartnoma shartlarining qonuniyligi
            
            Muvofiqlik ballini (0-100) va topilgan kamchiliklarni ko'rsating.
            """,
            agent=self.compliance_officer,
            expected_output="Compliance tekshiruvi bo'yicha hisobot va ball"
        )
        
        economic_task = Task(
            description=f"""
            Tenderning iqtisodiy jihatlarini tahlil qiling:
            
            Taxminiy byudjet: {tender_data.get('estimated_budget', 'Noma\'lum')}
            
            Tahlil qiling:
            1. Byudjetning haqqonyligi
            2. Bozor narxlari bilan solishtirish
            3. Narxning qulayligi
            4. Iqtisodiy samaradorlik
            5. Potensial xavflar
            
            Iqtisodiy bahosini (0-100) va tavsiyalarni ko'rsating.
            """,
            agent=self.economist,
            expected_output="Iqtisodiy tahlil hisoboti va bahosi"
        )
        
        technical_task = Task(
            description=f"""
            Tender texnik talablarini tahlil qiling:
            
            Tender tavsifi: {tender_data.get('description', 'Noma\'lum')}
            
            Tahlil qiling:
            1. Texnik talablarning aniqligi
            2. Bajarilishi mumkinligi
            3. Zamonaviy standartlarga muvofiqligi
            4. Texnik xavflar
            5. Sifat talablari
            
            Texnik bahosini (0-100) va tavsiyalarni ko'rsating.
            """,
            agent=self.technical_expert,
            expected_output="Texnik tahlil hisoboti va bahosi"
        )
        
        fraud_task = Task(
            description=f"""
            Tender jarayonida korrupsiya xavflarini tekshiring:
            
            Tender ma'lumotlari:
            - Tender raqami: {tender_data.get('tender_number', 'Noma\'lum')}
            - Tashkilot: {tender_data.get('organization', 'Noma\'lum')}
            - Taxminiy byudjet: {tender_data.get('estimated_budget', 'Noma\'lum')}
            
            Quyidagi xavf belgilarini tekshiring:
            1. Noaniq shartlar
            2. G'ayrioddiy qisqartirishlar
            3. Diskriminatsion talablar
            4. Shubhali muddatlar
            5. Narx manipulyatsiyasi
            
            Xavf darajasini (low/medium/high/critical) va tavsiyalarni ko'rsating.
            """,
            agent=self.fraud_investigator,
            expected_output="Korrupsiya xavfi tahlili va tavsiyalar"
        )
        
        # Crew yaratish
        crew = Crew(
            agents=[
                self.auditor,
                self.compliance_officer,
                self.economist,
                self.technical_expert,
                self.fraud_investigator
            ],
            tasks=[
                audit_task,
                compliance_task,
                economic_task,
                technical_task,
                fraud_task
            ],
            verbose=2,
            process="hierarchical",  # Auditor boshqaruvchi
            manager_llm=self.llm
        )
        
        return crew
    
    def create_participant_evaluation_crew(self, participant_data: Dict[str, Any]) -> Crew:
        """Ishtirokchi baholashi uchun crew yaratish"""
        
        # Vazifalarni yaratish
        participant_audit_task = Task(
            description=f"""
            Ishtirokchi taklifini audit qiling:
            
            Ishtirokchi ma'lumotlari:
            - Kompaniya: {participant_data.get('company_name', 'Noma\'lum')}
            - Taklif etilgan narx: {participant_data.get('proposed_price', 'Noma\'lum')}
            - Tajriba: {participant_data.get('experience', 'Noma\'lum')}
            
            Tekshiring:
            1. Hujjatlar to'liqligi
            2. Malaka talablariga javob berishi
            3. Narxning asosliligi
            4. Xavf belgilari
            5. Umumiy sifat
            
            Batafsil hisobot va ball (0-100) tayyorlang.
            """,
            agent=self.auditor,
            expected_output="Ishtirokchi audit hisoboti va balli"
        )
        
        fraud_check_task = Task(
            description=f"""
            Ishtirokchi taklifida korrupsiya xavflarini tekshiring:
            
            Ishtirokchi ma'lumotlari:
            - Kompaniya: {participant_data.get('company_name', 'Noma\'lum')}
            - Taklif etilgan narx: {participant_data.get('proposed_price', 'Noma\'lum')}
            - Hujjatlar: {participant_data.get('documents', 'Noma\'lum')}
            
            Xavf belgilarini tekshiring:
            1. Narx anomaliyalari
            2. Hujjatlar o'xshashligi
            3. Shubhali naqliklar
            4. Metadata o'xshashligi
            5. Vaqt patternlari
            
            Xavf darajasini va tavsiyalarni ko'rsating.
            """,
            agent=self.fraud_investigator,
            expected_output="Korrupsiya xavfi tekshiruvi natijalari"
        )
        
        # Crew yaratish
        crew = Crew(
            agents=[
                self.auditor,
                self.fraud_investigator
            ],
            tasks=[
                participant_audit_task,
                fraud_check_task
            ],
            verbose=2,
            process="sequential"
        )
        
        return crew
    
    def analyze_tender_with_agents(self, tender_data: Dict[str, Any]) -> Dict[str, Any]:
        """Agentlar yordamida tender tahlili"""
        try:
            logger.info(f"Agentlar yordamida tender tahlili boshlandi: {tender_data.get('tender_number')}")
            
            crew = self.create_tender_analysis_crew(tender_data)
            result = crew.kickoff()
            
            logger.info(f"Agentlar tahlili yakunlandi: {tender_data.get('tender_number')}")
            
            return {
                'success': True,
                'result': result,
                'agents_used': ['auditor', 'compliance_officer', 'economist', 'technical_expert', 'fraud_investigator']
            }
            
        except Exception as e:
            logger.error(f"Agentlar tahlilida xatolik: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'agents_used': []
            }
    
    def evaluate_participant_with_agents(self, participant_data: Dict[str, Any]) -> Dict[str, Any]:
        """Agentlar yordamida ishtirokchi baholashi"""
        try:
            logger.info(f"Agentlar yordamida ishtirokchi baholashi boshlandi: {participant_data.get('company_name')}")
            
            crew = self.create_participant_evaluation_crew(participant_data)
            result = crew.kickoff()
            
            logger.info(f"Agentlar baholashi yakunlandi: {participant_data.get('company_name')}")
            
            return {
                'success': True,
                'result': result,
                'agents_used': ['auditor', 'fraud_investigator']
            }
            
        except Exception as e:
            logger.error(f"Agentlar baholashida xatolik: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'agents_used': []
            }


# Global instance
tender_agents = TenderAnalysisAgents()
