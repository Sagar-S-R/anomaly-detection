# 🔨 Docker Build Process

## Build Overview

The Docker build process is optimized for **fast startup** by pre-loading AI models during build time rather than runtime.

## Build Strategy

### 🎯 Goals
- ✅ **Single build** creates backend image for both API and Dashboard
- ✅ **Model pre-loading** during build for instant container startup  
- ✅ **Layer caching** for faster subsequent builds
- ✅ **Minimal runtime** dependencies

### 📋 Build Order
1. **Backend Image** (with model pre-loading)
2. **Frontend Image** (React build)
3. **Service Orchestration** (docker-compose)

## Backend Build Process

### Stage 1: Base Environment
```dockerfile
FROM python:3.10-slim as base
```
- Python 3.10 runtime
- System dependencies (ffmpeg, OpenCV libs, audio processing)
- Build tools (gcc, make, cmake)

### Stage 2: Python Dependencies
```dockerfile
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
```
- Install all Python packages
- 68 validated packages including PyTorch, transformers, FastAPI
- No cache to reduce image size

### Stage 3: AI Model Pre-loading ⭐
```dockerfile
COPY preload_models.py ./preload_models.py
RUN python preload_models.py
```
**Models Downloaded During Build:**
- **CLIP Models**: `openai/clip-vit-base-patch32`, `openai/clip-vit-large-patch14`
- **BLIP Model**: `Salesforce/blip-image-captioning-base`  
- **Whisper Models**: `base`, `small` models
- **MediaPipe Models**: Pose estimation, face detection

**Cache Locations:**
- `/app/model_cache` - Persistent storage
- Environment variables set for all frameworks

### Stage 4: Application Code
```dockerfile
COPY . .
RUN chmod +x *.py
```
- Copy application files
- Set executable permissions
- Create required directories

### Stage 5: Flexible Entrypoint
```dockerfile
RUN echo '#!/bin/bash
if [ "$SERVICE_TYPE" = "dashboard" ]; then
    exec uvicorn dashboard_app:app --host 0.0.0.0 --port 8001
elif [ "$SERVICE_TYPE" = "api" ]; then
    exec uvicorn app:app --host 0.0.0.0 --port 8000
else
    exec uvicorn app:app --host 0.0.0.0 --port 8000
fi' > /app/entrypoint.sh && chmod +x /app/entrypoint.sh
```

## Frontend Build Process

### Simple Node.js Build
```dockerfile
FROM node:18-alpine
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build
```

## Build Commands

### Full System Build
```bash
# Build all services
docker-compose up --build

# Or using manage script
./manage.sh build
```

### Individual Service Builds
```bash
# Backend only
docker-compose build backend

# Frontend only  
docker-compose build frontend

# Backend + Dashboard (same image)
docker-compose build backend dashboard
```

### Development Build
```bash
# Development mode with live reload
docker-compose -f docker-compose.dev.yml up --build

# Or using manage script
./manage.sh dev
```

## Build Optimization

### 🚀 Fast Builds
- **Layer caching**: Dependencies change less than code
- **Multi-stage builds**: Separate concerns
- **Model pre-loading**: One-time download during build
- **.dockerignore**: Exclude unnecessary files

### 📦 Small Images
- **Slim base images**: `python:3.10-slim`, `node:18-alpine`
- **No cache**: `--no-cache-dir` for pip installs
- **Cleanup**: Remove package lists after install
- **Single RUN**: Combine commands to reduce layers

### ⚡ Runtime Performance
- **Pre-loaded models**: No download delays
- **Compiled dependencies**: Built during image creation
- **Optimized entrypoint**: Fast service switching

## Build Time Expectations

### Initial Build (with model download)
- **Backend**: 10-15 minutes (includes AI model downloads)
- **Frontend**: 2-3 minutes (npm install + build)
- **Total**: ~15-20 minutes

### Subsequent Builds (with cache)
- **Backend**: 2-3 minutes (if code changes only)
- **Frontend**: 1-2 minutes (if dependencies cached)
- **Total**: ~3-5 minutes

### Model Cache Benefits
- **First startup**: Instant (models already cached)
- **Container restart**: Instant (no re-download)
- **Multiple services**: Share same model cache

## Troubleshooting Builds

### Common Issues
1. **Docker daemon not running**
   ```bash
   docker --version  # Check if Docker is available
   ```

2. **Model download failures**
   - Network connectivity issues
   - Hugging Face rate limits
   - Disk space for model cache

3. **Dependency conflicts**
   - Check `requirements.txt` validity
   - Run `./manage.sh validate` before build

4. **Build context too large**
   - Update `.dockerignore`
   - Exclude unnecessary files

### Build Verification
```bash
# Test build syntax
docker build --no-cache --dry-run backend/

# Quick build test
docker build -t test-build backend/

# Full verification
./manage.sh check
```
