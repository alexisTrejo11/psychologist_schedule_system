#!/bin/bash

echo "Applying miigrations..."
python manage.py makemigrations
python manage.py migrate

echo "Recopiling static files..."
python manage.py collectstatic --noinput

# Inicia Gunicorn
echo "Init Gunicorn..."
exec gunicorn --bind 0.0.0.0:8000 pychologist_project.wsgi:application