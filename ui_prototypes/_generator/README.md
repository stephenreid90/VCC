# Scenario-interface prototype generator

Self-contained, offline interactive HTML prototypes of the VCC scenario-valuation
interface (for sharing / iteration). One file per company in `ui_prototypes/`.

- `build_cfgs.py` — real-data configs (per company) → `cfgs_gen.json`.
- `resource_cfg.py` — config for every resource-engine company (EVN), engine-run at build time.
- `gen_ui.py` — common HTML/JS scaffold; injects each config → `*_scenario_interface.html`.

Regenerate DNL, WBC, CSL and EVN:
    python3 ui_prototypes/_generator/build_cfgs.py
    python3 ui_prototypes/_generator/gen_ui.py

The CSL file (`csl_scenario_interface.html`) was hand-built before the generator and
is maintained directly. Slider responses are an illustrative approximation, not the
production DCF engine. Calibrated central cases only: CSL MT (USD 141.78 / AUD 214.82),
DNL MT (AUD 3.59), WBC MT (AUD 30.15). DNL/WBC carry all six real scenario values;
CSL's other five are placeholders pending calibration.

## resource_workbook.py (20 Oct 2026)

The formula workbook for resource-engine companies (gap 9): a mine-by-mine depletion run-off on the
Assumptions-sheet discipline, one run-off sheet per scenario, embedded in the page by `build_cfgs.py`.
Ties to the engine through a LibreOffice recalculation (`tests/dcf/golden/_recalc_generated_workbooks.py`,
`tests/dcf/test_evn_workbook_tie.py`). Run it directly to write `_<cid>_full.xlsx` (gitignored).
