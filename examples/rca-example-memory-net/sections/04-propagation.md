## 4. Failure propagation diagram
![Failure propagation from copy 1 of the service to its consumers](img:../diagrams/D1-propagation.png)
*Figure 2. How the failure spread: one copy of the service came close to its memory limit, stopped responding and its requests failed; the other copy stayed healthy. Red: root cause and components with errors · Orange: degraded · Green: healthy · Dashed gray: no visibility.*

**Propagation sequence**
1. **23:12 — Copy 1 (pod …-a):** with container memory at 91% of the limit, the .NET process spends 91–99% of its time in GC and its requests stall for up to 81 s (Evidence 5.3, 5.4 and 5.2).
2. **23:13 — Authorization service:** the requests handled by that copy end with HTTP 500; the service's failure rate reaches 9.43% in that minute (Evidence 2.1 and 5.1).
3. **23:13–23:14 — Consumers:** get an error on 9 authorizations (Evidence 2.1).
4. **23:14 — Recovery:** Kubernetes restarts the container, GC drops back to 0% and the service is back to normal at 23:21 (Evidence 5.5 and 5.3).

**Relevant unaffected components:** copy 2 (pod …-b) with 0 failures, GC at 0% and memory at 71% of the limit (Evidence 2.2, 5.3 and 5.4); Davis recorded no other affected entities (Evidence 3.2).
**Blind spots:** the exact reason for the restart (the tenant receives no Kubernetes events) and the service's consumers, not identified in this example (see G1).
