#!/bin/bash

# =============================================================================
# ProcOS Startup Script
# One-command startup for the entire ProcOS system
# =============================================================================

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
COMPOSE_FILE="$PROJECT_ROOT/docker-compose.yml"
ENV_FILE="$PROJECT_ROOT/.env"
ENV_EXAMPLE="$PROJECT_ROOT/env.example"

# Functions
print_header() {
    echo -e "${PURPLE}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                                                              ║"
    echo "║  ██████╗ ██████╗  ██████╗  ██████╗ ██████╗ ███████╗         ║"
    echo "║  ██╔══██╗██╔══██╗██╔═══██╗██╔════╝██╔═══██╗██╔════╝         ║"
    echo "║  ██████╔╝██████╔╝██║   ██║██║     ██║   ██║███████╗         ║"
    echo "║  ██╔═══╝ ██╔══██╗██║   ██║██║     ██║   ██║╚════██║         ║"
    echo "║  ██║     ██║  ██║╚██████╔╝╚██████╗╚██████╔╝███████║         ║"
    echo "║  ╚═╝     ╚═╝  ╚═╝ ╚═════╝  ╚═════╝ ╚═════╝ ╚══════╝         ║"
    echo "║                                                              ║"
    echo "║           Process-Oriented Operating System                  ║"
    echo "║                  🚀 Quick Start 🚀                          ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

print_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_dependencies() {
    print_step "Checking system dependencies..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed. Please install Python 3.8+ first."
        exit 1
    fi
    
    # Check pip
    if ! command -v pip3 &> /dev/null; then
        print_error "pip3 is not installed. Please install pip3 first."
        exit 1
    fi
    
    print_success "All dependencies are available"
}

setup_environment() {
    print_step "Setting up environment configuration..."
    
    cd "$PROJECT_ROOT"
    
    # Create .env file if it doesn't exist
    if [ ! -f "$ENV_FILE" ]; then
        if [ -f "$ENV_EXAMPLE" ]; then
            cp "$ENV_EXAMPLE" "$ENV_FILE"
            print_success "Created .env file from template"
        else
            print_warning ".env.example not found, creating basic .env file"
            cat > "$ENV_FILE" << EOF
PROCOS_ENV=development
LOG_LEVEL=INFO
CAMUNDA_BASE_URL=http://localhost:8080
RABBITMQ_HOST=localhost
RABBITMQ_USERNAME=procos
RABBITMQ_PASSWORD=procos123
EOF
        fi
    else
        print_success "Environment file already exists"
    fi
}

install_python_dependencies() {
    print_step "Installing Python dependencies..."
    
    cd "$PROJECT_ROOT"
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        print_step "Creating Python virtual environment..."
        python3 -m venv venv
        print_success "Virtual environment created"
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Install dependencies
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
        print_success "Python dependencies installed"
    else
        print_warning "requirements.txt not found, skipping Python dependencies"
    fi
}

start_infrastructure() {
    print_step "Starting ProcOS infrastructure (Camunda, RabbitMQ, Redis)..."
    
    cd "$PROJECT_ROOT"
    
    # Start Docker containers
    if command -v docker-compose &> /dev/null; then
        docker-compose up -d
    else
        docker compose up -d
    fi
    
    print_success "Infrastructure containers started"
}

wait_for_services() {
    print_step "Waiting for services to be ready..."
    
    # Wait for Camunda
    echo -n "Waiting for Camunda engine"
    for i in {1..30}; do
        if curl -f -s http://localhost:8080/engine-rest/engine > /dev/null 2>&1; then
            echo ""
            print_success "Camunda engine is ready"
            break
        fi
        echo -n "."
        sleep 2
    done
    
    # Wait for RabbitMQ
    echo -n "Waiting for RabbitMQ"
    for i in {1..20}; do
        if curl -f -s http://localhost:15672 > /dev/null 2>&1; then
            echo ""
            print_success "RabbitMQ is ready"
            break
        fi
        echo -n "."
        sleep 2
    done
    
    # Wait for Redis
    echo -n "Waiting for Redis"
    for i in {1..15}; do
        if redis-cli -h localhost ping > /dev/null 2>&1; then
            echo ""
            print_success "Redis is ready"
            break
        fi
        echo -n "."
        sleep 1
    done
}

deploy_processes() {
    print_step "Deploying BPMN processes..."
    
    cd "$PROJECT_ROOT"
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Deploy processes (if script exists)
    if [ -f "scripts/deploy_processes.py" ]; then
        python scripts/deploy_processes.py
        print_success "BPMN processes deployed"
    else
        print_warning "Process deployment script not found, skipping process deployment"
    fi
}

start_microkernel() {
    print_step "Starting ProcOS microkernel..."
    
    cd "$PROJECT_ROOT"
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Start microkernel (if it exists)
    if [ -f "src/microkernel/procos_kernel.py" ]; then
        echo "Starting microkernel in background..."
        python -m src.microkernel.procos_kernel &
        MICROKERNEL_PID=$!
        echo $MICROKERNEL_PID > microkernel.pid
        print_success "ProcOS microkernel started (PID: $MICROKERNEL_PID)"
    else
        print_warning "Microkernel not found, will need to be started manually"
    fi
}

start_workers() {
    print_step "Workers deprecated — using PDO/TDE model"
    
    cd "$PROJECT_ROOT"
    
    echo "External task workers have been absorbed into PDO/TDE BPMN design."
    echo "No worker processes will be started from this script."
    print_success "Proceeding without legacy workers"
}

show_status() {
    print_step "ProcOS System Status:"
    echo ""
    echo -e "${GREEN}🎯 ProcOS is ready!${NC}"
    echo ""
    echo "📊 Service URLs:"
    echo "  • Camunda Engine:    http://localhost:8080"
    echo "  • Camunda Cockpit:   http://localhost:8080/camunda"
    echo "  • RabbitMQ Admin:    http://localhost:15672 (procos/procos123)"
    echo "  • Redis:             localhost:6379"
    echo "  • Ollama API:        http://localhost:11434"
    echo ""
    echo "🔧 Management Commands:"
    echo "  • Stop system:       ./scripts/stop.sh"
    echo "  • View logs:         docker-compose logs -f"
    echo "  • Health check:      ./scripts/health_check.py"
    echo ""
    echo "🚀 Quick Test:"
    echo "  curl -X POST http://localhost:8080/engine-rest/deployment/create \\"
    echo "       -F 'deployment-name=test' \\"
    echo "       -F 'deployment-source=process application' \\"
    echo "       -F 'tenant-id=procos'"
    echo ""
}

# Main execution
main() {
    print_header
    
    # Parse command line arguments
    SKIP_DEPS=false
    SKIP_INSTALL=false
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --skip-deps)
                SKIP_DEPS=true
                shift
                ;;
            --skip-install)
                SKIP_INSTALL=true
                shift
                ;;
            -h|--help)
                echo "Usage: $0 [options]"
                echo "Options:"
                echo "  --skip-deps     Skip dependency checking"
                echo "  --skip-install  Skip Python dependency installation"
                echo "  -h, --help      Show this help message"
                exit 0
                ;;
            *)
                print_error "Unknown option: $1"
                exit 1
                ;;
        esac
    done
    
    # Execute startup steps
    if [ "$SKIP_DEPS" = false ]; then
        check_dependencies
    fi
    
    setup_environment
    
    if [ "$SKIP_INSTALL" = false ]; then
        install_python_dependencies
    fi
    
    start_infrastructure
    wait_for_services
    deploy_processes
    start_microkernel
    start_workers
    show_status
    
    print_success "ProcOS startup complete! 🎉"
}

# Run main function
main "$@"