# Roadmap — the agent-security line: current paper & future work

This is the planning catalog for **this repo's line only** — the *agent-side* security line: indirect
injection through the untrusted data channel, action-level harm, agent scaffolds, and injection-specific
defenses. One direction per section, in rough priority / readiness order.

**Not shared with the sibling repo (owner decision 2026-07-24).** This roadmap is *independent* of
`imaging_text_attacks_for_llm_jailbreaking`'s `future_work.md`: no coordinate is mirrored, nothing is kept in
sync across the two, and neither side owes the other an update when it moves. A direction earns a section here
only if it is **agent-side**; a model-side direction belongs in the sibling's roadmap and is simply absent
here. (Scope boundary: `CLAUDE.md`.)

**Line identity — the agent coordinate of the compositional-harm thesis.** Safety mechanisms that inspect one
unit are structurally incomplete when harm is *composed across units*. On this line the unit is the agent's
untrusted **data channel**, and the finding is that injection-specific defenses (spotlighting / isolation /
prompt-shield) inherit the same **decode blind spot** content guards have: an *encoded* injected instruction
rides through them and the agent decodes-and-acts. §5 extends the same logic to a further unit — the
**worker's fragment of context** inside a decomposed agent.

**Direction change, 2026-07-25 — and its immediate reversal.** The attack-first encoded-injection paper
(§1) was **CLOSED** on 2026-07-24: eight candidate contributions tested to destruction, all eight already
published (`text_docs/agent_injection/proposal.md §§11–12`). The defense half (§2) was promoted to lead in
its place, **gated on a scoop-check before any design** — and the gate closed it the same day at Level 1
(Full Overlap), blocked by ARGUS (arXiv:2605.03378). See §2's header for the full closure.

**Line status: no current work.** Two directions picked, two closed at Level 1, four days apart, each
blocked by work published 2–15 months before we picked it. §3, §4 and §5 below are **unchecked** — no
scoop-check has been run on any of them, and neither closure says anything about their novelty. The
standing recommendation (session, 2026-07-25) is **not to found a third direction in this line**: the
observed pattern is a cycle-time mismatch, not bad luck on a coordinate, and §3–§5 are the same shape of
bet. That is a recommendation, not a decision — the call is the owner's, and nothing here is retired.

Index:

- **§1 — CLOSED, do not re-enter** (Paper E "Smuggled Actions", `agent_injection`): encoded indirect
  injection, attack-first. Shelved 2026-07-24 at Level 1 (Full Overlap). Kept as the record of a direction
  tested to destruction; the verdict and its primary-source citations are in
  `text_docs/agent_injection/proposal.md §12`.
- **§2 — CLOSED, do not re-enter**: the action-level defense against **data-shaped** injection. Promoted to
  lead and closed by its own gate on 2026-07-25, Level 1 (Full Overlap), blocked by ARGUS. Kept as the
  record of a direction stopped *before* any build — the gate paying for itself.
- **§3 — multimodal / image-borne encoded injection**: extend the encoded-payload attack to VLM /
  computer-use (screenshot) agents.
- **§4 — the next coordinate**: multi-agent / distributed harm — a separate, later paper that generalizes §1
  from a single agent to a system of agents.
- **§5 — decomposed / small-model agents**: does splitting an agent across many small workers change its
  injection robustness? Carded 2026-07-24; cheaper and nearer than §3/§4, gated on a scoop-check.

Within each section, subsections are its component points.

---

## 1. ⛔ CLOSED — Encoded indirect injection (attack-first) [Paper E, shelved 2026-07-24]

> **Do not re-enter this section.** Shelved at scoop-check Level 1 (Full Overlap) on every claim, after
> five attack candidates and three measurement legs were each falsified or found already published —
> typically 6–18 months earlier, by a recurring set of authors. Full record with verified primary-source
> quotes: `text_docs/agent_injection/proposal.md §§11–12`.
>
> **The one-line reason, worth keeping:** an encoded injection must become cleartext instruction-shaped
> text exactly where the agent reads it — which is where a data-channel classifier sits. Encoding therefore
> evades only defenses placed *upstream of the decode*. That is a placement property of the pipeline, not a
> tunable one, so it does not yield to a better encoder.
>
> The text below is preserved unchanged as the historical statement of the direction.

