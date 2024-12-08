FROM python:3.11-slim-buster

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
ENV DOCKER_CONTAINER=1

RUN apt-get update -y && apt-get install -y git && apt-get clean

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create a non-root user and log directory
RUN useradd -m appuser && \
    mkdir -p /app/logs && \
    chown -R appuser:appuser /app
USER appuser

# Run the application
CMD ["python", "-u", "main.py"]
