from __future__ import annotations

import json
import os
import platform
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from .hashing import sha256_file, sha256_text


@dataclass(frozen=True)
class GateResult:
    name: str
    status: str
    details: Optional[Dict[str, Any]] = None


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def make_run_id(prefix: str = "RUN") -> str:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    return f"{prefix}_{stamp}"


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True), encoding="utf-8")


def env_fingerprint() -> Dict[str, Any]:
    return {
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "executable": sys.executable,
        "cwd": os.getcwd(),
    }


def compute_hashes(paths: List[Path]) -> Dict[str, str]:
    out: Dict[str, str] = {}
    for p in paths:
        if p.exists() and p.is_file():
            out[p.as_posix()] = sha256_file(p)
    return out


def make_receipt(run_id: str, inputs: Dict[str, Any], gates: List[GateResult], metrics: List[Dict[str, Any]], output_files: List[Path]) -> Dict[str, Any]:
    return {
        "run_id": run_id,
        "created_utc": utc_now_iso(),
        "inputs": inputs,
        "gates": [g.__dict__ for g in gates],
        "metrics": metrics,
        "outputs_sha256": compute_hashes(output_files),
        "env": env_fingerprint(),
    }


def make_manifest(project_id: str, packet_type: str, version: str, run_id: str, files_to_hash: List[Path], notes: str = "") -> Dict[str, Any]:
    file_hashes = compute_hashes(files_to_hash)
    return {
        "packet": {
            "project_id": project_id,
            "type": packet_type,
            "version": version,
            "generated_utc": utc_now_iso(),
            "notes": notes,
        },
        "run_id": run_id,
        "files_sha256": file_hashes,
        "manifest_sha256": sha256_text(json.dumps(file_hashes, sort_keys=True)),
    }
