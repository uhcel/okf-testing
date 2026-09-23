---
name: okf-documentation-generation
description: >-
  Convert documentation from any source — uploaded Word/PDF/Excel files,
  pasted text, URLs, git repositories, wikis, API docs — into an Open
  Knowledge Format (OKF) v0.2 knowledge bundle. OKF is an open
  spec for agent-readable knowledge: a directory of markdown files with YAML
  frontmatter supporting provenance, trust signals, lifecycle, and attested
  computations. Use this skill whenever the user asks to "document",
  "catalog", "knowledge-base", or "OKF" a resource, wants documentation
  restructured into markdown concepts, mentions a knowledge bundle, or provides
  docs/links/repos and asks for structured, machine-readable knowledge output.
  Also use when the user wants to validate or extend an existing OKF bundle.
category: documentation
support_tier: community
version: 0.2.0
tags: ['documentation', 'okf', 'knowledge-base', 'open-knowledge-format']
---

# OKF Documentation Generation

Turn source documentation of any kind into a conformant Open Knowledge Format
(OKF) v0.2 bundle: a directory tree of markdown "concept" documents with YAML
frontmatter, `index.md` files for progressive disclosure, an update `log.md`,
cross-links, provenance sources with credibility signals, trust/lifecycle
metadata, and optional attested computations.

The authoritative spec is bundled at `references/okf-spec.md`. **Read it before
producing your first bundle** — conformance is defined there, not here. This
file covers workflow; the spec covers format.

## Workflow overview

1.  **Ingest** sources (files, URLs, repos) and capture metadata.
2.  **Inventory** what knowledge is actually present.
3.  **Decompose** into concepts at the right granularity and design layout.
4.  **Interactive Pilot** to align with the user on style, depth, and structure.
5.  **Generate** concept documents, indexes, and the log.
6.  **Validate** with `scripts/validate_okf.py` and fix what it flags.
7.  **Deliver** the bundle (directory or zip) to the user.

For anything beyond a trivial single-document source, show the user the proposed
concept inventory and directory layout (step 3) before generating everything.
Restructuring a bundle after the fact is more expensive than a 30-second logic
check up front.

## Step 1: Ingest sources

Sources arrive in wildly different formats. Read
`references/source-ingestion.md` for per-format extraction guidance (PDF, docx,
xlsx, URLs, git repos, OpenAPI, etc.).

Key rules regardless of format:

-   **Follow links one level deep by default.** If the source document links to
    other pages/files, fetch them too — they're usually where the real detail
    lives. Go deeper only when the linked page is clearly part of the same
    documentation set (same domain/repo, same subject); ask the user before
    crawling anything large. Never follow links out to generic external sites
    (Wikipedia, vendor marketing pages) — cite those instead.
-   **Record provenance as you go.** Every fetched URL, filename, author, commit
    date, or repo path becomes a source entry. Keep a running map of claim →
    source; you will need it for the `sources` frontmatter list and markdown
    footnote citations (`[^source-id]`).
-   **Extract, don't reproduce.** The bundle should contain *knowledge about*
    the source expressed in your own words and structure — schemas, behaviors,
    relationships, procedures — not wholesale copies of copyrighted prose.
    Tables of fields, enumerations, and code/config examples are fine to carry
    over; paragraphs of narrative text are not.

## Step 2: Inventory the knowledge

Before writing any files, list what the source actually contains. Typical
knowledge kinds and the OKF `type` values that fit them:

| Knowledge found in source         | Suggested `type`                      |
| --------------------------------- | ------------------------------------- |
| Table, dataset, or sheet schema   | `Table`, `BigQuery Table`, `Dataset`  |
| An API operation or resource      | `API Endpoint`, `API Resource`        |
| A named metric, KPI, or business  | `Metric`                              |
: definition                        :                                       :
| Sanctioned computation or query   | `Attested Computation` (see spec §10) |
| A how-to, runbook, or operational | `Playbook`                            |
: procedure                         :                                       :
| A design decision, architecture   | `Architecture`, `Decision`            |
: description                       :                                       :
| A service, system, or component   | `Service`, `Component`                |
| An enumeration, glossary term,    | `Reference`                           |
: license, lookup list              :                                       :
| A business process or domain idea | `Concept`                             |

