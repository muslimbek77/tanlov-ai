from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    CustomTokenObtainPairView,
    LogoutView,
    UserViewSet,
    AuditLogViewSet,
    simple_login,
    simple_logout,
    get_current_user
)

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='users')
router.register(r'audit-logs', AuditLogViewSet, basename='audit-logs')

urlpatterns = [
    # JWT endpoints
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', LogoutView.as_view(), name='logout'),
    
    # Simple auth (backward compatible)
    path('login/', simple_login, name='simple_login'),
    path('simple-logout/', simple_logout, name='simple_logout'),
    path('me/', get_current_user, name='get_current_user'),
    
    # Router URLs
    path('', include(router.urls)),
]
