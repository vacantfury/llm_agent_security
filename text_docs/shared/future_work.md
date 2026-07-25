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

Index:

- **§1 — the current paper** (Paper E "Smuggled Actions", `agent_injection`): encoded indirect injection,
  attack-first. This is the shipping paper; its own near-term extensions live in
  `text_docs/agent_injection/proposal.md`, not here.
- **§2 — the direct follow-on**: the action-level *recover-before-act* defense + a flagship deployed-agent
  demonstration — the coupled, engineering-heavier, deliberately-later half of the Smuggled-Actions thesis.
- **§3 — multimodal / image-borne encoded injection**: extend the encoded-payload attack to VLM /
  computer-use (screenshot) agents.
- **§4 — the next coordinate**: multi-agent / distributed harm — a separate, later paper that generalizes §1
  from a single agent to a system of agents.
- **§5 — decomposed / small-model agents**: does splitting an agent across many small workers change its
  injection robustness? Carded 2026-07-24; cheaper and nearer than §3/§4, gated on a scoop-check.

Within each section, subsections are its component points.

---

## 1. Encoded indirect injection (attack-first) — the current paper [Paper E]

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

## 2. Action-level defense + a flagship demonstration — the direct follow-on

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
   (2026-07-23) found the tool-decode lift rising from ~+0.03 at 7B to ~+0.23 at 32B/72B (numbers in
   `TODO.md`).
2. **Planning danger (capability-positive).** Stronger orchestrators produce *more* successful harmful
   decompositions. Established finding — Semantic Intent Fragmentation (Ahad et al., AAAI 2026 Summer
   Symposium, arXiv:2604.08608), which reports 10/14 enterprise scenarios yielding policy-violating plans
   whose individual subtasks each pass classifiers.
3. **Detection loss (capability-negative) — OUR proposed mechanism, untested.** Small, context-starved
   workers are worse at noticing an injected instruction. This is the only one of the three not yet measured
   by anyone.

A fourth confound to control: small backbones are simply worse at the benign task. This repo's own sweep put
benign utility at 0.6 for Qwen-7B against 0.9 for 72B — so any robustness comparison must hold task competence
fixed or report the safety–utility frontier, not a bare attack-success number.

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
