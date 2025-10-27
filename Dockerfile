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

# Run the application
CMD ["python", "-m", "flask", "run", "--host=0.0.0.0"]
