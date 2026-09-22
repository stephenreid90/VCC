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

3. **Command discipline — Stephen does not use CMD or git directly.** He is the domain
   expert, not a shell user, and asking him to assemble, adapt or interpret a command is a
   defect in the handover, not a gap on his side. Whenever a session needs something run on
   his machine:
   - Give **one complete, pasteable command** — never a script name to find, never a
     sequence of steps to stitch together, never bare `git` verbs to type.
   - Render it in a **copy-button widget**, never a blockquote or a fenced block he has to
     select by hand.
   - Say in plain words what it will do, what "finished" looks like on screen, and what to
     do if it stops early.
   - **Verify the result yourself over the device bridge afterwards.** Never ask him to
     copy terminal output back; read `git log`, `git status` and the working tree directly.
   The standing landing command is `land_vcc.cmd` (see "Landing a session" below) and it
   never changes. Prefer it to a bespoke one-off script.

4. **Any number that reaches a document must come from committed code.** A harness that
   produced a published figure is a deliverable, not scaffolding: commit it in the same
   change as the document that cites it, and commit the assumption set that drove it
   alongside. A scratch script in a disposable container is not evidence — the container
   is reclaimed, the numbers survive in the document, and nobody can then say what
   produced them.

   This is not a style preference. On 25 August 2026 a methodology paper cited "a scratch
   harness that reproduces `FcfEngine` to 1e-15" without saying where it was, because it
   was nowhere. The next sitting could not reproduce it, rebuilt the harness, and landed a
   table about 2% away with no way to reconcile the difference. Reconciling it afterwards
   cost most of a third sitting.

   Concretely, for the horizon and terminal work: every published table is one entry in
   `design/methodology/horizon_variant_sets.yaml` carrying its complete assumption block
   and the levels it produced; `scripts/size_horizon_variants.py` regenerates it and
   `tests/dcf/test_horizon_variant_sets.py` asserts it. A table in a document cites a set
   name. Exactly one set is `current`; the others name what superseded them. Extend that
   pattern rather than opening a new scratch file.

5. **Plumbing is not the work, and it does not get airtime.** Asked for explicitly on
   16 September 2026, after a sitting in which landings, bundles, stale locks and stop-hook
   noise consumed most of the exchanges: *"can we please forget about git for, say, a
   month. It is consuming half of every chat and destroying my will on this project."* That
   is a fair reading of the record, and the fix is behavioural, not a promise. In force from
   16 September 2026 and to be reviewed 16 October 2026 — a scheduled reminder exists.

   - **Land once per sitting, at the end.** Work accumulates in the container clone. Do not
     land per change, do not ask whether to land now or later, and do not offer the choice.
   - **The landing is one line and nothing else.** No explanation of bundles, mounts, proxies
     or why the container cannot push. He knows. It goes at the *bottom* of a message, after
     the substance.
   - **Absorb stop-hook output silently.** The unpushed-commits hook fires every turn while a
     bundle is pending, which is the normal state of this repo. It is not news, it is not
     actionable, and relaying it three times in one sitting is how this rule came to be
     written. Fix what it flags if it is fixable; otherwise say nothing.
   - **Never report a git diagnostic unless it blocks a number.** A stranded lock, a stale
     remote ref, an untracked file: fix it, record it here or in `WORKING_NOTES.md` if it is
     durable, and move on. The test is whether Stephen has to *decide* something.
   - **Do not run experiments on the workflow mid-task.** Probing whether the mount can
     merge, or whether push works from the shell, belongs in its own deliberate sitting he
     has agreed to, not in the middle of a valuation change.
   - What does NOT change: standing rule 3 still applies to anything he must run, and work
     still has to be landed to survive. The discipline is about *narration and sequencing*,
     not about being careless with the repo.

## Bridge notes and the live layer

A bridge note in `notes/bridge/` is a **travelling snapshot**, written so the first exchange
of a new chat is not spent reconstructing context. It is not the system of record and it does
not update itself: it freezes on the day it is written.

