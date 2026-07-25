"""Guard capture pass — replay a guard over ALREADY-RECORDED agent trajectories.

Produces the JSONL that ``src/analysis/guard_threshold.py`` sweeps. This is the half of the
calibration sweep that touches a model; the sweep itself is pure arithmetic.

WHAT MAKES THIS FREE (for piguard)
-----------------------------------
PIGuard is a stateless text classifier over ONE tool output at a time
(``PromptInjectionDetector.query`` runs ``detect(text)`` per tool message). Nothing about its
verdict depends on the agent's backbone, on the rest of the trajectory, or on the guard's own
earlier decisions. So its verdicts can be recovered from the **no-defense** traces already on
disk — a DeBERTa forward pass per recorded tool output, on CPU, for the whole capability_sweep.
No GPU, no backbone inference, no new experiment run, therefore no experiment-run approval gate.

MELON CANNOT USE THIS PATH. It is behavioral: its cosine similarity is computed against a masked
re-run of the same episode, which does not exist in the stored traces. Capturing MELON scores
means actually running the agent again and IS an experiment run (GPU + $ + time estimate first,
per the repo's approval gate). This module deliberately supports piguard only.

FIDELITY
--------
``score_messages`` reproduces AgentDojo's ``TransformersBasedPIDetector.detect`` exactly:

    safety_score = result["score"] if result["label"] == safe_label else 1 - result["score"]

so the emitted number is a *safety* score on the same scale as the ``threshold`` in
``conf/experiment/agent_injection/defenses.yaml``, and the guard blocks BELOW it. The classifier
is called one message at a time, as the detector does — not batched — so tokenizer padding cannot
shift a score relative to the real run.

Usage
-----
    # validate parsing + carrier location without loading any model
    uv run python -m src.analysis.guard_capture --dry-run

    # the real capture (needs `uv sync --extra classifiers`)
    uv run python -m src.analysis.guard_capture \
        --out outputs/agent_injection/analysis/piguard_capture.jsonl
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any, Iterator, Optional

from src.analysis.guard_threshold import guard_cfg, load_config

REPO = Path(__file__).resolve().parents[2]
DEFAULT_RUNS = REPO / "outputs" / "agent_injection" / "runs"
DEFAULT_OUT = REPO / "outputs" / "agent_injection" / "analysis" / "piguard_capture.jsonl"

# Probe length (characters) used to locate the injection inside a tool output. Long enough to be
# unique against ordinary tool text, short enough to survive an injection that the environment
# truncated. Not a scientific knob — a string-matching detail; its correctness is MEASURED by the
# carrier-coverage number this module prints, which is the thing to watch.
_PROBE_CHARS = 120


# --------------------------------------------------------------------------
# trace parsing
# --------------------------------------------------------------------------
def text_of(message: dict) -> str:
    """Mirror agentdojo's `get_text_content_as_str`: concatenate the text blocks of a message."""
    content = message.get("content")
    if content is None:
        return ""
    if isinstance(content, str):
        return content
    parts = []
    for block in content:
        if isinstance(block, dict) and block.get("type", "text") == "text":
            parts.append(block.get("content") or block.get("text") or "")
        elif isinstance(block, str):
            parts.append(block)
    return "".join(parts)


def _norm(s: str) -> str:
    """Whitespace- and escape-insensitive form, for locating an injection inside a tool output.

    Two distinct formatting mismatches defeat a raw substring test, both verified against real
    traces (2026-07-24):

    1. Traces store injection templates with literal ``\\n`` two-character escapes, while the tool
       output embedding them carries real newlines.
    2. Tool outputs are serialized as YAML (``tool_output_format``), which line-wraps long strings
       with a trailing backslash plus indentation — so ``"...message from me, Emma Johnson, to
       you..."`` appears mid-output as ``"...to\\ \\ you..."``. Without this, the control payload
       ``encoded_plain`` located its carrier in only 28 of 160 episodes.

    Order matters: expand the two-character escapes FIRST, then drop the leftover lone backslashes
    from YAML wrapping. Deleting all backslashes up front would turn ``\\nThis`` into ``nThis``.
    """
    s = s.replace("\\n", " ").replace("\\t", " ").replace("\\r", " ")
    s = s.replace("\\", " ")
    return re.sub(r"\s+", " ", s).strip()


