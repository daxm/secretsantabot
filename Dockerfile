FROM python:3.11-slim

WORKDIR /app

# Copy project files
COPY pyproject.toml .
COPY app/ ./app/

# Install dependencies
RUN pip install --no-cache-dir -e .

# Create directory for database
RUN mkdir -p /app/data

# Expose port
EXPOSE 5000

# Set environment variables
ENV FLASK_APP=app
ENV PYTHONUNBUFFERED=1

# Run the application with Gunicorn (production WSGI server)
# Worker settings:
#   --workers 2: Two worker processes for handling requests
#   --timeout 300: Max 5 minutes per request (increased from 120s)
#   --graceful-timeout 30: Give workers 30s to finish after timeout
#   --keep-alive 5: Keep connections alive for 5s to reduce overhead
#   --log-level info: Log important events
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--timeout", "300", "--graceful-timeout", "30", "--keep-alive", "5", "--log-level", "info", "app:create_app()"]
