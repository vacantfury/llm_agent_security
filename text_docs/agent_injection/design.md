# Design — Smuggled Actions: the agent, the evaluation system, the attack, the defenses (`agent_injection`)

**Workflow stage:** S6 · design (this doc) → S7 · build. Ratified direction (owner 2026-07-20): encoded
indirect injection evades injection-specific *surface-form* defenses on LLM agents; a *behavioral* defense
(MELON) resists; and (headline bet) more capable backbones may be *more* vulnerable. See `proposal.md` (§3
design axes, §5 contributions, §10 cost) and `../shared/literature_review.md` (§§2–8 prior art).

**Grounding:** this design is built from a full read of the four established frameworks (AgentDojo, InjecAgent,
ASB) and the defenses (MELON, spotlighting, PI-classifiers, isolation), 2026-07-20 — source + paper level, not
recall. The governing principle is *reuse the mature harness, build only the genuinely new*: AgentDojo already
supplies the agent loop, the environments, the deterministic action scoring, and three of our target defenses;
we add the encoded-payload attack, the behavioral-defense baseline (MELON), the capability-scaling analysis,
and our config/registry layer.

---

## 1. Framework decision

| | **AgentDojo** (PRIMARY) | **InjecAgent** (breadth complement) | **ASB** (stretch 2nd harness) |
|---|---|---|---|
| Action-scored | **Yes, deepest** — pre/post environment-state diff + trace fallback | Partial — text-match on parsed ReAct output, no live executor | Yes — real tool invocation via a live agent-OS |
| Custom attack pluggable | Yes — `BaseAttack` subclass + `@register_attack`, returns `{vector_id: payload}` | Yes — JSONL placeholder edit | Yes — YAML config injection strings |
| Defenses shipped | **4** (`transformers_pi_detector`, `spotlighting_with_delimiting`, `tool_filter`, `repeat_user_prompt`) — name-match our target set | **None** | 11 (delimiters, sandwich, paraphrase, PPL/LLM detection, …) |
| Multi-backbone | High (unified pipeline, provider dispatch) | Medium (per-model `BaseModel` subclass) | High (YAML `llms` list, `ollama/` local) |
| Effort for us | Baseline (chosen primary) | Low (hours) | Medium-high (stand up a whole 2nd agent-OS) |

**Decision.**
- **AgentDojo = primary and sufficient for the headline result.** Deepest scoring, defenses that name-match the
  proposal, an attack API built for exactly our seam, pip-installable (`agentdojo` on PyPI, MIT).
- **InjecAgent = lightweight breadth check only** — a cheap second data point across 17 tool domains to show the
  encoding effect isn't AgentDojo-specific. **Not** for defense claims (ships no defenses; scoring is
  text-match, not executed-action).
- **ASB = stretch second full harness for the defense-evasion *generalization*** — the only other benchmark that
  combines action-scoring + real defenses + a ready backbone roster, so it lets us claim the effect holds on two
  independently-built defense stacks. But it is a whole second agent-OS (AIOS/PyOpenAgi) to stand up — **defer to
  post-pilot**, add only if a reviewer would want cross-harness defense generality.

