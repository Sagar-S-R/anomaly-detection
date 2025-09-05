# 🚀 Backend Deployment Requirements

## 📋 System Requirements for Anomaly Detection Backend

### 🖥️ **Minimum Hardware Requirements**

#### **CPU Requirements**
- **Minimum**: Intel i5-8400 (6 cores) or AMD Ryzen 5 2600 (6 cores)
- **Recommended**: Intel i7-10700K (8 cores) or AMD Ryzen 7 3700X (8 cores)
- **Optimal**: Intel i9-11900K (8 cores) or AMD Ryzen 9 5900X (12 cores)

#### **RAM Requirements**
- **Minimum**: 8 GB DDR4
- **Recommended**: 16 GB DDR4
- **Optimal**: 32 GB DDR4

**Memory Breakdown:**
- **Base System**: 2-3 GB
- **AI Models (Loaded)**: 4-6 GB
  - MediaPipe Pose Model: ~200 MB
  - CLIP ViT-Base-Patch32: ~600 MB
  - CLIP ViT-Large-Patch14: ~1.2 GB
  - BLIP Image Captioning: ~1.0 GB
  - Whisper Tiny: ~39 MB
  - Whisper Tiny: ~150 MB (optimized for Standard_B2s)
  - PyTorch Runtime: ~1-2 GB
- **Video Processing Buffer**: 1-2 GB
- **Audio Processing Buffer**: 500 MB
- **WebSocket Connections**: 100-500 MB
- **Operating Overhead**: 1-2 GB

#### **Storage Requirements**
- **Minimum**: 20 GB SSD
- **Recommended**: 50 GB SSD
- **Optimal**: 100 GB NVMe SSD

**Storage Breakdown:**
- **Application Code**: ~500 MB
- **AI Models Cache**: ~8 GB
- **Video Recordings**: 10-50 GB (configurable)
- **Anomaly Frames**: 1-5 GB
- **Audio Chunks**: 1-2 GB
- **System Logs**: 1-2 GB
- **Database Storage**: 1-5 GB

#### **GPU Requirements (Optional but Recommended)**
- **Minimum**: NVIDIA GTX 1060 (6GB VRAM) or equivalent
- **Recommended**: NVIDIA RTX 3060 (12GB VRAM) or equivalent
- **Optimal**: NVIDIA RTX 4070 (12GB VRAM) or higher

**GPU Benefits:**
- 3-5x faster inference for CLIP/BLIP models
- Reduced CPU load during video processing
- Better concurrent user support

---

## 🐳 **Docker Deployment Specifications**

### **Container Resource Limits**

```yaml
# Docker Compose Resource Allocation
services:
  anomaly-backend:
    image: anomaly-detection:latest
    deploy:
      resources:
        limits:
          cpus: '4.0'        # 4 CPU cores
          memory: 12G        # 12 GB RAM
        reservations:
          cpus: '2.0'        # Reserve 2 cores
          memory: 8G         # Reserve 8 GB
    environment:
      - TORCH_NUM_THREADS=4
      - OMP_NUM_THREADS=4
      - CUDA_VISIBLE_DEVICES=0  # If GPU available
```

### **Optimal Production Settings**
```yaml
# Production-Ready Configuration
version: '3.8'
services:
  anomaly-backend:
    image: anomaly-detection:production
    deploy:
      resources:
        limits:
          cpus: '8.0'        # 8 CPU cores
          memory: 16G        # 16 GB RAM
        reservations:
          cpus: '4.0'        # Reserve 4 cores
          memory: 12G        # Reserve 12 GB
      restart_policy:
        condition: on-failure
        max_attempts: 3
    volumes:
      - ./data:/app/data
      - ./models:/app/models
    environment:
      - FAST_MODE=true       # Enable performance optimizations
      - CUDA_VISIBLE_DEVICES=0
      - MODEL_CACHE_DIR=/app/models
```

---

## ☁️ **Cloud Platform Requirements**

### **AWS EC2 Instances**
| Instance Type | vCPUs | RAM | Storage | Use Case | Monthly Cost* |
|--------------|-------|-----|---------|----------|---------------|
| t3.large | 2 | 8 GB | 20 GB EBS | Development | ~$60 |
| c5.xlarge | 4 | 8 GB | 50 GB EBS | Minimum Production | ~$125 |
| c5.2xlarge | 8 | 16 GB | 100 GB EBS | **Recommended** | ~$250 |
| c5.4xlarge | 16 | 32 GB | 200 GB EBS | High Load | ~$500 |

**GPU Instances (Optional):**
| Instance Type | vCPUs | RAM | GPU | Use Case | Monthly Cost* |
|--------------|-------|-----|-----|----------|---------------|
| g4dn.xlarge | 4 | 16 GB | 1x T4 | GPU Acceleration | ~$400 |
| g4dn.2xlarge | 8 | 32 GB | 1x T4 | **GPU Recommended** | ~$600 |

*Costs are approximate and vary by region

