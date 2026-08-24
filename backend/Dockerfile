FROM python:3.11-slim

WORKDIR /app

# Install system dependencies + parser dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies (including parser)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install parser-specific dependencies
RUN pip install --no-cache-dir beautifulsoup4 requests lxml

# Copy application
COPY . .

# Create required directories
RUN mkdir -p /app/static /app/media /app/parser/src

# Expose port
EXPOSE 8000

# Entrypoint handles migrations and starts gunicorn
ENTRYPOINT ["sh", "-c", "mkdir -p /app/static && python manage.py migrate --fake-initial && python manage.py migrate && exec gunicorn --bind 0.0.0.0:8000 config.wsgi:application"]
