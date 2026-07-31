FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy backend code for Django imports
COPY backend/ /app/backend/

# Install Django and dependencies
RUN pip install --no-cache-dir -r /app/backend/requirements.txt

# Copy parser source
COPY src/ /app/src/

# Environment
ENV PYTHONPATH=/app

CMD ["python", "/app/src/load_to_db.py"]
