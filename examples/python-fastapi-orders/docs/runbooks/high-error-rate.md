---
runbook_id: high-error-rate
alert_names:
  - OrdersApiHighErrorRate
severity: high
service: orders-api
confidence: confirmed
---

# Runbook — orders-api high error rate

> Confidence: 🟢 CONFIRMED. Hand-authored. Drives `.holmes/runbooks/high-error-rate.yaml`.

## Symptom

5xx error rate on `orders-api` exceeds 1% over a 5-minute window.

## Severity

High — customer-visible failures during order placement.

## Triggers / signals

- Alertmanager rule: `OrdersApiHighErrorRate`
- Dashboard: https://grafana.example.com/d/orders-api
- Recent deploys in last 2h (most likely cause)

## Diagnostic steps

1. **Check recent deploys.** `gh run list --workflow=deploy.yml --limit 5`. If a
   deploy landed in the last 30 minutes, prime suspect.
2. **Pull error logs (last 100, ERROR level).** Look for:
   - Single repeated stack trace → deterministic bug introduced
   - Mixed stack traces → likely a downstream dependency degradation
   - Timeouts → downstream service unhealthy
3. **Check downstream health.** Direct probe each declared dependency in
   order of likelihood:
   - **Postgres** (`pricing.internal:5432`)
   - **Pricing service** (`pricing.internal:8080/health`) — but **see ADR-0003**:
     pricing failures should NOT be causing orders-api 5xx unless the
     fail-open fallback is broken. If pricing is the cause, file an incident.
   - **Inventory service** (`inventory.internal:8080/health`)
4. **Check the `orders_pricing_fallback_total` metric.** If high, pricing is
   degraded but orders should still be flowing (fail-open is working). If the
   error rate is also high, the fail-open code path may be broken — check
   recent commits to `src/orders/pricing.py`.

## Remediations (in escalating order)

1. **If recent deploy is the cause**: roll back.
   `gh workflow run rollback.yml -f sha=$(git rev-parse HEAD~1)`
2. **If a single downstream is the cause**: check that service's runbook and on-call.
3. **If pricing fail-open is broken** (rare but high impact): emergency
   feature-flag flip to bypass live pricing entirely, fall back to cache only.
4. **If neither and the rate is rising**: page secondary on-call, open
   incident channel.

## Followups

- Postmortem in `docs/investigations/` within 48h.
- If a new failure mode was discovered, add a runbook OR update this one.
- If ADR-0003 (fail-open pricing) needs revision after the incident,
  write a superseding ADR.