`WORKING_NOTES.md` is the live layer and is maintained. **Where a bridge note and
`WORKING_NOTES.md` disagree, `WORKING_NOTES.md` wins.**

Every bridge note therefore says so at the top, and its reading order names
`WORKING_NOTES.md` explicitly as the authoritative statement of where things are rather than
listing it among other files. A bridge note that reads as self-sufficient invites the next
session to skip the file that is actually current, which is how a superseded number gets
quoted back as live.

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

**Environment facts, verified 23 August 2026 and re-verified 16 September 2026. Read them
before planning any git work.**

- **The Cowork mount cannot delete or replace ANY file** — not just `.git/*.lock`. `rm`
  returns "Operation not permitted" and so does git's own unlink, which means `git merge`,
  `git checkout -- <file>` and `git branch -D` all fail on the mount. `mv` works, and so
  does plain truncate-and-write, which is how a file gets restored after a failed git
  operation. A session can only move things aside; Stephen clears them from his own cmd
  window.
- **This did NOT change when the device shell came back.** `device_bash` was down from the
  Windows update of 8 September until 16 September. Its return makes reads, writes and
  searches on the mount work again, and `git push` from the mount authenticates fine with
  the PAT at `.github-token` — so it is tempting to conclude the bundle dance is over. It
  is not. Re-tested 16 September: `git checkout -- README.md` on the mount fails, strands a
  `.git/index.lock` it cannot unlink, and every subsequent git write in that repo is
  blocked until the lock is cleared from Windows. Pushing without merging would publish the
  work while leaving Stephen's working tree behind origin, which is worse than not pushing.
  **The restriction is on the Cowork mount's view of the folder, not on Stephen's machine**
  — his own cmd window has full access, which is exactly why `land_vcc.cmd` works and a
  session's shell does not. Do not re-run this experiment; if you do it anyway, the stranded
  lock is cleared by step 1 of `land_vcc.cmd`, so the recovery is the landing itself.
- **`device_commit_files` cannot overwrite an existing file on the mount, and says it
  did.** Found 22 September 2026: it reported `session.bundle` written, updated the mtime,
  and left the old bytes in place. This is almost certainly the "vanished bundle" of
  16 September. Write to a NEW filename, then in `device_bash` truncate-and-write it over
  the target (`cat new > target`) and `mv` the new file into `.git/_stale_delete_me/`.
  Always check size or `git bundle list-heads` on the device before fetching.
- **The cloud container cannot push.** The git proxy allows clone and fetch and refuses
  push for this repo ("not in this session's authorized repository set", 403). The PAT at
  `.github-token` is not the constraint and re-trying will not help.
- **So the working pattern is:** do everything in a cloud-container clone (suite, ratchet,
  UI build, commits), then hand Stephen a `git bundle` plus a `.cmd` that clears stale
  locks, fetches from the bundle, fast-forwards, pushes and runs `sandbox_cleanup.cmd`.
  `land_session.cmd` in the repo root is the worked example.
- **Cleanup script.** Because the sandbox can't delete, each session orphans `*.bak`
  backups and `.git/*.lock*` files. `sandbox_cleanup.cmd` (repo root) clears them all,
  recursing into `.git/refs/` — a stale `.git/refs/heads/incoming.lock` silently defeated
  `git branch -D` on 24 August 2026 and blocked a landing. `land_vcc.cmd` calls it, so it
  rarely needs running on its own.

## Landing a session

The cloud container cannot push and the mount cannot delete, so finished work travels as a
`git bundle` and Stephen lands it from his own cmd window. **The command never changes:**

```
C:\Users\steph\vcc-valuations\land_vcc.cmd
```

`land_vcc.cmd` and `session.bundle` are both gitignored, so they never collide with the
merge they are carrying. At session end, write the bundle to `session.bundle` in the repo
root (via `SendUserFile` + `device_commit_files`), refresh `land_vcc.cmd` if it has changed,
and give Stephen that one line in a copy-button widget. The script clears every stale lock
under `.git`, deletes leftover scratch branches, fast-forwards from the bundle, pushes,
removes the bundle and runs `sandbox_cleanup.cmd`. It is safe to re-run.
