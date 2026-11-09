## Common Performance Test Types

| Test Type        | Goal                                  | Key Metric                              |
|------------------|---------------------------------------|-----------------------------------------|
| **Load**         | Validate system at expected load      | Response time, throughput, error rate   |
| **Stress**       | Find the breaking point               | Max VUs before degradation, error onset |
| **Soak/Endurance** | Detect memory leaks, slow degradation | Resource trend over time (hours)      |
| **Spike**        | Behavior under sudden traffic burst   | Recovery time, error spike              |
| **Capacity**     | Find max sustainable load             | Throughput ceiling at SLA thresholds    |
| **Smoke**        | Quick sanity check                    | Single VU - no errors                   |
| **Breakpoint**   | Incremental ramp until failure        | Failure threshold VU count              |
