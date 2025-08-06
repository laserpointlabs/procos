#!/bin/bash

# ProcOS Development Helper Commands
# Collection of useful development commands for ProcOS

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_help() {
    echo -e "${BLUE}ProcOS Development Helpers${NC}"
    echo ""
    echo "Usage: $0 [command]"
    echo ""
    echo "Commands:"
    echo "  validate-logging    Check logging compliance"
    echo "  create-service      Generate new service template"
    echo "  view-logs          View recent log activity"
    echo "  clean-logs         Clean old log files"
    echo "  test-logging       Test logging system"
    echo "  help               Show this help"
    echo ""
}

validate_logging() {
    echo -e "${BLUE}🔍 Validating Logging Compliance...${NC}"
    python scripts/dev/validate_logging.py
}

create_service() {
    echo -e "${BLUE}🔧 Creating New Service...${NC}"
    echo "Service types: worker, service, kernel, script, test"
    read -p "Enter service type: " service_type
    read -p "Enter service name: " service_name
    
    python scripts/dev/new_service_template.py "$service_type" "$service_name"
}

view_logs() {
    echo -e "${BLUE}📋 Recent Log Activity...${NC}"
    echo ""
    echo "Recent log files:"
    find logs/ -name "*.log" -mtime -1 2>/dev/null || echo "No recent log files found"
    echo ""
    echo "Log file counts by category:"
    for dir in logs/*/; do
        if [ -d "$dir" ]; then
            count=$(find "$dir" -name "*.log" 2>/dev/null | wc -l)
            echo "  $(basename "$dir"): $count files"
        fi
    done
    echo ""
    echo "Recent errors:"
    grep -r "ERROR\|CRITICAL" logs/ --include="*.log" | tail -5 2>/dev/null || echo "No recent errors found"
}

clean_logs() {
    echo -e "${YELLOW}🧹 Cleaning Old Logs...${NC}"
    echo "This will remove log files older than 7 days"
    read -p "Continue? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        find logs/ -name "*.log" -mtime +7 -delete 2>/dev/null || true
        echo -e "${GREEN}✅ Old logs cleaned${NC}"
    else
        echo "Cancelled"
    fi
}

test_logging() {
    echo -e "${BLUE}🧪 Testing Logging System...${NC}"
    
    # Create a temporary test file in the project
    cat > test_logging_temp.py << EOF
import sys
from pathlib import Path
sys.path.append(str(Path.cwd() / "src"))
from utils.logging_config import get_test_logger

logger = get_test_logger("dev_test")
logger.debug("🔍 Debug message")
logger.info("ℹ️ Info message") 
logger.warning("⚠️ Warning message")
logger.error("❌ Error message")
print("Test completed - check logs/tests/dev_test.log")
EOF

    python test_logging_temp.py
    rm test_logging_temp.py
    
    echo "Log file contents:"
    tail -5 logs/tests/dev_test.log 2>/dev/null || echo "Log file not found"
}

# Main command handling
case "${1:-help}" in
    validate-logging)
        validate_logging
        ;;
    create-service)
        create_service
        ;;
    view-logs)
        view_logs
        ;;
    clean-logs)
        clean_logs
        ;;
    test-logging)
        test_logging
        ;;
    help|*)
        print_help
        ;;
esac