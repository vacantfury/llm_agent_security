# Research Proposal — Smuggled Actions: Encoded Indirect Prompt Injection on LLM Agents (`agent_injection`)

**Workflow stage:** S6 · design + cost — **S4 scoop + deep-read DONE (Level 3 Medium, delta SAFE, 2026-07-19); S1 idea-check RETURNED + CONFIRMED (cspaper.org, 2026-07-20 — no new scoop; MELON surfaced, which sharpens the claim; §4).** Prior art in `literature_review.md §1` (full map §§2–6). Both High-risk candidates defanged on inspection. **Order from here (owner-corrected 2026-07-19 — keep this sequence):** (1) preliminary proposal ✅ → (2) S4 literature / scoop search ✅ → (3) `idea_check.md` ✅ (returned + confirmed, cspaper.org 2026-07-20) → (4) ✅ S5 main story (delta + positioning locked; surface-form-vs-behavioral sharpening folded in; compositional & multi-agent pivots scoop-checked and closed — lit review §§5/7/8) → (5) ✅ S6 design + cost — **owner ratified the direction 2026-07-20** (Paper E go; capability-scaling pilot authorized; blind-BoN axis held) — full design in `design.md` → (6) **NOW: S7 build — no-spend scaffolding BUILT + verified 2026-07-21** (attack `encoded_*`; defense factory + MELON port + PIGuard; `src/harness` run driver over AgentDojo; `src/scoring`; `runner --dry-run` assembles all cells offline; scoring reproduces the thesis split on synthetic data — design.md §8). **Pilot run GATED on owner-go + API keys.** Paper E, off the July AAAI crunch (Papers C/D own that); targets a later cycle (§8).

*Codename: **Smuggled Actions** (Paper E — the alias **E was reassigned from the parked `judge_reliability` direction** in the sibling repo `imaging_text_attacks_for_llm_jailbreaking`, 2026-07-19). Origin: this repo's `text_docs/shared/future_work.md §1` (the agent-side line, migrated from the sibling's future_work §5) + the compositional-harm identity. **Attack-first** — the attack is this paper; the defense is the deliberately-later half (`future_work.md §2`). Full paper-facing title refined at writing.*

---

## 1. Decision & posture (RATIFIED by owner 2026-07-20)

- **Paper E = an ATTACK-FIRST agent-security paper.** The question: does an **encoded** indirect-injection payload defeat **injection-specific defenses** and drive a harmful agent **action**? It leaves the model-only setting of Papers A–C entirely — a *separate line*, not a follow-on.
- **Home: THIS repo, `agent_injection` namespace.** It reuses this line's encoder suite and image transforms **as payloads**; the genuinely new build is the agent-harness integration + the injection-defense baselines + the action-completion metric.
- **One-line identity — the AGENT coordinate of the coverage / decode-gap thesis.** Papers A–C study *where harmful content is placed* (encoding, modality) against a **model** whose only output is text and whose only adversary is the prompt author. This paper moves **both axes at once**: the adversary becomes a **third party** controlling data the agent *ingests* (a tool output, a retrieved document, an on-screen image — *indirect* injection), and the harm becomes an **action the agent takes**. The claim: **injection defenses tuned on natural-language injections inherit a decode blind spot** — an *encoded* instruction slips past them exactly as encoded harm slips past content guards in Paper C.
- **Attack-first, by design.** A payload is portable — a data blob dropped into any harness — whereas a defense must hook the agent's internals. The attack (this paper) stays eval-only and decoupled; the defense + flagship demo (`future_work.md §2`) is the coupled, later half. **This paper's core is the attack.**
- **Scope discipline (the lesson of this very line).** Target the **minimal agent pattern** — untrusted-data → context → action — on a **standard harness** (AgentDojo / InjecAgent) swept across backbones. **Not** a bespoke complete agent whose idiosyncratic structure would make the result coupled and un-general. Generality comes from the multi-scaffold × multi-backbone sweep, exactly as the model results here generalize across VLMs. **Multi-agent composition is a SEPARATE, later paper** (`future_work.md §4`), explicitly not this one.
- **Posture on scoop (honest, load-bearing).** Agent indirect-injection is a crowded field; the unclaimed sliver is **ENCODING as an evasion axis against injection-specific defenses, scored by action completion**. §4 is the make-or-break gate — run BEFORE `idea_check.md` and before any commitment.

