from django.contrib import admin
from .models import Evaluation, TenderAnalysisResult


@admin.register(Evaluation)
class EvaluationAdmin(admin.ModelAdmin):
    list_display = ['id', 'tender', 'status', 'total_participants', 'evaluator', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['tender__title', 'tender__tender_number', 'evaluator__username']
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at', 'updated_at']


@admin.register(TenderAnalysisResult)
class TenderAnalysisResultAdmin(admin.ModelAdmin):
    list_display = ['id', 'tender_name', 'winner_name', 'participant_count', 'user', 'created_at']
    list_filter = ['created_at', 'user']
    search_fields = ['tender_name', 'winner_name', 'user__username']
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Asosiy ma\'lumotlar', {
            'fields': ('user', 'tender_name', 'tender_type')
        }),
        ('Natijalar', {
            'fields': ('winner_name', 'winner_score', 'participant_count', 'summary')
        }),
        ('Ma\'lumotlar', {
            'fields': ('tender_data', 'participants', 'ranking')
        }),
        ('Vaqt ma\'lumotlari', {
            'fields': ('created_at', 'updated_at')
        }),
    )
