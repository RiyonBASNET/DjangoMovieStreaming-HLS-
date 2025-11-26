import os
from celery import Celery

# Set default Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'watchdoge.settings')

app = Celery('watchdoge')

# Load settings with CELERY namespace
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks.py in all installed apps
app.autodiscover_tasks()
