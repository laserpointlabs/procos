#!/usr/bin/env python3
"""
ProcOS New Service Template Generator

Generates boilerplate code for new ProcOS services with proper logging configuration.

Usage: python scripts/dev/new_service_template.py [service_type] [service_name]

Author: ProcOS Development Team
License: MIT
"""

import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent.parent / "src"))
from utils.logging_config import get_service_logger

logger = get_service_logger("template_generator")

def generate_service_template(service_type: str, service_name: str) -> str:
    """Generate a service template with proper logging"""
    
    # Determine logger type and path based on service type
    logger_mapping = {
        'worker': ('get_worker_logger', 'src/workers', 'External task worker'),
        'service': ('get_service_logger', 'src/services', 'Microservice component'),
        'kernel': ('get_kernel_logger', 'src/kernel', 'Kernel component'),
        'script': ('get_service_logger', 'scripts', 'Utility script'),
        'test': ('get_test_logger', 'tests', 'Test script')
    }
    
    if service_type not in logger_mapping:
        raise ValueError(f"Unknown service type: {service_type}. Valid types: {list(logger_mapping.keys())}")
    
    logger_func, base_path, description = logger_mapping[service_type]
    
    # Determine relative path for import
    if base_path.startswith('src/'):
        import_path = "str(Path(__file__).parent.parent)"
    else:
        import_path = "str(Path(__file__).parent.parent / \"src\")"
    
    template = f'''#!/usr/bin/env python3
"""
{service_name.title()} - {description}

TODO: Add detailed description of what this service does

Author: ProcOS Development Team
License: MIT
"""

import sys
from pathlib import Path

# Add src to path
sys.path.append({import_path})
from utils.logging_config import {logger_func}

logger = {logger_func}("{service_name}")

class {service_name.title().replace('_', '')}:
    """
    {service_name.title()} implementation
    
    TODO: Add class documentation
    """
    
    def __init__(self):
        logger.info(f"🚀 {{self.__class__.__name__}} initializing...")
        
        # TODO: Add initialization code here
        
        logger.info(f"✅ {{self.__class__.__name__}} ready")
    
    def main_operation(self):
        """Main service operation"""
        try:
            logger.info("📋 Starting main operation...")
            
            # TODO: Implement main service logic here
            
            logger.info("✅ Operation completed successfully")
            
        except Exception as e:
            logger.error(f"❌ Operation failed: {{e}}")
            raise
    
    def health_check(self) -> bool:
        """Service health check"""
        try:
            # TODO: Implement health check logic
            logger.debug("🔍 Health check passed")
            return True
        except Exception as e:
            logger.warning(f"⚠️ Health check failed: {{e}}")
            return False

def main():
    """Main entry point"""
    try:
        service = {service_name.title().replace('_', '')}()
        service.main_operation()
        
    except KeyboardInterrupt:
        logger.info("📴 Service stopped by user")
    except Exception as e:
        logger.error(f"💥 Service failed: {{e}}")
        sys.exit(1)

if __name__ == "__main__":
    main()
'''
    
    return template

def main():
    """Main function"""
    if len(sys.argv) != 3:
        logger.error("❌ Usage: python new_service_template.py [service_type] [service_name]")
        logger.info("Valid service types: worker, service, kernel, script, test")
        logger.info("Example: python new_service_template.py worker email_processor")
        sys.exit(1)
    
    service_type = sys.argv[1].lower()
    service_name = sys.argv[2].lower()
    
    try:
        logger.info(f"🔧 Generating {service_type} template for '{service_name}'...")
        
        template = generate_service_template(service_type, service_name)
        
        # Determine output path
        logger_mapping = {
            'worker': 'src/workers',
            'service': 'src/services', 
            'kernel': 'src/kernel',
            'script': 'scripts',
            'test': 'tests'
        }
        
        output_dir = Path(logger_mapping[service_type])
        output_dir.mkdir(parents=True, exist_ok=True)
        output_file = output_dir / f"{service_name}.py"
        
        if output_file.exists():
            logger.warning(f"⚠️ File already exists: {output_file}")
            response = input("Overwrite? (y/N): ")
            if response.lower() != 'y':
                logger.info("📴 Template generation cancelled")
                return
        
        # Write template
        with open(output_file, 'w') as f:
            f.write(template)
        
        # Make executable if it's a script
        if service_type in ['script', 'test']:
            output_file.chmod(0o755)
        
        logger.info(f"✅ Template created: {output_file}")
        logger.info("🎯 Next steps:")
        logger.info(f"  1. Edit {output_file}")
        logger.info("  2. Replace TODO comments with actual implementation")
        logger.info("  3. Test the service")
        logger.info("  4. Run: python scripts/dev/validate_logging.py")
        
    except Exception as e:
        logger.error(f"❌ Template generation failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()