from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from . import analysis_views

router = DefaultRouter()
router.register(r'evaluations', views.EvaluationViewSet)
router.register(r'participant-scores', views.ParticipantScoreViewSet)
router.register(r'score-details', views.ScoreDetailViewSet)
router.register(r'evaluation-logs', views.EvaluationLogViewSet)

urlpatterns = [
    path('', include(router.urls)),
    
    # Tender tahlil API
    path('analyze-tender/', analysis_views.analyze_tender, name='analyze-tender'),
    path('analyze-participant/', analysis_views.analyze_participant, name='analyze-participant'),
    path('compare-participants/', analysis_views.compare_participants, name='compare-participants'),
    path('full-analysis/', analysis_views.full_analysis, name='full-analysis'),
    path('tender-requirements/', analysis_views.get_tender_requirements, name='tender-requirements'),
    path('reset/', analysis_views.reset_analysis, name='reset-analysis'),
]
