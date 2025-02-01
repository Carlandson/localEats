web: gunicorn localeats.wsgi
release: npm ci && npm run build && python manage.py collectstatic --noinput && python manage.py migrate