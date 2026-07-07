---
doctyze:
  artifact: spec
  generated_by: write-spec
  affects: [src/main/java/org/springframework/samples/petclinic/vet/Vet.java, src/main/java/org/springframework/samples/petclinic/vet/Specialty.java, src/main/java/org/springframework/samples/petclinic/vet/Vets.java, src/main/java/org/springframework/samples/petclinic/vet/VetController.java, src/main/java/org/springframework/samples/petclinic/vet/VetRepository.java, src/main/java/org/springframework/samples/petclinic/system/CacheConfiguration.java]
  last_verified: 2026-07-06
---
# Spec — Veterinarians & caching

## Summary

The `vet/` package lists veterinarians and their specialties. It is deliberately read-only — there are
no create/update forms — and the veterinarian list is served both as an HTML page and as a JSON/XML
document. Because the data is read-mostly, `VetRepository.findAll(...)` is cached under the `vets` cache,
which is created and enabled by `CacheConfiguration.java`.

## Domain (grounded in code)

| Type | Where | Role |
|---|---|---|
| `Vet` | `Vet.java` | `@Entity @Table(name = "vets")`, extends `Person`. Holds `Set<Specialty> specialties`. |
| `Specialty` | `Specialty.java` | `@Entity @Table(name = "specialties")`, extends `NamedEntity`. Reference data (e.g. dentistry). |
| `Vets` | `Vets.java` | **Not an entity** — a plain `@XmlRootElement` wrapper holding `List<Vet>`. |

`Vet` maps specialties with `@ManyToMany(fetch = FetchType.EAGER)` via
`@JoinTable(name = "vet_specialties", joinColumns = @JoinColumn(name = "vet_id"), inverseJoinColumns = @JoinColumn(name = "specialty_id"))`.
The raw set is kept private behind `getSpecialtiesInternal()` (lazily initialising a `HashSet`), while
the public `getSpecialties()` returns them **sorted by name** using
`Comparator.comparing(NamedEntity::getName)` and is annotated `@XmlElement` for marshalling.
`getNrOfSpecialties()` and `addSpecialty(Specialty)` round out the API.

### The `Vets` wrapper — why it exists
`VetController.showResourcesVetList()` returns a `Vets` object rather than a bare `Collection<Vet>`.
`Vets` is `@XmlRootElement` with an `@XmlElement`-annotated `getVetList()`, which (per its own Javadoc)
makes it "simpler for JSon/Object mapping" and usable by Spring's `MarshallingView`. Wrapping the
collection in a named root element gives both JSON and XML a stable top-level shape.

## Controller

`VetController` (`VetController.java`) is a `@Controller` depending on a single `VetRepository vetRepository`.
Two handlers:

| Method | Mapping | Returns |
|---|---|---|
| `showVetList(page, Model)` | `@GetMapping("/vets.html")` | View name `vets/vetList`, with a paged model (`PageRequest.of(page - 1, 5)` → `findAll(pageable)`). |
| `showResourcesVetList()` | `@GetMapping({ "/vets" })` | `@ResponseBody Vets` — content-negotiated to JSON or XML. |

`showVetList(...)` builds the pagination model (`currentPage`, `totalPages`, `totalItems`, `listVets`)
exactly like `OwnerController` does for owners.

## Data access & caching

`VetRepository` (`VetRepository.java`) extends the narrow Spring Data **`Repository<Vet, Integer>`**
(not `JpaRepository`), exposing only two methods — both read-only and both cached:

```java
@Transactional(readOnly = true)
@Cacheable("vets")
Collection<Vet> findAll() throws DataAccessException;

@Transactional(readOnly = true)
@Cacheable("vets")
Page<Vet> findAll(Pageable pageable) throws DataAccessException;
```

The `@Cacheable("vets")` annotations mean repeated calls are served from the `vets` cache instead of
hitting the database.

### Where the `vets` cache comes from
`CacheConfiguration.java` is `@Configuration(proxyBeanMethods = false)` **`@EnableCaching`** and defines
a `JCacheManagerCustomizer` bean, `petclinicCacheConfigurationCustomizer()`, that calls
`cm.createCache("vets", cacheConfiguration())`. The `cacheConfiguration()` helper returns a JCache
`MutableConfiguration` with `setStatisticsEnabled(true)`, so cache statistics are exposed (via JMX). Size
limits and eviction are left to the chosen JCache provider, as the class comment notes.

## Invariants
- The `vet/` package is read-only: the repository exposes no `save`/`delete`, and there are no
  `@PostMapping` handlers.
- The cache name in the repository annotations (`"vets"`) must match the cache created in
  `CacheConfiguration` — they are coupled by that string.
- `getSpecialties()` always returns specialties in name order, independent of insertion order in the set.

## Edge cases
- A vet with no specialties: `getSpecialtiesInternal()` lazily creates an empty `HashSet`, so
  `getNrOfSpecialties()` returns 0 and `getSpecialties()` returns an empty list rather than null.
- `/vets` vs `/vets.html`: the former returns marshalled data (`Vets`), the latter a rendered Thymeleaf
  list — two representations of the same underlying query.

## Related
- [Data access with Spring Data](data-access-with-spring-data.md) ·
  [Domain model diagram](../architecture/diagrams/domain-model.md) ·
  [Architecture overview](../architecture/overview.md)
