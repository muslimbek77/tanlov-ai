"""
Evaluations API testlari
"""
import pytest
from rest_framework import status
from rest_framework.test import APIClient
from apps.users.models import User, UserRole
from apps.evaluations.models import TenderAnalysisResult


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
def authenticated_client(api_client, admin_user):
    response = api_client.post('/api/auth/login/', {
        'username': 'admin_test',
        'password': 'admin123'
    })
    access_token = response.data['access']
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
    return api_client


class TestDashboardStats:
    """Dashboard statistika testlari"""
    
    def test_get_stats_empty(self, api_client):
        response = api_client.get('/api/evaluations/dashboard-stats/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['success'] == True
        assert 'stats' in response.data


class TestAnalysisHistory:
    """Tahlil tarixi testlari"""
    
    def test_save_result(self, api_client, db):
        data = {
            'tender': {
                'tender_purpose': 'Test tender',
                'tender_type': 'open'
            },
            'participants': [],
            'ranking': [
                {
                    'participant_name': 'Company A',
                    'total_weighted_score': 85,
                    'overall_match_percentage': 90
                }
            ],
            'winner': {
                'participant_name': 'Company A',
                'total_weighted_score': 85
            },
            'summary': 'Test summary',
            'language': 'uz'
        }
        
        response = api_client.post('/api/evaluations/save-result/', data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['success'] == True
        
        # Database'da tekshirish
        result = TenderAnalysisResult.objects.first()
        assert result is not None
        assert result.tender_name == 'Test tender'
    
    def test_get_history(self, api_client, db):
        # Ma'lumot yaratish
        TenderAnalysisResult.objects.create(
            tender_name='Test tender 1',
            tender_type='open',
            participants=[],
            ranking=[],
            winner_name='Company A',
            winner_score=85,
            summary='Summary 1'
        )
        
        response = api_client.get('/api/evaluations/history/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['success'] == True
        assert len(response.data['results']) == 1
    
    def test_delete_result(self, api_client, db):
        result = TenderAnalysisResult.objects.create(
            tender_name='Test tender',
            tender_type='open',
            participants=[],
            ranking=[],
            winner_name='Company A',
            winner_score=85,
            summary='Summary'
        )
        
        response = api_client.delete(f'/api/evaluations/history/{result.id}/delete/')
        assert response.status_code == status.HTTP_200_OK
        assert TenderAnalysisResult.objects.count() == 0


class TestExport:
    """Eksport testlari"""
    
    def test_export_csv(self, api_client):
        data = {
            'ranking': [
                {
                    'participant_name': 'Company A',
                    'total_weighted_score': 85,
                    'overall_match_percentage': 90,
                    'price_analysis': {'proposed_price': '1000000'},
                    'risk_level': 'low',
                    'recommendation': 'Recommended'
                }
            ],
            'language': 'uz'
        }
        
        response = api_client.post('/api/evaluations/download-csv/', data, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert response['Content-Type'] == 'text/csv; charset=utf-8'
    
    def test_export_excel(self, api_client):
        data = {
            'tender': {'tender_purpose': 'Test tender'},
            'ranking': [
                {
                    'participant_name': 'Company A',
                    'total_weighted_score': 85,
                    'overall_match_percentage': 90,
                    'price_analysis': {'proposed_price': '1000000'},
                    'risk_level': 'low',
                    'recommendation': 'Recommended',
                    'strengths': ['Good'],
                    'weaknesses': ['None']
                }
            ],
            'summary': 'Test summary',
            'language': 'uz'
        }
        
        response = api_client.post('/api/evaluations/download-excel/', data, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert 'spreadsheet' in response['Content-Type']
