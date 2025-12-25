web: gunicorn music_store.wsgi
worker: celery -A music_store worker -l info -Q media --concurrency=2 --max-tasks-per-child=10
beat: celery -A music_store beat -l info
