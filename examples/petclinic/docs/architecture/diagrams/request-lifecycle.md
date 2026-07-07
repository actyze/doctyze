---
doctyze:
  artifact: architecture
  generated_by: write-architecture
  affects: [src/main/java/org/springframework/samples/petclinic/owner/OwnerController.java, src/main/java/org/springframework/samples/petclinic/owner/OwnerRepository.java, src/main/java/org/springframework/samples/petclinic/owner/Owner.java]
  last_verified: 2026-07-06
---
# Request lifecycle

What happens between an HTTP request and a rendered Thymeleaf page, using the "find owners" and
"show owner" flows in `OwnerController.java` as the worked example. Grounded in `OwnerController`,
`OwnerRepository`, and the `Owner` aggregate.

```mermaid
sequenceDiagram
    autonumber
    participant B as Browser
    participant DS as DispatcherServlet
    participant C as OwnerController
    participant R as OwnerRepository
    participant DB as Database (JPA)
    participant V as Thymeleaf view

    B->>DS: GET /owners?lastName=Franklin&page=1
    DS->>C: processFindForm(page, owner, result, model)
    Note over C: @GetMapping("/owners")
    C->>R: findByLastNameStartingWith("Franklin", PageRequest.of(0, 5))
    R->>DB: derived query (paged)
    DB-->>R: Page<Owner>
    R-->>C: Page<Owner> ownersResults

    alt no matches
        C->>C: result.rejectValue("lastName", "notFound", "not found")
        C-->>DS: view name "owners/findOwners"
    else exactly one match
        C-->>DS: "redirect:/owners/{id}"
        DS->>C: showOwner(ownerId)
        Note over C: @GetMapping("/owners/{ownerId}")
        C->>R: findById(ownerId)
        R->>DB: select owner + EAGER pets/visits
        DB-->>R: Optional<Owner>
        R-->>C: Owner (or IllegalArgumentException if empty)
        C-->>DS: ModelAndView("owners/ownerDetails") + owner
    else many matches
        C-->>DS: "owners/ownersList" + pagination model
    end

    DS->>V: render(view, model)
    V-->>B: HTML
```

Key facts grounded in the code:

- **Binder + model setup runs first.** Before any handler, `OwnerController`'s `@InitBinder`
  `setAllowedFields(...)` calls `dataBinder.setDisallowedFields("id", "*.id")`, and the
  `@ModelAttribute("owner") findOwner(...)` method pre-loads the `owner` model object (a fresh `Owner`
  when no `ownerId` path variable is present, otherwise `owners.findById(ownerId)`).
- **Paging is explicit.** `findPaginatedForOwnersLastName(...)` builds a `PageRequest.of(page - 1, 5)`
  and calls the derived query `OwnerRepository.findByLastNameStartingWith(lastName, pageable)`, which
  returns a Spring Data `Page<Owner>`.
- **Single-result shortcut.** When `getTotalElements() == 1`, the controller redirects straight to
  `/owners/{id}` rather than rendering a one-row list.
- **Missing entity → exception.** `showOwner(...)` does `findById(ownerId).orElseThrow(() -> new IllegalArgumentException(...))`,
  so an unknown id surfaces as an error rather than a null.
- **Controllers return view names, not HTML.** The returned `String` (e.g. `"owners/ownerDetails"`) or
  `ModelAndView` view name is resolved to a Thymeleaf template by Spring MVC.

For form-submission handlers (`@PostMapping`) the same pipeline additionally runs `@Valid` Bean
Validation and collects errors in a `BindingResult`; see [Owner/Pet/Visit domain](../../specs/owner-pet-visit-domain.md).
