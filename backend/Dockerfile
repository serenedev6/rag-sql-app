# Base image
FROM python:3.13-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .


# Copy Nginx config
COPY nginx.conf /etc/nginx/sites-available/default

# Collect static files
RUN python manage.py collectstatic --noinput || true

# Create startup script
RUN echo '#!/bin/bash\n\
python setup_sample_db.py\n\
python manage.py migrate\n\
nginx\n\
gunicorn config.wsgi:application --bind 127.0.0.1:8000 --workers 2' > /start.sh
RUN chmod +x /start.sh

# Expose port
EXPOSE 8000


# Start Nginx + Gunicorn
CMD ["/start.sh"]

# Run Django server
# CMD ["sh", "-c", "python setup_sample_db.py && python manage.py migrate && gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 2"]
