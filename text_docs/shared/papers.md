# Papers in this repo — alias index

This repository is a **shared harness for a line of work** (the *agent-side* security line), not a single
paper. This file is the crisp `alias ↔ paper ↔ namespace` map so any reader or session can orient in one
glance. Sibling to [`imaging_text_attacks_for_llm_jailbreaking`](https://github.com/vacantfury/imaging_text_attacks_for_llm_jailbreaking),
which owns the model-side (VLM) line (Papers A–D); the two repos share only the encoders (see the scope
boundary in `CLAUDE.md`).

**This is a projection, not the source of truth.** The canonical registry — evaluation, priority, venue and
review status, publication record, and future aims — is the portfolio of record (psyche `self_model/portfolio.md`);
live status/venue tracking is the gitignored `TODO.md`. Keep review status, scores, and venue decisions **out
of this committed file** (public repo, public-grade discipline).

| Alias | Codename | Topic (one line) | Namespace | Key doc | Stage |
|---|---|---|---|---|---|
| **E** | Smuggled Actions | *Encoded indirect prompt injection defeats injection-specific defenses on LLM agents* — an encoded payload dropped into the agent's untrusted data channel rides past spotlighting / data-isolation / prompt-shield; success = the agent **completes the injected action** (attack-first; the action-level defense is the deliberately-later half) | `agent_injection` | `text_docs/agent_injection/{proposal,idea_check}.md` | founding (S4 lit/scoop done) |

**Namespacing convention.** Each paper owns a subdir keyed by its **Namespace** above under `text_docs/`,
`conf/experiment/`, and `outputs/`; `shared/` holds cross-paper material (venue facts, literature, future
work, this index). Aliases are the stable shorthand; codenames are the paper-facing titles. When a new paper
starts, add its row here and create its namespace subdirs.

**Origin — the `E` alias.** Paper E was spun out to this repo on **2026-07-19** from the sibling
`imaging_text_attacks_for_llm_jailbreaking` (where the alias `E` had briefly named the now-parked
`judge_reliability` direction). The agent runtime — a tool-use loop, injection into the untrusted *data*
channel, **action-completion** scoring — shares almost none of the sibling's VLM batch-eval pipeline, so it
lives here as its own line. The sibling keeps the model-side Papers A–D.

**Planned agent-side directions (not yet started papers — no namespace yet).** The line's roadmap lives in
`text_docs/shared/future_work.md`: the action-level **recover-before-act defense** + flagship deployed-agent
demonstration (the coupled, later half of the Smuggled-Actions thesis), and **multi-agent / distributed
composition** (a separate later paper). Each earns a row here only when it becomes an active paper with its
own namespace.
