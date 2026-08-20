# VCC — bridge note (11 Aug 2026, session end)

**Start:** read `CLAUDE.md`, then `WORKING_NOTES.md` from the top — blocks "11 August 2026 (f)" down through (a) cover this session. Run `git fetch && git status && git log --oneline -8` before trusting state: HEAD should be `6fd4f7f`, all pushed, working tree clean. Tests: `pip install pytest pydantic pyyaml scipy numpy --break-system-packages` then `python3 -m pytest -q` → **76 green**.

**Shipped this session (7 commits):**
1. β free-input in the β-workbench UI (analyst types any triangulated β; peers shown as reference).
2. DNL §5.3 share-count fix — 1,770m @ 2026-03-31, equity 6,390, debt/net-debt 1,260.8; §5.4 validator.
3. WBC layer split — last stored `cost_of_equity` cleared; `KNOWN_STORED_DERIVED` now empty.
4. CSL layer-1 circularity broken — segment scenario-assumptions moved to layer 2; provenance re-cited.
5–7. **M2: discount rate, equity-bridge adjustments (§4.2/§4.3), and per-year overlays (§11) are now DATA-DRIVEN.** DNL Muddle Through re-anchored to the ratified **β 1.10 → 3.073/share** (WACC 8.877%), superseding the β-0.95 workbook 3.484 — which `tests/dcf/test_e2e_dnl_mt.py` retains **only** as the engine-MECHANICS oracle.

**Next milestone — finish M2 wiring:** write `build_engine_inputs_from_data(inputs, scenario_id) -> FcfEngineInputs`, assembling the WHOLE engine input from data. The pieces already exist in `translator.py`: `build_wacc_from_inputs`, `equity_bridge_adjustments_net_from_data`, `engine_overlays_from_data`. Still hand-typed in `tests/dcf/golden/dnl_mt_inputs.py`: `base_year_revenue` 3400, the **revenue-growth chain** (industry baseline × geo-mix + Five-Forces offset — §11, needs a derivation from archetype/company/matrix data), `stub_years` 0.351, `horizon` 5, and the equity-bridge run-rates (OCF 500, capex 256, period_a 55/365, leases 194.3, market ref 3.61). Goal: reproduce **3.073** with ZERO hand-typed constants → then the other five scenarios → then M3 (segment FCFF for CSL).

**House / mechanics:** Australian English; number multi-point lists; plain-text numbered questions (UI drops AskUserQuestion). Commit sandbox-side (`mv .git/*.lock` aside; push with the `x-access-token` URL). Run `sandbox_cleanup.cmd` for orphaned files. The value-keyed ratchet (`test_ssot_lint`) trips when a migrated data value collides with a code hardcode — if it's a faithful duplicate, `python3 scripts/ssot_lint_baseline.py` regenerates the baseline (verify the diff is only the expected entries). β = **1.10 ratified (final)**. Generator UI base ties (DNL 3.48 / WBC 30.15 / CSL 203.83, netDebt 1512) are the separate reduced-form and unaffected by the engine work.

**Aside logged (not done):** CSL `company_position` doesn't validate against `CompanyPositionFile` (76 schema mismatches — `functional_currency_rationale` missing, `industry_type`/`share_statistics` extra, etc.). Pre-existing and latent (no test runs CSL through `load_inputs`); worth a pass before CSL hits the engine (M3).
