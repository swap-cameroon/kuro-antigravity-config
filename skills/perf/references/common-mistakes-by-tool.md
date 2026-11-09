## Common Mistakes by Tool

These are the mistakes that cause silent CI failures, misleading
results, or test collapse at scale. Flag them proactively whenever
reviewing scripts or diagnosing problems - users often don't know to
ask about them.

### k6

- **`check()` without `thresholds`** - checks log pass/fail but do
  NOT fail the test run. Without thresholds, CI always reports green
  regardless of latency. Always add `thresholds` to `options`.
- **Data loaded inside `default()`** - loading CSV or JSON inside the
  VU function runs on every iteration, causing massive per-iteration
  overhead and OOM at scale. Always use `SharedArray` in the init
  scope.
- **`shared-iterations` for user journeys** - VUs race to claim
  iterations and may skip steps, producing incomplete journey metrics.
  Use `per-vu-iterations` for any multi-step flow.
- **No `sleep()` between steps** - 100 VUs with zero think time
  generates the absolute maximum RPS for that iteration time, far
  exceeding what 100 real concurrent users produce. Always add
  realistic think time.
- **`console.log` in `default()`** - causes 30–50% throughput drop
  under load. Use custom metrics (`Counter`, `Trend`) instead.
- **Hardcoded `BASE_URL`** - use `__ENV.BASE_URL` for environment
  portability.

### JMeter

- **Listeners enabled in non-GUI runs** - View Results Tree, Aggregate
  Report etc. buffer all samples in memory during headless runs,
  causing memory leak and eventual crash. Disable all listeners before
  CI execution; use `-l results.jtl` for output.
- **Missing correlation on session-heavy apps** - JSESSIONID, CSRF
  tokens, ViewState, OAuth codes must be extracted and reused. Without
  correlation, the test fails for every user after the first.
- **Hardcoded thread counts** - parameterize via JMeter properties
  (`${__P(threads,10)}`) so CI can override without editing the JMX.
- **Zero think time** - never reflects real user behavior; always add
  at minimum a Constant Timer (300–500ms) between samplers.
- **Throughput Controller % mode misuse** - percentage applies per
  iteration of the parent controller, not globally. Most users expect
  global percentage; use `Total Executions` mode instead or be
  explicit.

### Gatling

- **Blocking calls inside `exec()`** - any blocking I/O inside an exec
  block stalls the entire Akka actor, killing simulation concurrency.
  Use Gatling's async feed/session API exclusively.
- **Missing `.check()` on responses** - without checks, 4xx and 5xx
  responses are silently counted as successful. Always add at minimum
  `.check(status.is(200))`.
- **Fixed `pause()` values** - use `uniformPaused(min, max)` or
  `normalPausedWithPercentageDuration` for realistic think time
  distribution.

### Locust

- **`self.client` without `catch_response=True`** - by default, Locust
  marks any HTTP response as success regardless of status code. Use
  `with self.client.get(..., catch_response=True) as r:` and call
  `r.failure()` explicitly.
- **Unequal task weights without intent** - tasks default to equal
  weight; if your user journey has unequal step frequency, set weights
  explicitly or the journey ratio will be wrong.
- **Master + workers on same machine** - causes resource contention
  that skews both throughput and latency measurements. Always run
  workers on separate machines or containers for distributed tests.

### Artillery

- **No `ensure` block** - without `ensure`, Artillery reports metrics
  but always exits 0, so CI never fails on latency or error spikes.
  Always add `ensure.thresholds` (or `conditions`) for SLA gates.
- **`arrivalRate` mistaken for concurrency** - it is new users per
  second (open model). On a slow backend, pending VUs pile up unbounded.
  Set `maxVusers` to cap real concurrency, or use `arrivalCount`.
- **Strict captures aborting VUs** - captures are strict by default;
  a missed extractor stops the whole VU. Only set `strict: false`
  when a downstream 404 is acceptable.
- **`payload.order: sequence` in distributed runs** - sequential CSV
  consumption breaks under Lambda/Fargate workers (each has its own
  copy). Use the default `random` ordering for distributed tests.
- **Zero `think` time** - 1 VU/sec with no think time fires the
  maximum RPS for the journey; add `think` to model real pacing.
- **Forgetting `http.response_time` is TTFB** - latency metrics are
  time-to-first-byte by default. Enable `config.http.extendedMetrics`
  for full download timing (`http.total.*`) when that matters.
