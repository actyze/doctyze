---
doctyze:
  artifact: spec
  generated_by: write-spec
  affects: [src/main/java/org/springframework/samples/petclinic/owner/Owner.java, src/main/java/org/springframework/samples/petclinic/owner/Pet.java, src/main/java/org/springframework/samples/petclinic/owner/Visit.java, src/main/java/org/springframework/samples/petclinic/owner/OwnerController.java, src/main/java/org/springframework/samples/petclinic/owner/PetController.java, src/main/java/org/springframework/samples/petclinic/owner/VisitController.java, src/main/java/org/springframework/samples/petclinic/owner/PetValidator.java, src/main/java/org/springframework/samples/petclinic/owner/PetTypeFormatter.java, src/main/java/org/springframework/samples/petclinic/owner/OwnerRepository.java]
  last_verified: 2026-07-06
---
# Spec — Owner / Pet / Visit domain

## Summary

The `owner/` package is the application's core aggregate. An `Owner` owns a collection of `Pet`s, and
each `Pet` has a collection of `Visit`s. The aggregate is loaded, mutated, and persisted **as a whole
through `Owner`** — pets and visits are added by calling methods on the owner and saved by saving the
owner, thanks to `CascadeType.ALL` on the associations. Three controllers drive the aggregate's web
forms.

## The aggregate (grounded in code)

| Type | Where | Role |
|---|---|---|
| `Owner` | `Owner.java` | Aggregate root. `@Entity @Table(name = "owners")`, extends `Person`. Owns `List<Pet> pets`. |
| `Pet` | `Pet.java` | `@Entity @Table(name = "pets")`, extends `NamedEntity`. Owns `Set<Visit> visits`, references one `PetType`. |
| `Visit` | `Visit.java` | `@Entity @Table(name = "visits")`, extends `BaseEntity`. A `date` + `@NotBlank description`. |

### Aggregate behavior on `Owner`
- `getPets()` returns the owned `List<Pet>` (a `final` list, `@OrderBy("name")`).
- `addPet(Pet)` appends only if `pet.isNew()` (guards against re-adding a persisted pet).
- `getPet(String name)` / `getPet(String name, boolean ignoreNew)` / `getPet(Integer id)` — lookups over
  the in-memory collection.
- `addVisit(Integer petId, Visit)` finds the pet by id (`Assert.notNull` guards on `petId`, `visit`, and
  the resolved pet) and delegates to `pet.addVisit(visit)`.

`Pet.addVisit(Visit)` adds to the `LinkedHashSet<Visit>` ordered `@OrderBy("date ASC")`. A `Visit`'s
no-arg constructor defaults `date` to `LocalDate.now().plusDays(1)` (tomorrow).

## Controllers

### `OwnerController`
`@Controller` depending on a single `OwnerRepository owners`. Handlers:

| Method | Mapping | Behavior |
|---|---|---|
| `initCreationForm()` | `@GetMapping("/owners/new")` | Returns `owners/createOrUpdateOwnerForm`. |
| `processCreationForm(@Valid Owner, BindingResult, RedirectAttributes)` | `@PostMapping("/owners/new")` | On errors, re-shows the form; otherwise `owners.save(owner)` and redirects to `/owners/{id}`. |
| `initFindForm()` | `@GetMapping("/owners/find")` | Returns `owners/findOwners`. |
| `processFindForm(page, Owner, BindingResult, Model)` | `@GetMapping("/owners")` | Paged search via `findByLastNameStartingWith`; 0 → error, 1 → redirect, many → `owners/ownersList`. |
| `initUpdateOwnerForm()` | `@GetMapping("/owners/{ownerId}/edit")` | Returns the create/update form. |
| `processUpdateOwnerForm(@Valid Owner, BindingResult, ownerId, RedirectAttributes)` | `@PostMapping("/owners/{ownerId}/edit")` | Rejects an id mismatch between form and URL, then `setId(ownerId)` + `save`. |
| `showOwner(ownerId)` | `@GetMapping("/owners/{ownerId}")` | Builds a `ModelAndView("owners/ownerDetails")` from `findById(...).orElseThrow(...)`. |

