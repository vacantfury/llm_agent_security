# llm_agent_security

Research harness for the **security of LLM agents**: **encoded / indirect prompt injection**, action-level attacks and defenses, and agent-safety evaluation. A shared codebase for a *line* of work (multiple papers under one harness), sibling to [`llm_guardrail_security`](https://github.com/vacantfury/llm_guardrail_security) (the model-side / VLM encoding-attack line).

## The line

Model-side jailbreak research asks whether a model *emits* harmful text. This repo moves to **agents**, where the adversary controls data the agent *ingests* (indirect prompt injection) and the harm is an **action the agent takes**. The through-line: safety mechanisms that inspect one unit — one representation, one modality, one message channel — are structurally incomplete when harm is *composed across units*; here the unit is the agent's untrusted data channel, and the finding is that injection-specific defenses (spotlighting, isolation, prompt-shield) inherit the same **decode blind spot** content guards have — an *encoded* injected instruction rides through them and the agent decodes-and-acts.

## Papers

| ID | Alias | Codename | Topic | Namespace | Stage |
|---|---|---|---|---|---|
| — *(dead, no ID)* | **E** | Smuggled Actions | Encoded indirect prompt injection defeats injection-specific defenses on LLM agents; success = action completion | `agent_injection` | founding (S4 lit/scoop done) |

See `text_docs/shared/papers.md` for the live roster and `text_docs/agent_injection/proposal.md` for the current paper's state.

## Status

Newly founded (2026-07-19). The agent runtime is not built yet — current work is design + literature (`text_docs/`). The text/image **encoders** in `src/prompt_transformations/` are copied from the sibling repo as payload generators.

## Setup

```bash
uv sync    # once the runtime + deps land
```

Public research repo — public-grade discipline (no secrets / PII in any committed file).
