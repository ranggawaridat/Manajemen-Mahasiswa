FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Prevent Python from writing .pyc files and enable stdout/stderr buffering
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy app source
COPY . /app/

# Expose port
EXPOSE 5000

# Use Gunicorn to serve the Flask app
CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app", "--workers", "2"]
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Prevent Python from writing .pyc files and enable stdout/stderr buffering
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy app source
COPY . /app/

# Expose port
EXPOSE 5000

# Use Gunicorn to serve the Flask app
CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app", "--workers", "1"]
