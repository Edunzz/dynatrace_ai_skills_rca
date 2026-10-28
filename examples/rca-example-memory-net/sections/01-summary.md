## 1. Executive summary
On January 15 between 23:08 and 23:21 (local time), the service that authorizes requests from the applications returned errors for some of them. **9 of about 4,900 requests (0.2%)** failed, some after waiting more than a minute; the rest were served normally.
- **Why it happened (root cause, ⚠️ Probable):** one of the two copies of the service ran almost out of available memory and spent nearly all its time trying to free it, so it stopped responding in time.
- **What triggered it:** that copy's memory had been growing steadily for hours until it reached 91% of its limit.
- **How we recovered:** the platform automatically restarted that copy at 23:14, and by 23:21 the service was working normally.
- **How we found out:** Dynatrace detected it automatically 6 minutes after the first failure.
- **Where things stand:** resolved, but the pattern keeps repeating: in the last 48 hours the service's copies restarted 18 times with the same memory growth.
- **What we'll do so it doesn't happen again:** fix the service's memory consumption (Jan 29), alert before memory reaches the limit (Jan 22) and record the platform's events (Jan 29).
