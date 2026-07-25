# Guard-threshold calibration — PIGuard (Paper E, `agent_injection`)

**Status:** done 2026-07-24 · **Cost: $0, no GPU, no new experiment run** (offline CPU replay over
traces already on disk, so the experiment-run approval gate does not apply).
**Scope: PIGuard only.** MELON is behavioral and cannot be replayed — see §6.

Answers the standing reviewer objection against any defense reported at a single operating point:
*"is this defense only sufficient because you set its threshold strict enough?"* The
`capability_sweep` result reported PIGuard as blocking attack **b** (`tooldecode_base64`) at
ASR = 0, measured at one threshold (0.5). This traces the whole curve instead.

Tooling: `src/analysis/guard_capture.py` (replay) + `src/analysis/guard_threshold.py` (sweep),
config `conf/analysis/guard_threshold.yaml`. Both COPIED from the sibling repo
(`imaging_text_attacks_for_llm_jailbreaking`, commit `25692f6`) and adapted — copy, not a
dependency, per the ecosystem charter.

---

## 1. Headline findings

**(1) The PIGuard result is not a threshold artifact.** Every one of the 409 injection-carrying
tool outputs scores a *safety* score ≤ **0.0173** (median 0.0001) — the classifier is
near-maximally confident. The shipped threshold 0.5 therefore sits about **28× above** the worst-
detected injection, and ASR is 0 for all three payloads at **every** threshold ≥ 0.02, on all four
backbones. The defense claim survives calibration.

**(2) But the shipped threshold is needlessly strict, and costs free utility.** Because injections
are detected with such margin, the threshold can be lowered far below 0.5 while still blocking
100% of injections — and doing so recovers all the benign utility PIGuard currently destroys:

| backbone | retention @ shipped τ=0.5 | zero-ASR band with full utility | gain |
|---|---|---|---|
| qwen2.5-7b | 88.9% | τ ∈ [0.02, 0.38] → 100% | +11.1 pp |
| qwen2.5-14b | 87.5% | τ ∈ [0.02, 0.34] → 100% | +12.5 pp |
| qwen2.5-32b | 88.9% | τ ∈ [0.02, 0.28] → 100% | +11.1 pp |
| qwen2.5-72b | 91.7% | τ ∈ [0.02, 0.40] → 100% | +8.3 pp |

