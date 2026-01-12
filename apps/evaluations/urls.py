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
    path('export-pdf/', analysis_views.export_pdf, name='export-pdf'),
    
    # Tahlil natijalarini saqlash va olish
    path('save-result/', analysis_views.save_analysis_result, name='save-result'),
    path('history/', analysis_views.get_analysis_history, name='analysis-history'),
    path('history/<int:pk>/', analysis_views.get_analysis_detail, name='analysis-detail'),
    path('history/<int:pk>/delete/', analysis_views.delete_analysis_result, name='delete-analysis'),
    path('dashboard-stats/', analysis_views.get_dashboard_stats, name='dashboard-stats'),
    
    # Eksport
    path('download-excel/', analysis_views.download_excel, name='download-excel'),
    path('download-csv/', analysis_views.download_csv, name='download-csv'),
    
    # Dashboard grafiklar
    path('chart-data/', analysis_views.get_chart_data, name='chart-data'),
    path('recent-activities/', analysis_views.get_recent_activities, name='recent-activities'),
]
