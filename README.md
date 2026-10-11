# RunLedger

A tiny append-only log for experiment summaries. Each JSON record contains the
hash of the previous record, so later edits or reordered lines are detectable.

```powershell
python runledger.py append ledger.jsonl run-001 complete --metrics '{"accuracy":0.82}'
python runledger.py verify ledger.jsonl
python -m pytest
```

The ledger is evidence of internal consistency, not proof that an experiment
really happened. Someone who can rewrite the whole file can also rebuild every
hash. For stronger provenance, publish the latest hash somewhere independently
or sign it with a protected key.

The [integrity and threat-model guide](docs/INTEGRITY_AND_THREAT_MODEL.md)
explains the record format, verification behaviour and ways to anchor a hash.

Main idea to explain: each record commits to both its own content and the
previous record. Changing one item breaks the chain from that point onward.
