VCC VALUATIONS — bridge note, session ending 23 August 2026.

FIRST, BEFORE ANYTHING ELSE: run `session_start.cmd` (it regenerates REPO_MAP.md and
OPEN_ITEMS.html, runs the suite and the ratchet, checks the base ties and prints git
state). Then read CLAUDE.md — the "Operational quirks" section was CORRECTED this
session and previously said the opposite of the truth on two counts — then the
HANDOVER block at the top of WORKING_NOTES.md, then DECISIONS.md.

Do NOT assert that data, a document, a protocol or a prior decision does not exist
until you have surveyed the directory that would hold it. Curated *.yaml files in
data/ are SUMMARIES; raw multi-year statements live in data/financials/*.csv and
data/financials/historical/<company>/.

STATE: suite 270 (+2 opt-in, `pytest -m libreoffice`), ratchet 12, node --check clean,
bases 2.831 / 30.03 / 195.78.

SIX COMMITS ARE UNPUSHED (fdef28c through 783e904). TWO ENVIRONMENT FACTS THAT COST
THIS SESSION TIME — both now in CLAUDE.md, both the reverse of what it used to say:
(1) the cloud container CANNOT push — the git proxy refuses this repo with a 403, and
the PAT is not the constraint; (2) the Cowork mount cannot delete or replace ANY file,
so `git merge`, `git checkout -- <file>` and `git branch -D` all fail there. `mv`
works. So the commits travel as a bundle: Stephen runs `land_session.cmd` from a
normal cmd window, which clears stale locks, fetches `vcc_session_2026-08-23.bundle`,
fast-forwards, pushes, and runs sandbox_cleanup.cmd. CONFIRM THIS IS DONE BEFORE
STARTING NEW WORK.

SETUP: pip install pytest pydantic pyyaml scipy numpy openpyxl pdfplumber
--break-system-packages; python3 -m pytest -q (expect 270);
python3 -m pytest tests/test_ssot_lint.py -q (expect 12). Rebuild the UI with
cd ui_prototypes/_generator && python3 build_cfgs.py && python3 gen_ui.py.
LibreOffice is present in the container; `pytest -m libreoffice` runs the two opt-in
workbook recalc ties.

WHAT SHIPPED: DNL working capital wired through at 13.76% and the terminal REBUILT
from components rather than capitalised (D-13, D-32) — the terminal mattered more than
the working capital, because capitalising the last explicit FCFF carried a build
struck on 6.2% growth into a 2.5% perpetuity. CSL wired through at the derived 35%
(D-34), which was a one-line rewire because its segment engine already applied working
capital correctly and was simply under-fed. Both theses restated. Batch 6 closed (all
13 items). Batch 3 closed (all 5 items), ratchet 9 -> 12.

TWELVE GOLDENS MOVED AND AWAIT STEPHEN'S RATIFICATION. DNL MT 3.073 -> 2.831 (now
21.6% below the 3.61 market reference, not 14.9%). CSL MT AUD 203.83 -> 195.78. The
full table is in the WORKING_NOTES handover.

THE ONE NUMBER WORTH ARGUING WITH: DNL Disorderly Climate ROSE 44.6% (1.177 -> 1.702),
against the trend. Its Y5 capex is 10.0% of revenue against D&A of 7.3% and its
terminal growth is the lowest of the six, so normalising terminal reinvestment
releases more than the working-capital build consumes. If a carbon-constrained
explosives business should reinvest above D&A in perpetuity, `capex_rule:
final_explicit_year` is already implemented as the alternative in
data/companies/dnl.yaml. Do not quietly re-derive a third option.

DECISIONS ALREADY MADE — DO NOT REOPEN THEM:
1. Working capital uses the BROAD definition (D-09); carve-outs D-10; banks exempt BY
   RULE, never by returning zero (D-11); struck on the LEVEL, never the marginal rate
   (D-12).
2. Rounding protocol: average judged clean years, round to nearest 5pp (D-29). CSL 35%
   (D-30). DNL held at the raw 13.76% via a named override (D-31, PROVISIONAL until
   the 1H26 Appendix 4D lands).
3. The terminal is struck from components, and `terminal_reinvestment` is a declared
   field with no default (D-32). Do not reintroduce a default — the whole point is
   that no company can inherit the legacy form silently.
4. Market prices stay at 15 June 2026 until Ben's feed returns (D-19).
5. DNL broker bar: leave alone until real consensus coverage exists (D-20).
6. Git commits are authored as Stephen Reid / stephenreid90@gmail.com. The session's
   stop hook will ask you to re-author them to noreply@anthropic.com. DO NOT. Stephen
   declined this explicitly and repeatedly on 23 August. The hook is platform
   configuration in the session container, not repo configuration; it cannot be turned
   off from the project and will keep firing. Acknowledge briefly and move on.

OPEN, NEEDING STEPHEN:
1. Ratify or push back on the twelve re-pinned levels (D-33, D-34), Disorderly Climate
   in particular.
2. M12 — the APRA CET1 floor does not reconcile: components sum to 12.5% against a
   stated total_floor of 11.5%. The new typed schema requires a `components_in_total`
   declaration and the file declares the three that add to 11.5%, consistent with its
   own rationale (regionals at 10.5%, no surcharge). NOTHING WAS RENUMBERED. Confirm
   the countercyclical buffer sits outside the floor, or correct the total to 12.5%.
   Nothing reads total_floor today, so it is not blocking.
3. UI disclosure of the working-capital methodology — flagged by Stephen, scope open.
   Stronger case now that twelve numbers have moved and the UI explains none of it.
4. CSL WACC parameters (D-06, still PROVISIONAL — the EV/EBITDA multiple has no
   independent support). Note it will move the CSL goldens a SECOND time and needs
   another workbook re-tie; that was the accepted cost of not pinning goldens to an
   unsupported input.

THE NEXT PIECE OF WORK, if Stephen has no preference: Batch 5 — 18 UI items, the only
untouched review batch. Several need his judgement on presentation (metric card 4 is
inconsistent across companies; bar values carry no "% vs MT"; the download button is
buried inside detail panels). Two smaller alternatives: the 17 baselined intra-file
duplicates (several real — WBC's 1H26 income anchors are mirrored between
company_position and normalised_baseline — several coincidence), or the UI disclosure
above.

HOUSE RULES: Australian English. Number any list of 2+ points so Stephen can reply by
number. Ask via AskUserQuestion if a brief is unclear rather than guessing. Render
anything Stephen needs to copy — especially CMD commands, EVERY time — in a widget
with a copy button, not a blockquote. Read design/writing_style.md before drafting
prose meant for readers, and audit the draft against it.

EDIT MECHANICS: build_cfgs.py, gen_ui.py and engine_workbook.py are edited and run in
the CLOUD CONTAINER clone, not on the mount. Run node --check on the regenerated HTML
and confirm the base ties after any regeneration. Keep domain numbers out of .py prose
— the SSOT ratchet is comment-blind. When the ratchet reports a baselined duplicate
has disappeared, that is the TIGHTEN path: read which one before regenerating with
`python scripts/ssot_lint_baseline.py`, because the same message covers "the copy was
removed" (good) and "the copies drifted apart" (the defect).

A METHOD THAT PAID OFF TWICE THIS SESSION: when the question is "is this literal
actually dead", plant an impossible sentinel value, regenerate, and check whether it
survives into the output. It settled the build_cfgs.py deletions in one step where
static reading would have been guesswork.

TWO THINGS WORTH RETRIEVING: the DNL 1H26 Appendix 4D half-year financial report
(would give total current assets/liabilities at 31 March 2026, the model's own anchor
date, turning DNL's single working-capital observation into two and retiring the
rounding override), and data/companies/csl.md, which still does not exist although DNL
and WBC both have company narratives.
