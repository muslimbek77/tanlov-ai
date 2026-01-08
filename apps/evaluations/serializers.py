from rest_framework import serializers
from .models import Evaluation, ParticipantScore, ScoreDetail, EvaluationLog


class EvaluationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Evaluation
        fields = '__all__'


class ParticipantScoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParticipantScore
        fields = '__all__'


class ScoreDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScoreDetail
        fields = '__all__'


class EvaluationLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = EvaluationLog
        fields = '__all__'
