## 7. Action plan
| ID | Action | Type | Origin | Owner | Due date | Priority | Status | Closing criteria |
|---|---|---|---|---|---|---|---|---|
| A1 | Automatic restart of the affected container | Containment | Trigger | @Kubernetes (automatic) | 2026-01-15 | 🔴 Critical | ✅ Done | Service at baseline since 23:21 |
| A2 | Analyze a memory dump and fix the retention in the code | Corrective | Root cause | @To be assigned | 2026-01-29 | 🔴 Critical | Pending | Memory growth below 10 MB/h for 48 h |
| A3 | Temporary mitigation: scheduled pod recycling before 80% memory, or a limit adjustment | Preventive | Contributing factor | @To be assigned | 2026-01-22 | 🟠 High | Pending | 0 GC or failure problems in 7 days |
| A4 | Create a detector for memory versus the limit and for GC time | Detection | G2 | @To be assigned | 2026-01-22 | 🟠 High | Pending | Alert tested before the next memory cycle |
| A5 | Ingest Kubernetes and deployment events | Detection | G1 | @To be assigned | 2026-01-29 | 🟠 High | Pending | Kubernetes events visible in Grail for the cluster |
- Owners marked `@To be assigned`: agree on them with the team that owns the service.
