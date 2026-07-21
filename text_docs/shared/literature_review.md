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
idea-check (cspaper.org, 2026-07-20), then further extended (2026-07-20) with the deep-read of the
compositional-harm and best-of-N scoop-check papers (§§5, 7, 8; 9 PDFs, 4 parallel readers). Citation keys
reference `paper/literature/my_base.bib` (agent-injection block `[1]`–`[23]`). PDFs are in `paper/literature/`.*

---

## 1. The gap and our delta

**Gap.** No published work systematically measures whether an **encoded** indirect-injection payload evades
**injection-specific** defenses on an agent, scored by whether the agent **completes the injected action**, nor
frames it as the agents' injection defenses inheriting the content guards' *surface-not-decoded* blind spot
(this line's own **published** model-side result, `pmlr-v318-zhang26a`; §6).
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

**Pivots considered and closed (2026-07-20).** Two *stronger*-looking directions were scoop-checked after the
idea-check and found crowded, which is why this line stays on the encoded-injection axis: **single-agent
compositional action harm** (per-step-benign / jointly-harmful) is **fully scooped** (§7), and **best-of-N over
encodings** is **heavily anticipated** (§5). The **multi-agent** extension (§8) is substantially anticipated by
`hu2026localmonitorsmisscompositional` but leaves an action-level + injection-defense slice open. Net: the
encoded-injection-vs-surface-form-defenses result remains the one unclaimed contribution; the pivots survive
only as an *added axis* (an N-budget dimension, §5) or a *reshaped* future paper (§8).

---

## 2. Agentic indirect-injection harnesses (the evaluation substrate)

- **AgentDojo** (`debenedetti2024agentdojo`, NeurIPS'24) — the preferred harness: a dynamic environment with
  **deterministic action-level scoring** of IPI attacks and defenses plus a benign-task utility score. Attacks
  are **natural-language** injections; encoders slot in as a new `attack()`, and success = the agent executing
  the injected action. This is the anchor for the plain-vs-encoded control.
- **InjecAgent** (`zhan-etal-2024-injecagent`, Findings-ACL'24) — the lightweight complement: 1,054 test cases,
  17 user tools × 62 attacker tools, two intent types (direct harm, data exfiltration); NL injections only.
- **Agent Security Bench / ASB** (`zhang2025agent`, ICLR'25) — a broad benchmark (10 scenarios, 400+ tools, 27
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
- **Independent brittleness evidence — `owireduashley2026attacksuccessrateactiongradedseverity`** (arXiv
  2607.07474) — on the *same* harness (AgentDojo) and defense family we target, an action-graded severity study
  finds a **"spotlighting paradox"** (spotlighting lowers binary ASR 48→40% on GPT-4o-mini yet *raises* the
  severe-episode tail, L5–L6 count 1→3) and **channel substitution** (a tool-filter defense reaches 0% ASR
  while the same payload still fires through an unfiltered `create_calendar_event` field). Surface-form
  injection defenses are brittle by their own metric, *before* any encoding — motivation, not a scoop.

**Behavioral / semantic defenses (the resistant class — the sharpening).**
- **MELON** (`zhu2025melon`, ICML'25) — **Masked re-Execution and TooL comparisON**: re-executes the agent
  trajectory with a masked user prompt and flags an attack when the actions match (the action depended on the
  injected task, not the user task). SOTA on AgentDojo. Because it keys on **action-dependence, not surface
  form**, encoding should NOT change what it detects — making MELON the **resistant contrast baseline** that
  localizes the blind spot to surface-form defenses, and the natural class our later `recover-before-act`
  defense belongs to.
- **Caveat — MELON resists *non-adaptive* encoding, not adaptive attack.**
  `nasr2025attackermovessecondstronger` breaks MELON on AgentDojo (**76% ASR blind, 95% with defense
  knowledge**) via an adaptive genetic search (§5). The sharpening is therefore scoped precisely: encoding
  defeats surface-form defenses *single-shot*, and MELON is the resistant contrast **within the blind /
  single-shot regime** our plain-vs-encoded control uses — we report the adaptive-attack boundary honestly
  rather than claim MELON is robust in general.
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
- **The Attacker Moves Second** (`nasr2025attackermovessecondstronger`, 2025) — the strongest adaptive result
  for us: its adaptive genetic search runs against our exact defense suite (spotlighting, prompt sandwiching,
  RPO, data sentinel, **and MELON**) on AgentDojo and **breaks MELON — 76% ASR blind, 95% with defense
  knowledge**. Lesson: MELON's resistance (§3) holds against a *blind/static* encoded payload, not a
  *defense-aware adaptive* attacker — a boundary we state explicitly rather than over-claim. Mechanism is still
  optimization, not a payload the model *decodes* — our distinguishing axis.
- **Assessing Automated Prompt Injection** (`hofer2026assessingautomatedpromptinjection`, 2026 — by the
  AgentDojo team, ETH) — defines **Success@N** ("at least one of N attempts succeeds"), **action-scored on
  AgentDojo** via the deterministic check functions (n=4 independent GCG/TAP optimization restarts × m=6 eval
  repeats); black-box TAP beats white-box GCG. So **the any-of-N / best-of-N framing on agent injection is
  already published** — but its N-repeats are *same-optimizer reseeds* (gibberish / social-engineering), **not**
  a curated structural/encoding bank, and it tests **zero defenses** ("focuses on evaluating attack
  effectiveness rather than defenses").
- **Sampling-aware Adversarial Attacks** (`beyer2026samplingaware`, ICLR'26) — the foundational mechanism cite
  (and the source Hofer credits): casts attacks as a *compute-allocation* problem between optimization and
  sampling, with Best-of-N a degenerate special case; +37 pp ASR / up to 100× cheaper. But it is **model-only**
  (single-turn chatbot harm judged by StrongREJECT) — no agent, no indirect injection, no encoding, no defense
  suite.

**Consequence for a best-of-N-over-encoding pivot (exploratory scoop-check, 2026-07-20).** Between Hofer
(Success@N on AgentDojo), Beyer (BoN-as-compute-allocation), Hughes' Best-of-N (in the sibling bib), and
Anthropic's publicly-disclosed internal "Best-of-N attacker" for its browser extension, the *framing* is
heavily anticipated. The surviving slice is narrow: a **blind (non-adaptive, no defense feedback) best-of-N over
a fixed structural/encoding bank**, crossed with the full defense suite **including MELON**, isolating whether
the encoding channel amplifies bypass beyond a surface-noise budget — and whether MELON's fall in Nasr et al. is
an artifact of *adaptivity* rather than budget alone. That is at most an **added axis on this paper's design**
(the payload axis gains an N-budget dimension), not a standalone paper (`proposal.md §4` exploratory scoop).

---

## 6. The decode-blind-spot lineage & non-scoops

- **Mathematical-encoding jailbreaks** (`pmlr-v318-zhang26a`, PMLR v318 / Canadian AI'26 — this line's own
  **published** model-side work, and the origin of the encoders reused here as payloads) — established that
  encoding a harmful request as a genuine mathematical problem (set theory / formal logic) bypasses **content
  guards** at 46–56% ASR across 8 models, precisely because the guards match *surface* semantics, not *decoded*
  content. This is the **content-guard decode blind spot** the agent line ports to the injection-defense setting.
  **Caveat for our capability axis:** it found **newer models (GPT-5/-mini) MORE robust** to math-encoding — the
  *opposite* direction to the agent line's "more-capable-more-vulnerable" bet. The reconciliation (content-guard
  evasion is gated by *alignment*, which scales up; agent action-injection is gated by *decoding competence*, which
  may not) is exactly what the capability-scaling pilot must establish — either answer is a finding.
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

## 7. Compositional action harm on agents — a crowded landscape (the single-agent pivot is closed)

A direction considered for this line — **compositional action harm** (each individual tool call benign in
isolation, the *composed* trajectory harmful) as a **single-agent** attack — was scoop-checked (2026-07-20) and
found **fully occupied**. Recorded here so the line does not re-open it. The through-line that keeps our paper
distinct: **none of these use *encoding*** — they decompose intent into benign-looking *natural-language* steps,
an axis orthogonal to our encoded-payload evasion.

- **STAC** (`li2026stacinnocenttoolsform`, arXiv 2509.25624; preprint) — the canonical statement. An automated,
  environment-verified pipeline generates **Sequential Tool Attack Chains** in which every step but the last is
  individually benign, reaching **91.2% mean final ASR** across 8 agents, **action-scored** on SHADE-Arena (an
  AgentDojo extension) + Agent-SafetyBench, and shows prompt-based defenses (spotlighting, a harm-benefit
  "reasoning" defense, ToolShield) are insufficient. Single-agent, single session, **no encoding**. This is the
  paper that closes single-agent compositional harm as a standalone contribution. (It does **not** test MELON —
  an open comparison, same as for the other compositional papers.)
- **Context-Fractured Decomposition** (`lin2026contextfractureddecompositionattackstoolusing`, arXiv 2606.09084;
  ICML'26 FAGEN workshop) — the **cross-session / provenance-gap** variant: benign artifacts are planted across
  context-reset sessions and recombined by an "innocent executor," action-scored on an AgentDojo exfiltration
  subset. It **explicitly hands the single-session case to STAC** ("STAC … operates within a single contiguous
  trajectory … Our attack class is distinct"), confirming the area has already split into named sub-variants. No
  encoding; only detection probes, no deployed defense (provenance tagging is future work). Workshop-tier.
- **SCR / Skill Composition Risk** (`xie2026benignisolationharmfulcomposition`, arXiv 2606.15242) — the literal
  framing "**benign in isolation, harmful in composition**," here for agent *skill ecosystems* (an upstream
  skill's output becomes a downstream trust / capability / authorization signal). Single-agent, own SCR-Bench,
  state-scored, no encoding, no new defense — the strongest evidence the phrase itself is a named risk category.
- **AgentLAB** (`jiang2026agentlabbenchmarkingllmagents`, arXiv 2602.16901) — a long-horizon-attack benchmark
  whose **tool-chaining** family (1 of 5) is exactly per-step-benign / jointly-harmful; NL social engineering,
  no encoding. Its finding that single-turn / classifier defenses fail to generalize to long-horizon attacks
  *supports* our surface-form-brittleness motivation.
- **Sequentially Contextual Harm** (`yueh-han2025monitoring`, ICLR'25 Building-Trust workshop) — the earliest
  statement of the insight (decomposition into benign subtasks slashes refusal; harm "can only be identified by
  analyzing the *composition*"). It monitors the **user-instruction channel** (not tool outputs), so it is
  adjacent to — not identical with — the MELON-style tool-output behavioral class (§3); it also finds
  trajectory-level LLM monitoring real but **fragile** (degraded by random-subtask noise), reinforcing why
  per-step defenses are insufficient in principle. It explicitly leaves **cross-conversation / cross-agent**
  composition open — the segue to §8.

**Verdict:** single-agent compositional action harm = **Level 1 (fully scooped)**; not a standalone direction
for this line. It stays valid *related work* (per-step defenses are provably insufficient), and the honest
distinction from our paper is the **encoding axis**, which none of these touch.

---

## 8. Multi-agent / distributed compositional harm — the future coordinate (substantially anticipated)

The line's broadest future coordinate (`future_work.md §4`) — harm *distributed across agents*, each agent's
contribution benign, the *joint* behavior harmful — is largely anticipated by one 2026 paper, which reshapes
what that future paper can claim:

- **Distributed Backdoors** (`hu2026localmonitorsmisscompositional`, arXiv 2607.11751) — formalizes an
  **observability boundary** (Prop. 1: once fragments are locally benign, *no* monitor confined to a local view
  separates attack from benign beyond ε) and instantiates it: a harmful payload is split into K=3 **encoded**
  fragments (base64 / hex / a reused DemonAgent codec), each carried in a benign-looking report by a different
  agent; only the assembled-and-decoded object is malicious. A marker-free one-class monitor recovers code
  payloads (0.874 AUROC) but **fails on natural-language payloads** (0.406); a decoded-view gate blocks 50/50
  only as a *diagnostic ceiling* (it assumes the codec is known). Multi-agent, action-scored
  (credential-exfiltration execution).

This **substantially scoops** the future §3 on its core idea (per-agent-benign / joint-harmful + a
wider-view / joint defense) **and already uses encoded fragments** — so the future paper cannot simply re-stake
"distributed compositional harm + joint verification." What it leaves open, and where §3 must relocate:
(1) **action / tool-call-level** distributed harm (sensitive tool calls split across agents), not assembled
executable-code payloads — the authors' own monitor collapses on non-code harm and they name it open;
(2) a **genuinely new encoding scheme** (this line's set-theory / formal-logic / cipher / classical-Chinese /
homoglyph encoders) rather than reused published codecs; (3) generalizing **injection-specific** defenses
(spotlighting / isolation / prompt-shield) to the multi-agent joint view — untouched (hu2026 tests only
observation-window monitors). §3, if pursued, is scoped to that intersection.

---

*Maintenance: this review is the agent line's single prior-art home. §§1–6 cover the current paper's prior art
(encoded indirect injection vs. injection-specific defenses); §§7–8 record the compositional-harm and
multi-agent scoop-checks — the directions this line deliberately does *not* pursue single-agent, and the
reshaped future coordinate. Add new agent-injection prior art with its `my_base.bib` key as the line advances;
keep model-side citations in the sibling repo's review.*
