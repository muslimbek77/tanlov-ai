from django.contrib.auth.models import AbstractUser
from django.db import models


class UserRole(models.TextChoices):
    """Foydalanuvchi rollari"""
    ADMIN = 'admin', 'Administrator'
    OPERATOR = 'operator', 'Operator'
    VIEWER = 'viewer', 'Ko\'ruvchi'


class User(AbstractUser):
    """Custom foydalanuvchi modeli"""
    role = models.CharField(
        max_length=20,
        choices=UserRole.choices,
        default=UserRole.VIEWER,
        verbose_name='Rol'
    )
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name='Telefon')
    department = models.CharField(max_length=100, blank=True, null=True, verbose_name='Bo\'lim')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Yaratilgan')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Yangilangan')

    class Meta:
        verbose_name = 'Foydalanuvchi'
        verbose_name_plural = 'Foydalanuvchilar'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

    @property
    def is_admin(self):
        return self.role == UserRole.ADMIN or self.is_superuser

    @property
    def is_operator(self):
        return self.role in [UserRole.ADMIN, UserRole.OPERATOR] or self.is_superuser

    @property
    def can_analyze(self):
        """Tahlil qilish huquqi"""
        return self.role in [UserRole.ADMIN, UserRole.OPERATOR]

    @property
    def can_view(self):
        """Ko'rish huquqi"""
        return True  # Barcha rollar ko'ra oladi


class AuditLog(models.Model):
    """Audit log - barcha amallarni kuzatish"""
    
    class ActionType(models.TextChoices):
        LOGIN = 'login', 'Kirish'
        LOGOUT = 'logout', 'Chiqish'
        TENDER_ANALYZE = 'tender_analyze', 'Tender tahlili'
        PARTICIPANT_ANALYZE = 'participant_analyze', 'Ishtirokchi tahlili'
        COMPARISON = 'comparison', 'Solishtirish'
        PDF_DOWNLOAD = 'pdf_download', 'PDF yuklab olish'
        EXCEL_DOWNLOAD = 'excel_download', 'Excel yuklab olish'
        SETTINGS_CHANGE = 'settings_change', 'Sozlamalar o\'zgartirish'
        USER_CREATE = 'user_create', 'Foydalanuvchi yaratish'
        USER_UPDATE = 'user_update', 'Foydalanuvchi yangilash'
        USER_DELETE = 'user_delete', 'Foydalanuvchi o\'chirish'

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_logs',
        verbose_name='Foydalanuvchi'
    )
    action = models.CharField(
        max_length=50,
        choices=ActionType.choices,
        verbose_name='Amal'
    )
    description = models.TextField(blank=True, verbose_name='Tavsif')
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name='IP manzil')
    user_agent = models.TextField(blank=True, verbose_name='User Agent')
    extra_data = models.JSONField(default=dict, blank=True, verbose_name='Qo\'shimcha ma\'lumot')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Vaqt')

    class Meta:
        verbose_name = 'Audit log'
        verbose_name_plural = 'Audit loglar'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user} - {self.get_action_display()} - {self.created_at}"

    @classmethod
    def log(cls, user, action, description='', request=None, extra_data=None):
        """Audit log yozish"""
        ip_address = None
        user_agent = ''
        
        if request:
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip_address = x_forwarded_for.split(',')[0]
            else:
                ip_address = request.META.get('REMOTE_ADDR')
            user_agent = request.META.get('HTTP_USER_AGENT', '')

        return cls.objects.create(
            user=user if user and user.is_authenticated else None,
            action=action,
            description=description,
            ip_address=ip_address,
            user_agent=user_agent,
            extra_data=extra_data or {}
        )
