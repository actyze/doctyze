---
doctyze:
  artifact: spec
  generated_by: write-spec
  affects: [src/main/java/org/springframework/samples/petclinic/owner/OwnerRepository.java, src/main/java/org/springframework/samples/petclinic/vet/VetRepository.java, src/main/java/org/springframework/samples/petclinic/owner/PetTypeRepository.java, src/main/java/org/springframework/samples/petclinic/model/BaseEntity.java, src/main/java/org/springframework/samples/petclinic/model/NamedEntity.java, src/main/java/org/springframework/samples/petclinic/model/Person.java]
  last_verified: 2026-07-06
---
# Spec — Data access with Spring Data

## Summary

PetClinic has **no hand-written persistence code**. Every repository is a Java *interface* that extends
a Spring Data base type; Spring generates the implementation at runtime. Queries come from three sources,
in increasing explicitness: inherited CRUD methods, derived query methods (parsed from the method name),
and a single `@Query`. All of them operate on the JPA entities built on the shared `@MappedSuperclass`
hierarchy.

## The repositories (grounded in code)

| Interface | Where | Base type | Methods |
|---|---|---|---|
| `OwnerRepository` | `OwnerRepository.java` | `JpaRepository<Owner, Integer>` | `findByLastNameStartingWith(String, Pageable)` → `Page<Owner>`; `findById(Integer)` → `Optional<Owner>` (+ inherited CRUD). |
| `PetTypeRepository` | `PetTypeRepository.java` | `JpaRepository<PetType, Integer>` | `findPetTypes()` → `List<PetType>` via an explicit `@Query`. |
| `VetRepository` | `VetRepository.java` | `Repository<Vet, Integer>` | `findAll()` and `findAll(Pageable)`, both `@Transactional(readOnly = true)` + `@Cacheable("vets")`. |

### Three query styles, no implementations
- **Inherited CRUD.** `OwnerRepository` and `PetTypeRepository` extend `JpaRepository`, so they inherit
  `save`, `findAll`, `deleteById`, etc. `OwnerController`/`PetController`/`VisitController` all persist
  the owner aggregate with the inherited `owners.save(owner)`.
- **Derived query.** `OwnerRepository.findByLastNameStartingWith(String lastName, Pageable pageable)` is
  implemented purely from its name — Spring Data parses `findBy…LastName…StartingWith` into a
  starts-with query and returns a paged `Page<Owner>`. There is no method body.
- **Explicit `@Query`.** `PetTypeRepository.findPetTypes()` carries
  `@Query("SELECT ptype FROM PetType ptype ORDER BY ptype.name")` — used where a specific ordering is
  wanted. It is called by both `PetController` (to populate the type dropdown) and `PetTypeFormatter`.

### Why `VetRepository` extends the narrower `Repository`
`VetRepository` extends **`Repository<Vet, Integer>`**, the minimal Spring Data marker interface, rather
than `JpaRepository`. That exposes *only* the two `findAll` methods the app actually needs, keeping the
vet data read-only by construction (no inherited `save`/`delete`). Both methods are `@Cacheable("vets")`;
see [Veterinarians & caching](veterinarians-and-caching.md).

## The entity base hierarchy

All three repository type parameters (`Owner`, `PetType`, `Vet`) resolve to entities built on the shared
`model/` `@MappedSuperclass` types:

- **`BaseEntity.java`** — `@Id @GeneratedValue(strategy = GenerationType.IDENTITY) Integer id`, plus
  `isNew()` (`id == null`). Implements `Serializable`. It is the primary-key contract every entity and
  repository (`…<T, Integer>`) shares.
- **`NamedEntity.java`** `extends BaseEntity` — adds `@Column @NotBlank String name` (base for `PetType`,
  `Specialty`, `Pet`).
- **`Person.java`** `extends BaseEntity` — adds `@NotBlank` `firstName`/`lastName`, each
  `@Column(length = 30) @Size(max = 30)` (base for `Owner`, `Vet`).

Because these are `@MappedSuperclass`, their fields are mapped into each concrete entity's own table; the
bases are never queried directly. Full relationships are in
[the domain model diagram](../architecture/diagrams/domain-model.md).

## Invariants
- Repositories are interfaces only — searching the source for a repository *implementation class* finds
  none. Behavior is inherited (`JpaRepository`/`Repository`), derived from method names, or declared with
  `@Query`.
- The id type is uniformly `Integer`, matching `BaseEntity.id`.
- Read-only access is expressed structurally: `VetRepository` extends `Repository` (no mutators) and
  marks its methods `@Transactional(readOnly = true)`.

## Edge cases
- `OwnerRepository.findById(...)` returns `Optional<Owner>`; callers use `.orElseThrow(...)` to convert a
  miss into an `IllegalArgumentException`.
- A blank last-name search: `OwnerController` substitutes an empty string, and `findByLastNameStartingWith("")`
  matches all owners (the "broadest possible search").

## Related
- [ADR-0001: Repository interfaces over hand-written DAOs](../architecture/decisions/0001-repository-interfaces-over-daos.md) ·
  [Owner/Pet/Visit domain](owner-pet-visit-domain.md) ·
  [Veterinarians & caching](veterinarians-and-caching.md) ·
  [Architecture overview](../architecture/overview.md)
