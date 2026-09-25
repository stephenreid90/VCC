#!/usr/bin/env python3
"""Session-start check: regenerate the maps, run the gates, print the state.

Four things used to be remembered separately at the start of every session and were
not always all done. This does them in one command and prints a single verdict block.

    python scripts/session_start.py            # full
    python scripts/session_start.py --fast     # skip the test suite

What it does:
  1. Regenerates REPO_MAP.md (what data exists — read it before concluding anything).
  2. Regenerates OPEN_ITEMS.html from design/open_items.json.
  3. Runs the test suite and the SSOT ratchet.
  4. Prints git state, unpushed commits, untracked files and the base ties.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_BASES = {"DNL": "1.846", "WBC": "30.03", "CSL": "195.78"}  # DNL 25 Sep (D-35/D-36/D-69/D-70 + D-49 roll-forward fix); WBC back to 30.03 on 17 Sep (M13)


def run(cmd: list[str], timeout: int = 900, cwd: Path | None = None) -> tuple[int, str]:
    try:
        # encoding/errors are explicit: text=True decodes with the platform
        # default codec, which mangles em dashes and arrows on Windows and made
        # the 14 Sep log unreadable in places.
        p = subprocess.run(
            cmd, cwd=cwd or ROOT, capture_output=True, text=True, timeout=timeout,
            encoding="utf-8", errors="replace",
        )
        return p.returncode, (p.stdout + p.stderr).strip()
    except Exception as exc:  # pragma: no cover
        return 1, str(exc)


def git(*args: str) -> str:
    return run(["git", *args], timeout=60)[1]


def section(title: str) -> None:
    print(f"\n\033[1m{title}\033[0m" if sys.stdout.isatty() else f"\n== {title} ==")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--fast", action="store_true", help="skip the test suite")
    args = ap.parse_args()
    problems: list[str] = []

    section("1. Regenerating maps")
    for script, out in (
        ("scripts/repo_inventory.py", "REPO_MAP.md"),
        ("scripts/build_open_items.py", "OPEN_ITEMS.html"),
    ):
        rc, msg = run([sys.executable, script], timeout=180)
        print(f"   {'ok ' if rc == 0 else 'FAIL'} {out}  {msg.splitlines()[-1] if msg else ''}")
        if rc:
            problems.append(f"{script} failed")

    section("2. Gates")
    if args.fast:
        print("   skipped (--fast)")
    else:
        rc, out = run([sys.executable, "-m", "pytest", "-q"])
        tail = out.strip().splitlines()[-1] if out else ""
        print(f"   {'ok ' if rc == 0 else 'FAIL'} suite      {tail}")
        if rc:
            problems.append("test suite failing")
        rc, out = run([sys.executable, "-m", "pytest", "tests/test_ssot_lint.py", "-q"])
        tail = out.strip().splitlines()[-1] if out else ""
        print(f"   {'ok ' if rc == 0 else 'FAIL'} ssot lint  {tail}")
        if rc:
            problems.append("SSOT ratchet failing")

    section("3. Base ties")
    # cfgs_gen.json is gitignored and nothing else regenerates it, so reading it
    # without rebuilding compares the ratified levels against whatever was last
    # built on this machine. On 14 Sep 2026 that reported two stale failures and
    # hid a syntax error in build_cfgs.py that meant no rebuild had happened at
    # all. Strike the tie on current code or do not strike it.
    gen = ROOT / "ui_prototypes" / "_generator"
    rc, msg = run([sys.executable, "build_cfgs.py"], timeout=600, cwd=gen)
    print(f"   {'ok ' if rc == 0 else 'FAIL'} rebuild    {msg.splitlines()[-1] if msg else ''}")
    if rc:
        problems.append("build_cfgs.py failed — base ties below are stale or absent")
    cfg = gen / "cfgs_gen.json"
    if rc:
        # A config the rebuild could not write is worse than no config: reading
        # it compares the ratified levels against a half-written or stale file.
        print("   -   skipping the ties: the rebuild above failed, so any config on")
        print("       disk is stale or partial. Fix the rebuild first.")
    elif cfg.exists():
        import json

        d = json.loads(cfg.read_text(encoding="utf-8"))
        for k, want in EXPECTED_BASES.items():
            got = d.get(k.lower(), {}).get("cp", {}).get("base")
            ok = str(got) == want
            print(f"   {'ok ' if ok else 'FAIL'} {k}  {got}  (expect {want})")
            if not ok:
                problems.append(f"{k} base tie moved: {got} != {want}")
    else:
        print("   -   cfgs_gen.json still absent after the rebuild above.")
        problems.append("cfgs_gen.json absent — base ties not checked")

    section("4. Git state")
    # refresh the remote ref first, or "unpushed" reports a stale count
    run(["git", "fetch", "--quiet", "origin"], timeout=90)
    print(f"   HEAD      {git('log', '-1', '--format=%h %s')[:96]}")
    print(f"   branch    {git('rev-parse', '--abbrev-ref', 'HEAD')}")
    ahead = git("log", "--oneline", "origin/main..HEAD")
    n = len(ahead.splitlines()) if ahead else 0
    print(f"   unpushed  {n}")
    if n:
        problems.append(f"{n} unpushed commit(s)")
    untracked = [l[3:] for l in git("status", "--short").splitlines() if l.startswith("??")]
    print(f"   untracked {len(untracked)}")
    for u in untracked[:8]:
        print(f"             {u}")
    if untracked:
        problems.append(f"{len(untracked)} untracked file(s) — invisible to a clone")

    section("5. Read next")
    print("   REPO_MAP.md        what data actually exists (read BEFORE concluding it doesn't)")
    print("   CLAUDE.md          durable rules + 'Survey before you conclude'")
    print("   DECISIONS.md       ratified decisions — check before proposing a method")
    print("   WORKING_NOTES.md   handover block at the top")
    print("   OPEN_ITEMS.html    what's open and which questions block it")

    section("Verdict")
    if problems:
        for p in problems:
            print(f"   ! {p}")
        return 1
    print("   clean")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
