# Migration & Portability Strategy (Vector Store + Knowledge Layer)

Goal: Lift-and-shift ProcOS (Microkernel + PEOs + TDEs + DAS) to new infrastructure (e.g., AWS, on‑prem, another cloud) **without losing knowledge memory** (embeddings, BPMN artifacts, prompts, logs, manifests) and with verifiable integrity.

---
## 1. Terminology
- Knowledge Artifact: Any BPMN XML, prompt template, pattern, example, domain profile.
- Embedding Record: {id, vector, metadata(json), version, source_hash, created_ts, updated_ts}.
- Snapshot: Immutable export bundle with manifest + data files + checksums.
- Delta: Increment since last snapshot (new/updated/deleted artifacts).

---
## 2. Abstraction Layer Contracts
Implement a `VectorRepository` interface to avoid backend lock-in:
```
class VectorRepository:
    def upsert(self, records: list[EmbeddingRecord]): ...
    def query(self, vector, k:int, filters: dict): ...
    def fetch(self, ids: list[str]): ...
    def delete(self, ids: list[str]): ...
    def export_snapshot(self, dest: Path) -> SnapshotManifest: ...
    def import_snapshot(self, src: Path, mode: str = "append"): ...
```
Backends implement this (pgvector, FAISS). Export *must* be deterministic and sorted for reproducibility.

---
## 3. Data Model & Files
Snapshot directory structure (tar/zip for transport):
```
/knowledge_snapshot_YYYYMMDD_HHMMSS/
  manifest.json            # High-level inventory
  embeddings.parquet       # All vectors (if FAISS: index.faiss + metadata.parquet)
  index.faiss              # (FAISS only)
  metadata.parquet         # (Optional separated metadata)
  bpmn/
    <process_id>_v<version>.bpmn
  prompts/
    <name>_v<version>.yaml
  patterns/
    pattern_catalog_v<version>.yaml
  examples/
    examples_v<version>.jsonl
  domains/
    domain_profiles.jsonl
  logs/
    generation_events.jsonl (optional truncated)
  checksums.sha256
```
`manifest.json` core fields:
```
{
  "snapshot_id": "20250812T153000Z",
  "vector_backend": "pgvector|faiss",
  "record_count": 12345,
  "dimensions": 1536,
  "bpmn_count": 42,
  "prompt_count": 18,
  "source_env": "dev-lab",
  "schema_version": 1,
  "created_utc": "2025-08-12T15:30:00Z",
  "hash_algorithm": "sha256"
}
```

---
## 4. Backend-Specific Strategies
### 4.1 pgvector
- Primary store inside Postgres. Use transactional consistency.
- Snapshot options:
  1. Logical dump: `pg_dump --schema=public --table=embeddings ...` plus artifact files.
  2. COPY to CSV/Parquet for embeddings + metadata (preferred: Parquet for columnar efficiency).
- Migration: Restore DB (pg_restore) or ingest Parquet via COPY; rebuild indexes.
- Replication (optional): Set up logical replication slot during transition for near-zero downtime.

### 4.2 FAISS
- In-memory index + metadata table (e.g., SQLite or Parquet).
- Export: Persist index via `write_index()`, write metadata parquet, produce deterministic ordering.
- Import: Load index; reconcile ID collisions by version precedence or GUID preservation.

---
## 5. Consistency & Cutover Phases
1. Prepare: Ensure version of schemas; run health check.
2. Quiesce (optional for minimal downtime): Temporarily pause writes (PEO triggers a `pause_ingestion` flag) OR leverage MVCC snapshot (pgvector) / clone index (FAISS copy-on-write).
3. Snapshot Export BPMN process (`export_snapshot.bpmn`).
4. Transfer (scp / S3 multipart upload / object storage).
5. Integrity Verification: Recompute sha256 for all files; compare to `checksums.sha256`.
6. Import via `import_snapshot.bpmn` on target environment.
7. Validation Tests:
   - Random sample queries produce identical top-k IDs & rank (tolerance for floating rounding).
   - Embedding dimension equality.
   - BPMN XML checksum match.
8. Cutover: Point DAS to new vector backend; unpause ingestion.
9. Decommission: Archive old environment snapshot (immutable storage e.g., S3 Glacier).

