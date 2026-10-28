## 5. Root cause analysis
### 5.1 Root cause
> **The authorization service keeps accumulating memory (75–90 MB per hour in each copy) until it nears the container's 1 GiB limit; above 90%, .NET garbage collection takes up almost all of the process's time, the application stalls and requests fail until the container restarts.**

**Certainty level:** ⚠️ Probable — the mechanism is confirmed by evidence (memory at 91% → GC at 91–99% → failures only on that copy → restart → recovery) and the pattern repeats over 48 h; still missing: what holds on to the memory (memory analysis, G3) and the exact reason for the restart (no Kubernetes events, G1).

| Classification | Description | Evidence | Official reference |
|---|---|---|---|
| Trigger | Copy 1 reached 936 MB (91% of the 1 GiB limit) and its GC time went from 15% to 99% between 04:09 and 04:14 UTC | Evidence 5.4 and 5.3 | [R2] |
| Root cause | Continuous memory growth of the .NET process (75–90 MB/h) in every copy, released only by a restart | Evidence 5.7 and 5.5 | [R2] |
| Contributing factor | GC suspends the application's threads, so in-flight requests waited for up to 81 s | Evidence 5.2 | [R3] |
| Contributing factor | No early-warning alert on memory versus the limit: 18 restarts in 48 h and repeated problems over 7 days | Evidence 5.5 and 5.6 | — |
| Mitigating factor | Copy 2 served 2,600 requests without failures and the affected copy restarted on its own | Evidence 2.2 and 5.5 | — |

### 5.2 5 whys analysis
![Root cause tree (5 whys) for incident P-2601001](img:../diagrams/D3-root-cause.png)
*Figure 3. 5 whys tree: authorizations failed because one copy of the service, almost out of free memory, spent most of its time freeing it; the service's memory grows steadily in every copy.*

| # | Question | Answer | Evidence | Official reference |
|---|---|---|---|---|
| 1 | Why did 9 authorizations fail? | Copy 1 kept requests waiting for up to 81 s and returned HTTP 500; the other copy did not fail | Evidence 2.1, 2.2 and 5.2 | — |
| 2 | Why did the requests stall? | The .NET process spent 91–99% of its time in GC, which suspends the application's threads | Evidence 5.3 | [R3] |
| 3 | Why so much GC? | The container was at 91% of its 1 GiB limit; .NET treats that limit as physical memory and above 90% runs more aggressive full collections | Evidence 5.4 | [R2] |
| 4 | Why was it so close to the limit? | Memory grows 75–90 MB per hour in every copy and only drops on restart (18 restarts in 48 h) | Evidence 5.7 and 5.5 | — |
| 5 | Why does memory grow? | ⚠️ Unconfirmed hypothesis: objects retained in the code (a leak or an unbounded cache); it needs a memory analysis of the process | N/A (G3) | — |
"—" is only valid for observed facts; every interpretation needs an official reference.

### 5.3 Hypotheses evaluated
| # | Hypothesis | For (Evidence) | Against (Evidence) | Official reference | Status |
|---|---|---|---|---|---|
| H1 | Memory pressure on copy 1 → excessive GC → failures | Failures only on copy 1 (Ev. 2.2); GC 91–99% (Ev. 5.3); memory 91% (Ev. 5.4) | — | [R2], [R3] | ✅ Confirmed |
| H2 | General failure of the service or its dependencies | — | Copy 2 had no failures and GC at 0% (Ev. 2.2, 5.1) | — | ❌ Ruled out |
| H3 | Container killed for running out of memory (OOM) | Restart at 04:14 (Ev. 5.5) | Peak usage 91%, it never reached the limit (Ev. 5.4) | — | ❌ Ruled out |
| H4 | A previous deployment or configuration change | — | No change events in 24 h, but the tenant does not receive them (Ev. 3.3) | — | ⚠️ Inconclusive |
| H5 | The Kubernetes liveness probe triggered the restart while the process was suspended | The restart matches GC at 99% (Ev. 5.3, 5.5) | No Kubernetes event with the reason | [R4] | ⚠️ Unconfirmed hypothesis |

### 5.4 Davis validation
- **Root cause entity proposed by Davis:** the service auth-api-v*-* (P-2601001) and, in a separate problem, the AuthApi.dll process group (P-2601002) (Evidence 3.2).
- **Matches the confirmed root cause:** Partially — Davis pointed to the service (the symptom) and, separately, to the process's GC (the mechanism); it kept them as two problems, while the analysis shows a single causal chain on copy 1.
- **How Davis determines the root cause:** it correlates events that share the same root cause into a single problem and ranks the most likely anomaly as the origin [R1].
