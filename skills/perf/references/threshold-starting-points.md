## Threshold Starting Points

These are community baselines - always tell the user to adjust these
to their actual SLA requirements. Never present them as universal
targets.

| Endpoint type    | p95       | p99        | Error rate | Notes                              |
|------------------|-----------|------------|------------|------------------------------------|
| Web page (HTML)  | < 3000ms  | < 5000ms   | < 1%       | Aligns with Google CWV LCP < 2.5s  |
| REST API         | < 500ms   | < 1000ms   | < 1%       | Common industry baseline           |
| Auth / Login     | < 300ms   | < 500ms    | < 0.1%     | Stricter - security-sensitive path |
| Search / Query   | < 800ms   | < 1500ms   | < 0.5%     | Varies heavily by dataset size     |
| Write (POST/PUT) | < 800ms   | < 1500ms   | < 0.5%     | Includes DB write latency          |
| Checkout/Payment | < 1000ms  | < 2000ms   | < 0.1%     | Stricter - revenue-critical path   |
| Background/async | < 5000ms  | < 10000ms  | < 2%       | Batch jobs, async processors       |

**k6 specific:** Always define both `http_req_duration` AND
`http_req_waiting` as separate thresholds. `http_req_waiting`
(TTFB) isolates server-side latency from network overhead - it is
the first metric to check when diagnosing high p95. Always include
`checks: ['rate>0.99']`.

**JMeter specific:** Add both a Response Assertion and a Duration
Assertion per sampler. Never rely on listener output alone for
CI pass/fail; use the JMeter exit code driven by assertions.
