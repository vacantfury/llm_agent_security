# S1 idea-check package — `agent_injection` (Paper E · "Smuggled Actions")

*Ready-to-paste distillation for cspaper.org/idea-check (S1, owner hands). Bring back: the verdict + the main critiques, especially on the novelty/scoop axis (§ "three things"). Written AFTER the S4 literature/scoop search (owner-corrected order 2026-07-19), so its novelty claims are grounded in the deep-read (`literature_review.md §1`, with the full prior-art map in §§2–6). Fallback if cspaper is skipped: the internal adversarial pass in `# Idea Review` below, marked `idea-check: internal-only (debt)`.*

## The idea in one line

Automated **indirect-prompt-injection defenses** — spotlighting, delimiter/data-isolation, prompt-shield classifiers — are tuned on *natural-language* injections, so they share the same **decode blind spot** this line's earlier work found in content guards: an **encoded** injected instruction (a text encoding — cipher / code / set-theory / classical-Chinese — or an image render) rides *through* the defense, and the agent **decodes it and takes the harmful action**.

## Background

Prior work in this line (Papers A–C) shows *content* safety fails on **encoded / image-rendered** harm because guards inspect surface form without decoding the payload. That work targets a **model** whose only output is text. **Agents** change the setting on two axes at once: the adversary becomes a **third party** who controls data the agent *ingests* (a tool output, a retrieved document, an on-screen image — *indirect* injection), and the harm becomes an **action the agent takes** (calling a sensitive tool, exfiltrating data). Agents also carry a *new* defense layer with no pure-model analog — **injection-specific** defenses (spotlighting, data-isolation, prompt-shield). Those defenses have never been calibrated against encoded payloads.

## The problem / gap

No published work systematically measures whether an **encoded** indirect-injection payload evades **injection-specific** defenses on an agent, scored by whether the agent **completes the injected action** — nor frames it as the agents' injection defenses inheriting the content guards' decode blind spot. The literature has only scattered pieces (all confirmed by a full deep-read):
- The two rigorous agentic-IPI harnesses (**AgentDojo**, **InjecAgent**) test **natural-language** injections only.
- The founding IPI paper (**Greshake 2023**) and a NeurIPS'25 firewall paper (**Bhagwatkar**) each show **one** anecdotal encoded bypass (a Base64 Bing-Chat demo; a single Braille example vs the authors' own bespoke sanitizer, in a v2 appendix, where base64 and whitespace *failed*) — neither systematic, both explicitly "future work" or a narrow "rare-token" aside.
- Encoding-as-evasion is studied **non-agentically** (Uysal 2026: base64/hex/ROT13 on plain chatbots, no defense, no action).
- Two papers name our exact contribution as **untested future work**: **VPI-Bench** (ICLR'26) asks for "techniques to conceal malicious prompts from users while keeping them detectable by screenshot-based agents"; **Spotlighting** §5.4 flags a reversible-encoding attacker who pre-encodes the payload — never built.

## The idea (core claim)

Injection defenses recognize an *imperative natural-language surface* in ingested data (delimiting it, datamarking it, classifying it). An **encoded** instruction presents a surface they were never tuned on, yet the backbone still **decodes-and-obeys** it — the surface-vs-decoded gap of Paper C, relocated to the agent's untrusted **data channel**. We measure it directly and fix-check it:
- **Attack (the core of this paper):** an encoded indirect-injection payload raises **injected-action success** over a plain-language payload against deployed injection defenses, **across ≥3 scaffolds × backbones**, on a standard harness (AgentDojo / InjecAgent). Success = the agent completes the injected action (agent-native metric), *not* a harmful-text verdict.
- **Falsifiable, refutation-is-a-finding:** if encoding gives no lift once an injection guard is present, that itself is a result — injection defenses, unlike alignment, would be encoding-robust.

**Seed plausibility (not hypothetical):** Reverse CAPTCHA (2026) quantifies that **tool-use amplifies compliance** with an encoded (invisible-Unicode) payload — Cohen's *h* up to **1.37**, compliance → 98–100% with tools; and this line already owns the encoders (MathEnc) and image transforms (ImgAug) that become the payloads.

## Intended contributions

1. The **first systematic, controlled** measurement of encoded indirect prompt injection as an evasion axis against **injection-specific** defenses (spotlighting / datamarking / isolation / sandwich / prompt-shield classifier), scored by **action completion**.
2. A **unifying account** — injection defenses inherit the content guards' *surface-not-decoded* blind spot (the agent coordinate of this line's coverage / decode-gap thesis).
3. A **generality result** across scaffolds × backbones, with a **plain-vs-encoded control** isolating the encoding effect, plus the **image-rendered** payload variant for VLM / computer-use agents.
4. (Later half, §5.2) an action-level **recover-before-act** defense + a flagship deployed-agent demonstration (responsible disclosure).

