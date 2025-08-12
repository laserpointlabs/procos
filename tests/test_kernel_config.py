#!/usr/bin/env python3

import os
import importlib


def test_config_validation_pass(monkeypatch):
    monkeypatch.setenv("CAMUNDA_BASE_URL", "http://localhost:8080")
    monkeypatch.setenv("HEALTH_CHECK_INTERVAL", "5")
    monkeypatch.setenv("HEALTH_BACKOFF_BASE_SECONDS", "2.0")
    monkeypatch.setenv("CAMUNDA_READY_MAX_ATTEMPTS", "3")
    monkeypatch.setenv("CAMUNDA_READY_BASE_SLEEP_SECONDS", "0.1")
    monkeypatch.setenv("CAMUNDA_READY_JITTER_SECONDS", "0.1")

    mk = importlib.import_module("src.microkernel.procos_kernel")
    cfg = mk.ProcOSConfig()
    # Should not raise in validation when calling via kernel
    kernel = mk.ProcOSKernel()
    # Run only validate method
    kernel._validate_environment()


def test_config_validation_fail(monkeypatch):
    monkeypatch.delenv("CAMUNDA_BASE_URL", raising=False)
    mk = importlib.import_module("src.microkernel.procos_kernel")
    kernel = mk.ProcOSKernel()
    try:
        kernel._validate_environment()
        assert False, "Expected RuntimeError for missing CAMUNDA_BASE_URL"
    except RuntimeError as e:
        assert "CAMUNDA_BASE_URL" in str(e)


