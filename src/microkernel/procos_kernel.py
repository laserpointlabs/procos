#!/usr/bin/env python3
"""
ProcOS Microkernel - The Heart of Process-Oriented Computing

This is the minimal bootstrap kernel that:
1. Validates the environment
2. Starts the Camunda BPMN engine
3. Deploys root orchestration processes
4. Monitors system health
5. Goes to sleep (everything else is handled by BPMN processes)

Author: ProcOS Development Team
License: MIT
"""

import asyncio
import logging
import os
import signal
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional

import requests
from dotenv import load_dotenv
from rich.console import Console
from rich.logging import RichHandler
from rich.panel import Panel

# Load environment variables
load_dotenv()

# Setup logging using centralized configuration
sys.path.append(str(Path(__file__).parent.parent))
from utils.logging_config import get_kernel_logger

logger = get_kernel_logger("kernel")
console = Console()

class ProcOSConfig:
    """Configuration management for ProcOS"""
    
    def __init__(self):
        # Core settings
        self.env = os.getenv('PROCOS_ENV', 'development')
        self.instance_id = os.getenv('PROCOS_INSTANCE_ID', 'procos-dev-001')
        self.version = os.getenv('PROCOS_VERSION', '1.0.0')
        
        # Camunda settings
        self.camunda_base_url = os.getenv('CAMUNDA_BASE_URL', 'http://localhost:8080')
        self.camunda_engine = os.getenv('CAMUNDA_ENGINE_NAME', 'default')
        self.camunda_api = f"{self.camunda_base_url}/engine-rest"
        
        # Process settings
        self.process_path = Path(os.getenv('PROCESS_DEPLOYMENT_PATH', './src/processes'))
        self.auto_deploy = os.getenv('AUTO_DEPLOY_PROCESSES', 'true').lower() == 'true'
        
        # Health monitoring
        self.health_check_interval = int(os.getenv('HEALTH_CHECK_INTERVAL', '30'))
        self.health_check_enabled = os.getenv('HEALTH_CHECK_ENABLED', 'true').lower() == 'true'
        
        # Worker settings
        self.worker_max_tasks = int(os.getenv('WORKER_MAX_TASKS', '10'))
        self.worker_lock_duration = int(os.getenv('WORKER_LOCK_DURATION', '300000'))

