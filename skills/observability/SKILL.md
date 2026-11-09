---
name: observability
description: "Instrument services with structured logs, metrics, traces (OpenTelemetry), SLO-based alerts and dashboards. Use when adding monitoring, debugging production, designing alerts, or making a service operable."
license: MIT
metadata:
  version: "1.0.0"
---

# Observability

Goal: answer "is it broken, for whom, and why?" without shipping new code. SLO/error-budget policy lives in `sre-engineer`; this skill is the instrumentation.

## Logs
- Structured JSON, one event per line: `timestamp` (UTC ISO 8601), `level`, `service`, `version`, `env`, `message`, `trace_id`, `span_id`, plus business keys (`order_id`). Same field names across services.
- Levels: ERROR = needs action; WARN = degraded but handled; INFO = business milestones; DEBUG off in prod by default (dynamic toggle).
- **Never log** secrets, tokens, full card/PII; mask or hash. Log decisions and outcomes, not every loop iteration. Sample high-volume info logs.
- Propagate a correlation/trace ID from the edge through every call, queue message and job.

## Metrics
- RED for services (Rate, Errors, Duration), USE for resources (Utilization, Saturation, Errors), plus queue depth/lag, pool usage, GC, cache hit ratio.
- Histograms for latency (buckets around SLO thresholds); report p50/p95/p99, not averages. Counters for events, gauges for levels.
- **Cardinality discipline**: labels are bounded sets (route template, status class, region). Never user IDs, emails, raw URLs, error text as labels.
- Naming: `service_subsystem_name_unit` (`http_server_request_duration_seconds`).

## Traces (OpenTelemetry)
Use OTel SDK + auto-instrumentation, OTLP to a collector. Name spans by operation (`GET /orders/{id}`, `db.query orders`), add attributes (not PII), record exceptions, propagate W3C `traceparent` over HTTP and message headers. Head-sample (e.g. 5-10%) with tail-sampling to keep errors and slow traces.

## Alerts
- Alert on **symptoms tied to SLOs** (burn-rate over multiple windows, e.g. 2% budget in 1 h / 5% in 6 h), not on causes like CPU>80%.
- Every page has: severity, impact, dashboard link, runbook link, owner. If it is not actionable, delete or downgrade it. Review noisy alerts weekly.
- Add synthetic probes for critical journeys and dependency health.

## Dashboards
One service overview per service: traffic, errors, latency, saturation, dependencies, deploy markers, SLO status. Put the golden signals on top; drill-down below. Dashboards as code (Grafana JSON/Terraform) in the repo.

## Verify
Trigger a failure in staging and confirm: alert fires, trace shows the failing span, logs correlate by `trace_id`, runbook is sufficient. A signal never exercised is untrusted.
