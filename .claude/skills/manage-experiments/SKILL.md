---
name: manage-experiments
description: >
  Keep a paper's experiment pile finite and legible — build or refresh its
  experiment_matrix.md (RQ → minimal cell-matrix → status), so "what have we run
  vs. what's still needed vs. what's a loose extra" is one glance. Use when the
  user says "manage experiments", "experiment matrix", "experiment status /
  inventory", "what have we run", "what's left to run", "organize / consolidate
  the experiments", "too many experiments", "which experiments are done", "what's
  the state of paper <X>", or before a paper freeze to see what's missing. This
  is the ORGANIZE layer above run-experiment (fill cells) and
  check-experiment-results (validate cells).
---

# Manage experiments (this repo)

This repo runs **multiple papers at once** (`autoattack_defense` = C, `imgaug_defense` = B,
`bestofn_defense` = D, …), each accumulating dozens of runs across two clusters, rejudge passes,
harmful+benign channels, and campaigns. The pile grows faster than it's consolidated, so "too many
experiments" is usually **lost legibility**, not too much compute. This skill restores legibility by
maintaining one **experiment matrix** per paper.

## The convention (every paper has one)

`text_docs/<paper>/experiment_matrix.md` — the paper's single checklist:

- **Each research question → the minimal set of cells that answers it → the status of every cell.**
  A candidate experiment either fills a cell for a named RQ, or it gets cut. That closing condition is
  the whole point — it turns an open pile into a finite burn-down.
- **Status vocabulary:** `done-valid` (result on disk, headline judge = gpt-5-mini, passed
  check-experiment-results) · `done-provisional` (result exists but pilot judge / small-n / un-triaged /
  unverified) · `pending` (planned, no result) · `stale` (superseded by a newer run) · `cuttable`
  (recorded but serves no RQ).
- **Numbers are POINTERS, not values.** A cell cites `campaign + judge + n`, never a hand-typed metric.
  The values self-compute from disk (`run_index.py`, `build_paper_tables.py`) and are checked by
  `verify_results_doc.py`. Hand-typed numbers are how the over-refusal figure got mis-diagnosed 3× —
  don't reintroduce them here.

`text_docs/autoattack_defense/experiment_matrix.md` is the worked template — match its shape.

## Operating principles

- **This skill never runs experiments or edits results docs' numbers.** It reads plan + disk and writes
  the matrix. Filling a `pending` cell is `run-experiment`; validating a `done-provisional` cell is
  `check-experiment-results`; emitting paper tables is `build_paper_tables.py`. Hand off, don't absorb.
- **Read disk, not memory.** The matrix reflects what's actually on disk today, cross-referenced against
  the plan — never what a prior session believed was run.
- **One matrix per paper; append/refresh, don't fork.** Re-running the skill refreshes the existing file.
- **Propose the prune, don't delete.** `cuttable`/`stale` campaigns are *listed* for the user to prune
  (via `cleanup_failed.py` or explicit `rm`), never deleted here.

## Procedure

### Step 1 — Identify the paper (consult the registry, don't assume)
**Read `text_docs/shared/papers.md` first** — the authoritative `alias ↔ codename ↔ namespace ↔ stage` map.
The paper set churns (namespaces get folded, aliases move), so never hardcode it. Current live papers:
**B** `imgaug_defense` (under review) · **C** `autoattack_defense` (in progress) · **D** `bestofn_attack`
(Variance Channels, in progress, AAAI-27) · **E** `agent_injection` (founding); **A** MathEnc is published
(no namespace, encoders in `src/`). **Not standalone papers — no matrix of their own:** `bestofn_defense`
(folded into D as its supportive §4 defense) and `judge_reliability` (parked; its content lives in C/D). A
paper's docs live in `text_docs/<namespace>/`, presets in `conf/experiment/<namespace>/`, outputs in
`outputs/<namespace>/`.

### Step 2 — Gather the INTENDED matrix (from the plan)
Read `text_docs/<paper>/experiments_plan.md` and/or `proposal.md`: extract the RQs and, per RQ, the
intended cell-matrix (models × defenses × attacks/encoders × benchmark × channel[harmful/benign]). Quote
the RQ labels as the doc names them. Skim `conf/experiment/<paper>/*.yaml` headers for the concrete cells.

### Step 3 — Gather the ACTUAL results (from disk)
```bash
python3 scripts/run_index.py --mode all --csv            # every run, all modes (incl. rejudge)
python3 scripts/run_index.py --mode rejudge --campaign <paper_x>   # the current-judge (gpt-5-mini) numbers
```
`run_index.py` is layout-agnostic and classifies by each results.json's own `mode` field (so it sees
paper-namespaced + rejudge runs). The **rejudge** cells carry the headline judge — trust those over the
original `defense+evaluate` score. Note which cells are local vs. still on a cluster.

### Step 4 — Cross-reference → classify every cell
For each intended cell, assign a status (Step-1 vocabulary). Flag: superseded runs (older judge/n → `stale`),
pilot-judge or small-n runs (`done-provisional`), planned-but-absent (`pending`), and recorded runs that map
to no RQ (`cuttable`). Call out consolidation gaps: results on a cluster not synced local, numbers in the
results doc with no results.json anchor (run `verify_results_doc.py --campaign <x>`), campaigns with no RQ home.

### Step 5 — Write `text_docs/<paper>/experiment_matrix.md`
Match the template's sections: header/thesis, the convention note, a Snapshot, one section per RQ (status
table, pointers not values), a Cuttable/superseded prune list, a Consolidation & tooling debt list, and a
**ranked next-actions** list — ordered by *what actually moves the paper* (a done-but-unrecorded result to
write up usually beats a new run). Show the diff, write, confirm.

### Step 6 — Hand off
State the top 1–3 next actions and their owning skill: `run-experiment` (fill `pending`),
`check-experiment-results` (triage `done-provisional`), `build_paper_tables.py` (emit tables),
`verify_results_doc.py` (check the doc). Stop — don't start those here.

## References
- `text_docs/shared/papers.md` — the authoritative paper registry (alias ↔ namespace ↔ stage); Step 1 reads it.
- `text_docs/autoattack_defense/experiment_matrix.md` — the worked template.
- `scripts/run_index.py` — the disk manifest (all modes; `--mode rejudge` for headline numbers).
- `scripts/build_paper_tables.py` — regenerates paper LaTeX tables from disk (currently Paper-B-shaped;
  needs a per-paper generator — a `pending` tooling item).
- `scripts/verify_results_doc.py` — fail-closed check that every recorded number traces to a results.json.
- Sibling skills: `run-experiment` (launch), `check-experiment-results` (validate).
- `CLAUDE.md` — pipeline roles, factories, multi-paper output namespacing.
