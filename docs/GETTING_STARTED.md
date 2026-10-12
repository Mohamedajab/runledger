# Getting started with RunLedger

Run the commands below from the repository root. Python 3.11 or newer is
required. The CLI uses only the Python standard library; `pytest` is needed
only to run the tests. There is no database, API key or hosted service to configure.

## Set up a development environment

On Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install pytest
.\.venv\Scripts\python.exe -m pytest
```

On macOS or Linux:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install pytest
.venv/bin/python -m pytest
```

Activation is optional. Use the virtual environment's Python path in place of
`python` in the following examples if it is not activated.

## Record and verify a small experiment

Use a fresh file path for this example:

```bash
python runledger.py append demo-ledger.jsonl demo-001 complete
python runledger.py append demo-ledger.jsonl demo-002 failed
python runledger.py verify demo-ledger.jsonl
```

Each append prints the stored record as JSON. With no `--metrics` argument,
the metrics object is empty. Verification prints `valid chain with 2 records`
and exits with status 0. The output hashes and timestamps vary between runs.

For metric values, see the JSON-object example in the [README](../README.md).
Run `python runledger.py --help` or `python runledger.py append --help` for
the argument list. Status labels are supplied by the caller, not a fixed set.

## Troubleshooting

- **Duplicate run ID:** use a new ID for a new run. Repeating this example
  against the same file rejects `demo-001`; it does not overwrite the old record.
- **Invalid JSON or non-object metrics:** `--metrics` must contain a JSON
  object. Arrays, scalar values and malformed JSON are not accepted. Shell
  quoting varies, particularly between older Windows PowerShell and PowerShell 7.
- **Missing directory:** create the ledger's parent directory first. Append
  creates the file but does not create parent directories.
- **Hash mismatch:** preserve the failed file for investigation. Do not edit
  records or rebuild the chain merely to make verification succeed.
- **Missing ledger still verifies:** an absent file is treated as an empty
  chain. Check file existence and the expected record count separately.

Verification is an internal-consistency check, not a signature or proof that
an experiment happened. Read the [integrity guide](INTEGRITY_AND_THREAT_MODEL.md)
before relying on it for provenance. Use one writer per ledger; concurrent
writes and durable storage are not implemented.
