# Papers in this repo — alias index

This repository is a **shared harness for a line of work** (the *agent-side* security line), not a single
paper. This file is the crisp `ID ↔ alias ↔ paper ↔ namespace` map so any reader or session can orient in one
glance. Series IDs follow the paper-ID standard (owner-ratified 2026-08-03; registry of record = the science
repo `portfolio.md`); numbers are never reused — a dead paper keeps its ID, marked †. Sibling to [`llm_guardrail_security`](https://github.com/vacantfury/llm_guardrail_security),
which owns the model-side (VLM) line (papers AS-1…AS-4, aliases A–D); the two repos share only the encoders
(see the scope boundary in `CLAUDE.md`).

**This is a projection, not the source of truth.** The canonical registry — evaluation, priority, venue and
review status, publication record, and future aims — is the portfolio of record (the science repo `portfolio.md`);
live status/venue tracking is the gitignored `TODO.md`. Keep review status, scores, and venue decisions **out
of this committed file** (public repo, public-grade discipline).

| ID | Alias | Codename | Topic (one line) | Namespace | Key doc | Stage |
|---|---|---|---|---|---|---|
| **AS-5†** | **E** | *(shelved)* | **⛔ SHELVED 2026-07-24 — scoop-check #3 returned Level 1 (Full Overlap) on all three legs of the successor direction; see `proposal.md §12`.** Eight candidate contributions were generated in this line and all eight were already published, typically 6–18 months earlier. The harness, defense ports, capability ladder and $0 probe machinery are preserved; the negative results are recorded with primary-source citations. Historical framing below. ~~Attack-first framing RETIRED 2026-07-24.~~ ~~Encoded indirect prompt injection defeats injection-specific defenses on LLM agents~~ — the encoded-payload thesis was tested to destruction (see `proposal.md §11`): encoding evades only defenses placed *upstream of the decode*, which is a placement property of the pipeline, not a tunable one. **Successor direction (gated on a $0 pilot): a measurement paper — *what do agent prompt-injection benchmarks actually measure?*** — ASR confounded by tool-use competence; injection detectors keying on imperative surface form rather than harm | `agent_injection` | `text_docs/agent_injection/proposal.md §11` (pivot record; §§1–2, 5, 9 historical) | **S9 · direction pivot — successor proposal written only after the pilot decides** |

**Namespacing convention.** Each paper owns a subdir keyed by its **Namespace** above under `text_docs/`,
`conf/experiment/`, and `outputs/`; `shared/` holds cross-paper material (venue facts, literature, future
work, this index). Aliases are the stable shorthand; codenames are the paper-facing titles. When a new paper
starts, add its row here and create its namespace subdirs.

**Origin — the ID and the `E` alias.** Series ID **AS-5†** assigned 2026-08-03 (retired — the paper died
2026-08-02 and its number is never reused; the letter E was reassigned the same day to the model-internals
first paper, **AS-6**, repo `model_internals_safety`). Paper E was spun out to this repo on **2026-07-19** from the sibling
`llm_guardrail_security` (where the alias `E` had briefly named the now-parked
`judge_reliability` direction). The agent runtime — a tool-use loop, injection into the untrusted *data*
channel, **action-completion** scoring — shares almost none of the sibling's VLM batch-eval pipeline, so it
lives here as its own line. The sibling keeps the model-side papers AS-1…AS-4 (A–D).

**The line has no current work (2026-07-25).** After Paper E was shelved, `future_work.md` **§2 — an
action-level defense against *data-shaped* injection** — was promoted to lead and **closed the same day by
its own gate**: scoop-check #4 returned Level 1 (Full Overlap), blocked by ARGUS (arXiv:2605.03378), which
states our problem framing, insight and mechanism in its own abstract and ships a benchmark for the task
setting. Three further closures are recorded in `future_work.md §2`. The gate did what it was built for —
the direction cost one day of search and never reached a design doc, a namespace, or a row here.

Two directions picked in this line, two closed at Level 1, four days apart. The standing recommendation is
**not to found a third here**; the call is the owner's.

**All remaining directions checked 2026-07-25 (scoop-check #5) — none earns a row.** §4 multi-agent is
**closed** at Level 1 by `hu2026localmonitorsmisscompositional` (2607.11751), which states the claim *and*
proves an impossibility result against it. §5 decomposed agents is **split**: the attack reading is closed,
the crossed *fragmentation × scale* measurement question survives at medium confidence, declined on genre and
GPU cost rather than novelty. §3 multimodal is **declined on headroom** — VPI-Bench (ICLR 2026) already
deceives computer-use agents at up to 51–100% with prompt-level defenses barely helping, leaving an encoded
visual payload nothing to demonstrate. Record: `outputs/scoop_check/2026-07-25-remaining/`.

**The line's thesis is itself published.** This repo's line identity — safety mechanisms that inspect one
unit are incomplete when harm is composed across units — is 2607.11751's headline sentence (*"Local safety is
not global safety when harm is compositional"*), dated six days before this repo was founded. The thesis was
correct; another group formalized and proved it first. The standing recommendation is to found no further
direction here and to treat this repo as a preserved harness; the call is the owner's.
