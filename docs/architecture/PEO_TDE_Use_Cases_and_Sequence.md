# BPMN-First PEO/TDE Model — Use Cases and Sequence

Version: 0.1 (Draft)
Date: 2025-01
Status: Draft for review

---

## Purpose

This paper defines the BPMN-first execution model for ProcOS using two core roles:

- **PEO (Process Execution Orchestrator)**: Responsible for orchestration only — routing, state, error boundaries, compensation, and delegation to task engines. No business logic.
- **TDE (Task Definition Executor)**: Responsible for executing an individual task in either deterministic (tool/adapter) or probabilistic (LLM-guided) mode.

The design aligns with ProcOS principles in `docs/architecture/ProcOS_Architecture_Specification.md` and the minimal microkernel in `src/microkernel/procos_kernel.py` where BPMN is the kernel language and the microkernel only boots, deploys, and monitors.

---

## Glossary

- **BPMN-first**: Behavior is defined in BPMN; code is limited to small, testable adapters (no imperative orchestration in code).
- **PEO**: BPMN process that orchestrates a business or system scenario. It delegates work; it does not implement work.
- **TDE Template (BPMN)**: BPMN subprocess (or called activity) that encapsulates a single task life-cycle (deterministic/probabilistic branches, retries, and governance).
- **TDE Executor/Adapter (Code)**: Thin, testable shims used by TDE BPMN when deterministic actions are required (e.g., HTTP, file I/O). See `src/tde/tde_executor.py`.
- **Camunda Engine**: Provides stateful process execution, external task pattern, and history.
- **Correlation ID**: End-to-end identifier that flows kernel → PEO → TDE → adapters → logs/metrics.

---

## High-Level Runtime Sequence

The following sequence shows a typical end-to-end execution where a PEO delegates to a TDE that may choose deterministic or probabilistic execution, then returns control to the PEO for continued orchestration.

```mermaid
sequenceDiagram
    autonumber
    participant U as User/DAS
    participant K as Microkernel
    participant C as Camunda Engine
    participant P as PEO (BPMN)
    participant T as TDE Template (BPMN)
    participant X as TDE Executor (Adapters)
    participant S as External Systems/APIs

    U->>C: Start PEO process (key=domain_process)
    K->>C: Deploy BPMN on bootstrap (optional auto-deploy)
    C-->>P: Create PEO instance with correlationId

    Note over P,P: PEO orchestrates only. No business logic.
    P->>C: Call Activity → TDE Template (taskSpec, mode)
    C-->>T: Instantiate TDE subprocess (inherits correlationId)

    alt Deterministic Path
        T->>X: Invoke adapter with inputs (toolSpec, context)
        X->>S: Perform action (HTTP/file/shell/etc.)
        S-->>X: Result/response
        X-->>T: Deterministic outputs
    else Probabilistic Path
        T->>X: Enter LLM loop (analyze → act → evaluate)
        loop Until success/guardrail/limit
            X->>S: Optional tool calls (retrieval, write, API)
            S-->>X: Signals/data
        end
        X-->>T: Probabilistic outputs + reasoning trace
    end

    T-->>C: Complete TDE subprocess (result vars)
    C-->>P: Resume PEO with task result
    P->>P: Route via gateways (success/retry/compensate)
    P-->>C: Continue or complete PEO instance

    Note over K,C: Kernel remains passive after bootstrap; monitoring only
```

---

## Object Responsibilities (Step-by-Step)

### Microkernel (`src/microkernel/procos_kernel.py`)
1. Validate environment and configuration (engine URL, health intervals).
2. Wait for Camunda readiness and write a readiness marker.
3. Deploy BPMN models from `src/processes` when `AUTO_DEPLOY_PROCESSES=true`.
4. Optionally start a root orchestrator (if present), e.g., `system_orchestrator`.
5. Enter monitoring mode; no orchestration or business logic at runtime.

### Camunda Engine
1. Persist process definitions and instances; track all tokens and variables.
2. Execute BPMN semantics for PEO and TDE templates.
3. Provide the External Task pattern for adapters if used.
4. Emit history for auditing (who/what/when + variables).

