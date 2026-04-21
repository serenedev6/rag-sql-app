# Base image
FROM python:3.13-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install system dependencies including Nginx
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    nginx \
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

# Copy and set up startup script
COPY start.sh /start.sh
RUN chmod +x /start.sh

# Expose port 80 (Nginx)
EXPOSE 80

# Start Nginx + Gunicorn
CMD ["/start.sh"]