`type` values are producer-defined in OKF — pick descriptive ones and stay
consistent within the bundle. Don't invent a new type for each document; a
bundle with 40 types is a bundle with no types.

## Step 3: Decompose — the granularity call

This is the judgment step that makes or breaks the bundle. The unit rule:

> **One concept = one thing an agent would want to retrieve on its own.**

Concretely:

-   Each table, endpoint, metric, playbook, service → its own file. An agent
    answering "what columns does `orders` have?" should be able to load one
    small file, not a 200-line monolith.
-   Each calculation or query that must be verified deterministically → its own
    `Attested Computation` concept file (e.g. under `computations/`), referenced
    from narrative concepts (`Metric`, `Report`).
-   Each enumeration or lookup list referenced by other concepts → its own file
    under `references/` so multiple concepts can link to it instead of
    duplicating it.
-   A source *document* is not a concept. A 60-page PDF might yield 25 concepts;
    a one-page README might yield one. Never mirror the source's chapter
    structure just because it exists — mirror the *entities* the source
    describes.

Signs the granularity is wrong:

-   **Too coarse:** a concept body covers multiple headings that don't reference
    each other; you keep wanting to link to "part of" a file. Split it.
-   **Too fine:** files under ~5 lines of body that only make sense next to
    their sibling; a directory of 30 one-liner files that are really rows of one
    enumeration. Merge into a single `Reference` concept with a table.

**Directory layout** groups concepts by kind or domain — whatever produces
directories of 5–30 related files. Common shape:

```
bundle-name/
├── index.md          # root index (may carry okf_version frontmatter)
├── log.md
├── tables/           # or endpoints/, services/, playbooks/, metrics/ …
│   ├── index.md
│   └── <concept>.md
├── computations/     # Attested Computation concepts
│   ├── index.md
│   └── <computation>.md
└── references/       # enumerations, lookup material, skills, attesters
    ├── index.md
    └── <concept>.md
```

Filenames: lowercase snake_case, derived from the concept title
(`post_history_type_ids.md` or `fiscal_revenue.md`). The path minus `.md` is the
concept ID — make it something a human can guess.

## Step 4: Interactive Pilot Phase & Preference Persistence

Do not generate the entire OKF bundle all at once. To ensure alignment with the
user's expectations, follow a "Pilot" approach:

1.  **Generate the First File:** Draft ONLY the first representative `.md`
    concept file (or `index.md`) and present it to the user.
2.  **Request Review:** Explicitly ask the user for feedback on the structure,
    tone, depth of detail, and formatting.
