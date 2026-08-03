# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

Visibility: public *(deliberately public from the start — owner policy 2026-07-09: science projects are public from birth, and the repo doubles as résumé/portfolio evidence. Consequence: public-grade discipline is MANDATORY — never commit personal data, ARR/reviewer text (`text_docs/reviews/` is gitignored), task files, secrets, or 1Password references.)*

## Project

Research codebase for the **security of LLM agents** line: **encoded / indirect prompt injection**, action-level attacks and defenses, and agent-safety evaluation. Like its sibling repo (see the scope boundary), this is a **shared harness for a line of work**, not a single paper — it namespaces multiple papers under one harness.

**Founded 2026-07-19**, spun out of `llm_guardrail_security`. Rationale: the agent runtime (a tool-use loop on an external harness, injection into the untrusted *data channel*, **action-completion** scoring) shares almost none of the sibling's VLM batch-eval pipeline (`prompt_transform → content-guard defense → VLM query → harm/refusal judge`) — the only genuinely shared piece is the **text/image encoders**, copied here as *payloads*. Forcing the two execution models into one repo would jam incompatible runtimes together.

First paper: **"Smuggled Actions"** (ID **AS-5†** — retired 2026-08-02; alias ~~E~~, the letter since reassigned to the model-internals paper AS-6; `agent_injection`) — an encoded indirect-injection payload evades injection-specific defenses (spotlighting / isolation / prompt-shield) on an LLM agent, scored by whether the agent completes the injected action; the agent coordinate of the sibling line's coverage / decode-gap thesis. See `text_docs/agent_injection/{proposal,idea_check}.md` and `text_docs/shared/{papers,future_work,literature_review}.md`.

## Scope boundary (load-bearing — read before deciding where work goes)

- **THIS repo owns everything AGENT:** indirect injection via a tool/data channel, action-completion harm, agent scaffolds + external harnesses (AgentDojo / InjecAgent), injection-specific defenses (spotlighting, data-isolation, prompt-shield / injection classifiers), and later multi-agent / distributed harm.
- **The SIBLING `llm_guardrail_security` owns the model-side (VLM) line:** encoding + imaging jailbreak *attacks* and *content-guard* defenses, judged by harm / refusal on the model's TEXT output. Papers AS-1…AS-4 (aliases A–D) live there; `judge_reliability` is parked there.
- **Shared = the ENCODERS only.** `src/prompt_transformations/` here is a **COPY** of the sibling's encoder/renderer factory — the payload generators. Keep them in sync **manually**; if a second real need appears, extract a standalone encoder package (rule of two). **Do NOT add a cross-repo import dependency** — the oikos charter bars a research-bet→research-bet dependency; copy, don't import.
- **One concrete example each side:** "encode a harmful request as set-theory, render to image" = an **encoder** (shared); "inject that encoded blob into a tool output and check whether the agent calls `send_email`" = **THIS repo**; "check whether a VLM emits harmful text for that image" = the **sibling**.

## Architecture (INTENDED — the `agent_injection` paper is at S6/design; the runtime build is S7, NOT done yet)

The agent pipeline, to be built at S7 (code design + implementation):

1. **Payload** — encode a harmful instruction with `src/prompt_transformations/` (text encoders: set-theory / formal-logic / code / cipher / classical-Chinese / homoglyph; or an image render).
2. **Inject** — place the payload into the agent's **untrusted data channel** (a tool output / retrieved doc / on-screen image) on a standard harness (**AgentDojo** preferred — deterministic action-level scoring; **InjecAgent** as the lightweight complement).
3. **Agent** — an agent scaffold × backbone runs the tool-use loop; optionally behind an **injection-specific defense** (spotlighting / isolation / prompt-shield).
4. **Score** — **action completion** (did the agent execute the injected action / call the sensitive tool), plus benign-task utility. Plain-vs-encoded control isolates the encoding effect.

Multi-paper namespacing mirrors the sibling: `text_docs/<paper>/`, `conf/experiment/<paper>/`, `outputs/<paper>/`, with `text_docs/shared/` for cross-paper material (`papers.md` roster, `future_work.md`, `literature_review.md`) and `paper/literature/my_base.bib` for citations. Follow the sibling's registry/factory pattern (the copied encoder factory is the template) and the YAML-config-not-magic-numbers rule.

## Common commands

