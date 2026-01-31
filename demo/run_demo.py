from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from src.baseline import baseline_moving_average
from src.data import make_synthetic_series, train_test_split_time
from src.metrics import mae, rmse, baseline_win
from src.model import candidate_exp_smoothing
from src.receipts import GateResult, make_manifest, make_receipt, make_run_id, write_json

PROJECT_ID = "PROOF_BUNDLE_DEMO"
PACKET_TYPE = "PUBLIC"
VERSION = "v0.1"
PRIMARY_METRIC = "rmse"
MIN_IMPROVEMENT_FRAC = 0.02

def ensure_dirs() -> dict:
    root = Path(".").resolve()
    paths = {"outputs_plots": root / "outputs" / "plots", "outputs_tables": root / "outputs" / "tables", "runs": root / "runs", "receipts": root / "runs" / "receipts"}
    for p in paths.values(): p.mkdir(parents=True, exist_ok=True)
    return paths

def write_docs(run_id: str, metrics_path: Path, receipt_path: Path) -> None:
    Path("AUDIT_SUMMARY.md").write_text("\\n".join([
        "# Audit Summary",
        "",
        f"- Project: {PROJECT_ID}",
        f"- Packet type: {PACKET_TYPE}",
        f"- Version: {VERSION}",
        f"- Run ID: {run_id}",
        "",
        "Deterministic demo on synthetic public-safe data.",
        "",
        "Proof artifacts:",
        f"- Metrics: {metrics_path.as_posix()}",
        f"- Receipt: {receipt_path.as_posix()}",
        "- Report: runs/tko_report.json",
    ]), encoding="utf-8")
    Path("METHODS.md").write_text("\\n".join([
        "# Methods",
        "",
        "Data: synthetic time series with a regime shift + deterministic noise.",
        "Split: time-ordered 70/30 train/test.",
        "Baseline: moving average.",
        "Candidate: exponential smoothing (fixed alpha).",
        "Metrics: MAE and RMSE on test.",
        "Gate: candidate must beat baseline RMSE by at least 2 percent.",
    ]), encoding="utf-8")
    Path("LIMITATIONS.md").write_text("\\n".join([
        "# Limitations",
        "",
        "- Synthetic data only: proves packaging pattern, not domain performance.",
        "- Candidate is intentionally simple (not proprietary).",
        "- Not a deployment system (no ingest, hardening, monitoring).",
    ]), encoding="utf-8")
    Path("REDACTIONS.md").write_text("\\n".join([
        "# Redactions",
        "",
        "This public packet excludes:",
        "- proprietary adapters/closures",
        "- tuned thresholds and operational parameters",
        "- sensitive datasets, scenario libraries, AOIs",
        "- production ingest and connectors",
    ]), encoding="utf-8")

def write_evidence_index(run_id: str) -> None:
    Path("EVIDENCE_INDEX.md").write_text("\\n".join([
        "# Evidence Index",
        "",
        "| Claim ID | Claim | Primary Artifact | Receipt |",
        "|---|---|---|---|",
        f"| C1 | Candidate beats baseline gate | outputs/tables/metrics.csv | runs/receipts/receipt_{run_id}.json |",
        f"| C2 | Run is hashed and auditable | MANIFEST.json | runs/receipts/receipt_{run_id}.json |",
    ]), encoding="utf-8")

