## 6. Observability gaps found
| # | Category | Gap | Effect on the incident | Recommendation | Priority |
|---|---|---|---|---|---|
| G1 | Context | The tenant receives no Kubernetes or deployment events (0 in 24 h, Evidence 3.3) | The reason for the restart could not be confirmed, nor a previous change ruled out | Enable Kubernetes event ingestion and send deployment events from CI/CD | 🟠 High |
| G2 | Alerting | No alert on container memory near the limit or on GC time | 18 restarts in 48 h and repeated problems with no early warning (Evidence 5.5 and 5.6) | Detector: memory above 85% of the limit for 10 min and GC above 25% | 🟠 High |
| G3 | Telemetry | No memory analysis of the .NET process (which objects hold memory) | Why memory grows could not be confirmed | Capture a memory dump when usage passes 80% of the limit and analyze it | 🟡 Medium |
| G4 | Process | No record of a person acknowledging the problem | MTTA cannot be measured | Link Davis problems to the ITSM tool | 🟡 Medium |
