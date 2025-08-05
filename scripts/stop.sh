#!/bin/bash

# =============================================================================
# ProcOS Stop Script
# Gracefully shutdown all ProcOS components
# =============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

print_step() {
    echo -e "${BLUE}[STOP]${NC} $1"
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

stop_workers() {
    print_step "Stopping ProcOS workers..."
    
    cd "$PROJECT_ROOT"
    
    # Stop workers by PID files
    for pidfile in *.pid; do
        if [ -f "$pidfile" ]; then
            pid=$(cat "$pidfile")
            if kill -0 "$pid" 2>/dev/null; then
                echo "Stopping $(basename "$pidfile" .pid) (PID: $pid)"
                kill "$pid"
                rm "$pidfile"
            else
                print_warning "Process $pid from $pidfile not running"
                rm "$pidfile"
            fi
        fi
    done
    
    print_success "Workers stopped"
}

stop_infrastructure() {
    print_step "Stopping ProcOS infrastructure..."
    
    cd "$PROJECT_ROOT"
    
    # Stop Docker containers
    if command -v docker-compose &> /dev/null; then
        docker-compose down
    else
        docker compose down
    fi
    
    print_success "Infrastructure stopped"
}

cleanup() {
    print_step "Cleaning up temporary files..."
    
    cd "$PROJECT_ROOT"
    
    # Remove any remaining PID files
    rm -f *.pid
    
    # Clean up any temporary process files
    rm -f /tmp/procos_*
    
    print_success "Cleanup complete"
}

main() {
    echo -e "${BLUE}"
    echo "╔══════════════════════════════════════╗"
    echo "║            ProcOS Stop               ║"
    echo "║     Graceful System Shutdown         ║"
    echo "╚══════════════════════════════════════╝"
    echo -e "${NC}"
    
    stop_workers
    stop_infrastructure
    cleanup
    
    print_success "ProcOS shutdown complete! 👋"
}

# Run main function
main "$@"