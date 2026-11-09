## Performance Testing Lifecycle Overview

Always think through these phases when helping a user - they often ask
about one phase but need context from others.

```
1. PLAN
   └─ Workload design → concurrency model → SLA targets → test type
       → references/topics/workload-design.md

2. DATA
   └─ Identify variables → parameterization strategy → data generation
       → references/topics/test-data.md

3. SCRIPT
   └─ Record or code → correlation → parameterization → assertions
       → references/topics/script-generation.md + tool-specific file

4. EXECUTE
   └─ Local → distributed → CI/CD → cloud burst → monitoring hooks
       → references/topics/test-execution.md

5. OBSERVE
   └─ APM → metrics → logs → traces → dashboards
       → references/topics/observability.md

6. ANALYZE
   └─ Throughput, latency percentiles, errors → bottleneck ID → report
       → references/topics/results-analysis.md

7. PRODUCTION
   └─ Canary testing → shadow load → chaos → synthetic monitoring
       → references/topics/production-testing.md
```
