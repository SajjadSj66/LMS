from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# تنظیمات محیطی
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'LMS.settings')
app = Celery('LMS')

# خواندن تنظیمات از فایل settings.py
app.config_from_object('django.conf:settings', namespace='CELERY')

# کشف خودکار وظایف در اپلیکیشن‌ها
app.autodiscover_tasks()
