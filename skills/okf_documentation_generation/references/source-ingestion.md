# Source ingestion guide

How to extract knowledge from each source format before OKF decomposition. In
all cases the goal is a working inventory of entities, schemas, procedures, and
relationships — plus a provenance map for `sources` entries and footnote
citations.

**Critical Metadata:** Always capture the source file's last modified date (or
last commit date for repositories) and author/usage signals alongside its
content. Pass these forward to populate the OKF `generated: { by, at }` and
`sources[].last_modified` frontmatter fields accurately.

## Uploaded files

Files land in `/mnt/user-data/uploads/`. Use the platform's file-reading skills
where they exist (`pdf-reading` for PDFs, `docx` skill tooling for Word, `xlsx`
skill tooling for spreadsheets) rather than raw `cat` on binaries.

### PDF

-   Extract text and tables per page; keep page numbers — they go in citations
    (`report.pdf, p. 14`).
-   Scanned PDFs: rasterize + OCR per the pdf-reading skill.
-   Slide decks exported to PDF are usually one concept per 2–5 slides, not per
    slide.

### Word (.docx)

-   Heading structure is a *hint* for decomposition, not the answer. Extract the
    heading tree first, then decide which headings are entities (→ concepts) vs.
    narrative glue (→ context inside a concept).
-   Tables in the doc usually map straight to OKF schema tables.
-   Capture embedded hyperlinks — they're the links to follow.

### Excel (.xlsx / .csv)

-   Each sheet with a header row is a candidate `Sheet`/`Table` concept:
    document the columns (name, inferred type, description if a data-dictionary
    row exists), row count, and 2–3 sample values per column. Do NOT dump the
    data itself into the bundle.
-   A workbook that is itself a data dictionary (columns like "Field", "Type",
    "Description") describes *other* assets — produce one concept per described
    asset, not per sheet.
-   Note cross-sheet formulas/lookups — they're relationships → cross-links.

### Unknown or Proprietary File Types (Fallback Logic)

When encountering an unrecognized file extension (e.g., `.lkml`, `.pbix`,
`.tf`), do not immediately skip it. Follow this fallback sequence:

1.  **Try Text:** Attempt to read the file as plain UTF-8 text. Many proprietary
    extensions (like LookML `.lkml` or Terraform `.tf`) are just text.
2.  **Try Unzip:** If the file is binary, attempt to extract it as a ZIP
    archive. Many modern enterprise formats (like Power BI `.pbix`) are actually
    zipped directories containing readable JSON, XML, or metadata files.
3.  **Document the Contents:** If unzipped successfully, inventory the extracted
    textual components (like `DataModelSchema` in a `.pbix`) into the OKF
    bundle.
4.  **Graceful Skip:** If the file is binary and not an archive (e.g., compiled
    executable or raw proprietary binary), note the file's presence for the user
    but gracefully skip extraction rather than failing.

## URLs and websites

-   Fetch the given page, extract content, collect same-site links that look
    like documentation (nav sidebars are the map). Follow one level by default;
    confirm with the user before crawling more than ~15 pages.
-   Prefer stable canonical URLs for `resource` and citations; strip tracking
    params.
-   For JS-heavy pages where fetch returns nothing useful, tell the user rather
    than fabricating content.

## Git repositories

-   Clone shallow with submodules (`git clone --depth 1 --recurse-submodules`).
    Inventory: README(s), `docs/`, OpenAPI/proto/schema files, migration files,
    config with comments, top-level package structure.
-   READMEs and `docs/` are primary sources. Code itself is a source for
    *interface-level* facts only (public API surface, schema definitions, CLI
    flags) — don't reverse-engineer internals into the bundle unless the user
    asks.
-   `resource` for repo-derived concepts: the web URL of the file
    (`https://github.com/org/repo/blob/main/path`), not the local clone path.
-   SQL migrations / ORM models / `.proto` / OpenAPI specs are gold: they
    decompose mechanically into `Table` / `API Endpoint` concepts with full
    schema tables.

## OpenAPI / Swagger specs

-   One concept per path+method group that shares a resource (e.g., `/users`
    CRUD → one `API Resource` concept with per-method sections), or per endpoint
    if the endpoints are heterogeneous.
-   Component schemas shared across endpoints → `references/` concepts, linked
    from each endpoint.

## Pasted text / chat content

-   Treat like a small document. Cite as "provided by user, `<date>`" — no URL
    to cite.

## Mixed sources

-   Merge inventories before decomposing. If two sources describe the same
    entity, produce ONE concept citing both; note disagreements explicitly in
    the body ("Source [1] states X; source [2] states Y") rather than silently
    picking one.
