VCC VALUATIONS — bridge note, session ending 21 August 2026.

FIRST, BEFORE ANYTHING ELSE: run `python scripts/repo_inventory.py` and read the
REPO_MAP.md it writes. Then read CLAUDE.md — note the new "Survey before you
conclude" directive — then the HANDOVER block at the top of WORKING_NOTES.md, then
open design/reviews/review_tracker_2026-08-13.html (the HTML, not the markdown).

Do NOT assert that data, a document, a protocol or a prior decision does not exist
until you have surveyed the directory that would hold it. Last session burned two
round trips on exactly that: it declared CSL had no balance-sheet data while a
six-year EODHD export sat in the same directory it had grepped, and proposed a
cost-of-debt method from scratch when data/companies/dnl.yaml:549 already implements
the house protocol. Curated *.yaml files in data/ are SUMMARIES. Raw multi-year
statements live in data/financials/*.csv and data/financials/historical/<company>/.

STATE: suite 146, ratchet 8, node --check clean, bases 3.073 / 30.03 / 203.83.
SEVEN COMMITS ARE UNPUSHED (675d931 through 35ea0d4). The sandbox has no GitHub
credentials — Stephen pushes from his own cmd window. Confirm this is done before
starting new work.

SETUP: pip install pytest pydantic pyyaml scipy numpy openpyxl pdfplumber
--break-system-packages; python3 -m pytest -q (expect 146);
python3 -m pytest tests/test_ssot_lint.py -q (expect 8). Rebuild the UI sandbox-side
with cd ui_prototypes/_generator && python3 build_cfgs.py && python3 gen_ui.py.

WHAT SHIPPED LAST SESSION: Batch 1 (18 scenario goldens pinned; terminal-share
warning ported to all three engines). Batch 2 (six UI credibility fixes — the CSL
page was opening on the broker bar and showing 136.00 as its headline). A 54-item
review tracker. Four methodology papers in design/methodology/. The DNL source
archive filed to data/financials/historical/dnl/.

DECISIONS ALREADY MADE — DO NOT REOPEN THEM:
1. CSL discount rate: build a WACC on a TARGET capital structure, not spot D/V.
2. DNL reinvestment: fix working capital AND terminal capex; rebuild the workbook.
3. Market prices stay at 15 June 2026 until Ben's feed returns.
4. DNL broker bar: leave alone until real consensus coverage exists.
5. Working capital: the BROAD definition — (current assets − cash) − (current
   liabilities − interest-bearing debt) — not trade-only. The DNL FY25 accounts
   proved it: receivables are defined three different ways across three documents
   (719.6 statutory / 840.5 in the feed / 488.0 in management's table) while the
   totals agree everywhere.

THE NEXT PIECE OF WORK is implementing the working-capital standard specified in
design/methodology/working_capital_treatment.md. It is fully written and entirely
uncoded. Five enforcement steps; step 3 — a working_capital_intensity_from_data()
function in the translator, so the intensity is derived and never hand-typed — is
the load-bearing one. Carve-outs that must be honoured: all interest-bearing items
INCLUDING CURRENT LEASE PORTIONS (otherwise leases are counted twice against the
Approach A equity bridge), assets and liabilities held for sale, and all cash. Banks
are exempt BY RULE, never by returning zero.

Derived intensities awaiting Stephen's final sign-off: CSL ~35% (six years of data,
range 27.6–46.6%, clean post-Vifor years 34.8% and 36.8%) against an assumed 10%,
worth −4.2% on CSL. DNL 13.76% on the broad measure against an assumed zero.

Also awaiting sign-off: the CSL WACC parameters — notional BBB+/A−, ~100bp spread
calibrated off DNL's own 170bp AUD BBB anchor, kd 5.50%; target 1.8× net debt/EBITDA
converted at a through-cycle 14× EV/EBITDA giving D/V 12.9%, WACC ≈8.2%, CSL MT
≈ AUD 228 (+12%). The EV/EBITDA multiple is the only input with no independent
support.

IMPORTANT: both changes retire an audited Muddle Through oracle and move all 18
pinned goldens. Each needs a workbook rebuild and re-tie, not just an engine edit.
Do not let the engine become self-certifying. Half a day for DNL, a day for CSL.

HOUSE RULES: Australian English. Number any list of 2+ points so Stephen can reply
by number. Ask via AskUserQuestion if a brief is unclear rather than guessing. Render
anything Stephen needs to copy in a widget with a copy button, not a blockquote.
Read design/writing_style.md before drafting prose meant for readers.

EDIT MECHANICS: build_cfgs.py and gen_ui.py are edited and run SANDBOX-SIDE; run
node --check and confirm the base ties after any regeneration. Keep domain numbers
out of .py prose — the SSOT ratchet is comment-blind and will fail on a number
written in a comment (this caught me once last session). Commit sandbox-side;
the .git/*.lock create-but-not-delete quirk needs `mv .git/index.lock
.git/index.lock.deadN` and a retry. Tell Stephen to run sandbox_cleanup.cmd at the
end of any session that commits.

TWO THINGS WORTH RETRIEVING: the DNL 1H26 Appendix 4D half-year financial report
(would give total current assets/liabilities at 31 March 2026, the model's own anchor
date), and data/companies/csl.md, which does not exist although DNL and WBC both have
company narratives.
