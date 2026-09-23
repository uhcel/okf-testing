#!/usr/bin/env python3
"""Unit tests for validate_okf.py."""

import importlib.util
import pathlib
import sys
import tempfile
import unittest

# Load validate_okf from the scripts directory
_SCRIPTS_DIR = pathlib.Path(__file__).resolve().parent.parent / "scripts"
_SPEC = importlib.util.spec_from_file_location(
    "validate_okf", _SCRIPTS_DIR / "validate_okf.py"
)
validate_okf = importlib.util.module_from_spec(_SPEC)
sys.modules["validate_okf"] = validate_okf
_SPEC.loader.exec_module(validate_okf)


class TestValidateOKF(unittest.TestCase):

  def test_parse_frontmatter_valid(self):
    text = "---\ntype: Concept\ntitle: Test\n---\n# Body\n"
    fm, err, body = validate_okf.parse_frontmatter(text)
    self.assertIsNone(err)
    self.assertEqual(fm.get("type"), "Concept")
    self.assertEqual(fm.get("title"), "Test")
    self.assertIn("# Body", body)

  def test_parse_frontmatter_no_delimiter(self):
    text = "# Just markdown\nNo frontmatter\n"
    fm, err, _ = validate_okf.parse_frontmatter(text)
    self.assertIsNotNone(err)
    self.assertIsNone(fm)

  def test_is_valid_iso_datetime(self):
    self.assertTrue(validate_okf.is_valid_iso_datetime("2026-08-21T12:00:00Z"))
    self.assertTrue(validate_okf.is_valid_iso_datetime("2026-08-21"))
    self.assertFalse(validate_okf.is_valid_iso_datetime("invalid-date"))

  def test_is_valid_actor(self):
    self.assertTrue(validate_okf.is_valid_actor("human:alice"))
    self.assertTrue(validate_okf.is_valid_actor("process:nightly-etl"))
    self.assertTrue(validate_okf.is_valid_actor("okf-agent/gemini-2.5-pro"))
    self.assertFalse(validate_okf.is_valid_actor("invalid_actor_format"))

  def test_get_trust_tier(self):
    self.assertEqual(validate_okf.get_trust_tier(None), "unverified")
    self.assertEqual(
        validate_okf.get_trust_tier({"by": "process:bot", "at": "2026-08-21"}),
        "machine-confirmed",
    )
    self.assertEqual(
        validate_okf.get_trust_tier({"by": "human:david", "at": "2026-08-21"}),
        "human-reviewed",
    )

  def test_bundle_validation_valid_bundle(self):
    with tempfile.TemporaryDirectory() as tmpdir:
      tmppath = pathlib.Path(tmpdir)

      # root index.md
      (tmppath / "index.md").write_text(
          '---\nokf_version: "0.2"\n---\n# Root\n* [Concept 1](concepts/c1.md)'
          " - Desc 1\n",
          encoding="utf-8",
      )

      # log.md
      (tmppath / "log.md").write_text(
          "# Log\n\n## 2026-08-21\n* **Creation**: Created concept.\n",
          encoding="utf-8",
      )

      # concepts/ directory
      concepts_dir = tmppath / "concepts"
      concepts_dir.mkdir()
      (concepts_dir / "index.md").write_text(
          "# Concepts\n* [Concept 1](c1.md) - Desc 1\n",
          encoding="utf-8",
      )
      (concepts_dir / "c1.md").write_text(
          "---\ntype: Concept\ntitle: Concept 1\ndescription: Desc"
          " 1\ngenerated: { by: okf-agent/v1, at: 2026-08-21T12:00:00Z"
          " }\n---\n# Concept 1\n",
          encoding="utf-8",
      )

      exit_code = validate_okf.main(str(tmppath))
      self.assertEqual(exit_code, 0)

  def test_escaping_computation_fails(self):
    with tempfile.TemporaryDirectory() as tmpdir:
      tmppath = pathlib.Path(tmpdir)
      (tmppath / "comp.md").write_text(
          "---\ntype: Attested Computation\ntitle: Escaping\nruntime:"
          " python\ncomputation: ../../../etc/passwd\n---\n",
          encoding="utf-8",
      )
      exit_code = validate_okf.main(str(tmppath))
      self.assertEqual(exit_code, 1)

  def test_escaping_directory_link_fails(self):
    with tempfile.TemporaryDirectory() as tmpdir:
      tmppath = pathlib.Path(tmpdir)
      (tmppath / "index.md").write_text(
          "# Root\n* [Escape](../../../)\n",
          encoding="utf-8",
      )
      exit_code = validate_okf.main(str(tmppath))
      self.assertEqual(exit_code, 1)


if __name__ == "__main__":
  unittest.main()
