---
doctyze:
  artifact: runbook
  generated_by: write-runbook
  affects: [pom.xml, build.gradle, docker-compose.yml, src/main/resources/application.properties, src/main/resources/application-mysql.properties, src/main/resources/application-postgres.properties]
  last_verified: 2026-07-06
---
# Runbook — Build and run Spring PetClinic

## Summary

Spring PetClinic is a Spring Boot 4.1.0 web application (`spring-boot-starter-webmvc` + Thymeleaf) built
on **Java 17**. It ships two interchangeable build systems — Maven (`pom.xml`) and Gradle (`build.gradle`) —
each with a committed wrapper (`./mvnw`, `./gradlew`). Out of the box it runs against an **in-memory H2**
database and serves on **port 8080**. Two other database profiles, `mysql` and `postgres`, are provided
and can be backed by the containers in `docker-compose.yml`.

Everything below is grounded in the files listed in `affects:`. Where a setting is not in the repo, it says so.

## Prerequisites

- **JDK 17+** — `pom.xml` enforces this via `maven-enforcer-plugin` (`requireJavaVersion` = `${java.version}` = 17),
  and `build.gradle` pins a `JavaLanguageVersion.of(17)` toolchain. The CI matrix (`.github/workflows/maven-build.yml`,
  `gradle-build.yml`) builds on Java 17 only.
- **No global Maven/Gradle install needed** — use the wrappers `./mvnw` and `./gradlew`.
- **Docker** (optional) — only needed for the MySQL/Postgres profiles via `docker-compose.yml`, or to build a
  container image.

## Build

### Maven

```bash
./mvnw package          # compile + test + package the jar into target/
./mvnw verify           # package + full verification (see note below)
```

`./mvnw verify` is what CI runs (`.github/workflows/maven-build.yml` → `./mvnw -B verify`). Because of the
plugins bound in `pom.xml`, `verify` also runs: `spring-javaformat:validate` and `checkstyle:check`
(nohttp) on the `validate` phase, JaCoCo coverage (`jacoco-maven-plugin` `report`), and generates
`build-info.properties`, `git.properties`, and a CycloneDX SBOM — all of which Spring Boot Actuator surfaces
at runtime.

### Gradle

```bash
./gradlew build         # compile + test + assemble; this is what CI runs
```

`.github/workflows/gradle-build.yml` runs `./gradlew build`. `build.gradle` wires `checkstyle` and
`io.spring.javaformat`/`io.spring.nohttp` into the same graph.

> The AOT/native format and checkstyle tasks are explicitly disabled in `build.gradle`
> (`checkFormatAot.enabled = false`, etc.), so those do not run during a normal `build`.

## Run locally (default H2 profile)

No database setup required — H2 is an in-memory runtime dependency (`com.h2database:h2`), and
`src/main/resources/application.properties` seeds it at startup from
`classpath*:db/h2/schema.sql` + `db/h2/data.sql` (`database=h2`).

```bash
./mvnw spring-boot:run
# or
./gradlew bootRun
```

Then open **http://localhost:8080/**. Port 8080 is the Spring Boot default — no `server.port` is set in any
`application*.properties`, so this is the built-in default, not a repo override.

Notable runtime behavior configured in `application.properties`:
- **H2 console** is reachable (per `README.md`) at `http://localhost:8080/h2-console`. JDBC URL, user, and
  password for the console are printed in the startup log.
- **JPA**: `spring.jpa.hibernate.ddl-auto=none` (schema comes from the SQL init scripts, not Hibernate),
  `spring.jpa.open-in-view=false`, snake_case physical naming, and `default_batch_fetch_size=16`.
- **Actuator** endpoints are all exposed (`management.endpoints.web.exposure.include=*`) — see
  `docs/observability/observability.md`.
- **Static resource caching**: `spring.web.resources.cache.cachecontrol.max-age=12h`.

## Switch database profiles

Profiles are selected the standard Spring Boot way — either an env var or a CLI flag:

```bash
SPRING_PROFILES_ACTIVE=mysql ./mvnw spring-boot:run
# or
./mvnw spring-boot:run -Dspring-boot.run.profiles=mysql
# or on the built jar
java -jar target/*.jar --spring.profiles.active=postgres
```

### MySQL profile

`src/main/resources/application-mysql.properties` sets `database=mysql` and points the datasource at
environment-overridable defaults:

| Property | Default (env override) |
|---|---|
| `spring.datasource.url` | `jdbc:mysql://localhost/petclinic` (`MYSQL_URL`) |
| `spring.datasource.username` | `petclinic` (`MYSQL_USER`) |
| `spring.datasource.password` | `petclinic` (`MYSQL_PASS`) |

`spring.sql.init.mode=always` re-runs the (idempotent) `db/mysql/*.sql` scripts on each boot.

### Postgres profile

`src/main/resources/application-postgres.properties` sets `database=postgres` with the analogous
`POSTGRES_URL` / `POSTGRES_USER` / `POSTGRES_PASS` (defaults `jdbc:postgresql://localhost/petclinic`,
`petclinic`/`petclinic`), also with `spring.sql.init.mode=always`.

The JDBC drivers (`com.mysql:mysql-connector-j`, `org.postgresql:postgresql`) are `runtime`-scope
dependencies in `pom.xml`/`build.gradle`, so no extra install is needed.

## Start a database with docker-compose

`docker-compose.yml` defines two services, **each named after its Spring profile**, so you bring up only the
one you need:

```bash
docker compose up mysql       # mysql:9.7  → host port 3306
docker compose up postgres    # postgres:18.4 → host port 5432
```

Credentials in `docker-compose.yml` match the profile defaults above (`petclinic`/`petclinic`, database
`petclinic`), so once the container is up:

```bash
docker compose up mysql
SPRING_PROFILES_ACTIVE=mysql ./mvnw spring-boot:run
```

The `mysql` service also mounts `./conf.d` read-only into the container; `postgres` needs no extra config.

## Build a container image

There is **no `Dockerfile`** in this repo. Per `README.md`, build an OCI image with the Spring Boot
build-image goal (buildpacks):

```bash
./mvnw spring-boot:build-image
docker run -p 8080:8080 docker.io/library/spring-petclinic:latest
```

For the Kubernetes/CI deployment path (which uses the prebuilt `dsyer/petclinic` image), see
`docs/runbooks/deployment.md`.

## Common issues

- **`This build requires at least Java 17`** — the enforcer/toolchain rejected an older JDK. Install a
  17+ JDK.
- **Build fails on `spring-javaformat:validate` or checkstyle** — a formatting/nohttp violation. Run
  `./mvnw spring-javaformat:apply` (or `./gradlew format`) to auto-fix; see
  `docs/skills/dev-and-testing.md`.
- **Cannot connect on a db profile** — confirm the matching `docker compose up <profile>` container is
  running and the `*_URL`/`*_USER`/`*_PASS` env vars (if you overrode them) point at it.
