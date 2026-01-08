import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tanlov_ai.settings')

app = Celery('tanlov_ai')

# Django sozlamalaridan Celery konfiguratsiyasi
app.config_from_object('django.conf:settings', namespace='CELERY')

# Avtomatik ravishda vazifalarni topish
app.autodiscover_tasks()

# Celery konfiguratsiyasi
app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='Asia/Tashkent',
    enable_utc=True,
    result_expires=3600,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 daqiqa
    task_soft_time_limit=25 * 60,  # 25 daqiqa
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

# Vazifa yo'llari
app.conf.task_routes = {
    'core.tasks.*': {'queue': 'document_processing'},
    'apps.evaluations.tasks.*': {'queue': 'evaluation'},
    'apps.anti_fraud.tasks.*': {'queue': 'fraud_detection'},
    'apps.compliance.tasks.*': {'queue': 'compliance'},
}

# Beat schedule uchun periodik vazifalar
app.conf.beat_schedule = {
    'cleanup-old-tasks': {
        'task': 'core.tasks.cleanup_old_tasks',
        'schedule': 3600.0,  # Har soat
    },
    'process-pending-documents': {
        'task': 'core.tasks.process_pending_documents',
        'schedule': 300.0,  # Har 5 daqiqa
    },
}


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
