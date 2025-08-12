#!/usr/bin/env python3

import importlib


def test_health_check_failure_increments_metric(monkeypatch):
    mk = importlib.import_module("src.microkernel.procos_kernel")
    kernel = mk.ProcOSKernel()

    # Force requests.get to raise a connection error
    class ConnErr(Exception):
        pass

    def fake_get(*args, **kwargs):
        raise mk.requests.exceptions.ConnectionError("boom")

    monkeypatch.setattr(mk.requests, "get", fake_get)

    before_fail = kernel.metrics.health_checks_fail
    ok = kernel._perform_health_check()
    assert ok is False
    assert kernel.metrics.health_checks_fail == before_fail + 1


def test_wait_for_camunda_times_out(monkeypatch):
    mk = importlib.import_module("src.microkernel.procos_kernel")
    kernel = mk.ProcOSKernel()

    # Speed up: small attempts and no sleeping
    kernel.config.camunda_ready_max_attempts = 2
    kernel.config.camunda_ready_base_sleep_seconds = 0
    kernel.config.camunda_ready_jitter_seconds = 0

    def fake_get(*args, **kwargs):
        # simulate timeout/unreachable
        raise mk.requests.exceptions.Timeout()

    monkeypatch.setattr(mk.requests, "get", fake_get)
    monkeypatch.setattr(mk.time, "sleep", lambda *_: None)

    try:
        kernel._wait_for_camunda()
        assert False, "Expected RuntimeError when Camunda not reachable"
    except RuntimeError as e:
        assert "failed to start" in str(e)


