# Roadmap — the agent-security line: current paper & future work

This is the planning catalog for **this repo's line** — the *agent-side* security line. It holds the line's
cross-paper future work, one direction per section, in rough priority / readiness order. The model-side (VLM)
roadmap this line was spun out of (compound/split-attack defenses, mechanism/theory, best-of-N, low-resource
encoding, judge reliability, the category-theory framing, etc.) lives in the sibling repo
`imaging_text_attacks_for_llm_jailbreaking`'s own `future_work.md` and is **not** duplicated here (scope
boundary: `CLAUDE.md`).

**Line identity — the AGENT coordinate of the compositional-harm thesis.** Safety mechanisms that inspect one
unit — one representation (encoding), one modality, one message channel — are structurally incomplete when
harm is *composed across units*. Here the unit is the agent's untrusted **data channel**, and the finding is
that injection-specific defenses (spotlighting / isolation / prompt-shield) inherit the same **decode blind
spot** content guards have: an *encoded* injected instruction rides through them and the agent
decodes-and-acts. (The full cross-repo identity frame — the representation / modality-presence /
modality-placement coordinates on the model side — is the sibling repo's material.)

Index:

- **§1 — the current paper** (Paper E "Smuggled Actions", `agent_injection`): encoded indirect injection,
  attack-first. This is the shipping paper; its own near-term extensions live in
  `text_docs/agent_injection/proposal.md`, not here.
- **§2 — the direct follow-on**: the action-level *recover-before-act* defense + a flagship deployed-agent
  demonstration — the coupled, engineering-heavier, deliberately-later half of the Smuggled-Actions thesis.
- **§3 — multimodal / image-borne encoded injection**: extend the encoded-payload attack to VLM /
  computer-use (screenshot) agents — the second-priority future direction, just below §2.
- **§4 — the next coordinate**: multi-agent / distributed harm — a separate, later paper that generalizes §1
  from a single agent to a system of agents.

Within each section, subsections are its component points.

---

## 1. Encoded indirect injection (attack-first) — the current paper [Paper E]

The agent setting leaves the model-only frame on two axes at once. The model-side line studies *where harmful
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
Generality comes from the multi-scaffold × multi-backbone sweep, exactly as the model-side results generalize
across VLMs.

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
on-screen element) that a **VLM / computer-use (screenshot) agent** reads, decodes, and acts on — the agent
coordinate of this line's modality-placement work (the encoders / renderers are the shared assets; the
model-side modality study is the sibling repo's).

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
steering as the mechanism, **joint / system-level verification** as the defense (the multi-agent analog of a
joint-verification defender). This is the broadest reach of the line's thesis.

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

---

*Maintenance — kept coherent with the sibling (`imaging_text_attacks_for_llm_jailbreaking`).* This roadmap and
the sibling's `future_work.md` share cross-line coordinates — the identity frame, and boundary directions built
on the shared encoders (e.g. §3 multimodal is the agent side of the sibling's modality work). They are **not** a
full mirror (scope-partitioned: agent-side here, model-side there), but the shared / boundary coordinates and
the cross-references between them are kept consistent — when one side's shared coordinate moves, update the
other. (The sibling's `future_work.md` is now local-only / untracked, so its side is a local edit.)

*Further identity coordinates the whole arc could extend into (harm × truth / fabrication-based harm; a formal
compositional language) are recorded in the sibling repo's `future_work.md` as part of the cross-line identity
frame — they are not agent-specific and are not carded here.*
