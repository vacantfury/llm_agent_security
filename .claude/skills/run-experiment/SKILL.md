---
name: run-experiment
description: Plan and launch the next experiment round for this repo — read the experiments plan + results, write conf/experiment/autoattack_defense/experiment.yaml against the project schema with a footprint sanity-check, then prepare/submit the cluster sbatch job. Triggers on "run experiment", "run the experiment", "kick off the next round", "write experiment.yaml", "submit the job", "launch on the cluster". Collaborative and gated: the user approves the yaml and runs the Cursor sync (a palette command I don't replicate); cluster submission only happens after explicit go-ahead and only when the cluster is confirmed live.
---

# Run Experiment

Use when the user wants to plan and launch a run: "run the experiment", "kick off the next round", "write experiment.yaml", "submit the job".

**Clusters are ALWAYS LIVE now (owner 2026-07-12) — do NOT ask, do NOT gate on cluster state.** Default flow: plan → write yaml → (user approves) → (user syncs) → submit → report job id. The old "is the cluster live?" check is retired. Fallback (rare): only if a submit **actually errors** with cluster-unreachable do you fall back to offline-prep (yaml ready, stop before submit) — never pre-emptively assume down.

## Backends — two live SLURM clusters + a multi-cluster splitter (pick one per round; AICR preferred)

- **AICR (default choice)** — bigger GPUs (RTX PRO 6000 ~96GB), 24h wall, **multi-GPU per job** → serves large / tensor-parallel judge+target models natively (no fp8 workaround). Wrapper `scripts/run_experiment_aicr.sbatch`; ssh alias `aicr`. Config: `conf/clusters/aicr.yaml`. Facts: `cluster_files/aicr_cluster_properties.md`.
- **NURC / Explorer** — conda primary (`scripts/run_experiment.sbatch`) or the uv variant (`scripts/run_experiment_uv.sbatch`); 1 GPU/job (fp8 for big models), 8h wall. ssh `zhang.haoyu6@login.explorer.northeastern.edu`. Config: `conf/clusters/nurc.yaml` / `nurc_uv.yaml`.
- **Both at once** — `python dispatch.py <preset>` splits one preset AICR-first across the pool (dry-run by default; `--submit` places + sbatches over ssh). Use when a matrix exceeds one cluster's server budget. ⚠️ The `--submit` path is dry-run-validated but its first LIVE run is still pending (item 4 residual) — for a single-cluster round, submit directly per Step 4.
- **Per-cluster budget + QOS limits live in `conf/clusters/<name>.yaml`** (`budget`, `max_submit`, `max_slurm_time_limit`). Read the CHOSEN cluster's file for the round's budget math (Step 2) — never a hardcoded number.

## Operating principles

- **You propose, the user disposes.** Two mandatory human gates: (1) the user approves `experiment.yaml` before sync; (2) the user runs the Cursor sync. Never skip either.
- **The cluster is a live, costly, hard-to-undo surface.** Never submit without (a) the user confirming the cluster is up this session, (b) showing the exact command, and (c) a footprint estimate. Submitting spawns vLLM servers and burns GPU hours.
- **Never run destructive commands** (`rm` on logs/outputs/mlruns, `scancel` of others' jobs). Cleanup is `check-experiment-results`' job, not this skill's.
- **Stop at WAIT-FOR-USER points** — post findings, ask, and stop emitting tool calls until the user replies.
- **One round per invocation.**
- **Cluster over local (standing rule, owner 2026-07-11).** Experiments run on a cluster (AICR preferred, or NURC), not locally — do NOT run a round locally unless genuinely urgent (both clusters down AND result time-critical). Local `python main.py` is for the `test` smoke check only. (Canonical rule: project `CLAUDE.md` Conventions.)
- **Ran ≠ confirmed — never present a result as in-our-favor until verified (owner correction 2026-07-09).** A completed sweep produces *candidate* numbers. Keep the confidence levels separate in every report — launched / completed / verified — and make no claim ("the rebuttal holds", "X beats Y") from cells that haven't passed sanity checks + a spot-read of raw outputs. Unconfirmed results are never mentioned as if real.
- **"Sample and check" means READ existing outputs (owner correction 2026-07-09).** Verification happens by reading the already-produced responses/judgments on disk — never by firing new API calls (fresh judge runs, re-scores) unless the owner explicitly asks. New calls cost money and are a different experiment, not a check.

## Step 0 — (retired) Cluster is always live

**Do NOT ask whether the cluster is live** (owner 2026-07-12: it is always live from now on). Go straight to Step 1. Only if a real submit later errors cluster-unreachable do you drop to offline-prep — never pre-emptively.

## Step 1 — Read the plan and results (offline)

```bash
# the spec — what round are we in, what's next
sed -n '1,140p' text_docs/autoattack_defense/experiments_plan.md     # §0 status, §3 Rounds, §4 gates
# what's already filled — avoid re-running cells
sed -n '1,100p' text_docs/autoattack_defense/experiment_results.md
# what's ACTUALLY in outputs/ (generated manifest — the source of truth, not the doc)
python3 scripts/run_index.py                       # add --campaign / --defense / --model to filter
```

Determine, and state back to the user before writing anything:
- **Which round / which RQ** this run serves (plan §3), and which result table it fills (`experiment_results.md` C0–C4).
- **The matrix**: models × defenses × encoders (× benchmark, prompt_range). What's *new* vs already-recorded — don't re-run filled cells without a reason.
- **Inputs**: which existing stage-1 outputs (`outputs/prompt_transform/<benchmark>/<encoder>_<ts>/...`) the tasks consume via `source_transform_subdir`. These must already exist locally (text renders are reused across rounds; images may need a re-render round first).

If the round or matrix is ambiguous, **WAIT FOR USER**.

## Step 2 — Write `conf/experiment/<paper>/experiment.yaml`

**Multi-paper layout (reorg 2026-07-13):** presets are namespaced by paper line — `autoattack_defense/` (the decode-gap defense) and `bestofn_defense/` (Paper D). Each paper's `experiment.yaml` is its *own* active preset; run it with `python main.py <paper>/experiment` or a cluster wrapper (`sbatch scripts/run_experiment_aicr.sbatch <paper>/experiment` on AICR, `scripts/run_experiment.sbatch` on NURC). Outputs auto-namespace to `outputs/<paper>/…` (the `paper` key is inferred from the preset subdir).

`experiment.yaml` is the **active preset, overwritten per round** (prior rounds live in git history, not extra files). So **first**: if the current `experiment.yaml` is uncommitted, offer to `git add -A conf/experiment/autoattack_defense/experiment.yaml && git commit` it before overwriting, so the round isn't lost.

Use the **current `experiment.yaml` and the presets in `conf/experiment/*.yaml` as templates** — match their structure, don't invent a schema. Reference: `CLAUDE.md` (3-layer config merge, factories), `src/experiment/schemas.py`, `src/llm_utils/llm_model.py` (model registry), and the factories `src/prompt_transformations/transformation_factory.py` (encoders + image renderers, unified), `src/defense/defender_factory.py`, `src/evaluation/evaluator_factory.py`.

Required shape (mirror the existing file):
- A **header comment block** tying the run to the plan/proposal section and stating the watch-points.
- `num_main_job_threads` (in-process concurrency; ≥ one per server) and `num_cluster_jobs`.
- **YAML anchors** for repeated `{mode, target_model, prompt_range}` and for `source_transform_subdir` paths.
- A `tasks:` list — one row per (model × defense × source) cell.

**Project rules to bake in (sanity-check before showing):**
- **Job budget (per CHOSEN cluster — read `conf/clusters/<name>.yaml`):** `num_cluster_jobs` = orchestrator (1) + one vLLM server per **distinct cluster model** — count **guard/perturbation models referenced inside a defense too**, not just `target_model` (the serve-plumbing serves them as their own gpu jobs). The cluster's `budget` (concurrent vLLM servers) bounds it; `MAX_SUBMIT_JOBS_PER_USER=8` stays the code fail-safe cap:
  - **AICR** (`conf/clusters/aicr.yaml`, `budget: 7`): 7 concurrent servers, multi-GPU allowed → big / tensor-parallel models serve natively (`num_gpus > 1` per-model). Comfortable for most rounds.
  - **NURC** (`conf/clusters/nurc.yaml`, `budget: 4`): QOS `MaxJobsPU=4` concurrent GPU jobs, 1 GPU/job → **≤ 4 distinct cluster models (servers)**, and only with **0 other gpu jobs running** — check `squeue --user=$USER` at submit, else the 4th server queues and the orchestrator hangs waiting for its endpoint. Prefer ≤ 3 for margin. The orchestrator runs on a separate CPU QOS (`short`), so it does NOT count against the 4.
  - Verify `1 + n_distinct_cluster_models ≤ num_cluster_jobs ≤ budget + 1`. (Source: the per-cluster config + `text_docs/shared/nurc_cluster_properties.md` §"QOS Job Limits".)
- **`prompt_range: [start, end]` is inclusive on BOTH ends, 0-indexed.** `[0, 99]` = 100 prompts.
- **Cluster targets** (vLLM-served, confirmed): `qwen2_5_vl_7b`, `internvl3_8b`, `pixtral_12b`. **Llama-3.2-Vision is excluded** (Mllama vLLM bug). API targets (no server, no cluster job): gemini / gpt / claude per the registry — for breadth/Round-5 only.
- **Defenses** per `src/defense/defender_factory.py` (`@register_defense`): `no_defense`, `sage`, `ecso`, `amia_ia`, `modality_complete`, `joint_verify`, `semantic_smooth`. Confirm any unfamiliar name against the factory. (`mllm_protector` / `eta` / `decoy` do NOT exist — removed or never built.)
  - **All defenses run in `mode: defense+evaluate`** — the modes are `prompt_transform` / `defense+evaluate` / `analyze`; there is no separate `defense` mode. Every `Defense` owns its own target-model interaction (wrap-and-query, or query→inspect→re-query).
  - `semantic_smooth` additionally needs a `perturbation_model` (default `gemini-2.5-flash-lite`; see project memory — keep the default), since it paraphrases-and-votes → extra API calls.
- **`source_transform_subdir` must point to an existing stage-1 dir.** `test -e` every referenced path locally before finalizing; a missing source silently produces an empty/failed cell.
- **Benchmark** is auto-inferred from the path (`harmbench`/`jailbreakbench`/`orbench_*`); set `benchmark:` only to override.
- **Tag the round:** set `campaign: <paper>_<round>` (e.g. `campaign: paper_c_round1`) on the tasks (via the shared YAML anchor is easiest). It lands in each `results.json` + MLflow params, so `python3 scripts/run_index.py --campaign paper_c_round1` and the MLflow UI can group the round at a glance. Cheap self-labeling — do it for every new round.

**Footprint summary to print with the yaml:**
- Cell count = encoders × defenses × models (e.g. 3 × 4 × 3 = 36).
- Distinct cluster models = N servers → `num_cluster_jobs` needed = N+1 (≤ 8?).
- Any `semantic_smooth` present (extra `perturbation_model` calls → more API spend)?
- Rough scale (prompts × cells) and which result table it fills.

**Compute-utilization / parallelization — MANDATORY at EVERY launch, do NOT skip (this is a forced step, not a thing to remember):** before choosing a cluster and submitting, actively decide how to spread the work; never default to one-server-one-cluster:
1. **Check GPU contention on BOTH clusters** — `ssh <cluster> 'squeue -p gpu -h -o "%t" | sort | uniq -c'` (AICR partitions are `rtx-batch`/`b200-batch`). Prefer the IDLE cluster; a saturated partition = a long queue wait for a node. **Free-cluster-first is NOT overridable by source-location (owner correction 2026-07-19):** if the idle cluster (AICR) lacks a run's `source_transform_subdir` (the default sync excludes `outputs/`), **scp/sync the source there** — a small text source transfers in seconds — never default to a *busy* cluster just because the source already lives there. And a **concurrent job on a cluster is NOT a collision**: SLURM queues and schedules, so don't cancel your own work or gate on another job. The ONLY real waste to avoid is running the *identical cells* twice (a quick glance, not paralysis) plus the shared 8-job/user budget. (Seed: 2026-07-19 — submitted a Pixtral re-run to a contended NURC because the source was there, treated a concurrent job as a "collision", cancelled my own work; the right move was AICR-first + scp the 11 MB source.)
2. **Find the independent parallelizable units.** Cells/arms are independent iff none consumes another's output. **Arms that share ONE target model (e.g. `no_defense` vs `canonicalize`, both on `qwen2_5_vl_7b`) STILL serialize through a single served endpoint** — they are independent *work* even though they share a *model*, so a single server is the bottleneck, not a convenience.
3. **Parallelize independent work across BOTH clusters** (each serves its own target replica) and/or serve replicas — instead of pushing everything through one server on one cluster. State the chosen split **and the expected wall-clock** in the footprint shown to the user.

This step is the ENFORCEMENT of memory `feedback-maximize-compute-utilization`. That memory in context did NOT prevent a serialized single-GPU run on 2026-07-16 (it was mis-scoped as "only multi-MODEL runs parallelize" and dropped under recovery-firefighting) — so the check lives HERE, in the launch procedure, where it fires every time rather than on recall.

**Cost tier — cheap-first for intermediate runs (MANDATORY, do NOT skip):** a PILOT / smoke / first-integration / directional round judges (and targets) with the **cheapest ADEQUATE open-source cluster-served** models — FREE — never the expensive validated/API models. Concretely: judge intermediate runs with **`wildguard`** (`judge_method: wildguard`) — the decided free judge (7B, cluster-served, no API cost); target with the served open models (`qwen2_5_vl_7b` is the smallest VLM). Reserve **`gpt-5-mini`** (API — the validated headline judge) for the FINAL reportable run only, or apply it as a `rejudge` pass over the pilot's SAVED responses (no re-query) so the API judge runs ONCE, on final numbers. Do NOT reach for `llama_3_3_70b_instruct` as the "cheap" judge — it is 70B (multi-GPU, does not fit NURC) and is NOT a decided judge; the shared judges are `gpt-5-mini` + `wildguard` only. Set `judge_model`/`judge_method` accordingly and show the per-run $ estimate in the footprint. Seed 2026-07-16: the Paper-D pilot judged 16k rows with `gpt-5-mini` (~$3–4) when free `wildguard` would have served. (Enforcement of memory `feedback-cheap-first-intermediate-runs`.)

**API-model HARD GATE (owner-ratified 2026-07-16 — do NOT skip):** if the preset contains ANY API model (`gpt-5-*`, `claude-*`, `gemini-*`, as judge OR target), you MUST (1) state a good reason why a free cluster-served model won't do, and (2) get an EXPLICIT owner OK for THAT api usage before submit — never bundle an API model into a run on the general go-ahead. Free open-source served models (judge `wildguard`; targets `qwen2_5_vl_7b`/`internvl3_8b`/`pixtral_12b`) proceed under the normal propose-and-go flow.

**Write** `conf/experiment/autoattack_defense/experiment.yaml`, then show the full yaml + footprint and hand off to the Sync stage (Step 3) with **one combined ask** — don't split "approve the yaml" and "run the sync" into two round-trips:

> *"If this looks right, run your Cursor sync (Cmd+Shift+P → sync local→remote) and tell me when it's done — that's my go-ahead to submit. If anything's off, tell me what to change and I'll rewrite before you sync."*

**WAIT FOR USER.** If they ask for changes, rewrite and re-show — still one combined ask per iteration.

**Offline-prep fallback (rare — only if a submit actually errors cluster-unreachable):** stop here (no sync, no submit) — summarize that the yaml is ready and what to do when the cluster returns. Do not enter this mode pre-emptively (cluster is always live, owner 2026-07-12).

## Step 3 — Sync: YOUR hands FOR NOW (a limitation to automate away, not a target state)

**Owner principle (2026-07-11): the experiment/research flow minimizes his participation to *meaningful gates only* — automate all pure actuation.** This sync is the one purely-mechanical actuation still on his plate, and the standing goal is to AUTOMATE it away (backlog: scripted rsync mirroring his Cursor excludes + direct `ssh -i <key>` auth, or git-pull delivery for the yaml direction). Until that lands it's his hands — not because it *should* be, but because:

The yaml is written **locally**; the cluster runs from its own checkout (`~/projects/imaging_text_attacks_for_llm_jailbreaking`), so the file must be carried across — and **I cannot carry it yet**. This stage is explicit, never skipped, never assumed done:

- The sync is the user's Cursor **Sync-Rsync** palette command (Cmd+Shift+P → sync local→remote), which I can't invoke; it also applies the repo's exclude patterns and carries any **new** stage-1 encode dirs a single-file copy would miss.
- A one-file `scp` of `experiment.yaml` over the Step-4 submit-ssh path is *theoretically* possible but **unreliable** (the ssh-agent gap below) and misses new inputs — so the Cursor sync stays the method. Do **not** try to replicate the sync yourself.
- **Prime-stance framing:** the user is the hands here because the tool can't reach this action, so the ask is *execute-ready* — exact command-path above, target = the yaml (+ any new encode dirs) reach the cluster checkout, confirm by replying "synced".
- **The user's "synced" IS the approval and the go-ahead to submit.** Emit no submit call until you hear it. **WAIT FOR USER.**

## Step 4 — Submit (only if cluster confirmed live, and only after the Step 3 sync)

Show the exact command and get a go-ahead:

```bash
# AICR (preferred):
ssh aicr \
  'cd ~/projects/imaging_text_attacks_for_llm_jailbreaking && squeue --user=$USER | head && sbatch scripts/run_experiment_aicr.sbatch autoattack_defense/experiment'
# NURC / Explorer (conda; use run_experiment_uv.sbatch for the uv env):
ssh zhang.haoyu6@login.explorer.northeastern.edu \
  'cd ~/projects/imaging_text_attacks_for_llm_jailbreaking && squeue --user=$USER | head && sbatch scripts/run_experiment.sbatch autoattack_defense/experiment'
```

Use the ssh/wrapper for the backend chosen in Step 0. (And use `test` instead of `experiment` for the ~$0.01 smoke preset first if the round introduces a new defender/model/serving path — the current yaml header usually flags "first real run of X".)

**Execution mode — I run the submission** (the user wants this automated after sync):
- After the user confirms sync, **I run the ssh+sbatch myself**, **unsandboxed** (`dangerouslyDisableSandbox: true`) so ssh can read the key.
- Auth caveat (2026-06-15, don't re-litigate by probing): a prior check showed the Bash tool's ssh-agent may not hold the cluster key — the interactive shell authenticates via `~/.ssh/agent/…`, while the tool saw the empty launchd agent. **If a submit returns `Permission denied (publickey)`, that's this gap — do NOT retry-loop.** Fall back once to the user running the command via the in-session `!` prefix, and flag that the agent needs sorting (e.g. loading the key into the agent the tool sees) so I can run it next time.
- When the cluster is freshly back and auth is unsettled, a single unsandboxed `ssh … 'echo ok'` confirms it before the real submit. One probe, not many.

After submission: capture the job id (`Submitted batch job <id>` → `mj_<id>`) and report it. Then give the **async handoff** — the owner works in-and-out, never alongside a running job (his instruction 2026-07-11), so bridge into `check-experiment-results` explicitly:

- **Runtime estimate (always give one).** Rough wall-clock, honestly hedged: the vLLM servers queue as *separate* SLURM jobs, so queue wait is the wildcard (minutes → longer under load); then inference + judging scale with the cell count. Give a *check-back window*, not a false-precise ETA (e.g. "~30–60 min of compute once servers are up; check back in ~1–1.5 h when you next work").
- **Sync-back-to-check handoff (this IS the bridge to `check-experiment-results`).** Tell him, execute-ready: *"When you next work — ideally after ~<estimate> — run your Cursor sync **remote→local** (Cmd+Shift+P → Sync-Rsync) to pull the run's `outputs/` + `logs/` down, then ping me and I'll run the correctness check (`check-experiment-results`)."*
- **The trigger is HIS return + sync, not a timer.** Don't set up cluster polling — the ssh-agent gap makes repeated ssh unreliable and he's async anyway. The correctness check begins when he syncs back. (A scheduled nudge only helps if he happens to be at the machine — offer it only if he asks.)
- Do **not** edit `experiment_results.md` here — that's the other skill's job.

## References

- `scripts/frequent_commands.md` — the canonical ssh / conda / squeue / sbatch / cleanup commands.
- `conf/clusters/` — per-cluster config (item 3): `_defaults.yaml` (agnostic) + `nurc.yaml` / `nurc_uv.yaml` / `aicr.yaml` (peers). Server params, `budget`, `max_submit`, `max_slurm_time_limit`, `sbatch` wrapper — one home per cluster. Selected by `CLUSTER_PROFILE` (default `nurc`).
- `scripts/run_experiment.sbatch` (NURC conda) / `run_experiment_uv.sbatch` (NURC uv) / `run_experiment_aicr.sbatch` (AICR) — the orchestrator wrappers (CPU; each exports its `CLUSTER_PROFILE`). They still carry a now-inert `mllm_protector` Auto-GPU guard (harmless dead code).
- `dispatch.py` + `conf/cluster_pool.yaml` (gitignored connection) — the multi-cluster splitter (item 4); `python dispatch.py <preset>` for a dry-run plan.
- `scripts/run_index.py` — generated manifest of every run in `outputs/` (read-only; filter by `--campaign`/`--defense`/`--model`). The source-of-truth index; don't hand-scan dirs.
- `text_docs/shared/nurc_cluster_properties.md` + `cluster_files/aicr_cluster_properties.md` — cluster specifics.
- `text_docs/autoattack_defense/experiments_plan.md` / `experiment_results.md` — the spec and the ledger.
