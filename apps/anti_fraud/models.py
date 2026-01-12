from django.db import models
from django.conf import settings
from apps.tenders.models import Tender
from apps.participants.models import TenderParticipant


class FraudDetection(models.Model):
    DETECTION_TYPES = [
        ('metadata_similarity', 'Metadata o\'xshashligi'),
        ('price_anomaly', 'Narx anomaliyasi'),
        ('content_similarity', 'Matn o\'xshashligi'),
        ('ip_similarity', 'IP manzil o\'xshashligi'),
        ('time_pattern', 'Vaqt patterni'),
        ('document_pattern', 'Hujjat patterni'),
    ]
    
    SEVERITY_LEVELS = [
        ('low', 'Past'),
        ('medium', 'O\'rta'),
        ('high', 'Yuqori'),
        ('critical', 'Tanqidiy'),
    ]
    
    STATUS_CHOICES = [
        ('detected', 'Aniqlangan'),
        ('reviewing', 'Ko\'rib chiqilmoqda'),
        ('confirmed', 'Tasdiqlangan'),
        ('false_positive', 'Xato signal'),
        ('resolved', 'Hal qilingan'),
    ]
    
    tender = models.ForeignKey(Tender, on_delete=models.CASCADE, related_name='fraud_detections')
    detection_type = models.CharField(max_length=30, choices=DETECTION_TYPES, verbose_name='Aniqlash turi')
    severity = models.CharField(max_length=20, choices=SEVERITY_LEVELS, verbose_name='Jiddiylik darajasi')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='detected', verbose_name='Holati')
    
    # Tavsif
    title = models.CharField(max_length=500, verbose_name='Sarlavha')
    description = models.TextField(verbose_name='Tavsif')
    risk_score = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='Xavf balli')
    
    # Ishhtirokchilar
    involved_participants = models.ManyToManyField(TenderParticipant, related_name='fraud_cases')
    
    # Tahlil ma'lumotlari
    detection_data = models.JSONField(default=dict, verbose_name='Aniqlash ma\'lumotlari')
    evidence = models.JSONField(default=list, verbose_name='Dalillar')
    
    # Tekshiruv
    reviewer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Tekshiruvchi')
    review_notes = models.TextField(null=True, blank=True, verbose_name='Tekshiruv izohlari')
    reviewed_at = models.DateTimeField(null=True, blank=True, verbose_name='Tekshirilgan vaqt')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Korrupsiya aniqlash'
        verbose_name_plural = 'Korrupsiya aniqlashlar'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.tender.tender_number} - {self.title}"


class MetadataAnalysis(models.Model):
    tender_participant = models.ForeignKey(TenderParticipant, on_delete=models.CASCADE, related_name='metadata_analyses')
    
    # PDF metadata
    created_by_software = models.CharField(max_length=200, null=True, blank=True, verbose_name='Yaratilgan dastur')
    creation_date = models.DateTimeField(null=True, blank=True, verbose_name='Yaratilgan sana')
    last_modified = models.DateTimeField(null=True, blank=True, verbose_name='Oxirgi o\'zgartirish')
    author = models.CharField(max_length=200, null=True, blank=True, verbose_name='Muallif')
    
    # Texnik metadata
    file_size = models.BigIntegerField(verbose_name='Fayl hajmi')
    page_count = models.IntegerField(null=True, blank=True, verbose_name='Sahifalar soni')
    word_count = models.IntegerField(null=True, blank=True, verbose_name='So\'zlar soni')
    
    # Xavf ko'rsatkichlari
    similarity_score = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, verbose_name='O\'xshashlik balli')
    risk_level = models.CharField(max_length=20, choices=FraudDetection.SEVERITY_LEVELS, default='low', verbose_name='Xavf darajasi')
    
    # Tahlil
    analysis_result = models.JSONField(default=dict, verbose_name='Tahlil natijalari')
    flags = models.JSONField(default=list, verbose_name='Bayroqlar')
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Metadata tahlili'
        verbose_name_plural = 'Metadata tahlillari'
    
    def __str__(self):
        return f"{self.tender_participant.participant.company_name} - Metadata"


