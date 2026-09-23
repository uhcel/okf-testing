#!/usr/bin/env python3
"""Validate an Open Knowledge Format (OKF) v0.2 bundle.

Errors   = Conformance violations per OKF v0.2 spec (§11).
Warnings = Soft-guidance issues (missing descriptions, broken links, orphans,
           schema/formatting recommendations, legacy v0.1 deprecations).

Usage: python3 validate_okf.py [path/to/bundle]
Exit code 0 if no errors (warnings allowed), 1 otherwise.
"""

import datetime
import pathlib
import re
import sys
from typing import Any, Dict, Optional, Tuple

try:
  import yaml
except ImportError:
  yaml = None

RESERVED_FILES = {"index.md", "log.md"}
VALID_STATUSES = {"draft", "stable", "deprecated"}
ISO_DATETIME_RE = re.compile(
    r"\d{4}-\d{2}-\d{2}(?:[T\s]\d{2}:\d{2}(?::\d{2}(?:\.\d+)?)?(?:Z|[+-]\d{2}:?\d{2})?)?"
)
ACTOR_RE = re.compile(
    r"(?:human:[a-zA-Z0-9_.-]+|process:[a-zA-Z0-9_.-]+|[a-zA-Z0-9_.-]+/[a-zA-Z0-9_.-]+)"
)
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


def parse_frontmatter(
    text: str,
) -> Tuple[Optional[Dict[str, Any]], Optional[str], str]:
  """Parses YAML frontmatter from markdown file text.

  Args:
    text: Raw markdown file content.

  Returns:
    A tuple of (parsed_dict_or_none, error_str_or_none, raw_body_str).
  """
  if not text.startswith("---"):
    return None, "no frontmatter block (file must start with '---')", text

  # Find the closing --- delimiter on its own line
  m = re.fullmatch(r"---\s*\n(.*?)\n---\s*\n?(.*)", text, re.DOTALL)
  if not m:
    return None, "unterminated frontmatter block (missing closing '---')", text

  fm_raw = m.group(1)
  body = m.group(2)

  if yaml is not None:
    try:
      parsed = yaml.safe_load(fm_raw)
      if parsed is None:
        return {}, None, body
      if not isinstance(parsed, dict):
        return (
            None,
            (
                "frontmatter must be a YAML mapping/dict, got"
                f" {type(parsed).__name__}"
            ),
            body,
        )
      return parsed, None, body
    except yaml.YAMLError as exc:
      return None, f"YAML parsing error: {exc}", body

  # Fallback lightweight parser if pyyaml is unavailable
  fm = {}
  lines = fm_raw.splitlines()
  for line in lines:
    stripped = line.strip()
    if not stripped or stripped.startswith("#"):
      continue
    if ":" in stripped and not stripped.startswith("- "):
      k, v = stripped.split(":", 1)
      k, v = k.strip(), v.strip().strip("'\"")
      if v.startswith("[") and v.endswith("]"):
        fm[k] = [
            x.strip().strip("'\"") for x in v[1:-1].split(",") if x.strip()
        ]
      else:
        fm[k] = v
  return fm, None, body


def is_valid_iso_datetime(val: Any) -> bool:
  """Checks if value is a valid ISO 8601 date or datetime.

  Args:
    val: Value to validate.

  Returns:
    True if value is a valid ISO 8601 date or datetime string/object.
  """
  if isinstance(val, (datetime.datetime, datetime.date)):
    return True
  if not isinstance(val, str):
    return False
  return bool(ISO_DATETIME_RE.fullmatch(val.strip()))


def is_valid_actor(val: Any) -> bool:
  """Checks if actor matches convention (<producer>/<version>, human:<id>, process:<id>).

  Args:
    val: Actor identifier to validate.

  Returns:
    True if valid actor format, False otherwise.
  """
  if not isinstance(val, str):
    return False
  return bool(ACTOR_RE.fullmatch(val.strip()))


def get_trust_tier(verified: Any) -> str:
  """Determines trust tier from verified frontmatter field.

  Args:
    verified: Content of the 'verified' frontmatter field.

  Returns:
    Trust tier: 'human-reviewed', 'machine-confirmed', or 'unverified'.
  """
  if not verified:
    return "unverified"

  entries = (
      [verified]
      if isinstance(verified, dict)
      else (verified if isinstance(verified, list) else [])
  )
  if not entries:
    return "unverified"

  for entry in entries:
    if isinstance(entry, dict):
      by = str(entry.get("by", ""))
      if by.startswith("human:"):
        return "human-reviewed"
  return "machine-confirmed"


