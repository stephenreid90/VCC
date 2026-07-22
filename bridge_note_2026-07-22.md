Continuing VCC. Read `CLAUDE.md`, then `WORKING_NOTES.md` — start with the "22 July 2026 (M1 engine · re-anchor decisions · IronCorp note)" block at the top.

Where we are. The real per-year DCF engine (M1) is built and green: a single-segment industrial FCFF engine (`src/vcc_valuations/dcf/fcf_engine.py`) that reproduces the audited DNL Muddle Through workbook to the cent — EV 7,736.6 → 3.484 a share — with a reproducible golden-master oracle (`tests/dcf/golden/_recalc.py` regenerates it from the workbook via headless LibreOffice), 20 assertions passing, full suite 63 passed. `WaccBuild` moved to a new `src/vcc_valuations/assumptions/` package. Nothing committed — commit from my terminal (delete `.git/index.lock` first if present).

Decisions made. The workbook is the single source of truth; the generator and `dnl.yaml` derive from it. The revenue basis is locked at the workbook's FY26 3,400 continuing-ops figure — the ~3,905 TTM re-base is reverted, because TTM includes Phosphate Hill (being divested) and the workbook build excludes it. The ~500 gap is that business, and keeping its revenue while the bridge also takes its sale proceeds double-counts it.

Pick this up first. The generator re-anchor was deliberately NOT executed, because EV depends on WACC, which depends on an open methodology fork: β 0.95 (workbook, world-index Hamada) vs β 1.10 (`dnl.yaml` and the β-workbench, peer-cluster triangulation). Both are documented and built into artefacts. Share count 1,770 (workbook) vs 1,884 rides along with it. Decide β and the share count, then re-anchor the generator and `dnl.yaml` in one consistent, engine-driven pass. Don't hand-patch — the generator carries a whole older parameter set (margin 13.5% vs 14.1%, netDebt 1,512, EV 8,064), and the five non-MT scenario values were calibrated on it and can't be re-derived by hand until the scenario engine exists.

Then M2 — wire the driver-keyed `AssumptionSet` → `FcfEngineInputs` (`linkage/` + `assumptions/`). Then M3 (segment FCFF + CSL; the binding-terminal-margin path is stubbed as a seam in `fcf_engine._terminal`).

Generator mechanics unchanged: edit `ui_prototypes/_generator/`, then `python3 build_cfgs.py && python3 gen_ui.py`; verify each CFG parses as JSON, `node --check`, and the headline ties. Prefer sandbox-side python overwrites for large files — the mount desyncs file-tool writes from the bash/python view.

Also open: consensus figures are mock pending Ben's EODHD feed; real EODHD behind the β workbench; the lease data-contract fields; WBC/CSL rich templates.

Track iterations — swap chats around 20.
