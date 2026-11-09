---
name: data-engineering
description: "Design reliable data pipelines: ingestion, ELT/dbt, orchestration, modeling, data quality, idempotency, lineage, cost. Use when building or reviewing ETL/ELT, analytics tables, streaming or batch jobs."
license: MIT
metadata:
  version: "1.0.0"
---

# Data engineering

Relational specifics: `postgres`. Observability of jobs: `observability`. Application-side schemas: `spring-data-jpa`.

## Architecture
- Prefer **ELT**: land raw data unchanged (immutable, partitioned by ingestion date), transform in the warehouse/lakehouse with SQL (dbt/SQLMesh). Layers: `raw/bronze` -> `staging/silver` (typed, deduped, renamed) -> `marts/gold` (business-ready, tested, documented).
- Batch by default; streaming (Kafka/Kinesis/Flink/Spark Structured Streaming) only when latency requirements (minutes or less) justify the operational cost. Define freshness SLAs per dataset.
- Storage formats: Parquet/Iceberg/Delta for lakes (columnar, schema evolution, time travel); partition by low-cardinality date columns; avoid tiny files (compaction).

## Pipeline properties (all required)
- **Idempotent**: re-running a window yields the same result (MERGE/upsert by business key, overwrite partitions, deterministic IDs). No append-only without dedupe.
- **Incremental**: process by watermark/CDC (Debezium) not full reload; support **backfill** for a date range with the same code.
- **Replayable**: keep raw inputs; transformations are pure functions of inputs + code version.
- **Observable**: run metadata (rows in/out, duration, freshness), alerts on failure and on late data; retries with backoff; dead-letter for bad records.
- Small, composable tasks in the orchestrator (Airflow/Dagster/Prefect); dependencies explicit; no business logic inside DAG definitions; secrets from a manager.

## Modeling
Dimensional modeling (facts at a declared grain + conformed dimensions) for analytics; surrogate keys; slowly changing dimensions type 2 where history matters; one definition per metric in a semantic/metrics layer; naming conventions (`dim_`, `fct_`, snake_case, `_at` timestamps UTC, `_id` keys).

## Data quality (tests are part of the pipeline)
Not-null, unique, accepted values, referential integrity, volume/freshness anomalies, distribution drift (dbt tests, Great Expectations, Soda). Fail the run or quarantine on critical breaks; publish a data-quality status per dataset. Contracts with producers (schema + semantics + SLA), versioned; breaking changes announced.

## Governance & security
PII classified and tagged; minimize, mask/tokenize, column- and row-level access policies; retention and deletion (GDPR/Loi 25 style requests must propagate to derived tables); audit access; lineage via OpenLineage/dbt docs; encrypt at rest and in transit; least-privilege service accounts.

## Performance & cost
Prune partitions, filter early, avoid `SELECT *` and cross joins, pre-aggregate heavy marts, choose clustering/sort keys by query patterns, right-size compute and auto-suspend, monitor cost per pipeline and per query, expire stale intermediates.

## Review checklist
Grain stated - idempotent and backfillable - tests on keys and freshness - raw preserved - PII handled - SLA and alerts defined - documented owners - cost estimated.
