#!/usr/bin/env python3
"""
ProcOS Process Deployment Script

Deploys BPMN process definitions to Camunda engine.
This script is called during system startup but can also be run manually.

Usage:
    python scripts/deploy_processes.py [--process-dir PATH] [--camunda-url URL]

Author: ProcOS Development Team
License: MIT
"""

import argparse
import logging
import os
import sys
from pathlib import Path
from typing import List, Optional

import requests
from dotenv import load_dotenv
from rich.console import Console
from rich.logging import RichHandler

# Load environment
load_dotenv()

# Setup logging using centralized configuration
sys.path.append(str(Path(__file__).parent.parent / "src"))
from utils.logging_config import get_service_logger

logger = get_service_logger("deploy_processes")


class ProcessDeployer:
    """Handles BPMN process deployment to Camunda"""
    
    def __init__(self, camunda_url: str, process_dir: Path):
        self.camunda_url = camunda_url.rstrip('/')
        self.camunda_api = f"{self.camunda_url}/engine-rest"
        self.process_dir = Path(process_dir)
        
        if not self.process_dir.exists():
            raise ValueError(f"Process directory does not exist: {self.process_dir}")
    
    def check_camunda_health(self) -> bool:
        """Check if Camunda engine is available"""
        try:
            response = requests.get(f"{self.camunda_api}/engine", timeout=5)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False
    
    def find_bpmn_files(self) -> List[Path]:
        """Find all BPMN files in the process directory"""
        bpmn_files = list(self.process_dir.glob("*.bpmn"))
        if not bpmn_files:
            logger.warning(f"No BPMN files found in {self.process_dir}")
        return bpmn_files
    
    def deploy_process(self, bpmn_file: Path) -> Optional[dict]:
        """Deploy a single BPMN process file"""
        try:
            logger.info(f"📋 Deploying: {bpmn_file.name}")
            
            with open(bpmn_file, 'rb') as f:
                files = {
                    'deployment-name': (None, f"procos-{bpmn_file.stem}"),
                    'deployment-source': (None, 'ProcOS Process Deployer'),
                    'tenant-id': (None, 'procos'),
                    'enable-duplicate-filtering': (None, 'true'),
                    'deploy-changed-only': (None, 'true'),
                    bpmn_file.name: f
                }
                
                response = requests.post(
                    f"{self.camunda_api}/deployment/create",
                    files=files,
                    timeout=30
                )
                
                if response.status_code == 200:
                    deployment = response.json()
                    logger.info(f"✅ Successfully deployed: {bpmn_file.name} (ID: {deployment.get('id')})")
                    return deployment
                else:
                    logger.error(f"❌ Failed to deploy {bpmn_file.name}: {response.status_code}")
                    logger.error(f"Response: {response.text}")
                    return None
                    
        except Exception as e:
            logger.error(f"❌ Error deploying {bpmn_file.name}: {e}")
            return None
    
    def deploy_all_processes(self) -> dict:
        """Deploy all BPMN processes found in the directory"""
        logger.info(f"🚀 Starting process deployment from: {self.process_dir}")
        
        # Check Camunda health first
        if not self.check_camunda_health():
            raise RuntimeError("Camunda engine is not available")
        
        logger.info("✅ Camunda engine is healthy")
        
        bpmn_files = self.find_bpmn_files()
        if not bpmn_files:
            return {"deployed": 0, "failed": 0, "skipped": 1}
        
        results = {
            "deployed": 0,
            "failed": 0,
            "skipped": 0,
            "deployments": []
        }
        
        for bpmn_file in bpmn_files:
            deployment = self.deploy_process(bpmn_file)
            if deployment:
                results["deployed"] += 1
                results["deployments"].append({
                    "file": bpmn_file.name,
                    "deployment_id": deployment.get('id'),
                    "status": "success"
                })
            else:
                results["failed"] += 1
                results["deployments"].append({
                    "file": bpmn_file.name,
                    "deployment_id": None,
                    "status": "failed"
                })
        
        logger.info(f"📋 Deployment Summary: {results['deployed']} deployed, {results['failed']} failed")
        return results
    
    def list_deployed_processes(self) -> List[dict]:
        """List all deployed process definitions"""
        try:
            response = requests.get(f"{self.camunda_api}/process-definition", timeout=10)
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to list processes: {response.status_code}")
                return []
        except Exception as e:
            logger.error(f"Error listing processes: {e}")
            return []


def main():
    """Main entry point for the deployment script"""
    parser = argparse.ArgumentParser(description="Deploy BPMN processes to Camunda")
    parser.add_argument(
        "--process-dir",
        default=os.getenv('PROCESS_DEPLOYMENT_PATH', './src/processes'),
        help="Directory containing BPMN files"
    )
    parser.add_argument(
        "--camunda-url",
        default=os.getenv('CAMUNDA_BASE_URL', 'http://localhost:8080'),
        help="Camunda engine base URL"
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List currently deployed processes"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be deployed without actually deploying"
    )
    
    args = parser.parse_args()
    
    try:
        deployer = ProcessDeployer(args.camunda_url, args.process_dir)
        
        if args.list:
            logger.info("📋 Listing deployed processes...")
            processes = deployer.list_deployed_processes()
            if processes:
                console.print("\n[bold green]Deployed Processes:[/bold green]")
                for process in processes:
                    console.print(f"  • {process.get('key', 'Unknown')} v{process.get('version', '?')} "
                                f"(ID: {process.get('id', 'Unknown')})")
            else:
                console.print("[yellow]No processes found[/yellow]")
            return
        
        if args.dry_run:
            logger.info("🔍 Dry run mode - showing what would be deployed...")
            bpmn_files = deployer.find_bpmn_files()
            for bpmn_file in bpmn_files:
                console.print(f"  📋 Would deploy: {bpmn_file.name}")
            return
        
        # Deploy all processes
        results = deployer.deploy_all_processes()
        
        if results["failed"] > 0:
            logger.error(f"❌ Some deployments failed ({results['failed']} failures)")
            sys.exit(1)
        elif results["deployed"] > 0:
            logger.info(f"🎉 All processes deployed successfully! ({results['deployed']} deployed)")
        else:
            logger.info("ℹ️  No new processes to deploy")
            
    except Exception as e:
        logger.error(f"❌ Deployment failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()