def is_stale(stale_after: Any) -> bool:
  """Checks if stale_after datetime has passed.

  Args:
    stale_after: ISO 8601 string, date, or datetime object.

  Returns:
    True if stale_after datetime has passed, False otherwise.
  """
  if not stale_after:
    return False
  try:
    now = datetime.datetime.now(datetime.timezone.utc)
    if isinstance(stale_after, datetime.datetime):
      stale_dt = (
          stale_after
          if stale_after.tzinfo
          else stale_after.replace(tzinfo=datetime.timezone.utc)
      )
      return now >= stale_dt
    if isinstance(stale_after, datetime.date):
      return now.date() >= stale_after
    if isinstance(stale_after, str):
      dt = datetime.datetime.fromisoformat(stale_after.replace("Z", "+00:00"))
      if not dt.tzinfo:
        dt = dt.replace(tzinfo=datetime.timezone.utc)
      return now >= dt
  except (ValueError, TypeError, AttributeError):
    pass
  return False


def main(bundle_path: str = ".") -> int:
  """Validates an OKF v0.2 bundle at the given directory path.

  Args:
    bundle_path: Path to the root directory of the OKF bundle.

  Returns:
    0 if validation passed without errors, 1 otherwise.
  """
  root = pathlib.Path(bundle_path).resolve()
  if not root.is_dir():
    print(f"ERROR: {root} is not a directory")
    return 1

  errors = []
  warnings = []
  if yaml is None:
    warnings.append(
        "PyYAML is not installed. Using a simplistic fallback parser which"
        " may misparse complex YAML."
    )
  md_files = sorted(root.rglob("*.md"))

  concepts = {}
  type_counts = {}
  trust_counts = {"human-reviewed": 0, "machine-confirmed": 0, "unverified": 0}
  stale_count = 0

  for f in md_files:
    rel = f.relative_to(root).as_posix()
    if f.stat().st_size > MAX_FILE_SIZE:
      errors.append(f"{rel}: file too large (>{MAX_FILE_SIZE} bytes)")
      continue
    try:
      text = f.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
      errors.append(f"{rel}: failed to read file ({exc})")
      continue

    # Reserved file handling (§3.1, §8, §9)
    if f.name in RESERVED_FILES:
      if f.name == "log.md":
        if text.startswith("---"):
          errors.append(f"{rel}: log.md MUST NOT contain frontmatter")
        dates = re.findall(r"^##\s+(.+)$", text, re.MULTILINE)
        if not dates:
          warnings.append(
              f"{rel}: log.md contains no '## YYYY-MM-DD' date sections"
          )
        for d in dates:
          if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", d.strip()):
            errors.append(f"{rel}: log date heading not ISO YYYY-MM-DD: {d!r}")
      elif f.name == "index.md":
        if text.startswith("---"):
          if rel != "index.md":
            errors.append(
                f"{rel}: frontmatter only permitted in bundle-root index.md"
                " (§8)"
            )
          else:
            fm, err, _ = parse_frontmatter(text)
            if err:
              errors.append(f"{rel}: {err}")
            elif fm and "okf_version" not in fm:
              warnings.append(
                  f"{rel}: root index.md frontmatter should define"
                  " 'okf_version: \"0.2\"'"
              )
        if not re.search(r"^\s*[*-]\s+\[.+\]\(.+\)", text, re.MULTILINE):
          warnings.append(
              f"{rel}: index has no list entries (e.g. '* [Title](path) -"
              " description')"
          )
      continue

    # Concept document parsing (§4)
    fm, err, body = parse_frontmatter(text)
    if err:
      errors.append(f"{rel}: {err}")
      continue

    concept_type = fm.get("type")
    if not concept_type or not str(concept_type).strip():
      errors.append(
          f"{rel}: missing or empty required 'type' field (§4.1, §11)"
      )
      continue

    concept_type = str(concept_type).strip()
    type_counts[concept_type] = type_counts.get(concept_type, 0) + 1

    # Recommended base fields
    if not fm.get("title"):
      warnings.append(f"{rel}: missing recommended 'title' field")
    if not fm.get("description"):
      warnings.append(
          f"{rel}: missing recommended 'description' field (used by index files"
          " and search)"
      )

    # Trust signals (§5.2, §5.3, §7)
    generated = fm.get("generated")
    if generated is not None:
      if isinstance(generated, dict):
        by = generated.get("by")
        at = generated.get("at")
        if not by:
          warnings.append(f"{rel}: 'generated' missing 'by' actor")
        elif not is_valid_actor(str(by)):
          warnings.append(
              f"{rel}: 'generated.by' does not match actor convention"
              f" (<producer>/<version>, human:<id>, process:<id>): {by!r}"
          )
        if not at:
          warnings.append(f"{rel}: 'generated' missing 'at' timestamp")
        elif not is_valid_iso_datetime(at):
          warnings.append(
              f"{rel}: 'generated.at' not ISO 8601 datetime: {at!r}"
          )
      else:
        warnings.append(
            f"{rel}: 'generated' should be a mapping {{ by: ..., at: ... }}"
        )

    # Legacy timestamp check (§13.1)
    if "timestamp" in fm and generated is None:
      warnings.append(
          f"{rel}: legacy 'timestamp' field is superseded by 'generated: {{ by,"
          " at }' in OKF v0.2"
      )

    # Verified field (§5.2)
    verified = fm.get("verified")
    if verified is not None:
      v_entries = (
          [verified]
          if isinstance(verified, dict)
          else (verified if isinstance(verified, list) else None)
      )
      if v_entries is None:
        warnings.append(
            f"{rel}: 'verified' must be a mapping or list of mappings"
        )
      else:
        for v_entry in v_entries:
          if isinstance(v_entry, dict):
            v_by = v_entry.get("by")
            v_at = v_entry.get("at")
            if not v_by:
              warnings.append(f"{rel}: 'verified' entry missing 'by' actor")
            elif not is_valid_actor(str(v_by)):
              warnings.append(
                  f"{rel}: 'verified.by' does not match actor convention:"
                  f" {v_by!r}"
              )
            if v_at and not is_valid_iso_datetime(v_at):
              warnings.append(
                  f"{rel}: 'verified.at' not ISO 8601 datetime: {v_at!r}"
              )
          else:
            warnings.append(f"{rel}: invalid entry in 'verified' list")

    tier = get_trust_tier(verified)
    trust_counts[tier] += 1

    # Lifecycle fields (§5.4, §5.5)
    status = fm.get("status")
    if status and status not in VALID_STATUSES:
      warnings.append(
          f"{rel}: 'status' value {status!r} should be one of"
          f" {sorted(VALID_STATUSES)}"
      )

    stale_after = fm.get("stale_after")
    if stale_after:
      if not is_valid_iso_datetime(stale_after):
        warnings.append(
            f"{rel}: 'stale_after' not ISO 8601 datetime: {stale_after!r}"
        )
      elif is_stale(stale_after):
        stale_count += 1
        warnings.append(
            f"{rel}: concept is STALE (now >= stale_after: {stale_after})"
        )

    # Provenance sources (§5.1)
    sources = fm.get("sources")
    source_ids = set()
    if sources is not None:
      if not isinstance(sources, list):
        warnings.append(
            f"{rel}: 'sources' must be a YAML list of source entries"
        )
      else:
        for s in sources:
          if not isinstance(s, dict):
            warnings.append(f"{rel}: each 'sources' entry must be a mapping")
            continue
          if not s.get("resource"):
            warnings.append(
                f"{rel}: source entry missing required 'resource' field"
            )
          sid = s.get("id")
          if sid:
            source_ids.add(str(sid))
          s_author = s.get("author")
          if s_author and not is_valid_actor(str(s_author)):
            warnings.append(
                f"{rel}: source author does not match actor convention:"
                f" {s_author!r}"
            )
          s_lm = s.get("last_modified")
          if s_lm and not is_valid_iso_datetime(s_lm):
            warnings.append(
                f"{rel}: source 'last_modified' not ISO 8601: {s_lm!r}"
            )
          s_count = s.get("usage_count")
          if s_count is not None and not isinstance(s_count, int):
            warnings.append(
                f"{rel}: source 'usage_count' should be an integer: {s_count!r}"
            )

    # Footnote citations check (§5.1)
    footnotes_used = re.findall(r"\[\^([a-zA-Z0-9_.-]+)\]", body)
    for fn in footnotes_used:
      if sources is None or fn not in source_ids:
        warnings.append(
            f"{rel}: footnote '[^{fn}]' has no matching 'sources' entry with id"
            f" '{fn}'"
        )

    # Legacy Citations heading check (§13.1)
    if re.search(r"^#+\s+Citations", body, re.MULTILINE) and sources is None:
      warnings.append(
          f"{rel}: body '# Citations' section is superseded by 'sources'"
          " frontmatter in OKF v0.2"
      )

    # Attested Computation contract validation (§10)
    if concept_type == "Attested Computation":
      runtime = fm.get("runtime")
      if not runtime or not str(runtime).strip():
        errors.append(
            f"{rel}: 'runtime' is REQUIRED for type 'Attested Computation'"
            " (§10.2)"
        )

      comp_path = fm.get("computation")
      if comp_path:
        if isinstance(comp_path, str) and not comp_path.startswith(
            ("http://", "https://")
        ):
          comp_target = (
              (root / comp_path.lstrip("/")).resolve()
              if comp_path.startswith("/")
              else (f.parent / comp_path).resolve()
          )
          try:
            comp_target.relative_to(root)
            if not comp_target.exists():
              warnings.append(
                  f"{rel}: referenced computation file does not exist:"
                  f" {comp_path}"
              )
          except ValueError:
            errors.append(
                f"{rel}: computation file escapes bundle boundary: {comp_path}"
            )
      else:
        # Check for # Computation section in body
        if not re.search(r"^#+\s+Computation", body, re.MULTILINE):
          warnings.append(
              f"{rel}: Attested Computation has no 'computation' file and no '#"
              " Computation' body section"
          )

      # Parameters check
      params = fm.get("parameters")
      if params is not None and not isinstance(params, list):
        warnings.append(
            f"{rel}: 'parameters' should be a list of {{ name, type,"
            " required }"
        )

      # Executor & Attester checks
      executor = fm.get("executor")
      if executor is not None:
        if not isinstance(executor, dict) or not executor.get("resource"):
          warnings.append(
              f"{rel}: 'executor' should be a mapping with a 'resource' field"
          )
      attester = fm.get("attester")
      if attester is not None:
        if not isinstance(attester, dict) or not attester.get("resource"):
          warnings.append(
              f"{rel}: 'attester' should be a mapping with a 'resource' field"
          )

    concepts[rel] = fm

  # Cross-links and orphan detection (§6, §8)
  indexed_links = set()
  for f in md_files:
    rel = f.relative_to(root).as_posix()
    if f.stat().st_size > MAX_FILE_SIZE:
      continue
    try:
      text = f.read_text(encoding="utf-8", errors="replace")
    except OSError:
      continue

    # Match markdown links to .md files
    for link_target in re.findall(r"\]\(([^)#\s]+?\.md)(?:#[^)]*)?\)", text):
      if link_target.startswith(("http://", "https://", "mailto:")):
        continue
      if link_target.startswith("/"):
        resolved = (root / link_target.lstrip("/")).resolve()
      else:
        resolved = (f.parent / link_target).resolve()

      try:
        target_rel = resolved.relative_to(root).as_posix()
      except ValueError:
        errors.append(f"{rel}: link escapes bundle boundary: {link_target}")
        continue

      if not resolved.exists():
        warnings.append(
            f"{rel}: broken link -> {link_target} (legal for placeholders, but"
            " confirm intentional)"
        )
      elif f.name == "index.md":
        indexed_links.add(target_rel)

    # Directory links in index.md
    if f.name == "index.md":
      for d in re.findall(r"\]\(([^)#\s]+?/)\)", text):
        if d.startswith(("http://", "https://")):
          continue
        if d.startswith("/"):
          resolved = (root / d.lstrip("/")).resolve()
        else:
          resolved = (f.parent / d).resolve()

        try:
          resolved.relative_to(root)
        except ValueError:
          errors.append(f"{rel}: directory link escapes bundle boundary: {d}")
          continue

        if not (resolved / "index.md").exists():
          warnings.append(
              f"{rel}: directory link -> {d} but no index.md found in target"
              " directory"
          )

  # Check for unindexed concepts (orphans)
  for rel in concepts:
    parent_dir = (root / rel).parent
    parent_index = parent_dir / "index.md"
    if parent_index.exists() and rel not in indexed_links:
      warnings.append(
          f"{rel}: not listed in its directory index"
          f" ({parent_dir.relative_to(root).as_posix()}/index.md)"
      )

  # Print summary report
  print("=" * 60)
  print("OKF v0.2 Bundle Validation Report")
  print("=" * 60)
  print(f"Scanned {len(md_files)} markdown files across '{root.name}'")
  print(f"Total Concepts: {len(concepts)}\n")

  print("Concept Types:")
  for ctype, count in sorted(type_counts.items(), key=lambda x: -x[1]):
    print(f"  - {ctype}: {count}")

  print("\nTrust Tiers:")
  print(f"  - Human-reviewed:   {trust_counts['human-reviewed']}")
  print(f"  - Machine-confirmed:{trust_counts['machine-confirmed']}")
  print(f"  - Unverified:       {trust_counts['unverified']}")

  if stale_count > 0:
    print(f"\nFreshness: {stale_count} concept(s) flagged as STALE")

  print("\n" + "-" * 60)
  if errors:
    print(f"ERRORS ({len(errors)}):")
    for e in errors:
      print(f"  [ERROR]   {e}")
  else:
    print("ERRORS: 0")

  if warnings:
    print(f"\nWARNINGS ({len(warnings)}):")
    for w in warnings:
      print(f"  [WARNING] {w}")
  else:
    print("WARNINGS: 0")

  print("=" * 60)
  if not errors and not warnings:
    print("RESULT: Bundle is fully CONFORMANT with OKF v0.2. No warnings.")
    return 0
  elif not errors:
    print(
        f"RESULT: Bundle is CONFORMANT with OKF v0.2 ({len(warnings)}"
        " warnings)."
    )
    return 0
  else:
    print(
        f"RESULT: Bundle is NOT CONFORMANT with OKF v0.2 ({len(errors)} errors,"
        f" {len(warnings)} warnings)."
    )
    return 1


if __name__ == "__main__":
  sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "."))
