# Build stage
FROM python:3.9-slim as builder

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt

# Final stage
FROM python:3.9-slim

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV DJANGO_SETTINGS_MODULE=aircraft_production.settings
ENV PORT=8000

WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Copy wheels from builder and install
COPY --from=builder /app/wheels /wheels
RUN pip install --no-cache /wheels/*

# Copy project files
COPY . .

# Create necessary directories
RUN mkdir -p /app/staticfiles /app/mediafiles

# Create and switch to non-root user
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

# Run setup script for static files
RUN chmod +x setup_static.sh && ./setup_static.sh

# Expose port
EXPOSE $PORT

# Start command
CMD gunicorn aircraft_production.wsgi:application --bind 0.0.0.0:$PORT