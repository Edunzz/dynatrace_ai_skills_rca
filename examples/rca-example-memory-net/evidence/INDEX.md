# Evidence index — RCA P-2601001 (example)

> In a real RCA this folder also stores the `E<N.x>.json` result of every query. They are left out of this example because they contain tenant data.

dtctl context: `my-tenant` (https://abc12345.apps.dynatrace.com) · dtctl 0.37.0 · Run on: 2026-01-16.
Every query carries its absolute time window inside the `.dql` file; they were validated with `dtctl verify query` and run with `dtctl query -f <file> -o json`.

| ID | File | Window (UTC) | Records | Warnings | Supports |
|---|---|---|---|---|---|
| E2.1 | queries/E2.1-service-errors.dql | 2026-01-16 03:45 → 04:45 | 1 series | None | 9 failures out of 4,863 requests; peak 9.43% at 04:13 |
| E2.2 | queries/E2.2-impact-by-pod.dql | 2026-01-16 03:45 → 04:45 | 2 | Extrapolated counts (trace sampling) | pod-a 9 of 2,298 failed; pod-b 0 of 2,600 |
| E3.1 | queries/E3.1-davis-events.dql | 2026-01-16 03:45 → 04:45 | 4 | None | Failures 04:09–04:21; long GC 04:12–04:18; restart 04:14:51 |
| E3.2 | queries/E3.2-davis-problems.dql | 2026-01-16 03:45 → 04:45 | 2 | None | P-2601001 04:14–04:21; P-2601002 04:15–04:18 |
| E3.3 | queries/E3.3-change-events-24h.dql | 2026-01-15 04:45 → 2026-01-16 04:45 | 4 | None | 0 change or Kubernetes events in 24 h |
| E5.1 | queries/E5.1-failures-by-pod-minute.dql | 2026-01-16 03:45 → 04:45 | 2 series | None | Failures only on copy 1 (04:08 and 04:12–04:14) |
| E5.2 | queries/E5.2-failure-details.dql | 2026-01-16 03:45 → 04:45 | 6 | 6 sampled traces represent 9 failures | HTTP 500; durations from 2.6 s to 81 s |
| E5.3 | queries/E5.3-net-process-gc.dql | 2026-01-16 03:45 → 04:45 | 2 series | None | GC on pod-a 5% → 99% (04:14), 0% after the restart; pod-b 0% |
| E5.4 | queries/E5.4-container-memory.dql | 2026-01-16 03:45 → 04:45 | 2 series | None | pod-a 936 MB (91.4% of 1 GiB); pod-b 728 MB (71.1%) |
| E5.5 | queries/E5.5-container-restarts.dql | 2026-01-14 04:45 → 2026-01-16 04:45 | 5 series | None | 18 restarts in 48 h (pod-c 8, pod-b 5, pod-d 2, pod-a 2, pod-e 1) |
| E5.6 | queries/E5.6-recurrence-7d.dql | 2026-01-09 04:45 → 2026-01-16 04:45 | 2 | None | 2 failure problems and 2 GC problems in 7 days |
| E5.7 | queries/E5.7-memory-trend-48h.dql | 2026-01-14 04:45 → 2026-01-16 04:45 | 5 series | None | Sawtooth pattern: +75–90 MB/h up to 850–930 MB in every copy |

Ruled out during exploration: summing `dt.runtime.clr.memory.consumption` across generations returned values above the container limit (the metric is not additive), so it was not used to draw conclusions; the container working set was used instead (E5.4, E5.7).
