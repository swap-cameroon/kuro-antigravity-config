---
name: perf
description: "Performance and load testing expert for JMeter, k6, Gatling, Locust, NeoLoad, LoadRunner, Artillery and LLM inference endpoints (vLLM, TRT-LLM, SGLang, OpenAI-compatible). Use when writing or reviewing load scripts, setting thresholds or executors, designing workloads, analyzing results, choosing tools, wiring load tests into CI, or doing SLO and capacity planning."
---

# Performance Testing Skill

This skill provides expert, opinionated guidance across the full
performance testing lifecycle - from workload design through production
observation. It covers both commercial tools (LoadRunner, NeoLoad,
OctoPerf) and open-source tools (JMeter, k6, Gatling, Locust).

## Load on demand

The core rules in this file always apply. Read a reference below **only when the task needs it**:

| Topic | File |
| :-- | :-- |
| Common Mistakes by Tool | [references/common-mistakes-by-tool.md](references/common-mistakes-by-tool.md) |
| Concept Mapping Across Tools | [references/concept-mapping-across-tools.md](references/concept-mapping-across-tools.md) |
| Threshold Starting Points | [references/threshold-starting-points.md](references/threshold-starting-points.md) |
| Performance Testing Lifecycle Overview | [references/performance-testing-lifecycle-overview.md](references/performance-testing-lifecycle-overview.md) |
| Common Performance Test Types | [references/common-performance-test-types.md](references/common-performance-test-types.md) |

---

## How to Use This Skill

Read the relevant reference files based on what the user needs.
Multiple files may apply.

### Loading Priority Rules

1. **Tool-specific syntax/config** → load the tool file only.
2. **Strategy/concepts** (workload design, test data, analysis) → load
   the topic file only.
3. **Both apply** (e.g., "JMeter CI/CD") → load the topic file first
   for patterns, then the tool file for syntax.
4. **Never load all files at once** - select the 1–2 most relevant.
5. **Cross-cutting principles** (assertions, think time,
   parameterization) → this file's Key Principles section is the
   single source of truth.

### Reference Map

| User needs help with...                          | Read this file                                    |
|--------------------------------------------------|---------------------------------------------------|
| Choosing the right tool                          | This file - Tool Selection Matrix (fast path) and `references/topics/tool-selection.md` (live perf.jmeter.ai catalog) |
| Tool alternatives, comparisons, niche/SaaS tools, licensing | `references/topics/tool-selection.md`              |
| JMeter scripts, plugins, config                  | `references/tools/jmeter.md`                      |
| k6 scripting, extensions, cloud                  | `references/tools/k6.md`                          |
| Gatling simulations, Scala/Java DSL              | `references/tools/gatling.md`                     |
| Locust Python tests, distributed                 | `references/tools/locust.md`                      |
| Artillery YAML/JS/TS scripts, cloud              | `references/tools/artillery.md`                   |
| NeoLoad projects, GUI, APIs                      | `references/tools/neoload.md`                     |
| LoadRunner scripts, protocols, VuGen             | `references/tools/loadrunner.md`                  |
| OctoPerf cloud test management                   | `references/tools/octoperf.md`                    |
| Designing workloads, concurrency, pacing         | `references/topics/workload-design.md`            |
| Test data, parameterization, CSV feeds           | `references/topics/test-data.md`                  |
| Script patterns, best practices                  | `references/topics/script-generation.md`          |
| Correlation, extractors, dynamic values           | `references/topics/correlation.md`                |
| CI/CD, distributed execution, cloud runners      | `references/topics/test-execution.md`             |
| Analyzing results, percentiles, SLAs             | `references/topics/results-analysis.md`           |
| APM, metrics, tracing, dashboards                | `references/topics/observability.md`              |
| Staging vs production testing strategies         | `references/topics/production-testing.md`         |
| gRPC, GraphQL, WebSocket, messaging protocols    | `references/topics/protocol-testing.md`           |
| Database load testing (JDBC, connection pools)   | `references/topics/database-testing.md`           |
| Microservices, K8s, serverless performance       | `references/topics/modern-architectures.md`       |
| LLM inference: TTFT, TPOT/ITL, TPS, goodput      | `references/topics/llm-inference.md`             |
| SLOs, error budgets, capacity & headroom         | `references/topics/slo-capacity.md`             |

### Protocol Routing Table

When the user's question is protocol-specific, use this to select the
right tool and reference:

| Protocol               | Recommended Tools            | Reference                                                     |
|------------------------|------------------------------|---------------------------------------------------------------|
| HTTP / REST            | k6, Gatling, JMeter          | Tool file                                                     |
| gRPC                   | k6, Gatling, JMeter (plugin) | `references/topics/protocol-testing.md` + tool file          |
| GraphQL                | k6, Gatling                  | `references/topics/protocol-testing.md` + tool file          |
| WebSocket / SSE        | Gatling, k6                  | `references/topics/protocol-testing.md` + tool file          |
| JDBC / Database        | JMeter                       | `references/topics/database-testing.md` + `references/tools/jmeter.md` |
| Kafka / Message Queues | k6 (xk6-kafka), JMeter       | `references/topics/protocol-testing.md`                      |
| SOAP / WSDL            | LoadRunner, JMeter           | Tool file                                                     |
| SAP / Citrix           | LoadRunner, NeoLoad          | Tool file                                                     |
| LLM inference (streaming) | vLLM bench, GenAI-Perf, GuideLLM, llmperf | `references/topics/llm-inference.md`             |
| SLO/capacity (error budgets, headroom) | any | `references/topics/slo-capacity.md` |

