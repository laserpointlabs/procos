# ProcOS / KnowOS Master TODO (Focused Edition)

Goal: Make the four living pillars operate together fast: Microkernel + PEOs (Process Execution Orchestrators) + TDEs (Task Definition Executors) + DAS (Digital Assistance System) with a Streamlit UI for generation, inspection, and knowledge operations. Remove legacy "worker" mindset; everything is orchestrated through BPMN-defined PEOs and TDE templates.

Legend:
- Priority: P0 (critical walking skeleton), P1 (near-term hardening), P2 (expansion), P3 (future/idea)
- Status: [ ] not started, [~] in progress, [x] done, [!] blocked

---
## 0. Walking Skeleton Readiness (Rolling Snapshot)
- Kernel bootstrap stable (env validate → Camunda ready → deploy → monitor): [ ]
- Root PEO BPMN deployed & starts cleanly: [ ]
- TDE template BPMN executes a sample deterministic + probabilistic task: [ ]
- DAS can ingest docs (via BPMN) and answer a RAG query: [ ]
- Streamlit UI: submit natural language → returns generated BPMN draft: [ ]
- Generated BPMN passes validation & can be deployed: [ ]
- Logging & minimal metrics observable: [ ]

---
## 1. Bootstrap & Environment (P0)
- [x] Verify docker-compose brings up Camunda + Postgres (adjust ports/healthchecks if needed)
- [x] Create `.env` from `env.example` with mandatory values (CAMUNDA_BASE_URL, VECTOR_BACKEND, EMBEDDING_MODEL)
- [x] Ensure microkernel launched via compose (service entrypoint) or documented local cmd
- [x] Add Makefile targets: up, down, logs, test, format
- [x] Extend `scripts/health_check.py` to assert: Camunda engine list, deployment count, version
- [x] Add simple readiness file `/tmp/procos.ready` after bootstrap success
- [x] Unified lifecycle script `procos.sh` (start/stop/restart/status/logs/test/down)

---
## 2. Microkernel Hardening (P0/P1)
- [ ] Centralized config validation (aggregate all missing/invalid vars before exit)
- [~] Retry/backoff constants for Camunda polling (exponential jitter)
- [ ] Structured startup event JSON log (component=kernel, phase=bootstrap_complete)
- [ ] Graceful shutdown event emission (kernel_stopping)
- [ ] Lightweight internal metrics collector (in-memory counters; export on demand)
- [ ] Unit tests: config validation, health check error path, Camunda timeout

---
## 3. Core BPMN Set (P0)
Directory: `src/processes/`
- [ ] `root_peo.bpmn` (aka system orchestrator) — phases: init_env → load_knowledge (call) → enable_generation → idle_monitor
- [ ] `knowledge_preload.bpmn` — iterate sources → chunk → embed → store → record manifest
- [ ] `rag_query.bpmn` — accept query → retrieve (vector) → synthesize (LLM) → return answer
- [ ] `process_generation.bpmn` — input intent → gather context (patterns+examples) → draft BPMN (LLM) → validate → approval (dev bypass) → commit/deploy
- [ ] `tde_template.bpmn` — receive task spec → select execution mode (probabilistic vs deterministic) → execute → report outcome
- [ ] Error boundary events + escalation pattern library (shared subprocess) added to repo
- [ ] BPMN metadata convention doc (name, version, intent, domain, created_by, validation_hash)
- [ ] Basic BPMN linter checklist (manual initially)

---
## 4. DAS Core (P0/P1)
Create `src/das/` structure.
- [ ] Package skeleton: `generation/`, `knowledge/`, `validation/`, `interfaces/`
- [ ] DAS interface: `initialize()`, `generate_process(intent:str)->BPMNArtifact`, `answer_query(q:str)->str`
- [ ] Vector access abstraction (embed, upsert, query)
- [ ] Knowledge manifest recorder (JSON lines: source, hash, ts, status)
- [ ] Prompt templates store (YAML) with version fields
- [ ] Simple BPMN validation (XML parse + required elements + naming rules)
- [ ] DAS README with ASCII architecture diagram

