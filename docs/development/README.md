# ProcOS Development Documentation

## 📚 Development Guides

This directory contains comprehensive development documentation for ProcOS contributors and maintainers.

### 📋 Quick Start for Developers

1. **Read the Standards**: [`logging-standards.md`](./logging-standards.md)
2. **Follow the Workflow**: [`logging-workflow.md`](./logging-workflow.md)
3. **Use Development Tools**: `scripts/dev/`

### 📝 Logging & Code Quality

| Document | Purpose | When to Use |
|----------|---------|-------------|
| [`logging-standards.md`](./logging-standards.md) | Mandatory logging requirements | Before writing any Python code |
| [`logging-workflow.md`](./logging-workflow.md) | Daily development workflow | Every development session |

### 🛠️ Development Tools

| Tool | Purpose | Usage |
|------|---------|-------|
| `scripts/dev/validate_logging.py` | Check logging compliance | Before every commit |
| `scripts/dev/new_service_template.py` | Generate compliant service templates | When creating new services |
| `scripts/dev/dev_helpers.sh` | Common development tasks | Daily development shortcuts |

### 🚀 Quick Commands

```bash
# Validate logging compliance
python scripts/dev/validate_logging.py

# Generate new service template  
python scripts/dev/new_service_template.py worker my_worker

# Development helpers
./scripts/dev/dev_helpers.sh help

# View logs
tail -f logs/**/*.log

# Check log structure
find logs/ -name "*.log" | head -10
```

### ⚠️ Critical Requirements

**EVERY** Python file in ProcOS MUST:

1. ✅ Use centralized logging from `utils.logging_config`
2. ✅ Have appropriate logger type for file location
3. ✅ Include meaningful log messages with emojis
4. ✅ Pass logging compliance validation

**NEVER** use:
- ❌ `logging.basicConfig()`
- ❌ `logging.getLogger(__name__)`
- ❌ `print()` statements for operational output

### 📊 Logging Categories

- **Workers** (`logs/workers/`): External task processors
- **Services** (`logs/services/`): Microservices and APIs  
- **Kernel** (`logs/kernel/`): Core system components
- **Tests** (`logs/tests/`): Test scripts and validation

### 🔄 Development Workflow

1. **Before Starting**: Run `python scripts/dev/validate_logging.py`
2. **Create Services**: Use `python scripts/dev/new_service_template.py`
3. **Before Committing**: Validate compliance again
4. **Monitor Logs**: Use `tail -f logs/**/*.log`

### 🎯 Enforcement

- **Automated Validation**: Run before commits
- **Code Reviews**: Check logging compliance
- **Templates**: Use provided service templates
- **Documentation**: Follow these standards religiously

---

*These standards ensure ProcOS maintains high code quality, debuggability, and operational excellence.*