class ProcOSKernel:
    """
    The ProcOS Microkernel
    
    Minimal bootstrap system that starts Camunda and then becomes passive,
    letting BPMN processes drive all system operations.
    """
    
    def __init__(self):
        self.config = ProcOSConfig()
        self.running = True
        self.startup_time = None
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        logger.info(f"ProcOS Kernel v{self.config.version} initializing...")

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        logger.info(f"Received signal {signum}, initiating graceful shutdown...")
        self.running = False

    def bootstrap(self) -> None:
        """
        Main bootstrap sequence - the ONLY imperative code in ProcOS
        Everything else is defined by BPMN processes
        
        This method implements the 6-phase bootstrap sequence:
        1. Environment validation
        2. Start Camunda engine  
        3. Wait for Camunda to be ready
        4. Deploy root orchestration processes
        5. Start root orchestrator
        6. Enter monitoring mode
        """
        try:
            logger.info("🚀 ProcOS Kernel Bootstrap Starting")
            
            # Phase 1: Environment validation
            self._validate_environment()
            
            # Phase 2: Wait for Camunda to be ready
            self._wait_for_camunda()
            
            # Phase 3: Deploy root processes
            if self.config.auto_deploy:
                self._deploy_processes()
            
            # Phase 4: Start root orchestrator process
            self._start_root_orchestrator()
            
            # Phase 5: Enter monitoring mode
            self.startup_time = time.time()
            logger.info("✅ ProcOS Kernel Bootstrap Complete")
            
            # Phase 6: Monitor and sleep (everything else is process-driven)
            self._enter_monitoring_mode()
            
        except Exception as e:
            logger.error(f"❌ Bootstrap failed: {e}")
            sys.exit(1)

    def _validate_environment(self) -> None:
        """Phase 1: Validate system environment and dependencies"""
        logger.info("🔍 Phase 1: Environment Validation")
        
        # Check Python version
        if sys.version_info < (3, 8):
            raise RuntimeError("Python 3.8+ required")
        
        # Check process directory
        if not self.config.process_path.exists():
            logger.warning(f"Process directory not found: {self.config.process_path}")
            self.config.process_path.mkdir(parents=True, exist_ok=True)
        
        # Validate configuration
        required_vars = ['CAMUNDA_BASE_URL']
        missing = [var for var in required_vars if not os.getenv(var)]
        if missing:
            raise RuntimeError(f"Missing required environment variables: {missing}")
        
        logger.info("✅ Environment validation complete")

    def _wait_for_camunda(self) -> None:
        """Phase 2: Wait for Camunda engine to be ready"""
        logger.info("⏳ Phase 2: Waiting for Camunda Engine")
        
        max_attempts = 30
        attempt = 0
        
        while attempt < max_attempts and self.running:
            try:
                response = requests.get(
                    f"{self.config.camunda_api}/engine",
                    timeout=5
                )
                
                if response.status_code == 200:
                    engines = response.json()
                    if engines:
                        engine_name = engines[0].get('name', 'default')
                        logger.info(f"✅ Camunda engine '{engine_name}' ready")
                        return
                
            except requests.exceptions.RequestException:
                pass
            
            attempt += 1
            time.sleep(2)
            logger.info(f"Waiting for Camunda... ({attempt}/{max_attempts})")
        
        if not self.running:
            return
            
        raise RuntimeError("Camunda engine failed to start within timeout")

    def _deploy_processes(self) -> None:
        """Phase 3: Deploy BPMN process definitions"""
        logger.info("📋 Phase 3: Deploying BPMN Processes")
        
        bpmn_files = list(self.config.process_path.glob("*.bpmn"))
        
        if not bpmn_files:
            logger.warning("No BPMN files found for deployment")
            return
        
        for bpmn_file in bpmn_files:
            try:
                with open(bpmn_file, 'rb') as f:
                    files = {
                        'deployment-name': (None, f"procos-{bpmn_file.stem}"),
                        'deployment-source': (None, 'ProcOS Microkernel'),
                        'tenant-id': (None, 'procos'),
                        'enable-duplicate-filtering': (None, 'true'),
                        'deploy-changed-only': (None, 'true'),
                        bpmn_file.name: f
                    }
                    
                    response = requests.post(
                        f"{self.config.camunda_api}/deployment/create",
                        files=files,
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        deployment = response.json()
                        logger.info(f"✅ Deployed: {bpmn_file.name} (ID: {deployment.get('id')})")
                    else:
                        logger.error(f"❌ Failed to deploy {bpmn_file.name}: {response.text}")
                        
            except Exception as e:
                logger.error(f"❌ Error deploying {bpmn_file.name}: {e}")
        
        logger.info("📋 Process deployment complete")

    def _start_root_orchestrator(self) -> None:
        """Phase 4: Start the root system orchestrator process"""
        logger.info("🎯 Phase 4: Starting Root Orchestrator")
        
        # Try to start the system orchestrator process
        try:
            response = requests.post(
                f"{self.config.camunda_api}/process-definition/key/system_orchestrator/start",
                json={
                    "variables": {
                        "kernel_instance_id": {"value": self.config.instance_id},
                        "startup_time": {"value": int(time.time())},
                        "environment": {"value": self.config.env}
                    }
                },
                timeout=10
            )
            
            if response.status_code == 200:
                instance = response.json()
                logger.info(f"✅ Root orchestrator started (Instance: {instance.get('id')})")
            else:
                logger.warning(f"Root orchestrator not started: {response.status_code}")
                logger.info("This is normal if system_orchestrator.bpmn is not deployed yet")
                
        except requests.exceptions.RequestException as e:
            logger.warning(f"Could not start root orchestrator: {e}")
            logger.info("System will continue - orchestrator can be started manually")

    def _enter_monitoring_mode(self) -> None:
        """Phase 5: Enter passive monitoring mode"""
        logger.info("👁️  Phase 5: Entering Monitoring Mode")
        
        # Display startup summary
        self._display_startup_summary()
        
        # Main monitoring loop
        last_health_check = 0
        
        while self.running:
            try:
                current_time = time.time()
                
                # Periodic health check
                if (self.config.health_check_enabled and 
                    current_time - last_health_check > self.config.health_check_interval):
                    
                    self._perform_health_check()
                    last_health_check = current_time
                
                # Sleep for 1 second
                time.sleep(1)
                
            except KeyboardInterrupt:
                logger.info("Received interrupt signal")
                break
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(5)
        
        logger.info("🛑 ProcOS Kernel shutting down gracefully")

    def _display_startup_summary(self) -> None:
        """Display a nice startup summary"""
        uptime = time.time() - self.startup_time if self.startup_time else 0
        
        summary = f"""
🎯 [bold green]ProcOS Kernel Active[/bold green]

📊 System Information:
  • Instance ID: {self.config.instance_id}
  • Version: {self.config.version}
  • Environment: {self.config.env}
  • Startup Time: {uptime:.2f}s

🔗 Service URLs:
  • Camunda Engine: {self.config.camunda_base_url}
  • Camunda Cockpit: {self.config.camunda_base_url}/camunda
  • REST API: {self.config.camunda_api}

🚀 Status: Ready for process execution!
        """
        
        console.print(Panel(summary, title="ProcOS Microkernel", border_style="green"))

    def _perform_health_check(self) -> None:
        """Perform lightweight health check"""
        try:
            response = requests.get(f"{self.config.camunda_api}/engine", timeout=5)
            if response.status_code == 200:
                logger.debug("🔍 Health check: All systems operational")
            else:
                logger.warning(f"🚨 Health check: Camunda returned {response.status_code}")
        except Exception as e:
            logger.error(f"🚨 Health check failed: {e}")

def main():
    """Main entry point for the ProcOS Kernel"""
    try:
        # Create and start the kernel
        kernel = ProcOSKernel()
        kernel.bootstrap()
        
    except KeyboardInterrupt:
        logger.info("Kernel stopped by user")
    except Exception as e:
        logger.error(f"Kernel failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()