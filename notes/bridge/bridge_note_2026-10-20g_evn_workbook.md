# Bridge note, 20 October 2026 (late evening): EVN formula workbook built; gap 9 closed

**This is a snapshot. `WORKING_NOTES.md` is the live record and wins where they differ.**

Read first: `CLAUDE.md`, then the top of `WORKING_NOTES.md` (the EVN FORMULA WORKBOOK BUILT block), then
`ui_prototypes/_generator/resource_workbook.py` (the whole module; its docstring lists the sheets).

## Where we are

1. `resource_workbook.py` builds a formula-only mine-by-mine depletion run-off workbook for any company whose
   engine is `resource`; `build_cfgs.py` embeds it in the EVN page for download. Nine sheets, 324 KB.
2. LibreOffice recalculation ties every per-period line and every value to the engine to 1e-6 in all six
   scenarios (`tests/dcf/test_evn_workbook_tie.py`, oracle `tests/dcf/golden/evn_workbook_all_scenarios.json`).
   Regenerate the oracle with `python tests/dcf/golden/_recalc_generated_workbooks.py` after any data change.
3. Six build choices are listed in `WORKING_NOTES.md` and are NOT yet confirmed by Stephen.
4. The suite passes (DCF 489, rest 406).

## Next sitting

1. Stephen's confirmation (or changes) of the six build choices.
2. Then nothing on EVN until D-101's observed betas arrive (Ben). The PDF renames in
   `notes/evn_pdf_rename_plan_2026-10-20.md` are still unapplied.
