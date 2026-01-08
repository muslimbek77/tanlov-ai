import logging
import hashlib
import ipaddress
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from decimal import Decimal
from django.utils import timezone
from django.db.models import Q, Count, Avg, StdDev
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from .models import (
    FraudDetection, MetadataAnalysis, PriceAnomalyDetection, 
    SimilarityAnalysis, FraudDetectionRule
)
from apps.tenders.models import Tender
from apps.participants.models import TenderParticipant, ParticipantDocument

logger = logging.getLogger(__name__)


class AntiFraudAnalyzer:
    """Anti-korrupsiya tahlili xizmati"""
    
    def __init__(self):
        self.similarity_threshold = 0.7
        self.price_deviation_threshold = 0.2  # 20%
        self.metadata_similarity_threshold = 0.8
        self.ip_similarity_threshold = 0.5
    
    def analyze_tender_fraud_risks(self, tender: Tender) -> Dict[str, Any]:
        """
        Tender uchun korrupsiya xavflarini tahlil qilish
        """
        try:
            logger.info(f"Tender korrupsiya tahlili boshlandi: {tender.id}")
            
            results = {
                'tender_id': tender.id,
                'total_risk_score': 0.0,
                'risk_level': 'low',
                'detections': [],
                'participants_risk': {},
                'recommendations': [],
            }
            
            participants = tender.participants.all()
            
            if len(participants) < 2:
                logger.info(f"Kam ishtirokchilar: {len(participants)}, korrupsiya tahlili cheklandi")
                return results
            
            # Metadata o'xshashligi tahlili
            metadata_results = self._analyze_metadata_similarity(participants)
            results['detections'].extend(metadata_results['detections'])
            results['total_risk_score'] += metadata_results['risk_score']
            
            # Narx anomaliyalari tahlili
            price_results = self._analyze_price_anomalies(tender, participants)
            results['detections'].extend(price_results['detections'])
            results['total_risk_score'] += price_results['risk_score']
            
            # Matn o'xshashligi tahlili
            similarity_results = self._analyze_content_similarity(participants)
            results['detections'].extend(similarity_results['detections'])
            results['total_risk_score'] += similarity_results['risk_score']
            
            # IP manzillar tahlili
            ip_results = self._analyze_ip_similarity(participants)
            results['detections'].extend(ip_results['detections'])
            results['total_risk_score'] += ip_results['risk_score']
            
            # Vaqt patternlari tahlili
            time_results = self._analyze_time_patterns(participants)
            results['detections'].extend(time_results['detections'])
            results['total_risk_score'] += time_results['risk_score']
            
            # Xavf darajasini aniqlash
            results['risk_level'] = self._determine_risk_level(results['total_risk_score'])
            
            # Tavsiyalar
            results['recommendations'] = self._generate_recommendations(results['detections'])
            
            # Har bir ishtirokchi uchun xavf balli
            results['participants_risk'] = self._calculate_participant_risks(results['detections'], participants)
            
            logger.info(f"Tender korrupsiya tahlili yakunlandi: Xavf balli {results['total_risk_score']}")
            return results
            
        except Exception as e:
            logger.error(f"Tender korrupsiya tahlilida xatolik: {str(e)}")
            return {
                'tender_id': tender.id,
                'status': 'error',
                'error': str(e),
            }
    
    def _analyze_metadata_similarity(self, participants) -> Dict[str, Any]:
        """Metadata o'xshashligini tahlil qilish"""
        results = {
            'detections': [],
            'risk_score': 0.0,
        }
        
        try:
            metadata_list = []
            participant_map = {}
            
            for participant in participants:
                # Har bir ishtirokchining hujjatlar metadata sini yig'ish
                documents = participant.documents.all()
                metadata = self._extract_participant_metadata(documents)
                
                if metadata:
                    metadata_list.append(metadata)
                    participant_map[participant.id] = metadata
            
            # Juftliklarni solishtirish
            for i in range(len(metadata_list)):
                for j in range(i + 1, len(metadata_list)):
                    similarity = self._calculate_metadata_similarity(
                        metadata_list[i], metadata_list[j]
                    )
                    
                    if similarity >= self.metadata_similarity_threshold:
                        # Xavf aniqlandi
                        risk_score = similarity * 100
                        
                        detection = {
                            'detection_type': 'metadata_similarity',
                            'severity': 'high' if similarity >= 0.9 else 'medium',
                            'risk_score': risk_score,
                            'description': f'Hujjatlari metadata jihatidan {similarity:.1%} o\'xshash',
                            'involved_participants': [
                                list(participant_map.keys())[i],
                                list(participant_map.keys())[j]
                            ],
                            'evidence': {
                                'similarity_score': similarity,
                                'shared_software': self._find_shared_software(
                                    metadata_list[i], metadata_list[j]
                                ),
                                'creation_times': {
                                    'participant_1': metadata_list[i].get('creation_date'),
                                    'participant_2': metadata_list[j].get('creation_date'),
                                }
                            }
                        }
                        
                        results['detections'].append(detection)
                        results['risk_score'] += risk_score
            
            logger.info(f"Metadata o'xshashligi tahlili: {len(results['detections'])} ta xavf topildi")
            
        except Exception as e:
            logger.error(f"Metadata o'xshashligi tahlilida xatolik: {str(e)}")
        
        return results
    
    def _analyze_price_anomalies(self, tender: Tender, participants) -> Dict[str, Any]:
        """Narx anomaliyalarini tahlil qilish"""
        results = {
            'detections': [],
            'risk_score': 0.0,
        }
        
        try:
            # Narxlar ro'yxatini olish
            prices = []
            participant_prices = {}
            
            for participant in participants:
                if participant.proposed_price:
                    prices.append(float(participant.proposed_price))
                    participant_prices[participant.id] = float(participant.proposed_price)
            
            if len(prices) < 2:
                return results
            
            # Statistik tahlil
            mean_price = np.mean(prices)
            std_price = np.std(prices)
            
            # Har bir ishtirokchi uchun narx anomaliyasini tekshirish
            for participant_id, price in participant_prices.items():
                # Z-score hisoblash
                if std_price > 0:
                    z_score = abs(price - mean_price) / std_price
                else:
                    z_score = 0
                
                # Foizdagi chetlanish
                deviation_percentage = abs(price - mean_price) / mean_price if mean_price > 0 else 0
                
                if deviation_percentage >= self.price_deviation_threshold:
                    # Anomaliya aniqlandi
                    if price < mean_price:
                        anomaly_type = 'too_low'
                        description = f'Taklif etilgan narx kutilganidan {deviation_percentage:.1%} past'
                    else:
                        anomaly_type = 'too_high'
                        description = f'Taklif etilgan narx kutilganidan {deviation_percentage:.1%} yuqori'
                    
                    risk_score = min(deviation_percentage * 100, 100)
                    
                    detection = {
                        'detection_type': 'price_anomaly',
                        'anomaly_type': anomaly_type,
                        'severity': 'critical' if deviation_percentage >= 0.5 else 'high',
                        'risk_score': risk_score,
                        'description': description,
                        'participant_id': participant_id,
                        'evidence': {
                            'proposed_price': price,
                            'expected_price': mean_price,
                            'deviation_percentage': deviation_percentage,
                            'z_score': z_score,
                            'price_range': {
                                'min': min(prices),
                                'max': max(prices),
                                'mean': mean_price,
                                'std': std_price,
                            }
                        }
                    }
                    
                    results['detections'].append(detection)
                    results['risk_score'] += risk_score
            
            # Sun'iy yaxlitlangan narxlarni tekshirish
            for participant_id, price in participant_prices.items():
                if self._is_unnaturally_round(price, mean_price):
                    detection = {
                        'detection_type': 'price_anomaly',
                        'anomaly_type': 'unnatural_round',
                        'severity': 'medium',
                        'risk_score': 30,
                        'description': 'Narx sun\'iy yaxlitlangan ko\'rinadi',
                        'participant_id': participant_id,
                        'evidence': {
                            'proposed_price': price,
                            'is_round_number': True,
                        }
                    }
                    
                    results['detections'].append(detection)
                    results['risk_score'] += 30
            
            logger.info(f"Narx anomaliyalari tahlili: {len(results['detections'])} ta xavf topildi")
            
        except Exception as e:
            logger.error(f"Narx anomaliyalari tahlilida xatolik: {str(e)}")
        
        return results
    
    def _analyze_content_similarity(self, participants) -> Dict[str, Any]:
        """Matn o'xshashligini tahlil qilish"""
        results = {
            'detections': [],
            'risk_score': 0.0,
        }
        
        try:
            # Matnlarni yig'ish
            texts = []
            participant_texts = {}
            
            for participant in participants:
                # Barcha hujjatlardan matnlarni olish
                documents = participant.documents.all()
                full_text = ' '.join([doc.extracted_text or '' for doc in documents])
                
                if full_text.strip():
                    texts.append(full_text)
                    participant_texts[participant.id] = full_text
            
            if len(texts) < 2:
                return results
            
            # TF-IDF vektorizatsiya
            vectorizer = TfidfVectorizer(
                max_features=1000,
                stop_words=['va', 'ham', 'bilan', 'uchun', 'va', 'the', 'and', 'or', 'but'],
                ngram_range=(1, 2)
            )
            
            try:
                tfidf_matrix = vectorizer.fit_transform(texts)
                
                # Kosinus o'xshashligi
                similarity_matrix = cosine_similarity(tfidf_matrix)
                
                # Yuqori o'xshashlikdagi juftliklarni topish
                participant_ids = list(participant_texts.keys())
                
                for i in range(len(similarity_matrix)):
                    for j in range(i + 1, len(similarity_matrix)):
                        similarity = similarity_matrix[i][j]
                        
                        if similarity >= self.similarity_threshold:
                            risk_score = similarity * 80
                            
                            detection = {
                                'detection_type': 'content_similarity',
                                'severity': 'critical' if similarity >= 0.9 else 'high',
                                'risk_score': risk_score,
                                'description': f'Taklif matnlari {similarity:.1%} o\'xshash',
                                'involved_participants': [
                                    participant_ids[i],
                                    participant_ids[j]
                                ],
                                'evidence': {
                                    'similarity_score': similarity,
                                    'text_length_1': len(texts[i]),
                                    'text_length_2': len(texts[j]),
                                    'matching_phrases': self._find_matching_phrases(
                                        texts[i], texts[j]
                                    ),
                                }
                            }
                            
                            results['detections'].append(detection)
                            results['risk_score'] += risk_score
            
            except Exception as e:
                logger.warning(f"TF-IDF tahlilida xatolik: {str(e)}")
            
            logger.info(f"Matn o'xshashligi tahlili: {len(results['detections'])} ta xavf topildi")
            
        except Exception as e:
            logger.error(f"Matn o'xshashligi tahlilida xatolik: {str(e)}")
        
        return results
    
    def _analyze_ip_similarity(self, participants) -> Dict[str, Any]:
        """IP manzillar o'xshashligini tahlil qilish"""
        results = {
            'detections': [],
            'risk_score': 0.0,
        }
        
        try:
            # IP manzillarni yig'ish
            ip_addresses = {}
            
            for participant in participants:
                if participant.ip_address:
                    ip_addresses[participant.id] = str(participant.ip_address)
            
            if len(ip_addresses) < 2:
                return results
            
            # IP manzillarni solishtirish
            participant_ids = list(ip_addresses.keys())
            
            for i in range(len(participant_ids)):
                for j in range(i + 1, len(participant_ids)):
                    ip1 = ip_addresses[participant_ids[i]]
                    ip2 = ip_addresses[participant_ids[j]]
                    
                    # IP manzillar o'xshashligi
                    similarity = self._calculate_ip_similarity(ip1, ip2)
                    
                    if similarity >= self.ip_similarity_threshold:
                        risk_score = similarity * 60
                        
                        detection = {
                            'detection_type': 'ip_similarity',
                            'severity': 'high' if similarity >= 0.8 else 'medium',
                            'risk_score': risk_score,
                            'description': f'IP manzillar o\'xshash: {ip1} va {ip2}',
                            'involved_participants': [
                                participant_ids[i],
                                participant_ids[j]
                            ],
                            'evidence': {
                                'ip_1': ip1,
                                'ip_2': ip2,
                                'similarity_score': similarity,
                                'subnet_1': self._get_subnet(ip1),
                                'subnet_2': self._get_subnet(ip2),
                            }
                        }
                        
                        results['detections'].append(detection)
                        results['risk_score'] += risk_score
            
            logger.info(f"IP o'xshashligi tahlili: {len(results['detections'])} ta xavf topildi")
            
        except Exception as e:
            logger.error(f"IP o'xshashligi tahlilida xatolik: {str(e)}")
        
        return results
    
    def _analyze_time_patterns(self, participants) -> Dict[str, Any]:
        """Vaqt patternlarini tahlil qilish"""
        results = {
            'detections': [],
            'risk_score': 0.0,
        }
        
        try:
            # Ro'yxatdan o'tish va topshirish vaqtlarini yig'ish
            registration_times = {}
            submission_times = {}
            
            for participant in participants:
                if participant.registration_date:
                    registration_times[participant.id] = participant.registration_date
                if participant.submission_date:
                    submission_times[participant.id] = participant.submission_date
            
            # Ro'yxatdan o'tish vaqtlarining o'xshashligi
            if len(registration_times) >= 2:
                participant_ids = list(registration_times.keys())
                
                for i in range(len(participant_ids)):
                    for j in range(i + 1, len(participant_ids)):
                        time1 = registration_times[participant_ids[i]]
                        time2 = registration_times[participant_ids[j]]
                        
                        # Vaqt farqi
                        time_diff = abs((time1 - time2).total_seconds())
                        
                        # Agar 5 daqiqa ichida ro'yxatdan o'tgan bo'lsa
                        if time_diff <= 300:  # 5 minutes
                            risk_score = 40
                            
                            detection = {
                                'detection_type': 'time_pattern',
                                'severity': 'medium',
                                'risk_score': risk_score,
                                'description': f'Ikkala ishtirokchi {time_diff/60:.1f} daqiqa oralig\'ida ro\'yxatdan o\'tgan',
                                'involved_participants': [
                                    participant_ids[i],
                                    participant_ids[j]
                                ],
                                'evidence': {
                                    'time_diff_seconds': time_diff,
                                    'time_1': time1.isoformat(),
                                    'time_2': time2.isoformat(),
                                }
                            }
                            
                            results['detections'].append(detection)
                            results['risk_score'] += risk_score
            
            # Topshirish vaqtlarining o'xshashligi
            if len(submission_times) >= 2:
                participant_ids = list(submission_times.keys())
                
                for i in range(len(participant_ids)):
                    for j in range(i + 1, len(participant_ids)):
                        time1 = submission_times[participant_ids[i]]
                        time2 = submission_times[participant_ids[j]]
                        
                        # Vaqt farqi
                        time_diff = abs((time1 - time2).total_seconds())
                        
                        # Agar 10 daqiqa ichida topshirgan bo'lsa
                        if time_diff <= 600:  # 10 minutes
                            risk_score = 30
                            
                            detection = {
                                'detection_type': 'time_pattern',
                                'severity': 'medium',
                                'risk_score': risk_score,
                                'description': f'Ikkala ishtirokchi {time_diff/60:.1f} daqiqa oralig\'ida ariza topshirgan',
                                'involved_participants': [
                                    participant_ids[i],
                                    participant_ids[j]
                                ],
                                'evidence': {
                                    'time_diff_seconds': time_diff,
                                    'time_1': time1.isoformat(),
                                    'time_2': time2.isoformat(),
                                }
                            }
                            
                            results['detections'].append(detection)
                            results['risk_score'] += risk_score
            
            logger.info(f"Vaqt patternlari tahlili: {len(results['detections'])} ta xavf topildi")
            
        except Exception as e:
            logger.error(f"Vaqt patternlari tahlilida xatolik: {str(e)}")
        
        return results
    
    def _extract_participant_metadata(self, documents) -> Dict[str, Any]:
        """Ishtirokchi metadata sini ajratish"""
        metadata = {
            'software_used': set(),
            'creation_dates': [],
            'authors': set(),
            'file_sizes': [],
        }
        
        for doc in documents:
            # Dastur nomlari
            if doc.created_by_software:
                metadata['software_used'].add(doc.created_by_software)
            
            # Yaratilgan sanalar
            if doc.creation_date:
                metadata['creation_dates'].append(doc.creation_date)
            
            # Mualliflar
            if hasattr(doc, 'author') and doc.author:
                metadata['authors'].add(doc.author)
            
            # Fayl hajmlari
            if doc.file_size:
                metadata['file_sizes'].append(doc.file_size)
        
        # Set larni list ga o'tkazish
        metadata['software_used'] = list(metadata['software_used'])
        metadata['authors'] = list(metadata['authors'])
        
        return metadata
    
    def _calculate_metadata_similarity(self, metadata1: Dict, metadata2: Dict) -> float:
        """Metadata o'xshashligini hisoblash"""
        try:
            similarity_score = 0.0
            total_checks = 0
            
            # Dastur nomlari o'xshashligi
            software1 = set(metadata1.get('software_used', []))
            software2 = set(metadata2.get('software_used', []))
            
            if software1 and software2:
                software_similarity = len(software1 & software2) / len(software1 | software2)
                similarity_score += software_similarity
                total_checks += 1
            
            # Yaratilgan sanalar o'xshashligi
            dates1 = metadata1.get('creation_dates', [])
            dates2 = metadata2.get('creation_dates', [])
            
            if dates1 and dates2:
                # Eng yaqin sanalarni topish
                min_diff = float('inf')
                for date1 in dates1:
                    for date2 in dates2:
                        diff = abs((date1 - date2).total_seconds())
                        min_diff = min(min_diff, diff)
                
                # Agar 1 soat ichida yaratilgan bo'lsa
                if min_diff <= 3600:  # 1 hour
                    date_similarity = 1.0 - (min_diff / 3600)
                    similarity_score += date_similarity
                    total_checks += 1
            
            # Fayl hajmlari o'xshashligi
            sizes1 = metadata1.get('file_sizes', [])
            sizes2 = metadata2.get('file_sizes', [])
            
            if sizes1 and sizes2:
                avg_size1 = np.mean(sizes1)
                avg_size2 = np.mean(sizes2)
                
                if avg_size1 > 0 and avg_size2 > 0:
                    size_similarity = min(avg_size1, avg_size2) / max(avg_size1, avg_size2)
                    similarity_score += size_similarity
                    total_checks += 1
            
            # Umumiy o'xshashlik
            if total_checks > 0:
                return similarity_score / total_checks
            else:
                return 0.0
        
        except Exception as e:
            logger.error(f"Metadata o'xshashligini hisoblashda xatolik: {str(e)}")
            return 0.0
    
    def _find_shared_software(self, metadata1: Dict, metadata2: Dict) -> List[str]:
        """Umumiy ishlatilgan dasturlarni topish"""
        software1 = set(metadata1.get('software_used', []))
        software2 = set(metadata2.get('software_used', []))
        
        return list(software1 & software2)
    
    def _is_unnaturally_round(self, price: float, mean_price: float) -> bool:
        """Sun'iy yaxlitlangan narxni tekshirish"""
        try:
            # Narxning yaxlitlik darajasini tekshirish
            price_str = f"{price:.2f}"
            
            # Agar .00 yoki .50 bilan tugasa
            if price_str.endswith('.00') or price_str.endswith('.50'):
                return True
            
            # Agar 1000, 10000 kabi yaxlit sonlar bo'lsa
            if price % 1000 == 0:
                return True
            
            # Agar o'rtacha narxdan juda farq qilsa va yaxlit bo'lsa
            deviation = abs(price - mean_price) / mean_price if mean_price > 0 else 0
            if deviation >= 0.3 and (price % 100 == 0):
                return True
            
            return False
        
        except Exception as e:
            logger.error(f"Sun'iy yaxlitlangan narxni tekshirishda xatolik: {str(e)}")
            return False
    
    def _find_matching_phrases(self, text1: str, text2: str, min_length: int = 10) -> List[str]:
        """Mos keladigan iboralarni topish"""
        try:
            # Matnlarni so'zlarga bo'lish
            words1 = text1.lower().split()
            words2 = text2.lower().split()
            
            matching_phrases = []
            
            # 3-5 so'zli iboralarni tekshirish
            for phrase_length in range(3, 6):
                for i in range(len(words1) - phrase_length + 1):
                    phrase = ' '.join(words1[i:i + phrase_length])
                    
                    if phrase in text2.lower() and len(phrase) >= min_length:
                        matching_phrases.append(phrase)
            
            # Takrorlarni olib tashlash
            return list(set(matching_phrases))[:10]  # Eng ko'pi bilan 10 ta
        
        except Exception as e:
            logger.error(f"Mos keladigan iboralarni topishda xatolik: {str(e)}")
            return []
    
    def _calculate_ip_similarity(self, ip1: str, ip2: str) -> float:
        """IP manzillar o'xshashligini hisoblash"""
        try:
            # Bir xil IP
            if ip1 == ip2:
                return 1.0
            
            # Subnet o'xshashligi
            subnet1 = self._get_subnet(ip1)
            subnet2 = self._get_subnet(ip2)
            
            if subnet1 == subnet2:
                return 0.8
            
            # Birinchi 3 oktet o'xshashligi
            octets1 = ip1.split('.')
            octets2 = ip2.split('.')
            
            if len(octets1) >= 3 and len(octets2) >= 3:
                if octets1[0] == octets2[0] and octets1[1] == octets2[1] and octets1[2] == octets2[2]:
                    return 0.6
            
            return 0.0
        
        except Exception as e:
            logger.error(f"IP o'xshashligini hisoblashda xatolik: {str(e)}")
            return 0.0
    
    def _get_subnet(self, ip: str) -> str:
        """IP subnetini olish"""
        try:
            octets = ip.split('.')
            if len(octets) >= 3:
                return f"{octets[0]}.{octets[1]}.{octets[2]}.0/24"
            return ip
        except:
            return ip
    
    def _determine_risk_level(self, risk_score: float) -> str:
        """Xavf darajasini aniqlash"""
        if risk_score >= 200:
            return 'critical'
        elif risk_score >= 100:
            return 'high'
        elif risk_score >= 50:
            return 'medium'
        else:
            return 'low'
    
    def _generate_recommendations(self, detections: List[Dict[str, Any]]) -> List[str]:
        """Tavsiyalar generatsiya qilish"""
        recommendations = []
        
        detection_types = set([d['detection_type'] for d in detections])
        
        if 'metadata_similarity' in detection_types:
            recommendations.append(
                "Hujjatlari metadata jihatidan o'xshash ishtirokchilarni qo'shimcha tekshirish kerak"
            )
        
        if 'price_anomaly' in detection_types:
            recommendations.append(
                "Narx anomaliyalari bo'lgan ishtirokchilarning moliyaviy imkoniyatlarini tekshirish kerak"
            )
        
        if 'content_similarity' in detection_types:
            recommendations.append(
                "Taklif matnlari o'xshash ishtirokchilar o'rtasida aloqa borligini tekshirish kerak"
            )
        
        if 'ip_similarity' in detection_types:
            recommendations.append(
                "Bir xil IP manzildan ro'yxatdan o'tgan ishtirokchilarni tekshirish kerak"
            )
        
        if 'time_pattern' in detection_types:
            recommendations.append(
                "Bir vaqtda ro'yxatdan o'tgan yoki ariza topshirgan ishtirokchilarni tekshirish kerak"
            )
        
        return recommendations
    
    def _calculate_participant_risks(self, detections: List[Dict[str, Any]], participants) -> Dict[int, Dict[str, Any]]:
        """Har bir ishtirokchi uchun xavf ballini hisoblash"""
        participant_risks = {}
        
        # Barcha ishtirokchilar uchun boshlang'ich qiymatlar
        for participant in participants:
            participant_risks[participant.id] = {
                'participant_id': participant.id,
                'company_name': participant.participant.company_name,
                'total_risk_score': 0.0,
                'risk_level': 'low',
                'detection_count': 0,
                'detection_types': set(),
            }
        
        # Har bir aniqlash uchun ishtirokchilarning xavf ballini yangilash
        for detection in detections:
            risk_score = detection['risk_score']
            detection_type = detection['detection_type']
            
            # Tashkilot etilgan ishtirokchilar
            if 'participant_id' in detection:
                participant_id = detection['participant_id']
                if participant_id in participant_risks:
                    participant_risks[participant_id]['total_risk_score'] += risk_score
                    participant_risks[participant_id]['detection_count'] += 1
                    participant_risks[participant_id]['detection_types'].add(detection_type)
            
            # Bir nechta ishtirokchilar ishtirok etgan
            elif 'involved_participants' in detection:
                for participant_id in detection['involved_participants']:
                    if participant_id in participant_risks:
                        participant_risks[participant_id]['total_risk_score'] += risk_score
                        participant_risks[participant_id]['detection_count'] += 1
                        participant_risks[participant_id]['detection_types'].add(detection_type)
        
        # Xavf darajasini aniqlash va set ni list ga o'tkazish
        for participant_id, risk_data in participant_risks.items():
            risk_data['risk_level'] = self._determine_risk_level(risk_data['total_risk_score'])
            risk_data['detection_types'] = list(risk_data['detection_types'])
        
        return participant_risks


# Global xizmat
anti_fraud_analyzer = AntiFraudAnalyzer()
