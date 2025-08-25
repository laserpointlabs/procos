## ProcOS First-Order Summary — Index

### Read this set in order
- Start here: [procos_start_here.md](./procos_start_here.md)
- Architecture (simple): [architecture.md](./architecture.md)
- Digital Assistant Service (DAS): [das.md](./das.md)
- Micro‑kernel: [microkernel.md](./microkernel.md)
- PEO (orchestrator): [peo.md](./peo.md)
- TDE (task executor): [tde.md](./tde.md)
- Use cases: [use_cases.md](./use_cases.md)

### One-picture overview
```mermaid
graph TB
    subgraph "ProcOS"
        MK["Micro‑kernel"] --> ENG["BPMN Engine"]
        ENG --> PEO["PEO (Orchestrator)"]
        PEO --> TDE["TDE (Task Executor)"]
        TDE --> ENG
        DAS["DAS (Assistant)"] -. watches .-> PEO
        DAS -. watches .-> TDE
        DAS --> KB["Knowledge Store"]
    end

    click MK "./microkernel.md" "Micro‑kernel"
    click PEO "./peo.md" "PEO"
    click TDE "./tde.md" "TDE"
    click DAS "./das.md" "DAS"
```

### What to look for
- Clear roles: micro‑kernel boots, PEO orchestrates, TDE executes, DAS learns
- BPMN‑only growth: change diagrams, not code
- MVP first: start small, add steps safely
