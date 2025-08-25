## ProcOS — Start Here (for managers)

### In one sentence
ProcOS lets a subject‑matter expert grow a simple “virtual OS” around their work, step by step, with help from a built‑in digital assistant.

### What the tool does
- Helps an SME describe how work should be done (in plain steps)
- Turns those steps into simple process diagrams (BPMN)
- Runs the process the same way every time
- Saves discussions, tasks, tests, and results as knowledge
- Lets you add/change steps without rebuilding apps

### How the system grows
- We grow only with BPMN processes.
- To change behavior, you edit a diagram, not code.
- Small, safe edits are easy to test and ship.

### The three base parts
1. Micro‑kernel: tiny core that boots, watches, and keeps the system stable
2. PDO (Process Definition Orchestrator): runs a BPMN process end‑to‑end
3. TDE (Task Definition Executor): does the actual work inside a step

These parts stay small on purpose. You can start with a very small baseline, test it, and ship an MVP. Users can keep growing by adding processes and tasks over time.

### The Digital Assistant Service (DAS)
- Built in from day one
- Sees actions as they happen
- Stores discussions, tasks, tests, and results as knowledge
- Helps design and refine processes
- Surfaces what worked (and what didn’t) when you make changes

### What you get at MVP
- A minimal system that runs a few key processes (via PDO + TDE)
- The micro‑kernel running and stable
- DAS capturing context and showing results
- A clear path to add more processes safely

### How teams use it (simple flow)
1. SME describes the goal
2. DAS drafts a BPMN process
3. Team reviews and tweaks the steps
4. Run it and see results
5. DAS saves what happened and suggests improvements

### What this is not
- Not a big platform rewrite
- Not a custom app per team
- Not a black box: processes are plain BPMN; tasks are simple and testable

### The pitch
Start small. Run real work. Learn fast. Grow safely. ProcOS makes your expert knowledge runnable and easy to improve, using only simple BPMN processes and three small parts: micro‑kernel, PDO, and TDE.

### Quick links
- Index of this set: [INDEX.md](./INDEX.md)
- Architecture: [architecture.md](./architecture.md)
- DAS: [das.md](./das.md)
- Micro‑kernel: [microkernel.md](./microkernel.md)
- PEO: [peo.md](./peo.md)
- TDE: [tde.md](./tde.md)
- Use cases: [use_cases.md](./use_cases.md)