---
## 5. Vector / Knowledge Layer (P0)
- [ ] Choose default backend (pgvector vs FAISS) (Open Question #1)
- [ ] Embedding model selection logic (env: LOCAL_OLLAMA=true → local; else remote provider)
- [ ] Chunker implementation (semantic boundary + max tokens fallback)
- [ ] Ingestion script invoked by `knowledge_preload.bpmn` (script task or external reference)
- [ ] Retrieval API: `retrieve(query, k, filters)` returns scored docs + metadata
- [ ] Re-index delta logic (hash compare); skip unchanged
- [ ] Unit tests: chunk edge cases (small file, huge file), retrieval ranking deterministic stub
- [ ] (NEW) VectorRepository interface stub (export/import capable) added under `src/das/knowledge/vector_repository.py`

---
## 6. PEO Architecture (P1)
- [ ] Formalize PEO responsibilities doc (no business logic; purely orchestration)
- [ ] Correlation ID propagation pattern (kernel → PEO → TDE)
- [ ] State transition logging (peo_state_change events)
- [ ] Parallel task handling test BPMN (gateway fan-out/fan-in)
- [ ] Timeout & retry semantics (boundary timer events) reference implementation

---
## 7. TDE Execution Model (P1)
- [ ] TDE task spec schema (JSON: id, inputs, mode=prob|deterministic, tools[])
- [ ] Probabilistic execution loop (LLM propose → evaluate → converge / max_iters)
- [ ] Deterministic adapter interface (e.g., FileOps, HTTP, Shell)
- [ ] Safety guard: sandbox path + allowlist for file/network operations
- [ ] Outcome report schema (status, outputs, probs, elapsed_ms)
- [ ] Add synthetic test tasks (echo, sum, classify) for harness

---
## 8. Process Generation Pipeline (P1)
- [ ] Intent normalization (strip noise, classify domain)
- [ ] Context assembly (patterns + examples + similar BPMN retrieval)
- [ ] LLM drafting prompt (include constraints + naming rules)
- [ ] Post-draft structural validation (XML + BPMN semantics subset)
- [ ] Logging: generation_attempt event with quality metrics placeholder
- [ ] Approval gate path; auto-approve dev mode flag
- [ ] Deployment step (call Camunda REST) with duplicate filtering

---
## 9. Streamlit UI (Generation & Ops) (P0/P1)
Dir: `ui/streamlit_app/`
- [ ] Minimal app shell (layout + sidebar status indicators)
- [ ] Panel: "Generate Process" (textarea intent → show BPMN XML + diagram render placeholder)
- [ ] Panel: "RAG Query" (input → answer with source snippets + score)
- [ ] Panel: "Knowledge Ingestion" (list sources, trigger re-index)
- [ ] Panel: "Running Instances" (poll Camunda instances; show state)
- [ ] Live log tail (polling fallback; websocket future)
- [ ] Simple BPMN diagram display (embed bpmn-js viewer or static SVG first)
- [ ] Action buttons (redeploy all, health check trigger)

---
## 10. Observability & Logging (P0/P1)
- [ ] Standard log schema (ts, level, component, event, correlation_id, process_instance_id, peo_id, tde_id, duration_ms)
- [ ] Logging utility to enrich context automatically
- [ ] Minimal metrics: counters (bpmn_deploys, generation_attempts, tde_success, tde_failure)
- [ ] Health check script extended to verify metric increments after sample run
- [ ] Redaction rules (mask secrets pattern)

---
## 11. Testing Strategy (P0/P1)
- [ ] Adopt pytest + config
- [ ] Unit: kernel config, vector chunking, DAS generation stub, BPMN validator
- [ ] Integration: deploy root_peo + launch instance + run through knowledge preload stub
- [ ] Scenario: generate process via UI → deploy → start → TDE executes deterministic task
- [ ] Smoke test script for CI (exit non-zero on failure)
- [ ] Coverage target initial 60%

---
## 12. Refactoring & Legacy Cleanup (P1)
- [ ] Mark `workers/` modules as legacy (rename folder `legacy_workers/` or deprecate note)
- [ ] Extract any reusable logic (logging helpers) into shared utils
- [ ] Remove worker polling loops once PEO+TDE path stable
- [ ] Update docs removing "worker" terminology (except historical context)

---
## 13. Governance & Safety (P2)
- [ ] BPMN generation policy rules (forbidden tasks, naming conventions)
- [ ] Validation hooks (pre-deploy gate)
- [ ] Audit log events: process_generated, process_deployed, knowledge_ingested
- [ ] Rollback: store last N BPMN versions & redeploy previous

---
## 14. Domain Specialization (P2)
- [ ] Domain profile metadata (stored alongside BPMN)
- [ ] Domain-aware retrieval filters
- [ ] Template override mechanism
- [ ] Evaluation metrics per domain (latency, success_rate)

---
## 15. Performance & Scaling (P2)
- [ ] Baseline latency measurements (generation, retrieval, TDE run)
- [ ] Parallel TDE stress test BPMN
- [ ] Optional async microkernel loops
- [ ] Caching frequent retrieval results (LRU layer)

---
## 16. CI/CD (P1)
- [ ] GitHub Action: lint + test + coverage + build image
- [ ] Artifact upload: logs + coverage report
- [ ] Failing scenario test attaches truncated log excerpt

---
## 17. Documentation Enhancements (P1/P2)
- [ ] BPMN style/metadata guide
- [ ] TDE execution model explainer
- [ ] Process generation prompt design doc
- [ ] Knowledge ingestion flow diagram
- [ ] PEO vs TDE responsibility matrix

---
## 18. Quality Gates
- [ ] Lint clean
- [ ] Unit + integration tests green
- [ ] Coverage >= target
- [ ] Health check passes after sample run
- [ ] No P0 open issues at release tag
- [ ] BPMN validation passes for all new definitions

---
## 19. Open Questions (Track & Resolve Early)
- [ ] (Q1) Primary vector backend default? (pgvector vs FAISS) — decide
- [ ] (Q2) BPMN versioning & promotion flow (direct deploy vs PR-like)
- [ ] (Q3) Embedding model fallback chain ordering
- [ ] (Q4) Deterministic tool sandboxing strategy (chroot? path allowlist?)
- [ ] (Q5) Long-running task handling (compensation pattern needed?)

---
## 20. Roadmap / Milestones
M0 Walking Skeleton (P0): Microkernel + root_peo + tde_template + knowledge_preload stub + Streamlit generate + basic retrieval
- [ ] All Section 1–5 + essential parts of 9 & 10 complete

M1 Generation & RAG Solidified: Stable process_generation.bpmn + validated drafts + RAG accuracy baseline
- [ ] Sections 6–8 core done

M2 TDE Expansion & Governance: Probabilistic loop robust + governance rules + rollback
- [ ] Sections 7 + 13 finalized

M3 Domain Layer: Domain metadata, specialization hooks
- [ ] Section 14 initial

M4 Performance & Scaling: Stress + caching + async options
- [ ] Section 15

---
## 21. Backlog / Future (P3)
- [ ] Graph DB lineage + pattern mining
- [ ] Autonomous self-diagnosis process (meta-PEO)
- [ ] Collaborative real-time BPMN editing assistance
- [ ] Adaptive prompt optimization loop (multi-armed bandit)
- [ ] Multi-agent negotiation patterns
- [ ] Ontology integration (requirements → components → processes linkage)

---
## 22. Risk Register
| Risk | Impact | Mitigation | Status |
|------|--------|------------|--------|
| LLM hallucination in BPMN draft | Invalid deployments | Structural validator + approval gate | Open |
| Vector drift (stale embeddings) | Poor retrieval quality | Hash-based delta + scheduled refresh | Open |
| Over-coupling DAS & kernel | Hard refactor later | Clear interface module boundaries | Open |
| Logging noise / volume | Signal loss | Schema + sampling if needed | Open |
| Single Camunda instance | Orchestration outage | Add HA/backup plan later | Open |

---
## 23. Daily Update Template
```
Date:
Kernel:
PEO/TDE Status:
DAS Generation:
Knowledge Delta:
UI Changes:
Incidents:
Risks Emerging:
Next 24h Priorities:
```

---
## 24. Execution Order (Condensed)
1. Bootstrap & kernel (Sections 1–2)
2. Core BPMN + knowledge preload (Section 3 + parts of 5)
3. DAS base + vector ops (Sections 4–5)
4. Streamlit generation panel (Section 9 minimal subset)
5. PEO architecture + TDE model (Sections 6–7)
6. Generation pipeline refinement (Section 8)
7. Observability + tests hardening (Sections 10–11)
8. Governance & domain expansion (Sections 13–14)

Keep this file living; move completed milestone notes to RELEASE_NOTES and aggressively prune obsolete tasks.

---
## 25. Migration & Portability (New)
Reference: `docs/architecture/migration_and_portability.md`
- [ ] Implement VectorRepository export/import (see Section 2 & 3 of migration doc)
- [ ] Scaffold `export_snapshot.bpmn` (start → freeze flag → dump vectors → package → checksum → release flag → emit event)
- [ ] Scaffold `import_snapshot.bpmn` (validate → verify checksums → load vectors/artifacts → rebuild index → readiness event)
- [ ] Scaffold `validate_snapshot.bpmn` (sample queries → compare ranks → pass/fail)
- [ ] Streamlit Migration Panel (export button, import uploader, status display)
- [ ] Snapshot manifest & checksum generator script (`scripts/generate_snapshot.py`)