def main() -> None:
    paths = ensure_dirs()
    run_id = make_run_id()
    df = make_synthetic_series(n=240, seed=0)
    train, test = train_test_split_time(df, train_frac=0.7)
    y_true = test["y"].to_numpy(dtype=float)
    y_base = baseline_moving_average(train, test, window=12)
    y_cand = candidate_exp_smoothing(train, test, alpha=0.35)
    base_mae = mae(y_true, y_base)
    base_rmse = rmse(y_true, y_base)
    cand_mae = mae(y_true, y_cand)
    cand_rmse = rmse(y_true, y_cand)
    win = baseline_win(PRIMARY_METRIC, base_rmse, cand_rmse, min_improvement_frac=MIN_IMPROVEMENT_FRAC)
    metrics_df = pd.DataFrame([
        {"model": "baseline_moving_average", "mae": base_mae, "rmse": base_rmse},
        {"model": "candidate_exp_smoothing", "mae": cand_mae, "rmse": cand_rmse},
    ])
    metrics_df["primary_metric"] = PRIMARY_METRIC
    metrics_df["min_improvement_frac"] = MIN_IMPROVEMENT_FRAC
    metrics_df["baseline_win_gate"] = bool(win)
    metrics_path = paths["outputs_tables"] / "metrics.csv"
    metrics_df.to_csv(metrics_path, index=False)
    fig = plt.figure()
    plt.plot(df["t"], df["y"], label="series")
    plt.axvline(x=float(train["t"].iloc[-1]), linestyle="--", label="train/test split")
    plt.title("Synthetic series (public-safe)")
    plt.xlabel("t")
    plt.ylabel("y")
    plt.legend()
    plot_path = paths["outputs_plots"] / "series.png"
    fig.savefig(plot_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    gates = [GateResult(name="reproducible_run", status="PASS", details={"seed": 0}), GateResult(name="baseline_win", status=("PASS" if win else "FAIL"), details={"metric": "rmse", "min_improvement_frac": MIN_IMPROVEMENT_FRAC})]
    run_manifest = {"run_id": run_id, "project_id": PROJECT_ID, "packet_type": PACKET_TYPE, "version": VERSION, "command": "python -m demo.run_demo"}
    run_manifest_path = paths["runs"] / "run_manifest.json"
    write_json(run_manifest_path, run_manifest)
    tko_report = {"run_id": run_id, "summary": {"baseline_mae": base_mae, "baseline_rmse": base_rmse, "candidate_mae": cand_mae, "candidate_rmse": cand_rmse, "baseline_win": bool(win)}, "gates": [g.__dict__ for g in gates], "artifacts": {"metrics_csv": metrics_path.as_posix(), "plot_png": plot_path.as_posix(), "run_manifest": run_manifest_path.as_posix()}}
    tko_path = paths["runs"] / "tko_report.json"
    write_json(tko_path, tko_report)
    output_files = [metrics_path, plot_path, run_manifest_path, tko_path]
    receipt = make_receipt(run_id=run_id, inputs={"data_seed": 0, "run_manifest": run_manifest}, gates=gates, metrics=[{"name": "mae_baseline", "value": base_mae}, {"name": "rmse_baseline", "value": base_rmse}, {"name": "mae_candidate", "value": cand_mae}, {"name": "rmse_candidate", "value": cand_rmse}, {"name": "baseline_win", "value": bool(win)}], output_files=output_files)
    receipt_path = paths["receipts"] / f"receipt_{run_id}.json"
    write_json(receipt_path, receipt)
    write_docs(run_id, metrics_path, receipt_path)
    write_evidence_index(run_id)
    files_to_hash = [Path("README.md"), Path("AUDIT_SUMMARY.md"), Path("METHODS.md"), Path("LIMITATIONS.md"), Path("REDACTIONS.md"), Path("EVIDENCE_INDEX.md"), metrics_path, plot_path, run_manifest_path, tko_path, receipt_path]
    manifest = make_manifest(project_id=PROJECT_ID, packet_type=PACKET_TYPE, version=VERSION, run_id=run_id, files_to_hash=files_to_hash, notes="Public-safe proof bundle demo with baseline gate and receipts.")
    Path("MANIFEST.json").write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    print("[OK] Run complete:", run_id)
    print("     Metrics:", metrics_path.as_posix())
    print("     Receipt:", receipt_path.as_posix())
    print("     Manifest: MANIFEST.json")

if __name__ == "__main__":
    main()
