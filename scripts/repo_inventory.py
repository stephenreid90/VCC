#!/usr/bin/env python3
"""Generate REPO_MAP.md — a what-exists-where inventory of the repository.

Why this exists
---------------
On 20 August 2026 a session asserted that CSL had no balance-sheet data, having
grepped the curated ``data/financials/csl.yaml`` summary and never noticed the raw
six-year EODHD export sitting in the same directory, nor the statutory accounts in
``data/financials/historical/csl/``. The same session then said DNL had only one
balance sheet, which was also wrong once the archive was found. Both errors came from
reading a *summary* and inferring the absence of a *source*.

A prose instruction to "look around first" does not fix that — the point of the
failure is that you do not know what you have not looked at. A generated map does:
it is cheap to read, it cannot be out of date if it is regenerated, and it makes
absence explicit rather than assumed.

Run from the repo root::

    python scripts/repo_inventory.py

Writes ``REPO_MAP.md``. Regenerate at the START of a session, not the end.
"""

from __future__ import annotations

import datetime as _dt
import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Directories whose contents are noise for orientation purposes.
SKIP_DIRS = {".git", "__pycache__", ".pytest_cache", "node_modules", ".venv", "venv"}

COMPANIES = ("dnl", "wbc", "csl")


def _human(n: int) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024 or unit == "GB":
            return f"{n:.0f}{unit}" if unit == "B" else f"{n/1:.0f}{unit}" if False else f"{n:.1f}{unit}"
        n /= 1024.0
    return f"{n:.1f}GB"


def _size(p: Path) -> str:
    try:
        return _human(p.stat().st_size)
    except OSError:
        return "?"


def _git(*args: str) -> str:
    try:
        return subprocess.run(
            ["git", *args], cwd=ROOT, capture_output=True, text=True, timeout=30
        ).stdout.strip()
    except Exception:
        return ""


def _tracked() -> set[str]:
    out = _git("ls-files")
    return set(out.splitlines()) if out else set()


def _tree(rel: str, max_depth: int = 2, show_files: bool = True) -> list[str]:
    """Indented listing of a subtree, files with sizes."""
    base = ROOT / rel
    if not base.exists():
        return [f"  _(missing: `{rel}`)_"]
    lines: list[str] = []
    for dirpath, dirnames, filenames in os.walk(base):
        dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS)
        d = Path(dirpath)
        depth = len(d.relative_to(base).parts)
        if depth > max_depth:
            dirnames[:] = []
            continue
        indent = "  " * depth
        if depth:
            lines.append(f"{indent}- **{d.name}/**")
        if show_files:
            for f in sorted(filenames):
                if f.startswith("."):
                    continue
                lines.append(f"{indent}  - `{f}` ({_size(d / f)})")
    return lines


def _company_sources(cid: str) -> list[str]:
    """Every source of truth for one company, and what is absent."""
    rows: list[str] = []
    checks = [
        (f"data/companies/{cid}.yaml", "company position + layer-2 method (judgement)"),
        (f"data/companies/{cid}.md", "company narrative"),
        (f"data/companies/{cid}_documents.yaml", "document register"),
        (f"data/financials/{cid}.yaml", "curated layer-1 financials (a SUMMARY — check for raw sources too)"),
    ]
    for rel, what in checks:
        p = ROOT / rel
        mark = "yes" if p.exists() else "**NO**"
        size = f" ({_size(p)})" if p.exists() else ""
        rows.append(f"| `{rel}` | {mark}{size} | {what} |")

    raw = sorted((ROOT / "data" / "financials").glob(f"{cid}_*.csv"))
    rows.append(
        f"| `data/financials/{cid}_*.csv` | "
        + (f"**{len(raw)} file(s)**" if raw else "**NO**")
        + " | RAW feed export — multi-year statements live here, not in the yaml |"
    )

    hist = ROOT / "data" / "financials" / "historical" / cid
    n = len(list(hist.glob("*"))) if hist.exists() else 0
    rows.append(
        f"| `data/financials/historical/{cid}/` | "
        + (f"**{n} document(s)**" if n else "**NO**")
        + " | primary source PDFs (annual reports, statutory accounts, presentations) |"
    )

    an = ROOT / "analyses" / cid
    if an.exists():
        sub = sorted(p.name for p in an.iterdir() if p.is_dir())
        files = len(list(an.rglob("*.xlsx")))
        rows.append(
            f"| `analyses/{cid}/` | yes | {files} workbook(s); subdirs: {', '.join(sub) or 'none'} |"
        )
    else:
        rows.append(f"| `analyses/{cid}/` | **NO** | — |")
    return rows


def build() -> str:
    now = _dt.date.today().isoformat()
    head = _git("log", "-1", "--format=%h %s")
    branch = _git("rev-parse", "--abbrev-ref", "HEAD")
    ahead = _git("log", "--oneline", "origin/main..HEAD")
    n_ahead = len(ahead.splitlines()) if ahead else 0
    untracked = [
        l[3:] for l in _git("status", "--short").splitlines() if l.startswith("??")
    ]
    tracked = _tracked()

    out: list[str] = []
    A = out.append

    A("# REPO_MAP — what exists, and where")
    A("")
    A(f"_Generated {now} by `scripts/repo_inventory.py`. **Regenerate at the start of")
    A("a session, before reasoning about what data exists.** Do not hand-edit._")
    A("")
    A(f"- HEAD: `{head}` on `{branch}`")
    A(f"- Unpushed commits: **{n_ahead}**")
    A(f"- Tracked files: {len(tracked)}")
    A(f"- Untracked files: {len(untracked)}")
    A("")
    A("> **The rule this file exists to enforce:** a curated `*.yaml` in `data/` is a")
    A("> SUMMARY, not the source. Before concluding that data does not exist, check the")
    A("> raw feed exports in `data/financials/*.csv` and the primary documents in")
    A("> `data/financials/historical/<company>/`. Absence in the yaml is not absence.")
    A("")

    A("## Per-company sources")
    for cid in COMPANIES:
        A("")
        A(f"### {cid.upper()}")
        A("")
        A("| Path | Present | What it is |")
        A("|---|---|---|")
        out.extend(_company_sources(cid))

    A("")
    A("## Data directory")
    A("")
    out.extend(_tree("data", max_depth=2))

    A("")
    A("## Design and methodology")
    A("")
    out.extend(_tree("design", max_depth=2))

    A("")
    A("## Source code")
    A("")
    out.extend(_tree("src", max_depth=3))

    A("")
    A("## Tests")
    A("")
    out.extend(_tree("tests", max_depth=2))

    A("")
    A("## UI generator")
    A("")
    out.extend(_tree("ui_prototypes", max_depth=2))

    A("")
    A("## Analyses (workbooks)")
    A("")
    out.extend(_tree("analyses", max_depth=2))

    if untracked:
        A("")
        A("## Untracked files")
        A("")
        A("Not in git. Either commit them or clear them — an untracked file is invisible")
        A("to anyone who clones the repo, and is the most common way work gets lost.")
        A("")
        for u in sorted(untracked):
            A(f"- `{u}`")

    A("")
    return "\n".join(out) + "\n"


if __name__ == "__main__":
    text = build()
    (ROOT / "REPO_MAP.md").write_text(text, encoding="utf-8")
    print(f"REPO_MAP.md written ({len(text.splitlines())} lines)")
