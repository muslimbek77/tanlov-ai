from rest_framework import permissions
from .models import UserRole


class IsAdmin(permissions.BasePermission):
    """Faqat Admin uchun"""
    message = 'Faqat administrator uchun ruxsat berilgan.'

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_admin


class IsOperatorOrAdmin(permissions.BasePermission):
    """Operator yoki Admin uchun"""
    message = 'Faqat operator yoki administrator uchun ruxsat berilgan.'

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_operator


class CanAnalyze(permissions.BasePermission):
    """Tahlil qilish huquqi"""
    message = 'Tahlil qilish uchun ruxsat yo\'q.'

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.can_analyze


class IsOwnerOrAdmin(permissions.BasePermission):
    """O'zi yoki Admin"""
    def has_object_permission(self, request, view, obj):
        if request.user.is_admin:
            return True
        return obj == request.user
