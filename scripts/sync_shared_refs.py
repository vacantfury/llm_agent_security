#!/usr/bin/env python3
"""Reconcile the shared-encoding bib overlap between this repo and its sibling.

This repo (llm_agent_security) and its sibling (llm_guardrail_security)
share the ENCODERS as payloads, so their encoding-literature citations overlap. The
oikos charter bars a research-bet -> research-bet import dependency, so the two
`paper/literature/my_base.bib` files are kept as separate copies (see CLAUDE.md
"Scope boundary"). This tool keeps the overlap honest:

  * it matches entries across the two bibs by CONTENT identity (arXiv id -> venue
    DOI -> title), because the citation KEYS differ freely between the repos;
  * it reports metadata conflicts on matched papers (stale arXiv versions,
    year/title drift, a published entry on one side vs a preprint on the other);
  * it lists the one-sided entries as porting candidates.

It NEVER writes to either bib. Whether a given paper belongs in both repos is a
scope-boundary judgment (agent-specific vs VLM-specific vs genuinely shared
encoder lit), so porting stays a manual decision. This is the deterministic half
(match + diff); the judgment half stays with the maintainer.

Usage:
    uv run python scripts/sync_shared_refs.py            # report to stdout
    uv run python scripts/sync_shared_refs.py --show-only # also dump one-sided lists
    uv run python scripts/sync_shared_refs.py --json      # machine-readable
    uv run python scripts/sync_shared_refs.py --strict    # exit 1 if conflicts found
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from difflib import SequenceMatcher
from pathlib import Path

import bibtexparser
import yaml
from bibtexparser.bparser import BibTexParser

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CONFIG = REPO_ROOT / "conf" / "sync_shared_refs.yaml"

# arXiv ids: new-style NNNN.NNNNN (4-digit YYMM, 4-5 digit sequence), optional vN.
_ARXIV_RE = re.compile(r"(\d{4}\.\d{4,5})(v\d+)?", re.IGNORECASE)
_ARXIV_URL_RE = re.compile(r"arxiv\.org/abs/(\d{4}\.\d{4,5})(v\d+)?", re.IGNORECASE)
_ARXIV_DOI_RE = re.compile(r"10\.48550/arxiv\.(\d{4}\.\d{4,5})(v\d+)?", re.IGNORECASE)
_DOI_URL_RE = re.compile(r"doi\.org/(10\.\S+)", re.IGNORECASE)


# --------------------------------------------------------------------------- #
# Config                                                                      #
# --------------------------------------------------------------------------- #
def load_config(path: Path) -> dict:
    with open(path, encoding="utf-8") as fh:
        return yaml.safe_load(fh)


# --------------------------------------------------------------------------- #
# Bib loading + identity extraction                                           #
# --------------------------------------------------------------------------- #
@dataclass
class Ref:
    """The identity + a few metadata fields we reconcile on."""

    key: str
    entrytype: str
    title_raw: str
    title_norm: str
    year: str
    arxiv_id: str | None
    arxiv_version: str | None
    doi: str | None
    is_published: bool
    raw: dict = field(repr=False)


def load_entries(path: Path) -> list[dict]:
    parser = BibTexParser(common_strings=True)
    parser.ignore_nonstandard_types = False
    parser.homogenize_fields = False
    with open(path, encoding="utf-8") as fh:
        db = bibtexparser.load(fh, parser=parser)
    return db.entries


def _clean(value: str) -> str:
    return re.sub(r"\s+", " ", value.replace("{", "").replace("}", "")).strip()


def normalize_title(entry: dict) -> str:
    title = entry.get("title", "")
    title = re.sub(r"[{}]", "", title).lower()
    title = re.sub(r"[^a-z0-9]+", " ", title)
    return re.sub(r"\s+", " ", title).strip()


def extract_arxiv(entry: dict) -> tuple[str | None, str | None]:
    """Return (normalized arXiv id, raw version like 'v2' or None)."""
    archive = entry.get("archiveprefix", "").lower()
    eprint = entry.get("eprint", "").strip()
    if eprint:
        m = _ARXIV_RE.search(eprint)
        if m and ("arxiv" in archive or m.group(0) == eprint or m.start() == 0):
            return m.group(1).lower(), (m.group(2).lower() if m.group(2) else None)
    for fname in ("url", "doi", "note"):
        val = entry.get(fname, "")
        if not val:
            continue
        m = _ARXIV_URL_RE.search(val) or _ARXIV_DOI_RE.search(val)
        if m:
            return m.group(1).lower(), (m.group(2).lower() if m.group(2) else None)
    return None, None


def extract_doi(entry: dict, arxiv_doi_prefixes: list[str]) -> str | None:
    doi = entry.get("doi", "").strip().lower()
    if not doi:
        m = _DOI_URL_RE.search(entry.get("url", ""))
        doi = m.group(1).lower() if m else ""
    doi = doi.strip().rstrip(".")
    if not doi:
        return None
    if any(doi.startswith(p) for p in arxiv_doi_prefixes):
        return None  # arXiv preprint DOI -> identity carried by the arXiv id
    return doi


def to_ref(entry: dict, cfg: dict) -> Ref:
    arxiv_id, arxiv_version = extract_arxiv(entry)
    doi = extract_doi(entry, cfg["matching"]["arxiv_doi_prefixes"])
    etype = entry.get("ENTRYTYPE", "").lower()
    has_venue = bool(entry.get("booktitle") or entry.get("journal"))
    is_published = etype in {"inproceedings", "article"} and has_venue
    return Ref(
        key=entry.get("ID", "?"),
        entrytype=etype,
        title_raw=_clean(entry.get("title", "")),
        title_norm=normalize_title(entry),
        year=entry.get("year", "").strip(),
        arxiv_id=arxiv_id,
        arxiv_version=arxiv_version,
        doi=doi,
        is_published=is_published,
        raw=entry,
    )


# --------------------------------------------------------------------------- #
# Matching                                                                    #
# --------------------------------------------------------------------------- #
@dataclass
class Pair:
    local: Ref
    sibling: Ref
    method: str  # arxiv | doi | title_exact | title_fuzzy


def _index(refs: list[Ref], attr: str) -> dict[str, list[int]]:
    idx: dict[str, list[int]] = {}
    for i, ref in enumerate(refs):
        val = getattr(ref, attr)
        if val:
            idx.setdefault(val, []).append(i)
    return idx


def match_bibs(
    local: list[Ref], sibling: list[Ref], cfg: dict
) -> tuple[list[Pair], list[Ref], list[Ref]]:
    consumed: set[int] = set()
    pairs: list[Pair] = []
    matched_local: set[int] = set()

    sib_by_arxiv = _index(sibling, "arxiv_id")
    sib_by_doi = _index(sibling, "doi")
    sib_by_title = _index(sibling, "title_norm")

    def take(candidates: list[int]) -> int | None:
        for j in candidates:
            if j not in consumed:
                return j
        return None

    # Strong-key passes, in order of identity strength.
    for method, index, attr in (
        ("arxiv", sib_by_arxiv, "arxiv_id"),
        ("doi", sib_by_doi, "doi"),
        ("title_exact", sib_by_title, "title_norm"),
    ):
        for i, ref in enumerate(local):
            if i in matched_local:
                continue
            val = getattr(ref, attr)
            if not val:
                continue
            j = take(index.get(val, []))
            if j is not None:
                consumed.add(j)
                matched_local.add(i)
                pairs.append(Pair(ref, sibling[j], method))

    # Fuzzy title pass over whatever is still unmatched on both sides.
    thr = cfg["matching"]["title_similarity_threshold"]
    len_pre = cfg["matching"]["title_length_prefilter"]
    rem_sibling = [j for j in range(len(sibling)) if j not in consumed]
    for i, ref in enumerate(local):
        if i in matched_local or not ref.title_norm:
            continue
        best_j, best_ratio = None, 0.0
        for j in rem_sibling:
            if j in consumed:
                continue
            other = sibling[j].title_norm
            if not other:
                continue
            la, lb = len(ref.title_norm), len(other)
            if min(la, lb) / max(la, lb) < len_pre:
                continue
            ratio = SequenceMatcher(None, ref.title_norm, other).ratio()
            if ratio > best_ratio:
                best_ratio, best_j = ratio, j
        if best_j is not None and best_ratio >= thr:
            consumed.add(best_j)
            matched_local.add(i)
            pairs.append(Pair(ref, sibling[best_j], "title_fuzzy"))

    only_local = [r for i, r in enumerate(local) if i not in matched_local]
    only_sibling = [r for j, r in enumerate(sibling) if j not in consumed]
    return pairs, only_local, only_sibling


# --------------------------------------------------------------------------- #
# Conflict classification                                                     #
# --------------------------------------------------------------------------- #
@dataclass
class Issue:
    severity: str  # conflict | note | info
    category: str
    detail: str


def classify(pair: Pair, cfg: dict) -> list[Issue]:
    sev = cfg["conflicts"]
    issues: list[Issue] = []
    a, b = pair.local, pair.sibling

    if a.year and b.year and a.year != b.year:
        issues.append(
            Issue(sev["year_mismatch"], "year_mismatch", f"local year={a.year}  sibling year={b.year}")
        )

    if a.arxiv_version and b.arxiv_version and a.arxiv_version != b.arxiv_version:
        issues.append(
            Issue(
                sev["arxiv_version_mismatch"],
                "arxiv_version_mismatch",
                f"local {a.arxiv_id}{a.arxiv_version}  sibling {b.arxiv_id}{b.arxiv_version}",
            )
        )

    # Title drift only meaningful when matched by a STRONG key (fuzzy already
    # implies near-identical titles by construction).
    if pair.method in {"arxiv", "doi", "title_exact"} and a.title_norm and b.title_norm:
        ratio = SequenceMatcher(None, a.title_norm, b.title_norm).ratio()
        if ratio < 0.80:
            issues.append(
                Issue(
                    sev["title_drift"],
                    "title_drift",
                    f'ratio={ratio:.2f}  local="{a.title_raw}"  sibling="{b.title_raw}"',
                )
            )

    if a.is_published != b.is_published:
        pub, pre = (a, b) if a.is_published else (b, a)
        pub_side = "local" if a.is_published else "sibling"
        issues.append(
            Issue(
                sev["published_upgrade"],
                "published_upgrade",
                f"{pub_side} has published ({pub.entrytype}); other still preprint ({pre.entrytype})",
            )
        )

    if a.key != b.key:
        issues.append(Issue(sev["key_mismatch"], "key_mismatch", f"local={a.key}  sibling={b.key}"))

    return issues


# --------------------------------------------------------------------------- #
# Reporting                                                                   #
# --------------------------------------------------------------------------- #
SEV_ORDER = {"conflict": 0, "note": 1, "info": 2}


def identity_str(ref: Ref) -> str:
    if ref.arxiv_id:
        return f"arXiv:{ref.arxiv_id}"
    if ref.doi:
        return f"doi:{ref.doi}"
    return "title-only"


def render_text(pairs, only_local, only_sibling, cfg, local_path, sibling_path) -> tuple[str, int]:
    lines: list[str] = []
    n_local = len(pairs) + len(only_local)
    n_sibling = len(pairs) + len(only_sibling)

    flagged = [(p, [i for i in classify(p, cfg) if i.severity != "info"]) for p in pairs]
    flagged = [(p, iss) for p, iss in flagged if iss]
    n_conflict = sum(1 for _, iss in flagged if any(i.severity == "conflict" for i in iss))

    lines.append(f"=== bib sync: {cfg['local_label']} <-> {cfg['sibling_label']} ===")
    lines.append(f"local  : {local_path}  ({n_local} entries)")
    lines.append(f"sibling: {sibling_path}  ({n_sibling} entries)")
    lines.append("")
    lines.append(f"Shared (matched in both) : {len(pairs)}")
    lines.append(f"  needs attention        : {len(flagged)}  ({n_conflict} conflict)")
    lines.append(f"Only in local            : {len(only_local)}")
    lines.append(f"Only in sibling          : {len(only_sibling)}")
    lines.append("")

    if flagged:
        lines.append("--- MATCHED PAPERS NEEDING ATTENTION ---")
        for pair, issues in sorted(
            flagged, key=lambda x: min(SEV_ORDER[i.severity] for i in x[1])
        ):
            lines.append(f'\n  "{pair.local.title_raw}"  [{identity_str(pair.local)}, match={pair.method}]')
            for iss in sorted(issues, key=lambda i: SEV_ORDER[i.severity]):
                lines.append(f"    [{iss.severity}: {iss.category}] {iss.detail}")
        lines.append("")

    if cfg["report"]["show_only_in"]:
        limit = cfg["report"]["only_in_limit"]
        for label, refs in (("local", only_local), ("sibling", only_sibling)):
            lines.append(f"--- Only in {label} (porting candidates; judgment required) ---")
            for ref in refs[:limit]:
                lines.append(f"  {ref.key}  [{identity_str(ref)}]  {ref.title_raw}")
            if len(refs) > limit:
                lines.append(f"  ... and {len(refs) - limit} more (raise report.only_in_limit)")
            lines.append("")

    if not flagged:
        lines.append("No metadata conflicts on shared entries. ✓")

    return "\n".join(lines), n_conflict


def render_json(pairs, only_local, only_sibling, cfg) -> tuple[str, int]:
    matched = []
    n_conflict = 0
    for p in pairs:
        issues = classify(p, cfg)
        real = [i for i in issues if i.severity != "info"]
        if any(i.severity == "conflict" for i in real):
            n_conflict += 1
        matched.append(
            {
                "identity": identity_str(p.local),
                "method": p.method,
                "local_key": p.local.key,
                "sibling_key": p.sibling.key,
                "title": p.local.title_raw,
                "issues": [{"severity": i.severity, "category": i.category, "detail": i.detail} for i in issues],
            }
        )
    payload = {
        "shared": len(pairs),
        "conflicts": n_conflict,
        "only_local": [{"key": r.key, "identity": identity_str(r), "title": r.title_raw} for r in only_local],
        "only_sibling": [{"key": r.key, "identity": identity_str(r), "title": r.title_raw} for r in only_sibling],
        "matched": matched,
    }
    return json.dumps(payload, indent=2, ensure_ascii=False), n_conflict


# --------------------------------------------------------------------------- #
# Main                                                                        #
# --------------------------------------------------------------------------- #
def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    ap.add_argument("--local", type=Path, help="override local bib path")
    ap.add_argument("--sibling", type=Path, help="override sibling bib path")
    ap.add_argument("--show-only", action="store_true", help="list the one-sided entries")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    ap.add_argument("--strict", action="store_true", help="exit 1 if any conflict is found")
    args = ap.parse_args()

    cfg = load_config(args.config)
    if args.show_only:
        cfg["report"]["show_only_in"] = True

    def resolve(p: Path) -> Path:
        return p if p.is_absolute() else (REPO_ROOT / p)

    local_path = resolve(args.local or Path(cfg["local_bib"]))
    sibling_path = resolve(args.sibling or Path(cfg["sibling_bib"]))

    for label, p in (("local", local_path), ("sibling", sibling_path)):
        if not p.exists():
            print(f"error: {label} bib not found: {p}", file=sys.stderr)
            return 2

    local_refs = [to_ref(e, cfg) for e in load_entries(local_path)]
    sibling_refs = [to_ref(e, cfg) for e in load_entries(sibling_path)]

    pairs, only_local, only_sibling = match_bibs(local_refs, sibling_refs, cfg)

    if args.json:
        out, n_conflict = render_json(pairs, only_local, only_sibling, cfg)
    else:
        out, n_conflict = render_text(
            pairs, only_local, only_sibling, cfg, local_path.name, sibling_path.name
        )
    print(out)

    return 1 if (args.strict and n_conflict) else 0


if __name__ == "__main__":
    raise SystemExit(main())
