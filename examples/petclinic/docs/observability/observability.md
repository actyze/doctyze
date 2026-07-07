---
doctyze:
  artifact: observability
  generated_by: write-observability
  affects: [pom.xml, src/main/resources/application.properties, src/main/java/org/springframework/samples/petclinic/system/CacheConfiguration.java, src/main/java/org/springframework/samples/petclinic/system/CrashController.java, k8s/petclinic.yml]
  last_verified: 2026-07-06
---
# Observability — Spring PetClinic

## Summary

PetClinic's observability surface is **Spring Boot Actuator with mostly default configuration**, plus a
JCache cache with statistics enabled and a deliberate crash endpoint used to exercise the error path. This
document is explicit about **what is configured in-repo versus what relies on Actuator defaults** — no
metrics, dashboards, or alerts are invented here, because none are defined in the repository.

## What provides the signals

- **Spring Boot Actuator** — `spring-boot-starter-actuator` is a declared dependency (`pom.xml`;
  `runtimeOnly` in `build.gradle`). This is the only telemetry framework in the project. There is **no**
  Micrometer registry dependency (Prometheus/OTLP/etc.), **no** tracing dependency, and **no** external
  APM in the repo.
- **Build/version metadata** — `pom.xml` runs the Spring Boot `build-info` goal, the
  `git-commit-id-maven-plugin`, and the CycloneDX SBOM plugin. Actuator surfaces these via
  `/actuator/info` (build info, git commit) and `/actuator/sbom` when present on the classpath.

## Actuator endpoints (what's actually exposed)

`src/main/resources/application.properties` contains exactly one management setting:

```properties
# Expose all actuator endpoints for monitoring and management purposes
# Don't do this in production, only for development and testing
management.endpoints.web.exposure.include=*
```

So **all** web-exposable Actuator endpoints are reachable under the default base path **`/actuator`**
(no `management.endpoints.web.base-path` override exists). The repo's own comment flags that `*` exposure
is a dev/test convenience, not a production setting.

Everything else about these endpoints is **Actuator default behavior**, not repo configuration — for
example `/actuator/health`, `/actuator/info`, `/actuator/metrics`, `/actuator/caches`, `/actuator/env`,
`/actuator/loggers`, `/actuator/mappings`. The available metric names are whatever Spring Boot auto-configures
for a JPA + web app; **no custom metrics or `@Timed`/counter instrumentation exist in the codebase.**

> Note: `CrashControllerIntegrationTests` runs with `management.endpoints.access.default=none` as a
> per-test property — that is a test-only override and does not reflect the running app's configuration.

## Health checks and probes

- **In the app config:** no explicit health settings — `/actuator/health` uses Actuator defaults (aggregates
  DB, disk space, etc.).
- **In Kubernetes** (`k8s/petclinic.yml`): the deployment sets
  `management.endpoint.health.probes.add-additional-paths: true` via `SPRING_APPLICATION_JSON`, which
  publishes the additional health paths **`/livez`** (liveness group) and **`/readyz`** (readiness group).
  The pod's `livenessProbe`/`readinessProbe` HTTP-GET those paths on port 8080. The Postgres pod
  (`k8s/db.yml`) instead uses `tcpSocket` probes on 5432. Full manifest detail is in
  `docs/runbooks/deployment.md`.

## Caching behavior

`src/main/java/org/springframework/samples/petclinic/system/CacheConfiguration.java`:

- `@Configuration(proxyBeanMethods = false)` + `@EnableCaching` turns on Spring's cache abstraction.
- A `JCacheManagerCustomizer` creates a single cache named **`vets`** and enables statistics
  (`MutableConfiguration.setStatisticsEnabled(true)`), which the class comments note become accessible via
  **JMX**.
- The JCache provider at runtime is **Caffeine** (`com.github.ben-manes.caffeine:caffeine`, runtime scope) —
  there is no distributed cache.

Observability implications:
- The `vets` cache backs the vets listing (the `@Cacheable` usage lives in the `vet` package). A stale vets
  list is almost always a caching effect, not a data bug.
- With statistics on, hit/miss/eviction counts are visible via JMX and via Actuator's cache metrics (again,
  standard Actuator/Caffeine metrics — nothing custom).
- The JCache spec exposes only a minimal config surface; as the class comment states, size/TTL limits would
  have to be set through the provider (Caffeine), and **no such limits are configured here** — the cache is
  effectively unbounded by config.

## Logging

Configured in `src/main/resources/application.properties`:

```properties
logging.level.org.springframework=INFO
# logging.level.org.springframework.web=DEBUG        (commented out)
# logging.level.org.springframework.context.annotation=TRACE   (commented out)
```

- Framework logging is at **INFO**; the two more verbose levels are present but commented out — uncomment
  to debug web request handling or bean wiring.
- Logging uses Spring Boot's **default console (Logback) setup** — there is no `logback-spring.xml`, no JSON
  log encoder, and no file/rotation config in the repo. Logs go to stdout, which is the right shape for the
  container/Kubernetes deployment (collect at the platform level).
- Actuator's `/actuator/loggers` endpoint (exposed via `*`) can adjust log levels at runtime without a
  restart.

## The deliberate error path

`src/main/java/org/springframework/samples/petclinic/system/CrashController.java` maps **`GET /oups`** and
throws a `RuntimeException` on purpose. It exists to demonstrate the framework error handling: the exception
resolves to the `error.html` view (`src/main/resources/templates/error.html`) via Spring Boot's default
error handling.

Use `/oups` as a known-good way to verify that:
- unhandled exceptions render the custom error page rather than a stack trace, and
- your log pipeline captures the resulting `ERROR`-level entry.

`CrashControllerTests` and `CrashControllerIntegrationTests` cover this path — see
`docs/skills/dev-and-testing.md`.

## Gaps — be honest

The repo does **not** contain: a metrics backend/registry, dashboards, alerting rules, distributed tracing,
an error-code registry, or SLO definitions. Any of those would be additive work, not documentation of
existing behavior. If you deploy this beyond the Kind smoke-test, expect to add a Micrometer registry and
tighten `management.endpoints.web.exposure.include` before exposing `/actuator` publicly.