def injection_carriers(injections: dict[str, str], tool_texts: list[str]) -> list[int]:
    """Indices of the tool outputs that embed an injected payload.

    Two probes per injection (head and middle) so a payload the environment truncated is still
    located. Returns sorted unique indices; empty means "could not locate" — the sweep degrades
    that episode to any-message semantics and reports it in the coverage line.
    """
    normed = [_norm(t) for t in tool_texts]
    hits: set[int] = set()
    for raw in injections.values():
        core = _norm(raw or "")
        if not core:
            continue
        probes = [core[:_PROBE_CHARS]]
        if len(core) > 2 * _PROBE_CHARS:
            mid = len(core) // 2
            probes.append(core[mid:mid + _PROBE_CHARS])
        for i, t in enumerate(normed):
            if any(p and p in t for p in probes):
                hits.add(i)
    return sorted(hits)


def iter_traces(runs_dir: Path, arm: Optional[str] = None) -> Iterator[tuple[str, Path, dict]]:
    """Yield (backbone, path, trace) for the NO-DEFENSE arm of every backbone.

    Layout written by ``src/harness/runner.py``:
        runs/<backbone>/<pipeline_name>/<suite>/<user_task>/<attack>/<injection_task>.json
    where ``pipeline_name`` is the bare backbone for the undefended arm and ``<backbone>-<defense>``
    for a defended one. Only the undefended arm is guard-independent, so only it is a valid reuse
    base — reusing a defended arm would score a guard against trajectories that guard already
    shaped.
    """
    for backbone_dir in sorted(p for p in runs_dir.iterdir() if p.is_dir()):
        backbone = backbone_dir.name
        want = arm or backbone
        pipeline_dir = backbone_dir / want
        if not pipeline_dir.is_dir():
            continue
        for path in sorted(pipeline_dir.rglob("*.json")):
            try:
                trace = json.loads(path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError) as exc:
                print(f"  ! unreadable trace {path}: {exc}")
                continue
            yield backbone, path, trace


def episode_id(backbone: str, trace: dict) -> str:
    return "/".join(str(x) for x in (
        backbone, trace.get("suite_name"), trace.get("user_task_id"),
        trace.get("attack_type") or "none", trace.get("injection_task_id") or "none"))


# --------------------------------------------------------------------------
# the guard
# --------------------------------------------------------------------------
class PIGuardScorer:
    """PIGuard as a pure scoring function over tool-output text.

    Loads the same HF model id the experiment ran, with ``trust_remote_code=True`` because
    ``leolee99/PIGuard`` ships custom model code (verified at build time — the stock detector
    silently skipped every PIGuard cell without it). Acceptable for a pinned, published research
    artifact; never point this at an untrusted model id.
    """

    def __init__(self, model_name: str, safe_label: str) -> None:
        import torch
        from transformers import pipeline

        self.safe_label = safe_label
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.pipeline = pipeline(
            "text-classification", model=model_name, device=device, trust_remote_code=True)

    def safety_score(self, text: str) -> float:
        """AgentDojo's safety score for one tool output. Higher = safer; the guard blocks below tau."""
        result: dict[str, Any] = self.pipeline(text)[0]
        score = float(result["score"])
        return score if result["label"] == self.safe_label else 1.0 - score


