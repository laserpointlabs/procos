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
import json
import random
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
from utils.metrics import KernelMetrics

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
        self.readiness_file = Path(os.getenv('KERNEL_READINESS_FILE', '/tmp/procos.ready'))
        self.max_health_failures = int(os.getenv('HEALTH_MAX_CONSECUTIVE_FAILURES', '5'))
        self.health_backoff_base_seconds = float(os.getenv('HEALTH_BACKOFF_BASE_SECONDS', '1.5'))

        # Camunda readiness polling
        self.camunda_ready_max_attempts = int(os.getenv('CAMUNDA_READY_MAX_ATTEMPTS', '30'))
        self.camunda_ready_base_sleep_seconds = float(os.getenv('CAMUNDA_READY_BASE_SLEEP_SECONDS', '2.0'))
        self.camunda_ready_jitter_seconds = float(os.getenv('CAMUNDA_READY_JITTER_SECONDS', '0.75'))

        # Metrics
        self.metrics_snapshot_file = Path(os.getenv('KERNEL_METRICS_SNAPSHOT_FILE', 'logs/kernel/metrics.json'))
        
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
        self.metrics = KernelMetrics()
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        logger.info(json.dumps({
            "event": "kernel_starting",
            "component": "kernel",
            "version": self.config.version,
            "env": self.config.env,
        }))

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        logger.info(json.dumps({
            "event": "kernel_signal",
            "component": "kernel",
            "signal": int(signum),
            "message": "initiating graceful shutdown",
        }))
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
            logger.info(json.dumps({
                "event": "kernel_bootstrap_start",
                "component": "kernel",
            }))
            
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
            logger.info(json.dumps({
                "event": "kernel_bootstrap_complete",
                "component": "kernel",
                "phase": "monitoring",
            }))
            
            # Phase 6: Monitor and sleep (everything else is process-driven)
            self._enter_monitoring_mode()
            
        except Exception as e:
            logger.error(json.dumps({
                "event": "kernel_bootstrap_failed",
                "component": "kernel",
                "error": str(e),
            }))
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
        
        # Validate configuration (aggregate errors)
        errors = []
        # Required envs
        if not os.getenv('CAMUNDA_BASE_URL'):
            errors.append("Missing CAMUNDA_BASE_URL")
        # Numeric validations
        if self.config.health_check_interval <= 0:
            errors.append("HEALTH_CHECK_INTERVAL must be > 0")
        if self.config.health_backoff_base_seconds <= 1.0:
            errors.append("HEALTH_BACKOFF_BASE_SECONDS should be > 1.0")
        if self.config.camunda_ready_max_attempts <= 0:
            errors.append("CAMUNDA_READY_MAX_ATTEMPTS must be > 0")
        if self.config.camunda_ready_base_sleep_seconds <= 0:
            errors.append("CAMUNDA_READY_BASE_SLEEP_SECONDS must be > 0")

        if errors:
            raise RuntimeError("Config validation errors: " + "; ".join(errors))
        
        logger.info("✅ Environment validation complete")

    def _wait_for_camunda(self) -> None:
        """Phase 2: Wait for Camunda engine to be ready"""
        logger.info("⏳ Phase 2: Waiting for Camunda Engine")
        
        max_attempts = self.config.camunda_ready_max_attempts
        attempt = 0
        
        while attempt < max_attempts and self.running:
            try:
                self.metrics.increment("camunda_wait_attempts")
                response = requests.get(
                    f"{self.config.camunda_api}/engine",
                    timeout=5
                )
                
                if response.status_code == 200:
                    engines = response.json()
                    if engines:
                        engine_name = engines[0].get('name', 'default')
                        logger.info(f"✅ Camunda engine '{engine_name}' ready")
                        # Write readiness marker
                        try:
                            self.config.readiness_file.write_text(str(int(time.time())))
                        except Exception as e:
                            logger.warning(f"Could not write readiness file: {e}")
                        return
                
            except requests.exceptions.RequestException:
                pass
            
            attempt += 1
            # Sleep with jitter to avoid thundering herd
            sleep_for = self.config.camunda_ready_base_sleep_seconds + random.uniform(0, self.config.camunda_ready_jitter_seconds)
            time.sleep(sleep_for)
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
        consecutive_failures = 0
        
        while self.running:
            try:
                current_time = time.time()
                
                # Periodic health check
                if (self.config.health_check_enabled and 
                    current_time - last_health_check > self.config.health_check_interval):
                    
                    ok = self._perform_health_check()
                    if ok:
                        consecutive_failures = 0
                        last_health_check = current_time
                    else:
                        consecutive_failures += 1
                        # Exponential backoff on failures to avoid hammering Camunda
                        backoff = min(60.0, (self.config.health_backoff_base_seconds ** consecutive_failures))
                        logger.warning(f"Health check failed (#{consecutive_failures}). Backing off {backoff:.1f}s")
                        time.sleep(backoff)
                        last_health_check = current_time

                    # Update readiness marker if healthy
                    if consecutive_failures == 0:
                        try:
                            if not self.config.readiness_file.exists():
                                self.config.readiness_file.write_text(str(int(time.time())))
                        except Exception as e:
                            logger.debug(f"Readiness file update skipped: {e}")
                
                # Sleep for 1 second
                time.sleep(1)
                
            except KeyboardInterrupt:
                logger.info("Received interrupt signal")
                break
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(5)
        
        # Emit metrics snapshot and shutdown event
        try:
            self.metrics.write_snapshot(self.config.metrics_snapshot_file)
            self.metrics.log_snapshot(logger)
        except Exception as e:
            logger.debug(f"Metrics snapshot failed: {e}")

        logger.info(json.dumps({
            "event": "kernel_stopping",
            "component": "kernel",
        }))

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

    def _perform_health_check(self) -> bool:
        """Perform Camunda health diagnostics.

        Returns:
            bool: True if healthy, False otherwise.
        """
        try:
            # 1) Engine list (primary readiness)
            engine_resp = requests.get(f"{self.config.camunda_api}/engine", timeout=5)
            if engine_resp.status_code != 200:
                logger.warning(f"🚨 Health check: engine endpoint returned {engine_resp.status_code}")
                return False

            engines = engine_resp.json()
            if not engines:
                logger.warning("🚨 Health check: no engines reported")
                return False

            engine_name = engines[0].get('name', 'default')

            # 2) Version info
            version_resp = requests.get(f"{self.config.camunda_api}/version", timeout=5)
            if version_resp.status_code == 200:
                version = version_resp.json().get('version', 'unknown')
                logger.debug(f"Camunda version: {version}")
            else:
                logger.debug("Camunda version endpoint not available")

            # 3) Deployment count
            dep_resp = requests.get(f"{self.config.camunda_api}/deployment", timeout=5)
            if dep_resp.status_code == 200:
                deployments = dep_resp.json()
                logger.debug(f"Deployments: {len(deployments)}")
            else:
                logger.debug("Deployment list unavailable")

            # 4) Active process instances (lightweight)
            pi_resp = requests.get(f"{self.config.camunda_api}/process-instance?maxResults=1", timeout=5)
            if pi_resp.status_code in (200, 204):
                logger.debug("Process instance endpoint reachable")

            logger.debug(f"🔍 Health check OK for engine '{engine_name}'")
            self.metrics.increment("health_checks_ok")
            return True

        except Exception as e:
            logger.error(f"🚨 Health check failed: {e}")
            self.metrics.increment("health_checks_fail")
            return False

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