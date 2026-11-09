## Concept Mapping Across Tools

Use this when users are migrating between tools or asking how a
concept from one tool maps to another. Claude should always provide
the specific mapping rather than a generic explanation.

| Concept          | JMeter                  | k6                      | Gatling                  | Locust                   | Artillery                | LoadRunner          |
|------------------|-------------------------|-------------------------|--------------------------|--------------------------|--------------------------|---------------------|
| Virtual user     | Thread                  | VU                      | User                     | User                     | VU (arrival per sec)     | Vuser               |
| Test plan        | .jmx file               | .js / .ts script        | Simulation class         | .py file                 | .yml / .js / .ts script  | VuGen script (.usr) |
| User entrypoint  | Thread Group            | `default()` function    | `scenario()`             | task methods             | `flow` in scenario       | `Action()`          |
| Concurrency ctrl | Thread Group settings   | executor                | `inject()`               | `spawn_rate`             | `maxVusers` / `arrivalRate` | Vuser Group         |
| Think time       | Constant/Uniform Timer  | `sleep()`               | `pause()`                | `time.sleep()`           | `think`                  | `lr_think_time()`   |
| Inline assertion | Response Assertion      | `check()`               | `.check()`               | `catch_response`         | `afterResponse` hooks    | `lr_eval_string()`  |
| SLA enforcement  | Duration Assertion      | `thresholds`            | Assertions (Enterprise)  | custom + exit code       | `ensure` plugin          | SLA definition      |
| Correlation      | Regex / CSS Extractor   | `res.json()` / regex    | `.check()` + `saveAs()`  | `response.text` + regex  | `capture` (json/xpath/regexp/header) | `web_reg_save_param`|
| Data feed        | CSV Data Set Config     | `SharedArray`           | `feeder`                 | CSV reader               | `payload` / `variables`  | `lr_paramarr()`     |
| Grouping         | Transaction Controller  | `group()`               | `group()`                | task sets                | `name` on scenario       | Transaction         |
| Distributed      | Controller + Agents     | k6 cloud / k6 operator  | Gatling Enterprise       | master + workers         | Lambda / Fargate workers | Load Generator      |
| Results output   | .jtl (CSV/XML)          | JSON / InfluxDB / cloud | simulation.log           | CSV / Locust web UI      | JSON / HTML report       | .lrr file           |
