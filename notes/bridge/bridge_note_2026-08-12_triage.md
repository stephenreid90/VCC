VCC — TRIAGE THE FULL-PROJECT REVIEW (select Opus — deliberately a DIFFERENT model from the reviewer,
Claude Fable 5, for an independent second opinion). A full-project review of VCC Valuations has been
produced; your job is to critically VALIDATE and TRIAGE its findings against the actual codebase, then
produce a prioritised action plan. Do NOT implement any fix until Stephen approves the plan.

THE FINDINGS: Stephen will paste Fable's review below (or it is saved at
design/reviews/full_project_review_2026-08-12_fable.md). If pasted, save it there first, then work from it.

SETUP: `git fetch` (HEAD 92bbd2c or later, all pushed). `pip install pytest pydantic pyyaml scipy numpy
--break-system-packages`; `python3 -m pytest -q` (expect 122). Ratchet: `python3 -m pytest
tests/test_ssot_lint.py -q` (8).

READ ORDER: CLAUDE.md → WORKING_NOTES.md (top) → the Fable findings → then verify each finding against
the relevant source: engines in src/vcc_valuations/dcf/ (fcf_engine / bank_engine / segment_engine),
translator.py, data/{companies,financials,scenarios,industries}, tests/, design/architecture.md, the
audited workbooks in analyses/{dnl,wbc,csl}/valuations/, and the UI in ui_prototypes/*_scenario_interface.html
(rebuild with build_cfgs.py && gen_ui.py).

FOR EACH FINDING in the review:
1. Reproduce / verify it against the code (cite file:line). Is it real, correct, and material — or
   overstated, wrong, or already handled? Do not take a claim on trust: if a finding says a number is
   wrong, re-derive it against the audited workbook (LibreOffice recalc) before agreeing; if it claims a
   test is circular, read the test.
2. Classify: CONFIRMED must-fix (correctness / methodology bug) | CONFIRMED nice-to-have | DISPUTED
   (explain why you disagree) | NEEDS-STEPHEN (methodology / judgment) | UI suggestion.
3. For confirmed items: estimate effort + risk, note dependencies and any regression risk to the base
   ties (3.073 / 30.03 / 203.83) or the 122-test suite.

THEN PRODUCE (number everything so Stephen can approve/reject by number):
(a) A prioritised action plan — must-fix correctness first, then methodology, then data/tests/code
    quality, then UI quick-wins — with a recommended execution order and which items to batch.
(b) An explicit list of anything you think Fable got WRONG or overstated, with your reasoning.
(c) Any material issues Fable MISSED.
Assessment + plan first; NO code changes until Stephen confirms.

HOUSE: AU English; number multi-point lists so Stephen can reply by number; ask if anything is unclear
before starting. Working mechanics if you later edit: build_cfgs.py / gen_ui.py SANDBOX-SIDE only (the
Edit tool corrupts them); node --check + base ties after regen; keep domain numbers out of .py prose
(the ratchet is comment-blind); commit sandbox-side (mv .git/index.lock aside on the create-but-not-delete
mount), push via the x-access-token URL then git fetch; sandbox_cleanup.cmd for orphaned files.
