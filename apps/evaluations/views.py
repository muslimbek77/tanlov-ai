from rest_framework import viewsets
from .models import Evaluation, ParticipantScore, ScoreDetail, EvaluationLog
from .serializers import EvaluationSerializer, ParticipantScoreSerializer, ScoreDetailSerializer, EvaluationLogSerializer


class EvaluationViewSet(viewsets.ModelViewSet):
    queryset = Evaluation.objects.all()
    serializer_class = EvaluationSerializer


class ParticipantScoreViewSet(viewsets.ModelViewSet):
    queryset = ParticipantScore.objects.all()
    serializer_class = ParticipantScoreSerializer


class ScoreDetailViewSet(viewsets.ModelViewSet):
    queryset = ScoreDetail.objects.all()
    serializer_class = ScoreDetailSerializer


class EvaluationLogViewSet(viewsets.ModelViewSet):
    queryset = EvaluationLog.objects.all()
    serializer_class = EvaluationLogSerializer
