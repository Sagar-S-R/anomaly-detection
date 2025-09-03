#!/bin/bash
# 🎯 Anomaly Detection System - Master Control Script
# Centralized management for all operations

set -e  # Exit on any error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

show_help() {
    echo -e "${CYAN}🎯 Anomaly Detection System - Master Control${NC}"
    echo "=============================================="
    echo ""
    echo -e "${YELLOW}VALIDATION:${NC}"
    echo "  ./manage.sh validate         - Validate requirements and dependencies"
    echo "  ./manage.sh scan            - Scan code for missing dependencies"
    echo "  ./manage.sh verify          - Verify model setup"
    echo ""
    echo -e "${YELLOW}TESTING:${NC}"
    echo "  ./manage.sh test            - Run containerization tests"
    echo "  ./manage.sh demo            - Demo live code updates"
    echo "  ./manage.sh check           - Pre-build system check"
    echo ""
    echo -e "${YELLOW}DEPLOYMENT:${NC}"
    echo "  ./manage.sh deploy          - Deploy the system"
    echo "  ./manage.sh build           - Build all containers"
    echo "  ./manage.sh start           - Start all services"
    echo "  ./manage.sh stop            - Stop all services"
    echo "  ./manage.sh restart         - Restart all services"
    echo "  ./manage.sh logs            - Show service logs"
    echo ""
    echo -e "${YELLOW}DEVELOPMENT:${NC}"
    echo "  ./manage.sh dev             - Start development mode"
    echo "  ./manage.sh clean           - Clean containers and volumes"
    echo ""
    echo -e "${YELLOW}DOCUMENTATION:${NC}"
    echo "  ./manage.sh docs            - List available documentation"
    echo "  ./manage.sh guide <name>    - Open specific guide"
    echo "  ./manage.sh docker-docs     - Show Docker documentation"
    echo ""
    echo -e "${YELLOW}EXAMPLES:${NC}"
    echo "  ./manage.sh validate        # Check all requirements"
    echo "  ./manage.sh build           # Build and start system"
    echo "  ./manage.sh logs backend    # Show backend logs"
    echo "  ./manage.sh guide build     # Open build guide"
}

run_validation() {
    echo -e "${BLUE}🔍 Running Requirements Validation${NC}"
    cd backend && python ../scripts/validation/validate_requirements.py
}

run_scan() {
    echo -e "${BLUE}🔍 Scanning Dependencies${NC}"
    python scripts/validation/scan_dependencies.py
}

run_verify() {
    echo -e "${BLUE}🤖 Verifying Models${NC}"
    python scripts/validation/verify_models.py
}

run_test() {
    echo -e "${BLUE}🧪 Running Containerization Tests${NC}"
    bash scripts/testing/test_containerization.sh
}

run_demo() {
    echo -e "${BLUE}🎬 Running Live Update Demo${NC}"
    bash scripts/testing/demo_live_updates.sh
}

run_check() {
    echo -e "${BLUE}🔍 Pre-Build System Check${NC}"
    bash scripts/deployment/pre_build_check.sh
}

run_deploy() {
    echo -e "${BLUE}🚀 Deploying System${NC}"
    if [[ -f "scripts/deployment/deploy.sh" ]]; then
        bash scripts/deployment/deploy.sh
    else
        echo -e "${YELLOW}⚠️  Using docker-compose deploy${NC}"
        docker-compose up --build -d
    fi
}

run_build() {
    echo -e "${BLUE}🔨 Building All Containers${NC}"
    docker-compose up --build
}

run_start() {
    echo -e "${GREEN}▶️  Starting All Services${NC}"
    docker-compose up -d
}

run_stop() {
    echo -e "${RED}⏹️  Stopping All Services${NC}"
    docker-compose down
}

run_restart() {
    echo -e "${YELLOW}🔄 Restarting All Services${NC}"
    docker-compose restart
}

run_logs() {
    local service="$2"
    if [[ -n "$service" ]]; then
        echo -e "${CYAN}📋 Showing logs for: $service${NC}"
        docker-compose logs -f "$service"
    else
        echo -e "${CYAN}📋 Showing all service logs${NC}"
        docker-compose logs -f
    fi
}

