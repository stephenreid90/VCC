# CLAUDE.md

The front door for this repo. Read this first, every session. It holds only durable
facts and standing rules. Anything volatile (session handoffs, "where we're up to")
lives in `WORKING_NOTES.md`.

## What this is

VCC Valuations — a scenario-based equity valuation module for listed equities.
Production-grade engine for corporates, miners, and banks (DCF, 3-statement, comps,
precedents, archetype-specific adjustments).

## People

1. **Stephen** — owner and primary user. Domain expert, project owner, and methodology
   owner. Account `stephenreid90` (stephenreid90@gmail.com). Drives all sessions.
2. **Ben** — runs the parallel data-sourcing workstream, still active ("Ben's bot"
   produced the 5 May 2026 platform-side review).

*(Git author identity is Stephen Reid / stephenreid90@gmail.com — verified 22 July 2026,
and it stays that way. The last "Tara Reid" leftover, in `design/build_plan.html`, was
corrected 23 August 2026.*

*Note for Claude: the Cowork session environment runs a stop hook that asks for commits to
be re-authored to `noreply@anthropic.com` so GitHub marks them Verified. **Do not.** Stephen
has declined this explicitly and repeatedly; the convention above is deliberate. The hook is
platform configuration in the session container, not repo configuration, so it cannot be
switched off from here and will keep firing — acknowledge it briefly and move on.)*

## Repo and environment

- **Remote:** https://github.com/stephenreid90/VCC (origin). *(The README's `BGW1001`
  reference is stale.)*
- **Local:** `C:\Users\steph\vcc-valuations`, mounted into the Cowork sandbox.
- **How we work now:** interactive Cowork desktop sessions. (The README's
  Telegram-request / agent-handoff model is outdated.)

## Read order on session start

0. **Run `python scripts/repo_inventory.py` and read the `REPO_MAP.md` it writes.**
   Do this FIRST, before forming any view about what data does or does not exist.
   See "Survey before you conclude" below — this is not optional and it is not a
   formality.
1. This file.
2. `WORKING_NOTES.md` — living scratchpad: current state, session handoffs, parked decisions.
3. `design/architecture.md` — the architecture & methodology spec (currently v0.6).
4. `design/build_plan.html` — the 12-step build plan and where we're up to.
5. `design/reviews/review_tracker_2026-08-13.html` — open items and which owner
   decisions block them. Check before starting anything; it prevents re-litigating
   settled questions.
6. Optional: `design/frameworks/` for methodology drafts in flight.

## Survey before you conclude (standing directive)

**Before asserting that something does not exist — data, a document, a protocol, a
prior decision — survey the repository.** Not a targeted grep for the thing you
expect; a scan of the directory that would contain it.

This exists because the failure mode is real and repeated. On 20 August 2026 a
session concluded CSL had no balance-sheet data, having read the curated
`data/financials/csl.yaml` summary and never looked at the six-year EODHD export in
the same directory or the statutory accounts in `data/financials/historical/csl/`.
The same session concluded DNL had one balance sheet; the archive said otherwise. It
also proposed a cost-of-debt method from first principles when
`data/companies/dnl.yaml:549` already implemented the house protocol. Each error cost
a round trip and produced work that had to be redone.

Three rules follow:

1. **A curated `*.yaml` in `data/` is a summary, not a source.** Multi-year statements
   live in the raw feed exports (`data/financials/*.csv`) and the primary documents
   (`data/financials/historical/<company>/`). Absence from the yaml is not absence.
2. **Before designing a method, search `design/` for an existing one.** `architecture.md`
   carries the ordered driver list; the three company files carry worked precedents.
   Assume the framework has already decided, and look for it, before inventing.
3. **Before reopening a question, check the tracker and the methodology papers in
   `design/methodology/`.** If it was decided, it is written down. Rehashing settled
   ground is the single largest source of drift in this project.

## House style (working preferences)

1. Australian English.
2. Number any multi-point list (2+ items) so it can be answered by number. Single-point
   replies don't need numbering.