### PEO (Process Execution Orchestrator) — BPMN process
1. Receive start event and initialize `correlationId` and context variables.
2. Select next task via BPMN gateways (business rules in BPMN, not code).
3. Delegate actual work to a TDE Template via Call Activity or Subprocess.
4. Handle normal/exceptional outcomes through explicit BPMN boundary events.
5. Apply compensation/rollback flows where required.
6. Emit observability events to logs/metrics as variables or external tasks.

### TDE Template — BPMN subprocess for a single task
1. Accept inputs: `taskSpec`, `mode` = `deterministic | probabilistic`, `correlationId`.
2. Branch by mode using an exclusive gateway.
3. Deterministic: Call adapter service task(s) for concrete actions (HTTP, file, etc.).
4. Probabilistic: Enter a governed loop (limits, guardrails) for LLM-guided actions; optionally invoke adapters.
5. Capture outputs and structured traces (decisions, tool calls, errors) into variables.
6. On failure, raise BPMN error to PEO, or apply local retry per policy.

### TDE Executor/Adapters — Code (see `src/tde/tde_executor.py`)
1. Provide a thin interface with a spec (`TDESpec`) and two modes.
2. Deterministic: Directly execute a single, testable action; return structured outputs.
3. Probabilistic: Orchestrate a bounded analyze→act→evaluate loop; return outputs + reasoning trace.
4. Never embed orchestration; return control to BPMN immediately after work.

---

## Core Use Cases

- **UC-1: Deterministic Tool Call**
  - PEO delegates to TDE with `mode=deterministic` and `toolSpec=http.post`.
  - TDE invokes adapter → performs HTTP call → returns response JSON → PEO routes next step.

- **UC-2: Probabilistic Content Generation**
  - PEO delegates with `mode=probabilistic` and a prompt/context.
  - TDE runs an LLM loop with guardrails and optional retrieval; returns draft → PEO routes to review or auto-approve.

- **UC-3: Retry and Compensation**
  - TDE raises BPMN error on adapter failure; PEO catches and routes to retry or compensation subprocess.

- **UC-4: Parallelization**
  - PEO spawns multiple TDE call activities (multi-instance) for fan-out; joins on completion; routes aggregate result.

---

## Governance and Guardrails

- Deterministic adapters must be idempotent where feasible; otherwise provide compensations.
- Probabilistic loops must enforce limits (iterations, time) and capture reasoning traces.
- All paths must propagate `correlationId` and key variables for end-to-end auditing.
- Errors should be explicit BPMN errors, not silent failures; prefer boundary events.

---

## Correlation and Observability

- Generate `correlationId` at process start; store as a root variable.
- Include `correlationId` in adapter calls, logs, and metrics snapshots.
- Use kernel metrics for health and lightweight counters; use BPMN history for state.

---

## Implementation Notes

- The microkernel intentionally contains no imperative orchestration. See `_deploy_processes` and `_start_root_orchestrator` for bootstrap only.
- Keep PEO BPMN definitions readable: gateways for rules, boundary events for errors, and call activities for TDE templates.
- Keep adapters tiny and testable; avoid embedding orchestration or decision logic in code.
- TDE spec example (code-side) is modeled in `src/tde/tde_executor.py` to keep the surface area minimal and explicit.

---

## Example: Minimal TDE Template (Conceptual)

This conceptual BPMN layout (not the full XML) illustrates a TDE with two branches:

```
Start → Exclusive Gateway (mode)
  → [deterministic] Service Task (Adapter Call) → End
  → [probabilistic] Subprocess (LLM Loop + Guardrails) → End
```

Represent each step explicitly in BPMN to keep execution transparent and auditable.

---

## Next Steps

- Add reference BPMN models under `src/processes/`:
  - `peo_example.bpmn` (orchestration only)
  - `tde_task_template.bpmn` (deterministic/probabilistic branches)
- Wire minimal deterministic adapter (HTTP/file) and end-to-end test scenario.
- Expand governance (timeouts, retries, compensations) as formal templates.


