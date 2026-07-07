---
doctyze:
  artifact: adr
  generated_by: write-adr
  affects: [src/main/java/org/springframework/samples/petclinic/owner/OwnerRepository.java, src/main/java/org/springframework/samples/petclinic/vet/VetRepository.java, src/main/java/org/springframework/samples/petclinic/owner/PetTypeRepository.java]
  last_verified: 2026-07-06
---
# ADR-0001: Spring Data repository interfaces instead of hand-written DAOs

**Status:** 🟢 ACCEPTED (reverse-engineered from the code — describes PetClinic's existing design)
**Date:** 2026-07-06
**Deciders:** Spring PetClinic maintainers (inferred)

> Reverse-engineered by Doctyze from the code as a demonstration of the `write-adr` skill. It documents
> a decision PetClinic already embodies; it is not a proposal to change PetClinic.

## Context

The application needs CRUD and a handful of finder queries over its JPA entities (`Owner`, `Pet`,
`PetType`, `Vet`, …). The classic Java EE approach would be a **DAO layer**: an interface plus a
hand-written implementation class per aggregate, each opening an `EntityManager`/`Session`, writing the
JPQL, managing transactions, and translating exceptions. That is a lot of boilerplate whose logic is
near-identical from one entity to the next.

## Decision

PetClinic defines persistence as **Spring Data repository *interfaces* with no implementation classes**.
Each repository extends a Spring Data base type and lets the framework generate the implementation:

- `OwnerRepository extends JpaRepository<Owner, Integer>` (`OwnerRepository.java`)
- `PetTypeRepository extends JpaRepository<PetType, Integer>` (`PetTypeRepository.java`)
- `VetRepository extends Repository<Vet, Integer>` (`VetRepository.java`)

Queries are obtained in the least-explicit way that works:

1. **Inherited CRUD** from `JpaRepository` (`save`, `findAll`, …) — used directly by the controllers.
2. **Derived queries** parsed from the method name — `OwnerRepository.findByLastNameStartingWith(String, Pageable)`
   has no body.
3. **An explicit `@Query`** only where a specific result is needed —
   `PetTypeRepository.findPetTypes()` carries `@Query("SELECT ptype FROM PetType ptype ORDER BY ptype.name")`.

When a repository should stay read-only, it extends the **narrower `Repository<T, ID>`** marker rather
than `JpaRepository`, exposing only the methods declared. `VetRepository` does exactly this and marks its
methods `@Transactional(readOnly = true)` and `@Cacheable("vets")`.

## Rationale

1. **No boilerplate.** The repetitive `EntityManager` plumbing and transaction handling that a DAO impl
   would contain is provided by Spring Data; the codebase contains zero repository implementation classes.
2. **Intent-revealing method names.** `findByLastNameStartingWith` reads as the query it runs, and Spring
   Data guarantees the generated SQL matches the name.
3. **Least privilege by base type.** Choosing `Repository` vs `JpaRepository` per aggregate expresses
   read-only vs full-CRUD *structurally* — the vet data cannot be mutated because no mutator is inherited.
4. **Cross-cutting concerns compose as annotations.** Caching (`@Cacheable`) and transactions
   (`@Transactional`) attach to interface methods, so a DAO body is not needed just to host them.

## Consequences

- **Positive:** minimal, uniform persistence code; queries and their signatures stay in sync; read-only
  vs read-write is enforced by the chosen base interface; caching/transaction policy lives declaratively
  next to the query.
- **Tradeoff:** query semantics are partly encoded in *method names* and framework conventions, which is
  implicit — a reader must know Spring Data's derivation rules to know what `findByLastNameStartingWith`
  does. Complex queries still need an explicit `@Query`, and very complex ones would need a custom
  fragment.
- **Constraint:** the entities must fit Spring Data's conventions — a single `Integer` id (satisfied by
  `BaseEntity`), and finder method names that map cleanly to properties.

## Related
- [Data access with Spring Data](../../specs/data-access-with-spring-data.md) ·
  [Veterinarians & caching](../../specs/veterinarians-and-caching.md) ·
  [Architecture overview](../overview.md)
