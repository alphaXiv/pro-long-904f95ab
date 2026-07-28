#!/usr/bin/env python3
"""Run one fixed-budget PRO-LONG condition or emit an explicit setup gate."""

from __future__ import annotations

import glob
import hashlib
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONFIG = json.loads((ROOT / "reproduction" / "config.json").read_text())
START = time.time()


def audit_release() -> dict:
    """Integrity/shape audit of the sanitized release; never fresh evidence."""
    scorecards = sorted(
        glob.glob(str(ROOT / "release_logs/fable5/fable_online/*/rep1/scorecard.json"))
    )
    trajectory_files = sorted(
        glob.glob(str(ROOT / "release_logs/fable5/fable_online/*/rep1/logs.txt"))
    )
    analyzer_files = sorted(
        glob.glob(
            str(ROOT / "release_logs/fable5/fable_online/*/rep1/logs_analyzer.txt")
        )
    )
    scores: list[float] = []
    levels = actions = 0
    retrieval = {"grep_mentions": 0, "python_mentions": 0, "log_mentions": 0}
    digest = hashlib.sha256()
    for path in scorecards:
        raw = Path(path).read_bytes()
        digest.update(raw)
        data = json.loads(raw)
        scores.append(float(data["score"]))
        levels += int(data.get("total_levels_completed") or 0)
        actions += int(data.get("total_actions") or 0)
    for path in analyzer_files:
        text = Path(path).read_text(errors="replace")
        retrieval["grep_mentions"] += len(re.findall(r"\bgrep\b|regex", text, re.I))
        retrieval["python_mentions"] += len(re.findall(r"\bpython(?:3)?\b", text, re.I))
        retrieval["log_mentions"] += len(re.findall(r"logs\.txt", text, re.I))
    return {
        "label": "released-log-audit-not-reproduction",
        "scorecard_files": len(scorecards),
        "trajectory_files": len(trajectory_files),
        "analyzer_files": len(analyzer_files),
        "mean_score": round(sum(scores) / len(scores), 4) if scores else None,
        "levels_completed_sum": levels,
        "actions_sum": actions,
        "retrieval_mentions": retrieval,
        "scorecard_sha256": digest.hexdigest(),
    }


def arc_key_works(key: str) -> tuple[bool, str]:
    request = urllib.request.Request(
        "https://three.arcprize.org/api/games",
        headers={"X-API-Key": key, "Accept": "application/json"},
    )
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            return response.status == 200, f"http-{response.status}"
    except urllib.error.HTTPError as exc:
        return False, f"http-{exc.code}"
    except Exception as exc:  # network errors are reported without secret material
        return False, f"{type(exc).__name__}"


def condition_args() -> list[str]:
    args = [
        sys.executable,
        "-m",
        "prolong_agent.agent.swarm",
        "--game",
        ",".join(CONFIG["games"]),
        "--max-actions",
        str(CONFIG["max_actions"]),
        "--backend",
        "codex",
        "--model",
        CONFIG["model"],
        "--reasoning-effort",
        CONFIG["reasoning_effort"],
        "--action-cap",
        str(CONFIG["action_cap"]),
        "--retries",
        str(CONFIG["analyzer_retries"]),
        "--grid-mode",
        CONFIG["grid_mode"],
        "--workspace",
        CONFIG["workspace"],
        "--operation-mode",
        "online",
        "--note",
        f"fresh-recovery-{CONFIG['condition']}",
    ]
    if CONFIG["log_window"] is not None:
        args.extend(["--log-window", str(CONFIG["log_window"])])
    return args


def main() -> int:
    print("PROTOCOL=" + json.dumps(CONFIG, sort_keys=True), flush=True)
    audit = audit_release()
    print("RELEASE_AUDIT=" + json.dumps(audit, sort_keys=True), flush=True)

    missing = [
        name for name in ("ARC_API_KEY", "OPENAI_API_KEY") if not os.getenv(name)
    ]
    arc_ok, arc_status = (
        arc_key_works(os.environ["ARC_API_KEY"])
        if "ARC_API_KEY" not in missing
        else (False, "not-set")
    )
    if not arc_ok and "ARC_API_KEY" not in missing:
        missing.append("ARC_API_KEY(valid)")

    if missing:
        result = {
            "evidence_kind": "kubernetes-setup-gate",
            "status": "blocked",
            "condition": CONFIG["condition"],
            "missing": missing,
            "arc_preflight": arc_status,
            "fresh_arc_episodes": 0,
            "elapsed_seconds": round(time.time() - START, 3),
            "note": "Released-log audit is provenance checking, not reproduction evidence.",
        }
        print("REPRODUCTION_RESULT=" + json.dumps(result, sort_keys=True), flush=True)
        return 0

    args = condition_args()
    print("ONLINE_COMMAND=" + json.dumps(args), flush=True)
    completed = subprocess.run(args, cwd=ROOT, check=False)
    result = {
        "evidence_kind": "fresh-online-arc-agi-3",
        "status": "completed" if completed.returncode == 0 else "failed",
        "condition": CONFIG["condition"],
        "returncode": completed.returncode,
        "fresh_arc_episodes": len(CONFIG["games"]),
        "elapsed_seconds": round(time.time() - START, 3),
    }
    print("REPRODUCTION_RESULT=" + json.dumps(result, sort_keys=True), flush=True)
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
