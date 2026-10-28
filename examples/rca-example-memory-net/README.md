# Example: RCA of failures caused by memory pressure in a .NET service

A **real** RCA produced with the `dt-custom-rca-jromero` skill on a Dynatrace SaaS tenant, then **anonymized** for publication. It shows what the skill delivers from start to finish, in English.

The same case in Spanish is in [`rca-ejemplo-memoria-net`](../rca-ejemplo-memoria-net/). The original session was run in Spanish; this edition follows the English template the skill uses when you ask in English.

> **Anonymized data.** The customer, tenant, service, pod and process names, the entity, event and problem IDs, and the dates were replaced. The operational figures (requests, percentages, memory, times) were kept because they identify no one. The queries use fictitious IDs: they are valid DQL, but they return no data in your tenant.

## The case in one sentence

One of the two copies of an authorization service (.NET on Kubernetes) reached 91% of its memory limit and spent almost all its time in garbage collection. It stopped responding, and 9 of about 4,900 requests failed until Kubernetes restarted the container. The underlying cause: the service's memory grows 75–90 MB per hour in every copy. **Certainty: ⚠️ Probable.**

## What the agent was asked

> “Run a simple test RCA on the tenant `<context>`. Pick a recent, simple Davis problem.”

The agent followed the skill's flow:

1. **Prerequisites:** the checker returned READY and the user confirmed the context.
2. **Anchor:** it chose a "failure rate increase" problem with a single affected entity, plus a related "long garbage collection" problem one minute later.
3. **Investigation:**
   - It ruled out the first hypothesis, that the container had run out of memory: peak usage was 91%.
   - It found that every failure came from one copy.
   - It widened the window to 48 h and found the sawtooth pattern: memory grows until it nears the limit and drops on every restart (18 restarts in 48 h).
4. **Backing:** 12 evidence queries and 4 official references (Dynatrace, Microsoft .NET and Kubernetes).
5. **Build and publish:** `build_notebook.py --strict` and `dtctl apply --dry-run` passed with no errors, and the notebook was published.

## Contents

| Path | What it is |
|---|---|
| [`NOTEBOOK.md`](NOTEBOOK.md) | **Preview of the whole notebook** in Markdown: the 10 sections, the diagrams and the queries |
| [`rca_spec.json`](rca_spec.json) | Order of sections and evidence, with `"language": "en"` (input of `build_notebook.py`) |
| [`sections/`](sections/) | The 10 sections in Markdown (`00-cover.md` … `09-appendices.md`) |
| [`queries/`](queries/) | The 12 evidence queries `E<N.x>-*.dql`, each with an absolute time window |
| [`diagrams/`](diagrams/) | D1, D2 and D3 as `.drawio` (editable) and `.png` (with the XML embedded) |
| [`evidence/INDEX.md`](evidence/INDEX.md) | Evidence index. The raw `E<N.x>.json` results are left out because they contain tenant data |

## Diagrams

**D1 — How the failure spread**
![D1](diagrams/D1-propagation.png)

**D2 — Timeline**
![D2](diagrams/D2-timeline.png)

**D3 — 5 whys**
![D3](diagrams/D3-root-cause.png)

## Rebuild it

```bash
cd examples/rca-example-memory-net
python ../../skills/dt-custom-rca-jromero/scripts/build_notebook.py rca_spec.json -o notebook.json --strict
# OK: notebook.json | sections: 22 | evidence: 12 | images: 3
```

To publish it in your tenant as a demo: `dtctl apply -f notebook.json --context <your-context>`. The DQL sections will return no data because they use fictitious IDs.

For your own RCA, don't copy this example. Ask the agent for the RCA of your problem and the skill creates the whole working folder.