3.  **Persist Preferences:** When the user provides feedback, update the pilot
    file. Extract the underlying rules from their feedback (e.g., "User prefers
    schema tables over lists", "User wants explicit sources with usage counts")
    and persist these rules in your active context.
4.  **Batch Generation:** Once the pilot file is approved, batch-generate the
    remaining markdown files in Step 5. Strictly apply the persisted rules to
    all subsequent generations without pausing for approval on each file, unless
    the user explicitly requests step-by-step review.

## Step 5: Generate documents

For every concept file, follow §4, §5, §7, and §10 of the spec.

### Frontmatter Schema (OKF v0.2)

-   **`type` is REQUIRED**: Short string identifying concept kind (`BigQuery
    Table`, `Metric`, `Attested Computation`, `Playbook`, etc.).
-   **Recommended base fields**:

    -   `title`: Human-readable display name.
    -   `description`: Single sentence summary (reused in `index.md`).
    -   `resource`: Canonical URI / URL of underlying asset (omit for abstract).
    -   `tags`: YAML array for cross-cutting classification (`[finance,
        revenue]`).

-   **Provenance family (`sources`, `usage_window`)**:

    ```yaml
    sources:
      - id: ga4-schema               # Stable ID for footnote attribution
        resource: https://...        # REQUIRED within source entry
        title: GA4 Export schema     # Optional label
        author: team:ga4-docs        # Optional actor
        usage_count: 5000            # Optional exercise count
        last_modified: 2026-05-30T00:00:00Z
    usage_window: { from: 2026-06-01T00:00:00Z, to: 2026-06-30T00:00:00Z }
    ```

-   **Trust family (`generated`, `verified`) & Actor Convention**:

    -   `generated: { by: <actor>, at: <ISO-8601> }` (replaces legacy
        `timestamp`).
    -   `verified: [{ by: <actor>, at: <ISO-8601> }]` (or bare `{ by, at }`).
    -   **Actor convention**:
    -   `<producer>/<version>` for agents/tools (`okf-agent/gemini-2.5-pro`).
    -   `human:<id>` for people (`human:alice`).
    -   `process:<id>` for automated jobs (`process:nightly-etl`).
    -   **Trust tiers**: *unverified* (none) → *machine-confirmed* (non-human
        verifier) → *human-reviewed* (`human:` verifier).

-   **Lifecycle family (`status`, `stale_after`)**:

    -   `status`: `draft` | `stable` (default) | `deprecated`.
    -   `stale_after`: ISO 8601 datetime (e.g., `2026-12-31T00:00:00Z`).

-   **Attested Computation contract fields** (for `type: Attested Computation`):

    ```yaml
    runtime: bigquery                 # REQUIRED for Attested Computation
    parameters:
      - { name: year, type: integer, required: true }
    executor:
      resource: references/skills/run-on-bq.md
      receipt: [job_id, executed_sql, result]
    attester:
      resource: references/attesters/sql-equality.py
    ```

### Bodies & Section Headings

-   **Bodies are structural markdown**: headings, tables, lists, code blocks.
    Prefer a schema table over prose describing fields.
-   **Conventional headings**:
    -   `# Schema` for assets with columns/fields.
    -   `# Examples` for concrete usage examples and queries.
    -   `# Computation` for inline code fences of an Attested Computation.
-   **Per-claim attribution**: Use markdown footnotes keyed to `sources[].id`:

    ```markdown
    The `events_` table is sharded daily as `events_YYYYMMDD`.[^ga4-schema]

    [^ga4-schema]: GA4 BigQuery Export schema
    ```
-   **Cross-link aggressively** with bundle-relative links
    (`/tables/customers.md` — leading slash, `.md` suffix kept). Links to
    not-yet-written concepts legal.

### Reserved Files

-   **Index files (`index.md`)**:
    -   Root `index.md` MAY carry `okf_version: "0.2"` in frontmatter.
    -   Subdirectory `index.md` files contain NO frontmatter.
    -   Body groups concepts: `* [Title](relative-url) - description`.
-   **Log file (`log.md`)**:
    -   Date-grouped, newest first, `## YYYY-MM-DD` headings.
    -   Entries: `* **Creation**: Established [Concept](/path/concept.md).`, `*
        **Update**: ...`, `* **Deprecation**: ...`.

## Step 6: Validate

Run the bundled checker against the finished bundle:

```bash
python3 scripts/validate_okf.py path/to/bundle
```

It checks OKF v0.2 conformance requirements (parseable frontmatter everywhere,
non-empty `type`, `runtime` on Attested Computations, reserved-file structure)
plus soft warnings (missing descriptions, broken internal links, invalid
actors/dates, unlinked footnotes, orphan concepts unreachable from any index).
Fix every error; use judgment on warnings.

## Step 7: Deliver

Zip the bundle directory and present it, along with a summary:

-   Concept count by type
-   Trust tier distribution (human-reviewed, machine-confirmed, unverified)
-   Any deliberately unresolved links or pending computations
-   Remind user that an OKF bundle is designed to live directly in git.

## Updating or Migrating an Existing Bundle

When updating an existing bundle or migrating from v0.1:

1.  Read the root `index.md` and `log.md` first.
2.  Upgrade `timestamp` to `generated: { by: <actor>, at: <ISO-8601> }`.
3.  Migrate body `# Citations` lists into frontmatter `sources:` and body
    footnotes `[^source-id]`.
4.  Separate verifiable formulas/queries into `type: Attested Computation`
    concepts where appropriate.
5.  Append new dated sections to `log.md` — never rewrite history.
6.  Refresh affected `index.md` listings and run `scripts/validate_okf.py`.
