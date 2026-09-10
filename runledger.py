"""Append and verify hash-linked experiment records."""
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

GENESIS = "0" * 64


def digest(record: dict) -> str:
    unsigned = {key: value for key, value in record.items() if key != "sha256"}
    data = json.dumps(unsigned, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(data.encode()).hexdigest()


def read(path: Path) -> list[dict]:
    if not path.exists():
        return []
    records = []
    for number, line in enumerate(path.read_text("utf-8").splitlines(), 1):
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError as error:
            raise ValueError(f"invalid JSON on line {number}") from error
    return records


def verify(path: Path) -> tuple[bool, str]:
    previous = GENESIS
    for number, record in enumerate(read(path), 1):
        if record.get("previous_sha256") != previous:
            return False, f"line {number}: previous hash mismatch"
        if record.get("sha256") != digest(record):
            return False, f"line {number}: record hash mismatch"
        previous = record["sha256"]
    return True, f"valid chain with {len(read(path))} records"


def append(path: Path, run_id: str, status: str, metrics: dict) -> dict:
    records = read(path)
    if any(record.get("run_id") == run_id for record in records):
        raise ValueError(f"run_id already exists: {run_id}")
    valid, reason = verify(path)
    if not valid:
        raise ValueError(reason)
    record = {"run_id": run_id, "status": status, "metrics": metrics,
              "recorded_utc": datetime.now(timezone.utc).isoformat(),
              "previous_sha256": records[-1]["sha256"] if records else GENESIS}
    record["sha256"] = digest(record)
    with path.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(record, sort_keys=True) + "\n")
    return record


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    add = sub.add_parser("append")
    add.add_argument("ledger", type=Path); add.add_argument("run_id"); add.add_argument("status")
    add.add_argument("--metrics", default="{}", help="JSON object")
    check = sub.add_parser("verify"); check.add_argument("ledger", type=Path)
    args = parser.parse_args()
    if args.command == "append":
        metrics = json.loads(args.metrics)
        if not isinstance(metrics, dict):
            parser.error("--metrics must be a JSON object")
        print(json.dumps(append(args.ledger, args.run_id, args.status, metrics), indent=2))
    else:
        valid, message = verify(args.ledger)
        print(message)
        raise SystemExit(0 if valid else 1)
