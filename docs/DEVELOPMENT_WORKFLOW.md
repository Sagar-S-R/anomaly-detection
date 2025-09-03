# 🔄 Code Update Workflow in Containerized Development

## Current Setup Analysis

Your `docker-compose.yml` is configured for **live code updates** with volume mapping:

```yaml
volumes:
  - ./backend:/app                    # 🔥 Live code sync
  - ./backend/anomaly_frames:/app/anomaly_frames
  - ./backend/uploads:/app/uploads
  - ./backend/logs:/app/logs
  - model_cache:/app/model_cache      # Persistent model cache
```

## 🔄 Update Scenarios & Methods

### **Scenario 1: Python Code Changes** ✅ **INSTANT UPDATES**
**Files**: `*.py` (app.py, utils/*.py, tier1/*.py, tier2/*.py)
**Update Method**: 🚀 **AUTOMATIC** - No rebuild needed!

```bash
# ✅ WORKS: Edit any .py file and save
# Changes reflect immediately due to volume mapping
```

**How it works**:
- Volume mapping: `./backend:/app` syncs your local files to container
- FastAPI/Uvicorn auto-reloads when Python files change
- Dashboard app also auto-reloads

### **Scenario 2: Requirements.txt Changes** ⚠️ **NEEDS REBUILD**
**Files**: `requirements.txt`, `requirements-dev.txt`
**Update Method**: 🔨 **REBUILD REQUIRED**

```bash
# Add new package to requirements.txt
echo "new-package>=1.0.0" >> requirements.txt

# Rebuild containers
docker-compose up --build
```

### **Scenario 3: Docker Configuration Changes** ⚠️ **NEEDS REBUILD**
**Files**: `Dockerfile*`, `docker-compose.yml`, `preload_models.py`
**Update Method**: 🔨 **FULL REBUILD**

```bash
# Clean rebuild
docker-compose down
docker-compose up --build
```

### **Scenario 4: Model/Static Files** ✅ **INSTANT UPDATES**
**Files**: Templates, static files, model files
**Update Method**: 🚀 **AUTOMATIC**

```bash
# ✅ WORKS: Update dashboard.html, CSS, JS files
# Changes reflect immediately
```

## 🚀 Recommended Development Workflow

### **1. Initial Build** (First time only)
```bash
cd /Users/samrudhp/Projects-git/anomaly-detection
docker-compose up --build  # Takes ~10-15 minutes (model downloading)
```

### **2. Daily Development** (99% of the time)
```bash
# Start containers (if not running)
docker-compose up -d

# Edit your Python code normally
# Changes auto-reload in containers! 🎉

# View logs in real-time
docker-compose logs -f backend
docker-compose logs -f dashboard
```

### **3. Adding New Dependencies** (Occasionally)
```bash
# 1. Edit requirements.txt
echo "new-package>=1.0.0" >> backend/requirements.txt

# 2. Test locally first (optional but recommended)
cd backend
python validate_requirements.py

# 3. Rebuild containers
docker-compose up --build

# 4. Verify new package works
docker-compose logs backend
```

## ⚡ Hot Reload Features

Your setup includes **automatic reloading**:

### **Backend API** (Port 8000):
```python
# In Dockerfile, uvicorn runs with --reload
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
```

### **Dashboard** (Port 8001):
```python  
# Dashboard app also has auto-reload
# Edit dashboard_app.py and see changes instantly
```

## 🧪 Testing Code Changes

### **Test Individual Components**:
```bash
# Test backend changes
curl http://localhost:8000/health

# Test dashboard changes  
curl http://localhost:8001/health

# Test specific endpoints
curl -X POST http://localhost:8000/api/process-frame \
  -F "frame=@test_image.jpg"
```

### **Live Development Dashboard**:
- **Backend**: http://localhost:8000/docs (FastAPI Swagger UI)
- **Dashboard**: http://localhost:8001 (Live anomaly detection)
- **Logs**: `docker-compose logs -f`

## 🚨 When Rebuild IS Required

### **Rebuild Triggers**:
```bash
# ⚠️ REBUILD NEEDED for:
- Adding/removing packages in requirements.txt
- Changing Dockerfile
- Modifying docker-compose.yml  
- Updating preload_models.py
- Changing environment variables in compose file
```

### **Rebuild Commands**:
```bash
# Quick rebuild (keeps volumes)
docker-compose up --build

# Clean rebuild (removes everything)
docker-compose down --volumes
docker-compose up --build

# Rebuild specific service
docker-compose up --build backend
```

## 🔧 Advanced Development Tips

### **1. Live Debugging**:
```bash
# SSH into running container for debugging
docker exec -it anomaly-backend bash

# Check Python imports
docker exec -it anomaly-backend python -c "import cv2; print('OK')"
```

### **2. Model Cache Persistence**:
```bash
# Models download once and persist across rebuilds
# Cache location: model_cache volume
docker volume inspect anomaly-detection_model_cache
```

### **3. Development vs Production**:
```bash
# Development (with hot reload)
docker-compose up

# Production (optimized, no reload)
docker-compose -f docker-compose.prod.yml up -d
```

## 📊 Update Speed Comparison

| Change Type | Method | Time | Auto-Reload |
|------------|--------|------|-------------|
| Python code (.py) | ✅ Edit & Save | ~1-2 seconds | YES |
| HTML/CSS/JS | ✅ Edit & Save | Instant | YES |
| Requirements.txt | 🔨 Rebuild | ~3-5 minutes | NO |
| Dockerfile | 🔨 Full Rebuild | ~10-15 minutes | NO |

## ✅ **ANSWER: Your Current Setup**

**For 99% of development work (Python code changes):**
```bash
# 1. Start containers once
docker-compose up -d

# 2. Edit code normally in your IDE
# 3. Changes appear instantly! 🚀
# 4. No rebuild needed!
```

**Only rebuild when adding new packages or changing Docker config!**

Your volume mapping setup is perfect for rapid development! 🎉
