## PEO (Process Execution/Definition Orchestrator)

### In plain words
- PEO runs a process diagram from start to finish
- It routes steps and calls TDEs to do the work
- PEO does not do the work itself

### Simple view
```mermaid
sequenceDiagram
    autonumber
    participant P as PEO
    participant T as TDE
    participant E as Engine

    P->>E: Start process
    loop Each step
        P->>T: Call task
        T-->>P: Return result
        P->>P: Route to next step
    end
    P-->>E: Complete process
```


