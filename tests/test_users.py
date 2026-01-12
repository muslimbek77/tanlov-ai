"""
User va Authentication testlari
"""
import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from apps.users.models import User, UserRole, AuditLog


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def admin_user(db):
    return User.objects.create_user(
        username='admin_test',
        password='admin123',
        email='admin@test.com',
        role=UserRole.ADMIN
    )


@pytest.fixture
def operator_user(db):
    return User.objects.create_user(
        username='operator_test',
        password='operator123',
        email='operator@test.com',
        role=UserRole.OPERATOR
    )


@pytest.fixture
def viewer_user(db):
    return User.objects.create_user(
        username='viewer_test',
        password='viewer123',
        email='viewer@test.com',
        role=UserRole.VIEWER
    )


class TestUserModel:
    """User model testlari"""
    
    def test_create_user(self, db):
        user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@test.com'
        )
        assert user.username == 'testuser'
        assert user.role == UserRole.VIEWER  # Default role
        assert user.check_password('testpass123')
    
    def test_admin_role(self, admin_user):
        assert admin_user.is_admin == True
        assert admin_user.is_operator == True
        assert admin_user.can_analyze == True
    
    def test_operator_role(self, operator_user):
        assert operator_user.is_admin == False
        assert operator_user.is_operator == True
        assert operator_user.can_analyze == True
    
    def test_viewer_role(self, viewer_user):
        assert viewer_user.is_admin == False
        assert viewer_user.is_operator == False
        assert viewer_user.can_analyze == False
        assert viewer_user.can_view == True


class TestAuthentication:
    """Authentication testlari"""
    
    def test_login_success(self, api_client, admin_user):
        response = api_client.post('/api/auth/login/', {
            'username': 'admin_test',
            'password': 'admin123'
        })
        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data
        assert 'refresh' in response.data
        assert response.data['user']['role'] == 'admin'
    
    def test_login_wrong_password(self, api_client, admin_user):
        response = api_client.post('/api/auth/login/', {
            'username': 'admin_test',
            'password': 'wrongpassword'
        })
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_login_creates_audit_log(self, api_client, admin_user):
        api_client.post('/api/auth/login/', {
            'username': 'admin_test',
            'password': 'admin123'
        })
        audit = AuditLog.objects.filter(
            user=admin_user,
            action=AuditLog.ActionType.LOGIN
        ).first()
        assert audit is not None
    
    def test_jwt_token_access(self, api_client, admin_user):
        # Login
        response = api_client.post('/api/auth/login/', {
            'username': 'admin_test',
            'password': 'admin123'
        })
        access_token = response.data['access']
        
        # Protected endpoint
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        response = api_client.get('/api/auth/me/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['user']['username'] == 'admin_test'
    
    def test_jwt_token_invalid(self, api_client):
        api_client.credentials(HTTP_AUTHORIZATION='Bearer invalid_token')
        response = api_client.get('/api/auth/me/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestAuditLog:
    """Audit log testlari"""
    
    def test_create_audit_log(self, db, admin_user):
        log = AuditLog.log(
            user=admin_user,
            action=AuditLog.ActionType.TENDER_ANALYZE,
            description='Test tender tahlili'
        )
        assert log.user == admin_user
        assert log.action == AuditLog.ActionType.TENDER_ANALYZE
        assert log.description == 'Test tender tahlili'
    
    def test_audit_log_without_user(self, db):
        log = AuditLog.log(
            user=None,
            action=AuditLog.ActionType.LOGIN,
            description='Anonymous action'
        )
        assert log.user is None
        assert log.action == AuditLog.ActionType.LOGIN
