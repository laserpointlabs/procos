## Micro‑kernel (simple)

### What it does
- Boots the BPMN engine
- Deploys process models
- Monitors health

### Why it is small
- Fewer moving parts
- Easier to reason about
- Safer changes

```mermaid
flowchart LR
    Start[Start system] --> Boot[Micro‑kernel boots engine]
    Boot --> Deploy[Deploy BPMN models]
    Deploy --> Monitor[Monitor health]
```


