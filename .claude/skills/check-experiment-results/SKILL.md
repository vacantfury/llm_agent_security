---
name: check-experiment-results
description: Triage a completed (or failed) experiment run for this repo. Walks logs → cleanup → result correctness → spot-check raw outputs → bad-logic detection → update experiment_results.md → discuss findings. The user wants a *collaborative* triage: many steps end with "wait for the user" — never run destructive commands and never edit experiment_results.md without an explicit go-ahead.
---

# Check Experiment Results

Use this when the user says "check experiment results", "check the latest job", "triage mj_<id>", or otherwise asks you to review a SLURM run or a batch of experiment folders.

## Operating principles

- **You propose, the user disposes.** All deletions, code fixes, and writes to `text_docs/autoattack_defense/experiment_results.md` require explicit user approval. Print the command/diff and stop.
- **Stop at the wait points.** Several steps below say *WAIT FOR USER*. That means: post your findings, ask the targeted question, and stop emitting tool calls until the user replies.
- **Approval is one round — then execute.** When the user approves a write to `text_docs/autoattack_defense/experiment_results.md` (or already told you to record), do the edit in the SAME pass and confirm it's done — never re-ask, defer, or leave it pending. Label every reported number with its confidence: **confirmed** (passed the sanity + method-implementation checks) vs **provisional** (checks pending) — never state a provisional result as a conclusion. (Both directions observed as real corrections here, 2026-07-11.)
- **Numbers must trace to raw output — the evidence pre-check (Phase-0 integrity, `text_docs/shared/auto_research_pattern.md` §5).** Every number written to `experiment_results.md` must come from a run's `results.json` — never inferred, remembered from another round, or interpolated to complete a table. A number not yet available is written as the literal **`DATA_NEEDED`**, never a plausible-looking guess. After any edit to the doc, run `python3 scripts/verify_results_doc.py` (Step 7) and resolve every **FLAG** before calling a number *confirmed* — **fail-closed**: a flagged cell, or a cited run-dir whose `results.json` can't be read, blocks the confirmed label. Honest limit: it verifies a number EXISTS in the cited raw output, NOT its column placement or which run a multi-run row's each cell came from — the Step 4/5 spot-checks still stand.
- **One pass per invocation.** Don't loop back to step 1 after step 8 unless the user asks for another run.
- **A completed run is NOT a valid result — check the method's CODE, not just the numbers (owner instruction 2026-07-11).** `status: success` + plausible metrics do NOT mean the experiment measured what you intended; the method must actually *implement* what its framing claims. For any **first-run method** or any **surprising result** (a new method under- OR over-performing, a baseline beating the contribution, a suspiciously clean win), run a **method-implementation check BEFORE concluding or recording**: read the method/defense code, confirm the code path matches the claimed mechanism, and verify the intermediate step actually ran on the RIGHT content (via the raw responses, added logging, or the code itself). Separate *"the method genuinely does X → result Y"* (a real finding) from *"the code doesn't do X — bug/gap → the result is a meaningless test"* (→ diagnose with `systematic-debugging`, fix, re-run; do **not** record it as science). Precedents (2026-07-11): Round-1 `modality_complete` looked like it *failed* but had NO text-decode step (≈ `sage` by construction); its decode then covered only the text channel, not the recovered image content (would have wrongly *failed* the image round). Both ran clean; both were invalid as tests of the claim. This extends run-experiment's "ran ≠ confirmed" from *unverified* to *invalidly-implemented*.

## Inputs to identify first

Before starting, figure out:
1. **Which job?** Latest `logs/mj_*.out` / `.err` pair by mtime, or a specific `mj_<id>` the user named.
2. **Which experiment folders does this job own?** Cross-reference the `.out` log timestamps with `outputs/<mode>/<benchmark>/*` mtimes (the run timestamp is also embedded in the folder name, e.g. `..._20260519_055518_82362539`).

If either is ambiguous, ask the user before proceeding.

---

## Step 0 — Get the run's outputs local: ASK for the sync UP FRONT (owner correction 2026-07-12)

**Owner correction (2026-07-12, SUPERSEDES the earlier auto-pull default): do NOT self-pull the run's data.** When a triage needs the cluster's `outputs/`/`logs/` local, **the FIRST thing the session says is the remote→local sync request, then WAIT** — do not `scripts/sync_back.sh` or SSH-read `results.json` / `raw_results.jsonl` off the cluster yourself as a workaround. (Rationale + boundary: memory `feedback_request_sync_upfront_not_self_pull` — the ssh **submit** path stays automated; this rule is about pulling data *down*.)