# --------------------------------------------------------------------------
# driver
# --------------------------------------------------------------------------
def capture(runs_dir: Path, out_path: Path, cfg: dict, *, dry_run: bool = False) -> dict:
    g = guard_cfg("piguard", cfg)
    scorer = None if dry_run else PIGuardScorer(g["hf_model"], g["safe_label"])

    out_path.parent.mkdir(parents=True, exist_ok=True)
    stats = {"episodes": 0, "benign": 0, "attack": 0, "messages": 0,
             "carrier_located": 0, "carrier_missing": 0,
             # The load-bearing pair: ASR can only ever count successful attacks, so carrier
             # coverage AMONG SUCCESSES is what decides whether the safety axis is faithful.
             "successful_attacks": 0, "successful_with_carrier": 0,
             "score_errors": 0}
    missing: list[str] = []

    with out_path.open("w", encoding="utf-8") as fh:
        for backbone, path, trace in iter_traces(runs_dir):
            tool_texts = [text_of(m) for m in trace.get("messages", [])
                          if m.get("role") == "tool"]
            attack_type = trace.get("attack_type")
            kind = "attack" if attack_type else "benign"
            injections = trace.get("injections") or {}
            carriers = injection_carriers(injections, tool_texts) if kind == "attack" else []

            scores: list[float] = []
            if scorer is not None:
                for t in tool_texts:
                    try:
                        scores.append(scorer.safety_score(t))
                    except Exception as exc:  # noqa: BLE001 - record, never silently drop
                        stats["score_errors"] += 1
                        print(f"  ! scoring failed ({path.name}): {type(exc).__name__}: {exc}")
                        # Fail CLOSED for a broken verdict: a message we could not score must not
                        # look safe. 0.0 safety = always blocked, for a guard that blocks below tau.
                        scores.append(0.0)
            else:
                scores = [0.0] * len(tool_texts)

            rec = {
                "id": episode_id(backbone, trace),
                "guard": "piguard",
                "backbone": backbone,
                "kind": kind,
                "suite": trace.get("suite_name", "workspace"),
                "user_task": trace.get("user_task_id"),
                "injection_task": trace.get("injection_task_id"),
                "payload": attack_type,
                "message_scores": scores,
                "injection_indices": carriers,
                "security": bool(trace.get("security", False)),
                "utility": bool(trace.get("utility", False)),
            }
            fh.write(json.dumps(rec) + "\n")

            stats["episodes"] += 1
            stats[kind] += 1
            stats["messages"] += len(tool_texts)
            if kind == "attack":
                if carriers:
                    stats["carrier_located"] += 1
                else:
                    stats["carrier_missing"] += 1
                    if rec["security"] and len(missing) < 10:
                        missing.append(rec["id"])
                if rec["security"]:
                    stats["successful_attacks"] += 1
                    stats["successful_with_carrier"] += 1 if carriers else 0

    if missing:
        print("\n  !! injection carrier NOT located in these SUCCESSFUL attacks (up to 10) — "
              "these fall back to any-message semantics and make the curve pessimistic:")
        for m in missing:
            print(f"    {m}")
    return stats


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--runs-dir", type=Path, default=DEFAULT_RUNS)
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
    ap.add_argument("--dry-run", action="store_true",
                    help="parse traces and locate injection carriers WITHOUT loading the model")
    args = ap.parse_args()

    cfg = load_config()
    print(f"capturing piguard over {args.runs_dir} (dry_run={args.dry_run})")
    stats = capture(args.runs_dir, args.out, cfg, dry_run=args.dry_run)
    print("\n=== capture summary ===")
    for k, v in stats.items():
        print(f"  {k:18} {v}")
    cov = stats["carrier_located"] / stats["attack"] if stats["attack"] else 0.0
    print(f"  carrier coverage   {100 * cov:.1f}% (all attack episodes)")
    n_ok, n_s = stats["successful_with_carrier"], stats["successful_attacks"]
    sc = n_ok / n_s if n_s else 1.0
    print(f"  CARRIER COVERAGE AMONG SUCCESSFUL ATTACKS: {n_ok}/{n_s} = {100 * sc:.1f}%"
          + ("   <-- safety axis is faithful" if n_ok == n_s
             else "   <-- safety axis degrades to any-message for the rest"))
    print(f"  wrote {args.out}")


if __name__ == "__main__":
    main()
