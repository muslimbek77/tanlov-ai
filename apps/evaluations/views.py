from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Evaluation, ParticipantScore, ScoreDetail, EvaluationLog
from .serializers import EvaluationSerializer, ParticipantScoreSerializer, ScoreDetailSerializer, EvaluationLogSerializer


class EvaluationViewSet(viewsets.ModelViewSet):
    serializer_class = EvaluationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Faqat joriy foydalanuvchi baholagan evaluationlarni ko'rsatish"""
        return Evaluation.objects.filter(evaluator=self.request.user)
    
    def perform_create(self, serializer):
        """Evaluation yaratishda avtomatik foydalanuvchini bog'lash"""
        serializer.save(evaluator=self.request.user)


class ParticipantScoreViewSet(viewsets.ModelViewSet):
    serializer_class = ParticipantScoreSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Faqat joriy foydalanuvchining evaluationlariga tegishli ballar"""
        return ParticipantScore.objects.filter(evaluation__evaluator=self.request.user)


class ScoreDetailViewSet(viewsets.ModelViewSet):
    serializer_class = ScoreDetailSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Faqat joriy foydalanuvchining evaluationlariga tegishli batafsil ballar"""
        return ScoreDetail.objects.filter(participant_score__evaluation__evaluator=self.request.user)


class EvaluationLogViewSet(viewsets.ModelViewSet):
    serializer_class = EvaluationLogSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Faqat joriy foydalanuvchining evaluationlariga tegishli loglar"""
        return EvaluationLog.objects.filter(evaluation__evaluator=self.request.user)
