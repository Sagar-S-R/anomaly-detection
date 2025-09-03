#!/bin/bash

# Anomaly Detection System - Enhanced Deployment Script with Model Pre-loading
set -e

echo "🚀 Starting Anomaly Detection System Deployment with AI Model Pre-loading"
echo "========================================================================="

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your actual values before continuing!"
    echo "   Required: GROQ_API_KEY"
    read -p "Press Enter to continue after editing .env file..."
fi

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p backend/anomaly_frames
mkdir -p backend/uploads
mkdir -p backend/logs
mkdir -p nginx/ssl

# Clean up any existing containers
echo "🧹 Cleaning up existing containers..."
docker-compose down --remove-orphans || true

# Build images with model pre-loading
echo "🏗️  Building Docker images with AI model pre-loading..."
echo "⏳ This will take a while on first build as models are downloaded..."
echo "📦 Models include: CLIP, BLIP, Whisper, MediaPipe"
docker-compose build --no-cache

echo "🌐 Starting services..."
docker-compose up -d

# Wait for services to be ready (longer wait for model loading)
echo "⏳ Waiting for services to initialize (including model loading)..."
echo "🤖 AI models are being loaded from cache..."
sleep 45

# Check service health with detailed model status
echo "🔍 Checking service health and model status..."
services=("backend" "dashboard" "frontend" "mongo")

for service in "${services[@]}"; do
    if docker-compose ps | grep -q "${service}.*Up"; then
        echo "✅ $service is running"
        
        # Check model status for backend services
        if [[ "$service" == "backend" || "$service" == "dashboard" ]]; then
            echo "🤖 Checking AI model status for $service..."
            if docker-compose exec -T $service python verify_models.py 2>/dev/null; then
                echo "✅ AI models loaded successfully in $service"
            else
                echo "⚠️  AI models verification failed in $service (may still be loading)"
            fi
        fi
    else
        echo "❌ $service failed to start"
        docker-compose logs $service
    fi
done

# Display model cache information
echo ""
echo "🤖 AI Model Cache Information:"
echo "=============================="
model_cache_size=$(docker volume inspect anomaly-detection_model_cache --format '{{.Mountpoint}}' 2>/dev/null | xargs du -sh 2>/dev/null | cut -f1 || echo "Unknown")
echo "💾 Model cache size: $model_cache_size"
echo "⚡ Models are pre-loaded and cached for instant startup"

echo ""
echo "🎉 Deployment Complete with AI Model Pre-loading!"
echo "================================================="
echo "🌐 Frontend: http://localhost:3000"
echo "🔧 Backend API: http://localhost:8000"
echo "📊 Dashboard: http://localhost:8001"
echo "🗄️  MongoDB: localhost:27017"
echo "🤖 AI Models: Pre-loaded and cached"
echo ""
echo "⚡ Performance Benefits:"
echo "   • Instant model loading on container restart"
echo "   • No download delays during runtime"
echo "   • Consistent performance across deployments"
echo ""
echo "📋 Useful Commands:"
echo "   View logs: docker-compose logs -f [service_name]"
echo "   Stop services: docker-compose down"
echo "   Restart: docker-compose restart [service_name]"
echo "   Update: docker-compose pull && docker-compose up -d"
echo "   Model status: docker-compose exec backend python verify_models.py"
echo ""
echo "🔧 Troubleshooting:"
echo "   - Check .env file for correct API keys"
echo "   - Ensure ports 3000, 8000, 8001, 27017 are available"
echo "   - View service logs for detailed error information"
echo "   - First build takes longer due to model downloads"
echo "   - Subsequent builds are faster due to Docker layer caching"
