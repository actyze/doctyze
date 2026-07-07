# Example — [spring-projects/spring-petclinic](https://github.com/spring-projects/spring-petclinic) (Java / Spring Boot)

Doctyze's **complete artifact suite** generated for Spring PetClinic, reverse-engineered from its source
and ops config at commit [`51045d1`](https://github.com/spring-projects/spring-petclinic/tree/51045d1648dad955df586150c1a1a6e22ef400c2).
See [PROVENANCE.md](./PROVENANCE.md) for exact source/version and scope.

**Why this entry is different.** The library entries (click / hono / cobra) show the code-grounded
structured layer. PetClinic is a *deployable service*, so it shows the whole suite — including
**runbooks** and **observability**, grounded in the real `docker-compose.yml`, `k8s/` manifests, CI
workflows, and Actuator config. This is the strongest illustration of Doctyze on a legacy-flavored
enterprise service: point it at code with no docs, get the full operational + architectural set.

## What's in `docs/`

| Artifact | Doc | Grounded in |
|---|---|---|
| Architecture | [architecture/overview.md](docs/architecture/overview.md) | layered Spring MVC, module split, `@MappedSuperclass` hierarchy, caching, i18n |
| Diagram | [architecture/diagrams/domain-model.md](docs/architecture/diagrams/domain-model.md) | entity inheritance + Owner/Pet/Visit/Vet/Specialty (Mermaid) |
| Diagram | [architecture/diagrams/request-lifecycle.md](docs/architecture/diagrams/request-lifecycle.md) | HTTP → `OwnerController` → `OwnerRepository` → Thymeleaf (Mermaid) |
| Spec | [specs/owner-pet-visit-domain.md](docs/specs/owner-pet-visit-domain.md) | the Owner aggregate, 3 controllers, `PetValidator`, `@InitBinder` |
| Spec | [specs/veterinarians-and-caching.md](docs/specs/veterinarians-and-caching.md) | Vet/Specialty, `VetController`, `@Cacheable("vets")` + `CacheConfiguration` |
| Spec | [specs/data-access-with-spring-data.md](docs/specs/data-access-with-spring-data.md) | repository interfaces, derived queries, `@Query`, no hand-written DAOs |
| ADR | [architecture/decisions/0001-repository-interfaces-over-daos.md](docs/architecture/decisions/0001-repository-interfaces-over-daos.md) | why Spring Data interfaces instead of DAOs |
| Runbook | [runbooks/build-and-run.md](docs/runbooks/build-and-run.md) | Maven/Gradle build, H2 default, MySQL/Postgres profiles, docker-compose |
| Runbook | [runbooks/deployment.md](docs/runbooks/deployment.md) | the CI workflows + `k8s/` manifests (with a "not in repo" section) |
| Observability | [observability/observability.md](docs/observability/observability.md) | Actuator, `/livez`+`/readyz`, the `vets` cache, `/oups` — with an explicit gaps section |
| Dev/testing skills | [skills/dev-and-testing.md](docs/skills/dev-and-testing.md) | the real test slices, spring-javaformat + nohttp, dual build |

> Source references are by filename at the
> [pinned commit](https://github.com/spring-projects/spring-petclinic/tree/51045d1648dad955df586150c1a1a6e22ef400c2).
> Where the repo lacks something (Dockerfile, metrics backend, alerts), the docs say so rather than invent it.
