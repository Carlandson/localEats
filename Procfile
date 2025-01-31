web: gunicorn localeats.wsgi
release: python manage.py migrate && python manage.py collectstatic --noinput && npm ci && npm run build