### **Google Cloud Platform**
| Machine Type | vCPUs | RAM | Storage | Use Case | Monthly Cost* |
|-------------|-------|-----|---------|----------|---------------|
| e2-standard-4 | 4 | 16 GB | 50 GB SSD | Development | ~$120 |
| c2-standard-8 | 8 | 32 GB | 100 GB SSD | **Recommended** | ~$300 |
| n1-standard-8 | 8 | 30 GB | 100 GB SSD | Production | ~$250 |

### **Azure Virtual Machines**
| VM Size | vCPUs | RAM | Storage | Use Case | Monthly Cost* |
|---------|-------|-----|---------|----------|---------------|
| Standard_D4s_v3 | 4 | 16 GB | 50 GB Premium SSD | Development | ~$140 |
| Standard_D8s_v3 | 8 | 32 GB | 100 GB Premium SSD | **Recommended** | ~$280 |

---

## 🔧 **Performance Optimization Settings**

### **Environment Variables for Production**
```bash
# Performance Optimization
export FAST_MODE=true
export TORCH_NUM_THREADS=4
export OMP_NUM_THREADS=4
export MALLOC_ARENA_MAX=2

# Memory Management
export PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:512
export TRANSFORMERS_CACHE=/app/models/cache
export HF_HOME=/app/models/huggingface

# API Rate Limits
export MAX_CONCURRENT_CONNECTIONS=10
export WEBSOCKET_TIMEOUT=300
export FRAME_PROCESSING_RATE=1  # Process 1 frame per second

# Storage Optimization
export VIDEO_RETENTION_DAYS=7
export ANOMALY_FRAME_LIMIT=1000
export AUDIO_CHUNK_RETENTION_HOURS=24
```

### **FastAPI Production Configuration**
```python
# app.py production settings
uvicorn.run(
    "app:app",
    host="0.0.0.0",
    port=8000,
    workers=4,                    # 4 worker processes
    access_log=False,             # Disable access logs for performance
    server_header=False,          # Security
    date_header=False,            # Performance
    loop="uvloop",                # High-performance event loop
    http="httptools",             # Fast HTTP parser
    ws_max_size=16777216,         # 16MB WebSocket message limit
    ws_ping_interval=20,          # WebSocket keepalive
    ws_ping_timeout=20,
    timeout_keep_alive=30,
    limit_concurrency=100,        # Concurrent request limit
    limit_max_requests=1000,      # Max requests before worker restart
)
```

---

## 📊 **Real-Time Performance Metrics**

### **Processing Benchmarks**
| Component | CPU Usage | RAM Usage | Processing Time |
|-----------|-----------|-----------|-----------------|
| MediaPipe Pose | 15-25% | 200 MB | 33ms/frame |
| CLIP Scene Analysis | 20-35% | 800 MB | 150ms/frame |
| Whisper Audio | 10-20% | 100 MB | 2s/chunk |
| Fusion Logic | 5-10% | 50 MB | 10ms/decision |
| **Total System** | **50-90%** | **4-6 GB** | **<2s latency** |

### **Concurrent User Support**
| RAM | CPU Cores | Max Users | Notes |
|-----|-----------|-----------|-------|
| 8 GB | 4 cores | 2-3 users | Basic monitoring |
| 16 GB | 8 cores | 5-8 users | **Recommended** |
| 32 GB | 16 cores | 10-15 users | High-capacity |

### **Network Requirements**
- **Bandwidth**: 5-10 Mbps per video stream
- **Latency**: <100ms for real-time monitoring
- **WebSocket**: Persistent connections required
- **Storage I/O**: 50-100 MB/s for video recording

---

## 🛠️ **Installation & Deployment Commands**

### **Quick Docker Deployment**
```bash
# Clone repository
git clone https://github.com/Samrudhp/anomaly-detection.git
cd anomaly-detection

# Build optimized production image
docker build -f Dockerfile.production -t anomaly-detection:latest .

# Run with resource limits
docker run -d \
  --name anomaly-backend \
  --cpus="4.0" \
  --memory="12g" \
  -p 8000:8000 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/models:/app/models \
  -e FAST_MODE=true \
  -e TORCH_NUM_THREADS=4 \
  anomaly-detection:latest
```

### **Docker Compose Production**
```bash
# Start with production configuration
docker-compose -f docker-compose.prod.yml up -d

# Monitor resource usage
docker stats anomaly-backend

# View logs
docker logs -f anomaly-backend
```

### **Kubernetes Deployment**
```yaml
# k8s-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: anomaly-detection
spec:
  replicas: 2
  selector:
    matchLabels:
      app: anomaly-detection
  template:
    metadata:
      labels:
        app: anomaly-detection
    spec:
      containers:
      - name: anomaly-backend
        image: anomaly-detection:latest
        resources:
          requests:
            memory: "8Gi"
            cpu: "2"
          limits:
            memory: "16Gi"
            cpu: "4"
        ports:
        - containerPort: 8000
        env:
        - name: FAST_MODE
          value: "true"
        - name: TORCH_NUM_THREADS
          value: "4"
```