## Closest prior art + our delta (to pre-empt "isn't this already done?")

- **Greshake 2023 / Bhagwatkar 2025** — *one anecdotal* encoded bypass each; no sweep, no control, one defense, narrow explanation. → own only "it can happen once," not the systematic characterization.
- **Adaptive Attacks Break IPI Defenses (Zhan 2025)** — same metric + "defenses fall to evasion" frame, but **white-box GCG gibberish suffixes, not semantic encoding**. → the white-box optimizer analogue; ours is the black-box, human-readable-encoding route.
- **Spotlighting (Hines 2024)** — the defense we test; its "encoding" variant encodes the *whole document as a defender signal*, attack payload always plain English; §5.4 flags our attack and never builds it.
- **VPI-Bench (2026)** — image + agent + action, but a *plaintext* pop-up (no decode step) and no injection guard; names our gap as future work.
- **Our delta:** the *encoded/rendered payload × injection-specific defense × agent action-completion × decode-blind-spot frame* combination, systematic and controlled, is unclaimed. (S4 scoop verdict: **Level 3 / Medium Overlap, delta defensible** — more defensible than the parked `judge_reliability` line, whose insight was owned by an active subfield.)

## Venue class

AI-agent / LLM **security** — target a MAIN conference (IEEE SaTML / S&P / USENIX Security, or *ACL via ARR). Off the July AAAI crunch; a later cycle. **Workshops are fallback-only, never the target** (owner rule 2026-07-19).

## The three things we most want the idea-check to stress-test

1. **Scoop / novelty (make-or-break).** Given that the *phenomenon* has one-off anecdotes (Greshake Base64, Bhagwatkar Braille) and two papers flag the systematic version as future work, is "first systematic characterization + decode-blind-spot frame" a strong enough contribution for a main venue — or will a reviewer read it as "obvious next step, already anticipated"? This is a **hot, fast-moving field** — how much scoop-race risk?
2. **Is the framing a real contribution or a re-label?** Does "injection defenses inherit the content guards' decode blind spot" carry weight beyond "encoding evades defenses," given the field already knows encoding evades things?
3. **Is the metric/setup convincing?** Is "action completion on AgentDojo/InjecAgent, plain-vs-encoded, across scaffolds × backbones" the right rigorous design, and is the external-agent-harness build cost worth it versus a cheaper approximation?

---

# Idea Review

*(Internal adversarial pass — the S1 fallback if cspaper is skipped. Run a FRESH-context critique before trusting this; author-context rubber-stamps. Replace with the cspaper verdict when it returns.)*

