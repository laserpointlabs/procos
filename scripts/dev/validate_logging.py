#!/usr/bin/env python3
"""
ProcOS Logging Compliance Validator

Checks all Python files for compliance with centralized logging standards.
Run this before commits to ensure logging consistency.

Author: ProcOS Development Team
License: MIT
"""

import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple

# Add src to path
sys.path.append(str(Path(__file__).parent.parent.parent / "src"))
from utils.logging_config import get_service_logger

logger = get_service_logger("logging_validator")

class LoggingValidator:
    """Validates Python files for logging compliance"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.violations = []
        
    def validate_all_files(self) -> bool:
        """Validate all Python files in the project"""
        logger.info("🔍 Starting logging compliance validation...")
        
        # Find all Python files
        python_files = []
        for pattern in ['src/**/*.py', 'scripts/**/*.py']:
            python_files.extend(self.project_root.glob(pattern))
        
        # Exclude certain files
        excluded = ['__init__.py', 'utils/logging_config.py']
        python_files = [f for f in python_files if f.name not in excluded]
        
        logger.info(f"📋 Checking {len(python_files)} Python files...")
        
        compliant_count = 0
        for file_path in python_files:
            if self.validate_file(file_path):
                compliant_count += 1
            
        total_files = len(python_files)
        violation_count = len(self.violations)
        
        logger.info(f"📊 Validation Results:")
        logger.info(f"  ✅ Compliant files: {compliant_count}/{total_files}")
        logger.info(f"  ❌ Files with violations: {violation_count}")
        
        if self.violations:
            logger.warning("⚠️  LOGGING COMPLIANCE VIOLATIONS FOUND:")
            for violation in self.violations:
                logger.warning(f"  • {violation}")
            return False
        else:
            logger.info("🎉 All files are logging compliant!")
            return True
    
    def validate_file(self, file_path: Path) -> bool:
        """Validate a single Python file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            relative_path = file_path.relative_to(self.project_root)
            violations = []
            
            # Check for legacy logging patterns
            legacy_patterns = [
                (r'logging\.basicConfig\s*\(', 'Uses logging.basicConfig() instead of centralized logging'),
                (r'logging\.getLogger\s*\([^)]*__name__[^)]*\)', 'Uses logging.getLogger(__name__) instead of centralized logging'),
                (r'print\s*\([^)]*\)', 'Uses print() statements for output (consider using logger)'),
            ]
            
            for pattern, message in legacy_patterns:
                if re.search(pattern, content):
                    violations.append(f"{relative_path}: {message}")
            
            # Check for centralized logging import (if file uses logging)
            uses_logging = bool(re.search(r'logger\s*=|logger\.', content))
            has_centralized_import = bool(re.search(r'from utils\.logging_config import', content))
            
            if uses_logging and not has_centralized_import:
                violations.append(f"{relative_path}: Uses logging but missing centralized logging import")
            
            # Check for appropriate logger types based on file location
            if has_centralized_import:
                expected_logger_types = self._get_expected_logger_types(relative_path)
                if expected_logger_types:
                    found_logger_type = self._extract_logger_type(content)
                    if found_logger_type and found_logger_type not in expected_logger_types:
                        violations.append(
                            f"{relative_path}: Uses {found_logger_type} but expected {' or '.join(expected_logger_types)} "
                            f"based on file location"
                        )
            
            self.violations.extend(violations)
            return len(violations) == 0
            
        except Exception as e:
            logger.error(f"❌ Error validating {file_path}: {e}")
            return False
    
    def _get_expected_logger_types(self, file_path: Path) -> List[str]:
        """Get expected logger types based on file location"""
        path_str = str(file_path)
        
        if 'workers/' in path_str:
            return ['get_worker_logger']
        elif 'microkernel/' in path_str or 'kernel/' in path_str:
            return ['get_kernel_logger']
        elif 'services/' in path_str or 'scripts/' in path_str:
            return ['get_service_logger']
        elif 'test' in path_str.lower():
            return ['get_test_logger']
        
        # For other locations, any type is acceptable
        return []
    
    def _extract_logger_type(self, content: str) -> str:
        """Extract the logger type being used"""
        pattern = r'(get_\w+_logger)\s*\('
        match = re.search(pattern, content)
        return match.group(1) if match else None
    
    def check_log_directory_structure(self) -> bool:
        """Verify log directory structure exists"""
        logger.info("🗂️  Checking log directory structure...")
        
        required_dirs = ['logs', 'logs/workers', 'logs/services', 'logs/kernel', 'logs/tests']
        missing_dirs = []
        
        for dir_path in required_dirs:
            full_path = self.project_root / dir_path
            if not full_path.exists():
                missing_dirs.append(dir_path)
        
        if missing_dirs:
            logger.error(f"❌ Missing log directories: {missing_dirs}")
            return False
        else:
            logger.info("✅ Log directory structure is correct")
            return True
    
    def suggest_fixes(self):
        """Provide suggestions for fixing violations"""
        if not self.violations:
            return
        
        logger.info("💡 SUGGESTED FIXES:")
        logger.info("")
        logger.info("1. Replace legacy logging with centralized logging:")
        logger.info("   ❌ logging.basicConfig(...)")
        logger.info("   ❌ logger = logging.getLogger(__name__)")
        logger.info("   ✅ from utils.logging_config import get_service_logger")
        logger.info("   ✅ logger = get_service_logger('my_service')")
        logger.info("")
        logger.info("2. Add the required import pattern to files missing it:")
        logger.info("   ✅ sys.path.append(str(Path(__file__).parent.parent))")
        logger.info("   ✅ from utils.logging_config import get_[TYPE]_logger")
        logger.info("")
        logger.info("3. Replace print() statements with appropriate logging:")
        logger.info("   ❌ print('Service started')")
        logger.info("   ✅ logger.info('🚀 Service started')")
        logger.info("")
        logger.info("4. Use appropriate logger types based on file location:")
        logger.info("   • Workers: get_worker_logger()")
        logger.info("   • Services/Scripts: get_service_logger()")
        logger.info("   • Kernel: get_kernel_logger()")
        logger.info("   • Tests: get_test_logger()")

def main():
    """Main validation function"""
    validator = LoggingValidator()
    
    # Check directory structure
    structure_ok = validator.check_log_directory_structure()
    
    # Validate all files
    compliance_ok = validator.validate_all_files()
    
    # Provide suggestions if there are issues
    if not compliance_ok:
        validator.suggest_fixes()
    
    # Exit with appropriate code
    if structure_ok and compliance_ok:
        logger.info("🎯 All logging standards are met!")
        sys.exit(0)
    else:
        logger.error("💥 Logging compliance check FAILED")
        logger.error("Please fix the violations above before committing")
        sys.exit(1)

if __name__ == "__main__":
    main()