## 2. The idea (core claim)

**Claim.** An **encoded** indirect-injection payload raises **injected-action success** over a plain-language payload against **deployed injection defenses** — spotlighting, delimiter / data-isolation, prompt-shield / classifier guards — that are tuned on natural-language injections. These defenses have **no pure-model analog**, so defeating them is a genuinely new result, not a re-run of text-side jailbreaking.

**Mechanism (the through-line).** Injection defenses detect or neutralize instructions hidden in ingested data by recognizing an imperative **natural-language surface form** (delimiting the data, datamarking it, or classifying it). An **encoded** instruction (set-theory / cipher / code / classical-Chinese, or image-rendered) presents a surface the defense was never tuned on — yet the backbone still **decodes-and-obeys** it. This is the same **surface-vs-decoded gap** as Paper C, now relocated to the agent's untrusted *data channel*. **Scope refinement (from the S1 idea-check):** this predicts encoding defeats *surface-form* injection defenses (spotlighting / isolation / prompt-shield / shield-prompt) specifically — and NOT *behavioral* defenses like MELON (`zhu2025melon`), which key on action-dependence rather than surface form. That split localizes the blind spot to the surface-form class and is itself a result; MELON enters as the resistant contrast baseline.

- **Success = action completion** (the agent actually executed the injected instruction / called the sensitive tool) — the agent-native metric, **not** a harmful-text verdict.
- **Falsifiable:** encoded payloads raise injected-action success over plain-language payloads against deployed injection defenses, **across ≥3 scaffolds × backbones**. **Refutation is itself a finding** — if encoding gives no lift once an injection guard is present, that says injection defenses, unlike alignment, are encoding-robust (a clean, publishable negative).

## 3. Experiment design (preliminary — firmed at S6)

The core artifact is a matrix — **payload-encoding × injection-defense × scaffold × backbone** — measuring **injected-action success** against a programmatic ground truth of whether the sensitive action fired.