- **Bib sync** — reconcile the shared-encoding citation overlap with the sibling repo:
  `uv run python scripts/sync_shared_refs.py` (`--show-only` for the one-sided lists; `--strict` to exit non-zero on a metadata conflict). Report-only — it never writes; config in `conf/sync_shared_refs.yaml`. Per the scope boundary above, the two bibs are kept as separate copies (not imported), and this tool keeps their overlap honest.

The agent runtime is not built yet — the `agent_injection` paper is at **S6 (design)** (see its `proposal.md`); the runtime **build is S7**. Once built, this section mirrors the sibling's `python main.py <preset>` shape adapted to the agent harness. Until then, work is docs + design (`text_docs/`) plus the maintenance command above.

## Skills (copied from the sibling; adapt the runtime-specific ones)

`.claude/skills/` holds copies of the sibling's research skills:
- **`lit-review-loop`, `scoop-check`** — directly reusable (general research skills; already used to found Paper AS-5's (Smuggled Actions) literature base).
- **`run-experiment`, `check-experiment-results`, `manage-experiments`** — **need adaptation** to the agent runtime; they currently assume the sibling's VLM cluster pipeline (`conf/experiment/autoattack_defense`, vLLM serving, HarmBench judge). Adapt at S7/S8 when the agent harness exists.

Global skills (`research-workflow`, `found-project`, `bootstrap-research-skills`, etc.) apply unchanged.

## Conventions

- **Package manager: `uv`** (this is a new repo — global law: uv, not poetry). Deps in `pyproject.toml`, lock is `uv.lock`.
- **LLM provider layer = the `llm_utils` base package** (pinned git dep by tag, currently `llm_utils @ git+https://github.com/vacantfury/llm_utils@v3.1.0`; the vendored `src/llm_utils/` copy was removed 2026-07-23). Import `from llm_utils import LLMServiceFactory, LLMModel, ...`; no config loader is wired in this repo, so `LLMServiceFactory.create()` uses caller kwargs only. Upgrades = bump the tag deliberately; never vendor a copy back. Note: upstream tags are not immutable — the v2.x tags were removed when v3.0.0 rewrote history, so a stale pin can stop resolving; track the newest tag rather than sitting on an old one. v3.1.0 added `batch_chat_with_logprobs` (per-token logprobs, `SlurmClusterService` only — the Anthropic and Google services raise `NotImplementedError`, a permanent provider gap); nothing in this repo needs it yet, since both wired guards emit a real score natively.
- **Experiment-run approval gate (owner rule 2026-07-22):** agent experiments are heavy, so BEFORE launching ANY experiment run report an explicit estimate of **(1) GPU count + type, (2) money ($), and (3) wall-clock running time**, and get the owner's explicit go. Never launch a run without an approved estimate. Design-time cost estimation stays a first-class constraint; this adds the mandatory pre-run GPU+$+time report + approval. Prefer the open-weight cluster arm to drive API spend toward zero — reserve paid API models for the final paper, not for gating pilots.
- **Cluster sync (family standard, settled 2026-08-02):** this repo already follows it — git clone/pull for the committed source + rsync for the gitignored `scripts/*.sbatch` ops layer + rsync-down for results. Canonical statement + rationale + footguns: science organ `knowledge/cluster_sync_convention.md`. Cite it; don't re-derive a per-repo scheme.
- **Public-grade discipline** (mandatory): no secrets / PII / 1Password refs in any committed file; `TODO.md`, `outputs/`, `paper/literature/`, `data/`, `text_docs/reviews/` are gitignored.
- **Conference deadlines:** the CANONICAL timeline lives in the sibling repo — `llm_guardrail_security/text_docs/shared/conference_timeline.md` (deadlines + Rep/Fit/Bar/Archival columns). Local `text_docs/shared/conference_timeline.md` is a pointer stub only. Update the canonical, never fork per-paper deadline lists; when this repo reaches venue planning, add a per-repo Fit column THERE (2026-07-20).
- **English only** in task files (human names may stay as-is).
- This is an **active research repo whose direction shifts** — consult `text_docs/shared/papers.md` + the paper's `proposal.md` (with its `Workflow stage:` line) before assuming what's important.

## Task system

Root `TODO.md` (gitignored — task text is personal), psyche task standard (position = priority; finished items move to the central psyche archive). Registered in the psyche oikos map as a research bet.