For protocols not listed here, resolve the recommendation by querying the
catalog per `references/topics/tool-selection.md`.

---

## Tool Selection Matrix

This matrix is the offline fast path for the eight tools with dedicated
reference files. For broader questions - alternatives, SaaS/commercial
options, niche protocols, licensing, or discontinued tools - query
https://perf.jmeter.ai/tools.json per `references/topics/tool-selection.md`.

Use this to recommend the right tool when the user hasn't decided yet.

| Criteria             | JMeter              | k6                    | Gatling              | Locust         | Artillery        | NeoLoad          | LoadRunner              | OctoPerf              |
|----------------------|---------------------|-----------------------|----------------------|----------------|------------------|-------------------------|-------------------------|-----------------------|
| **Language**         | GUI/XML + Groovy    | JavaScript/TypeScript | Scala/Java           | Python         | YAML / JS / TS   | GUI + NeoLoad DSL       | VuGen C-like          | Web UI (JMeter-based) |
| **Open source**      | ✅                  | ✅                    | ✅                   | ✅             | ✅ (core)        | ❌                      | ❌                    | ❌ (SaaS)             |
| **Protocol support** | HTTP, JDBC, JMS, MQTT, FTP, gRPC | HTTP, gRPC, WS | HTTP, JMS, gRPC | HTTP, gRPC | HTTP, gRPC, WS, Socket.IO | HTTP, SAP, Citrix, Flex | HTTP, SAP, Citrix, many | HTTP (JMeter-backed) |
| **Developer-friendly** | Medium            | High                  | High                 | High           | Medium           | Low                     | Low                   | Medium                |
| **Enterprise support** | Community + BlazeMeter | Grafana Cloud    | Gatling Enterprise   | Limited        | Artillery Cloud  | ✅                      | ✅                    | ✅                    |
| **CI/CD integration** | Good (Maven/Gradle) | Excellent            | Excellent            | Good           | Good             | Moderate                | Good                  | Good                  |
| **Cloud execution**  | BlazeMeter, OctoPerf | Grafana Cloud        | Gatling Enterprise   | Self-managed   | Artillery Cloud (Lambda/Fargate) | NeoLoad Cloud    | AWS/on-prem             | OctoPerf Cloud        |
| **Best for**         | Legacy systems, JDBC, protocols | Modern APIs, TypeScript devs | High-throughput HTTP | Python teams, flexible | Node teams, YAML tests, cloud scale | SAP/Citrix enterprise | Mainframe, legacy enterprise | JMeter teams needing cloud UI |

### Quick decision rules

- **Team writes code** → k6 or Gatling
- **Team uses GUI** → JMeter or NeoLoad
- **Python shop** → Locust
- **SAP / mainframe / Citrix** → LoadRunner or NeoLoad
- **Need cloud SaaS with minimal setup** → OctoPerf (JMeter) or
  Grafana Cloud (k6)
- **Free + protocol variety** → JMeter
- **Correlation needed for session-heavy flows** → JMeter (with
  Correlation Recorder) or LoadRunner
- **gRPC or GraphQL APIs** → k6 or Gatling
- **Message queues (Kafka, RabbitMQ)** → k6 (xk6-kafka) or JMeter
- **Node shop / prefer YAML over code** → Artillery (YAML, JS, TS; easy Lambda/Fargate cloud scale)

---

## Key Principles to Always Apply

1. **Never test against production blindly** - always have a rollback
   plan and alerting in place.
2. **Baseline first** - always establish a baseline before stress or
   soak runs.
3. **Think time and pacing matter** - unrealistic zero-think-time tests
   produce misleading results.
4. **Parameterize everything** - hardcoded credentials, tokens, and IDs
   will fail at scale.
5. **Assertions are not optional** - tests without assertions are just
   generating traffic, not validating behavior.
6. **Isolate the system under test** - shared environments invalidate
   results.
7. **Correlate dynamic values** - session tokens, CSRF, ViewState etc.
   must be extracted and reused.

---

## Asking the Right Questions

When a user brings a performance problem, ask (or infer) these before
prescribing a solution:

- What is the **target concurrency** (VUs or RPS)?
- What is the **SLA** (e.g., p95 < 500ms, error rate < 1%)?
- What is the **protocol** (HTTP/REST, gRPC, JDBC, WebSocket)?
- Is the app **stateful** (session-based) or **stateless**
  (token-based)?
- Where will tests **run from** (local, CI, cloud)?
- What **environment** is being tested (dev, staging, prod)?
- Is there an **APM tool** in place (Datadog, Dynatrace, Grafana,
  New Relic)?