Binding setup: `@InitBinder setAllowedFields(...)` disallows `id`/`*.id`; `@ModelAttribute("owner") findOwner(...)`
pre-loads the model object.

### `PetController`
`@Controller @RequestMapping("/owners/{ownerId}")` depending on `OwnerRepository owners` and
`PetTypeRepository types`. Notable pieces:

- `@ModelAttribute("types") populatePetTypes()` returns `types.findPetTypes()` to fill the type dropdown.
- `@ModelAttribute("owner")` and `@ModelAttribute("pet")` pre-load the owner and pet (a new `Pet` when
  `petId` is absent, otherwise `owner.getPet(petId)`).
- Two binders: `@InitBinder("owner")` disallows id fields; **`@InitBinder("pet")` installs the custom
  validator** via `dataBinder.setValidator(new PetValidator())` and also disallows id fields.
- `processCreationForm(...)` / `processUpdateForm(...)` (`@PostMapping(".../pets/new")` /
  `".../pets/{petId}/edit"`) add domain-level rules on top of validation: reject a duplicate pet name for
  the owner (`owner.getPet(name, ...)`), and reject a `birthDate` in the future. On success they mutate
  the owner (`addPet` / `updatePetDetails`) and `owners.save(owner)` — the pet is persisted via cascade.

### `VisitController`
`@Controller` depending on `OwnerRepository owners`. `@ModelAttribute("visit") loadPetWithVisit(...)`
runs before each handler: it loads the owner, resolves the `Pet` (throwing `IllegalArgumentException`
if the pet isn't found for that owner), seeds the model with `pet`/`owner`, creates a fresh `Visit`, and
`pet.addVisit(visit)`. `@ModelAttribute("minVisitDate")` exposes tomorrow's date to the form.
`processNewVisitForm(...)` (`@PostMapping(".../visits/new")`) rejects a non-future date, then
`owner.addVisit(petId, visit)` + `owners.save(owner)`.

## Form binding helpers

- **`PetValidator`** (`PetValidator.java`) — a Spring `Validator` (not Bean Validation annotations,
  per its own comment "it is easier to define such validation rule in Java"). `validate(Object, Errors)`
  requires a non-blank `name`, a non-null `type` when `pet.isNew()`, and a non-null `birthDate`.
  `supports(...)` returns true for `Pet` and subclasses. It is wired in by `PetController`'s
  `@InitBinder("pet")`.
- **`PetTypeFormatter`** (`PetTypeFormatter.java`) — a `@Component` implementing `Formatter<PetType>`.
  `print(PetType, Locale)` returns the type's name; `parse(String, Locale)` scans
  `types.findPetTypes()` for a matching name and throws `ParseException` if none match. This lets a form
  submit a pet type by name and have Spring convert it to a `PetType` instance.

## Invariants
- The aggregate is saved through its root: controllers call `owners.save(owner)`, never a pet- or
  visit-specific repository (there is none). Cascade + eager fetch keep pets and visits consistent with
  their owner.
- `id`/`*.id` are always disallowed for binding, so a client cannot overwrite a primary key via form
  fields.
- A `Pet` name is unique within an `Owner` (enforced in the controller, not the schema).

## Edge cases
- Creating an owner whose form has errors re-renders `owners/createOrUpdateOwnerForm` with a flash
  `error` attribute rather than persisting.
- On update, an `Owner` id that disagrees with the URL path variable is rejected (`result.rejectValue("id", "mismatch", ...)`).
- A future `birthDate` (Pet) or non-future visit `date` is rejected with a `typeMismatch.*` code.

## Related
- [Data access with Spring Data](data-access-with-spring-data.md) ·
  [Domain model diagram](../architecture/diagrams/domain-model.md) ·
  [Request lifecycle](../architecture/diagrams/request-lifecycle.md) ·
  [Architecture overview](../architecture/overview.md)
