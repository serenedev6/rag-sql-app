#!/bin/bash
python manage.py migrate
/usr/local/bin/gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 2