(Retention = benign task utility as a fraction of the same backbone's no-defense benign utility.)

**(3) The utility cost is driven by false positives on ordinary tool output.** 11% of benign tool
outputs score below 0.5 and get redacted, versus 0% of injections scoring above 0.018 — the two
distributions are almost disjoint, so the operating point is the only thing standing between
"free defense" and "8–12 pp utility tax".

**(4) Consequence for the paper.** The defense-claim reframe (TODO item 1, next step (c)) can now
say something sharper than "PIGuard catches b": *a tool-output classifier catches the tool-decode
payload with near-total margin, and the residual cost of deploying it is a calibration choice, not
a detection limit.* This strengthens the surface-form-vs-behavioral story rather than weakening it:
b evades **prompt-level** spotlighting precisely because the payload is not in the prompt — and is
caught by a classifier that reads the tool output where the payload actually lives.

---

## 2. Method

For a threshold τ, an injected action counts as completed iff *the guard passes the injected
content at τ* **and** *the agent completed the injected action*. The second conjunct is
guard-independent, so it is reused from the **no-defense** arm already on disk. Sweeping then needs
only a guard-only replay — a DeBERTa forward pass per recorded tool output.

Two adaptations vs. the sibling's prompt-level version, both load-bearing:

- **The threshold axis is the guard's own knob, in its own direction.** AgentDojo's
  `TransformersBasedPIDetector` computes a *safety* score and flags when `safety_score < threshold`
  (blocks **below** τ); MELON flags when `cosine > threshold` (blocks **above** τ). A single
  normalized "severity" axis would silently invert one of them, so direction is declared per guard
  in config and never inferred.
- **The safety axis tests the injection-carrying message specifically.** With
  `raise_on_injection=False` (what `src/defenses/factory.py` builds), a flagged tool output is
  *redacted*, not aborted — so redacting some *other* message does not neutralize the injection.
  The capture pass locates the carrier by normalized substring match.

Corpus: 536 no-defense episodes (480 attack, 56 benign) across 4 backbones, 1,090 scored tool
outputs, 0 scoring errors.

---

## 3. Validation against the real run

The replay was checked against the actual PIGuard-arm traces from `capability_sweep`:

- **Safety axis — exact.** Predicted ASR at τ=0.5 matches the measured PIGuard-arm ASR in **all 12
  (backbone × payload) cells**. Weak evidence on its own, since both sides are 0 everywhere.
- **Carrier location — complete where it counts.** All **50/50** successful attacks have a located
  carrier, so the safety axis never falls back to coarser any-message semantics. (Raw coverage over
  *all* attack episodes is 77%; the uncovered 110 are episodes whose attack already failed — 61 of
  them never called a tool at all — and contribute 0 to ASR at every threshold.)
- **Utility axis — close, and biased in the documented direction.** Predicted benign utility at
  τ=0.5 vs. measured: 14b 0.500/0.571, 32b 0.571/0.643, 72b 0.786/0.786, 7b 0.571/0.714. The
  prediction is never *above* the truth, as expected: an episode is counted broken if any tool
  output is redacted, but redaction does not always break the task. **Reported utility cost is an
  upper bound.**
- **The approximation is bracketed, and the truth sits at the faithful end.** Running the sweep
  under both aggregation rules brackets ASR(b) at τ=0.5 on 72B: `any_message` → 0.000,
  `first_only` → 0.125. The measured run is 0.000, i.e. exactly the `any_message` end. So the
  bracket contains the truth, and the gap (12.5 pp) is an upper bound on how much the reuse
  approximation could ever have mattered here. It also shows the injection carrier is frequently
  *not* the first tool output — which is why the carrier-locating safety axis (§2) is worth having
  rather than just testing message 0.

---

## 4. Caveats

- Pilot-grade throughout: 40 attack episodes per (backbone, payload) cell, and only **14 benign
  episodes** per backbone — the utility axis is the thin one, and a 1-episode change moves
  retention by ~7 pp. The retention table should be read as a direction, not a precise number.
- Workspace suite only; the cross-suite breadth run (TODO item 1, next step (b)) has not happened.
- The replay reuses no-defense trajectories. A genuinely defended run can diverge after its first
  redaction, so late tool outputs in a reused trajectory may be ones a defended run would never
  have produced. The safety axis is insulated (the carrier is reached before divergence); the
  utility axis is not, which is the other reason it is a bound.
- **Before quoting a specific lowered threshold in the paper, run PIGuard once at that τ for real.**
  This analysis *sites* that run; it does not replace it.

---

## 5. Reproducing

```bash
uv sync --extra classifiers            # torch + transformers (kept out of the base install)
uv run python -m src.analysis.guard_capture          # replay -> capture JSONL  (add --dry-run to
                                                     # validate parsing without loading the model)
uv run python -m src.analysis.guard_threshold \
    --json-out outputs/agent_injection/analysis/piguard_curves.json
```

Artifacts (gitignored, under `outputs/agent_injection/analysis/`): `piguard_capture.jsonl` (per-
episode scores + reused labels), `piguard_curves.json` (full curves for the paper's figure).

---

## 6. Not covered: MELON

MELON's cosine similarity is computed against a **masked re-run** of the same episode, which does
not exist in the stored traces — so it cannot be replayed offline. Capturing MELON scores means
actually running the agent again, which **is** an experiment run and hits the approval gate
(GPU + $ + wall-clock estimate, then owner go). Do it only if the paper needs MELON's curve too;
the PIGuard curve already answers the calibration objection for the classifier arm.
