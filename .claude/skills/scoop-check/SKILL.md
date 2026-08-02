---
name: scoop-check
description: Verify whether a specific claimed research contribution/novelty is already covered by existing work — decomposes the claim into 4 axes (problem framing, core mechanism, key insight, application domain), searches + triages prior art, deep-dives the closest candidates, and produces a 5-level overlap verdict plus a one-sentence delta statement. Triggers on "check if an idea is novel", "check if this is already scooped", "prior-art check for a specific claim", "novelty check", "has this been done", "verify our contribution is new", "scoop check", "am I scooped". Delegates the actual paper download+verify to lit-review-loop — never fetches PDFs itself. NOT for general literature reviews unrelated to a specific novelty claim — use lit-review-loop for that.
---

# Scoop Check

Verify whether a proposed research novelty overlaps with existing literature. The goal is either (a) surface prior work that already covers the claim, or (b) produce a crisp, defensible one-sentence "delta" that distinguishes the contribution. Adapted from `other_repos/ResearchStudio/ResearchStudio-Idea/skills/scoop_check/` — the decompose/rubric/funnel/delta machinery is preserved; the fetch/logging/persistence layer is rewired to this repo's house rules below.

**Corpus home since 2026-08-02:** the shared literature corpus moved into the science repo (`vacantfury/science`, private; local path recorded in `paper/literature/README.md`) under `literature/llm-security/` — master `references.bib` (328 entries, merged 2026-08-02 from both AI-safety repos' `my_base.bib`) + per-paper `papers/<paper-name>/` bundles (PDF + `source/`) + legacy flat `pdfs/` + `reviews/` (this repo's is `agent_prompt_injection_review.md`). This repo's own `paper/literature/my_base.bib` now holds only this paper's own (to-be-trimmed) cited subset — all candidate staging happens in the science master bib.

## Inputs

Two inputs: **Research problem** (the specific gap being addressed) and **Novelty** (the specific claimed contribution — method, theorem, dataset, framing, or insight). If either is missing, vague, or the novelty merely restates the problem, infer the most reasonable interpretation and proceed — do not use `AskUserQuestion` for the framing/decompose/search steps (Steps 0–3). The one exception is the download hand-off in Step 4, which follows lit-review-loop's own shared-step rule (offer to download, don't reflexively stop-and-wait, but the owner may take it).

## Operating principles (how this differs from the source skill)

