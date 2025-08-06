#!/usr/bin/env python3
"""
ProcOS AI Worker

Handles AI-powered external tasks using OpenAI API and local Ollama models.
Supports text generation, analysis, and various AI-powered operations.

Author: ProcOS Development Team
License: MIT
"""

import json
import logging
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, Optional, Union
import traceback

from camunda.external_task.external_task import ExternalTask, TaskResult
from camunda.external_task.external_task_worker import ExternalTaskWorker
from dotenv import load_dotenv
from rich.console import Console
from rich.logging import RichHandler

# AI Libraries
import openai
import ollama

# Load environment
load_dotenv()

# Setup logging using centralized configuration
sys.path.append(str(Path(__file__).parent.parent))
from utils.logging_config import get_worker_logger

logger = get_worker_logger("ai_worker")

class AIWorker:
    """
    AI worker for handling AI-powered external tasks
    
    Handles:
    - ai_query: General AI question answering
    - text_generation: Content creation and completion
    - analysis: Data and text analysis
    - code_generation: Code writing and review
    - translation: Text translation between languages
    """
    
    def __init__(self):
        self.camunda_url = os.getenv('CAMUNDA_BASE_URL', 'http://localhost:8080')
        self.worker_id = os.getenv('AI_WORKER_ID', 'ai_worker_001')
        
        # AI Configuration
        self.strategy = os.getenv('AI_STRATEGY', 'hybrid')  # openai, ollama, or hybrid
        self.default_provider = os.getenv('AI_DEFAULT_PROVIDER', 'ollama')
        self.fallback_enabled = os.getenv('AI_FALLBACK_ENABLED', 'true').lower() == 'true'
        
        # OpenAI Configuration
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.openai_model = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
        self.openai_max_tokens = int(os.getenv('OPENAI_MAX_TOKENS', '2048'))
        self.openai_temperature = float(os.getenv('OPENAI_TEMPERATURE', '0.7'))
        
        # Ollama Configuration
        self.ollama_base_url = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
        self.ollama_model = os.getenv('OLLAMA_MODEL', 'llama3.2:1b')
        self.ollama_timeout = int(os.getenv('OLLAMA_TIMEOUT', '120'))
        self.ollama_pull_model = os.getenv('OLLAMA_PULL_MODEL', 'true').lower() == 'true'
        
        # Initialize AI clients
        self._init_ai_clients()
        
        # Setup external task worker
        self.worker = ExternalTaskWorker(
            worker_id=self.worker_id,
            base_url=f"{self.camunda_url}/engine-rest",
            config={
                "maxTasks": int(os.getenv('AI_WORKER_MAX_TASKS', '5')),
                "lockDuration": int(os.getenv('AI_WORKER_LOCK_DURATION', '300000')),
                "asyncResponseTimeout": int(os.getenv('AI_WORKER_RETRY_TIMEOUT', '30000')),
                "retries": 3,
                "retryTimeout": 5000,
            }
        )
        
        logger.info(f"🤖 AI Worker {self.worker_id} initialized")
        logger.info(f"📋 Strategy: {self.strategy}, Default: {self.default_provider}, Fallback: {self.fallback_enabled}")

    def _init_ai_clients(self):
        """Initialize AI client connections"""
        self.openai_available = False
        self.ollama_available = False
        
        # Initialize OpenAI
        if self.openai_api_key:
            try:
                openai.api_key = self.openai_api_key
                self.openai_client = openai.OpenAI(api_key=self.openai_api_key)
                self.openai_available = True
                logger.info("✅ OpenAI client initialized")
            except Exception as e:
                logger.warning(f"⚠️ OpenAI initialization failed: {e}")
        else:
            logger.warning("⚠️ OpenAI API key not provided")
        
        # Initialize Ollama
        try:
            self.ollama_client = ollama.Client(host=self.ollama_base_url, timeout=self.ollama_timeout)
            
            # Test connection and pull model if needed
            if self._test_ollama_connection():
                self.ollama_available = True
                logger.info("✅ Ollama client initialized")
                
                # Pull model if requested
                if self.ollama_pull_model:
                    self._ensure_ollama_model()
            else:
                logger.warning("⚠️ Ollama connection test failed")
                
        except Exception as e:
            logger.warning(f"⚠️ Ollama initialization failed: {e}")
    
    def _test_ollama_connection(self) -> bool:
        """Test Ollama connection"""
        try:
            models = self.ollama_client.list()
            return True
        except Exception:
            return False
    
    def _ensure_ollama_model(self):
        """Ensure the configured Ollama model is available"""
        try:
            logger.info(f"📥 Checking/pulling Ollama model: {self.ollama_model}")
            
            # Check if model exists
            models = self.ollama_client.list()
            model_names = [model['name'] for model in models.get('models', [])]
            
            if self.ollama_model not in model_names:
                logger.info(f"📥 Pulling Ollama model: {self.ollama_model}")
                self.ollama_client.pull(self.ollama_model)
                logger.info(f"✅ Model {self.ollama_model} pulled successfully")
            else:
                logger.info(f"✅ Model {self.ollama_model} already available")
                
        except Exception as e:
            logger.error(f"❌ Failed to ensure Ollama model: {e}")

    def start(self):
        """Start the worker and subscribe to external tasks"""
        logger.info("🚀 Starting AI Worker...")
        
        # Subscribe to different AI task types
        self.worker.subscribe("ai_query", self.handle_ai_query)
        self.worker.subscribe("text_generation", self.handle_text_generation)
        self.worker.subscribe("analysis", self.handle_analysis)
        self.worker.subscribe("code_generation", self.handle_code_generation)
        self.worker.subscribe("translation", self.handle_translation)
        
        logger.info("✅ AI Worker subscriptions active")
        logger.info("📋 Subscribed to: ai_query, text_generation, analysis, code_generation, translation")

    def _choose_provider(self, task: ExternalTask, preferred_provider: Optional[str] = None) -> str:
        """Choose AI provider based on strategy and availability"""
        # Use task-specific provider if specified
        if preferred_provider and preferred_provider in ['openai', 'ollama']:
            if preferred_provider == 'openai' and self.openai_available:
                return 'openai'
            elif preferred_provider == 'ollama' and self.ollama_available:
                return 'ollama'
        
        # Use default provider from configuration
        if self.default_provider == 'openai' and self.openai_available:
            return 'openai'
        elif self.default_provider == 'ollama' and self.ollama_available:
            return 'ollama'
        
        # Fallback logic
        if self.openai_available:
            return 'openai'
        elif self.ollama_available:
            return 'ollama'
        
        raise Exception("No AI providers available")

    def _call_openai(self, prompt: str, system_prompt: str = None, **kwargs) -> Dict[str, Any]:
        """Call OpenAI API"""
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            response = self.openai_client.chat.completions.create(
                model=kwargs.get('model', self.openai_model),
                messages=messages,
                max_tokens=kwargs.get('max_tokens', self.openai_max_tokens),
                temperature=kwargs.get('temperature', self.openai_temperature)
            )
            
            return {
                "success": True,
                "provider": "openai",
                "model": response.model,
                "content": response.choices[0].message.content,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                }
            }
        except Exception as e:
            raise Exception(f"OpenAI API error: {str(e)}")

    def _call_ollama(self, prompt: str, system_prompt: str = None, **kwargs) -> Dict[str, Any]:
        """Call Ollama API"""
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            response = self.ollama_client.chat(
                model=kwargs.get('model', self.ollama_model),
                messages=messages,
                options={
                    "temperature": kwargs.get('temperature', 0.7),
                    "num_predict": kwargs.get('max_tokens', 2048)
                }
            )
            
            return {
                "success": True,
                "provider": "ollama",
                "model": response['model'],
                "content": response['message']['content'],
                "usage": {
                    "prompt_tokens": response.get('prompt_eval_count', 0),
                    "completion_tokens": response.get('eval_count', 0),
                    "total_tokens": response.get('prompt_eval_count', 0) + response.get('eval_count', 0)
                }
            }
        except Exception as e:
            raise Exception(f"Ollama API error: {str(e)}")

    def _call_ai(self, task: ExternalTask, prompt: str, system_prompt: str = None, **kwargs) -> Dict[str, Any]:
        """Call AI with fallback logic"""
        preferred_provider = task.get_variable("ai_provider")
        
        try:
            # Choose primary provider
            primary_provider = self._choose_provider(task, preferred_provider)
            logger.info(f"🤖 Using {primary_provider} for AI task")
            
            # Make the call
            if primary_provider == 'openai':
                return self._call_openai(prompt, system_prompt, **kwargs)
            else:
                return self._call_ollama(prompt, system_prompt, **kwargs)
                
        except Exception as e:
            logger.warning(f"⚠️ Primary AI provider failed: {e}")
            
            # Try fallback if enabled
            if self.fallback_enabled:
                try:
                    fallback_provider = 'ollama' if primary_provider == 'openai' else 'openai'
                    
                    if fallback_provider == 'openai' and self.openai_available:
                        logger.info("🔄 Falling back to OpenAI")
                        return self._call_openai(prompt, system_prompt, **kwargs)
                    elif fallback_provider == 'ollama' and self.ollama_available:
                        logger.info("🔄 Falling back to Ollama")
                        return self._call_ollama(prompt, system_prompt, **kwargs)
                        
                except Exception as fallback_error:
                    logger.error(f"❌ Fallback provider also failed: {fallback_error}")
            
            # If we get here, all providers failed
            raise e

    def handle_ai_query(self, task: ExternalTask) -> TaskResult:
        """Handle general AI query external tasks"""
        try:
            logger.info(f"🤖 Processing AI query task: {task.get_task_id()}")
            
            query = task.get_variable("query")
            context = task.get_variable("context")
            system_prompt = task.get_variable("system_prompt")
            
            if not query:
                return task.failure("Query is required for AI query task")
            
            # Build prompt
            prompt = query
            if context:
                prompt = f"Context: {context}\n\nQuery: {query}"
            
            # Call AI
            result = self._call_ai(task, prompt, system_prompt)
            
            logger.info(f"✅ AI query completed using {result['provider']}")
            return task.complete(result)
            
        except Exception as e:
            logger.error(f"❌ AI query failed: {e}")
            return task.failure(f"AI query error: {str(e)}")

    def handle_text_generation(self, task: ExternalTask) -> TaskResult:
        """Handle text generation external tasks"""
        try:
            logger.info(f"📝 Processing text generation task: {task.get_task_id()}")
            
            prompt = task.get_variable("prompt")
            text_type = task.get_variable("text_type")  # e.g., "email", "article", "summary"
            length = task.get_variable("length")  # e.g., "short", "medium", "long"
            tone = task.get_variable("tone")  # e.g., "professional", "casual", "formal"
            
            if not prompt:
                return task.failure("Prompt is required for text generation")
            
            # Build system prompt
            system_parts = ["You are a helpful text generation assistant."]
            
            if text_type:
                system_parts.append(f"Generate {text_type} content.")
            if length:
                system_parts.append(f"Keep the response {length}.")
            if tone:
                system_parts.append(f"Use a {tone} tone.")
                
            system_prompt = " ".join(system_parts)
            
            # Call AI
            result = self._call_ai(task, prompt, system_prompt)
            
            logger.info(f"✅ Text generation completed using {result['provider']}")
            return task.complete(result)
            
        except Exception as e:
            logger.error(f"❌ Text generation failed: {e}")
            return task.failure(f"Text generation error: {str(e)}")

    def handle_analysis(self, task: ExternalTask) -> TaskResult:
        """Handle analysis external tasks"""
        try:
            logger.info(f"🔍 Processing analysis task: {task.get_task_id()}")
            
            data = task.get_variable("data")
            analysis_type = task.get_variable("analysis_type")  # e.g., "sentiment", "summary", "trends"
            instructions = task.get_variable("instructions")
            
            if not data:
                return task.failure("Data is required for analysis")
            
            # Build prompt
            prompt = f"Please analyze the following data:\n\n{data}"
            
            if analysis_type:
                prompt += f"\n\nFocus on {analysis_type} analysis."
            
            if instructions:
                prompt += f"\n\nSpecific instructions: {instructions}"
            
            system_prompt = "You are an expert data analyst. Provide clear, actionable insights."
            
            # Call AI
            result = self._call_ai(task, prompt, system_prompt)
            
            logger.info(f"✅ Analysis completed using {result['provider']}")
            return task.complete(result)
            
        except Exception as e:
            logger.error(f"❌ Analysis failed: {e}")
            return task.failure(f"Analysis error: {str(e)}")

    def handle_code_generation(self, task: ExternalTask) -> TaskResult:
        """Handle code generation external tasks"""
        try:
            logger.info(f"💻 Processing code generation task: {task.get_task_id()}")
            
            description = task.get_variable("description")
            language = task.get_variable("language")  # e.g., "python", "javascript"
            framework = task.get_variable("framework")  # e.g., "react", "flask"
            requirements = task.get_variable("requirements")
            
            if not description:
                return task.failure("Description is required for code generation")
            
            # Build prompt
            prompt = f"Write code based on this description: {description}"
            
            if language:
                prompt += f"\n\nUse {language} programming language."
            if framework:
                prompt += f"\n\nUse {framework} framework."
            if requirements:
                prompt += f"\n\nAdditional requirements: {requirements}"
            
            system_prompt = "You are an expert software developer. Write clean, well-documented code with comments."
            
            # Call AI
            result = self._call_ai(task, prompt, system_prompt)
            
            logger.info(f"✅ Code generation completed using {result['provider']}")
            return task.complete(result)
            
        except Exception as e:
            logger.error(f"❌ Code generation failed: {e}")
            return task.failure(f"Code generation error: {str(e)}")

    def handle_translation(self, task: ExternalTask) -> TaskResult:
        """Handle translation external tasks"""
        try:
            logger.info(f"🌍 Processing translation task: {task.get_task_id()}")
            
            text = task.get_variable("text")
            source_language = task.get_variable("source_language")
            target_language = task.get_variable("target_language")
            
            if not text or not target_language:
                return task.failure("Text and target_language are required for translation")
            
            # Build prompt
            if source_language:
                prompt = f"Translate the following text from {source_language} to {target_language}:\n\n{text}"
            else:
                prompt = f"Translate the following text to {target_language}:\n\n{text}"
            
            system_prompt = "You are an expert translator. Provide accurate translations that preserve meaning and context."
            
            # Call AI
            result = self._call_ai(task, prompt, system_prompt)
            
            logger.info(f"✅ Translation completed using {result['provider']}")
            return task.complete(result)
            
        except Exception as e:
            logger.error(f"❌ Translation failed: {e}")
            return task.failure(f"Translation error: {str(e)}")

def main():
    """Main entry point for the AI worker"""
    try:
        worker = AIWorker()
        worker.start()
        
        logger.info("🤖 AI Worker running... Press Ctrl+C to stop")
        
        # Keep the worker running
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("AI Worker stopped by user")
    except Exception as e:
        logger.error(f"AI Worker failed: {e}")
        logger.error(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    main()