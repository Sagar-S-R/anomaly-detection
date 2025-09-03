# Multi-stage Docker build for Anomaly Detection Backend with Advanced Model Pre-loading
FROM python:3.10-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONPATH=/app

# Set model cache directories for all AI frameworks
ENV TRANSFORMERS_CACHE=/app/model_cache
ENV TORCH_HOME=/app/model_cache
ENV HF_HOME=/app/model_cache
ENV WHISPER_CACHE_DIR=/app/model_cache
ENV MEDIAPIPE_CACHE_DIR=/app/model_cache

# Create app directory and model cache
WORKDIR /app
RUN mkdir -p /app/model_cache /app/logs /app/uploads /app/anomaly_frames /app/static/anomaly_frames

# Install system dependencies with optimizations
RUN apt-get update && apt-get install -y \
    # Build tools
    gcc \
    g++ \
    make \
    cmake \
    # SSL and crypto
    libffi-dev \
    libssl-dev \
    # Audio processing
    libasound2-dev \
    portaudio19-dev \
    # Video processing and OpenCV dependencies
    ffmpeg \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libglib2.0-0 \
    libgtk-3-0 \
    libgstreamer1.0-0 \
    libgstreamer-plugins-base1.0-0 \
    # Additional OpenCV dependencies
    libavcodec-dev \
    libavformat-dev \
    libavutil-dev \
    libswscale-dev \
    libswresample-dev \
    # Utilities
    git \
    curl \
    wget \
    unzip \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Install Python dependencies with caching
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip setuptools wheel
RUN pip install --no-cache-dir -r requirements.txt

# Copy model pre-loading script
COPY preload_models.py ./preload_models.py

# ALWAYS pre-load ALL models during BUILD for instant container startup
RUN echo "🚀 Pre-loading ALL AI models during build for instant startup..." && \
    python preload_models.py && \
    echo "✅ All models cached! Container will start instantly!" && \
    echo "📊 Model cache size:" && du -sh /app/model_cache/ || true

# Copy application code
COPY . .

# Set proper permissions
RUN chmod +x *.py && \
    chmod -R 755 /app/model_cache && \
    chmod -R 755 /app/uploads && \
    chmod -R 755 /app/anomaly_frames

# Create entrypoint script for flexible service startup
RUN echo '#!/bin/bash\n\
# Multi-service startup script\n\
if [ "$SERVICE_TYPE" = "dashboard" ]; then\n\
    echo "🖥️ Starting Dashboard Service on port 8001..."\n\
    exec uvicorn dashboard_app:app --host 0.0.0.0 --port 8001 --reload\n\
elif [ "$SERVICE_TYPE" = "api" ]; then\n\
    echo "🔧 Starting API Service on port 8000..."\n\
    exec uvicorn app:app --host 0.0.0.0 --port 8000 --reload\n\
else\n\
    echo "🚀 Starting Full System (API + Dashboard)..."\n\
    exec uvicorn app:app --host 0.0.0.0 --port 8000 --reload\n\
fi' > /app/entrypoint.sh && chmod +x /app/entrypoint.sh

# Expose both API and Dashboard ports
EXPOSE 8000 8001

# Enhanced health check for both services
HEALTHCHECK --interval=30s --timeout=30s --start-period=60s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Use the flexible entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]
