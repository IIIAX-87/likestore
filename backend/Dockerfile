FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create static directory (fixes STATICFILES_DIRS warning)
RUN mkdir -p /app/static

# Collect static files
RUN python manage.py collectstatic --noinput || true

# Expose port
EXPOSE 8000

# Entrypoint handles migrations and product loading
ENTRYPOINT ["sh", "-c", "python manage.py migrate --noinput && python manage.py loaddata fixtures/initial.json || python manage.py load_products || true && exec gunicorn --bind 0.0.0.0:8000 config.wsgi:application"]
