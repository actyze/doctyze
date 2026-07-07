---
doctyze:
  artifact: skill
  generated_by: write-skills
  affects: [pom.xml, build.gradle, src/checkstyle/nohttp-checkstyle.xml, .editorconfig, src/test/java/org/springframework/samples/petclinic/service/ClinicServiceTests.java]
  last_verified: 2026-07-06
---
# Skill — Developing and testing Spring PetClinic

Guidance for an agent working in **this** repo: a Spring Boot 4.1.0 / Java 17 MVC app with a Maven **and** a
Gradle build. All conventions below are grounded in the build config and the actual test suite under
`src/test/java`.

## Stack at a glance

- **Java 17** (enforced by `maven-enforcer-plugin` and the Gradle toolchain — do not use newer-language
  features that require a higher release).
- **Spring Boot 4.1.0**, `spring-boot-starter-webmvc` + Thymeleaf views, `spring-boot-starter-data-jpa`,
  `-validation`, `-cache`, `-actuator`.
- **Two builds, one source tree:** `pom.xml` (Maven, `./mvnw`) and `build.gradle` (Gradle, `./gradlew`).
  CI runs both (`.github/workflows/maven-build.yml`, `gradle-build.yml`). If you change dependencies or
  plugins, **update both files** or you break one pipeline.

## Build, run, test commands

```bash
# build (with verification)
./mvnw verify            # or: ./gradlew build   — what CI runs

# run locally on H2
./mvnw spring-boot:run   # or: ./gradlew bootRun  → http://localhost:8080/

# tests only
./mvnw test              # or: ./gradlew test
```

Details on profiles/databases/ports live in `docs/runbooks/build-and-run.md`.

## Code style — non-negotiable, the build enforces it

- **`io.spring.javaformat`** — `pom.xml` binds `spring-javaformat-maven-plugin`'s `validate` goal to the
  `validate` phase (v0.0.47); `build.gradle` applies the `io.spring.javaformat` plugin. A formatting
  violation **fails the build**. Auto-fix before committing:
  ```bash
  ./mvnw spring-javaformat:apply      # or: ./gradlew format
  ```
- **`.editorconfig`** — Java/XML use **tabs** (`indent_style = tab`, `tab_width = 4`); `pom.xml` uses
  2-space indent; HTML/SQL/`.gradle` use 2-space. Respect this; it matches the formatter.
- **Checkstyle + nohttp** — `maven-checkstyle-plugin` (and the Gradle `checkstyle` task) run
  `src/checkstyle/nohttp-checkstyle.xml`, which **fails on any plain `http://` URL** in the tree (use
  `https://`, or add a suppression in `src/checkstyle/nohttp-checkstyle-suppressions.xml`).
- License headers: existing source files carry the Apache 2.0 header — keep it on new files.

## Test conventions — use the narrowest slice that fits

The suite deliberately mixes Spring Boot **test slices** so tests stay fast. Match the pattern already used
for the layer you're touching:

| Slice / annotation | Used for | Example in repo |
|---|---|---|
| `@DataJpaTest` | Repository / persistence tests (H2 by default) | `service/ClinicServiceTests.java` — with `@AutoConfigureTestDatabase(replace = Replace.NONE)` so the active DB profile is honored |
| `@WebMvcTest(SomeController.class)` | Controller/web-layer tests (mocked services) | `owner/OwnerControllerTests`, `owner/PetControllerTests`, `owner/VisitControllerTests`, `vet/VetControllerTests`, `system/WelcomeControllerTests` |
| `@SpringBootTest(webEnvironment = RANDOM_PORT)` | Full-context integration tests | `PetClinicIntegrationTests`, `system/CrashControllerIntegrationTests` |
| `@SpringBootTest` + `@Testcontainers` + `@ServiceConnection` | Real-database integration | `MySqlIntegrationTests` (Testcontainers MySQL), `PostgresIntegrationTests` (via `spring-boot-docker-compose`) |
| `@ExtendWith(MockitoExtension.class)` | Plain unit tests (no Spring context) | `owner/PetValidatorTests`, `owner/PetTypeFormatterTests` |
| Plain JUnit 5 | POJO/validation/i18n tests | `model/ValidatorTests`, `vet/VetTests`, `system/I18nPropertiesSyncTest`, `system/CrashControllerTests` |

Notes grounded in the code:
- Integration tests that need Docker are annotated `@DisabledInNativeImage` and, for Testcontainers,
  `@Testcontainers(disabledWithoutDocker = true)` — they skip cleanly when Docker is absent.
- `MysqlTestApplication` and the `@ServiceConnection`-annotated containers wire the DB automatically; you do
  not hand-configure datasource URLs in tests.
- `PostgresIntegrationTests` uses `spring.docker.compose.skip.in-tests=false` to spin the `postgres` service
  from `docker-compose.yml` during the test.
- Test dependencies are the Boot 4.x `*-test` starters (`spring-boot-starter-webmvc-test`,
  `-data-jpa-test`, `-restclient-test`, etc.) plus `spring-boot-testcontainers`,
  `spring-boot-docker-compose`, and `testcontainers-mysql` — all in `pom.xml`/`build.gradle`.
- Coverage is produced by JaCoCo during `./mvnw verify` (report in `target/site/jacoco`).
- There is also a JMeter plan at `src/test/jmeter/petclinic_test_plan.jmx` for load testing (not run by CI).

## Where things live (package by feature)

Source is organized by domain feature, not by layer, under
`src/main/java/org/springframework/samples/petclinic/`:
- `owner/` — owners, pets, visits (controllers + JPA entities + repositories + validators/formatters).
- `vet/` — vets and specialties (this is the `@Cacheable` `vets` path; see
  `docs/observability/observability.md`).
- `model/` — shared `BaseEntity` / `NamedEntity` / `Person` base classes.
- `system/` — cross-cutting config: `CacheConfiguration`, `WebConfiguration` (i18n), `CrashController`
  (`/oups` error demo), `WelcomeController`.

When adding a feature, put the controller, entity, repository, and their tests in the matching feature
package, and add a `@WebMvcTest` for the controller plus a `@DataJpaTest` (or extend `ClinicServiceTests`)
for the repository.

## Pre-commit checklist

1. `./mvnw spring-javaformat:apply` (or `./gradlew format`).
2. `./mvnw verify` **and** `./gradlew build` pass (CI runs both).
3. No plain `http://` URLs (nohttp checkstyle).
4. New source files carry the Apache 2.0 license header and live in the right feature package.
