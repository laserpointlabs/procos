#!/usr/bin/env python3
"""
PDO Orchestrator (stub)

A thin Python facade representing the Process Definition Orchestrator. In
ProcOS, the actual orchestration is defined in BPMN and executed by Camunda.
This module provides interfaces and helpers the microkernel or DAS can use to
interact with PDO instances via Camunda REST.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional
import requests


@dataclass
class PDOConfig:
    camunda_base_url: str
    engine_api: str


class ProcessDefinitionOrchestrator:
    def __init__(self, config: PDOConfig):
        self.config = config

    def start(self, key: str, variables: Optional[Dict] = None) -> Dict:
        """Start a PDO BPMN process by key."""
        payload = {"variables": variables or {}}
        resp = requests.post(
            f"{self.config.engine_api}/process-definition/key/{key}/start",
            json=payload,
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()


