# Proof Bundle Demo (public-safe)

This repo demonstrates a grant-friendly packaging pattern:
- baseline vs candidate comparison
- one-command replay
- auditable receipts (hashes + gate results)
- explicit limitations + redactions

This is NOT the secret sauce. It uses synthetic data and simple models.

## Quickstart

```bash
pip install -r requirements.txt
python -m demo.run_demo
```

## Outputs (created after the run)
- outputs/tables/metrics.csv
- outputs/plots/series.png
- runs/run_manifest.json
- runs/tko_report.json
- runs/receipts/receipt_<RUN_ID>.json
- MANIFEST.json
- EVIDENCE_INDEX.md
- AUDIT_SUMMARY.md / METHODS.md / LIMITATIONS.md / REDACTIONS.md

Generated artifacts are ignored by git by default (see .gitignore).
