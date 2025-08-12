#!/usr/bin/env python3
"""
ProcOS Health Check Script
Comprehensive system health monitoring and diagnostics
"""

import asyncio
import json
import logging
import sys
import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple

import requests
import redis
import pika
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

# Setup
console = Console()
logging.basicConfig(level=logging.WARNING)  # Suppress noisy logs

class HealthChecker:
    """ProcOS system health checker"""
    
    def __init__(self):
        self.console = console
        self.results = {}
        
    def check_camunda(self) -> Tuple[bool, str, Dict]:
        """Check Camunda engine health"""
        try:
            camunda_base = os.getenv('CAMUNDA_BASE_URL', 'http://localhost:8080')
            api = f"{camunda_base}/engine-rest"
            # Check engine status
            response = requests.get(
                f'{api}/engine',
                timeout=10
            )
            
            if response.status_code == 200:
                engines = response.json()
                if engines:
                    engine_name = engines[0].get('name', 'default')
                    
                    # Check version info
                    version_response = requests.get(f'{api}/version', timeout=5)
                    
                    version_info = {}
                    if version_response.status_code == 200:
                        version_info = version_response.json()
                    
                    # Check process definitions
                    processes_response = requests.get(f'{api}/process-definition', timeout=5)
                    
                    process_count = 0
                    if processes_response.status_code == 200:
                        process_count = len(processes_response.json())
                    
                    details = {
                        'engine_name': engine_name,
                        'version': version_info.get('version', 'unknown'),
                        'process_definitions': process_count,
                        'url': f'{camunda_base}/camunda'
                    }
                    
                    return True, f"Engine '{engine_name}' running", details
                else:
                    return False, "No engines found", {}
            else:
                return False, f"HTTP {response.status_code}", {}
                
        except requests.exceptions.ConnectionError:
            return False, "Connection refused", {}
        except requests.exceptions.Timeout:
            return False, "Request timeout", {}
        except Exception as e:
            return False, f"Error: {str(e)}", {}

    def check_rabbitmq(self) -> Tuple[bool, str, Dict]:
        """Check RabbitMQ health"""
        try:
            # Check management API
            response = requests.get(
                'http://localhost:15672/api/overview',
                auth=('procos', 'procos123'),
                timeout=10
            )
            
            if response.status_code == 200:
                overview = response.json()
                
                # Check AMQP connection
                connection = pika.BlockingConnection(
                    pika.ConnectionParameters(
                        host='localhost',
                        port=5672,
                        virtual_host='/',
                        credentials=pika.PlainCredentials('procos', 'procos123')
                    )
                )
                connection.close()
                
                details = {
                    'version': overview.get('rabbitmq_version', 'unknown'),
                    'erlang_version': overview.get('erlang_version', 'unknown'),
                    'management_url': 'http://localhost:15672',
                    'amqp_port': 5672
                }
                
                return True, "RabbitMQ healthy", details
            else:
                return False, f"Management API HTTP {response.status_code}", {}
                
        except requests.exceptions.ConnectionError:
            return False, "Management API connection refused", {}
        except pika.exceptions.AMQPConnectionError:
            return False, "AMQP connection failed", {}
        except Exception as e:
            return False, f"Error: {str(e)}", {}

    def check_redis(self) -> Tuple[bool, str, Dict]:
        """Check Redis health"""
        try:
            r = redis.Redis(host='localhost', port=6379, db=0, socket_timeout=5)
            
            # Test ping
            ping_result = r.ping()
            
            if ping_result:
                # Get Redis info
                info = r.info()
                
                details = {
                    'version': info.get('redis_version', 'unknown'),
                    'mode': info.get('redis_mode', 'unknown'),
                    'connected_clients': info.get('connected_clients', 0),
                    'used_memory_human': info.get('used_memory_human', 'unknown'),
                    'port': 6379
                }
                
                return True, "Redis responsive", details
            else:
                return False, "Ping failed", {}
                
        except redis.exceptions.ConnectionError:
            return False, "Connection refused", {}
        except redis.exceptions.TimeoutError:
            return False, "Connection timeout", {}
        except Exception as e:
            return False, f"Error: {str(e)}", {}

    def check_processes(self) -> Tuple[bool, str, Dict]:
        """Check running ProcOS processes"""
        import psutil
        import os
        
        try:
            processes = []
            
            # Check for microkernel
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    cmdline = ' '.join(proc.info['cmdline'] or [])
                    if 'procos_kernel' in cmdline:
                        processes.append({
                            'name': 'ProcOS Microkernel',
                            'pid': proc.info['pid'],
                            'status': 'running'
                        })
                    elif 'generic_worker' in cmdline:
                        processes.append({
                            'name': 'Generic Worker',
                            'pid': proc.info['pid'],
                            'status': 'running'
                        })
                    elif 'ai_worker' in cmdline:
                        processes.append({
                            'name': 'AI Worker',
                            'pid': proc.info['pid'],
                            'status': 'running'
                        })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # Check PID files
            pid_files = []
            for filename in os.listdir('.'):
                if filename.endswith('.pid'):
                    pid_files.append(filename)
            
            details = {
                'running_processes': len(processes),
                'processes': processes,
                'pid_files': pid_files
            }
            
            if processes:
                return True, f"Found {len(processes)} ProcOS processes", details
            else:
                return False, "No ProcOS processes found", details
                
        except Exception as e:
            return False, f"Error checking processes: {str(e)}", {}

    def run_health_check(self) -> Dict:
        """Run comprehensive health check"""
        checks = [
            ('Camunda Engine', self.check_camunda),
            ('RabbitMQ', self.check_rabbitmq),
            ('Redis', self.check_redis),
            ('ProcOS Processes', self.check_processes),
        ]
        
        results = {}
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console,
            transient=True
        ) as progress:
            
            for check_name, check_func in checks:
                task = progress.add_task(f"Checking {check_name}...", total=None)
                
                healthy, message, details = check_func()
                
                results[check_name] = {
                    'healthy': healthy,
                    'message': message,
                    'details': details,
                    'timestamp': datetime.now().isoformat()
                }
                
                progress.remove_task(task)
        
        return results

    def display_results(self, results: Dict):
        """Display health check results in a nice format"""
        
        # Create summary table
        table = Table(title="🏥 ProcOS Health Check Results")
        table.add_column("Component", style="cyan", no_wrap=True)
        table.add_column("Status", style="green")
        table.add_column("Message", style="white")
        table.add_column("Details", style="dim")
        
        overall_healthy = True
        
        for component, result in results.items():
            status = "✅ Healthy" if result['healthy'] else "❌ Unhealthy"
            details_str = ""
            
            if result['details']:
                key_details = []
                details = result['details']
                
                if 'version' in details:
                    key_details.append(f"v{details['version']}")
                if 'process_definitions' in details:
                    key_details.append(f"{details['process_definitions']} processes")
                if 'running_processes' in details:
                    key_details.append(f"{details['running_processes']} running")
                if 'url' in details:
                    key_details.append(details['url'])
                
                details_str = " | ".join(key_details)
            
            table.add_row(component, status, result['message'], details_str)
            
            if not result['healthy']:
                overall_healthy = False
        
        self.console.print(table)
        
        # Overall status panel
        if overall_healthy:
            status_panel = Panel(
                "🎉 All systems operational!\nProcOS is ready for process execution.",
                title="System Status",
                style="green"
            )
        else:
            status_panel = Panel(
                "⚠️  Some components are unhealthy.\nCheck the details above for troubleshooting.",
                title="System Status",
                style="red"
            )
        
        self.console.print("\n")
        self.console.print(status_panel)
        
        return overall_healthy

def main():
    """Main health check entry point"""
    console.print("\n[bold blue]🔍 ProcOS Health Check[/bold blue]\n")
    
    checker = HealthChecker()
    results = checker.run_health_check()
    healthy = checker.display_results(results)
    
    # Output JSON if requested
    if '--json' in sys.argv:
        print(json.dumps(results, indent=2))
    
    # Exit with appropriate code
    sys.exit(0 if healthy else 1)

if __name__ == "__main__":
    main()