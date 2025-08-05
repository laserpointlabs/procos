#!/bin/bash
# ProcOS Ollama Model Management Script

set -euo pipefail

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
OLLAMA_URL="http://localhost:11434"
DEFAULT_MODEL="llama3.2:3b"

print_header() {
    echo -e "${BLUE}"
    echo "╔══════════════════════════════════════════════════════════════════════════════╗"
    echo "║                         ProcOS Ollama Model Manager                          ║"
    echo "╚══════════════════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

print_step() {
    echo -e "${YELLOW}📋 $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

check_ollama_running() {
    print_step "Checking if Ollama is running..."
    
    if curl -s "$OLLAMA_URL/api/tags" > /dev/null 2>&1; then
        print_success "Ollama is running and accessible"
        return 0
    else
        print_error "Ollama is not running or not accessible at $OLLAMA_URL"
        echo "Please ensure the ProcOS infrastructure is started:"
        echo "  ./scripts/start.sh"
        exit 1
    fi
}

list_models() {
    print_step "Listing available models..."
    
    response=$(curl -s "$OLLAMA_URL/api/tags")
    
    if [ "$(echo "$response" | jq -r '.models | length')" -eq 0 ]; then
        echo "No models installed"
    else
        echo "$response" | jq -r '.models[] | "\(.name) (\(.size | . / 1024 / 1024 / 1024 | floor)GB)"'
    fi
}

pull_model() {
    local model_name="$1"
    print_step "Pulling model: $model_name"
    
    echo "This may take several minutes depending on the model size..."
    
    # Use curl to stream the pull process
    curl -X POST "$OLLAMA_URL/api/pull" \
        -H "Content-Type: application/json" \
        -d "{\"name\":\"$model_name\"}" \
        --no-buffer \
        -s | while IFS= read -r line; do
            if [ -n "$line" ]; then
                status=$(echo "$line" | jq -r '.status // empty')
                if [ -n "$status" ]; then
                    echo "Status: $status"
                fi
                
                completed=$(echo "$line" | jq -r '.completed // empty')
                total=$(echo "$line" | jq -r '.total // empty')
                if [ -n "$completed" ] && [ -n "$total" ]; then
                    percent=$((completed * 100 / total))
                    echo "Progress: $percent% ($completed/$total bytes)"
                fi
            fi
        done
    
    print_success "Model $model_name pulled successfully"
}

remove_model() {
    local model_name="$1"
    print_step "Removing model: $model_name"
    
    curl -X DELETE "$OLLAMA_URL/api/delete" \
        -H "Content-Type: application/json" \
        -d "{\"name\":\"$model_name\"}"
    
    print_success "Model $model_name removed successfully"
}

test_model() {
    local model_name="$1"
    print_step "Testing model: $model_name"
    
    echo "Sending test query to $model_name..."
    
    response=$(curl -s -X POST "$OLLAMA_URL/api/generate" \
        -H "Content-Type: application/json" \
        -d "{
            \"model\":\"$model_name\",
            \"prompt\":\"What is ProcOS?\",
            \"stream\":false
        }")
    
    if [ $? -eq 0 ]; then
        echo "Response:"
        echo "$response" | jq -r '.response'
        print_success "Model $model_name is working correctly"
    else
        print_error "Failed to test model $model_name"
    fi
}

setup_default_models() {
    print_step "Setting up recommended models for ProcOS..."
    
    # Pull recommended models
    models=(
        "llama3.2:3b"      # Fast, general purpose
        "llama3.2:1b"      # Ultra-fast for simple tasks
        "codellama:7b"     # Code generation
    )
    
    for model in "${models[@]}"; do
        echo ""
        echo "Pulling $model..."
        pull_model "$model"
    done
    
    print_success "Default models setup complete"
}

show_usage() {
    echo "Usage: $0 [command] [options]"
    echo ""
    echo "Commands:"
    echo "  list                    List installed models"
    echo "  pull <model_name>       Pull a specific model"
    echo "  remove <model_name>     Remove a specific model"
    echo "  test <model_name>       Test a specific model"
    echo "  setup                   Setup recommended models for ProcOS"
    echo "  status                  Check Ollama status"
    echo ""
    echo "Examples:"
    echo "  $0 list"
    echo "  $0 pull llama3.2:3b"
    echo "  $0 test llama3.2:3b"
    echo "  $0 setup"
    echo ""
    echo "Recommended models:"
    echo "  • llama3.2:1b    - Ultra-fast (1.3GB)"
    echo "  • llama3.2:3b    - Balanced (2.0GB)"
    echo "  • llama3.1:8b    - High quality (4.7GB)"
    echo "  • codellama:7b   - Code generation (3.8GB)"
    echo "  • mistral:7b     - Alternative option (4.1GB)"
}

main() {
    print_header
    
    case "${1:-}" in
        "list")
            check_ollama_running
            list_models
            ;;
        "pull")
            if [ -z "${2:-}" ]; then
                print_error "Model name required"
                show_usage
                exit 1
            fi
            check_ollama_running
            pull_model "$2"
            ;;
        "remove")
            if [ -z "${2:-}" ]; then
                print_error "Model name required"
                show_usage
                exit 1
            fi
            check_ollama_running
            remove_model "$2"
            ;;
        "test")
            if [ -z "${2:-}" ]; then
                print_error "Model name required"
                show_usage
                exit 1
            fi
            check_ollama_running
            test_model "$2"
            ;;
        "setup")
            check_ollama_running
            setup_default_models
            ;;
        "status")
            check_ollama_running
            list_models
            ;;
        *)
            show_usage
            ;;
    esac
}

# Check if jq is available
if ! command -v jq &> /dev/null; then
    print_error "jq is required but not installed"
    echo "Please install jq: sudo apt-get install jq"
    exit 1
fi

main "$@"