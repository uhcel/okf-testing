---
type: Attested Computation
title: Run Backend Test Suite
description: Blessed computation for executing backend pytest test suite with coverage report.
status: stable
runtime: bash
parameters:
  - { name: extra_args, type: string, required: false }
executor:
  resource: baseline_repo/backend/scripts/test.sh
  receipt: [exit_code, stdout, coverage_percentage]
attester:
  resource: /references/attesters/exit_code_zero.py
generated:
  by: okf-agent/gemini-2.5-pro
  at: 2026-09-16T13:14:03Z
verified:
  - by: human:leszekw
    at: 2026-09-16T13:20:00Z
sources:
  - id: test-script
    resource: baseline_repo/backend/scripts/test.sh
    title: Test Runner Script
    author: human:tiangolo
    last_modified: 2026-08-01T00:00:00Z
---

# Computation

```bash
FASTAPI_ENV=development coverage run -m pytest tests/
coverage report
coverage html --title "coverage"
```

The script executes all Pytest tests in the backend repository and asserts exit code 0[^test-script].

[^test-script]: baseline_repo/backend/scripts/test.sh
