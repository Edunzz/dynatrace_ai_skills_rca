## 9. Appendices
### 9.1 Anchor, time windows and evidence
**Anchor:** Problem P-2601001, chosen on 2026-01-16 as a simple, recent case from the example tenant.
| Window | From (UTC) | To (UTC) | Reason |
|---|---|---|---|
| Initial | 2026-01-16 03:45 | 2026-01-16 04:45 | Derived from the anchor (problem 04:14–04:21 with a margin before it) |
| Extension 1 | 2026-01-15 04:45 | 2026-01-16 04:45 | Look for previous changes (24 h of events) |
| Extension 2 | 2026-01-14 04:45 | 2026-01-16 04:45 | Memory trend and restarts of every copy (48 h) |
| Extension 3 | 2026-01-09 04:45 | 2026-01-16 04:45 | Problem recurrence (7 days) |

| Evidence | .dql file | Records | Warnings / adjusted limits | Supports |
|---|---|---|---|---|
| 2.1 | E2.1-service-errors.dql | 1 series | None | Impact: 9 failures out of 4,863, peak 9.43% |
| 2.2 | E2.2-impact-by-pod.dql | 2 | Counts extrapolated from trace sampling | Failures only on pod …-a (copy 1) |
| 3.1 | E3.1-davis-events.dql | 4 | None | Times of the failures, the long GC and the restart |
| 3.2 | E3.2-davis-problems.dql | 2 | None | Opening and closing of both problems |
| 3.3 | E3.3-change-events-24h.dql | 4 | None | No change or Kubernetes events (G1) |
| 5.1 | E5.1-failures-by-pod-minute.dql | 2 series | None | Failures by pod and minute |
| 5.2 | E5.2-failure-details.dql | 6 | Sampled traces: 6 records represent 9 failures | HTTP 500 and waits of up to 81 s |
| 5.3 | E5.3-net-process-gc.dql | 2 series | None | GC at 99% on copy 1 and 0% on copy 2 |
| 5.4 | E5.4-container-memory.dql | 2 series | None | Memory at 91% (copy 1) and 71% (copy 2) of the limit |
| 5.5 | E5.5-container-restarts.dql | 5 series | None | 18 restarts in 48 h |
| 5.6 | E5.6-recurrence-7d.dql | 2 | None | 2 failure problems and 2 GC problems in 7 days |
| 5.7 | E5.7-memory-trend-48h.dql | 5 series | None | Growth of 75–90 MB/h in every copy |
All evidence was collected with dtctl 0.37.0 on the my-tenant context; the evidence sections can be re-run and carry the fixed time window inside the query.
### 9.2 Glossary
| Term | Definition |
|---|---|
| GC (garbage collection) | The .NET process that frees memory no longer in use; while it runs, it pauses the application |
| Pod / container | A copy of the service running on Kubernetes with its own memory limit |
| Working set | Memory the container is actually using |
| Davis | Dynatrace's AI engine that detects anomalies and opens problems |
| MTTD | Mean time to detect |
| MTTA | Mean time to acknowledge |
| MTTR | Mean time to resolve |
### 9.3 Official references
| ID | Official source | URL | Accessed | Supports |
|---|---|---|---|---|
| R1 | Dynatrace Docs — Root cause analysis concepts | https://docs.dynatrace.com/docs/dynatrace-intelligence/root-cause-analysis/concepts | 2026-01-16 | Davis groups events that share a root cause into one problem |
| R2 | Microsoft Learn — Garbage collector config settings (.NET) | https://learn.microsoft.com/en-us/dotnet/core/runtime-config/garbage-collector | 2026-01-16 | In containers the limit is treated as physical memory; above 90% GC runs more aggressive full collections; heap limit 75% |
| R3 | Microsoft Learn — Fundamentals of garbage collection | https://learn.microsoft.com/en-us/dotnet/standard/garbage-collection/fundamentals | 2026-01-16 | Managed threads are suspended during a collection |
| R4 | Kubernetes Docs — Configure Liveness, Readiness and Startup Probes | https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/ | 2026-01-16 | If the liveness probe fails, the kubelet kills and restarts the container |
**Other references:** Problem [P-2601001](/ui/apps/dynatrace.davis.problems/problem/1000000000000000001_1768536540000V2) · Problem [P-2601002](/ui/apps/dynatrace.davis.problems/problem/1000000000000000002_1768536720000V2) · draw.io sources: D1-propagation.drawio, D2-timeline.drawio, D3-root-cause.drawio (the embedded PNG contains the editable XML).
### 9.4 Version history
| Version | Date | Author | Change |
|---|---|---|---|
| 1.0 | 2026-01-16 | Example author (AI-assisted) | Initial version — example of the dt-custom-rca-jromero skill (dtctl 0.37.0) |
