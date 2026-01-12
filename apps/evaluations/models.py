from django.db import models
from django.conf import settings
from apps.tenders.models import Tender
from apps.participants.models import TenderParticipant


class Evaluation(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Kutilmoqda'),
        ('in_progress', 'Jarayonda'),
        ('completed', 'Yakunlangan'),
        ('failed', 'Xatolik'),
    ]
    
    tender = models.ForeignKey(Tender, on_delete=models.CASCADE, related_name='evaluations')
    evaluator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, verbose_name='Baholovchi')
    
    # Baholash jarayoni
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='Holati')
    started_at = models.DateTimeField(null=True, blank=True, verbose_name='Boshlanish vaqti')
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name='Tugash vaqti')
    
    # Umumiy natijalar
    total_participants = models.IntegerField(default=0, verbose_name='Jami ishtirokchilar')
    qualified_participants = models.IntegerField(default=0, verbose_name='Saralangan ishtirokchilar')
    disqualified_participants = models.IntegerField(default=0, verbose_name='Saralashdan o\'tmaganlar')
    
    # Xavf ko'rsatkichlari
    high_risk_count = models.IntegerField(default=0, verbose_name='Yuqori xavfli ishtirokchilar')
    medium_risk_count = models.IntegerField(default=0, verbose_name="O'rta xavfli ishtirokchilar")
    low_risk_count = models.IntegerField(default=0, verbose_name='Past xavfli ishtirokchilar')
    
    # Yaratilgan sabablari
    reasoning = models.TextField(null=True, blank=True, verbose_name='Baholash sabablari')
    ai_analysis = models.TextField(null=True, blank=True, verbose_name='AI tahlili')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Baholash'
        verbose_name_plural = 'Baholashlar'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.tender.tender_number} - Baholash"


class ParticipantScore(models.Model):
    RISK_LEVELS = [
        ('low', 'Past xavf'),
        ('medium', 'O\'rta xavf'),
        ('high', 'Yuqori xavf'),
        ('critical', 'Tanqidiy xavf'),
    ]
    
    evaluation = models.ForeignKey(Evaluation, on_delete=models.CASCADE, related_name='participant_scores')
    tender_participant = models.ForeignKey(TenderParticipant, on_delete=models.CASCADE, related_name='scores')
    
    # Ballar (100 ballik tizim)
    total_score = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='Jami ball')
    compliance_score = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='Compliance balli')
    financial_score = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='Moliyaviy ball')
    technical_score = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='Texnik ball')
    experience_score = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='Tajriba balli')
    
    # Xavf darajasi
    risk_level = models.CharField(max_length=20, choices=RISK_LEVELS, default='low', verbose_name='Xavf darajasi')
    risk_score = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, verbose_name='Xavf balli')
    
    # Red flags
    red_flags = models.JSONField(default=list, verbose_name='Xavf belgilari')
    warnings = models.JSONField(default=list, verbose_name='Ogohlantirishlar')
    
    # Sabablari
    score_reasoning = models.TextField(verbose_name='Ball berish sabablari')
    risk_reasoning = models.TextField(null=True, blank=True, verbose_name='Xavf sabablari')
    
    # Reytinq
    rank = models.IntegerField(null=True, blank=True, verbose_name='O\'rni')
    is_winner = models.BooleanField(default=False, verbose_name='G\'olib')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Ishtirokchi balli'
        verbose_name_plural = 'Ishtirokchi ballari'
        unique_together = ['evaluation', 'tender_participant']
        ordering = ['-total_score']
    
    def __str__(self):
        return f"{self.tender_participant.participant.company_name} - {self.total_score}"


class ScoreDetail(models.Model):
    SCORE_TYPES = [
        ('compliance', 'Compliance'),
        ('financial', 'Moliyaviy'),
        ('technical', 'Texnik'),
        ('experience', 'Tajriba'),
        ('price', 'Narx'),
        ('delivery', 'Yetkazib berish'),
        ('warranty', 'Kafolat'),
    ]
    
    participant_score = models.ForeignKey(ParticipantScore, on_delete=models.CASCADE, related_name='score_details')
    score_type = models.CharField(max_length=20, choices=SCORE_TYPES, verbose_name='Ball turi')
    
    # Ball ma'lumotlari
    max_score = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='Maksimal ball')
    achieved_score = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='Erishilgan ball')
    percentage = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='Foiz')
    
    # Tahlil
    analysis = models.TextField(verbose_name='Tahlil')
    reasoning = models.TextField(verbose_name='Sabablari')
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Ball tafsilotlari'
        verbose_name_plural = 'Ball tafsilotlari'
        unique_together = ['participant_score', 'score_type']
    
    def __str__(self):
        return f"{self.participant_score.tender_participant.participant.company_name} - {self.score_type}"


class EvaluationLog(models.Model):
    LOG_TYPES = [
        ('info', 'Ma\'lumot'),
        ('warning', 'Ogohlantirish'),
        ('error', 'Xatolik'),
        ('fraud_detected', 'Korrupsiya aniqlandi'),
        ('compliance_issue', 'Compliance muammosi'),
    ]
    
    evaluation = models.ForeignKey(Evaluation, on_delete=models.CASCADE, related_name='logs')
    log_type = models.CharField(max_length=20, choices=LOG_TYPES, verbose_name='Log turi')
    message = models.TextField(verbose_name='Xabar')
    details = models.JSONField(default=dict, verbose_name='Tafsilotlar')
    
    # Agent ma'lumotlari
    agent_name = models.CharField(max_length=100, verbose_name='Agent nomi')
    agent_type = models.CharField(max_length=50, verbose_name='Agent turi')
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Baholash logi'
        verbose_name_plural = 'Baholash loglari'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.evaluation.tender.tender_number} - {self.log_type}"


class TenderAnalysisResult(models.Model):
    """
    Tender tahlil natijalarini saqlash uchun model.
    Frontend'dan kelgan tahlil natijalarini bazaga saqlaydi.
    """
    
    # Tender ma'lumotlari
    tender_name = models.CharField(max_length=500, verbose_name='Tender nomi')
    tender_type = models.CharField(max_length=100, null=True, blank=True, verbose_name='Tender turi')
    tender_data = models.JSONField(default=dict, verbose_name='Tender tahlili')
    
    # Ishtirokchilar tahlili
    participants = models.JSONField(default=list, verbose_name='Ishtirokchilar tahlili')
    participant_count = models.IntegerField(default=0, verbose_name='Ishtirokchilar soni')
    
    # Natijalar
    ranking = models.JSONField(default=list, verbose_name='Reyting')
    winner_name = models.CharField(max_length=255, null=True, blank=True, verbose_name='G\'olib')
    winner_score = models.FloatField(null=True, blank=True, verbose_name='G\'olib balli')
    summary = models.TextField(null=True, blank=True, verbose_name='Xulosa')
    
    # Meta
    language = models.CharField(max_length=10, default='uz', verbose_name='Til')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Yaratilgan vaqt')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Yangilangan vaqt')
    
    class Meta:
        verbose_name = 'Tender tahlil natijasi'
        verbose_name_plural = 'Tender tahlil natijalari'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.tender_name} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"