The agent setting leaves the model-only frame on two axes at once. A model-only study asks *where harmful
content is placed* (encoding, modality) against a **model** whose only output is text and whose only adversary
is the prompt author. Agents shift both axes: the adversary becomes a **third party** who controls data the
agent *ingests* (a tool output, a retrieved document, an on-screen image — *indirect* injection), and the harm
becomes an **action the agent takes**, not text it emits. This adds a new input surface (the untrusted
tool/data channel) and a new harm axis (action completion) to the coverage frame, and it inherits this line's
assets: the encoders and image transforms become the **payloads**, now delivered through the agent's data
channel instead of the user prompt.

**Scope discipline (the lesson of this very line):** target the *minimal agent pattern* — untrusted-data →
context → action — instantiated on a standard harness (AgentDojo / InjecAgent) and swept across backbones,
**not** a bespoke complete agent whose idiosyncratic structure would make the result coupled and un-general.
Generality comes from the multi-scaffold × multi-backbone sweep.

The core question: does an encoded payload survive **injection-specific** defenses — spotlighting,
delimiter-isolation, prompt-shield / classifier guards — that are tuned on *natural-language* injections?
These defenses have no pure-model analog, so defeating them is a genuinely new result, not a re-run of
text-side jailbreaking.

- **Success = action completion**, not a harmful-text verdict: the agent actually executed the injected
  instruction / called the sensitive tool. This is the agent-native metric.
- **Attack-first, by design.** A payload is portable — a data blob dropped into any harness — whereas a
  defense must hook the agent's internals; the attack stays eval-only and decoupled, the defense (§2) is the
  coupled, later half.
- **Falsifiable:** encoded payloads raise injected-action success over plain-language payloads against
  deployed injection defenses, across ≥3 scaffolds × backbones. Refutation (encoding gives no lift once an
  injection guard is present) is itself a finding — injection defenses, unlike alignment, would be
  encoding-robust.