- **This skill never downloads or fetches a PDF.** A Step 4 high-potential candidate is staged as a `% CANDIDATE <date>` BibTeX entry in the science master `references.bib` (`literature/llm-security/references.bib`; same convention lit-review-loop's Phase 1 uses) and the actual download+verify is handed to **`lit-review-loop`'s Phase 2** — shared, owner or me, never silently skipped. Don't write a fetch script; don't hand-roll a `curl`/`pdftotext` pipeline — that's lit-review-loop's job.
- **Check what's already staged/known before searching** (Step 0) — the science master bib is already 328 entries; a scoop-check that re-searches from scratch wastes a round-trip and risks re-staging a duplicate.
- **Logs are gitignored.** Per-step logs go to `outputs/scoop_check/<date>/`, never the repo root — this repo is public, and a root-level `stepN.md` would leak an unpublished prior-art gap analysis into a public commit. (`outputs/` is already gitignored repo-wide; no `.gitignore` edit needed.)
- **Persist the verdict.** The final Verdict + Delta get written as a dated line into the relevant paper's decision log (`text_docs/<paper>/experiments_plan.md`) so the check survives a session reset — the source skill only prints to the conversation.

## Step 0 — Check what's already known

Before searching, rule out re-staging something already in hand:
- Existing bib titles/keys: skim the science master `references.bib` (`literature/llm-security/references.bib`; grep titles, not abstract bodies — entries carry full abstracts).
- Existing write-up coverage: `grep -nE '^#{1,3} '` science `literature/llm-security/reviews/agent_prompt_injection_review.md` (organized by attack/defense/eval taxonomy — §3 image attacks, §5 encoding attacks, §6 defenses, §7 eval).
- Already-downloaded-but-unstaged papers: `ls` science `literature/llm-security/papers/` (plus legacy `pdfs/`) — some papers are on disk with no bib entry yet.

State the concrete "what's already covered" list before moving to Step 1, so Step 2's search targets only the gap.

## Step 1 — Decompose the Novelty

Break the claimed **Novelty** into four atomic axes, presented as a labeled list:

- **Problem framing** — Task definition, inputs, outputs, and evaluation regime.
- **Core mechanism** — The technical contribution — architecture, algorithm, proof technique, or data construction.
- **Key insight** — What makes it work; what prior state-of-the-art lacked.
- **Application domain** — Where it applies and how broadly.

## Step 2 — Search and Deduplicate

Craft three complementary search queries from the **Research problem**: **Query 1 — Original-Problem** (restate it directly), **Query 2 — Broad-Domain** (the high-level area, ~3–5 words), **Query 3 — Method-Signature** (the specific technical move, ~5–8 words).

This repo has no standalone `paper-search` skill — run the three queries through the general search skills lit-review-loop already wraps (`literature-search-arxiv`, `literature-search-openalex`, `citation-management`); delegate the fan-out to subagents on a cheaper model per lit-review-loop's own cost-discipline habit if the query count warrants it. Merge results across all three queries and deduplicate by normalized title (case/whitespace-insensitive) — against **both** the live results **and** Step 0's existing-bib title list, so a paper already staged doesn't get re-surfaced as new.

After the search-based results are merged, augment with **papers recalled from training knowledge** that are directly relevant but didn't surface in search — search routinely misses landmark or tangentially-phrased prior work, and missing the canonical reference is the most common way a novelty check fails. Constraints on recalled papers:
- **No overlap** — check by normalized title (and arXiv ID/DOI when available) against the deduplicated set before adding.
- **Mark provenance** — tag each recalled entry `Source: model-recall` so Step 4/5 know it needs extra verification.
- **Stay modest** — typically 0–5 recalled papers; add none if you can't recall any with confidence. Fabricating citations is far worse than a smaller candidate pool.
- **Flag uncertainty** — leave date/venue/author fields blank rather than guessing; Step 5's deep dive resolves them from the real paper.

## Step 3 — Abstract-Level Triage

For every deduplicated paper, extract from title + abstract: **Title**, **Date** (YYYY-MM), **Problem framing**, **Core mechanism**, **Key insight**, **Application domain**, **Overlap score (0–4)** — number of the four axes that plausibly match the proposed novelty, judging from the abstract alone (feeds `level = 5 − axes_matched` in Step 6) — and **Source** (URL/arXiv ID/DOI). The overlap score is a triage signal, not a final verdict — abstracts hide the details (assumptions, scope, limitations) that live only in the body.

## Step 4 — Identify High-Potential Candidates, Stage, and Hand Off

A paper is a **high-potential candidate** if any hold: overlap score ≥ 2 · **mechanism-match escalation** — the abstract matches on core mechanism specifically, even if framing/domain differ, since mechanism overlap is the most dangerous kind and always escalates to a full read regardless of the other axes · same narrow subfield within the last 24 months, even at a lower score · the abstract is ambiguous in a way that can't rule out overlap from the abstract alone. Apply uniformly to search results and recalled papers alike — a recalled paper doesn't get auto-promoted for being recalled, or auto-demoted for being unverified.

Cap the set at **3–7 papers** after triage (keep the highest-overlap, tie-break toward mechanism matches and recency; if fewer than 3 qualify, lower the threshold so Step 5 still has coverage). List each candidate with its selection reason.

**Stage, don't fetch.** For each candidate, append a `% CANDIDATE <date>` comment + a BibTeX entry carrying `note = {CANDIDATE — verify+download}` to the science master `references.bib` (`literature/llm-security/references.bib`; key style `authorYYYYshorttitle`, matching the file's existing convention) — auto-generated metadata is unverified until downloaded. Then hand off to **`lit-review-loop`'s Phase 2** for the download+verify, under its **division-by-citation-metadata-clarity rule** (owner rule 2026-07-24): I do every candidate whose metadata is CLEAR (plain-arXiv-only, or confirmable published venue); the owner takes the UNCLEAR ones — found only on arXiv but looks actually published at a venue I can't pin down — which I FLAG (never guess the venue) for him to resolve and append to the bottom of the science master `references.bib`. (Auth-walled / non-arXiv also go to him.) Don't proceed to Step 5 for a candidate until its download+verify has actually landed.

## Step 5 — Full-Paper Deep Dive on Candidates

Once lit-review-loop's Phase 2 has landed a candidate's PDF + `source/` in science `literature/llm-security/papers/<paper-name>/`, read it — prefer the `.tex`/HTML `source/` over the PDF (PDF extraction garbles tables/math/figures, per lit-review-loop). Don't hand a PDF URL to `WebFetch` for this — it returns a model-written summary that drops the methodological detail this step exists to capture.

**Budget per paper:** skim, don't read end-to-end. Once you've quoted or referenced **three concrete passages** that together pin down the problem setup, the core mechanism, and the scope/assumptions, stop — you have enough for the verified record. For unusually large documents (a thesis, a survey, heavy appendices), restrict the skim to intro/method/conclusion and note the partial coverage. If a candidate's download failed or was auth-walled and lit-review-loop couldn't land it, fall back to `WebFetch` on the abstract/HTML with a targeted question and record the limitation explicitly — never claim to have read the full paper when you haven't.

