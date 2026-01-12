from rest_framework import status, viewsets, generics
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate

from .models import User, AuditLog
from .serializers import (
    CustomTokenObtainPairSerializer,
    UserSerializer,
    UserCreateSerializer,
    ChangePasswordSerializer,
    AuditLogSerializer
)
from .permissions import IsAdmin, IsOperatorOrAdmin, IsOwnerOrAdmin


class CustomTokenObtainPairView(TokenObtainPairView):
    """JWT token olish"""
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            # Audit log
            user = User.objects.filter(username=request.data.get('username')).first()
            if user:
                AuditLog.log(user, AuditLog.ActionType.LOGIN, 'Tizimga kirish', request)
        return response


class LogoutView(APIView):
    """Chiqish"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            
            AuditLog.log(request.user, AuditLog.ActionType.LOGOUT, 'Tizimdan chiqish', request)
            return Response({'message': 'Muvaffaqiyatli chiqildi'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(viewsets.ModelViewSet):
    """Foydalanuvchilarni boshqarish"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsAdmin]

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        return UserSerializer

    def perform_create(self, serializer):
        user = serializer.save()
        AuditLog.log(
            self.request.user,
            AuditLog.ActionType.USER_CREATE,
            f'Yangi foydalanuvchi yaratildi: {user.username}',
            self.request,
            {'new_user_id': user.id, 'role': user.role}
        )

    def perform_update(self, serializer):
        user = serializer.save()
        AuditLog.log(
            self.request.user,
            AuditLog.ActionType.USER_UPDATE,
            f'Foydalanuvchi yangilandi: {user.username}',
            self.request,
            {'updated_user_id': user.id}
        )

    def perform_destroy(self, instance):
        AuditLog.log(
            self.request.user,
            AuditLog.ActionType.USER_DELETE,
            f'Foydalanuvchi o\'chirildi: {instance.username}',
            self.request,
            {'deleted_user_id': instance.id}
        )
        instance.delete()

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def me(self, request):
        """Joriy foydalanuvchi ma'lumotlari"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def change_password(self, request):
        """Parolni o'zgartirish"""
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            if not request.user.check_password(serializer.validated_data['old_password']):
                return Response({'old_password': 'Noto\'g\'ri parol'}, status=status.HTTP_400_BAD_REQUEST)
            
            request.user.set_password(serializer.validated_data['new_password'])
            request.user.save()
            
            AuditLog.log(
                request.user,
                AuditLog.ActionType.SETTINGS_CHANGE,
                'Parol o\'zgartirildi',
                request
            )
            return Response({'message': 'Parol muvaffaqiyatli o\'zgartirildi'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    """Audit loglarni ko'rish"""
    queryset = AuditLog.objects.all()
    serializer_class = AuditLogSerializer
    permission_classes = [IsAuthenticated, IsAdmin]

    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by action
        action = self.request.query_params.get('action')
        if action:
            queryset = queryset.filter(action=action)
        
        # Filter by user
        user_id = self.request.query_params.get('user_id')
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        
        # Filter by date range
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        if date_from:
            queryset = queryset.filter(created_at__date__gte=date_from)
        if date_to:
            queryset = queryset.filter(created_at__date__lte=date_to)

        return queryset[:100]  # Limit to 100 records


# Simple auth views (backward compatible)
@api_view(['POST'])
@permission_classes([AllowAny])
def simple_login(request):
    """Oddiy login (JWT bilan)"""
    username = request.data.get('username')
    password = request.data.get('password')

    if not username or not password:
        return Response({
            'success': False,
            'error': 'Username va password kiritilishi shart'
        }, status=status.HTTP_400_BAD_REQUEST)

    user = authenticate(username=username, password=password)
    
    if user is not None:
        # JWT token yaratish
        refresh = RefreshToken.for_user(user)
        
        AuditLog.log(user, AuditLog.ActionType.LOGIN, 'Tizimga kirish', request)
        
        return Response({
            'success': True,
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role,
                'role_display': user.get_role_display(),
                'first_name': user.first_name,
                'last_name': user.last_name,
                'is_admin': user.is_admin,
                'can_analyze': user.can_analyze,
            }
        })
    else:
        return Response({
            'success': False,
            'error': 'Noto\'g\'ri username yoki password'
        }, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def simple_logout(request):
    """Oddiy logout"""
    try:
        refresh_token = request.data.get('refresh')
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()
    except:
        pass
    
    AuditLog.log(request.user, AuditLog.ActionType.LOGOUT, 'Tizimdan chiqish', request)
    return Response({'success': True, 'message': 'Muvaffaqiyatli chiqildi'})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_current_user(request):
    """Joriy foydalanuvchi"""
    user = request.user
    return Response({
        'success': True,
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': user.role,
            'role_display': user.get_role_display(),
            'first_name': user.first_name,
            'last_name': user.last_name,
            'is_admin': user.is_admin,
            'can_analyze': user.can_analyze,
        }
    })
