from django.db import models
from django.contrib.auth.models import User
from apps.tenders.models import Tender
from apps.participants.models import TenderParticipant


class ComplianceRule(models.Model):
    RULE_TYPES = [
        ('legal', 'Huquqiy qoida'),
        ('technical', 'Texnik qoida'),
        ('financial', 'Moliyaviy qoida'),
        ('document', 'Hujjat qoidasi'),
        ('qualification', 'Malaka qoidasi'),
    ]
    
    SEVERITY_LEVELS = [
        ('low', 'Past'),
        ('medium', 'O\'rta'),
        ('high', 'Yuqori'),
        ('critical', 'Tanqidiy'),
    ]
    
    # Normativ hujjatlar
    REGULATION_TYPES = [
        ('orq_684', 'O\'RQ-684'),
        ('orq_585', 'O\'RQ-585'),
        ('orq_437', 'O\'RQ-437'),
        ('government_decree', 'Hukumat qarori'),
        ('ministry_regulation', 'Vazirlik qoidasi'),
        ('internal', 'Ichki qoida'),
    ]
    
    name = models.CharField(max_length=300, verbose_name='Qoida nomi')
    rule_type = models.CharField(max_length=20, choices=RULE_TYPES, verbose_name='Qoida turi')
    regulation_type = models.CharField(max_length=30, choices=REGULATION_TYPES, verbose_name='Normativ hujjat turi')
    regulation_number = models.CharField(max_length=100, verbose_name='Normativ hujjat raqami')
    
    # Tavsif
    description = models.TextField(verbose_name='Tavsif')
    requirement = models.TextField(verbose_name='Talab')
    penalty_description = models.TextField(null=True, blank=True, verbose_name='Jarima tavsifi')
    
    # Qoida parametrlari
    severity = models.CharField(max_length=20, choices=SEVERITY_LEVELS, verbose_name='Jiddiylik darajasi')
    is_mandatory = models.BooleanField(default=True, verbose_name='Majburiy')
    validation_rules = models.JSONField(default=dict, verbose_name='Validatsiya qoidalari')
    
    # Status
    is_active = models.BooleanField(default=True, verbose_name='Faol')
    effective_date = models.DateField(verbose_name='Kuchga kirish sanasi')
    expiry_date = models.DateField(null=True, blank=True, verbose_name='Amal qilish muddati')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Compliance qoidasi'
        verbose_name_plural = 'Compliance qoidalari'
        ordering = ['regulation_type', 'name']
    
    def __str__(self):
        return f"{self.regulation_type} - {self.name}"


class ComplianceCheck(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Kutilmoqda'),
        ('in_progress', 'Jarayonda'),
        ('passed', 'O\'tdi'),
        ('failed', 'O\'tmadi'),
        ('warning', 'Ogohlantirish'),
        ('error', 'Xatolik'),
    ]
    
    tender = models.ForeignKey(Tender, on_delete=models.CASCADE, related_name='compliance_checks')
    tender_participant = models.ForeignKey(TenderParticipant, on_delete=models.CASCADE, related_name='compliance_checks')
    rule = models.ForeignKey(ComplianceRule, on_delete=models.CASCADE, related_name='checks')
    
    # Natijalar
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='Holati')
    score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name='Ball')
    max_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name='Maksimal ball')
    
    # Tahlil
    check_result = models.JSONField(default=dict, verbose_name='Tekshirish natijasi')
    evidence = models.JSONField(default=list, verbose_name='Dalillar')
    violations = models.JSONField(default=list, verbose_name='Buzilishlar')
    
    # Izohlar
    findings = models.TextField(verbose_name='Topilmalar')
    recommendations = models.TextField(null=True, blank=True, verbose_name='Tavsiyalar')
    
    # Tekshiruv ma'lumotlari
    checked_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Tekshirgan')
    checked_at = models.DateTimeField(null=True, blank=True, verbose_name='Tekshirilgan vaqt')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Compliance tekshiruvi'
        verbose_name_plural = 'Compliance tekshiruvlari'
        unique_together = ['tender_participant', 'rule']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.tender_participant.participant.company_name} - {self.rule.name}"


