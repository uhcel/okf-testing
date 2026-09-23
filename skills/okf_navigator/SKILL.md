---
name: okf-navigator
description: >-
  Navigate, search, and retrieve knowledge from Open Knowledge Format (OKF)
  v0.2 bundles using deterministic progressive disclosure. Use this skill
  whenever an agent needs to answer questions about systems, schemas, APIs,
  configurations, or operational procedures documented in an OKF bundle.
category: documentation
support_tier: community
version: 0.2.0
tags: ['documentation', 'okf', 'navigation', 'progressive-disclosure', 'open-knowledge-format']
---

# OKF Navigation Protocol (`okf-navigator`)

This skill defines the standard "Verb Pattern" navigation protocol for AI coding and research agents consuming an **Open Knowledge Format (OKF) v0.2** knowledge bundle.

Instead of running unbounded keyword searches (`grep`, `find`) across a repository or loading entire monolithic files into context, follow a deterministic 4-step progressive disclosure traversal:

## Step 1: Root Discovery (`<bundle>/index.md`)

1. Always start by reading `<bundle>/index.md` (Layer 1).
2. Inspect the `okf_version` frontmatter and the top-level domain directory listings (e.g., `playbooks/`, `services/`, `configurations/`, `computations/`, `references/`).
3. Classify the user's intent against the domain descriptions to select the matching domain directory in $O(1)$ hops.

## Step 2: Category Resolution (`<bundle>/<domain>/index.md`)

1. Follow the link from the root index to the selected domain index: `<bundle>/<domain>/index.md` (Layer 2).
2. Read the 1-sentence concept summaries (`* [Title](concept.md) - description`).
3. Identify the exact atomic concept file (`<concept>.md`) that answers the query.

## Step 3: Targeted Concept Ingestion (`<bundle>/<domain>/<concept>.md`)

1. Read **only** the specific target concept file `<bundle>/<domain>/<concept>.md` (Layer 3).
2. Never ingest the entire bundle directory or perform broad text greps unless a concept is explicitly marked missing.
3. Extract:
   - **Lifecycle & Trust Signals**: Check `status` (`stable`, `draft`, `deprecated`), `stale_after`, `generated`, and `verified` (`human-reviewed`, `machine-confirmed`, or `unverified`).
   - **Provenance Citations**: Map inline footnote markers (`[^source-id]`) to their corresponding entries in the frontmatter `sources:` list (`id`, `resource`, `title`, `author`, `last_modified`).
   - **Grounded Content**: Extract the exact commands, schemas, or configurations from the structured Markdown body.

## Step 4: Attestation & Execution Contract Check (`<bundle>/computations/<name>.md`)

1. If the concept references an executable recipe or links to `/computations/<name>.md` (`type: Attested Computation`), inspect that computation concept (Layer 4).
2. Verify the execution contract fields before running or recommending the command:
   - `runtime`: Execution environment (e.g., `bash`, `bigquery`, `python`).
   - `parameters`: Required and optional input parameters.
   - `executor.resource` and `executor.receipt`: The script/runner and expected receipt schema (e.g., `[exit_code, stdout, coverage_percentage]`).
   - `attester.resource`: The deterministic validator script (e.g., `/references/attesters/exit_code_zero.py`) used to verify execution receipts.