- Lead with, execute-ready: *"Sync remote→local (Cmd+Shift+P → Sync-Rsync) to pull this run's `outputs/` + `logs/`, then say go."* **WAIT FOR USER.**
- Once the user confirms, verify locally: `python3 scripts/run_index.py --campaign <x>` (expected cell count) + `ls logs/mj_<id>.*`, then go to Step 1.
- `scripts/sync_back.sh` and SSH result-reads are **retired as the default** (owner declined the self-pull pattern 2026-07-12). A bare *is-the-job-done?* liveness `squeue` check is still fine; pulling RESULTS is what waits for the sync.

---

## Step 1 — Scan logs for errors

```bash
ls -lt logs/ | head
# pick the relevant mj_<id>.{out,err} pair, then:
tail -200 logs/mj_<id>.err
grep -niE "error|exception|traceback|timeout|failed|killed" logs/mj_<id>.out logs/mj_<id>.err | head -50
```

Classify each error as:
- **Infrastructure** (SLURM OOM, node failure, vLLM startup timeout, batch-API timeout for Anthropic/Google) — folders are likely incomplete, candidates for cleanup.
- **Code bug** (Python traceback, schema validation, JSON decode) — folders may be partial; need user discussion before fixing.
- **API refusal/safety** (Google "content flagged", OpenAI account restriction) — not a bug; record but don't delete unless user says so.
- **Benign warnings** (deprecation, retry-then-succeed) — ignore.

Output a short table: `error_class | count | sample_message | suspected_folders`.

**If errors exist → go to Step 2. If clean → skip to Step 4.**

---

## Step 2 — Propose cleanup commands (DO NOT RUN)

The repo's helper is `scripts/cleanup_failed.py` — prefer it over manual `rm -rf`.

```bash
# dry-run first, scoped to recent activity if the job is fresh
python scripts/cleanup_failed.py --recent 1d
# then user-approved delete
python scripts/cleanup_failed.py --recent 1d --delete
```

For folders that have `results.json` but are still invalid (judge bug, wrong config, etc.) — `cleanup_failed.py` will NOT catch them. Print explicit `rm -rf` commands per folder, grouped by reason. Also print the matching `mlruns/<exp_id>/<run_id>` paths (read `mlflow_run_id` from each `results.json`).

**WAIT FOR USER** — do not execute deletions.

---

## Step 3 — Discuss code bugs (if any)

For each code-level error: post the file:line, the exception, your one-paragraph hypothesis of root cause, and the minimal fix you'd propose. Do not start editing.

**WAIT FOR USER** — they'll say "go ahead", "different approach", or "skip for now".

---

## Step 4 — Result correctness check

For every successful folder owned by this job:

```bash
# Quick scan: the generated manifest, scoped to this run (fields read from
# results.json — asr/refusal, defense, model, chain, count, status, cost).
python3 scripts/run_index.py --since <run-date>          # add --campaign <x> to scope to the round
```

Sanity rules (current framing — no more `text_original`/`prompt_stages` 2×2; results are per (model, defense, encoder-chain) cells):
- Bare `no_defense` encoded-attack ASR on the open-weight VLMs is normally **substantial** (e.g. `code_attack` text ~77% on qwen; `set_theory`/`formal_logic` lower). A near-**0%** `no_defense` cell is suspicious — OCR failure on an image cell, the empty-response judge bug, or encoder refusals; verify raw before trusting.
- A defended cell (`sage`/`ecso`/`amia_ia`/`modality_complete`) *below* its `no_defense` control is the expected decode-gap direction; a defended cell *above* control is suspicious → check raw.
- `count` should equal the `prompt_range` span (`[0,99]` → 100). `status: partial_judge` means judge errors on some prompts (excluded from the denominator) — report how many.
- Absolute ASR is **judge-sensitive** (gpt-5-nano inflates ~2–3×, plan §0) — trust *direction / relative* contrasts; the consensus rejudge is planned for headline numbers.

**If everything looks reasonable → skip to Step 7.**

---

## Step 5 — Spot-check `raw_results.jsonl` for outliers

For any folder flagged in Step 4:

