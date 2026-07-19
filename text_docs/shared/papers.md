# Papers in this repo — alias index

This repository is a **shared harness for a line of work** (the security of LLM agents), not a single
paper. This file is the crisp `alias ↔ paper ↔ namespace` map so any reader or session can orient in one
glance. Sibling repo: `imaging_text_attacks_for_llm_jailbreaking` (the model-side / VLM encoding-attack line,
Papers A–D).

**This is a projection, not the source of truth.** The canonical registry — evaluation, priority, venue and
review status — is the portfolio of record (psyche `self_model/portfolio.md`); live status/venue tracking is
the gitignored `TODO.md`. Keep review status, scores, and venue decisions **out of this committed file**
(public repo, public-grade discipline).

| Alias | Codename | Topic (one line) | Namespace | Key doc | Stage |
|---|---|---|---|---|---|
| **E** | Smuggled Actions | *Encoded Indirect Prompt Injection on LLM Agents* — this line's MathEnc/ImgAug transforms become **payloads** delivered through an agent's untrusted data channel; encoded payloads defeat injection-specific defenses (spotlighting / delimiter isolation / prompt-shield) tuned on natural-language injections; success = **action completion**. The coverage / decode-gap thesis lifted from models to agents. Attack-first | `agent_injection` | `text_docs/agent_injection/{proposal,idea_check}.md` | founding (S4 lit/scoop done → next S5) |

**Alias continuity.** Alias **E** was assigned in the sibling repo (`imaging_text_attacks_for_llm_jailbreaking`)
before this line spun out on 2026-07-19; it is retained here so the portfolio's paper letters stay stable
(A–D in the sibling, E here). New papers on this line take the next letters (F, …).

**Namespacing convention.** Each paper owns a subdir keyed by its **Namespace** under `text_docs/`,
`conf/experiment/`, and `outputs/`; `shared/` holds cross-paper material (roster, future work, literature).
When a new paper starts, add its row here and create its namespace subdirs.
