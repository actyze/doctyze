# Runbook — Batch failure recovery

> Confidence: 🟡 INFERRED. Doctyze drafted this from typical legacy batch
> patterns; verify against this specific system.

## Symptom

A scheduled batch job failed before completion. Downstream jobs are
either waiting (blocked) or were skipped (data integrity at risk).

## Severity

Variable. Depends on:
- Which job (some are recoverable, some are not)
- Whether downstream jobs already ran on partial data
- Whether this is an SLA-bound business cycle (month-end, year-end, etc.)

## Diagnostic steps

1. **Identify the failed job** — from the job-scheduler console or
   alert. Note the ABEND code / return code.
2. **Look up the ABEND code** in [`abend-codes.md`](abend-codes.md).
   Common ones have known recovery procedures.
3. **Check the dataset state** — did the job partially write?
   Was there a checkpoint? See the job's specific runbook in
   [`docs/programs/`](../programs/).
4. **Identify downstream jobs** that depend on this one. See the
   [job-dependency diagram](../architecture/diagrams/job-dependencies.mmd).
5. **Determine recovery type**:
   - **Restart from checkpoint** — if the job is checkpoint-restartable.
   - **Restart from beginning** — if outputs from this run can be safely
     overwritten.
   - **Manual fix-up** — if data was partially committed and downstream
     jobs ran. Coordinate with the senior operator.

## Remediations

1. **Notify the on-call operator** — for any production batch failure,
   page the operations team first. They have authority over scheduling.
2. **Resolve the underlying error** — application bug, data quality,
   resource exhaustion (sort work space, region size, etc.).
3. **Restart per the determined recovery type**.
4. **Update downstream jobs** if they ran on partial data.

## Followups

- Add a postmortem in [`docs/investigations/`](../investigations/) within 48h.
- Update this runbook if a new ABEND code or recovery pattern is discovered.
- 🔴 GAP — verify with senior engineer: who has authority to call a
  business-cycle reset (i.e., re-running the entire monthly close)?

## 🔴 GAP — please fill in

- Which jobs are checkpoint-restartable vs. restart-from-beginning?
- Who is the senior operator authorized to call recovery actions?
- What's the SLA on critical batch cycles?
