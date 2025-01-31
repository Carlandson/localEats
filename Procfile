web: gunicorn localeats.wsgi
release: python manage.py migrate && python manage.py collectstatic --noinput && npm install && npm run build