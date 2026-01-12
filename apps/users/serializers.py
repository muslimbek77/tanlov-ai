from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import User, AuditLog


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """JWT token olish uchun custom serializer"""
    
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Token ichiga qo'shimcha ma'lumot
        token['username'] = user.username
        token['role'] = user.role
        token['is_admin'] = user.is_admin
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        # Response'ga qo'shimcha ma'lumot
        data['user'] = {
            'id': self.user.id,
            'username': self.user.username,
            'email': self.user.email,
            'role': self.user.role,
            'role_display': self.user.get_role_display(),
            'first_name': self.user.first_name,
            'last_name': self.user.last_name,
            'is_admin': self.user.is_admin,
            'can_analyze': self.user.can_analyze,
        }
        return data


class UserSerializer(serializers.ModelSerializer):
    """Foydalanuvchi serializer"""
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'role', 'role_display', 'phone', 'department',
            'is_active', 'is_admin', 'can_analyze',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_admin', 'can_analyze']


class UserCreateSerializer(serializers.ModelSerializer):
    """Foydalanuvchi yaratish serializer"""
    password = serializers.CharField(write_only=True, min_length=6)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            'username', 'email', 'password', 'password_confirm',
            'first_name', 'last_name', 'role', 'phone', 'department'
        ]

    def validate(self, attrs):
        if attrs['password'] != attrs.pop('password_confirm'):
            raise serializers.ValidationError({'password_confirm': 'Parollar mos kelmadi'})
        return attrs

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class ChangePasswordSerializer(serializers.Serializer):
    """Parol o'zgartirish serializer"""
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, min_length=6)
    new_password_confirm = serializers.CharField(required=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({'new_password_confirm': 'Yangi parollar mos kelmadi'})
        return attrs


class AuditLogSerializer(serializers.ModelSerializer):
    """Audit log serializer"""
    user_name = serializers.CharField(source='user.username', read_only=True)
    action_display = serializers.CharField(source='get_action_display', read_only=True)

    class Meta:
        model = AuditLog
        fields = [
            'id', 'user', 'user_name', 'action', 'action_display',
            'description', 'ip_address', 'extra_data', 'created_at'
        ]
        read_only_fields = fields
