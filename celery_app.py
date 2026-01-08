# Bu fayl tanlov_ai/celery.py ga yo'naltirildi
# Celery konfiguratsiyasi tanlov_ai/celery.py da joylashgan

from tanlov_ai.celery import app

__all__ = ['app']

@app.task(bind=True)
def debug_task(self):
    """Debug vazifasi"""
    print(f'Request: {self.request!r}')

@app.task
def health_check():
    """Salomatlik tekshiruvi"""
    return {
        'status': 'healthy',
        'timestamp': timezone.now().isoformat(),
    }
