import json
from pathlib import Path
import pytest
from runledger import append, verify


def test_chain_verifies(tmp_path: Path):
    path = tmp_path / "runs.jsonl"
    append(path, "run-1", "complete", {"f1": 0.72})
    append(path, "run-2", "failed", {})
    assert verify(path) == (True, "valid chain with 2 records")


def test_tampering_is_detected(tmp_path: Path):
    path = tmp_path / "runs.jsonl"
    append(path, "run-1", "complete", {"f1": 0.72})
    record = json.loads(path.read_text())
    record["metrics"]["f1"] = 0.99
    path.write_text(json.dumps(record) + "\n")
    assert verify(path)[0] is False


def test_duplicate_run_id_is_rejected(tmp_path: Path):
    path = tmp_path / "runs.jsonl"
    append(path, "run-1", "complete", {})
    with pytest.raises(ValueError, match="already exists"):
        append(path, "run-1", "complete", {})