- **Payload axis.** Plain-language injection (control) vs this line's encoders (set-theory / formal-logic / code / classical-Chinese / cipher / homoglyph) vs **image-rendered** (`ir_plain`, for VLM / computer-use agents). The encoders + transforms are reused verbatim as payloads.
- **Defense axis.** No-defense (control) vs deployed injection defenses: **spotlighting** (delimiting / datamarking / encoding the data boundary), **delimiter / quarantine isolation**, **prompt-shield / classifier guards** on ingested content. Each wrapped as an evaluatable baseline, deployed as its authors intend. Plus a **behavioral contrast defense** — **MELON** (masked re-execution + tool comparison; `zhu2025melon`), expected to *resist* encoding, included to show the blind spot is specific to the surface-form class (idea-check finding, §4).
- **Scaffold × backbone.** ≥3 agent scaffolds on a standard harness (AgentDojo / InjecAgent — tool-use injection benchmarks with built-in attack + utility scoring) × multiple backbones (the repo's served + API models), for generality.
- **Metric.** Injected-action success rate (attack) **and** benign-task utility (the harness's own utility score, to bound over-blocking), per cell. **Headline** = encoded payloads lift injected-action success over plain payloads *specifically where an injection defense is present*.
- **Capability-scaling analysis (the headline-finding axis, ratified 2026-07-20).** Treat backbone capability as a *first-class analysis dimension*, not just a generality sweep: order the backbones by capability and test whether encoded-injection success *rises* with capability (better decoders → more exposed). This is the paper's candidate non-obvious finding; a flat/negative trend is itself a clean result.
- **Pilot first (S6 → gated run).** Before the full matrix, a small capability-scaling pilot — ~5–6 backbones spanning a capability range × plain + 2 encoders × spotlighting + no-defense × 1 scaffold × an AgentDojo task-injection subset — decides whether the capability trend and the encoding lift exist at all. Cost estimate in §10; the pilot runs only after the S7 harness build and the owner's go on spend.

## 4. Novelty & prior-art — THE gate (S4, UNRUN — make-or-break; it GROUNDS `idea_check.md`)

**Preliminary — the literature search is the next step, and `idea_check.md` is written from its findings (owner-corrected order).** Agent indirect-injection is an active, crowded field; the paper survives only if ENCODING-as-evasion-axis against injection-specific defenses is unclaimed.

- **Adjacent prior art to differentiate (to be verified by the search):** AgentDojo / InjecAgent / ASB (agent-injection benchmarks) · spotlighting (Hines et al.) / data-isolation / prompt-shield (the injection defenses we test) · Imprompter and obfuscated / adversarial-suffix injection work · the general indirect-injection framing (Greshake et al.). **The most dangerous partial scoop** would be an existing "obfuscated / encoded indirect injection defeats spotlighting / prompt-shield" result — the search must find it if it exists.
- **Provisional delta:** nobody has systematically measured ENCODING (semantic + image) as an evasion axis against **injection-specific** defenses, scored by **action** completion, **across scaffolds × backbones** — the agent coordinate of this line's coverage / decode-gap identity, with a plain-vs-encoded control isolating the encoding effect.
- **Gate procedure (the corrected order):** `scoop-check` (dual-channel — signature terms + adjacent-subfield aliases: indirect prompt injection, tool-use / agent security, spotlighting / data-isolation, obfuscated / encoded injection, computer-use-agent attacks) → `lit-review-loop` (stage bib → owner verify + download → read → write the review) → **THEN write `idea_check.md`** grounded in the findings → **advance only if the delta survives.**

### S4 scoop-check #1 — 2026-07-19 (Level 3, Medium Overlap — leaning High; delta defensible, two unresolved candidates)

Ran `scoop-check` (3 search angles × ~30 queries via subagents) + the in-repo Step-0 check. **No paper does the full 4-axis combination** (encoded payload × injection-specific defense × agent action-completion × decode-blind-spot frame), **but the phenomenon has been demonstrated once and the pieces are scattered across an active field.** Verdict: **Level 3 (Medium Overlap), with a High-Overlap caveat** pinned to one appendix result + two unresolved candidates.

- **⚠️ Most dangerous scoop — `bhagwatkar2025firewalls` (NeurIPS'25, 2510.05244).** Appendix E shows a **Braille-encoded injection bypassing their own Sanitizer on AgentDojo, action-scored** — the single closest precedent. It **kills the "first to show encoding defeats an agent injection defense" headline.** Delta survives only as: *systematic* (vs one anecdote), *multi-encoding + spotlighting/isolation/prompt-shield families* (vs one custom Sanitizer), *plain-vs-encoded control*, and the *decode-blind-spot* framing (they hypothesize a narrower rare-token cause).
- **Structural analogue (different mechanism) — `zhan2025adaptiveipi` (NAACL'25, 2503.00061)** + the already-downloaded "Attacker Moves Second": break agent injection defenses, action-scored — OUR metric + frame — but via **GCG/AutoDAN gibberish suffixes, not semantic/decodable encoding.** Our mechanism (a readable payload the model *decodes*) is the distinguishing axis.
- **Insight twin (different domain) — `fairoze2025` controlled-release** (already in bib): the decode-capability-asymmetry "decode blind spot" insight, but chat platforms / direct jailbreak, not agents / action.
- **Gap evidence (encoding studied, but not on agents) — `uysal2026multilingualobfuscated` (2606.29602)** tests base64/hex/ROT13 on plain chatbots (no agent, no defense-in-loop); `hines2024spotlighting` never stress-tests encoded payloads. **Encoding-in-agents is only touched** (`graves2026reversecaptcha` invisible-Unicode, tool-use amplifies compliance; `cao2025vpibench` image+agent+action but plain UI vector).
- **UNRESOLVED (could push to High) — `dziemian2026agentcompetition` (2603.15714)** (272K-submission competition, action-scored — did it test encoded payloads systematically?) and **`kong2024injectbench`** (2024 VT thesis, base64/hex/ROT13 IPI benchmark — agentic?). Both need the owner's verify+download + a deep read before the verdict firms.

**Delta (one sentence):** unlike the Firewalls Braille *appendix anecdote*, the *adaptive-gibberish* agent-injection attacks, the *chat-domain* decode-asymmetry insight, and the *non-agentic* encoding studies, this paper is the **first systematic characterization of semantic + image encoding as an evasion axis against injection-*specific* defenses (spotlighting / isolation / prompt-shield) on LLM agents, action-scored, with plain-vs-encoded controls and the decode-blind-spot unifying frame.**

**Pattern vs `judge_reliability`:** this is a **more defensible delta** — judge-reliability's insight was owned by an entire active subfield (scalable-oversight scaling laws); here the phenomenon is only an *appendix anecdote* and the systematic version is genuinely open. **But two honest costs cut the other way:** (a) the field is *much hotter / faster-moving* (a scoop-race risk — the systematic version is an obvious next step others may take), and (b) the *build cost* is higher (external agent harness). **Gate outcome = advance to deep-read the scoop-critical candidates.** Full log `outputs/scoop_check/2026-07-19/`; prior art written up in `literature_review.md §1`.

### S4 deep-read RESOLVED — 2026-07-19 (verdict FIRMS to clean Medium; both dangerous candidates DEFANGED)

Owner downloaded 11 papers; deep-read (4 parallel readers, full-text). **The two candidates that could have pushed to High both collapsed on inspection → verdict settles at a clean Level 3 (Medium), and the "first systematic characterization" framing is SAFE:**
- **`bhagwatkar2025indirect` (the "most dangerous scoop") — defanged.** The Braille bypass is **v2-only** (2026-03; our downloaded PDF is stale **v1**, which lacks it — **owner action: replace with v2 for citation**). It is **one anecdote** (1 model, 1 task) against their **own bespoke Sanitizer** (not spotlighting), where **base64 + whitespace were tried and FAILED**, explained by a narrow **"rare-token" hypothesis**, no sweep/control/cross-defense. Caps only "first to show *any* bypass" (which `greshake` already owns), NOT "first systematic."
- **`dziemian2026...` competition — not a scoop.** "Encode or Obfuscate Text" is 1 of 27 incidental post-hoc tags (ASR 3.4%), text-only, and injection defenses were **explicitly turned OFF** ("out of scope").
- **`shayoni2026...netinjectbench` (swapped in for the InjectBench thesis) — orthogonal.** Tests Spotlighting/Self-Reminder on agents action-scored (a defense-eval parallel), but **100% NL authority-impersonation, zero encoding**.
- **Two papers name our exact contribution as untested future work:** `cao2026vpibench` §A ("conceal prompts from users while keeping them detectable by screenshot agents") and `hines2024defending` §5.4 (a reversible-encoding attacker who pre-encodes the payload — flagged, never built). `graves2026...reversecaptcha` **quantifies** that tool-use amplifies encoded-payload compliance (Cohen's h up to 1.37) — our motivation.

**Firmed verdict: Level 3 (Medium Overlap), delta SAFE.** Claim the **first systematic, controlled characterization** (multi-encoding × injection-specific-defense families × plain-vs-encoded control × scaffold×backbone, decode-blind-spot frame, harness = AgentDojo + InjecAgent); DROP "first to show encoding bypasses a defense." Honest residual = hot field (scoop-race) + external-harness build cost. **Gate outcome = ADVANCE.** Next: write `idea_check.md` (grounded in this), then S5 story.

### S1 idea-check RETURNED — 2026-07-20 (cspaper.org; verdict CONFIRMED, no new scoop, MELON surfaced)

The cspaper.org idea-check (10 related papers) independently confirmed the placement: the idea "diverges by testing reversible encodings and image-rendered payloads … addresses the gap of evaluating whether existing defenses are overly reliant on surface-form lexical patterns at the expense of decoded semantics." No new scoop. Of 10 retrieved papers, **5 are real agent-security prior art** — MELON, ChatInject, Defense-by-Attack-Techniques, AdvAgent, ASB — now in `my_base.bib` [12]–[16] and written up in `literature_review.md §§2–6`; the other 5 are co-retrieval noise.

- **The one substantive addition — MELON (`zhu2025melon`, ICML'25).** A *behavioral/trajectory* IPI defense (masked re-execution + tool comparison), SOTA on AgentDojo, that the S4 deep-read missed. It likely *resists* encoding (it keys on action-dependence, not surface form) — so it **sharpens** the thesis rather than threatening it: encoding defeats *surface-form* injection defenses and NOT behavioral ones, which localizes the decode blind spot. Contribution #1 re-scoped to surface-form defenses accordingly (§5); MELON added as the resistant contrast defense (§3).
- **Neighbors / baselines added:** ChatInject (`chang2026chatinject`, structural chat-template attack — parallel vector, not a scoop), Defense-by-Attack-Techniques (`chen-etal-2025-defense`, surface shield-prompt — baseline to beat), AdvAgent (`xu2025advagent`, RL invisible-HTML — web-agent support), ASB (`zhang2025asb`, possible alt harness).
- **Validated future directions:** the check independently named "multi-agent collaborative security" as an open gap (= `future_work.md §4`) and "theoretical learnability bounds for instruction/data separation" (a discussion-section framing, not to be owned).
- **Venue note (weak, corpus-confounded):** all 10 retrieved papers were ICML/ICLR/ACL — evidence that ICLR / ACL-via-ARR are live homes for this work, *not* evidence against the security-venue target (cspaper under-indexes SaTML/S&P/USENIX). Keep both tracks for the S10 decision.

**Gate outcome = ADVANCE to S5** (main story). Full report pasted in `idea_check.md § "# Review"`.

### EXPLORATORY scoop-check — 2026-07-20 (best-of-N-over-encoding pivot; NOT ratified, NOT gating S5)

**Not part of the S4/S1 chain above — a separate scoop-check run on a candidate PIVOT** (best-of-N /
repeated-sampling over structural-encoding variants as the attack mechanism, vs. this paper's current
single-shot encoded payload) raised by a prior-art check, owner review pending. Recorded here so it
survives a session reset; **does not change §4's verdict or the S5 gate outcome above.**

- **Verdict: Level 2 (High Overlap)** on the *mechanism* axis specifically — the "any-of-N attempts
  succeeds, action-scored on AgentDojo" framing is **already published** by AgentDojo's own creators:
  `hofer2026assessingautomatedpromptinjection` (2606.10525) defines **Success@N** exactly this way
  (n=4 independent GCG/TAP restarts × m=6 eval repeats), action-scored via deterministic check
  functions. **But it tests ZERO defenses** and its N-repeats are same-optimizer reseeds (gibberish/
  paraphrase), not curated structural/encoding variants (cipher/code/set-theory/classical-Chinese).
- **`nasr2025attackermovessecondstronger`** (already in bib) is the second-most dangerous candidate:
  its adaptive genetic search tests our exact defense suite (Spotlighting, Prompt Sandwiching, RPO,
  Data Sentinel, **MELON**) on AgentDojo, functions as an any-of-N-attempts framing (≤800 queries),
  and organically discovers encoding variants (Hex/Base64/Unicode) as part of its strategy repertoire.
  **Critically, it BREAKS MELON (76% ASR blind, 95% with defense knowledge)** — direct evidence
  AGAINST this pivot's "MELON resists repeated attempts" sub-hypothesis, though via an ADAPTIVE,
  defense-aware attack, not a blind structural-encoding best-of-N.
  Anthropic's public but non-academic "internal Best-of-N attacker" for the Claude browser extension
  (disclosed 2025-11-24) is further evidence the *naming/framing* ("best-of-N attacker vs. agent
  prompt injection") is not novel as a concept, even though it doesn't cover the systematic
  encoding-channel × defense-family study.
- **Surviving delta (narrow, but real):** neither paper runs a **blind (non-adaptive, no
  defense-feedback) best-of-N over a fixed structural/encoding bank**, isolating whether the
  structural/encoding channel *specifically* amplifies defense bypass beyond a surface-noise best-of-N
  baseline — and whether MELON's fall in Nasr et al. is an artifact of *adaptivity/defense-knowledge*
  rather than budget alone. That controlled ablation (encoding-channel BoN vs. surface-noise BoN vs.
  no-BoN single-shot, crossed with the full defense suite incl. MELON) is open.
- **Recommendation:** if pursued, reframe as an ablation ADDED to the existing Paper E design (payload
  axis gets an N-budget dimension; MELON's resistance becomes "resists blind budget, falls only to
  adaptive/defense-aware attacks" — a sharper, still-novel claim) rather than a standalone new paper.
  Full candidates staged in `my_base.bib` (`hofer2026...`, `beyer2026...`); not yet downloaded/deep-read
  via `lit-review-loop` Phase 2 — owner call on whether to pursue before that spend.

### S7 scoop-check — 2026-07-22 (new-attack-element candidates; owner asked "can this be a clean NEW agent attack paper?")

Checked candidate new elements layered on encoded injection. Full log `outputs/scoop_check/2026-07-22/` (logged under the pre-rename labels A/A′/B; the settled repo-wide names are **a/b/c**, mapped below). All three share one idea — *keep the harmful cleartext only where a defense isn't looking* — at three strengths:
- **a — decode in the agent's head (was A): Level 2 / High Overlap — NOT a new attack; the BASELINE/CONTROL.** This is the CURRENT paper's core mechanism: the decode-capability-asymmetry insight is already owned by Controlled-Release Prompting (`fairoze2026...`, chat domain) and our existing delta already IS "relocate it to the agent data channel + action metric" (§1, lit review §6). Keep it as the control/floor, never pitch it as new.
- **b — tool-assisted self-decoding (was A′; agent invokes its OWN tools — code interpreter / translator — to decode the smuggled action): Level 4–5 / OPEN — the NOVEL CORE.** ~30 queries + ~30 abstract deep-checks found no paper doing this. Genuinely new, agent-native, and it DISSOLVES the MathEnc capability tension (impossible in a single-shot model/VLM setting, so no self-contradiction). The readable harmful text materializes only in the agent's OWN tool output, which surface-form defenses don't inspect; it also reaches encodings too hard to decode in-head. **Cost:** needs a decode-capable tool in the environment — AgentDojo's stock suites lack one → either add a benign utility tool to a suite (keeps built infra) or use a coding-agent harness (native code tool; cf. `maloyan2026promptinjectionattacksagentic`, 2601.17548).
- **c — single-agent distributed encoded injection (was B; fragments across tool outputs, reassembled in-context): Level 3 / Medium but FRAGILE — EXTENSION AXIS only.** Slice is unoccupied but one axis from `hu2026localmonitorsmisscompositional` (multi-agent encoded) and STAC (single-agent NL); Context Stitching (`karanjai2026contextcontaminationllmanalysis`, 2607.14493) proves the mechanism in a non-agent log setting. Re-opens single-agent compositional harm, which §7 CLOSED (Level 1). **Present ONLY combined with b (b+c), never c standalone** — folded into b it inherits b's novelty and stays clear of the closed-ground critique.
- **New prior art (downloaded + read + written into lit review 2026-07-22):** `chauhan2026caughtactivationpreoutputmultiturn` (2606.04141, activation-level exfil defense — mirror-image; sharpens our text-level-vs-behavioral delta, lit review §3), `karanjai2026contextcontaminationllmanalysis` (2607.14493, Context Stitching — non-agent fragmentation analog, §7), `maloyan2026promptinjectionattacksagentic` (2601.17548, coding-agent SoK — confirms b open + coding-agent shell = viable decode tool, §2/§6). Contrast attacks to cite (evade defenses but NOT via encoding — strengthen "encoding is the axis"): IterInject (2605.24659), AutoDojo (2606.15057), Agent Data Injection (2607.05120).

**DIRECTION (owner-settled 2026-07-22).** Elevate Paper E to a clean new-attack paper on the **escalation ladder a → b → b+c**, one thesis (*decode relocation*: the harmful action's readable form exists only where the defense doesn't inspect), NOT three competing contributions:
- **a = baseline/control** (already runnable with the built no-spend scaffolding).
- **b = the flagship, PRIORITIZED** — build and validate first; it is the un-scooped, agent-native core.
- **b+c = the final combined attack** — distributed encoded fragments the agent reconstructs with its own tools (most hostile to any surface-form defense); layered on only AFTER b is proven.
- Keep all three in mind throughout; the paper's narrative is the ladder. **Open sub-decision for b: the decode-tool harness** — AgentDojo + one added benign utility tool (reuses the built infra + deterministic action scoring; my recommendation) vs. a coding-agent harness (native shell = realistic decode tool, but a new harness build + less deterministic scoring). Settle before the b build.

## 5. Contributions (provisional)

1. **The first systematic measurement** of ENCODED indirect prompt injection as an evasion axis against injection-specific **surface-form** defenses (spotlighting / isolation / prompt-shield / shield-prompt), scored by **action completion** — with a **behavioral defense (MELON) as the resistant contrast** that localizes the blind spot to the surface-form class (idea-check sharpening, §4).
2. **The capability-scaling finding (the headline bet, pilot-gated).** Because the attack requires the *backbone itself* to decode the payload before it can act, more capable models — better decoders — may be **more** vulnerable to encoded injection, inverting the usual "a stronger model is a safer one" expectation. If the trend holds (the pilot decides, §3), this is the non-obvious result that lifts the paper above a routine evasion measurement; if it does not, the flat/negative trend is itself a clean, publishable finding. **Tension to reconcile (`pmlr-v318-zhang26a`):** this line's own *published* model-side MathEnc result found the OPPOSITE — newer models (GPT-5/-mini) are MORE robust to math-encoding — because content-guard evasion is gated by *alignment*, which scales up. The agent bet is that data-channel *action*-injection is gated instead by *decoding competence*, so the trend may reverse in the agent setting; but that is genuinely open, so the honest framing is the **question** "does the agent action-injection setting reverse MathEnc's model-side robustness trend?" — either answer is a finding, decided by the pilot. (Do NOT assert "more capable = more vulnerable" as settled; it contradicts our own published model-side data.)
3. **The agent coordinate of the coverage / decode-gap thesis:** injection defenses inherit the *surface-not-decoded* blind spot — a unifying account, not a new widget.
4. **A generality result** across ≥3 scaffolds × backbones (not a single-agent anecdote), with the plain-vs-encoded control isolating the encoding effect.
5. **(Later half, `future_work.md §2`)** an action-level *recover-before-act* defense + a flagship demonstration on a deployed, recognizable agent (responsible disclosure) — the coupled, engineering-heavier second contribution.

## 6. Threats to validity

- **Scoop (§4)** — the dominant risk; gated before commitment and before `idea_check.md`.
- **Harness realism** — a benchmark harness (AgentDojo / InjecAgent) may not reflect deployed agents; mitigate with multi-scaffold coverage plus one realistic scaffold; the flagship demo (`future_work.md §2`) addresses external validity but is the later half.
- **Defense fairness** — test each injection defense as its authors intend (spotlighting on the data channel, prompt-shield on ingested content) so a bypass reads as "encoding evades a *correctly-deployed* defense," not a misconfiguration (the `project_wildguard_invalid_as_asr_judge` lesson, transposed).
- **Decoder dependency** — if the backbone must itself decode the payload to act, that is the attack's *mechanism*, not a confound; note that stronger backbones (better decoders) may show MORE lift (a capability-gap echo — cite the scalable-oversight framing, do not re-own it).
- **Dual-use / disclosure** — action-harm on agents; keep the attack eval-only on benchmarks and follow responsible disclosure for any real-system demonstration.

## 7. Reused machinery + new code owed

- **Reused (no new attack build):** the encoder factory (`src/prompt_transformations/text/`) + image renderer (`ir_plain`) as **payloads**; the model registry / serving for backbones.
- **New (the real cost — be honest):** integration with an **external agent harness** — `uv add agentdojo` (pip package) and extend via its public API; no clone needed (read the installed source under `.venv/` if wiring needs it; full design in `design.md §1`); **injection-defense wrappers** (MELON built; spotlighting / classifier / isolation baselines mostly reused from AgentDojo) as baselines; the **action-completion metric** + attack/utility scoring (largely reused). Materially bigger than the eval-only VLM setup, but the framework study (2026-07-20) shows AgentDojo supplies most of it — see `design.md §§1,5,6,8`.

## 8. Publication strategy (candidate — LIVE deadline re-check at S10)

- **Target = a MAIN conference** (owner rule 2026-07-19; workshops fallback-only). Agent / LLM security maps to **IEEE SaTML / S&P / USENIX Security** and to the *ACL family (EACL / ACL / EMNLP via ARR). Off the July AAAI crunch; a later cycle. Deadlines from `text_docs/shared/conference_timeline.md` (single source); the pick stays deferred until the story / results firm up (EMNLP-vs-AACL precedent).
- **Fit:** a distinct contribution axis (agent action-harm + indirect-injection surface) from the model-side defense / attack / eval papers, inheriting this line's encoder / modality assets as payloads.

## 9. Next actions (gates — the corrected order)

1. ✅ **Preliminary proposal** (this doc).
2. ✅ **S4 · literature / scoop search — DONE** (Level 3 Medium, delta SAFE): `scoop-check` + `lit-review-loop` (bib staged, PDFs downloaded, review written to `literature_review.md`).
3. ✅ **`idea_check.md` — DONE, returned + confirmed** (cspaper.org, 2026-07-20): verdict confirmed, no new scoop; MELON surfaced → contribution re-scope (§4).
4. ✅ **S5 · main story — DONE + RATIFIED** (owner 2026-07-20): direction approved (Paper E go), capability-scaling pilot authorized, blind-BoN axis held; compositional & multi-agent pivots scoop-checked and closed (lit review §§5/7/8); title + abstract refined.
5. ✅ **S6 · design + cost — DONE** — full system design in `design.md` (framework decision, agent/scaffolds, attack seam, defense baseline set, eval, matrix, build plan); cost + build estimate in §10.
6. **S7 · build — NEXT** — per `design.md §8`: `uv add agentdojo` → encoded-payload attack → defense baselines (incl. MELON) → backbones/scaffolds → config + scoring → pilot. The real gate before any run.
7. **Run** — pilot first, then (if positive) the full matrix. **Nothing runs without the owner's go on the cost.**

## 10. Cost & build estimate (S6, order-of-magnitude — firm at S7)

Assumptions (explicit, to be re-measured against AgentDojo's real token footprint once wired): an agent task = ~5–15 LLM calls (a multi-turn tool loop); ~3K tokens/call on average as the context grows.

- **Capability-scaling pilot.** ~6 backbones × 3 payload conditions (plain + 2 encoders) × 2 defense conditions (none + spotlighting) × 1 scaffold × ~75 AgentDojo cases ≈ **~2.7K agent runs ≈ ~27K LLM calls ≈ ~80M tokens.** On API models at a blended ~$1–10/M tokens that is **order ~$100–800**; on **served open-weight backbones (NEU / employer cluster) the compute is near-zero** — so run the open-weight arm on the cluster and reserve API spend for the frontier-capability points. Owner's go is needed only for the API arm.
- **Full matrix (post-pilot, only if the pilot is positive).** All encoders (6 + image) × defense families (none / spotlighting / isolation / prompt-shield / MELON) × ≥3 scaffolds × more backbones ≈ **~10–20× the pilot** → low-thousands of API dollars, again largely offloadable to the cluster for the open-weight arm.
- **Build effort (S7 — the real gate, not the API spend).** Integrate AgentDojo (clone into gitignored `other_repos/`, read before wiring), wire the copied encoders as an `attack()`, wrap spotlighting / isolation / prompt-shield / MELON as evaluatable defense baselines, add action-completion + utility scoring. This engineering is the dominant cost of the direction; the API dollars are secondary.