---

## 🚨 **Critical Production Considerations**

### **Security Requirements**
- **Firewall**: Only expose port 8000 (HTTPS recommended)
- **Authentication**: Implement API keys or JWT tokens
- **CORS**: Configure allowed origins
- **Rate Limiting**: Prevent API abuse
- **Video Encryption**: Encrypt stored video files

### **Monitoring & Logging**
```bash
# Essential monitoring commands
htop                          # CPU/Memory monitoring
nvidia-smi                    # GPU monitoring (if available)
iostat -x 1                   # Disk I/O monitoring
netstat -tulpn                # Network connections
df -h                         # Disk space monitoring

# Log locations
tail -f /app/logs/anomaly.log      # Application logs
tail -f /var/log/docker/anomaly.log  # Docker logs
```

### **Backup & Recovery**
- **Database**: Daily automated backups
- **Model Cache**: Backup downloaded models
- **Video Archives**: Configurable retention policy
- **Configuration**: Version control all configs

### **Scaling Strategies**
1. **Vertical Scaling**: Increase CPU/RAM on single instance
2. **Horizontal Scaling**: Multiple backend instances with load balancer
3. **Microservices**: Separate pose, scene, and audio processing
4. **CDN**: Use CDN for model distribution

---

## 📈 **Cost Optimization Tips**

### **Development Environment**
- Use **t3.medium** (2 vCPU, 4GB RAM) for ~$30/month
- Enable **spot instances** for 60-70% cost reduction
- Use **local development** with Docker for testing

### **Production Environment**
- **Reserved Instances**: Save 30-60% with 1-3 year commitments
- **Auto-scaling**: Scale down during low usage
- **Storage Optimization**: Use S3/Blob storage for videos
- **Model Caching**: Pre-download models to reduce startup time

### **Performance vs Cost Matrix**
| Budget | Instance Type | Performance | Users | Use Case |
|--------|---------------|-------------|-------|----------|
| $60/month | t3.large | Basic | 1-2 | Development |
| $125/month | c5.xlarge | Good | 3-5 | Small Production |
| $250/month | c5.2xlarge | **Excellent** | 5-10 | **Recommended** |
| $500/month | c5.4xlarge | Premium | 10-20 | High Load |

---

## ✅ **Deployment Checklist**

### **Pre-Deployment**
- [ ] Server meets minimum RAM requirements (8GB+)
- [ ] Docker installed and configured
- [ ] Sufficient storage space (20GB+)
- [ ] Network ports configured (8000)
- [ ] Environment variables set
- [ ] SSL certificate configured (production)

### **Model Preparation**
- [ ] Download all AI models (~8GB)
- [ ] Verify MediaPipe pose model
- [ ] Test CLIP/BLIP models
- [ ] Validate Whisper audio models
- [ ] Configure model cache directory

### **Post-Deployment**
- [ ] Health check endpoint responding
- [ ] WebSocket connections working
- [ ] Video processing functional
- [ ] Audio transcription working
- [ ] Database connectivity verified
- [ ] Monitoring setup complete
- [ ] Backup strategy implemented

---

## 🆘 **Troubleshooting Common Issues**

### **High Memory Usage (>90%)**
```bash
# Check model loading
docker exec anomaly-backend python -c "import torch; print(torch.cuda.memory_summary())"

# Reduce model size
export CLIP_MODEL="openai/clip-vit-base-patch32"  # Use base instead of large
export WHISPER_MODEL="tiny"                        # Use tiny instead of large
```

### **CPU Bottleneck (>95%)**
```bash
# Enable FAST_MODE
export FAST_MODE=true
export FRAME_SKIP_RATE=3                    # Process every 3rd frame

# Reduce concurrent processing
export MAX_WORKERS=2
export TORCH_NUM_THREADS=2
```

### **Storage Issues**
```bash
# Clean old recordings
find /app/data/videos -name "*.mp4" -mtime +7 -delete

# Clean anomaly frames
find /app/data/anomaly_frames -name "*.jpg" -mtime +3 -delete

# Clean audio chunks
find /app/data/audio_chunks -name "*.wav" -mtime +1 -delete
```

---

## 📞 **Support & Resources**

### **Documentation**
- [API Reference](./API_REFERENCE.md)
- [Configuration Guide](./CONFIGURATION.md)
- [Performance Tuning](./PERFORMANCE_TUNING.md)

### **Monitoring Tools**
- **Grafana**: System metrics dashboard
- **Prometheus**: Metrics collection
- **ELK Stack**: Log aggregation and analysis
- **Sentry**: Error tracking and performance monitoring

### **Community**
- **GitHub Issues**: Bug reports and feature requests
- **Discord**: Real-time community support
- **Documentation**: Comprehensive guides and tutorials

---

*Last Updated: September 4, 2025*
*Version: 2.0.0*
