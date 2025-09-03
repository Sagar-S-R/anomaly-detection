# 🚀 Quick Docker Commands Reference

## Build Commands

### Full System
```bash
# Build and start all services
./manage.sh build
docker-compose up --build

# Build without starting
docker-compose build

# Force rebuild (no cache)
docker-compose build --no-cache
```

### Individual Services
```bash
# Build specific service
docker-compose build backend
docker-compose build frontend
docker-compose build dashboard

# Build multiple services
docker-compose build backend dashboard
```

## Run Commands

### Production
```bash
# Start all services
./manage.sh start
docker-compose up -d

# Start with build
./manage.sh build
docker-compose up --build

# Start specific services
docker-compose up backend mongo
```

### Development
```bash
# Development mode
./manage.sh dev
docker-compose -f docker-compose.dev.yml up --build

# With live reload
docker-compose -f docker-compose.dev.yml up
```

## Management Commands

### Service Control
```bash
# Stop all services
./manage.sh stop
docker-compose down

# Restart services
./manage.sh restart
docker-compose restart

# Restart specific service
docker-compose restart backend
```

### Logs and Monitoring
```bash
# View all logs
./manage.sh logs
docker-compose logs -f

# View specific service logs
./manage.sh logs backend
docker-compose logs -f backend

# View recent logs only
docker-compose logs --tail=50 -f
```

### Health Checks
```bash
# Check service status
docker-compose ps

# Check specific service
docker ps | grep anomaly

# Service health
docker inspect anomaly-backend | grep Health -A5
```

## Debug Commands

### Container Access
```bash
# Execute shell in running container
docker exec -it anomaly-backend bash
docker exec -it anomaly-frontend sh

# Run temporary container
docker run -it --rm anomaly-detection-backend bash
```

### File Operations
```bash
# Copy files from container
docker cp anomaly-backend:/app/logs ./local-logs

# Copy files to container
docker cp ./config.json anomaly-backend:/app/
```

### Network Debugging
```bash
# List networks
docker network ls

# Inspect network
docker network inspect anomaly-detection_anomaly-network

# Test connectivity
docker exec anomaly-backend ping anomaly-mongo
```

## Volume Management

### List Volumes
```bash
# List all volumes
docker volume ls

# Inspect specific volume
docker volume inspect anomaly-detection_model_cache
docker volume inspect anomaly-detection_mongo_data
```

### Volume Operations
```bash
# Backup model cache
docker run --rm -v anomaly-detection_model_cache:/data -v $(pwd):/backup alpine tar czf /backup/model_cache.tar.gz -C /data .

# Restore model cache
docker run --rm -v anomaly-detection_model_cache:/data -v $(pwd):/backup alpine tar xzf /backup/model_cache.tar.gz -C /data
```

## Cleanup Commands

### Safe Cleanup
```bash
# Stop and remove containers
./manage.sh stop
docker-compose down

# Remove unused images
docker image prune -f

# Remove unused volumes (BE CAREFUL!)
docker volume prune -f
```

### Deep Cleanup
```bash
# Complete cleanup (DESTRUCTIVE!)
./manage.sh clean

# Manual deep cleanup
docker-compose down --volumes --remove-orphans
docker system prune -a -f
```

### Selective Cleanup
```bash
# Remove specific images
docker rmi anomaly-detection-backend
docker rmi anomaly-detection-frontend

# Remove stopped containers
docker container prune -f
```

## Environment Commands

### Environment Variables
```bash
# Show environment in container
docker exec anomaly-backend env | grep -E "(SERVICE_TYPE|GROQ|MONGO)"

# Load environment file
docker-compose --env-file .env.production up
```

### Configuration
```bash
# Validate compose files
docker-compose config
docker-compose -f docker-compose.dev.yml config

# Show effective configuration
docker-compose config --services
docker-compose config --volumes
```

## Performance Commands

### Resource Usage
```bash
# Show resource usage
docker stats

# Specific container stats
docker stats anomaly-backend anomaly-frontend

# Container processes
docker exec anomaly-backend top
```

### Image Information
```bash
# List images with sizes
docker images | grep anomaly

# Image layers and history
docker history anomaly-detection-backend

# Image details
docker inspect anomaly-detection-backend
```

## Quick Troubleshooting

### Common Issues
```bash
# Check if Docker is running
docker --version
docker info

# Check service health
docker-compose ps
curl http://localhost:8000/health

# Port conflicts
lsof -i :8000
lsof -i :8001

# Disk space
df -h
docker system df
```

### Emergency Commands
```bash
# Force stop all containers
docker kill $(docker ps -q)

# Remove all containers
docker rm -f $(docker ps -aq)

# Free up space immediately
docker system prune -a -f --volumes
```

## Useful Aliases

Add to your `~/.zshrc` or `~/.bashrc`:

```bash
# Docker aliases
alias dps='docker ps'
alias dimg='docker images'
alias dlogs='docker-compose logs -f'
alias dup='docker-compose up'
alias ddown='docker-compose down'
alias dbuild='docker-compose build'

# Anomaly detection specific
alias anomaly='cd /path/to/anomaly-detection'
alias anomaly-build='./manage.sh build'
alias anomaly-dev='./manage.sh dev'
alias anomaly-logs='./manage.sh logs'
```