class ComplianceReport(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Qoralama'),
        ('review', 'Ko\'rib chiqish'),
        ('approved', 'Tasdiqlangan'),
        ('rejected', 'Rad etilgan'),
    ]
    
    tender = models.ForeignKey(Tender, on_delete=models.CASCADE, related_name='compliance_reports')
    
    # Hisobot ma'lumotlari
    report_number = models.CharField(max_length=100, unique=True, verbose_name='Hisobot raqami')
    title = models.CharField(max_length=500, verbose_name='Hisobot nomi')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', verbose_name='Holati')
    
    # Xulosa
    total_checks = models.IntegerField(default=0, verbose_name='Jami tekshiruvlar')
    passed_checks = models.IntegerField(default=0, verbose_name='O\'tgan tekshiruvlar')
    failed_checks = models.IntegerField(default=0, verbose_name='O\'tmagan tekshiruvlar')
    warning_checks = models.IntegerField(default=0, verbose_name='Ogohlantirishlar')
    
    # Ballar
    overall_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name='Umumiy ball')
    max_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name='Maksimal ball')
    compliance_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name='Compliance foizi')
    
    # Muhim topilmalar
    critical_violations = models.JSONField(default=list, verbose_name='Tanqidiy buzilishlar')
    major_violations = models.JSONField(default=list, verbose_name='Asosiy buzilishlar')
    minor_violations = models.JSONField(default=list, verbose_name='Kichik buzilishlar')
    
    # Tavsiyalar
    recommendations = models.TextField(verbose_name='Tavsiyalar')
    corrective_actions = models.TextField(null=True, blank=True, verbose_name='Tuzatish choralari')
    
    # Tasdiq
    prepared_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='prepared_reports', verbose_name='Tayyorlovchi')
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_reports', verbose_name='Tasdiqlovchi')
    approved_at = models.DateTimeField(null=True, blank=True, verbose_name='Tasdiqlangan vaqt')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Compliance hisoboti'
        verbose_name_plural = 'Compliance hisobotlari'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.tender.tender_number} - {self.report_number}"


class DocumentCompliance(models.Model):
    DOCUMENT_TYPES = [
        ('proposal', 'Taklif hujjati'),
        ('financial', 'Moliyaviy hujjat'),
        ('technical', 'Texnik hujjat'),
        ('certificate', 'Sertifikat'),
        ('license', 'Litsenziya'),
        ('experience', 'Tajriba hujjati'),
    ]
    
    tender_participant = models.ForeignKey(TenderParticipant, on_delete=models.CASCADE, related_name='document_compliances')
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPES, verbose_name='Hujjat turi')
    
    # Hujjat talablari
    required_sections = models.JSONField(default=list, verbose_name='Talab qilinadigan bo\'limlar')
    mandatory_fields = models.JSONField(default=list, verbose_name='Majburiy maydonlar')
    format_requirements = models.JSONField(default=dict, verbose_name='Format talablari')
    
    # Tekshirish natijalari
    is_present = models.BooleanField(default=False, verbose_name='Mavjud')
    is_valid = models.BooleanField(default=False, verbose_name='Yaroqli')
    is_complete = models.BooleanField(default=False, verbose_name='To\'liq')
    
    # Tahlil
    missing_sections = models.JSONField(default=list, verbose_name='Yo\'q bo\'limlar')
    invalid_fields = models.JSONField(default=list, verbose_name='Yaroqsiz maydonlar')
    format_issues = models.JSONField(default=list, verbose_name='Format muammolari')
    
    # Ball
    compliance_score = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, verbose_name='Compliance balli')
    max_score = models.DecimalField(max_digits=5, decimal_places=2, default=10.00, verbose_name='Maksimal ball')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Hujjat compliance'
        verbose_name_plural = 'Hujjat compliancelari'
        unique_together = ['tender_participant', 'document_type']
    
    def __str__(self):
        return f"{self.tender_participant.participant.company_name} - {self.document_type}"


class ComplianceTemplate(models.Model):
    TEMPLATE_TYPES = [
        ('tender', 'Tender shabloni'),
        ('proposal', 'Taklif shabloni'),
        ('contract', 'Shartnoma shabloni'),
        ('report', 'Hisobot shabloni'),
    ]
    
    name = models.CharField(max_length=300, verbose_name='Shablon nomi')
    template_type = models.CharField(max_length=20, choices=TEMPLATE_TYPES, verbose_name='Shablon turi')
    description = models.TextField(verbose_name='Tavsif')
    
    # Shablon tarkibi
    required_sections = models.JSONField(default=list, verbose_name='Talab qilinadigan bo\'limlar')
    field_validations = models.JSONField(default=dict, verbose_name='Maydon validatsiyalari')
    compliance_rules = models.JSONField(default=list, verbose_name='Compliance qoidalari')
    
    # Fayl
    template_file = models.FileField(upload_to='templates/', null=True, blank=True, verbose_name='Shablon fayli')
    
    # Status
    is_active = models.BooleanField(default=True, verbose_name='Faol')
    version = models.CharField(max_length=20, default='1.0', verbose_name='Versiya')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Compliance shabloni'
        verbose_name_plural = 'Compliance shablonlari'
        ordering = ['template_type', 'name']
    
    def __str__(self):
        return f"{self.template_type} - {self.name}"
