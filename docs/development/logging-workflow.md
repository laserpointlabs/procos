# ProcOS Logging Development Workflow

## 🔄 Daily Development Workflow

### Before Starting Development

1. **Check Current Compliance**
   ```bash
   python scripts/dev/validate_logging.py
   ```

2. **Review Logging Standards**
   - Read `docs/development/logging-standards.md`
   - Check `.cursor/rules/development-standards.mdc`

### Creating New Services

1. **Use the Template Generator**
   ```bash
   python scripts/dev/new_service_template.py [type] [name]
   
   # Examples:
   python scripts/dev/new_service_template.py worker email_processor
   python scripts/dev/new_service_template.py service notification_manager
   python scripts/dev/new_service_template.py kernel process_monitor
   ```

2. **Verify Template is Compliant**
   ```bash
   python scripts/dev/validate_logging.py
   ```

### Before Each Commit

1. **Run Logging Validation**
   ```bash
   python scripts/dev/validate_logging.py
   ```

2. **Fix Any Violations** (see output suggestions)

3. **Test Logging Output**
   ```bash
   # Test your service
   python -m src.workers.your_worker  # (timeout after a few seconds)
   
   # Check log files were created
   ls -la logs/workers/your_worker.log
   tail logs/workers/your_worker.log
   ```

## 🛠️ Common Development Tasks

### Converting Legacy Logging

**Old Pattern (❌ Don't use):**
```python
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
```

**New Pattern (✅ Use this):**
```python
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent))
from utils.logging_config import get_worker_logger

logger = get_worker_logger("service_name")
```

### Adding Logging to Existing Files

1. **Add the standard imports** at the top
2. **Choose appropriate logger type** based on file location
3. **Replace print() statements** with logger calls
4. **Add meaningful log messages** with emojis

### Testing Log Output

```bash
# View logs in real-time
tail -f logs/**/*.log

# View specific service logs
tail -f logs/workers/ai_worker.log

# Search all logs
grep -r "ERROR" logs/

# View logs by date
grep "2024-01-15" logs/**/*.log
```

## 🎯 Integration Points

### With Git Hooks (Future)

```bash
# Pre-commit hook (coming soon)
#!/bin/bash
python scripts/dev/validate_logging.py
if [ $? -ne 0 ]; then
    echo "❌ Logging compliance check failed"
    exit 1
fi
```

### With CI/CD Pipeline (Future)

```yaml
# GitHub Actions step (coming soon)
- name: Validate Logging Compliance
  run: python scripts/dev/validate_logging.py
```

### With IDE Integration

Add to your development environment:

1. **VSCode/Cursor Settings:**
   - Use logging templates in snippets
   - Configure linter to check for logging patterns

2. **Code Review Checklist:**
   - [ ] Uses centralized logging
   - [ ] Appropriate logger type
   - [ ] Meaningful log messages
   - [ ] No print() statements
   - [ ] Proper log levels

## 📋 Quick Reference Commands

```bash
# Validate all logging
python scripts/dev/validate_logging.py

# Generate new service template
python scripts/dev/new_service_template.py worker my_worker

# Check log directory structure
ls -la logs/

# View recent logs
find logs/ -name "*.log" -mtime -1

# Live monitoring
tail -f logs/**/*.log

# Search for errors
grep -r "ERROR\|CRITICAL" logs/

# Count log files
find logs/ -name "*.log" | wc -l
```

## 🚨 Troubleshooting

### "Missing centralized logging import"

**Problem:** File uses `logger` but doesn't import from `utils.logging_config`

**Solution:**
```python
# Add these imports
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from utils.logging_config import get_service_logger

logger = get_service_logger("my_service")
```

### "Wrong logger type for file location"

**Problem:** Using `get_worker_logger()` in a script file

**Solution:** Use the appropriate logger type:
- **Workers:** `get_worker_logger()`
- **Services/Scripts:** `get_service_logger()`
- **Kernel:** `get_kernel_logger()`
- **Tests:** `get_test_logger()`

### "Log files not being created"

**Check:**
1. Logs directory exists: `ls -la logs/`
2. Proper logger import and initialization
3. Service is actually running and logging
4. File permissions on logs directory

## 💡 Best Practices

1. **Always validate before committing**
2. **Use descriptive service names** in logger initialization  
3. **Include context in log messages** (IDs, counts, etc.)
4. **Use appropriate log levels** (DEBUG for development, INFO for operations)
5. **Add emojis for visual categorization** 🚀 ✅ ❌ ⚠️
6. **Test your logging** by running the service briefly

---

*Following this workflow ensures consistent, high-quality logging across all ProcOS development.*