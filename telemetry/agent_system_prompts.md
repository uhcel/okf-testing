# Agent-Level System Prompts and Runtime Configurations

This document records the exact agent-level system prompt, behavioral guidelines, available tools, and task-level prompts under which both autonomous evaluation subagents were executed.

---

## 1. Runtime Architecture & Model

- **Agent Runtime**: Gemini CLI Agent Architecture
- **Model**: `inherit` (Gemini 2.5 Pro)
- **Subagent Type**: `self` (inherits the parent agent's full toolset, system prompt, and reasoning profile in an isolated conversation context)
- **Conversation IDs**:
  - Baseline Subagent: `a38b0c9e-2423-491b-a8db-5ace7e01ea0a`
  - OKF Subagent: `92921646-7573-4bc8-a3bb-0176d0815909`

---

## 2. Agent-Level System Prompt (Inherited Configuration)

Both subagents operated under the following core system instructions:

```markdown
You are an expert agentic AI coding assistant pair programming with a software engineer.
Assist them in completing their research and software development tasks.

### Guidelines
- Maintain documentation integrity. Preserve all existing comments and docstrings that are unrelated to your code changes.
- Never trade accuracy about the state of the work for the appearance of completion.
- Present numbers, results, tables, or metrics only from commands or computations that ran successfully.
- Describe the contents of a file, document, or page only if you were able to read it.
- If something blocks you, exhaust legitimate alternative search paths before concluding you are blocked.
- Keep responses concise and formatted in GitHub-flavored markdown.
- Create clickable file links using the file:// scheme.
```

---

## 3. Toolset Provided to Both Agents

Both subagents had identical access to the local filesystem and search tools:

1. **`view_file`**: Read file contents with line slicing (`StartLine`, `EndLine`).
2. **`grep_search`**: Ripgrep-based regex or literal pattern search across files and directories.
3. **`find_by_name`**: File and directory finder by pattern and extension (`fd`).
4. **`list_dir`**: Directory listing of child files and subdirectories.
5. **`code_search`**: Code search across source repositories.
6. **`send_message`**: Asynchronous messaging back to the parent agent upon task completion.

---

## 4. Task-Level User Requests (Prompt Given in `<USER_REQUEST>`)

### Subagent A (Baseline Repository)
```text
<USER_REQUEST>
You are evaluating documentation retrieval on a baseline repository.
Goal: Find the exact commands and steps to create a new database migration using Alembic and SQLModel, and apply the migration locally.
Instructions:
1. Search within /workspace/okf_testing/baseline_repo to locate where migrations are documented.
2. Read the documentation file(s).
3. Report:
   - The exact files you inspected.
   - The total lines/content examined.
   - The final answer with exact commands.
   - Any difficulty or ambiguity encountered in finding the information.
</USER_REQUEST>
```

### Subagent B (OKF Knowledge Bundle)
```text
<USER_REQUEST>
You are evaluating documentation retrieval on an OKF v0.2 knowledge bundle.
Goal: Find the exact commands and steps to create a new database migration using Alembic and SQLModel, and apply the migration locally.
Instructions:
1. Start by viewing /workspace/okf_testing/okf_bundle/index.md.
2. Follow the progressive disclosure link to the relevant category index.
3. Read ONLY the specific concept document needed.
4. Report:
   - The exact files you inspected in order.
   - The total lines/content examined.
   - The final answer with exact commands.
   - Trust tier, verifier, and provenance citations found in the OKF concept frontmatter.
</USER_REQUEST>
```

---

## 5. Skills Used for Migration, Navigation & Verification

### 5.1 Migration & Validation Skill: `okf-documentation-generation`
- **Skill Path in Repo**: [`skills/okf_documentation_generation/SKILL.md`](../skills/okf_documentation_generation/SKILL.md)
- **Bundled Reference Specs & Scripts in Repo**:
  - [`skills/okf_documentation_generation/references/okf-spec.md`](../skills/okf_documentation_generation/references/okf-spec.md) — Authoritative OKF v0.2 specification (§3–§13).
  - [`skills/okf_documentation_generation/references/source-ingestion.md`](../skills/okf_documentation_generation/references/source-ingestion.md) — Source ingestion & provenance mapping guidelines.
  - [`skills/okf_documentation_generation/scripts/validate_okf.py`](../skills/okf_documentation_generation/scripts/validate_okf.py) — Official OKF v0.2 conformance validator (also at [`tools/validate_okf.py`](../tools/validate_okf.py)).
- **Role**: Used to ingest `baseline_repo/`, inventory and decompose documentation into 12 atomic OKF concepts across 5 domain directories, attach YAML frontmatter (`type`, `status`, `generated`, `verified`, `sources`), define Attested Computations (`computations/`), and validate bundle conformance (`python3 tools/validate_okf.py okf_bundle`).

### 5.2 Production OKF Navigator Skill (`okf-navigator` — The Verb Pattern)
- **Skill Path in Repo**: [`skills/okf_navigator/SKILL.md`](../skills/okf_navigator/SKILL.md)

In standard production agent fleets, an agent is equipped with the following reusable skill definition in its system prompt to deterministically traverse OKF bundles:

```yaml
---
name: okf-navigator
description: Navigate, search, and retrieve knowledge from Open Knowledge Format (OKF) bundles using progressive disclosure.
---
```
```markdown
# OKF Navigation Protocol
When answering questions about systems, schemas, or procedures documented in an OKF bundle:
1. Root Discovery: Always inspect `<bundle>/index.md` first to determine the matching domain directory.
2. Category Resolution: Follow the link to `<domain>/index.md` and match the user intent against the 1-sentence concept summaries.
3. Targeted Ingestion: Read ONLY the specific `<domain>/<concept>.md` file. Never load the entire bundle or run unbounded text greps.
4. Attestation Check: If the concept links to `/computations/<name>.md`, read the computation concept to verify the runtime execution contract and receipts.
```
