# ProcOS Kernel Structured Events Schema

This document defines the JSON event shapes emitted by the ProcOS microkernel during startup, monitoring, and shutdown. Events are logged via the kernel logger as single-line JSON objects for easy ingestion.

## Common Fields

- `event` (string): Event name (see below)
- `component` (string): Always `"kernel"` for kernel events
- `ts` (optional string): ISO timestamp when available (logger may add)
- Additional fields depend on event type

## Events

### kernel_starting

Emitted when the kernel process initializes.

Example:
```json
{
  "event": "kernel_starting",
  "component": "kernel",
  "version": "1.0.0",
  "env": "development"
}
```

Fields:
- `version` (string) — kernel version
- `env` (string) — environment name

### kernel_bootstrap_start

Emitted at the beginning of the bootstrap sequence.

```json
{
  "event": "kernel_bootstrap_start",
  "component": "kernel"
}
```

### kernel_bootstrap_complete

Emitted when bootstrap successfully completes and the kernel is entering monitoring mode.

```json
{
  "event": "kernel_bootstrap_complete",
  "component": "kernel",
  "phase": "monitoring"
}
```

Fields:
- `phase` (string) — next phase; currently `"monitoring"`

### kernel_bootstrap_failed

Emitted if bootstrap raises a fatal exception.

```json
{
  "event": "kernel_bootstrap_failed",
  "component": "kernel",
  "error": "<stringified exception>"
}
```

Fields:
- `error` (string) — error message

### kernel_signal

Emitted when the kernel receives a shutdown signal.

```json
{
  "event": "kernel_signal",
  "component": "kernel",
  "signal": 15,
  "message": "initiating graceful shutdown"
}
```

Fields:
- `signal` (number) — signal number
- `message` (string) — description

### kernel_stopping

Emitted during graceful shutdown just before process exit.

```json
{
  "event": "kernel_stopping",
  "component": "kernel"
}
```

### kernel_metrics_snapshot

Emitted on shutdown after writing metrics to disk.

```json
{
  "event": "kernel_metrics_snapshot",
  "metrics": {
    "health_checks_ok": 10,
    "health_checks_fail": 2,
    "camunda_wait_attempts": 5,
    "deployments_attempted": 3,
    "deployments_succeeded": 3
  }
}
```

Fields:
- `metrics` (object) — see metrics.json for full snapshot content

## Notes

- All events are single-line JSON to simplify log parsing.
- Timestamps may be added by the logging layer; consumers can also rely on file TS.
- Future: event correlation IDs can be added to `kernel_starting` and propagated.


