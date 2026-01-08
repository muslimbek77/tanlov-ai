from django.db import models
from django.contrib.auth.models import User
from apps.tenders.models import Tender
from pgvector.django import VectorField


class Participant(models.Model):
    STATUS_CHOICES = [
        ('active', 'Faol'),
        ('inactive', 'Faol emas'),
        ('blacklisted', 'Qora ro\'yxatda'),
    ]
    
    COMPANY_TYPES = [
        ('llc', 'MChJ'),
        ('jsc', 'AJ'),
        ('ie', 'Yuridik shaxs bo\'lmagan tadbirkor'),
        ('state', 'Davlat korxonasi'),
        ('foreign', 'Xorijiy kompaniya'),
    ]
    
    # Asosiy ma'lumotlar
    company_name = models.CharField(max_length=300, verbose_name='Kompaniya nomi')
    company_type = models.CharField(max_length=20, choices=COMPANY_TYPES, verbose_name='Kompaniya turi')
    tax_identification_number = models.CharField(max_length=20, unique=True, verbose_name='INN/STIR')
    registration_number = models.CharField(max_length=50, unique=True, verbose_name='Ro\'yxatdan o\'tish raqami')
    
    # Kontakt ma'lumotlari
    legal_address = models.TextField(verbose_name='Yuridik manzil')
    actual_address = models.TextField(verbose_name='Haqiqiy manzil')
    phone = models.CharField(max_length=20, verbose_name='Telefon')
    email = models.EmailField(verbose_name='Email')
    website = models.URLField(null=True, blank=True, verbose_name='Veb-sayt')
    
    # Raxbariyat
    director_name = models.CharField(max_length=200, verbose_name='Direktor F.I.O.')
    director_phone = models.CharField(max_length=20, verbose_name='Direktor telefoni')
    director_email = models.EmailField(verbose_name='Direktor emaili')
    
    # Status va reyting
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', verbose_name='Holati')
    trust_score = models.DecimalField(max_digits=5, decimal_places=2, default=50.00, verbose_name='Ishonch reytingi')
    
    # Hujjatlar
    registration_certificate = models.FileField(upload_to='participants/certificates/', null=True, blank=True, verbose_name='Ro\'yxatdan o\'tish guvohnomasi')
    tax_certificate = models.FileField(upload_to='participants/tax/', null=True, blank=True, verbose_name='Soliq to\'lov sertifikati')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Ishtirokchi'
        verbose_name_plural = 'Ishtirokchilar'
        ordering = ['company_name']
    
    def __str__(self):
        return self.company_name


class TenderParticipant(models.Model):
    STATUS_CHOICES = [
        ('registered', 'Ro\'yxatdan o\'tgan'),
        ('submitted', 'Ariza topshirgan'),
        ('qualified', 'Saralangan'),
        ('disqualified', 'Saralashdan o\'tmagan'),
        ('winner', 'G\'olib'),
        ('withdrawn', 'Chekinagan'),
    ]
    
    tender = models.ForeignKey(Tender, on_delete=models.CASCADE, related_name='participants')
    participant = models.ForeignKey(Participant, on_delete=models.CASCADE, related_name='tender_participations')
    
    # Ariza ma'lumotlari
    registration_date = models.DateTimeField(auto_now_add=True, verbose_name='Ro\'yxatdan o\'tish vaqti')
    submission_date = models.DateTimeField(null=True, blank=True, verbose_name='Ariza topshirish vaqti')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='registered', verbose_name='Holati')
    
    # Taklif ma'lumotlari
    proposed_price = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, verbose_name='Taklif etilgan narx')
    currency = models.CharField(max_length=10, default='UZS', verbose_name='Valyuta')
    delivery_time = models.IntegerField(null=True, blank=True, verbose_name='Yetkazib berish muddati (kun)')
    warranty_period = models.IntegerField(null=True, blank=True, verbose_name='Kafolat muddati (oy)')
    
    # Hujjatlar
    proposal_document = models.FileField(upload_to='proposals/', null=True, blank=True, verbose_name='Taklif hujjati')
    financial_document = models.FileField(upload_to='proposals/financial/', null=True, blank=True, verbose_name='Moliyaviy hujjat')
    technical_document = models.FileField(upload_to='proposals/technical/', null=True, blank=True, verbose_name='Texnik hujjat')
    
    # Vektorli ma'lumotlar
    proposal_vector = VectorField(dimensions=1536, null=True, blank=True, verbose_name='Taklif vektori')
    
    # Metadata
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name='IP manzil')
    user_agent = models.TextField(null=True, blank=True, verbose_name='User Agent')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Tender ishtirokchisi'
        verbose_name_plural = 'Tender ishtirokchilari'
        unique_together = ['tender', 'participant']
        ordering = ['-registration_date']
    
    def __str__(self):
        return f"{self.tender.tender_number} - {self.participant.company_name}"


class ParticipantDocument(models.Model):
    DOCUMENT_TYPES = [
        ('proposal', 'Taklif hujjati'),
        ('financial', 'Moliyaviy hujjat'),
        ('technical', 'Texnik hujjat'),
        ('certificate', 'Sertifikat'),
        ('experience', 'Tajriba hujjati'),
        ('other', 'Boshqa hujjat'),
    ]
    
    tender_participant = models.ForeignKey(TenderParticipant, on_delete=models.CASCADE, related_name='documents')
    title = models.CharField(max_length=300, verbose_name='Hujjat nomi')
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPES, verbose_name='Hujjat turi')
    file = models.FileField(upload_to='participants/documents/', verbose_name='Hujjat fayli')
    
    # Metadata
    file_size = models.BigIntegerField(verbose_name='Fayl hajmi (bayt)')
    file_type = models.CharField(max_length=50, verbose_name='Fayl turi')
    page_count = models.IntegerField(null=True, blank=True, verbose_name='Sahifalar soni')
    
    # OCR va strukturalash
    extracted_text = models.TextField(null=True, blank=True, verbose_name='Ajratilgan matn')
    is_processed = models.BooleanField(default=False, verbose_name='Ishlov berildi')
    
    # Metadata audit
    created_by_software = models.CharField(max_length=200, null=True, blank=True, verbose_name='Yaratilgan dastur')
    creation_date = models.DateTimeField(null=True, blank=True, verbose_name='Yaratilgan sana')
    last_modified = models.DateTimeField(null=True, blank=True, verbose_name='Oxirgi o\'zgartirish')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Ishtirokchi hujjati'
        verbose_name_plural = 'Ishtirokchi hujjatlari'
    
    def __str__(self):
        return f"{self.tender_participant.participant.company_name} - {self.title}"
