# RunLedger: integrity model and practical limits

RunLedger records experiment summaries as a **hash-linked JSON Lines chain**.
It detects many local edits or reorderings provided that the expected chain
tip is preserved elsewhere. It does **not** prove that experiments happened,
that metrics are true, or that someone did not rewrite the entire file.

## Quick start

```bash
python runledger.py append ledger.jsonl run-001 complete --metrics '{"accuracy":0.82}'
python runledger.py append ledger.jsonl run-002 failed --metrics '{}'
python runledger.py verify ledger.jsonl
python -m pytest
```

The `--metrics` option requires a JSON **object**. Quoting is shell-specific;
see the [README](../README.md) for the PowerShell example. Each `run_id`
must be unique in the currently read file.

## Record format

| Field | Meaning |
| --- | --- |
| `run_id` | Caller-supplied unique run label |
| `status` | Caller-supplied status; no fixed enumeration is enforced |
| `metrics` | Caller-supplied JSON object |
| `recorded_utc` | Local computer clock expressed in UTC |
| `previous_sha256` | Previous record's stored hash; 64 zeroes for the first |
| `sha256` | SHA-256 digest of the current record without this field |

`digest()` serialises the unsigned object using `json.dumps` with
`sort_keys=True`, separators `(",", ":")` and `ensure_ascii=False`,
then hashes the resulting UTF-8 bytes. Each new record therefore
contains a commitment to its fields and to the previous link.

`verify()` walks the chain, checking each predecessor and recalculating
its digest. A changed metric without corresponding rewritten hashes
fails verification. The included tests cover a valid chain, a modified
metric and duplicate run-ID rejection.

## Important verification edge cases

- The CLI returns **0** when the chain verifies, and **1** when the chain
  explicitly fails a link or digest check. Invalid JSON can instead raise
  a Python exception with a nonzero exit status.
- **A nonexistent file verifies as an empty valid chain.** `read()`
  returns `[]` for a missing path. A successful `verify` command is
  therefore *not proof that any run was recorded*. Independently check
  file existence and expected record count.
- Append prevents duplicate `run_id` values using the records available
  at append time. Verification does **not** independently validate ID
  uniqueness, timestamps or experiment schemas.
- The timestamp comes from the local clock. This is not trusted
  timestamping, and the ledger contains no signatures.
- The file is written using a simple append call. There is no file
  locking, transaction protocol or fsync guarantee. Avoid multiple
  writers to the same path and preserve backups.

## Threats and unsupported guarantees

| Threat | Current detection | Stronger control |
| --- | --- | --- |
| Accidental change to a saved metric | Hash mismatch, unless subsequent chain rewritten | Retain external tip |
| Remove or reorder middle rows | Broken hash link, unless entire chain rebuilt | External tip and expected count |
| Rewrite all rows and recalculate every hash | Not detected | Digitally sign and externally anchor the final digest |
| Fabricate a run or metric | Not detected | Hash and independently inspect primary evidence |
| Delete the file entirely | Not detected as failure (empty chain accepted) | Require expected file/count |
| Concurrent append or partial write | No robustness guarantee | Exclusive lock and atomic durable storage |
| Falsify local clock | Not detected | Trusted time source |

This code uses cryptographic *hashes*, not a cryptographic *signature*.
Anyone with access to rewrite the full file can recompute a
self-consistent chain.

## Suggested evidence workflow (not built in)

1. Save the raw evaluation outputs and calculate a SHA-256 hash for
   each artifact in a separate verification step.
2. Record artifact hashes and run settings in the `metrics` object or
   an attached manifest; the utility will not calculate these for you.
3. Append the run summary, then save its final `sha256` and expected
   record count **outside the ledger's writable boundary**.
4. When auditing, verify the chain, check the independently stored
   tip and count, and recompute hashes of the actual result artifacts.

An independently controlled, signed release or transparency log is
stronger than placing the tip next to the ledger in the same mutable
repository. Even an externally anchored hash cannot establish that
the recorded experimental claim is factually correct.

## Wording for a portfolio

Supported: "Built a Python append-only experiment log using SHA-256
hash links, duplicate-ID checks and verifiable JSONL records."

Unsupported: "tamper-proof provenance", "proof of research execution"
or "production-compliant audit system".

