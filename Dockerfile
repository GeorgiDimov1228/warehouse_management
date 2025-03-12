FROM python:3.8-slim

WORKDIR /app

# Install specific dependency versions to ensure compatibility
RUN pip install --no-cache-dir \
    Flask==2.0.1 \
    Werkzeug==2.0.1 \
    Flask-SQLAlchemy==2.5.1 \
    SQLAlchemy==1.4.23 \
    Flask-Migrate==3.1.0 \
    python-dotenv==0.19.1 \
    opcua==0.98.13 \
    cryptography==36.0.0 \
    tenacity


# Copy requirements.txt for reference (but we've already installed fixed versions)
COPY requirements.txt .

# Copy the application
COPY . .

# Set environment variables
ENV FLASK_APP=run.py
ENV FLASK_ENV=development
ENV FLASK_DEBUG=1
ENV PYTHONUNBUFFERED=1

# Expose port
EXPOSE 5000

# Run the application
CMD ["flask", "run", "--host=0.0.0.0"]