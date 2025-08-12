#!/usr/bin/env python3
"""
ProcOS Metrics Utilities

Lightweight in-memory metrics collector for kernel and services.
Exports a simple snapshot on demand or emits to logs on shutdown.
"""

from __future__ import annotations

import json
import threading
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict


@dataclass
class KernelMetrics:
    """In-memory counters for the ProcOS kernel."""

    health_checks_ok: int = 0
    health_checks_fail: int = 0
    camunda_wait_attempts: int = 0
    deployments_attempted: int = 0
    deployments_succeeded: int = 0

    _lock: threading.Lock = field(default_factory=threading.Lock, init=False, repr=False)

    def increment(self, name: str, amount: int = 1) -> None:
        with self._lock:
            if not hasattr(self, name):
                raise AttributeError(f"Unknown metric: {name}")
            setattr(self, name, getattr(self, name) + amount)

    def snapshot(self) -> Dict[str, int]:
        with self._lock:
            return {
                "health_checks_ok": self.health_checks_ok,
                "health_checks_fail": self.health_checks_fail,
                "camunda_wait_attempts": self.camunda_wait_attempts,
                "deployments_attempted": self.deployments_attempted,
                "deployments_succeeded": self.deployments_succeeded,
            }

    def write_snapshot(self, target_file: Path) -> None:
        target_file.parent.mkdir(parents=True, exist_ok=True)
        data = self.snapshot()
        target_file.write_text(json.dumps(data, indent=2))

    def log_snapshot(self, logger) -> None:
        logger.info(
            json.dumps({
                "event": "kernel_metrics_snapshot",
                "metrics": self.snapshot(),
            })
        )