*(This is the shipping paper — its full proposal, scoop verdict, and design are in
`text_docs/agent_injection/`. This section records only its place in the line's roadmap.)*

---

## 2. ⛔ CLOSED — action-level defense against data-shaped injection [closed 2026-07-25]

> **Do not re-enter this section.** Promoted to lead direction on 2026-07-25 and **closed the same day** by
> its own gate: scoop-check #4 returned **Level 1 (Full Overlap)**. Full record with verified quotes:
> `outputs/scoop_check/2026-07-25-defense/step7_verdict.md` (gitignored).
>
> **The blocking work is ARGUS** (arXiv:2605.03378, May 2026, `weng2026argus`), which matches on all four
> axes — our problem framing, our insight, and our mechanism are each stated in its abstract, and it ships
> **AgentLure**, a benchmark for the exact task setting. Three further closures: **CaMeL**
> (`debenedetti2025camel`) covers the no-instruction case *by construction* — it never inspects for
> instruction-likeness, so our motivating gap is not a gap it has; the **out-of-band defense survey**
> (`narisetty2026outofband`) already names and taxonomizes the whole non-detection genre and already ran the
> first adaptive evaluation on AgentDojo with Qwen2.5-7B on one H200 — our exact fallback position and our
> exact hardware arm; and **`abdelnabi2026contextualintegrity`** argues an *impossibility result* for this
> class: "an adversary can always construct a context under which a blocked flow appears legitimate, or a
> defender who tightens norms will block genuinely legitimate flows."
>
> **The one-line reason, worth keeping:** the "defenses key on instruction-likeness" gap is real, but it is
> the *field's own headline open problem*, worked by Google DeepMind, Microsoft Research and several
> university groups simultaneously — so it is the most contested ground in the area, not open ground. The
> §2.0 argument below inverted the truth: naming a gap in a current abstract is evidence the gap is
> **crowded**, not that it is available.
>
> **The gate worked.** Cost of this direction: one day of search, zero GPU-hours, zero dollars, no design
> doc, no namespace, no `papers.md` row. That is the gate paying for itself — contrast §1, which reached a
> full build before its verdict.
>
> The text below is preserved unchanged as the historical statement of the direction and of the reasoning
> that picked it — including the parts that were wrong.

### 2.0 Why this one, and the gate that comes first *(historical — the reasoning that picked it)*

**Why it was picked over §3–§5.** Three reasons, in order of weight:

1. **The problem is named open by current primary sources — verified, not inferred.** The two papers that
   closed §1's last leg both state the defensive gap in their own abstracts and neither closes it:
   - AutoDojo (arXiv:2606.15057, Jun 2026): *"This is a **structural limit**: on such tasks the injection
     can pose as ordinary data rather than an explicit instruction, **bypassing defenses that rely on
     detecting instruction-like text**."*
   - Agent Data Injection (arXiv:2607.05120, Jul 2026): *"ADI **remains underexplored** and easily bypasses
     existing IPI defenses."* — 0 of 108 payloads detected by Llama Prompt Guard 2.
2. **Different competition dynamics.** §1 died eight times to a speed mismatch: a payload idea is cheap, so
   a handful of labs iterating monthly reached every one of ours first. A defense takes months to build and
   validate, which both slows the field's clock and raises the barrier — the mismatch that beat us bites far
   less here. This is the genre argument, and it is the main lesson §1 paid for.
3. **Our assets are already defense-shaped.** A defense paper needs a harness, comparison baselines, and a
   capability sweep — we have all three: the AgentDojo runtime, our own ports of MELON (behavioral),
   PIGuard (classifier) and spotlighting (prompt-level), the open-weight Qwen ladder, and the $0 offline
   probe machinery (`src/analysis/`). §1's negative results become this paper's motivation section rather
   than being discarded.

**THE GATE — scoop-check before any design.** This is the re-entry condition written into
`proposal.md §12`, and it binds this direction first: run `scoop-check` on the defense claim, checked
against **our own bib** and **our own wired baselines' abstracts**, *before* a design doc exists. §1's
decisive failure was not insufficient search — three of the papers that killed it were already in our
possession, including PIGuard, whose abstract states the property we spent a day rediscovering. No design,
no build, no namespace, and no `papers.md` row until the check clears.

**Known prior art to clear (from §1's own scoop-checks — start here, do not re-derive):** MELON
(`zhu2025melon`, masked re-execution) · RETA (`he2026reta`, and its "Canary-Blind Entanglement" bypass) ·
PlanGuard (2604.10134, "Intent Verifier" over parameter deviations) · dual-LLM quarantine and
information-flow-control designs · `bhagwatkar2025firewalls` (tool-input/output firewall, near-perfect on
current benchmarks) · DataSentinel (IEEE S&P'25, known-answer probing). The honest first question for the
check is whether "defend against injection that carries no instruction" is already someone's paper —
because if a defense keys on instruction-likeness it is disqualified by construction, and the surviving
design space may be narrow.

### 2.1 The direction (as previously stated)

The coupled, later half of the thesis: after the attack (§1) establishes the blind spot, close it.

- **Action-level coverage (the defense half).** The coverage map gains the untrusted tool/data channel as a
  new *surface* and the action as a new *harm type*; the natural agent analog of a recover-before-guard
  defense recovers and checks content on the data channel **before** it can reach an action. But agent
  defenses (information-flow control, dual-LLM quarantine) couple to agent structure — so this is the harder,
  more engineering-heavy, later contribution.
- **Flagship demonstration (a deliberately deferred *choice*).** The general result lands on a standard
  harness; impact comes from one striking demo on a *deployed, recognizable* agent with high-stakes actions —
  an email/calendar assistant (data exfiltration, sending on the user's behalf) or a coding agent with
  repo/CI access (supply-chain-flavored). The target is chosen for recognizability and stakes **at execution
  time** — explicitly *not* a niche tool. Any released-system demonstration follows responsible disclosure.

---

## 3. Multimodal / image-borne encoded injection (the second-priority direction)

The direct modality extension of §1: keep the attack and the action-completion metric, change the *channel*.
Instead of an encoded instruction in a text tool-output, the payload is **rendered to an image** (or an
on-screen element) that a **VLM / computer-use (screenshot) agent** reads, decodes, and acts on. The encoders
and renderers in `src/prompt_transformations/` are the payload assets.

- **Why it is a *separate* direction, not part of §1's core.** The core harness (AgentDojo) is **text-only** —
  it has no path to deliver an image payload — so this needs a distinct **multimodal / computer-use harness** (a
  VPI-Bench-style screenshot-agent setup). It also introduces a **vision / OCR capability axis** distinct from
  text-decode competence, which would confound §1's capability-scaling result — a reason to study it on its own
  terms. (Scope decided 2026-07-20: the core paper is text encoders; the abstract's "rendered image" clause maps
  here.)
- **Prior art / seed** (`literature_review.md §4`): VPI-Bench (image + agent + action, but a *plaintext* pop-up,
  no injection guard — explicitly names concealing prompts from users while keeping them agent-readable as future
  work) and Reverse CAPTCHA (invisible-Unicode injection; tool-use amplifies compliance). The encoded
  image-payload against an injection-defended VLM agent is the open, systematic version.
- **Relation to §2.** The §2 flagship demonstration is naturally a computer-use agent — so §2 and §3 pair: §3
  supplies the image-borne attack, §2 the deployed-agent stage and the recover-before-act defense.
- **Cost honesty.** A multimodal harness is a materially bigger build than the text / AgentDojo core — the reason
  it is sequenced as a follow-on, not folded into the shipping paper.

---

## 4. The next coordinate — multi-agent / distributed harm (a separate, later paper)

A multi-agent adversary is the **cross-agent analog of cross-modal splitting**: harm distributed across
agents, each agent's individual contribution benign, the *joint* behavior harmful — deception / collusion /
steering as the mechanism, **joint / system-level verification** as the defense. This is the broadest reach of
the line's thesis.

- **Relation to §1.** §1 is *single-agent* indirect injection (one agent, one compromised data channel); §4
  is the *multi-agent* composition where **no single agent is individually compromised** — the harm exists
  only in the joint behavior. §4 overlaps §1 but generalizes it; it is explicitly a **separate, later paper**,
  not this one.
- **Cost honesty.** A multi-agent harness is a materially bigger, more compute-heavy build than the eval-only
  single-agent setup — the main reason it is sequenced after §1 (and §2), not run in parallel.
- **Entry discipline.** Enter via the *rigorous compositional-harm* angle (per-agent-benign / joint-harmful,
  plus a joint-verification defense), reusing the harness identity — **not** another
  propensity-for-deception leaderboard. Keep the through-line sharp: an axis that doesn't reduce to the
  compositional-harm thesis doesn't belong on this arc.
- **Partial-anticipation warning.** `hu2026localmonitorsmisscompositional` (`literature_review.md`) already
  covers encoded fragments split across agents collapsing local monitors — re-check the delta before entering.

---

## 5. Decomposed / small-model agents — does splitting the agent change its injection robustness? [idea]

*Carded 2026-07-24. Origin: an owner idea framed as an **efficiency** proposal — decompose a task into many
small subtasks and hand each to a small, cheap model to save money and latency. The efficiency framing was
checked against the literature the same day and is **occupied** (see "What is closed" below). The framing that
survives is the **security** question, which is this line's.*

**The question.** A production agent is increasingly not one large model doing everything, but an orchestrator
that decomposes a task and dispatches subtasks to smaller, cheaper workers. Does that architecture change the
agent's vulnerability to **indirect prompt injection** — and if so, through which mechanism?

**Why it is on-thesis.** It is the line's compositional-harm thesis on a new unit. §1's unit is the data
channel; here the unit is **the worker's fragment of context**. The hypothesis: a small worker that sees only
its own fragment lacks the global context a single large agent would use to recognize an injected instruction
as anomalous — so per-worker inspection is structurally incomplete even when every worker is individually
defended. Same claim shape as §1, new surface.

### 5.1 Three mechanisms that must be disentangled

This separation *is* the contribution — it is what makes the direction a paper rather than a one-line ablation.
Two of the three run **opposite** to the naive "small models are less safe" intuition, so a study that does not
pull them apart will be refuted on first read.

1. **Decode exposure (capability-positive).** Bigger backbones decode encoded payloads better and are
   therefore *more* exposed. This repo has already measured it: the 4-tier Qwen `capability_sweep`
   (2026-07-23) found the tool-decode lift rising monotonically with backbone capability, negligible at the
   small tiers and large at the top two (numbers in `TODO.md`, the live-status home).
2. **Planning danger (capability-positive).** Stronger orchestrators produce *more* successful harmful
   decompositions. Established finding — Semantic Intent Fragmentation (Ahad et al., AAAI 2026 Summer
   Symposium, arXiv:2604.08608), which reports 10/14 enterprise scenarios yielding policy-violating plans
   whose individual subtasks each pass classifiers.
3. **Detection loss (capability-negative) — OUR proposed mechanism, untested.** Small, context-starved
   workers are worse at noticing an injected instruction. This is the only one of the three not yet measured
   by anyone.

A fourth confound to control: small backbones are simply worse at the benign task — the same sweep found
benign utility falling substantially from the top tier to the smallest. Any robustness comparison must
therefore hold task competence fixed or report the safety–utility frontier, not a bare attack-success number.

### 5.2 What is open

Prior-art sweep 2026-07-24, verified against arXiv abstract pages. A formal `scoop-check` is still owed.

- Nobody has run the direct comparison — one large orchestrator doing the whole task versus the same task
  split across many small workers — scored on indirect-injection success.
- The detection-loss mechanism (5.1 item 3) is untested anywhere found.
- Defense degradation on small backbones rests on a **single** data point: an established workshop result
  (Pai et al., AdvML-Frontiers × CoTMA @ COLM 2026, arXiv:2606.18530) finding spotlighting halves attack
  success on Claude Haiku but delivers **zero** benefit on Llama-3.1-8B — single-agent, never in a decomposed
  pipeline. CaMeL (Debenedetti et al., arXiv:2503.18813) likewise assumes its privileged LLM is capable enough
  to emit correct control-flow code, with no small-backbone ablation.
- Neither standard harness supports the measurement: AgentDojo (Debenedetti et al., arXiv:2406.13352) and
  InjecAgent (Zhan et al., ACL 2024 Findings, arXiv:2403.02691) publish no capability-tier sweep on a common
  task set and have no decomposed / multi-worker execution mode. That instrumentation is part of the build.

### 5.3 What is closed — do not enter through these doors

- **The efficiency framing is scooped.** Established: "Small Language Models are the Future of Agentic AI"
  (Belcak et al., NVIDIA, arXiv:2506.02153) states the thesis; Falconer (Zhang et al., arXiv:2510.01427) and
  EffGen (Srivastava et al., arXiv:2602.00887) implement it; the cost-routing line (FrugalGPT, Chen et al.,
  arXiv:2305.05176; RouteLLM, Ong et al., arXiv:2406.18665; Hybrid LLM, Ding et al., arXiv:2404.14618) and the
  decomposition line (Decomposed Prompting, Khot et al., ICLR 2023, arXiv:2210.02406) precede it; a 2025
  survey (arXiv:2510.13890) already catalogues the space. Cost and latency may appear only as *motivation for
  why the architecture is deployed*, never as a contribution.
- **The efficiency premise is itself contested** — cite this rather than assuming it: multi-agent failure
  taxonomies (MAST, Cemri et al., arXiv:2503.13657) and step-compounding results (arXiv:2601.22290) both show
  that adding steps adds failure surface.
- **Attacker-side decomposition is a different threat model, and it is occupied.** Established: DrAttack (Li
  et al., EMNLP Findings 2024, arXiv:2402.16914) and DeCompBench (Kothamasu et al., arXiv:2606.13994) study an
  *attacker* manually splitting a harmful request against one capable model. Our question is *externally
  injected* content reaching a *small* worker. The distinction is real but must be stated explicitly in
  related work, or a reviewer will collapse the two.

### 5.4 Relation to §4, cost, and gating

**Relation to §4.** §4 is the multi-agent composition where **no single agent is compromised** and harm exists
only in the joint behavior. §5 is a **single injected payload** against a decomposed executor — one compromised
data channel, many small readers. Distinct questions; §5 is the cheaper and nearer of the two.

**Cost honesty.** Cheaper than §3 and §4: it reuses the Paper-E harness, the encoders, and the Qwen capability
ladder already built and run. The new build is a decomposed scaffold (orchestrator + N workers) plus a
per-worker context-scoping control — no new harness, no new modality.

**Gating, in order.** (a) A formal `scoop-check` on the composite claim, paying particular attention to
`hu2026localmonitorsmisscompositional` (`literature_review.md`), the nearest prior claim. (b) A small pilot —
monolithic versus decomposed at one backbone tier, one payload, one defense — before any commitment.
**Sequenced after Paper E ships**; not started (owner decision 2026-07-24).
