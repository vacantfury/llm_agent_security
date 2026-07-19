# Future work — the agent-security line

Candidate papers on this line beyond the founding Paper E. Migrated 2026-07-19 from the sibling repo's
`future_work.md` §5 / §7.2 (the agent coordinates of the compositional-harm thesis). One project per section.

## 1. Paper E — Smuggled Actions (the founding paper, `agent_injection`)

Encoded indirect prompt injection defeats injection-specific defenses on LLM agents; success = action completion.
Attack-first. Live state: `text_docs/agent_injection/proposal.md`. (Not "future" — the current paper; listed for
orientation.)

## 2. Action-level defense — recover-before-act (the coupled defense half)

The defense half of the agent line (sibling `future_work.md §5.2`). The coverage-complete guard's agent analog:
recover / decode content on the untrusted data channel **before** it can reach an action. Agent defenses
(information-flow control, dual-LLM quarantine, CaMeL-style capability tracking) couple to agent structure — so
this is the harder, engineering-heavier, later contribution. Includes the **multimodal / image-borne** injection
variant (computer-use / screenshot agents) and a possible flagship demonstration on a deployed, recognizable
agent (responsible disclosure).

## 3. Multi-agent / distributed harm (the broadest reach)

The cross-agent analog of cross-modal splitting (sibling `future_work.md §7.2`): harm distributed across agents,
each agent's individual contribution benign, the *joint* behavior harmful — deception / collusion / steering as
the mechanism, **joint / system-level verification** as the defense. Overlaps §2 but generalizes it: §2 is
single-agent indirect injection; this is the *multi-agent* composition where no single agent is individually
compromised. The most compute-heavy build — naturally timed for a richer-resource era. Scope discipline: enter via
the *compositional-harm* angle (per-agent-benign / joint-harmful + a joint-verification defense), NOT another
propensity-for-deception leaderboard.
