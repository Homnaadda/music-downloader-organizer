# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY requirements.txt . 
COPY app.py .
COPY organize_music.py .
COPY templates/ ./templates/
COPY static/ ./static/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Create a directory for downloads and organized music
RUN mkdir -p /app/downloads /app/downloads/organized

# Expose the port the app runs on
EXPOSE 5000

# Set environment variables
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0

# Run the application
CMD ["flask", "run"]
