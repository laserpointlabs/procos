## Use Cases (simple)

### 1) Onboard a new process
- SME writes steps in plain words
- DAS drafts a BPMN diagram
- Team reviews and runs it as an MVP

```mermaid
flowchart LR
    SME[SME describes steps] --> DAS[DAS drafts BPMN]
    DAS --> Review[Team reviews]
    Review --> Run[Run MVP]
    Run --> Learn[Save results / suggest improvements]
```

### 2) Add a new task safely
- Edit the diagram
- TDE handles the new task
- DAS saves what happened

```mermaid
flowchart LR
    Edit[Edit BPMN] --> Deploy[Deploy]
    Deploy --> Run[Run]
    Run --> Save[DAS saves results]
```

### 3) Repeatable operations
- PEO runs the same steps each time
- TDEs do the work
- Results are tracked and learned from

```mermaid
sequenceDiagram
    autonumber
    participant P as PEO
    participant T as TDE(s)
    participant D as DAS

    P->>T: Do task A
    T-->>P: Done
    P->>T: Do task B
    T-->>P: Done
    P->>D: Log results
```