Extract a richer record that **supersedes** the abstract-level entry: **Problem framing (verified)**, **Core mechanism (verified)**, **Key insight (verified)**, **Application domain (verified)**, **Venue (verified)** (use "arXiv preprint" if not yet peer-reviewed, "unknown" only if genuinely undisclosed), **Assumptions & scope**, **Closest-passage evidence** (a short verbatim quote or precise section reference), **Refined overlap** (per-axis match/partial/differ, now grounded in the body). Downgrade a paper that turns out to target a different setting or mechanism; upgrade one where the body reveals a closer match than the abstract suggested.

## Step 6 — Compare Against the Proposed Novelty

Build a comparison list — proposed work first, then each prior work — with every entry carrying the same fields (Title, Date, Source, Problem framing, Core mechanism, Key insight, Application domain), each `Field: value` on its own indented line.

For each prior work, count how many of the four axes match (0–4) and map to one of five novelty levels — **Level 5 is most novel** (no axis overlaps), **Level 1 is least novel** (all four match / fully scooped):

| Axes matching | Level | Label |
|---|---|---|
| 0 | 5 | **No Overlap** — most novel |
| 1 | 4 | **Low Overlap** |
| 2 | 3 | **Medium Overlap** |
| 3 | 2 | **High Overlap** |
| 4 | 1 | **Full Overlap** — fully scooped, least novel |

The overall verdict is the **worst case — the minimum level across all prior works** (a single closest prior work caps the novelty). No prior works at all → Level 5.

## Step 7 — Articulate the Delta

Produce a one-sentence delta:

> Unlike [closest prior work], which [does X under assumption Y], the proposed work [does X′ / drops Y / extends to Z], yielding [concrete measurable benefit].

Name the closest prior work, the specific axis of divergence, and the resulting benefit concretely — draw the assumption/mechanism phrasing from Step 5's verified record when the closest work went through the deep dive. If no crisp one-sentence delta can be written, say so explicitly and name which prior work is blocking it, rather than forcing a sentence that doesn't hold.

Roll up Step 6's per-paper levels into the overall **Verdict** (minimum level across all prior works):

- **Level 5 — No Overlap** — every entry all-axes-differ, or no prior works at all. The delta stands on its own.
- **Level 4 — Low Overlap** — closest entry matches one axis. The delta is comfortable.
- **Level 3 — Medium Overlap** — closest entry matches two axes. The delta is defensible but must be stated explicitly in any write-up.
- **Level 2 — High Overlap** — closest entry matches three axes. The delta hinges on a single distinguishing axis and is fragile — sharpen or reframe.
- **Level 1 — Full Overlap** — some entry matches all four axes. Recommend reframing the contribution.

State the verdict with its level number and label, then a one-paragraph justification naming the specific papers driving the decision.

## Report

Render inline in the conversation, in this order, with no omissions:
1. **Verdict** — the level + label from Step 7.
2. **Delta** — the one-sentence statement (or the explicit "no crisp delta" call-out).
3. **Decomposed claim** — Step 1's four axes.
4. **Structured papers** — every deduplicated paper from Step 3 (all fields); if zero results, say so and list the queries used.
5. **Comparison result** — Step 6's full list, each entry's per-axis fields plus its level/label.

## Persist the verdict

Append a dated line to the relevant paper's decision log — `text_docs/<paper>/experiments_plan.md` where `<paper>` is `autoattack_defense` (C) / `bestofn_defense` (D) / `imgaug_defense` (B), inferred from which paper line the novelty claim belongs to (ask only if genuinely ambiguous between two live papers). Line = date, verdict level/label, one-line delta, and the closest prior work's title. This is what survives a session reset — the Report above is conversation-only.

## Important Notes

- **Negative results are valuable.** A thorough search that returns nothing is itself evidence of novelty — document the queries used.
- **Log every step.** After each step, write a markdown file to `outputs/scoop_check/<date>/step{N}.md` with the step number, name, timestamp, and full structured result — gitignored, never the repo root.
- **Display the full report.** Give the complete report in the conversation — search results, analysis, and reasoning — not a summary.
- **Never fabricate.** Recalled papers with uncertain metadata get blank fields, not guesses; a candidate stays `CANDIDATE — verify+download` until lit-review-loop's Phase 2 actually lands it.

## References

- `.claude/skills/lit-review-loop/SKILL.md` — owns Phase 2 (download+verify) and Phase 3 (write-up into science `literature/llm-security/reviews/agent_prompt_injection_review.md`); this skill only stages candidates and hands off.
- science `literature/llm-security/references.bib` — candidate + verified bib entries.
- science `literature/llm-security/reviews/agent_prompt_injection_review.md` — existing coverage, checked in Step 0.
