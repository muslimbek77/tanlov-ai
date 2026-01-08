import logging
import os
import json
from typing import Dict, List, Any, Optional, Union
from abc import ABC, abstractmethod
import openai
import requests
from django.conf import settings
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)


class BaseLLMProvider(ABC):
    """LLM provayderi uchun asosiy klass"""
    
    @abstractmethod
    def generate_response(self, prompt: str, **kwargs) -> str:
        """Javob generatsiya qilish"""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Provayderni mavjudligini tekshirish"""
        pass


class OpenAIProvider(BaseLLMProvider):
    """OpenAI GPT provayderi"""
    
    def __init__(self):
        self.api_key = settings.OPENAI_API_KEY
        self.model = settings.OPENAI_MODEL
        self.client = None
        
        if self.api_key:
            try:
                self.client = openai.OpenAI(api_key=self.api_key)
            except Exception as e:
                logger.error(f"OpenAI clientini ishga tushirishda xatolik: {str(e)}")
    
    def is_available(self) -> bool:
        """OpenAI mavjudligini tekshirish"""
        # Faqat client va API key mavjudligini tekshirish (test so'rov yubormay)
        return self.client is not None and self.api_key is not None
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def generate_response(self, prompt: str, **kwargs) -> str:
        """OpenAI orqali javob generatsiya qilish"""
        if not self.client:
            raise ValueError("OpenAI client mavjud emas")
        
        try:
            messages = [
                {"role": "system", "content": kwargs.get('system_prompt', '')},
                {"role": "user", "content": prompt}
            ]
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=kwargs.get('max_tokens', 1000),
                temperature=kwargs.get('temperature', 0.7),
                top_p=kwargs.get('top_p', 1.0),
                frequency_penalty=kwargs.get('frequency_penalty', 0.0),
                presence_penalty=kwargs.get('presence_penalty', 0.0)
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"OpenAI dan javob olishda xatolik: {str(e)}")
            raise


class OllamaProvider(BaseLLMProvider):
    """Ollama local LLM provayderi"""
    
    def __init__(self):
        self.base_url = settings.OLLAMA_BASE_URL
        self.model = settings.OLLAMA_MODEL
        self.timeout = 60
    
    def is_available(self) -> bool:
        """Ollama mavjudligini tekshirish"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get('models', [])
                model_names = [model['name'] for model in models]
                return any(self.model in name for name in model_names)
            return False
        except Exception as e:
            logger.warning(f"Ollama mavjud emas: {str(e)}")
            return False
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def generate_response(self, prompt: str, **kwargs) -> str:
        """Ollama orqali javob generatsiya qilish"""
        try:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": kwargs.get('temperature', 0.7),
                    "top_p": kwargs.get('top_p', 1.0),
                    "num_predict": kwargs.get('max_tokens', 1000),
                }
            }
            
            if kwargs.get('system_prompt'):
                payload["system"] = kwargs['system_prompt']
            
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('response', '').strip()
            else:
                raise Exception(f"Ollama API xatosi: {response.status_code}")
                
        except Exception as e:
            logger.error(f"Ollama dan javob olishda xatolik: {str(e)}")
            raise


