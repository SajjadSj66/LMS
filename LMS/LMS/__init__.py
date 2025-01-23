from __future__ import absolute_import, unicode_literals

# این تضمین می‌کند که Celery هنگام شروع پروژه load شود
from .celery import app as celery_app

__all__ = ('celery_app',)
