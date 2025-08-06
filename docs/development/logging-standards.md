# ProcOS Logging Standards

## Overview

This document defines the mandatory logging standards for all ProcOS development. Following these standards ensures consistent, maintainable, and debuggable code across the entire system.

## 🚨 MANDATORY REQUIREMENTS

### 1. **Use Centralized Logging Configuration**

**ALL** Python files MUST use the centralized logging system:

```python
# ✅ CORRECT - Use centralized logging
import sys
from pathlib import Path

# Add src to path (adjust relative path as needed)
sys.path.append(str(Path(__file__).parent.parent))  # From workers/
sys.path.append(str(Path(__file__).parent.parent / "src"))  # From scripts/

from utils.logging_config import get_worker_logger, get_service_logger, get_kernel_logger, get_test_logger

# Choose appropriate logger type
logger = get_worker_logger("my_worker")        # For workers
logger = get_service_logger("my_service")      # For services  
logger = get_kernel_logger("my_component")     # For kernel components
logger = get_test_logger("my_test")            # For tests

# ❌ WRONG - Don't use basic logging
import logging
logging.basicConfig(...)  # DON'T DO THIS
logger = logging.getLogger(__name__)  # DON'T DO THIS
```

### 2. **Logging Categories and File Locations**

| Service Type | Function | Log Directory | Example |
|--------------|----------|---------------|---------|
| **Workers** | External task processors | `logs/workers/` | `ai_worker.log`, `generic_worker.log` |
| **Services** | Microservices & APIs | `logs/services/` | `context_manager.log`, `deploy_processes.log` |
| **Kernel** | Core system components | `logs/kernel/` | `kernel.log`, `orchestrator.log` |
| **Tests** | Test scripts & validation | `logs/tests/` | `integration_test.log`, `unit_test.log` |

### 3. **Required Import Pattern**

**Standard Template for ALL new Python files:**

```python
#!/usr/bin/env python3
"""
Brief description of the file/service
"""

# Standard imports
import sys
from pathlib import Path

# Add src to path - ADJUST PATH AS NEEDED
sys.path.append(str(Path(__file__).parent.parent))  # From src/workers/, src/services/
# OR
sys.path.append(str(Path(__file__).parent.parent / "src"))  # From scripts/, tests/

# Import centralized logging - MANDATORY
from utils.logging_config import get_[TYPE]_logger

# Create logger - MANDATORY  
logger = get_[TYPE]_logger("[SERVICE_NAME]")

# Rest of your code...
```

### 4. **Log Level Usage Guidelines**

| Level | When to Use | Example |
|-------|-------------|---------|
| `DEBUG` | Development info, variable dumps, detailed flow | `logger.debug(f"Processing variable: {data}")` |
| `INFO` | Normal operation, status updates, key events | `logger.info("🚀 Service started successfully")` |
| `WARNING` | Concerning but recoverable situations | `logger.warning("⚠️ Retry attempt 3/5")` |
| `ERROR` | Errors that don't crash the service | `logger.error("❌ Failed to connect to database")` |
| `CRITICAL` | Fatal errors that will crash the service | `logger.critical("💥 Critical system failure")` |

### 5. **Message Format Standards**

- **Use emojis** for visual categorization: 🚀 ✅ ❌ ⚠️ 🔍 📋 💾 🌐
- **Be descriptive** but concise
- **Include context** when helpful (IDs, counts, timings)
- **Use structured data** for complex information

```python
# ✅ GOOD examples
logger.info("🚀 AI Worker ai_worker_001 started successfully")
logger.error("❌ Failed to deploy process: system_orchestrator.bpmn")
logger.debug(f"🔍 Processing task {task.id} with {len(variables)} variables")

# ❌ AVOID
logger.info("started")  # Too vague
logger.error("error occurred")  # No context
logger.debug("here")  # Useless
```

## 🔧 Development Workflow Integration

### Pre-commit Checklist

Before committing ANY Python file, ensure:

- [ ] Uses centralized logging (`from utils.logging_config import...`)
- [ ] Has appropriate logger type (`get_worker_logger`, `get_service_logger`, etc.)
- [ ] No `logging.basicConfig()` or `logging.getLogger(__name__)` calls
- [ ] Descriptive log messages with emojis
- [ ] Appropriate log levels used

### Code Review Requirements

**ALL** code reviews must verify:

1. **Logging Import**: Uses centralized logging configuration
2. **Proper Category**: Correct logger type for the service
3. **Message Quality**: Descriptive, categorized messages
4. **No Legacy Logging**: No basic logging or print statements

### New Service Template

When creating new services, copy this template:

```python
#!/usr/bin/env python3
"""
[SERVICE_NAME] - Brief description

Author: ProcOS Development Team
License: MIT
"""

import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent))
from utils.logging_config import get_service_logger  # Adjust logger type

logger = get_service_logger("[service_name]")

class [ServiceName]:
    def __init__(self):
        logger.info(f"🚀 {self.__class__.__name__} initializing...")
        # ... initialization code ...
        logger.info(f"✅ {self.__class__.__name__} ready")

    def main_operation(self):
        try:
            logger.info("📋 Starting main operation...")
            # ... operation code ...
            logger.info("✅ Operation completed successfully")
            
        except Exception as e:
            logger.error(f"❌ Operation failed: {e}")
            raise

if __name__ == "__main__":
    service = [ServiceName]()
    service.main_operation()
```

## 🚫 Common Mistakes to Avoid

### ❌ DON'T DO THESE:

```python
# DON'T use basic logging
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# DON'T use print statements for operational info
print("Service started")  # Use logger.info() instead

# DON'T use vague messages
logger.info("done")  # What's done?
logger.error("failed")  # What failed? Why?

# DON'T mix logging styles in one file
logger1 = logging.getLogger("one")
logger2 = get_service_logger("two")  # Pick one approach

# DON'T forget emojis and context
logger.info("Processing")  # Better: logger.info("📋 Processing 15 tasks...")
```

## 🔍 Validation Tools

### Quick Check Command

Run this to verify logging compliance:

```bash
# Check for legacy logging patterns
grep -r "logging.basicConfig\|logging.getLogger" src/ scripts/ --exclude-dir=__pycache__

# Should return only utils/logging_config.py
```

### Log File Verification

```bash
# Verify logs are being created correctly
find logs/ -name "*.log" -mtime -1  # Files modified in last day
tail -f logs/**/*.log  # Live monitoring
```

## 📚 Environment Configuration

Set these environment variables for optimal logging:

```env
# .env file
LOG_LEVEL=INFO          # Console log level
FILE_LOG_LEVEL=DEBUG    # File log level (more detailed)
```

## 🎯 Enforcement

### Automated Checks (Coming Soon)

- Pre-commit hooks to check logging imports
- CI/CD pipeline verification
- Automated code quality reports

### Manual Review Points

- **New PRs**: Must use centralized logging
- **Refactoring**: Opportunity to upgrade legacy logging
- **Bug fixes**: Check if better logging would help debugging

---

## 💡 Remember

**Good logging is not optional in ProcOS.** It's essential for:
- **Debugging** complex process flows
- **Monitoring** system health in production  
- **Understanding** service interactions
- **Troubleshooting** issues across distributed components

When in doubt, **log more rather than less**, but keep it **structured and meaningful**.

---

*This document is enforced for ALL ProcOS development. No exceptions.*