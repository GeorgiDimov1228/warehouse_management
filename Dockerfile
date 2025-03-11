FROM python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_ENV=production \
    FLASK_APP=run.py \
    PYTHONPATH=/app

# Create and set working directory
WORKDIR /app

# Create user for security
RUN groupadd -g 1000 appuser && \
    useradd -u 1000 -g appuser -s /bin/sh -m appuser

# Install required packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir gunicorn

# Create log and backup directories
RUN mkdir -p /var/log/warehouse /var/backups/warehouse && \
    chown -R appuser:appuser /var/log/warehouse /var/backups/warehouse

# Copy application code
COPY . .

# Make run.py executable
RUN chmod +x run.py

# Set proper permissions
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 5000

# Command to run the application
CMD ["gunicorn", "--config", "gunicorn_config.py", "app:create_app()"]