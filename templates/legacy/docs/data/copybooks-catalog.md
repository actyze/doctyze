# Copybooks / shared structures catalog

> Confidence: 🟡 INFERRED. Doctyze extracted this from the codebase.
> Verify and refine.

In legacy systems, shared data structures are the **highest-coupling**
artifacts. Changing a copybook ripples through every program that
copies it in. This catalog is the authoritative reference.

## Conventions

- One entry per significant copybook / shared structure.
- Cross-reference: which programs USE each structure?
- Versioning history: when was the structure last changed and why?

## Catalog

### Example: COBOL copybook `CUST-REC.cpy`

- **Purpose**: Customer master record layout
- **Length**: 256 bytes
- **Used by**: Programs CUST001, CUST002, BATCH-NIGHTLY-CUSTUPDATE
- **Owner**: Customer Master team
- **Last changed**: {{LAST_CHANGED}}
- **Change history**: (link to git log or change-management records)
- **Known consumers downstream**: (interfaces that consume this structure)

### Example: ABAP DDIC structure `ZCUST_REC`

- **Purpose**: Customer master record
- **Used by**: Programs ZCUST001, ZCUST002, function module ZCUST_GET_DATA
- **Owner**: Customer Master team

### 🔴 GAP — these need senior-engineer input

- Which copybooks have **undocumented field-level meanings** (e.g., the
  flag field's bit 3 means "credit on hold" in production but isn't
  in the comment)?
- Which copybooks were created for a specific incident or workaround
  that's no longer relevant but can't be removed because callers depend
  on the size?

## Why this matters

When modernizing or making any non-trivial change to a legacy system,
the copybook catalog is the first place to look. A single wrong byte
in a heavily-shared structure can corrupt every consumer downstream.
