# Scenario-interface prototype generator

Self-contained, offline interactive HTML prototypes of the VCC scenario-valuation
interface (for sharing / iteration). One file per company in `ui_prototypes/`.

- `build_cfgs.py` — real-data configs (per company) → `/tmp/cfgs.json`.
- `gen_ui.py` — common HTML/JS scaffold; injects each config → `*_scenario_interface.html`.

Regenerate DNL + WBC:
    python3 ui_prototypes/_generator/build_cfgs.py
    python3 ui_prototypes/_generator/gen_ui.py

The CSL file (`csl_scenario_interface.html`) was hand-built before the generator and
is maintained directly. Slider responses are an illustrative approximation, not the
production DCF engine. Calibrated central cases only: CSL MT (USD 141.78 / AUD 214.82),
DNL MT (AUD 3.59), WBC MT (AUD 30.15). DNL/WBC carry all six real scenario values;
CSL's other five are placeholders pending calibration.
