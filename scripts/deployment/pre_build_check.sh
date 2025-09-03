#!/bin/bash
# Pre-build system check
echo "🔍 Pre-Build System Check"
echo "========================"

cd /Users/samrudhp/Projects-git/anomaly-detection

echo "📁 Checking project structure..."
if [[ -f "docker-compose.yml" ]]; then
    echo "✅ docker-compose.yml found"
else
    echo "❌ docker-compose.yml missing"
    exit 1
fi

if [[ -d "frontend" ]]; then
    echo "✅ frontend directory found"
    if [[ -f "frontend/Dockerfile" ]]; then
        echo "✅ frontend/Dockerfile found"
    else
        echo "❌ frontend/Dockerfile missing"
    fi
    if [[ -f "frontend/package.json" ]]; then
        echo "✅ frontend/package.json found"
    else
        echo "❌ frontend/package.json missing"
    fi
else
    echo "❌ frontend directory missing"
fi

if [[ -d "backend" ]]; then
    echo "✅ backend directory found"
    if [[ -f "backend/Dockerfile" ]]; then
        echo "✅ backend/Dockerfile found"
    else
        echo "❌ backend/Dockerfile missing"
    fi
    if [[ -f "backend/requirements.txt" ]]; then
        echo "✅ backend/requirements.txt found"
    else
        echo "❌ backend/requirements.txt missing"
    fi
else
    echo "❌ backend directory missing"
fi

echo ""
echo "🐳 Checking Docker..."
if command -v docker &> /dev/null; then
    echo "✅ Docker installed"
    if docker --version &> /dev/null; then
        docker_version=$(docker --version)
        echo "   Version: $docker_version"
    fi
else
    echo "❌ Docker not installed"
    exit 1
fi

if command -v docker-compose &> /dev/null; then
    echo "✅ Docker Compose installed"
    compose_version=$(docker-compose --version)
    echo "   Version: $compose_version"
else
    echo "❌ Docker Compose not installed"
    exit 1
fi

echo ""
echo "🔧 Checking Docker daemon..."
if docker ps &> /dev/null; then
    echo "✅ Docker daemon running"
else
    echo "❌ Docker daemon not running"
    echo "   Please start Docker Desktop"
    exit 1
fi

echo ""
echo "📦 Checking for existing containers..."
existing_containers=$(docker-compose ps -q 2>/dev/null | wc -l | xargs)
if [[ $existing_containers -gt 0 ]]; then
    echo "⚠️  Found $existing_containers existing containers"
    echo "   Running: docker-compose ps"
    docker-compose ps
    echo ""
    echo "   To clean start, run:"
    echo "   docker-compose down --volumes"
else
    echo "✅ No existing containers (clean slate)"
fi

echo ""
echo "💾 Checking disk space..."
available_space=$(df -h . | awk 'NR==2{print $4}')
echo "   Available space: $available_space"

echo ""
echo "🌐 Checking required ports..."
ports=(3000 8000 8001 27017 80)
for port in "${ports[@]}"; do
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        process=$(lsof -Pi :$port -sTCP:LISTEN -t | head -1)
        echo "⚠️  Port $port is in use (PID: $process)"
    else
        echo "✅ Port $port is available"
    fi
done

echo ""
echo "🎯 READY TO BUILD!"
echo "=================="
echo "All checks passed. You can now run:"
echo ""
echo "🚀 Quick start:"
echo "   docker-compose up -d"
echo ""
echo "🔨 Full build (recommended first time):"
echo "   docker-compose up --build"
echo ""
echo "📊 Monitor progress:"
echo "   docker-compose logs -f"
echo ""
echo "🌐 Access URLs (after build):"
echo "   Frontend:  http://localhost:3000"
echo "   Backend:   http://localhost:8000/docs"
echo "   Dashboard: http://localhost:8001"
