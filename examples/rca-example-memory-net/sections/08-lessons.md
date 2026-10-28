## 8. Lessons learned
- **What went well:** Dynatrace detected the failure increase and the long GC within minutes; Kubernetes restarted the affected copy and the other copy absorbed the load.
- **What could be improved:** alert on the memory trend before it affects customers; ingest Kubernetes events to know the reason for each restart.
- **Where we got lucky:** the other copy was at 71% and climbing; if both had hit the limit at the same time, the outage would have been total.
