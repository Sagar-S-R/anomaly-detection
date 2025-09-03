#!/bin/bash
# 🔍 Docker Configuration Verification Script
# Comprehensive check for all Docker configurations

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}🔍 DOCKER CONFIGURATION VERIFICATION${NC}"
echo "========================================"
echo ""

# 1. Check Docker daemon
echo -e "${BLUE}1. Checking Docker daemon...${NC}"
if docker info >/dev/null 2>&1; then
    echo -e "${GREEN}✅ Docker daemon is running${NC}"
else
    echo -e "${RED}❌ Docker daemon is not running${NC}"
    echo -e "${YELLOW}💡 Please start Docker Desktop or run: sudo systemctl start docker${NC}"
    exit 1
fi
echo ""

# 2. Validate docker-compose files
echo -e "${BLUE}2. Validating Docker Compose files...${NC}"

echo "   📋 Production (docker-compose.yml):"
if docker-compose config --quiet 2>/dev/null; then
    echo -e "   ${GREEN}✅ Valid${NC}"
else
    echo -e "   ${RED}❌ Invalid${NC}"
    docker-compose config 2>&1 | head -5
fi

echo "   📋 Development (docker-compose.dev.yml):"
if docker-compose -f docker-compose.dev.yml config --quiet 2>/dev/null; then
    echo -e "   ${GREEN}✅ Valid${NC}"
else
    echo -e "   ${RED}❌ Invalid${NC}"
    docker-compose -f docker-compose.dev.yml config 2>&1 | head -5
fi
echo ""

# 3. Check required files
echo -e "${BLUE}3. Checking required files...${NC}"

files_to_check=(
    "backend/Dockerfile"
    "backend/app.py"
    "backend/dashboard_app.py"
    "backend/requirements.txt"
    "backend/preload_models.py"
    "frontend/Dockerfile"
)

all_files_exist=true
for file in "${files_to_check[@]}"; do
    if [[ -f "$file" ]]; then
        echo -e "   ${GREEN}✅ $file${NC}"
    else
        echo -e "   ${RED}❌ $file (missing)${NC}"
        all_files_exist=false
    fi
done
echo ""

# 4. Check service configurations
echo -e "${BLUE}4. Checking service configurations...${NC}"

echo "   🚀 Production services:"
docker-compose config --services 2>/dev/null | sed 's/^/      - /' || echo "   ❌ Cannot list services"

echo "   💻 Development services:"
docker-compose -f docker-compose.dev.yml config --services 2>/dev/null | sed 's/^/      - /' || echo "   ❌ Cannot list services"
echo ""

# 5. Test Dockerfile syntax
echo -e "${BLUE}5. Testing Dockerfile syntax...${NC}"

echo "   🐳 Backend Dockerfile:"
if docker build --no-cache --dry-run backend/ >/dev/null 2>&1; then
    echo -e "   ${GREEN}✅ Syntax valid${NC}"
else
    echo -e "   ${YELLOW}⚠️ Dry-run not supported, will test with quick build${NC}"
    # Try a quick build test
    if docker build --quiet --no-cache -f backend/Dockerfile backend/ -t test-syntax 2>/dev/null | head -1; then
        echo -e "   ${GREEN}✅ Build started successfully${NC}"
        docker rmi test-syntax 2>/dev/null || true
    else
        echo -e "   ${RED}❌ Build failed${NC}"
    fi
fi

echo "   🌐 Frontend Dockerfile:"
if [[ -f "frontend/Dockerfile" ]]; then
    if docker build --quiet --no-cache frontend/ -t test-frontend-syntax 2>/dev/null | head -1; then
        echo -e "   ${GREEN}✅ Frontend build syntax valid${NC}"
        docker rmi test-frontend-syntax 2>/dev/null || true
    else
        echo -e "   ${RED}❌ Frontend build failed${NC}"
    fi
else
    echo -e "   ${YELLOW}⚠️ Frontend Dockerfile not found${NC}"
fi
echo ""

# 6. Check environment variables
echo -e "${BLUE}6. Checking environment setup...${NC}"

if [[ -f ".env" ]]; then
    echo -e "   ${GREEN}✅ .env file found${NC}"
    echo "   📝 Environment variables:"
    grep -E '^[A-Z_]+=.*' .env 2>/dev/null | sed 's/=.*/=***/' | sed 's/^/      /' || echo "      (No variables found)"
else
    echo -e "   ${YELLOW}⚠️ No .env file found${NC}"
    echo -e "   ${CYAN}💡 Create .env with: GROQ_API_KEY=your_key_here${NC}"
fi
echo ""

# 7. Check for port conflicts
echo -e "${BLUE}7. Checking for port conflicts...${NC}"

ports=(8000 8001 3000 27017 80)
for port in "${ports[@]}"; do
    if lsof -i :$port >/dev/null 2>&1; then
        echo -e "   ${YELLOW}⚠️ Port $port is in use${NC}"
        lsof -i :$port | head -2 | tail -1 | awk '{print "      Process: " $1 " (PID: " $2 ")"}'
    else
        echo -e "   ${GREEN}✅ Port $port is available${NC}"
    fi
done
echo ""

# Summary
echo -e "${CYAN}📊 VERIFICATION SUMMARY${NC}"
echo "========================"

if $all_files_exist; then
    echo -e "${GREEN}✅ All required files present${NC}"
else
    echo -e "${RED}❌ Some files are missing${NC}"
fi

if docker-compose config --quiet 2>/dev/null && docker-compose -f docker-compose.dev.yml config --quiet 2>/dev/null; then
    echo -e "${GREEN}✅ All Docker configurations valid${NC}"
else
    echo -e "${RED}❌ Some Docker configurations invalid${NC}"
fi

echo ""
echo -e "${CYAN}🚀 READY TO BUILD?${NC}"
echo "If all checks passed, you can now run:"
echo -e "${GREEN}  ./manage.sh build    ${NC}# Build and start all services"
echo -e "${GREEN}  ./manage.sh dev      ${NC}# Start development mode"
echo -e "${GREEN}  ./manage.sh start    ${NC}# Start pre-built services"