**Strongest case FOR.** The gap is real and triangulated by a full deep-read: no paper unifies the four axes, two papers explicitly name the contribution as future work, and the agent-amplification premise is already quantified (Reverse CAPTCHA, Cohen's *h* 1.37). The payloads and encoders are reused from prior work, and AgentDojo gives deterministic action-level scoring (not an LLM judge an injection could also hijack). The through-line ("per-unit safety is incomplete against composed harm") makes it a clean identity extension, not a topic pivot.

**Strongest case AGAINST (the risks to clear).**
- **Hot-field scoop race.** Two papers flag this as future work → others see it too. The systematic version is an obvious next step; timing/speed matters. → Move fast; lead with the decode-blind-spot *frame* + the plain-vs-encoded *control* + the image-rendered axis, which the anecdotes lack, so the contribution is more than "we ran the sweep."
- **Build cost.** An external agent harness is a materially bigger build than the eval-only VLM setup — the honest cost of this direction. → Anchor on AgentDojo (encoders slot in as a new `attack()`), keep the attack eval-only and decoupled; defer the coupled defense (§5.2).
- **"Encoding evades" is not surprising.** The reviewer's reflex is "of course encoding evades a classifier." → The non-obvious, load-bearing results are (a) it survives against *injection-specific, provenance-based* defenses (spotlighting/isolation), not just a content classifier, and (b) the plain-vs-encoded control quantifies *how much* of the defense's protection is surface-pattern-matching.

**Verdict (provisional, internal):** a real, defensible gap (Medium overlap), with a stronger novelty position than the parked judge-reliability line — gated on moving before the fast-moving field closes it, and on accepting the external-harness build cost. Advance to S5 (main story) and an S6 design + cost estimate.

# Review

Encoded Indirect Prompt Injection Bypasses Agent Defenses
Job ID: aff982bd-baa2-4c31-a1c9-4232f3987fe9

Completed on Jul 20, 2026 02:53

View submitted idea
Show abstract
Related papers

10

From last 2 years

10 / 10

Your idea in context
Your idea fits centrally into the cluster of agent security and indirect prompt injection. While retrieved papers explore structural (chat templates) or environmental (HTML) attack vectors and propose surface-level defenses, the your idea diverges by testing reversible encodings and image-rendered payloads. It explicitly addresses the gap of evaluating whether existing defenses are overly reliant on surface-form lexical patterns at the expense of decoded semantics.

ICML
×7
ICLR
×2
ACL
×1
What the field looks like
The dominant technical theme is the security of LLM-based agents, specifically focusing on indirect prompt injection (IPI) vulnerabilities and corresponding defense mechanisms. This likely caused co-retrieval due to shared terminology surrounding tool outputs, adversarial payloads, and agent execution harnesses.

high confidence
Methodological spectrum: Mostly empirical, focusing on evaluating attacks and defenses against state-of-the-art models on standard benchmarks, with a few theoretically driven or optimization-heavy outliers from unrelated domains.

◆
Also touches on
Development of training-free, inference-time defense mechanisms to detect or neutralize malicious instructions.#2
#5
Exploitation of structural, visual, or non-plaintext input modalities to bypass standard safety constraints.#3
#6
✦
Opportunities & gaps
No papers explore the theoretical upper bounds of learnability for IPI detection, such as formal proofs regarding whether a classifier can ever definitively separate instructions from untrusted data in an integrated prompt.
No papers address multi-agent collaborative security, specifically how indirect prompt injections might propagate or be mitigated when one compromised agent interacts within a cooperative swarm.
Related work (10)
1
iVGR: Internalizing Visually Grounded Reasoning for MLLMs with Reinforcement Learning
Chang-Bin Zhang, Yujie Zhong, Qiang Zhang, Kai Han
ICML 2026

🔍 Worth a look
82% match

While visually grounded Chain-of-Thought (CoT) has emerged as a promising paradigm to enhance fine-grained perception in multimodal large language models (MLLMs), its efficacy during the inference phase remains underexplored. In this work, we empirically find that mandating explicit object boxes in visually grounded CoT during inference often degrades performance compared to standard textual CoT, which reasons without explicit visual grounding. We hypothesize that the visual localization capability can be internalized into the textual CoT and that the mandatory explicit grounding introduces unnecessary interference with the model's primary objective of answer prediction. To address this problem, we propose Internalizing Visually Grounded Reasoning (**iVGR**), a novel reinforcement learning framework that transfers localization capabilities into the textual reasoning process. We employ a dual-stream training strategy, where a textual stream is aligned with a high-quality visually grounded stream via a proposed consistency reward, enabling the model to localize accurately without explicit grounding during inference. Extensive experiments demonstrate that our method significantly outperforms existing baselines on fine-grained benchmarks, while maintaining the flexibility to support tool-assisted inference workflows. Project page: https://visual-ai.github.io/ivgr/

Show more
What sets it apart

Internalizes visual grounding via dual-stream RL to eliminate explicit bounding box generation during inference. Sets a performance bar on V* and HR8K for Qwen-VL that new MLLM reasoning methods must beat.

Relevance to your idea

The problem setting involves multimodal LLM reasoning rather than agent security. The dual-stream RL methodology differs entirely from the query's attack evaluation framework, meaning results regarding visual grounding do not transfer to indirect prompt injection.

2
MELON: Provable Defense Against Indirect Prompt Injection Attacks in AI Agents
Kaijie Zhu, Xianjun Yang, Jindong Wang, Wenbo Guo, William Yang Wang
ICML 2025

🔍 Worth a look
82% match

Recent research has explored that LLM agents are vulnerable to indirect prompt injection (IPI) attacks, where malicious tasks embedded in tool-retrieved information can redirect the agent to take unauthorized actions. Existing defenses against IPI have significant limitations: either require essential model training resources, lack effectiveness against sophisticated attacks, or harm the normal utilities. We present MELON (Masked re-Execution and TooL comparisON), a novel IPI defense. Our approach builds on the observation that under a successful attack, the agent’s next action becomes less dependent on user tasks and more on malicious tasks. Following this, we design MELON to detect attacks by re-executing the agent’s trajectory with a masked user prompt modified through a masking function. We identify an attack if the actions generated in the original and masked executions are similar. We also include three key designs to reduce the potential false positives and false negatives. Extensive evaluation on the IPI benchmark AgentDojo demonstrates that MELON outperforms SOTA defenses in both attack prevention and utility preservation. Moreover, we show that combining MELON with a SOTA prompt augmentation defense (denoted as MELON-Aug) further improves its performance. We also conduct a detailed ablation study to validate our key designs. Code is available at https://github.com/kaijiezhu11/MELON.

Show more
What sets it apart

Introduces a training-free IPI defense that masks user prompts and re-executes trajectories to verify the causal dependency of anomalous tool calls. It sets a strong defense baseline on AgentDojo while maintaining high utility.

Relevance to your idea

Both focus on defending LLM agents against indirect prompt injection. While the query evaluates surface-level defense bypasses using encodings, this paper's semantic, trajectory-based defense might be uniquely robust to such encodings, offering a highly relevant baseline for comparison.

3
ChatInject: Abusing Chat Templates for Prompt Injection in LLM Agents
Hwan Chang, Yonghyun Jun, Hwanhee Lee
ICLR 2026

🔍 Worth a look
82% match

The growing deployment of large language model (LLM) based agents that interact with external environments has created new attack surfaces for adversarial manipulation. One major threat is indirect prompt injection, where attackers embed malicious instructions in external environment output, causing agents to interpret and execute them as if they were legitimate prompts. While previous research has focused primarily on plain-text injection attacks, we find a significant yet underexplored vulnerability: LLMs' dependence on structured chat templates and their susceptibility to contextual manipulation through persuasive multi-turn dialogues. To this end, we introduce ChatInject, an attack that formats malicious payloads to mimic native chat templates, thereby exploiting the model's inherent instruction-following tendencies. Building on this foundation, we develop a template-based Multi-turn variant that primes the agent across conversational turns to accept and execute otherwise suspicious actions. Through comprehensive experiments across frontier LLMs, we demonstrate three critical findings: (1) ChatInject achieves significantly higher average attack success rates than traditional prompt injection methods, improving from 5.18% to 32.05% on AgentDojo and from 15.13% to 45.90% on InjecAgent, with multi-turn dialogues showing particularly strong performance at average 52.33% success rate on InjecAgent, (2) chat-template-based payloads demonstrate strong transferability across models and remain effective even against closed-source LLMs, despite their unknown template structures, and (3) existing prompt-based defenses are largely ineffective against this attack approach, especially against Multi-turn variants. These findings highlight vulnerabilities in current agent systems. The code is available at https://github.com/hwanchang00/ChatInject.

Show more
What sets it apart

Demonstrates that role-delimiting chat template forgery within tool outputs acts as a major vector for indirect prompt injection. It establishes an attack success rate baseline on AgentDojo and InjecAgent that future IPI defenses must address.

Relevance to your idea

Both explore methods to achieve indirect prompt injection in LLM agents. This paper exploits structural chat templates while your idea uses reversible encodings, meaning both highlight different blind spots whose combined insights map the broader attack surface.

4
Causally Evaluating the Learnability of Formal Language Tasks
Vésteinn Snæbjarnarson, Anej Svete, Josef Valvoda, Reda Boumasmoud, Brian DuSell, Ryan Cotterell
ICML 2026

🔍 Worth a look
82% match

Language models, as multi-task learners, acquire a wide range of abilities during training. A fundamental question is how much task-specific data is needed to learn a given task. Answering this for natural language is difficult: tasks are hard to delineate and can confound one another. To rigorously investigate the relationship between data frequency and learnability, we turn to a controlled setting using formal languages induced from probabilistic finite automata. These serve as a methodological testbed to demonstrate that standard correlational evaluation practices are inherently flawed. To enable causal analysis, we introduce the binning semiring, an algebraic object that lets us control how often a targeted property occurs in a sampled corpus. We formulate the experimental pipeline as a causal graphical model and derive decomposed Kullback--Leibler divergence metrics to measure the learnability of specific sub-tasks. Our experiments show that evaluating learnability without causal intervention leads to incorrect conclusions due to confounders in correlational analysis, and serve as a warning about correlational pitfalls in natural-language settings.

Show more
What sets it apart

Isolates the causal effect of data frequency on learnability using a binning semiring and PFA constraint sampling. This forecloses prior claims based on correlational evaluation by disentangling frequency from structural confounders.

Relevance to your idea

The formal language learnability setting is entirely unrelated to prompt injection security. The exact-count sampling approach shares no methodological overlap with the query, and the theoretical findings offer no direct insight for agent defenses.

5
Defense Against Prompt Injection Attack by Leveraging Attack Techniques
Yulin Chen, Haoran Li, Zihao Zheng, Dekai Wu, Yangqiu Song, Bryan Hooi
ACL 2025

🔍 Worth a look
81% match

With the advancement of technology, large language models (LLMs) have achieved remarkable performance across various natural language processing (NLP) tasks, powering LLM-integrated applications like Microsoft Copilot. However, as LLMs continue to evolve, new vulnerabilities, especially prompt injection attacks arise. These attacks trick LLMs into deviating from the original input instructions and executing the attacker’s instructions injected in data content, such as retrieved results. Recent attack methods leverage LLMs’ instruction-following abilities and their inabilities to distinguish instructions injected in the data content, and achieve a high attack success rate (ASR). When comparing the attack and defense methods, we interestingly find that they share similar design goals, of inducing the model to ignore unwanted instructions and instead to execute wanted instructions. Therefore, we raise an intuitive question: *Could these attack techniques be utilized for defensive purposes?* In this paper, we invert the intention of prompt injection methods to develop novel defense methods based on previous training-free attack methods, by repeating the attack process but with the original input instruction rather than the injected instruction. Our comprehensive experiments demonstrate that our defense techniques outperform existing defense approaches, achieving state-of-the-art results.

Show more
What sets it apart

Creates a training-free defense by appending known attack techniques, like escape characters, as a final shield prompt. It establishes a strong baseline for prompt-based defenses without requiring fine-tuning.

Relevance to your idea

Both address the efficacy of defenses against prompt injection. This paper relies on surface-level textual shield prompts, which perfectly sets up the exact type of defense your idea hypothesizes will fail against encoded payloads.

6
AdvAgent: Controllable Blackbox Red-teaming on Web Agents
Chejian Xu, Mintong Kang, Jiawei Zhang, Zeyi Liao, Lingbo Mo, Mengqi Yuan, Huan Sun, Bo Li
ICML 2025

🔍 Worth a look
80% match

Foundation model-based agents are increasingly used to automate complex tasks, enhancing efficiency and productivity. However, their access to sensitive resources and autonomous decision-making also introduce significant security risks, where successful attacks could lead to severe consequences. To systematically uncover these vulnerabilities, we propose AdvAgent, a black-box red-teaming framework for attacking web agents. Unlike existing approaches, AdvAgent employs a reinforcement learning-based pipeline to train an adversarial prompter model that optimizes adversarial prompts using feedback from the black-box agent. With careful attack design, these prompts effectively exploit agent weaknesses while maintaining stealthiness and controllability. Extensive evaluations demonstrate that AdvAgent achieves high success rates against state-of-the-art GPT-4-based web agents across diverse web tasks. Furthermore, we find that existing prompt-based defenses provide only limited protection, leaving agents vulnerable to our framework. These findings highlight critical vulnerabilities in current web agents and emphasize the urgent need for stronger defense mechanisms. We release code at https://ai-secure.github.io/AdvAgent/.

Show more
What sets it apart

Optimizes invisible HTML prompt injection for web agents using black-box Direct Policy Optimization. It sets a high attack success rate benchmark against top-tier vision-language web agents like GPT-4V.

Relevance to your idea

Both explore non-standard, visually or structurally obfuscated indirect prompt injections. This paper uses RL to optimize HTML placement, whereas the query uses fixed reversible encodings, but this paper's findings on multimodal agent vulnerabilities directly support the query's claims.

7
Preconditioned DeltaNet: Curvature-aware Sequence Modeling for Linear Recurrences
Neehal Tumma, Noel Loo, Daniela Rus
ICML 2026

🔍 Worth a look
80% match

To address the increasing long-context compute limitations of softmax attention, several subquadratic recurrent operators have been developed. This work includes models such as Mamba-2, DeltaNet, Gated DeltaNet (GDN), and Kimi Delta Attention (KDA). As the space of recurrences grows, a parallel line of work has arisen to taxonomize them. One compelling view is the test-time regression (TTR) framework, which interprets recurrences as performing online least squares updates that learn a linear map from the keys to values. Existing delta-rule recurrences can be seen as first-order approximations to this objective, but notably ignore the curvature of the least-squares loss during optimization. In this work, we address this by introducing preconditioning to these recurrences. Starting from the theory of online least squares, we derive equivalences between linear attention and the delta rule in the exactly preconditioned case. Next, we realize this theory in practice by proposing a diagonal approximation: this enables us to introduce preconditioned variants of DeltaNet, GDN, and KDA alongside efficient chunkwise parallel algorithms for computing them. Empirically, we find that our preconditioned delta-rule recurrences yield consistent performance improvements across synthetic recall benchmarks and language modeling at the 340M and 1B scale.

Show more
What sets it apart

Preconditions linear recurrences using an inverse key Gram matrix to approximate exact least squares. It sets a new throughput-efficiency standard for long-context sequence modeling that subsequent architectures must compare against.

Relevance to your idea

The long-context sequence modeling domain is orthogonal to adversarial prompt injection. The mathematical preconditioning method differs completely from the query's empirical security evaluations, so the results do not transfer.

8
Prompt Reinjection: Alleviating Prompt Forgetting in Multimodal Diffusion Transformers
Yuxuan Yao, Yuxuan Chen, Hui Li, Kaihui Cheng, Qipeng Guo, Yuwei Sun, Zilong Dong, Jingdong Wang, Siyu Zhu
ICML 2026

🔍 Worth a look
80% match

Multimodal Diffusion Transformers (MMDiTs) for text-to-image generation maintain separate text and image branches, with bidirectional information flow between text tokens and visual latents throughout denoising. In this setting, we observe a prompt forgetting phenomenon: the semantics of the prompt representation in the text branch is progressively forgotten as depth increases. We further verify this effect on three representative MMDiTs—SD3, SD3.5, and FLUX.1 by probing linguistic attributes of the representations over the layers in the text branch. Motivated by these findings, we introduce a training-free approach, prompt reinjection, which reinjects prompt representations from early layers into later layers to alleviate this forgetting. Experiments on GenEval, DPG, and T2I-CompBench++ show consistent gains in instruction-following capability, along with improvements on metrics capturing preference, aesthetics, and overall text--image generation quality.

Show more
What sets it apart

Fixes text feature drift in multimodal diffusion transformers via inference-time residual addition of shallow features. It introduces distribution anchoring and geometry alignment mechanisms that subsequent MMDiT interventions must build upon.

Relevance to your idea

The setting focuses on text fidelity in image generation rather than adversarial instructions in agent tools. While both touch on multimodal text processing, the residual addition methodology is fundamentally different, preventing direct result transfer.

9
Agent Security Bench (ASB): Formalizing and Benchmarking Attacks and Defenses in LLM-based Agents
Hanrong Zhang, Jingyuan Huang, Kai Mei, Yifei Yao, Zhenting Wang, Chenlu Zhan, Hongwei Wang, Yongfeng Zhang
ICLR 2025

🔍 Worth a look
80% match
What sets it apart

Establishes a comprehensive multi-stage security benchmark for LLM agents and introduces the Plan-of-Thought backdoor. It provides the Net Resilient Performance metric that future agent security evaluations should adopt.

Relevance to your idea

Both investigate vulnerabilities and defenses in tool-using LLM agents. This paper provides a broad benchmarking framework, while the query introduces a specific evaluation axis for encoded payloads, meaning the query's attacks could directly integrate into this paper's testbed.

10
Multi-timescale Reinforcement Learning by Value Reconstruction
Zhan Su, Peixi Peng, Xinyu Hu, Cong Li, Yisen Zhao, Zhuojian Li, Yonghong Tian, Fanqi Shen
ICML 2026

🔍 Worth a look
80% match

Most reinforcement learning (RL) baselines maximize future cumulative rewards with a fixed single discount factor, which limits their performance in complex sequential decision-making tasks due to a failure to balance short-term objectives and long-term planning. To address this issue, this paper focuses on a multi-timescale critic framework, where each component corresponds to a Q-value with a distinct discount factor. Two key improvements are proposed: (1) A Neural Reward Decoder reconstructs the reward sequence from multi-scale Q-values, with value and reward reconstruction losses enhancing Q-value estimation consistency; (2) A cross-attention-based Q-weight predictor adaptively adjusts Q-value weights via current observations to generate the final Q-value for policy optimization. Extensive experiments on DMControl and CARLA benchmarks demonstrate that our method significantly outperforms state-of-the-art (SOTA) baselines. Furthermore, we validate the framework's generalizability by integrating it with both off-policy (SAC, DrQ-v2) and on-policy (PPO) algorithms, achieving consistent performance gains. The code is available in the supplementary material.

Show more
What sets it apart

Solves multi-scale temporal RL using a Neural Reward Decoder to enforce bidirectional consistency across discount factors. It sets a new performance bar on DMControl hard tasks that future continuous control methods must exceed.

Relevance to your idea

The continuous control RL setting is disconnected from LLM agent security. The neural reward decoding method shares no overlap with evaluating prompt injection payloads, and the findings do not transfer to the query's problem.