class HybridLLMEngine:
    """Gibrid LLM dvigateli"""
    
    def __init__(self):
        self.providers = []
        self._initialize_providers()
    
    def _initialize_providers(self):
        """Provayderlarni ishga tushirish"""
        # OpenAI provayderi
        openai_provider = OpenAIProvider()
        if openai_provider.is_available():
            self.providers.append(('openai', openai_provider))
            logger.info("OpenAI provayderi ulandi")
        
        # Ollama provayderi
        ollama_provider = OllamaProvider()
        if ollama_provider.is_available():
            self.providers.append(('ollama', ollama_provider))
            logger.info("Ollama provayderi ulandi")
        
        if not self.providers:
            logger.error("Hech qanday LLM provayderi mavjud emas!")
    
    def generate_response(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """
        Javob generatsiya qilish (failover bilan)
        """
        if not self.providers:
            raise ValueError("Hech qanday LLM provayderi mavjud emas")
        
        last_error = None
        
        for provider_name, provider in self.providers:
            try:
                logger.info(f"{provider_name} provayderi orqali javob generatsiya qilinmoqda...")
                response = provider.generate_response(prompt, **kwargs)
                
                return {
                    'success': True,
                    'response': response,
                    'provider': provider_name,
                    'model': getattr(provider, 'model', 'unknown'),
                }
                
            except Exception as e:
                last_error = e
                logger.warning(f"{provider_name} provayderi xatolik berdi: {str(e)}")
                continue
        
        # Barcha provayderlar xatolik bersa
        error_msg = f"Barcha LLM provayderlari xatolik berdi. Oxirgi xatolik: {str(last_error)}"
        logger.error(error_msg)
        
        return {
            'success': False,
            'error': error_msg,
            'provider': None,
            'response': None,
        }
    
    def analyze_document(self, text: str, analysis_type: str = 'general') -> Dict[str, Any]:
        """
        Hujjatni tahlil qilish
        """
        prompts = {
            'compliance': f"""
            Quyidagi hujjatni O'zbekiston Respublikasining "Davlat xaridlari to'g'risi" (O'RQ-684) talablariga muvofiqligini tekshiring:
            
            Hujjat matni:
            {text}
            
            Quyidagi formatda javob bering:
            {{
                "compliance_score": 0-100 oralig'ida ball,
                "violations": ["buzilishlar ro'yxati"],
                "recommendations": ["tavsiyalar ro'yxati"],
                "missing_sections": ["yo'q bo'limlar"],
                "analysis": "qisqa tahlil"
            }}
            """,
            
            'fraud': f"""
            Quyidagi hujjatni korrupsiya xavflari nuqtai nazaridan tahlil qiling:
            
            Hujjat matni:
            {text}
            
            Quyidagi xavf turlariga e'tibor bering:
            - G'ayrioddiy narxlar
            - Shubhli shartlar
            - Noaniq ifodalar
            - Standartlardan chetlanish
            
            Quyidagi formatda javob bering:
            {{
                "risk_level": "low/medium/high/critical",
                "risk_score": 0-100 oralig'ida ball,
                "red_flags": ["xavf belgilari"],
                "suspicious_patterns": ["shubhali patternlar"],
                "recommendations": ["tavsiyalar"]
            }}
            """,
            
            'technical': f"""
            Quyidagi texnik hujjatni tahlil qiling va uning sifatini baholang:
            
            Hujjat matni:
            {text}
            
            Quyidagi formatda javob bering:
            {{
                "technical_score": 0-100 oralig'ida ball,
                "completeness": 0-100 oralig'ida ball,
                "clarity": 0-100 oralig'ida ball,
                "specifications": ["topilgan spetsifikatsiyalar"],
                "missing_info": ["yo'q ma'lumotlar"],
                "quality_issues": ["sifat muammolari"]
            }}
            """,
            
            'general': f"""
            Quyidagi hujjatni umumiy tahlil qiling:
            
            Hujjat matni:
            {text}
            
            Quyidagi formatda javob bering:
            {{
                "summary": "qisqa xulosa",
                "key_points": ["asosiy nuqtalar"],
                "entities": ["topilgan obyektlar"],
                "sentiment": "pozitiv/negativ/neytral",
                "language": "hujjat tili",
                "document_type": "hujjat turi"
            }}
            """
        }
        
        prompt = prompts.get(analysis_type, prompts['general'])
        
        result = self.generate_response(
            prompt,
            temperature=0.3,  # Analiz uchun past temperatura
            max_tokens=1500
        )
        
        if result['success']:
            try:
                # JSON javobini parse qilish
                response_text = result['response']
                # JSON ni matndan ajratish
                if '```json' in response_text:
                    json_start = response_text.find('```json') + 7
                    json_end = response_text.find('```', json_start)
                    json_text = response_text[json_start:json_end].strip()
                else:
                    json_text = response_text
                
                analysis_result = json.loads(json_text)
                
                return {
                    'success': True,
                    'analysis': analysis_result,
                    'provider': result['provider'],
                    'raw_response': response_text,
                }
                
            except json.JSONDecodeError as e:
                logger.error(f"LLM javobini parse qilishda xatolik: {str(e)}")
                return {
                    'success': False,
                    'error': f"Parse xatolik: {str(e)}",
                    'raw_response': result['response'],
                    'provider': result['provider'],
                }
        else:
            return result
    
    def compare_documents(self, doc1: str, doc2: str) -> Dict[str, Any]:
        """
        Ikki hujjatni solishtirish
        """
        prompt = f"""
        Quyidagi ikkita hujjatni solishtiring va ularning o'xshashlik darajasini aniqlang:
        
        Hujjat 1:
        {doc1}
        
        Hujjat 2:
        {doc2}
        
        Quyidagi formatda javob bering:
        {{
            "similarity_score": 0-100 oralig'ida ball,
            "similar_sections": ["o'xshash bo'limlar"],
            "differences": ["farqlar"],
            "plagiarism_risk": "low/medium/high/critical",
            "shared_terminology": ["umumiy terminologiya"],
            "analysis": "qisqa tahlil"
        }}
        """
        
        result = self.generate_response(
            prompt,
            temperature=0.2,
            max_tokens=1000
        )
        
        if result['success']:
            try:
                response_text = result['response']
                if '```json' in response_text:
                    json_start = response_text.find('```json') + 7
                    json_end = response_text.find('```', json_start)
                    json_text = response_text[json_start:json_end].strip()
                else:
                    json_text = response_text
                
                comparison_result = json.loads(json_text)
                
                return {
                    'success': True,
                    'comparison': comparison_result,
                    'provider': result['provider'],
                    'raw_response': response_text,
                }
                
            except json.JSONDecodeError as e:
                logger.error(f"Solishtirish natijasini parse qilishda xatolik: {str(e)}")
                return {
                    'success': False,
                    'error': f"Parse xatolik: {str(e)}",
                    'raw_response': result['response'],
                    'provider': result['provider'],
                }
        else:
            return result
    
    def generate_evaluation_report(self, evaluation_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Baholash hisobotini generatsiya qilish
        """
        prompt = f"""
        Quyidagi baholash ma'lumotlariga asoslanib, batafsil hisobot yarating:
        
        Baholash ma'lumotlari:
        {json.dumps(evaluation_data, ensure_ascii=False, indent=2)}
        
        Hisobot quyidagi bo'limlarni o'z ichiga olishi kerak:
        1. Xulosa
        2. Ishtirokchilar reytingi
        3. Asosiy topilmalar
        4. Xavf tahlili
        5. Tavsiyalar
        
        Javobni strukturali formatda bering.
        """
        
        result = self.generate_response(
            prompt,
            temperature=0.5,
            max_tokens=2000
        )
        
        return result
    
    def check_provider_status(self) -> Dict[str, Any]:
        """
        Barcha provayderlarning statusini tekshirish
        """
        status = {}
        
        for provider_name, provider in self.providers:
            status[provider_name] = {
                'available': provider.is_available(),
                'model': getattr(provider, 'model', 'unknown'),
            }
        
        return {
            'total_providers': len(self.providers),
            'available_providers': len([p for p in status.values() if p['available']]),
            'providers': status,
        }


# Global instance
llm_engine = HybridLLMEngine()