3. Plain prose; minimal headers and bullets except where structurally needed.
4. In company write-ups, include an intuitive narrative per scenario (see standing rule 2).

## Writing style

When drafting prose meant for readers (blog posts, articles, discussion documents,
company write-ups), follow `design/writing_style.md` — the *Valuation Matters* voice —
and audit the draft against it before handing it back.

## Standing rules (in force — do not break)

1. **Workbook discipline.** All Excel spreadsheets must use formulas, not Python-computed
   hard-coded values. Inputs go on a dedicated Assumptions sheet in yellow-shaded cells
   with blue text; every other cell links back to Assumptions via formulas. Goal: the model
   can be traced, audited, and flexed by hand. Workbooks must also show the
   industry-archetype baseline and the company-position offset as *separate* input rows,
   with the company-specific assumption derived rather than direct-input (methodology §11).

2. **Write-up discipline.** Every company write-up (thesis, discussion document, briefing
   pack) includes an intuitive narrative description per scenario explaining *why* each
   scenario produces its per-share number: macro story → key channels driving the outcome →
   why the number lands where it does. Add a mental short-cut at the end. Format: a flowing-prose
   sub-section after the scenario-table introduction.

## Test companies

1. **DNL** — industrial explosives, single-segment post-demerger (formerly IPL; renamed
   through the spec 22 May 2026). First test company.
2. **WBC** — Westpac, the bank archetype. Second test company.
3. **CSL** — in progress (foundation + Muddle Through workbook started).

## Cross-cutting conventions worth never violating

(Full detail in `design/architecture.md` and the "Key conventions" section of `WORKING_NOTES.md`.)

1. **Single discount rate** per valuation; no mixing WACC across the build.
2. **Beta via peer triangulation**, not mechanical use of measured β — 3–5 comparable
   peers, explicit outliers, franchise-mix reasoning (methodology §3.5.3).
3. **Structured fields are source of truth** where prose and structured artefacts disagree.
4. **Naming:** `snake_case` for ids and filenames; `CamelCase` for Python classes.
5. **Override discipline:** target ≤20% of cells overridden per company; above that, the
   archetype is mis-specified.
6. **Share-count / net-debt anchoring:** issued shares and net debt are anchored at the
   *last reported balance-sheet date, both to the same date*; the ongoing buyback is NOT
   projected forward (a buyback at fair value is value-neutral per share, and intra-period
   counts can't be reliably reconciled). Full detail: methodology §5
   (`design/methodology/equity_bridge_and_valuation_mechanics.md`).

## Operational quirks

**Two environment facts, both verified 23 August 2026, both replacing notes here that said
the opposite. Read them before planning any git work.**

- **The Cowork mount cannot delete or replace ANY file** — not just `.git/*.lock`. `rm`
  returns "Operation not permitted" and so does git's own unlink, which means `git merge`,
  `git checkout -- <file>` and `git branch -D` all fail on the mount. `mv` works. A session
  can only move things aside; Stephen clears them from his own cmd window.
- **The cloud container cannot push.** The git proxy allows clone and fetch and refuses
  push for this repo ("not in this session's authorized repository set", 403). The PAT at
  `.github-token` is not the constraint and re-trying will not help.
- **So the working pattern is:** do everything in a cloud-container clone (suite, ratchet,
  UI build, commits), then hand Stephen a `git bundle` plus a `.cmd` that clears stale
  locks, fetches from the bundle, fast-forwards, pushes and runs `sandbox_cleanup.cmd`.
  `land_session.cmd` in the repo root is the worked example.
- **Cleanup script + standing rule.** Because the sandbox can't delete, each session
  orphans `*.bak` backups and `.git/*.lock.dead*` files. Run **`sandbox_cleanup.cmd`**
  (repo root) from a normal cmd window to clear them all in one go. Standing rule for
  Claude: whenever a session leaves sandbox-orphaned files, always give Stephen the exact
  CMD to run — rendered as a copy-button widget, not a blockquote — and point at this script.