---
## 6. BPMN Support Processes
Create these minimal processes:
- `export_snapshot.bpmn`: start → freeze flag set → dump embeddings → package artifacts → compute checksums → clear freeze flag → emit event.
- `import_snapshot.bpmn`: start → validate package → verify checksums → load vectors → register artifacts → rebuild search structures → emit readiness event.
- `validate_snapshot.bpmn`: sample retrievals → quality threshold decision → pass/fail.

External script tasks reference versioned scripts:
```
<bpmn:scriptTask id="dump_vectors" name="Dump Vectors" scriptFormat="python">
  <bpmn:script src="https://raw.githubusercontent.com/organization/procos-scripts/v1/dump_vectors.py"/>
</bpmn:scriptTask>
```

---
## 7. Versioning & Deltas
- Full snapshot cadence: daily (low volume) or weekly (higher volume).
- Delta snapshot: JSONL append file containing only changed embeddings `{id, op, version, vector_hash}`.
- Reconstruct target by applying last full snapshot + ordered deltas.
- Maintain `snapshot_catalog.jsonl` with lineage.

---
## 8. Integrity & Security
- Checksums: `sha256sum **/* > checksums.sha256` (exclude file itself first pass).
- Sign snapshot: Optional GPG signature detached.
- Encryption at rest: If using S3, enable SSE (KMS). Local: envelope encrypt sensitive components.
- Access control: Snapshot export BPMN requires approval lane (manual in prod, auto in dev).

---
## 9. Schema Evolution
Maintain `SCHEMA_VERSION` constant. If incremented:
- Provide migration script `migrate_snapshot_vX_to_vY.py`.
- BPMN import process detects mismatch → runs migration before load.

---
## 10. Disaster Recovery
RPO / RTO guidelines:
- RPO target: <= 24h (align with full + delta cadence) or tighter with streaming replication (pgvector).
- RTO target: < 1h (import + validation processes automated).
- DR drill: Quarterly run `simulate_restore.bpmn` on staging; store report.

---
## 11. Testing Migration
Automated test sequence:
1. Generate synthetic embeddings (N=500) + artifacts.
2. Export snapshot.
3. Delete local store (simulate loss).
4. Import snapshot.
5. Assert all IDs present; random 20 queries produce same top-5 set (allow reorder if scores identical).
6. Run TDE retrieval task end-to-end (BPMN scenario).

---
## 12. Streamlit UI Hooks
Add Migration Panel:
- Export Snapshot (button) → triggers `export_snapshot` process; poll status.
- Upload & Import (file uploader) → posts to import endpoint; triggers `import_snapshot` BPMN.
- Verification Dashboard: shows last snapshot id, record counts, hash status, drift detection.

---
## 13. Drift Detection
Job (BPMN or scheduled script):
- Random sample embeddings IDs.
- Hash current serialized vector bytes.
- Compare to last snapshot manifest; mismatches → raise `vector_drift_detected` event.

---
## 14. Performance Notes
- Export as columnar (Parquet) to minimize bandwidth.
- For pgvector large sets: use cursor-based streaming, chunk commit size.
- Compress index files with ZSTD (level 6) for FAISS; tradeoff speed/size.

---
## 15. Open Decisions
| Topic | Options | Decision Owner | Due |
|-------|---------|----------------|-----|
| Default backend | pgvector / FAISS / hybrid |  |  |
| Snapshot cadence | daily / weekly / mixed |  |  |
| Delta format | JSONL vs Parquet |  |  |
| Encryption | KMS-managed vs app-level |  |  |

---
## 16. TODO Extraction (Add to Master TODO)
- Implement VectorRepository export/import.
- Add BPMN: export_snapshot, import_snapshot, validate_snapshot.
- Add Streamlit migration panel.
- Create snapshot manifest & checksum generator.
- Add integrity + drift detection tasks.

---
## 17. Quick Lift & Shift Playbook
1. Run export_snapshot (ensure success event).
2. Transfer bundle to target (S3 upload).
3. Provision target infra (IaC) & deploy services.
4. Run import_snapshot.
5. Run validate_snapshot.
6. Point DAS `VECTOR_ENDPOINT` env to new backend.
7. Monitor first 15m queries for anomalies.
8. Decommission old environment after retention window.

---
## 18. Summary
By enforcing a clean repository abstraction, deterministic snapshotting, BPMN-managed export/import, and integrity validation, ProcOS can migrate environments with minimal downtime and zero knowledge loss, keeping evolution continuous and auditable.