class PriceAnomalyDetection(models.Model):
    ANOMALY_TYPES = [
        ('too_low', 'Juda past narx'),
        ('too_high', 'Juda yuqori narx'),
        ('unnatural_round', 'Sun\'iy yaxlitlangan narx'),
        ('suspicious_pattern', 'Shubhali pattern'),
        ('market_deviation', 'Bozordan chetlanish'),
    ]
    
    tender = models.ForeignKey(Tender, on_delete=models.CASCADE, related_name='price_anomalies')
    tender_participant = models.ForeignKey(TenderParticipant, on_delete=models.CASCADE, related_name='price_anomalies')
    
    anomaly_type = models.CharField(max_length=30, choices=ANOMALY_TYPES, verbose_name='Anomaliya turi')
    
    # Narx ma'lumotlari
    proposed_price = models.DecimalField(max_digits=15, decimal_places=2, verbose_name='Taklif etilgan narx')
    expected_price = models.DecimalField(max_digits=15, decimal_places=2, verbose_name='Kutilgan narx')
    market_price = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, verbose_name='Bozor narxi')
    
    # Deviation
    deviation_percentage = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='Chetlanish foizi')
    z_score = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='Z-score')
    risk_score = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='Xavf balli')
    
    # Tahlil
    analysis_data = models.JSONField(default=dict, verbose_name='Tahlil ma\'lumotlari')
    recommendation = models.TextField(verbose_name='Tavsiya')
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Narx anomaliyasi'
        verbose_name_plural = 'Narx anomaliyalari'
    
    def __str__(self):
        return f"{self.tender_participant.participant.company_name} - {self.anomaly_type}"


class SimilarityAnalysis(models.Model):
    SIMILARITY_TYPES = [
        ('content', 'Matn mazmuni'),
        ('structure', 'Hujjat tuzilishi'),
        ('formatting', 'Formatlash'),
        ('language', 'Til uslubi'),
        ('tables', 'Jadvallar'),
    ]
    
    tender = models.ForeignKey(Tender, on_delete=models.CASCADE, related_name='similarity_analyses')
    participant_1 = models.ForeignKey(TenderParticipant, on_delete=models.CASCADE, related_name='similarity_as_p1')
    participant_2 = models.ForeignKey(TenderParticipant, on_delete=models.CASCADE, related_name='similarity_as_p2')
    
    similarity_type = models.CharField(max_length=20, choices=SIMILARITY_TYPES, verbose_name='O\'xshashlik turi')
    similarity_score = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='O\'xshashlik balli')
    
    # Tahlil ma'lumotlari
    compared_sections = models.JSONField(default=list, verbose_name='Solishtirilgan bo\'limlar')
    matching_phrases = models.JSONField(default=list, verbose_name='Mos keladigan iboralar')
    structural_similarity = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name='Strukturaviy o\'xshashlik')
    
    # Xavf
    risk_level = models.CharField(max_length=20, choices=FraudDetection.SEVERITY_LEVELS, default='low', verbose_name='Xavf darajasi')
    is_suspicious = models.BooleanField(default=False, verbose_name='Shubhali')
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'O\'xshashlik tahlili'
        verbose_name_plural = 'O\'xshashlik tahlillari'
        unique_together = ['participant_1', 'participant_2', 'similarity_type']
    
    def __str__(self):
        return f"{self.participant_1.participant.company_name} vs {self.participant_2.participant.company_name}"


class FraudDetectionRule(models.Model):
    RULE_TYPES = [
        ('metadata', 'Metadata qoidasi'),
        ('price', 'Narx qoidasi'),
        ('similarity', 'O\'xshashlik qoidasi'),
        ('time', 'Vaqt qoidasi'),
        ('behavior', 'Xulq-atvor qoidasi'),
    ]
    
    name = models.CharField(max_length=200, verbose_name='Qoida nomi')
    rule_type = models.CharField(max_length=20, choices=RULE_TYPES, verbose_name='Qoida turi')
    description = models.TextField(verbose_name='Tavsif')
    
    # Qoida parametrlari
    conditions = models.JSONField(default=dict, verbose_name='Shartlar')
    threshold = models.DecimalField(max_digits=5, decimal_places=2, verbose_name=' chegarasi')
    severity = models.CharField(max_length=20, choices=FraudDetection.SEVERITY_LEVELS, verbose_name='Jiddiylik darajasi')
    
    # Status
    is_active = models.BooleanField(default=True, verbose_name='Faol')
    priority = models.IntegerField(default=1, verbose_name='Prioritet')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Korrupsiya aniqlash qoidasi'
        verbose_name_plural = 'Korrupsiya aniqlash qoidalari'
        ordering = ['-priority', 'name']
    
    def __str__(self):
        return self.name
