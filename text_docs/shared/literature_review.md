# Literature Review — Encoded Indirect Prompt Injection on LLM Agents

*Scope: this repo's line — the **agent-side** security line (Paper E "Smuggled Actions" / `agent_injection`, and its
later coordinates). It covers agentic indirect-prompt-injection (IPI) harnesses, injection-specific defenses,
encoded / obfuscated / non-plaintext injection payloads, and adaptive attacks on agent defenses. The
**model-side (VLM) survey** — typographic / perturbation / encoding jailbreaks against content guards, judge
reliability, best-of-N — lives in the sibling repo `imaging_text_attacks_for_llm_jailbreaking`'s own
`literature_review.md` and is not duplicated here (scope boundary: `CLAUDE.md`). Only the **encoders** are shared,
and here they are **payloads**, not model-side attacks.*

*Provenance: grounded in the S4 scoop-check + full deep-read (11 papers, 4 parallel readers, 2026-07-19;
synthesis in `text_docs/agent_injection/proposal.md §4`) and extended with the papers surfaced by the S1
idea-check (cspaper.org, 2026-07-20). Citation keys reference `paper/literature/my_base.bib` (agent-injection
block `[1]`–`[16]`). PDFs are in `paper/literature/`.*

---

## 1. The gap and our delta

**Gap.** No published work systematically measures whether an **encoded** indirect-injection payload evades
**injection-specific** defenses on an agent, scored by whether the agent **completes the injected action**, nor
frames it as the agents' injection defenses inheriting the content guards' *surface-not-decoded* blind spot.
The pieces exist but are scattered: the rigorous agentic-IPI harnesses test natural-language (NL) injections
only (§2); the phenomenon appears only as one-off anecdotes and two explicit "future work" flags (§4, §6);
encoding-as-evasion is otherwise studied non-agentically (§4); and the adaptive-attack line that shares our
metric and frame uses gibberish optimization rather than human-readable, decodable encoding (§5).

**Delta (one sentence).** Unlike the anecdotal encoded bypasses (Greshake's Base64, Bhagwatkar's Braille), the
adaptive *gibberish-suffix* agent-injection attacks, the chat-domain decode-asymmetry insight, and the
non-agentic encoding studies, this line is the **first systematic, controlled characterization of semantic +
image encoding as an evasion axis against injection-*specific* defenses (spotlighting / datamarking /
isolation / prompt-shield) on LLM agents, action-scored, with plain-vs-encoded controls and the
decode-blind-spot unifying frame.**

**Scoop verdict:** Level 3 / Medium Overlap, delta SAFE (both High-risk candidates defanged on deep-read;
`proposal.md §4`). The idea-check (2026-07-20) independently confirmed the placement — "the idea diverges by
testing reversible encodings and image-rendered payloads … addresses the gap of evaluating whether existing
defenses are overly reliant on surface-form lexical patterns at the expense of decoded semantics" — and
surfaced no new scoop, but it added one defense (MELON, §3) that sharpens the claim.

---

## 2. Agentic indirect-injection harnesses (the evaluation substrate)

