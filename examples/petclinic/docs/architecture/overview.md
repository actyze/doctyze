---
doctyze:
  artifact: architecture
  generated_by: write-architecture
  affects: [src/main/java/org/springframework/samples/petclinic/PetClinicApplication.java, src/main/java/org/springframework/samples/petclinic/owner/OwnerController.java, src/main/java/org/springframework/samples/petclinic/vet/VetController.java, src/main/java/org/springframework/samples/petclinic/system/WebConfiguration.java, src/main/java/org/springframework/samples/petclinic/model/BaseEntity.java]
  last_verified: 2026-07-06
---
# Architecture overview — Spring PetClinic

Spring PetClinic is a classic layered **Spring MVC + Spring Data JPA** web application. A browser
request hits a `@Controller`, which reads and writes domain entities through a Spring Data repository
*interface*, and renders the result with a server-side Thymeleaf template. There is no hand-written
persistence code and no service layer of note: the controllers depend directly on repositories, and
the repositories are interfaces Spring implements at runtime.

The Spring Boot entry point is `PetClinicApplication.java` — a single `@SpringBootApplication` class
whose `main()` calls `SpringApplication.run(...)`. It also carries `@ImportRuntimeHints(PetClinicRuntimeHints.class)`
so the app can be compiled ahead-of-time (GraalVM native image); `PetClinicRuntimeHints.java` registers
resource patterns (`db/*`, `messages/*`) and reflection/serialization hints for `BaseEntity`, `Person`,
and `Vet`.

## Layers

| Layer | Where | Responsibility |
|---|---|---|
| **Web / MVC** | `owner/`, `vet/`, `system/` controllers | `@Controller` classes with `@GetMapping`/`@PostMapping` handlers; form binding via `@InitBinder`, `@ModelAttribute`, and `@Valid`. Return Thymeleaf view names (or a `@ResponseBody` object for JSON/XML). |
| **Data access** | `owner/`, `vet/` repositories | Spring Data interfaces (`OwnerRepository`, `PetTypeRepository`, `VetRepository`) — derived queries + a couple of `@Query`/`@Cacheable` methods. No implementation classes. |
| **Domain model** | `model/`, `owner/`, `vet/` entities | JPA `@Entity` classes over a shared `@MappedSuperclass` hierarchy (`BaseEntity` → `NamedEntity`/`Person`). |
| **System / config** | `system/` | `WebConfiguration` (i18n), `CacheConfiguration` (the `vets` cache), `WelcomeController`, `CrashController`. |
| **View** | `src/main/resources/templates/*` | Thymeleaf templates named by the strings controllers return (e.g. `"owners/ownerDetails"`). |

## Module split

The code is organised by feature package, not by technical layer:

- **`owner/`** — the application's core aggregate. `Owner`, `Pet`, `PetType`, `Visit` plus their
  controllers (`OwnerController`, `PetController`, `VisitController`), repositories, the `PetValidator`,
  and the `PetTypeFormatter`. See [Owner/Pet/Visit domain](../specs/owner-pet-visit-domain.md).
- **`vet/`** — `Vet`, `Specialty`, the `Vets` XML/JSON wrapper, `VetController`, and the cached
  `VetRepository`. See [Veterinarians & caching](../specs/veterinarians-and-caching.md).
- **`model/`** — the shared `@MappedSuperclass` base types every entity inherits from.
- **`system/`** — cross-cutting configuration and the welcome/crash controllers.

## The entity base hierarchy

Every persistent object inherits shared JPA mapping from three `@MappedSuperclass` types in `model/`:

- **`BaseEntity.java`** — the identity base. Holds `@Id @GeneratedValue(strategy = GenerationType.IDENTITY)`
  `Integer id`, plus `isNew()` (true when `id == null`). Implements `Serializable`.
- **`NamedEntity.java`** `extends BaseEntity` — adds a `@NotBlank String name`.
- **`Person.java`** `extends BaseEntity` — adds `@NotBlank` `firstName` / `lastName`, each `@Column(length = 30)`.

`Owner` and `Vet` extend `Person`; `Pet`, `PetType`, and `Specialty` extend `NamedEntity`; `Visit`
extends `BaseEntity` directly. Because these bases are `@MappedSuperclass` (not `@Entity`), their
columns are folded into each concrete table rather than mapped to a table of their own. The full picture
is in [Domain model](diagrams/domain-model.md).

## Request flow (one invocation)

```text
HTTP GET /owners/42
  └─ DispatcherServlet routes to OwnerController.showOwner(42)   # @GetMapping("/owners/{ownerId}")
       └─ owners.findById(42)          # OwnerRepository (Spring Data JPA) → Optional<Owner>
            └─ Owner aggregate loaded (pets EAGER-fetched, ordered by name)
       └─ ModelAndView("owners/ownerDetails") + owner
  └─ Thymeleaf renders owners/ownerDetails.html
```

Form submissions add binding and validation to that flow: `@InitBinder` methods configure the
`WebDataBinder` (e.g. `setDisallowedFields("id", "*.id")`), `@ModelAttribute` methods pre-load the
`owner`/`pet` model object, and `@Valid` triggers Bean Validation with results collected in a
`BindingResult`. The full sequence is in [Request lifecycle](diagrams/request-lifecycle.md).

## Caching

The veterinarian listing is read-mostly, so `VetRepository.findAll(...)` is annotated `@Cacheable("vets")`.
The `vets` cache is created by `CacheConfiguration.java` (`@Configuration(proxyBeanMethods = false)`
`@EnableCaching`) via a `JCacheManagerCustomizer` bean. Details in
[Veterinarians & caching](../specs/veterinarians-and-caching.md).

## Internationalisation

`WebConfiguration.java` (`@Configuration implements WebMvcConfigurer`) registers a session-scoped
`SessionLocaleResolver` (default `Locale.ENGLISH`) and a `LocaleChangeInterceptor` bound to the `lang`
request parameter, so `?lang=de` switches the UI language per session.

## Design decisions

- [ADR-0001: Repository interfaces over hand-written DAOs](decisions/0001-repository-interfaces-over-daos.md)
