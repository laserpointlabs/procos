# PDO (Process Definition Orchestrator)

In ProcOS, PDO is BPMN-first. Orchestration logic lives in BPMN deployed to
Camunda. The microkernel boots the engine, deploys PDO/TDE processes, and
monitors health and events. It does not contain a Python imperative PDO layer.

- Start new instances via Camunda REST or BPMN triggers
- Route work to TDEs via BPMN gateways and call activities
- Keep the orchestrator logic declarative and visual