- **AgentDojo** (`debenedetti2024agentdojo`, NeurIPS'24) — the preferred harness: a dynamic environment with
  **deterministic action-level scoring** of IPI attacks and defenses plus a benign-task utility score. Attacks
  are **natural-language** injections; encoders slot in as a new `attack()`, and success = the agent executing
  the injected action. This is the anchor for the plain-vs-encoded control.
- **InjecAgent** (`zhan-etal-2024-injecagent`, Findings-ACL'24) — the lightweight complement: 1,054 test cases,
  17 user tools × 62 attacker tools, two intent types (direct harm, data exfiltration); NL injections only.
- **Agent Security Bench / ASB** (`zhang2025asb`, ICLR'25) — a broad benchmark (10 scenarios, 400+ tools, 27
  attack/defense methods, 7 metrics, 13 backbones). A possible **complementary** harness — encoded-payload
  attacks could integrate into its testbed — though its breadth trades off the fine-grained action-scoring
  AgentDojo gives.
- **NetInjectBench** (`shayoni2026netinjectbenchbenchmarkingindirectprompt`) — network-ops IPI, action-scored,
  and it *does* evaluate Spotlighting / Self-Reminder on agents (a defense-eval parallel to ours) — but its
  payloads are **100% NL authority-impersonation, zero encoding**. Orthogonal, not a scoop.

All four share the same blind spot for our purposes: **none tests decodable-encoded payloads against a
defense-in-the-loop.**

---

## 3. Injection-specific defenses — the surface-form vs. behavioral split

The idea-check's key contribution was forcing this distinction, which *localizes* our claim rather than
weakening it: **encoding is predicted to defeat surface-form defenses and NOT behavioral ones.**

**Surface-form / provenance defenses (the class we expect to fall).** These recognize an imperative NL surface
in ingested data — delimiting it, datamarking it, or classifying it.
- **Spotlighting** (`hines2024defending`, 2024) — the canonical injection defense (delimiting / datamarking /
  encoding the *data boundary*). Its own "encoding" variant encodes the *whole document as a defender signal*;
  the attack payload is always plain English. Crucially, **§5.4 explicitly flags a reversible-encoding
  attacker who pre-encodes the payload — and never builds it.** That is our attack, named as future work.
- **Defense by Leveraging Attack Techniques** (`chen-etal-2025-defense`, ACL'25) — a training-free **surface
  shield-prompt** defense (inverts attack techniques into a defensive suffix); SOTA among prompt-based
  defenses. Exactly the surface-pattern defense the decode blind spot predicts encoding will slip past — a
  clean baseline to beat.
- **Firewalls / bespoke Sanitizer** (`bhagwatkar2025indirect`, NeurIPS'25) — a firewall/sanitizer framework;
  see §4 for its one Braille anecdote.

**Behavioral / semantic defenses (the resistant class — the sharpening).**
- **MELON** (`zhu2025melon`, ICML'25) — **Masked re-Execution and TooL comparisON**: re-executes the agent
  trajectory with a masked user prompt and flags an attack when the actions match (the action depended on the
  injected task, not the user task). SOTA on AgentDojo. Because it keys on **action-dependence, not surface
  form**, encoding should NOT change what it detects — making MELON the **resistant contrast baseline** that
  localizes the blind spot to surface-form defenses, and the natural class our later `recover-before-act`
  defense belongs to.
- **Recursive-LM procedural defense** (`shavit2026recursivelanguagemodelsjailbreak`) — a procedural jailbreak
  defense for tool-augmented agents; another non-surface-form point of comparison.

**Consequence for the story:** contribution #1 should be scoped to injection-specific **surface-form**
defenses, with MELON reported as the semantic defense encoding does *not* beat — turning a potential threat
into a pillar (the blind spot is a property of the surface-form class, and quantifying which family falls is
itself the result).

---

## 4. Encoded / obfuscated / non-plaintext injection payloads (the attack vector)

**One-off encoded anecdotes (own only "it can happen once").**
- **Greshake et al.** (`10.1145/3605764.3623985`, AISec'23) — the founding IPI paper; a **Base64 Bing-Chat**
  demo is the first informal "encoding evades detection" note. One anecdote, no defense-in-loop, no sweep.
- **Bhagwatkar et al.** (`bhagwatkar2025indirect`, NeurIPS'25) — a **single Braille** example bypassing the
  authors' **own bespoke Sanitizer** (not spotlighting), where **Base64 and whitespace were tried and
  FAILED**, explained by a narrow **"rare-token" hypothesis**; no sweep, no control, one defense. It caps only
  "first to show *any* bypass" (which Greshake already owns), not "first systematic." **Note: the Braille
  result is v2-only (2026-03) — cite the v2, not the stale v1.**

**Structural (non-decodable) parallels — close neighbors, different mechanism.**
- **ChatInject** (`chang2026chatinject`, ICLR'26) — forges **native chat-template markup** inside tool outputs;
  lifts ASR 5.18→32.05% on AgentDojo and 15.13→45.90% on InjecAgent (multi-turn variant to 52.33% on
  InjecAgent), and existing prompt-based defenses are largely ineffective. This is a **structural** surface, not
  a decodable encoding the model must *decode* — a parallel blind spot, an excellent baseline/comparison, not a
  scoop.
- **AdvAgent** (`xu2025advagent`, ICML'25) — **RL-optimized invisible-HTML** indirect injection on web agents
  (GPT-4-based); prompt-based defenses give "only limited protection." Structural-obfuscation support for the
  claim from the web-agent side.

**Visual injection.**
- **VPI-Bench** (`cao2026vpibench`, ICLR'26) — image + agent + action, but the vector is a **plaintext pop-up
  (no decode step)** and there is **no injection guard**. Its §A explicitly names our contribution as future
  work: "conceal malicious prompts from users while keeping them detectable by screenshot-based agents." The
  image-rendered payload variant (`ir_plain`) is our answer to that.
- **Reverse CAPTCHA** (`graves2026reversecaptchaevaluatingllm`, 2026) — invisible-Unicode instruction
  injection; **quantifies that tool-use amplifies compliance** with an encoded payload (Cohen's *h* up to
  **1.37**; compliance → 98–100% with tools). This is our **seed plausibility** — the mechanism is measured,
  not hypothetical.

**Non-agentic encoding (the gap evidence).**
- **Uysal et al.** (`uysal2026multilingualobfuscated`, 2026) — Base64 / hex / ROT13 on **plain chatbots**, no
  agent, no defense-in-loop. Confirms encoding-as-evasion is studied, but never in the agent + defense setting.

---

## 5. Adaptive & evasion attacks on agent injection defenses

Our metric (action completion) and frame ("defenses fall to evasion") are shared by an adaptive-attack line —
but its **mechanism is the distinguishing axis**: gibberish optimization vs. human-readable, decodable
encoding.
- **Adaptive Attacks Break IPI Defenses** (`zhan-etal-2025-adaptive`, NAACL'25) — breaks agent injection
  defenses, action-scored, via **GCG / AutoDAN gibberish suffixes** (white-box optimization). Our black-box,
  readable-encoding route is the distinguishing mechanism.
- **The Attacker Moves Second** (`nasr2025attackermovessecondstronger`, 2025) — stronger adaptive attacks
  bypass defenses against jailbreaks and prompt injections; same "adaptivity beats static defenses" lesson,
  again via optimization rather than a payload the model *decodes*.

---

## 6. The decode-blind-spot lineage & non-scoops

- **Controlled-Release Prompting** (`fairoze2026bypassingpromptguardsproduction`, 2026) — the **decode-capability
  asymmetry** insight ("a payload only the model can decode slips past a guard that cannot"), but on **chat
  platforms / direct jailbreak**, not agents / action. The insight twin, in a different domain; we relocate it
  to the agent's untrusted **data channel** and pair it with the action metric.
- **Large-scale IPI competition** (`dziemian2026vulnerableaiagentsindirect`, 2026) — 272K submissions, but
  "Encode or Obfuscate Text" is **1 of 27 incidental post-hoc tags (ASR 3.4%)**, text-only, and injection
  defenses were **explicitly turned OFF** ("out of scope"). **Not a scoop.**

**Two independent "future-work" flags** (Spotlighting §5.4 and VPI-Bench §A, both above) name our exact
contribution and never build it — the strongest evidence the systematic version is genuinely open, tempered by
the honest cost that a hot, fast-moving field makes it an obvious next step (scoop-race risk).

---

*Maintenance: this review is the agent line's single prior-art home. Add new agent-injection prior art here
(with its `my_base.bib` key) as the line advances; keep model-side citations in the sibling repo's review.*
