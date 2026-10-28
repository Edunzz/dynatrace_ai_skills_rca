## 3. Timeline of events
![Timeline of incident P-2601001 from the first failure to recovery](img:../diagrams/D2-timeline.png)
*Figure 1. Incident timeline (local time, UTC-05:00): failures began when copy 1 was spending almost all its time freeing memory, and ended after its automatic restart.*

| # | UTC time | Local time (UTC-05:00) | Event | Type | Source |
|---|---|---|---|---|---|
| 1 | 2026-01-16 04:08 | 23:08 | First failed request (HTTP 500) on pod …-a (copy 1); GC at 11.8% | Impact | Evidence 2.1 and 5.2 |
| 2 | 2026-01-16 04:10 | 23:10 | GC time on pod …-a (copy 1) rises to 39.5% | Impact | Evidence 5.3 |
| 3 | 2026-01-16 04:12 | 23:12 | GC at 91%: Davis records the long GC event; requests stall for up to 81 s | Impact | Evidence 5.3, 3.1 and 5.2 |
| 4 | 2026-01-16 04:13 | 23:13 | Failure peak: 9.43% of the requests in that minute | Impact | Evidence 2.1 |
| 5 | 2026-01-16 04:14 | 23:14 | Davis opens P-2601001 (failure rate increase) | Detection | Evidence 3.2 |
| 6 | 2026-01-16 04:14 | 23:14 | Restart of container dotnet-container on pod …-a (copy 1) (process restart event at 04:14:51) | Mitigation | Evidence 3.1 and 5.5 |
| 7 | 2026-01-16 04:15 | 23:15 | Davis opens P-2601002 (long GC); GC time drops back to 0% | Detection | Evidence 3.2 and 5.3 |
| 8 | 2026-01-16 04:21 | 23:21 | Failure events close; service back to normal | Resolution | Evidence 3.1 and 2.1 |

| Indicator | Value | Calculation |
|---|---|---|
| MTTD | 6 min | Detection (04:14) − Impact start (04:08) |
| MTTA | N/A | No record of the team acknowledging the problem (see G4) |
| MTTR | 13 min | Resolution (04:21) − Impact start (04:08) |