```bash
# inspect a few rows
head -3 outputs/<mode>/<benchmark>/<folder>/raw_results.jsonl | python3 -m json.tool
# specifically check empty responses (the May 8 bug pattern)
python3 -c "
import json
rows = [json.loads(l) for l in open('outputs/<mode>/<benchmark>/<folder>/raw_results.jsonl')]
empty = [r for r in rows if not (r.get('response') or '').strip()]
print(f'{len(empty)}/{len(rows)} empty responses')
print(f'Empty marked harmful: {sum(1 for r in empty if r.get(\"is_harmful\") or r.get(\"label\")==\"unsafe\")}')
"
```

Look for: empty responses misclassified as unsafe, judge LLM errors, truncated generations, refused-but-marked-success patterns.

---

## Step 6 — Identify problematic logic & list folders to delete (DO NOT RUN)

For each folder whose *logic* is wrong (not just incomplete), output:
- Folder path
- Why it's wrong (one sentence)
- The `mlruns/.../<run_id>` to delete alongside it
- The proposed `rm -rf` command

Then describe the suspected bug in the pipeline code (file:line if you can pinpoint it). **WAIT FOR USER** before either deleting or editing code.

---

## Step 7 — Append correct results to `experiment_results.md`

Only after Steps 1–6 are resolved (errors handled, bad folders flagged). Match the existing structure exactly:

- The results doc is `experiment_results.md` (**Paper C only** — the Paper-B rebuttal is split into `paper_b_rebuttal_results.md`). Fill the matching `## C0–C4` table for the round; don't invent a `## P<N>` heading (that was the old Paper-B structure).
- Use the same table columns as the nearest comparable section (P7c-style for HarmBench, P9-style for OR-Bench, etc.).
- Include: model, encoding, all available `prompt_stages` ASRs, `Δ (img−txt enc)` if both present, judge, rows, experiment dir (basename only).
- Add a brief "Key findings" subsection if there's something notable (defense effect direction, baseline shift, anomaly).
- Update the "Total evaluations" counter at the bottom.
- **Provenance for checkability:** name the round's `campaign` in the section's intro paragraph (or give each row a `Dir` column). The evidence pre-check resolves recorded numbers against raw output by those anchors; a section with neither is reported UNVERIFIABLE (still honest — nothing is silently passed, but it can't be machine-checked).
- **Unavailable numbers → `DATA_NEEDED`, never a guess.** Any cell whose number isn't in a `results.json` yet gets the literal `DATA_NEEDED` (greppable). Before any paper freeze: `grep -n DATA_NEEDED text_docs/autoattack_defense/experiment_results.md` — every hit is an open hole to fill or a claim to drop.

Show the user the diff (or the new section as a code block) **before** writing — wait for approval, then `Edit` immediately and confirm done. If the user already instructed the write, skip the re-ask and write in the same pass.

**Then run the evidence pre-check** (Phase-0 integrity — deterministic, fail-closed):

```bash
python3 scripts/verify_results_doc.py                 # audit the whole doc
python3 scripts/verify_results_doc.py --campaign <x>  # scope to this round
```

It confirms every recorded number traces to a real `results.json`, lists any `DATA_NEEDED` holes, and **FLAGS** any cell not found in the cited raw output (fabrication / mis-transcription). A FLAG — or a cited run-dir with no readable `results.json` — means **do NOT mark that number confirmed**: fix the transcription or add the missing provenance, then re-run. Exit 0 = all anchored numbers verified. (It never edits the doc; it only reports.)

---

## Step 8 — Discuss findings

Post a 3–6 bullet summary:
- What this run confirms or contradicts vs. existing P-sections.
- Any new direction this suggests (new encodings to try, defense gaps, model-specific anomalies).
- Open questions for the user.

**WAIT FOR USER** — they'll steer the next experiment from here.

---

## Quick reference — repo conventions

- Output layout: `outputs/<mode>/<benchmark>/<shortname>_<timestamp>_<rand>/results.json`
- Modes: `prompt_transform`, `defense+evaluate`, `analyze`
- Benchmarks: `jailbreakbench`, `jailbreakbench_benign`, `harmbench`, `orbench_harmful`, `orbench`
- Each `results.json` contains `mlflow_run_id` → maps to `mlruns/<exp_id>/<run_id>/`
- SLURM log naming: `mj_<jobid>.out` / `mj_<jobid>.err` (sbatch script: `scripts/run_experiment.sbatch`)
- Known judge bug history: empty Claude responses → use the empty-response-safe logic already in evaluators (`src/evaluation/*`); if results predate May 8, suspect this bug.
