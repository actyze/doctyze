# ADR-0003 — Fail open when the pricing service is unreachable

- Status: accepted
- Date: 2026-06-06
- Confidence: 🟢 CONFIRMED

## Context

Order placement calls the pricing service (`pricing.internal`) to confirm the
current price for each SKU. The pricing service has historically had ~99.5%
availability — meaning a ~3-minute monthly outage on average.

If we treat pricing as a hard dependency, every pricing outage becomes a
customer-visible orders outage. Pricing failures are also disproportionately
likely during peak load (flash sales, marketing events) — exactly when
customer-facing reliability matters most.

The price for any SKU changes rarely (median 3 changes/year per SKU). The
risk of charging a price that's a few hours stale is materially smaller than
the risk of failing to take an order from a buying customer.

## Decision

The orders service **fails open** when the pricing service is unreachable or
returns an error:

1. The orders service maintains a local read-through cache of the last-known
   price for each SKU (TTL: 24 hours).
2. If the live pricing call fails (timeout, 5xx, connection error), the
   service uses the cached price and logs a `pricing_fallback` warning with
   structured context (SKU, cache age, pricing error).
3. If a price is not in the cache, the order is rejected with a 503 — but
   in practice this is extremely rare (cache miss rate < 0.01% in steady state).
4. The pricing-fallback rate is exposed as a metric (`orders_pricing_fallback_total`)
   and alerted at >5% over 5 minutes.

## Alternatives rejected

- **Fail closed** (reject the order if pricing is unavailable). Standard
  defensive engineering, but the math doesn't favor it: pricing outages
  would translate 1:1 to lost revenue + customer trust damage.
- **Synchronous retry with exponential backoff** — adds latency to the
  hot path with no upside. The pricing service is either healthy or not;
  retries within a single request don't change the answer.
- **Async order placement** (accept the order, confirm price later) —
  defers the problem rather than solving it. Customers would receive a
  confirmation, then later a "sorry, price changed" email. Worse UX.

## Consequences

- (+) Pricing-service outages do not become orders-service outages.
- (+) Customer-facing reliability remains high during peak load events.
- (−) Brief windows where customers are charged a stale price (bounded by
  the 24h cache TTL).
- (−) Operational discipline required: the `pricing_fallback` metric MUST
  be alerted, and the alert MUST be triaged. Letting it run hot indefinitely
  would mean systematic overcharging or undercharging.

## Important note for any AI tool reading this

**Do not "fix" the fail-open behavior** by adding an exception that aborts
the request. This is intentional design, validated against real incidents,
and changing it WILL cause a customer-visible outage during the next
pricing-service hiccup.

The `pricing_fallback` warning log is the desired path under that
condition, not a bug to be silenced.
