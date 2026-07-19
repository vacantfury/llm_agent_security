# Literature Review — Security of LLM Agents

Prior-art review for this repo's line (agent-side indirect injection). Migrated 2026-07-19 from the sibling
repo's shared review (`imaging_text_attacks_for_llm_jailbreaking` §14) when Paper E spun out. Organized by
paper; extend with the sibling's `lit-review-loop` / `scoop-check` skills (copied into `.claude/skills/`).

## 1. Agent-side indirect injection — Paper E ("Smuggled Actions") prior art

Paper E (`agent_injection`) lifts the sibling line's encoding / decode-gap thesis from **models to agents**: an
**encoded** indirect-injection payload (semantic text encoders reused from MathEnc, or an image render) evades
**injection-specific** defenses (spotlighting / datamarking / isolation / sandwich / prompt-shield) and drives a
harmful **agent action**. S4 scoop-check #1 (2026-07-19, 3 search angles + full deep-read of 11 papers) verdict:
**no paper does the 4-axis combination; Level 3 (Medium Overlap), delta defensible** — and the two most
dangerous candidates *defanged on inspection*.

### 1.1 The agentic IPI harnesses — natural-language attacks only (the testbeds)

**AgentDojo** (`debenedetti2024agentdojo`, NeurIPS'24 D&B) and **InjecAgent** (`zhan-etal-2024-injecagent`,
ACL Findings'24) are the two rigorous agentic-IPI harnesses. Both test **only natural-language** injections,
with real tool-use and **deterministic action-level scoring** (AgentDojo: benign-utility / utility-under-attack /
targeted-ASR over environment state; InjecAgent: ASR-valid, with a 2-step criterion for data-exfiltration).
AgentDojo's defenses (data delimiters, a DeBERTa PI-classifier, sandwiching, tool-filter) are exactly the
injection-specific defenses we test; its authors flag **multimodal extension as future work** (§5), and
InjecAgent's §8 flags varied injection phrasing as unexplored. → **AgentDojo is the best harness fit**
(encoding slots in as a new `attack()` at the placeholder); InjecAgent is the lightweight complement.

### 1.2 The closest anecdotes — "encoding evades detection," shown once, never measured

- **Greshake et al.** (`10.1145/3605764.3623985`, AISec'23) — the **foundational IPI paper** — §4.3.2 "Encoded
  Injections" gives **one** Base64 Bing-Chat demonstration and explicitly leaves systematic evaluation to future
  work (§5.2, §5.6). The direct ancestor of our claim, never measured.
- **Bhagwatkar et al.** (`bhagwatkar2025indirect`, NeurIPS'25 workshop) — the interim "most dangerous scoop,"
  **defanged** on deep-read: the Braille bypass is **v2-only** (2026-03; verify the version cited), a **single
  anecdote** (one model, one task) against their **own bespoke Sanitizer** (not spotlighting), where **base64 and
  whitespace were tried and FAILED**, explained by a narrow **"rare-token" hypothesis**, *not* a decode-blind-spot
  claim, with **no sweep, no control, no cross-defense**. → Caps only "first to show *any* encoded bypass"
  (Greshake already owns that), **not** "first systematic characterization."

### 1.3 The structural analogue — adaptive attacks break agent IPI defenses, different mechanism

**Zhan et al.** (`zhan-etal-2025-adaptive`, NAACL Findings'25) breaks **all 8** IPI defenses (incl. data-prompt
isolation, sandwich, paraphrasing, detectors) on InjecAgent/AgentDojo, **action-scored** — our exact metric and
"defenses fall to evasion" frame. But the mechanism is **white-box GCG/AutoDAN gradient-optimized gibberish
suffixes**, explicitly *not* semantic/readable encoding. → The **white-box optimizer analogue** to our
**black-box semantic-encoding** attack: same metric+frame, cleanly distinguishable mechanism, complementary
citation, not a scoop.

### 1.4 The spotlighting gap — the defense's own analysis flags our attack, untested

**Hines et al.** (`hines2024defending`, CAMLIS'24 — the canonical IPI defense) has three techniques (delimiting /
datamarking / encoding). Its "encoding" variant base64-encodes the **whole untrusted document** as a defender
**provenance** signal — the attacker payload riding inside is **always plain English**. §5.4 explicitly notes a
*reversible* encoding could be subverted by an attacker who **pre-encodes their payload** — but they **never build
or test it**. → Our paper is exactly the untested vulnerability their own §5.4 anticipates.

### 1.5 Agent context amplifies encoded compliance — the motivation, quantified

**Graves** (`graves2026reversecaptchaevaluatingllm`) — invisible-Unicode encoded instructions — quantifies that
**tool-use dramatically amplifies compliance** with the encoded payload (Cohen's *h* up to **1.37**; compliance →
98–100% with tools+hints vs ≤17% without). No defense tested, success is compliance-graded not action-scored. →
**Motivation citation**: agents are a higher-stakes setting for encoded injection than plain chat.

### 1.6 Image + agent + action — plaintext vector, our gap named as future work

**Cao et al.** (`cao2026vpibench`, ICLR'26) — computer-use / browser agents take **scored actions** against
visual injections and defenses **fail**. But the visual vector is a **plaintext socially-engineered pop-up** (no
decode step) and **no injection-detection guard** is tested. Its Limitations §A names our exact contribution:
*"Future research should investigate techniques to conceal malicious prompts from users, while ensuring that they
remain detectable by AI agents that rely on screenshot-based visual input."* → Our **image-rendered encoded
payload** is that future work.

### 1.7 Encoding studied off-agent; a defense-eval parallel; the competition

- **Uysal et al.** (`uysal2026multilingualobfuscated`) tests base64/hex/ROT13 + multilingual — our encoders — but
  **non-agentically** (direct chatbot, tool-free, defense-free; *direct* not even *indirect* injection). → **Gap
  evidence.**
- **NetInjectBench** (`shayoni2026netinjectbenchbenchmarkingindirectprompt`, network-ops domain) *does* test
  Spotlighting + Self-Reminder on agents, action-scored — a **defense-eval methodology parallel** — but its attacks
  are **100% NL authority-impersonation, zero encoding, zero image.** → Orthogonal-domain cite.
- **Dziemian et al.** (`dziemian2026vulnerableaiagentsindirect`, 272K-submission Gray Swan competition) —
  action-scored at scale, but "Encode or Obfuscate Text" is **1 of 27 incidental post-hoc tags** (ASR 3.4%),
  text-only, and injection defenses were **explicitly turned OFF**. → Not a scoop.

### 1.8 Positioning verdict (S4 gate: SURVIVES at Medium — delta defensible)

No paper unifies **encoded/rendered payload × injection-specific defense × agent action-completion ×
decode-blind-spot frame**. The phenomenon exists only as one-off anecdotes (Greshake's Base64, Firewalls'
Braille), the mechanism exists **non-agentically** (Uysal; the cipher-jailbreak lineage), the agent-amplification
is **quantified** (Reverse CAPTCHA), and **two papers name our exact contribution as untested future work**
(VPI-Bench §A; Spotlighting §5.4).

- **DROP:** "first to show encoding can bypass an injection defense" — Greshake + Firewalls anecdotes own the *existence*.
- **CLAIM:** the **first systematic, controlled characterization** — multi-encoding (semantic + image-rendered) ×
  injection-specific-defense families × **plain-vs-encoded control** × scaffold × backbone — action-scored on a
  standard harness (AgentDojo + InjecAgent), under the **decode-blind-spot** unifying frame.
- **Must-distinguish set:** Firewalls (one Braille anecdote), Adaptive-Attacks (white-box gibberish, not encoding),
  Reverse CAPTCHA (no defense, not action-scored), VPI-Bench (plaintext, no guard), Greshake (one unmeasured Base64
  anecdote).
- **Honest residual risk:** a **hot, fast-moving field** (two papers flag this as future work → scoop-race), and the
  **build cost is higher** (an external agent harness).

**Key references (all in `paper/literature/my_base.bib`):** `debenedetti2024agentdojo`, `zhan-etal-2024-injecagent`,
`10.1145/3605764.3623985`, `bhagwatkar2025indirect`, `zhan-etal-2025-adaptive`, `hines2024defending`,
`graves2026reversecaptchaevaluatingllm`, `cao2026vpibench`, `uysal2026multilingualobfuscated`,
`shayoni2026netinjectbenchbenchmarkingindirectprompt`, `dziemian2026vulnerableaiagentsindirect`; plus
`fairoze2025` (controlled-release, insight twin).
