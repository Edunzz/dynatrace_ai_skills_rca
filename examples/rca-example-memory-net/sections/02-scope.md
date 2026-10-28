## 2. Scope and impact
### 2.1 Affected components
| Component | Type | Role in the incident | Observed impact | Evidence |
|---|---|---|---|---|
| auth-api-v*-* | Service | Affected (symptom) | Failure rate 0% → **9.43%** in the 04:13 UTC minute (Davis reported 2.07% over its window) | Evidence 2.1 |
| Pod auth-api-v1-5f7c9d8b6-pod-a | Pod / .NET process | Origin | **9 of 2,298** requests failed (0.39%); GC 5% → **99%**; memory at **91%** of the limit | Evidence 2.2, 5.3 and 5.4 |
| Pod auth-api-v1-5f7c9d8b6-pod-b | Pod / .NET process | Not affected | 0 of 2,600 requests failed; GC 0% | Evidence 2.2 |
### 2.2 Impact on users and business
| Dimension | Value | Source |
|---|---|---|
| Failed requests | **9 of 4,863 (0.19%)** between 03:45 and 04:45 UTC; all with HTTP 500 | Evidence 2.1 |
| Wait time of the failed requests | up to **81 s** before returning an error | Evidence 5.2 |
| Affected users / sessions | N/A — Davis reports no affected users for this problem | Evidence 3.2 |
| Lost business transactions | N/A — there are no business events for this flow | N/A |
| Affected SLO | N/A — not evaluated in this example | N/A |
