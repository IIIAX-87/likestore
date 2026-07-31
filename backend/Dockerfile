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

# Create required directories (will be recreated if volume mounts over them)
RUN mkdir -p /app/static /app/media /app/parser/src
RUN touch /app/parser/src/parsed_data.json

# Expose port
EXPOSE 8000

# Entrypoint handles migrations and starts gunicorn
# mkdir is needed because volume mount may override static directory
ENTRYPOINT ["sh", "-c", "mkdir -p /app/static && python manage.py migrate --fake-initial && python manage.py migrate && exec gunicorn --bind 0.0.0.0:8000 config.wsgi:application"]