run_dev() {
    echo -e "${GREEN}💻 Starting Development Mode${NC}"
    if [[ -f "docker-compose.dev.yml" ]]; then
        docker-compose -f docker-compose.dev.yml up --build
    else
        docker-compose up --build
    fi
}

run_clean() {
    echo -e "${RED}🧹 Cleaning Containers and Volumes${NC}"
    echo -e "${YELLOW}⚠️  This will remove all containers, volumes, and cached data!${NC}"
    read -p "Are you sure? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        docker-compose down --volumes --remove-orphans
        docker system prune -f
        echo -e "${GREEN}✅ Cleanup complete${NC}"
    else
        echo -e "${BLUE}ℹ️  Cleanup cancelled${NC}"
    fi
}

list_docs() {
    echo -e "${PURPLE}📚 Available Documentation${NC}"
    echo "=========================="
    if [[ -d "docs" ]]; then
        for doc in docs/*.md; do
            if [[ -f "$doc" ]]; then
                basename "$doc" .md | sed 's/_/ /g' | awk '{for(i=1;i<=NF;i++) $i=toupper(substr($i,1,1)) tolower(substr($i,2)); print "  " $0}'
            fi
        done
    else
        echo -e "${YELLOW}⚠️  No docs directory found${NC}"
    fi
    echo ""
    echo -e "${CYAN}Usage: ./manage.sh guide <name>${NC}"
    echo "  Example: ./manage.sh guide build"
}

open_guide() {
    local guide="$2"
    if [[ -z "$guide" ]]; then
        echo -e "${RED}❌ Please specify a guide name${NC}"
        list_docs
        return 1
    fi
    
    # Convert guide name to filename
    local filename="docs/${guide^^}_GUIDE.md"  # Try uppercase first
    [[ ! -f "$filename" ]] && filename="docs/${guide^^}_AND_TEST_GUIDE.md"
    [[ ! -f "$filename" ]] && filename="docs/${guide^^}_WORKFLOW.md"
    [[ ! -f "$filename" ]] && filename="docs/$(echo "$guide" | tr '[:lower:]' '[:upper:]').md"
    
    if [[ -f "$filename" ]]; then
        echo -e "${GREEN}📖 Opening: $filename${NC}"
        if command -v code &> /dev/null; then
            code "$filename"
        elif command -v open &> /dev/null; then
            open "$filename"
        else
            cat "$filename"
        fi
    else
        echo -e "${RED}❌ Guide not found: $guide${NC}"
        list_docs
    fi
}

show_documentation() {
    echo -e "${BLUE}📚 Project Documentation${NC}"
    echo -e "${CYAN}=========================${NC}"
    echo
    echo -e "${GREEN}📖 Project Documentation:${NC}"
    echo -e "  ${YELLOW}Project Overview:${NC} docs/PROJECT_OVERVIEW.md"
    echo -e "  ${YELLOW}Backend Services:${NC} docs/BACKEND_SERVICES.md"
    echo -e "  ${YELLOW}Frontend Application:${NC} docs/FRONTEND_APPLICATION.md"
    echo -e "  ${YELLOW}Development Workflow:${NC} docs/DEVELOPMENT_WORKFLOW.md"
    echo
    echo -e "${GREEN}🐳 Docker Documentation:${NC}"
    echo -e "  ${YELLOW}Docker Overview:${NC} docs/docker/README.md"
    echo -e "  ${YELLOW}Architecture:${NC} docs/docker/docker-architecture.md"
    echo -e "  ${YELLOW}Build Process:${NC} docs/docker/docker-build-process.md"
    echo -e "  ${YELLOW}Services:${NC} docs/docker/docker-services.md"
    echo -e "  ${YELLOW}Commands:${NC} docs/docker/docker-commands.md"
    echo
    echo -e "${GREEN}🚀 Quick Commands:${NC}"
    echo -e "  ${CYAN}./manage.sh guide project-overview${NC} - Open project overview"
    echo -e "  ${CYAN}./manage.sh guide backend-services${NC} - Open backend documentation"
    echo -e "  ${CYAN}./manage.sh guide frontend-application${NC} - Open frontend documentation"
    echo -e "  ${CYAN}./manage.sh docker-docs${NC} - View Docker documentation"
    echo
}

show_guide() {
    local guide_type="$1"
    
    case "$guide_type" in
        project-overview)
            if [[ -f "docs/PROJECT_OVERVIEW.md" ]]; then
                echo -e "${GREEN}Opening Project Overview...${NC}"
                open "docs/PROJECT_OVERVIEW.md" 2>/dev/null || cat "docs/PROJECT_OVERVIEW.md"
            else
                echo -e "${RED}Project Overview documentation not found!${NC}"
                return 1
            fi
            ;;
        backend-services)
            if [[ -f "docs/BACKEND_SERVICES.md" ]]; then
                echo -e "${GREEN}Opening Backend Services documentation...${NC}"
                open "docs/BACKEND_SERVICES.md" 2>/dev/null || cat "docs/BACKEND_SERVICES.md"
            else
                echo -e "${RED}Backend Services documentation not found!${NC}"
                return 1
            fi
            ;;
        frontend-application)
            if [[ -f "docs/FRONTEND_APPLICATION.md" ]]; then
                echo -e "${GREEN}Opening Frontend Application documentation...${NC}"
                open "docs/FRONTEND_APPLICATION.md" 2>/dev/null || cat "docs/FRONTEND_APPLICATION.md"
            else
                echo -e "${RED}Frontend Application documentation not found!${NC}"
                return 1
            fi
            ;;
        development-workflow)
            if [[ -f "docs/DEVELOPMENT_WORKFLOW.md" ]]; then
                echo -e "${GREEN}Opening Development Workflow documentation...${NC}"
                open "docs/DEVELOPMENT_WORKFLOW.md" 2>/dev/null || cat "docs/DEVELOPMENT_WORKFLOW.md"
            else
                echo -e "${RED}Development Workflow documentation not found!${NC}"
                return 1
            fi
            ;;
        *)
            echo -e "${RED}Unknown guide type: $guide_type${NC}"
            echo -e "${YELLOW}Available guides:${NC}"
            echo -e "  ${CYAN}project-overview${NC} - Complete system overview"
            echo -e "  ${CYAN}backend-services${NC} - API and Dashboard services"
            echo -e "  ${CYAN}frontend-application${NC} - Web interface and features"
            echo -e "  ${CYAN}development-workflow${NC} - Development process"
            return 1
            ;;
    esac
}

show_docker_docs() {
    echo -e "${CYAN}🐳 Docker Documentation${NC}"
    echo "======================="
    echo ""
    if [[ -d "docs/docker" ]]; then
        echo -e "${BLUE}📁 Available Docker Documentation:${NC}"
        for doc in docs/docker/*.md; do
            if [[ -f "$doc" ]]; then
                basename "$doc" .md | sed 's/docker-//' | sed 's/_/ /g' | awk '{for(i=1;i<=NF;i++) $i=toupper(substr($i,1,1)) tolower(substr($i,2)); print "  📄 " $0}'
            fi
        done
        echo ""
        echo -e "${YELLOW}Quick Access:${NC}"
        echo "  ./manage.sh guide docker-architecture  - System overview"
        echo "  ./manage.sh guide docker-build        - Build process"  
        echo "  ./manage.sh guide docker-services     - Service details"
        echo "  ./manage.sh guide docker-commands     - Command reference"
        echo ""
        echo -e "${GREEN}Or browse: docs/docker/${NC}"
    else
        echo -e "${YELLOW}⚠️  No Docker documentation found${NC}"
    fi
}

# Main script logic
case "$1" in
    validate)   run_validation ;;
    scan)       run_scan ;;
    verify)     run_verify ;;
            docs)
            show_documentation
            ;;
        docker-docs)
            show_docker_docs
            ;;
        guide)
            shift
            show_guide "$@"
            ;;
        test)       run_test ;;
    demo)       run_demo ;;
    check)      run_check ;;
    deploy)     run_deploy ;;
    build)      run_build ;;
    start)      run_start ;;
    stop)       run_stop ;;
    restart)    run_restart ;;
    logs)       run_logs "$@" ;;
    dev)        run_dev ;;
    clean)      run_clean ;;
    docs)       list_docs ;;
    docker-docs) show_docker_docs ;;
    guide)      open_guide "$@" ;;
    help|--help|-h) show_help ;;
    *)
        echo -e "${RED}❌ Unknown command: $1${NC}"
        echo ""
        show_help
        exit 1
        ;;
esac
