#!/bin/bash
python setup_sample_db.py
python manage.py migrate
nginx
/usr/local/bin/gunicorn config.wsgi:application --bind 127.0.0.1:8000 --workers 2