**Integration path (supersedes the earlier "clone into `other_repos/`" note in `proposal.md §7` / TODO):**
`uv add agentdojo` and extend via its public API — register our attack/defenses as modules loaded with the
`--module-to-load` flag (or construct `AgentPipeline` directly). No repo clone needed; if deep source reading is
wanted during the build, read the installed package under `.venv/` (a clone would trip the clone-ask rule and
isn't necessary). MELON ships as a *patch* to AgentDojo — we reuse its logic as our own pipeline element rather
than patching a cloned tree (§4).

**Component provenance (published-first — owner steer 2026-07-21).** The paper's *key* building blocks should
be peer-reviewed / published, not arXiv-only or non-paper artifacts (our own builds excluded). Audit of the
stack: harness **AgentDojo (NeurIPS'24 D&B)** ✓; resistant behavioral defense **MELON (ICML'25)** ✓;
complements **InjecAgent (Findings-ACL'24)** ✓ and **ASB (ICLR'25)** ✓; **spotlighting (Hines et al.,
CAMLIS'24)** ✓ (canonical, smaller venue). Published methods we build on (the encoding side): set-theory + formal-logic are the owner's **published**
MathEnc work (`pmlr-v318-zhang26a`, PMLR v318 / Canadian AI'26) — peer-reviewed, so the core encoding method
satisfies the rule despite being ours; cipher / homoglyph are standard techniques. Only `llm_utils` is excluded,
as tooling/infrastructure (ours). **One flag:** the PI-classifier baseline
`transformers_pi_detector` = ProtectAI `deberta-v3-base-prompt-injection` is a HuggingFace *artifact*, not a
published method — keep it as the de-facto open PI-detector the field benchmarks and AgentDojo ships, but label
it as such, and if a reviewer wants a published detector, add one (a PI-detection paper's method) as a second
surface-form classifier. arXiv-only *related work* (STAC, hu2026, …) is cited as prior art, not built on, so it
is outside this rule.

---

## 2. System architecture

Layer our code *on top of* AgentDojo, mirroring the sibling's registry/factory + YAML-config-not-magic-numbers
pattern (the copied encoder factory is the template).

```
src/
  prompt_transformations/     # REUSE (copied encoders) — the payload generators
  attacks/                    # encoded-payload attack(s) registered into AgentDojo
  defenses/                   # MELON + spotlighting variants + classifier/isolation wrappers
  harness/                    # AgentDojo integration: pipeline/backbone construction, run driver
  scoring/                    # metric aggregation + the capability-scaling analysis
conf/experiment/agent_injection/
  *.yaml                      # the matrix: payloads × defenses × scaffolds × backbones × harness × task-subset × N
```

Everything AgentDojo exposes as a `BasePipelineElement` (a one-method `query(...)->5-tuple` interface) composes
into an `AgentPipeline([...])` — this single seam is how the LLM call, the tool executor, AND every defense plug
in, so our defenses and scaffolds are first-class extensions, not hacks. Tunables (which encoders, which
defenses, backbone list, task subset, N-budget, thresholds) live in YAML; code reads them.

---

## 3. The agent — scaffolds × backbones

**Scaffolds (we claim ≥3, generality axis).** AgentDojo's tool-use loop shape is fixed
(`ToolsExecutionLoop`); scaffold variation lives in *how tool calls are elicited*:
1. **Native function-calling** — OpenAI / Anthropic / Google / Cohere structured tool APIs. Free.
2. **Prompted / XML tool-calling** — `PromptingLLM` / `LocalLLM`: tool schemas serialized into the system
   prompt, model emits `<function-call>…</function-call>` with a `<function-thoughts>` reasoning step (already
   ReAct-flavored). Free; also the path for open-weight/local models. Gives an apples-to-apples
   native-vs-prompted comparison per backbone.
3. **A built 3rd scaffold** — an explicit ReAct or planner→executor `BasePipelineElement` (AgentDojo ships
   `planner.py` stubs, `NotImplementedError`, scaffolded for exactly this). BUILD, low-medium.

**Backbones (capability-scaling sweep, ~6+).** Order by capability; the axis IS the headline finding.
- Frontier API models: add `ModelsEnum` + `MODEL_PROVIDERS` entries (the shipped list tops out ~GPT-4o /
  Claude-3.7 / Gemini-2.5-preview — current-gen entries are a few lines each), or bypass the enum via
  `PipelineConfig.llm: BasePipelineElement` with a hand-built LLM object.
- Open-weight low/mid capability: served on the **NEU / employer cluster** via vLLM →
  `--model local|vllm_parsed|openai-compatible`. Near-zero API cost (resource-acquisition rule). This arm anchors
  the low-capability end of the scaling curve.

---

## 4. The attack — encoded payloads

**Payload generators = REUSE** `src/prompt_transformations/` (set-theory / formal-logic / code / cipher /
classical-Chinese / homoglyph). No new attack *mechanism* — the paper's novelty is the systematic evaluation,
not a new encoder (lit review §§1, 4).

**The injection seam (precise).** An attack's `attack(user_task, injection_task) -> dict[str,str]` returns
`{injection_vector_id: payload_string}`. The payload physically lands via
`TaskSuite.load_and_inject_default_environment(injections)`, which does a literal Python `str.format(**injections)`
over the environment YAML text (placeholders like `{email_facebook_injection}` sit in string fields), then
`yaml.safe_load`s. **Constraints our encoder output must satisfy:** (a) `.format()`-safe — no stray unescaped
`{`/`}`; (b) YAML-double-quoted-string-safe — escape quotes/newlines. So the encoded-payload attack needs a thin
**serialization/escaping step** after encoding. `get_injection_candidates` (canary-based) already tells us which
vectors are on-path for a given user task, so we only inject where the model will actually read it.

**Implementation.** Subclass `FixedJailbreakAttack` (or `BaseAttack` for per-vector encoder choice); inside
`attack()`, run the encoder over `injection_task.GOAL` (wrapped in a minimal carrier template), escape, return
the dict; `@register_attack("encoded_<scheme>")`. Usable via `--attack encoded_<scheme>` or `load_attack`.

**Payload axis:** `plain` (control, = AgentDojo's `important_instructions`/`direct` baseline) vs each encoder.

**Image-render caveat (scope decision).** AgentDojo is **text-only** — tool outputs are text/YAML, so the
`ir_plain` image-rendered payload has *no delivery path here*. Image-borne injection needs a **VLM / computer-use
(screenshot) agent** (e.g. a VPI-Bench-style setup). **Decision: the core paper is text-encoders on AgentDojo;
the image-render arm is a scoped extension requiring a separate multimodal harness** (`future_work.md §3`), not
part of the core matrix. Do not promise image results on the AgentDojo track.

---

## 5. The defenses — the baseline set

Mapped to the surface-form vs behavioral thesis (lit review §3). "Reuse" = ships in AgentDojo.

| Defense | Class | Status | Effort | Expected vs. encoding |
|---|---|---|---|---|
| no-defense | — | reuse | — | control |
| `transformers_pi_detector` (ProtectAI DeBERTa `deberta-v3-base-prompt-injection-v2`) | surface-form (classifier) | **reuse** | — | **falls** — the headline; classifier trained on plaintext injection phrasing |
| `spotlighting_with_delimiting` (Hines) | surface-form (prompt) | **reuse** | — | **falls** — doesn't touch semantics; weak even non-adaptively |
| `tool_filter` (OpenAI-only tool-list restriction) | isolation (coarse, content-agnostic) | **reuse** | — | **≈unchanged** — useful contrast (encoding isn't what moves it) |
| **MELON** (masked re-execution + tool-call comparison) | **behavioral** | **build (low)** | ~½ day | **resists** — never reads tool-output text, only the resulting tool-call trajectory |
| `spotlighting_with_datamarking` / `_with_encoding` | surface-form | build (low) | hrs | secondary ablation — double-encoding / whitespace-corruption interaction |

**MELON (the resistant baseline — build detail).** Public reference: `github.com/kaijiezhu11/MELON` (a 2-file
patch: adds a `MELON(PromptInjectionDetector)` element run inside `ToolsExecutionLoop`). Mechanism: each step,
re-run the LLM on a *masked* state (real user task replaced by a neutral "summarize / follow any instructions"
prompt, prior tool outputs consolidated); if the masked run emits a tool call *similar* (embedding cosine) to the
original run's, that call was driven by injected content, not the user → flag. Compares **tool calls only**
(not response text), with a cross-step cache. **Adapt, don't copy verbatim:** (a) the released code hardcodes
`cosine_sim > 0.8` (the `threshold` arg is dead) — expose it as a YAML knob; (b) it hardcodes OpenAI
`text-embedding-3-large` — even a non-OpenAI backbone then needs an OpenAI key for embeddings (budget this); (c)
its patch targets an older flat-string message API while current AgentDojo uses list-of-content-blocks — expect
~½ day of API adaptation, not a rewrite. **Recurring cost:** ~2× LLM calls/step (parallelizable) + one embedding
call per compared tool call — factor into the run budget.

**Headline defense set = {no-defense, DeBERTa-detector, spotlighting-delimiting, tool_filter, MELON}** — three
reuse + MELON (½-day patch) demonstrate "surface-form falls, behavioral resists" at minimal build cost.
**Stretch resistant baselines (only if reviewers want more than MELON):** the Firewalls "Minimize & Sanitize"
Sanitizer (`bhagwatkar2025indirect`; no public code → medium build) as a second *semantic* defense; a true
dual-LLM / CaMeL quarantine is medium-high build (restructures how tool results enter context) — skip unless
demanded. Prompt-shield variants (Meta Prompt Guard, Lakera) are low-effort drop-in classifier swaps if we want
more than one surface-form classifier.

**Defense interface note.** AgentDojo has no `register_defense` (defenses are `if`-branches in
`AgentPipeline.from_config` gated by a `DEFENSES` list). We wrap this behind our own small defense
registry/factory (`src/defenses/`) so the matrix config can name defenses uniformly, composing
`BasePipelineElement`s directly rather than forking `from_config`.

---

## 6. The evaluation system

**Scoring = REUSE** AgentDojo's deterministic, code-based checks (never an LLM judge — an LLM judge is itself
injectable, a deliberate AgentDojo design choice we inherit):
- **Utility** — `user_task.utility(...)` / `utility_from_traces(...)`: did the benign task get done (env-state
  diff / trace). Bounds over-blocking.
- **Security (attack success)** — `injection_task.security(...)`: did the injected sensitive action actually
  fire. This is our action-completion metric.

**Metrics per cell:** Benign Utility (no attack), Utility Under Attack, **Targeted ASR** (security). Adopt ASB's
composite **NRP = PNA × (1 − ASR)** as a single utility-vs-security number. **Headline analyses:**
1. **Encoding lift** — ASR(encoded) − ASR(plain), *specifically where an injection defense is present* (the
   plain-vs-encoded control isolates the encoding effect).
2. **Defense-class split** — encoding lift on surface-form defenses vs on MELON (expect lift on the former, ~none
   on the latter).
3. **Capability-scaling** — ASR vs backbone-capability ordering (expect *rising* ASR with capability; a
   flat/negative trend is itself a clean result).

**Logging = REUSE** AgentDojo's `TraceLogger` JSON tree (`runs/<pipeline>/<suite>/<user_task>/<attack>/<injection_task>.json`)
+ its caching/resume; our `src/scoring/` reads these for aggregation + the scaling analysis.

---

## 7. Experiment matrix + pilot

Full matrix (design target): **payload** (plain + ~6 encoders) × **defense** (the 5-set) × **scaffold** (≥3) ×
**backbone** (~6+, capability-ordered) × AgentDojo's 4 suites (629 security cases). This multiplies fast — each
cell reruns the ≤15-iteration tool loop per case.

**Pilot first (gated on owner-go for the API arm), per `proposal.md §10`:** ~6 backbones (capability-spread) ×
{plain + 2 encoders} × {no-defense + spotlighting} × 1 scaffold × an AgentDojo task-injection subset (~75
cases). Decides whether (a) encoding lifts ASR at all and (b) the capability trend exists, before committing to
the full matrix. Open-weight arm on the cluster (near-zero); API arm ~$100–800 (§10). MELON's 2×-call overhead
enters at the full-matrix stage.

---

## 8. Build plan (S7, ordered)

1. **Harness up.** `uv add agentdojo`; run a vanilla benchmark to confirm the loop + scoring + a couple of
   backbones work end-to-end. Pin the version.
2. **Attack.** Decouple `src/prompt_transformations/` to the payload-gen subset (TODO item 2); implement +
   `@register_attack` the encoded-payload attack with the escape/serialization step; verify a payload survives
   `.format()`→YAML and that the model decodes it (a sanity decode-rate check on one backbone).
3. **Defenses.** Wire the 3 shipped (config); implement MELON as a `BasePipelineElement` (port `pi_detector.py`
   to the current message-block API; YAML threshold; embedding-backend knob); add the spotlighting
   datamarking/encoding variants.
4. **Backbones + scaffolds.** Add `ModelsEnum` entries / configure the cluster vLLM open-weight arm; build the
   3rd scaffold (ReAct or planner→executor).
5. **Config + scoring.** YAML matrix config (`conf/experiment/agent_injection/`); `src/scoring/` aggregation +
   the capability-scaling analysis + the plain-vs-encoded lift.
6. **Pilot run** — owner-go on the API arm; then read results before designing the full-matrix run.

Skills to adapt at this point (TODO item 2): `run-experiment` / `check-experiment-results` / `manage-experiments`
currently assume the sibling's VLM cluster pipeline — rewire to this AgentDojo runtime.

---

## 9. Open decisions & risks

- **Image-render arm** is out of the AgentDojo core (text-only harness) — a scoped multimodal extension, not a
  core-matrix promise (§4). Confirm the paper's scope reflects text encoders on the agent track.
- **3rd scaffold** must be structurally distinct from the isolation *defense* (don't double-count planner-isolation
  as both a scaffold and a defense).
- **MELON's OpenAI-embedding dependency** — either keep an OpenAI key for embeddings or swap the embedder; note in
  the run budget.
- **ASB as a 2nd harness** — real cost (a whole agent-OS); commit only post-pilot and only for cross-harness
  defense generality.
- **Scoop-race** (lit review §1) — the field is hot; the pilot + build should move promptly once greenlit.
- **Cost** — 629 cases × axes × MELON's 2× multiplies; the pilot is the gate, and open-weight-on-cluster keeps the
  scaling arm cheap.
