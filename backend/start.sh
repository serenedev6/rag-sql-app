#!/bin/bash
python setup_sample_db.py
python manage.py migrate
/usr/local/bin/gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 2