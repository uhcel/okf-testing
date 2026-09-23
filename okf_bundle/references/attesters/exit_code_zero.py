#!/usr/bin/env python3
"""Deterministic attester for receipt exit code verification."""
import sys
import json

def verify_receipt(receipt_path: str) -> bool:
    with open(receipt_path, "r") as f:
        data = json.load(f)
    return data.get("exit_code") == 0

if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(1)
    success = verify_receipt(sys.argv[1])
    sys.exit(0 if success else 1)
