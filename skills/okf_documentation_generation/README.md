# OKF Documentation Generation Skill

## Overview

The **OKF Documentation Generation** skill converts documentation from any
source — uploaded Word/PDF/Excel files, pasted text, URLs, git repositories,
wikis, or API docs — into an **Open Knowledge Format (OKF) v0.2** knowledge
bundle.

OKF is an open specificationification for human- and agent-readable
knowledge: a directory tree of markdown "concept" documents with YAML
frontmatter, index files for progressive disclosure, an update log, cross-links,
provenance sources with credibility signals, trust/lifecycle metadata, and
attested computations.

## What's New in OKF v0.2

OKF v0.2 introduces first-class support for trust, provenance, lifecycle, and
deterministic computation while maintaining a lightweight, zero-dependency
markdown foundation:

1.  **Provenance & Source Credibility Signals (§5.1)**
    -   Frontmatter `sources:` list capturing source `id`, `resource`
        (URL/path/scope), `title`, and objective signals (`author`,
        `usage_count`, `last_modified`, `usage_window`).
    -   Markdown footnote citations (`[^source-id]`) linking specific statements
        directly to structured sources.
2.  **Trust & Verification (§5.2, §5.3, §7)**
    -   `generated: { by: <actor>, at: <ISO 8601> }` (supersedes legacy
        `timestamp`).
    -   `verified: [{ by: <actor>, at: <ISO 8601> }]` documenting independent
        validation events.
    -   Standardized actor format: `<producer>/<version>` (agents/tools),
        `human:<id>` (people), and `process:<id>` (automated processes).
    -   Inferred trust tiers: *unverified*, *machine-confirmed*, and
        *human-reviewed*.
3.  **Lifecycle & Freshness (§5.4, §5.5)**
    -   `status`: `draft` | `stable` (default) | `deprecated`.
    -   `stale_after`: ISO 8601 timestamp marking when content requires
        re-verification.
4.  **Attested Computations (§10)**
    -   Dedicated `type: Attested Computation` concepts carrying blessed
        calculations/queries (`runtime`, `parameters`, `executor`, `attester`).
    -   Verifiable execution with runtime receipts, separating calculation
        definitions from consumer narratives.

## Bundle Structure

An OKF bundle is a clean directory tree designed to live directly in version
control:

```
bundle-name/
├── index.md          # Optional root directory listing (may declare `okf_version: "0.2"`)
├── log.md            # Chronological history of updates (## YYYY-MM-DD)
├── tables/           # Concepts organized by domain or entity type
│   ├── index.md      # Progressive disclosure index for tables/
│   ├── customers.md
│   └── orders.md
├── computations/     # Sanctioned Attested Computation concepts
│   ├── index.md
│   └── fiscal_revenue.md
└── references/       # Shared enumerations, lookup tables, skills, attesters
    ├── index.md
    └── order_status_codes.md
```

### Reserved Files

| Filename   | Purpose                        | Frontmatter Rule               |
| ---------- | ------------------------------ | ------------------------------ |
| `index.md` | Progressive disclosure         | Only root `index.md` may carry |
:            : directory listing (`*          : frontmatter (`okf_version\:    :
:            : [Title](path) - description`)  : "0.2"`); subdirectories have   :
:            :                                : none.                          :
| `log.md`   | Chronological update audit log | No frontmatter. Headings must  |
:            :                                : follow `## YYYY-MM-DD`.        :

## Concept Document Anatomy

Every concept is a UTF-8 markdown file consisting of YAML frontmatter and
structural markdown:

````markdown
---
type: Attested Computation
title: Revenue for fiscal year
description: Recognized revenue for a fiscal year per Finance definition.
status: stable
runtime: bigquery
parameters:
  - { name: year, type: integer, required: true }
executor:
  resource: references/skills/run-on-bq.md
  receipt: [job_id, executed_sql, result]
attester:
  resource: references/attesters/sql-equality.py
generated: { by: reference_agent/gemini-2.5-pro, at: 2026-06-20T22:53:05Z }
verified: { by: human:alice, at: 2026-06-25T09:00:00Z }
stale_after: 2026-12-31T00:00:00Z
sources:
  - id: rev-policy
    resource: https://wiki.acme/finance/revenue-recognition
    title: Revenue recognition policy
    author: team:finance-fpa
    last_modified: 2026-04-02T00:00:00Z
---

# Computation

```sql
SELECT SUM(amount) AS revenue
FROM finance.recognized_revenue
WHERE fiscal_year = @year
````

Recognized revenue per policy.[^rev-policy]

[^rev-policy]: Revenue recognition policy

````

## Validation Tool

Validate any OKF bundle against the OKF v0.2 specification using the included validation script:

```bash
python3 scripts/validate_okf.py path/to/bundle
````

The script verifies:

-   **Conformance**: Frontmatter parseability, non-empty `type`, `runtime` for
    Attested Computations, valid reserved filenames and structures.
-   **Guidance & Quality**: Missing `title`/`description`, invalid dates/actors,
    broken internal cross-links, unlinked footnotes, escaping paths, and
    unindexed orphan concepts.
-   **Summary Metrics**: Scanned file counts, concept breakdown by type, trust
    tier distributions, and freshness status.

## When to Use This Skill

-   **"Document", "catalog", "knowledge-base", or "OKF"** a specific resource or
    dataset.
-   **Transform unstructured documentation** (PDFs, Word docs, spreadsheets,
    wikis, repos) into structured agent-ready knowledge.
-   **Establish trusted metrics and attested computations** with
    machine-verifiable execution contracts.
-   **Validate, update, or migrate** an existing OKF bundle (v0.1 → v0.2).

## Authoritative Reference

-   Full OKF v0.2 Specification:
    [`references/okf-spec.md`](references/okf-spec.md)
-   Source Ingestion Guide:
    [`references/source-ingestion.md`](references/source-ingestion.md)
