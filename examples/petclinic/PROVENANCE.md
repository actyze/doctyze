# Provenance — petclinic

- **Source:** https://github.com/spring-projects/spring-petclinic
- **Commit:** `51045d1648dad955df586150c1a1a6e22ef400c2` (`51045d1`)
- **Generated with:** doctyze, version 0.3.4
- **Generated on:** 2026-07-06
- **Stack:** Java / Spring Boot (Maven + Gradle, JPA, Thymeleaf, Actuator)

## Scope of this entry — the full suite

Unlike the library entries (click / hono / cobra), Spring PetClinic is a **deployable service** with a
real ops surface (Docker Compose, k8s manifests, CI workflows, Spring Boot Actuator, multi-DB profiles).
So this entry shows Doctyze's **complete artifact suite**, not just the structured layer:

| Artifact | Docs | Grounded in |
|---|---|---|
| Architecture + Mermaid | overview + domain-model + request-lifecycle | `model`/`owner`/`vet`/`system` Java |
| Specs | owner-pet-visit-domain, veterinarians-and-caching, data-access-with-spring-data | the controllers, repositories, entities |
| ADR | repository-interfaces-over-daos | the Spring Data repository design |
| Runbooks | build-and-run, deployment | `pom.xml`/`build.gradle`, `docker-compose.yml`, `k8s/`, CI workflows |
| Observability | observability | Actuator config, `/livez`+`/readyz`, the `vets` cache, `/oups` error path |
| Dev/testing skills | dev-and-testing | the real test slices, spring-javaformat + nohttp checks |

Every doc carries a Doctyze freshness `affects:` anchor. The runbook/observability docs are grounded in
the **actual** ops config — where something isn't in the repo (no Dockerfile, no metrics backend, no
alerts), the docs say so explicitly rather than inventing it. Source references in prose are by filename
at the pinned commit: https://github.com/spring-projects/spring-petclinic/tree/51045d1648dad955df586150c1a1a6e22ef400c2

## Freshness demo (verified 2026-07-06)

Editing a **code** file and an **ops** file together and running `doctyze watch --base HEAD` flagged docs
across both dimensions — the operational anchors fire just like the code ones:

```
# edited OwnerController.java (code) + docker-compose.yml (ops)
4 doc(s) may be stale:
  - docs/specs/owner-pet-visit-domain.md              (regenerate: write-spec)
  - docs/architecture/overview.md                     (regenerate: write-architecture)
  - docs/architecture/diagrams/request-lifecycle.md   (regenerate: write-architecture)
  - docs/runbooks/build-and-run.md                    (regenerate: write-runbook)   ← flagged by the docker-compose edit
```

## Reproduce

```bash
scripts/build-example.sh prep petclinic https://github.com/spring-projects/spring-petclinic
# then run /doctyze in your IDE on examples/.work/petclinic (or generate by hand)
scripts/build-example.sh collect petclinic
```
