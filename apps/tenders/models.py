from django.db import models
from django.contrib.auth.models import User
from pgvector.django import VectorField


class Tender(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Qoralama'),
        ('active', 'Faol'),
        ('evaluation', 'Baholash'),
        ('completed', 'Yakunlangan'),
        ('cancelled', 'Bekor qilingan'),
    ]
    
    TYPE_CHOICES = [
        ('open', 'Ochiq tender'),
        ('closed', 'Yopiq tender'),
        ('two_stage', 'Ikki bosqichli tender'),
    ]
    
    title = models.CharField(max_length=500, verbose_name='Tender nomi')
    description = models.TextField(verbose_name='Tender tavsifi')
    tender_number = models.CharField(max_length=100, unique=True, verbose_name='Tender raqami')
    organization = models.CharField(max_length=300, verbose_name='Tashkilot')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', verbose_name='Holati')
    tender_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='open', verbose_name='Tender turi')
    
    # Moliyaviy ma'lumotlar
    estimated_budget = models.DecimalField(max_digits=15, decimal_places=2, verbose_name='Taxminiy byudjet')
    currency = models.CharField(max_length=10, default='UZS', verbose_name='Valyuta')
    
    # Vaqt ma'lumotlari
    start_date = models.DateTimeField(verbose_name='Boshlanish vaqti')
    end_date = models.DateTimeField(verbose_name='Tugash vaqti')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Hujjatlar
    requirements_document = models.FileField(upload_to='tenders/requirements/', null=True, blank=True, verbose_name='Talablar hujjati')
    technical_specification = models.FileField(upload_to='tenders/technical/', null=True, blank=True, verbose_name='Texnik spetsifikatsiya')
    
    # Vektorli ma'lumotlar RAG uchun
    requirements_vector = VectorField(dimensions=1536, null=True, blank=True, verbose_name='Talablar vektori')
    
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name='Yaratuvchi')
    
    class Meta:
        verbose_name = 'Tender'
        verbose_name_plural = 'Tenderlar'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.tender_number} - {self.title}"


class TenderDocument(models.Model):
    DOCUMENT_TYPES = [
        ('requirements', 'Talablar hujjati'),
        ('technical', 'Texnik spetsifikatsiya'),
        ('financial', 'Moliyaviy hujjat'),
        ('other', 'Boshqa hujjat'),
    ]
    
    tender = models.ForeignKey(Tender, on_delete=models.CASCADE, related_name='documents')
    title = models.CharField(max_length=300, verbose_name='Hujjat nomi')
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPES, verbose_name='Hujjat turi')
    file = models.FileField(upload_to='tenders/documents/', verbose_name='Hujjat fayli')
    
    # Metadata
    file_size = models.BigIntegerField(verbose_name='Fayl hajmi (bayt)')
    file_type = models.CharField(max_length=50, verbose_name='Fayl turi')
    page_count = models.IntegerField(null=True, blank=True, verbose_name='Sahifalar soni')
    
    # OCR va strukturalash
    extracted_text = models.TextField(null=True, blank=True, verbose_name='Ajratilgan matn')
    is_processed = models.BooleanField(default=False, verbose_name='Ishlov berildi')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Tender hujjati'
        verbose_name_plural = 'Tender hujjatlari'
    
    def __str__(self):
        return f"{self.tender.tender_number} - {self.title}"


class TenderRequirement(models.Model):
    REQUIREMENT_TYPES = [
        ('technical', 'Texnik talab'),
        ('financial', 'Moliyaviy talab'),
        ('legal', 'Huquqiy talab'),
        ('experience', 'Tajriba talabi'),
        ('certification', 'Sertifikat talabi'),
    ]
    
    tender = models.ForeignKey(Tender, on_delete=models.CASCADE, related_name='requirements')
    title = models.CharField(max_length=500, verbose_name='Talab nomi')
    description = models.TextField(verbose_name='Talab tavsifi')
    requirement_type = models.CharField(max_length=20, choices=REQUIREMENT_TYPES, verbose_name='Talab turi')
    
    # Baholash uchun
    weight = models.DecimalField(max_digits=5, decimal_places=2, default=1.00, verbose_name='Vazni')
    max_score = models.DecimalField(max_digits=5, decimal_places=2, default=10.00, verbose_name='Maksimal ball')
    is_mandatory = models.BooleanField(default=False, verbose_name='Majburiy')
    
    # Vektorli ma'lumotlar
    requirement_vector = VectorField(dimensions=1536, null=True, blank=True, verbose_name='Talab vektori')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Tender talabi'
        verbose_name_plural = 'Tender talablari'
    
    def __str__(self):
        return f"{self.tender.tender_number} - {self.title}"
