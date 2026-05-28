# Runbook — High error rate

> Confidence: 🟡 INFERRED. Doctyze drafted this seed; verify and refine.

## Symptom

5xx error rate on `{{SERVICE_NAME}}` exceeds 1% over a 5-minute window.

## Severity

High — customer-visible failures.

## Triggers / signals

- Alertmanager rule: `{{SERVICE_NAME}}HighErrorRate` (see
  [`{{ALERT_RULES_FILE}}`]({{ALERT_RULES_LINK}}) if it exists)
- Dashboard: {{DASHBOARD_URL}}
- Recent deploys in last 2h (most likely cause)

## Diagnostic steps

1. **Check recent deploys** — `git log --oneline -10` on `main` or check
   the deploy workflow's recent runs. If a deploy landed in the last
   30 minutes, that's the prime suspect.
2. **Pull error logs** — last 100 ERROR-level log entries scoped to
   `{{SERVICE_NAME}}`. Look for:
   - Single repeated stack trace (deterministic bug introduced)
   - Mixed stack traces (likely external dependency degradation)
   - Timeouts (downstream service unhealthy)
3. **Check downstream health** — direct curl/probe to each declared
   dependency (database, auth service, payment provider, etc.).
4. **Look at metric breakdown** — is the spike concentrated on one
   endpoint or distributed?

## Remediations (in escalating order)

1. **If recent deploy is the cause**: roll back. See
   [`docs/runbooks/rollback-deploy.md`](rollback-deploy.md).
2. **If a single downstream is the cause**: check that service's
   runbook and on-call.
3. **If neither and the rate is rising**: page the secondary on-call,
   open an incident channel, begin a war-room investigation.

## Followups

- Add a postmortem in [`docs/investigations/`](../investigations/) within 48h
  of resolution.
- If a new failure mode was discovered, update this runbook OR add a new
  one and link it here.
- If an ADR was implicitly violated by the incident, write an ADR documenting
  the constraint going forward.

## 🔴 GAP — please fill in

- What's the typical baseline error rate for this service? (current value: unknown)
- Who is the secondary on-call for `{{SERVICE_NAME}}`?
- Are there any "this is expected" error patterns that should be suppressed
  from alerting? (e.g., known noisy clients, intentional 4xx responses
  alerting as 5xx-adjacent)
