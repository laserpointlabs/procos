#!/usr/bin/env python3
"""
ProcOS Generic Worker

Handles basic external tasks like HTTP requests, email sending, file operations, etc.
This is the Swiss Army knife worker for common operations.

Author: ProcOS Development Team
License: MIT
"""

import json
import logging
import os
import smtplib
import sys
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from typing import Any, Dict, Optional

import requests
from camunda.external_task.external_task import ExternalTask, TaskResult
from camunda.external_task.external_task_worker import ExternalTaskWorker
from dotenv import load_dotenv
from rich.console import Console
from rich.logging import RichHandler  # noqa: F401 (imported for side-effects in logging)

# Load environment
load_dotenv()

# Setup logging using centralized configuration
sys.path.append(str(Path(__file__).parent.parent))
from utils.logging_config import get_worker_logger

logger = get_worker_logger("generic_worker")

class GenericWorker:
    """
    Generic worker for common external tasks
    
    Handles:
    - HTTP requests (GET, POST, PUT, DELETE)
    - Email sending
    - File operations (read, write, delete)
    - Data validation
    - Simple transformations
    """
    
    def __init__(self):
        self.camunda_url = os.getenv('CAMUNDA_BASE_URL', 'http://localhost:8080')
        self.worker_id = os.getenv('WORKER_ID', 'generic_worker_001')
        
        # Setup external task worker
        self.worker = ExternalTaskWorker(
            worker_id=self.worker_id,
            base_url=f"{self.camunda_url}/engine-rest",
            config={
                "maxTasks": int(os.getenv('WORKER_MAX_TASKS', '10')),
                "lockDuration": int(os.getenv('WORKER_LOCK_DURATION', '300000')),
                "asyncResponseTimeout": int(os.getenv('WORKER_RETRY_TIMEOUT', '30000')),
                "retries": 3,
                "retryTimeout": 5000,
            }
        )
        
        logger.info(f"🔧 Generic Worker {self.worker_id} initialized")

    def start(self):
        """Start the worker and subscribe to external tasks"""
        logger.info("🚀 Starting Generic Worker...")
        
        # Subscribe to different task types
        self.worker.subscribe("http_request", self.handle_http_request)
        self.worker.subscribe("email_send", self.handle_email_send)
        self.worker.subscribe("file_operation", self.handle_file_operation)
        self.worker.subscribe("data_validation", self.handle_data_validation)
        self.worker.subscribe("data_transform", self.handle_data_transform)
        
        logger.info("✅ Generic Worker subscriptions active")
        logger.info("📋 Subscribed to: http_request, email_send, file_operation, data_validation, data_transform")

    def handle_http_request(self, task: ExternalTask) -> TaskResult:
        """Handle HTTP request external tasks"""
        try:
            logger.info(f"🌐 Processing HTTP request task: {task.get_task_id()}")
            
            # Get task variables
            method = task.get_variable("method") or "GET"
            url = task.get_variable("url")
            headers = task.get_variable("headers") or {}
            data = task.get_variable("data")
            params = task.get_variable("params")
            timeout = task.get_variable("timeout") or 30
            
            if not url:
                return task.failure("URL is required for HTTP request")
            
            # Make the request
            response = requests.request(
                method=method.upper(),
                url=url,
                headers=headers,
                json=data if data else None,
                params=params,
                timeout=timeout
            )
            
            # Prepare response data
            result_data = {
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "text": response.text,
                "success": 200 <= response.status_code < 300
            }
            
            # Try to parse JSON if possible
            try:
                result_data["json"] = response.json()
            except ValueError:
                result_data["json"] = None
            
            logger.info(f"✅ HTTP {method} {url} completed: {response.status_code}")
            return task.complete(result_data)
            
        except Exception as e:
            logger.error(f"❌ HTTP request failed: {e}")
            return task.failure(f"HTTP request error: {str(e)}")

    def handle_email_send(self, task: ExternalTask) -> TaskResult:
        """Handle email sending external tasks"""
        try:
            logger.info(f"📧 Processing email task: {task.get_task_id()}")
            
            # Get email configuration
            smtp_server = task.get_variable("smtp_server") or os.getenv('SMTP_SERVER')
            smtp_port = task.get_variable("smtp_port") or int(os.getenv('SMTP_PORT', '587'))
            smtp_username = task.get_variable("smtp_username") or os.getenv('SMTP_USERNAME')
            smtp_password = task.get_variable("smtp_password") or os.getenv('SMTP_PASSWORD')
            
            # Get email details
            from_email = task.get_variable("from_email") or smtp_username
            to_email = task.get_variable("to_email")
            subject = task.get_variable("subject")
            body = task.get_variable("body")
            body_type = task.get_variable("body_type") or "plain"  # "plain" or "html"
            
            if not all([smtp_server, to_email, subject, body]):
                return task.failure("Missing required email parameters")
            
            # Create message
            msg = MIMEMultipart()
            msg['From'] = from_email
            msg['To'] = to_email
            msg['Subject'] = subject
            
            msg.attach(MIMEText(body, body_type))
            
            # Send email
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                if smtp_username and smtp_password:
                    server.login(smtp_username, smtp_password)
                server.send_message(msg)
            
            logger.info(f"✅ Email sent to {to_email}")
            return task.complete({"sent": True, "to": to_email})
            
        except Exception as e:
            logger.error(f"❌ Email sending failed: {e}")
            return task.failure(f"Email error: {str(e)}")

    def handle_file_operation(self, task: ExternalTask) -> TaskResult:
        """Handle file operation external tasks"""
        try:
            logger.info(f"📁 Processing file operation: {task.get_task_id()}")
            
            operation = task.get_variable("operation")  # "read", "write", "delete", "exists"
            file_path = task.get_variable("file_path")
            content = task.get_variable("content")  # For write operations
            encoding = task.get_variable("encoding") or "utf-8"
            
            if not file_path:
                return task.failure("file_path is required")
            
            path = Path(file_path)
            result = {}
            
            if operation == "read":
                if not path.exists():
                    return task.failure(f"File not found: {file_path}")
                
                content = path.read_text(encoding=encoding)
                result = {"content": content, "size": len(content)}
                
            elif operation == "write":
                if content is None:
                    return task.failure("content is required for write operation")
                
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(content, encoding=encoding)
                result = {"written": True, "size": len(content)}
                
            elif operation == "delete":
                if path.exists():
                    path.unlink()
                    result = {"deleted": True}
                else:
                    result = {"deleted": False, "reason": "file_not_found"}
                    
            elif operation == "exists":
                result = {"exists": path.exists(), "is_file": path.is_file(), "is_dir": path.is_dir()}
                
            else:
                return task.failure(f"Unknown file operation: {operation}")
            
            logger.info(f"✅ File operation '{operation}' completed: {file_path}")
            return task.complete(result)
            
        except Exception as e:
            logger.error(f"❌ File operation failed: {e}")
            return task.failure(f"File operation error: {str(e)}")

    def handle_data_validation(self, task: ExternalTask) -> TaskResult:
        """Handle data validation external tasks"""
        try:
            logger.info(f"🔍 Processing data validation: {task.get_task_id()}")
            
            data = task.get_variable("data")
            rules = task.get_variable("validation_rules")  # List of validation rules
            
            if not data or not rules:
                return task.failure("data and validation_rules are required")
            
            errors = []
            warnings = []
            
            for rule in rules:
                rule_type = rule.get("type")
                field = rule.get("field")
                value = data.get(field) if isinstance(data, dict) else None
                
                if rule_type == "required" and not value:
                    errors.append(f"Field '{field}' is required")
                elif rule_type == "type":
                    expected_type = rule.get("expected_type")
                    if value is not None and not isinstance(value, eval(expected_type)):
                        errors.append(f"Field '{field}' must be of type {expected_type}")
                elif rule_type == "min_length":
                    min_len = rule.get("min_length", 0)
                    if value and len(str(value)) < min_len:
                        errors.append(f"Field '{field}' must be at least {min_len} characters")
                elif rule_type == "max_length":
                    max_len = rule.get("max_length", 1000)
                    if value and len(str(value)) > max_len:
                        warnings.append(f"Field '{field}' exceeds recommended length of {max_len}")
            
            result = {
                "valid": len(errors) == 0,
                "errors": errors,
                "warnings": warnings,
                "validated_fields": len(rules)
            }
            
            logger.info(f"✅ Data validation completed: {len(errors)} errors, {len(warnings)} warnings")
            return task.complete(result)
            
        except Exception as e:
            logger.error(f"❌ Data validation failed: {e}")
            return task.failure(f"Validation error: {str(e)}")

    def handle_data_transform(self, task: ExternalTask) -> TaskResult:
        """Handle data transformation external tasks"""
        try:
            logger.info(f"🔄 Processing data transformation: {task.get_task_id()}")
            
            data = task.get_variable("data")
            transformation_type = task.get_variable("transformation_type")
            transformation_config = task.get_variable("transformation_config") or {}
            
            if not data:
                return task.failure("data is required for transformation")
            
            result = None
            
            if transformation_type == "uppercase":
                result = str(data).upper()
            elif transformation_type == "lowercase":
                result = str(data).lower()
            elif transformation_type == "json_parse":
                result = json.loads(data) if isinstance(data, str) else data
            elif transformation_type == "json_stringify":
                result = json.dumps(data)
            elif transformation_type == "extract_field":
                field = transformation_config.get("field")
                result = data.get(field) if isinstance(data, dict) and field else None
            elif transformation_type == "add_timestamp":
                import time
                if isinstance(data, dict):
                    data["timestamp"] = int(time.time())
                    result = data
                else:
                    result = {"data": data, "timestamp": int(time.time())}
            else:
                return task.failure(f"Unknown transformation type: {transformation_type}")
            
            logger.info(f"✅ Data transformation '{transformation_type}' completed")
            return task.complete({"transformed_data": result, "original_data": data})
            
        except Exception as e:
            logger.error(f"❌ Data transformation failed: {e}")
            return task.failure(f"Transformation error: {str(e)}")

def main():
    """Main entry point for the generic worker"""
    try:
        worker = GenericWorker()
        worker.start()
        
        logger.info("🔧 Generic Worker running... Press Ctrl+C to stop")
        
        # Keep the worker running
        import time
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("Generic Worker stopped by user")
    except Exception as e:
        logger.error(f"Generic Worker failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()