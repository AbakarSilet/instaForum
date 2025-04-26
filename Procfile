web: gunicorn ForumInsta.wsgi
worker: celery -A ForumInsta worker -l info
beat: celery -A ForumInsta beat -l info