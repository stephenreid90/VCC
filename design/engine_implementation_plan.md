# Engine implementation plan — build-plan steps 6 and 10

**Status:** FOR OWNER APPROVAL (25 June 2026). No production code to be written until signed off.
**Provenance:** Designed via the Plan agent against the live repo; all golden numbers below were
recalculated from the workbooks (LibreOffice headless) and reconcile to WORKING_NOTES.
**Scope:** the production translator (step 6: `linkage/` + `assumptions/`) and the DCF engines
(step 10: `fcf_engine.py` + `bank_engine.py`), with the validated workbooks as the regression oracle.

---

## 0. What was verified before planning

- **The workbooks are the engine.** All CSL / DNL / WBC valuation logic lives in hand-built
  formula workbooks. `src/vcc_valuations/translator.py` and `dcf/fcf_stub.py` are Phase 3.5
  smoke-test stubs — structurally different (single-segment, end-period discounting, additive
  direction x magnitude deltas, no binding terminal margin). They prove pipeline shape but do
  NOT reproduce the workbook numbers. The production engines must reproduce the workbook logic.
- **The two engine shapes are fully legible in the workbooks.** Industrial (CSL/DNL): segment-level
  FCFF with a Gordon terminal whose FCFF is rebuilt from a *binding* terminal EBIT margin and
  terminal capex = D&A. Bank (WBC): a DDM with NII = AIEA x NIM, credit losses as a per-year
  primary driver, CET1-binding payout, and ROE-fade terminal `Equity_T x (ROE_T - g)/(Ke - g)`.
- **Golden numbers (the regression oracle):**
  - CSL MT v4: USD 134.52. Six-scenario (USD/AUD): Orderly 156.61/237.29; Muddle 134.52/203.83;
    AI Lag 131.03/198.53; Disorderly 115.36/174.79; Fragmentation 111.03/168.23;
    Stagflation 105.53/159.90. Terminal share 73.4-76.7% (validator-fires-structurally confirmed).
  - WBC MT v4: AUD 30.03 (flat 0.75 payout); comparison sheet 30.28 (CET1-solved). Y1 cash EPS 2.164.
    Six-scenario: Orderly 35.84; Muddle 30.28; AI Lag 29.92; Fragmentation 27.36; Disorderly 23.21;
    Stagflation 20.11.
  - DNL MT v5: AUD 3.59 vs market 3.61.
- **Structural facts shaping the design:** CSL is genuinely 3-segment (Behring/Seqirus/Vifor + corp),
  per-segment revenue vectors and `n/6`-phased margin uplift; DNL single-segment. The
  scenario-comparison workbooks already express the scenario-overlay pattern the linkage layer must
  produce (CSL overlays absolute per-scenario values; WBC overlays deltas off Muddle Through).
  `data/translation_rules/` does NOT exist yet (§11.2). CSL has NO impact matrix and NO
  `financials.yaml`.

---

## 1. Module layout and responsibilities

### 1.1 `src/vcc_valuations/linkage/` — Layer 5 (matrix application + overrides + validators)

Turns scenario + archetype + company + impact-matrix into a per-scenario `DriverMovementSet`
(qualitative, with quantified bands where present). Does NOT produce numbers.

- `linkage/__init__.py` — public surface: `apply_matrix(...) -> DriverMovementSet`.
- `linkage/loader.py` — load + validate scenario/archetype/company/impact-matrix/financials;
  generalise `translator.load_inputs`; resolve a company whose segments span multiple archetypes
  (CSL) to the union of matrices.
- `linkage/matrix.py` — `select_scenario_entry`; sparse-driver resolution (§10.2; absent ->
  neutral/small/not-assessed); honour `final_quantified_band` (hybrid encoding §11.2.2).
- `linkage/overrides.py` — apply company `scenario_sensitivity_overrides_global` over the archetype
  entry (DNL high-carbon under climate; CSL defensive-margin overlays); record in the trace.
- `linkage/validators.py` — §10.6 "what the matrix may write": no writes to `role: derived`
  drivers (tax, WACC, cost-of-equity, ROE, RWA); defended-exception governance for terminal-state
  drivers (§10.6 rule 2). Emits structured `ValidationFinding` (error/warning); never silently mutates.
- `linkage/driver_movement.py` — the `DriverMovementSet` wrapper consumed by `assumptions/`.

Classes/functions: `DriverMovementSet`, `DriverMovement`, `ValidationFinding`, `apply_matrix()`,
`select_scenario_entry()`, `apply_company_overrides()`, `validate_matrix_writes()`.

### 1.2 `src/vcc_valuations/assumptions/` — Layer 6 (translator -> numbers)

Turns the qualitative `DriverMovementSet` + base-year snapshot into a schema-compliant `AssumptionSet`
(existing `schemas/assumption.py`). The scenario-macro -> industry-archetype -> company-position ->
driver-set chain plus time profiles, derivations and consistency checks.

- `assumptions/__init__.py` — `translate(driver_movements, financials, company, archetype) -> AssumptionSet`.
- `assumptions/rules.py` — loader for `data/translation_rules/*.yaml` (global/per-archetype/per-driver);
  replaces the hardcoded delta dicts in `translator.py`. `confidence` widens/narrows the band ->
  produces `{min,mid,max}`, not a scalar.
- `assumptions/time_profiles.py` — the §11.3 library as code: `impulse`, `regime_shift`, `step`,
  `cyclical`, `front_loaded`, `back_loaded`, `linear_through_horizon`; each `expand(base, target_delta,
  horizon, **params) -> List[float]`. CSL's `n/6` margin phasing is `regime_shift(phase_in_years=6)`;
  the Behring J-curve is an explicit per-year override vector.
- `assumptions/chain.py` — the §2 derivation chain showing industry baseline AND company offset as
  SEPARATE trace rows (§11.1 Step 2->Step 3; the WBC P&L rows 5/6/7 and CSL segment growth vectors).
- `assumptions/derivations.py` — §11.4.1 deterministic identities (effective tax, capex->D&A, cost of
  equity Rf+bxERP, WACC, EBIT/EBITDA margin, bank ROE, RWA growth). Relocate the `WaccBuild`
  dataclass from `dcf/fcf_stub.py` to `assumptions/wacc.py`.
- `assumptions/consistency.py` — §11.4.2 checks (operating-leverage; terminal-state convergence;
  mix-shift; terminal-share hook) plus the v0.7 §11.6 terminal-continuity check (terminal margin must
  not exceed explicit-period exit-year margin — the orphaned-CSL-terminal-margin bug, caught in code).
- `assumptions/aggregate.py` — §11.2 step-5 segment aggregation via per-driver `aggregation_method`
  (`revenue_weighted_avg`, `ebit_weighted_avg`, `sum`, `identity_if_company_scope`). CSL needs it;
  identity for DNL/WBC.
- `assumptions/build.py` — orchestrates chain -> time profiles -> derivations -> consistency -> emit
  `AssumptionSet` with full `reasoning_trace`.

### 1.3 Single-WACC discipline (§3.5) lives in `assumptions/`, not the DCF

`assumptions/derivations.py` computes ONE `WaccBuild` from valuation-date components and writes that
single WACC into the consolidated assumptions. `linkage/validators.py` blocks any scenario from
flowing Rf / ERP / country-risk / beta deltas into the discount rate (§3.5.6) — retained for
narrative/interest only. Terminal growth IS the deliberate scenario-conditional exception (§3.5.5).
The DCF receives WACC as a single derived scalar and never recomputes it per scenario (matches every
CSL `S_*` discounting at the same Re; WBC at the same Ke).

---

## 2. The DCF engines (step 10)

### 2.1 `dcf/fcf_engine.py` — industrial, segment-level FCFF

`class FcfEngine` with `run(assumption_set) -> FcfDcfResult`. Mirrors `Segment Forecasts` +
`Per-Share Value`:
- `_forecast_segments` — per-segment revenue vector (CSL Behring J-curve; Seqirus/Vifor flat CAGR);
  per-segment OR margin = base + peer-gap-closure uplift phased `n/N` (§3.2); roll up to group
  revenue + segment OR; subtract corporate; -> Group EBIT.
- `_fcff` — NOPAT = EBIT x (1-tax); + D&A; - capex; - ΔWC. (CSL `S_*` rows 23-27.)
- `_terminal` — THE load-bearing correctness requirement. Terminal FCFF rebuilt from the BINDING
  terminal EBIT margin, with terminal capex = D&A (v4 fix):
  `terminal_FCFF = FY31_rev x terminal_margin x (1-tax) + D&A - terminal_capex` (capex = D&A);
  `TV = terminal_FCFF/(Re - g)`, discounted at end-Y5. Never capitalise the exit-year peak margin
  (the CSL v1 bug, ~84% of the USD 23 correction).
- `_discount` — mid-period convention; explicit-period start parameterised (CSL excludes FY26 from
  explicit PV); Period-A/B stub optional, off by default to match the oracle.
- `_equity_bridge` — EV - net debt - restructuring-cash-to-come (PV, §4.4(b)); ÷ shares; x FX (FX only
  at the per-share line).
- Diagnostics: terminal share of EV; fire the §11.4.2 70% validator (warning, not raise).

`FcfDcfResult`: revenue/ebit/nopat/capex/da/fcf vectors, terminal block, pv_explicit, pv_terminal,
EV, equity, per-share (USD + AUD), terminal_share, per-segment detail, notes.

### 2.2 `dcf/bank_engine.py` — the §15 bank fork (DDM)

`class BankEngine` with `run(assumption_set) -> BankDdmResult`. Cost of equity, not WACC; no EV->equity
bridge. Mirrors `P&L Forecast` + `Per-Share Value`:
- `_nii` — AIEA grows at industry AIEA growth + Five-Forces offset (§11.1 derived row);
  NII = AIEA x NIM x period; per-year NIM trajectory; stub-year ramp parameterised.
- non-interest income; opex = total income x per-year CTI (peer-gap-closure glide); pre-provision profit.
- `_credit` — credit losses as a PRIMARY driver (§15.4): - avg-loans x per-year credit-loss-rate;
  per-year vector scenario-conditional.
- `_capital` — CET1-binding payout (§15.5): CET1 generated = cash earnings x (1-payout); required =
  ΔRWA x CET1 target; payout forced down if generated < required, surplus returnable above buffer.
  (The comparison workbook implements this; the flat-0.75 MT workbook simplifies it — see R5.)
- `_terminal` — ROE-fade `TV_equity = Closing_book_equity_T x (ROE_T - g)/(Ke - g)` (§15.8).
- `_equity_bridge` — total equity claim - AT1 hybrid (face) - NCI (book) - treasury (book) = ordinary;
  Tier 2 / senior debt NOT bridged (they flow through NIM). (§15.7.)

`BankDdmResult`: NPAT vector, dividend vector, avg-payout, final CET1, closing book equity,
PV-dividends, PV-terminal, total-equity-claim, ordinary-equity, per-share.

### 2.3 §16 market-implied cross-check (§3.5.7) — `dcf/market_implied.py`

A POST-valuation diagnostic, not part of the DCF. `reverse_dcf(result, market_price, fx) ->
MarketImpliedReport` reproduces the CSL `Market-Implied (§3.5.7)` sheet: market equity -> EV target ->
required terminal PV -> implied terminal margin / implied Re (beta) / implied terminal g, single-lever.
For banks: implied terminal ROE / Ke. The §16 interpretive output (which scenario the market is
implicitly pricing) comes from the six-scenario distribution (closest per-share + enumerate the
differing assumptions). Single-WACC keeps this clean: vary one lever against a fixed base WACC.

---

## 3. Regression oracle — golden-master test strategy

Tolerance: ±0.5% on per-share; ±0.05 absolute on headline per-share; ±0.5pp on terminal-share.

- `tests/dcf/golden/_recalc.py` — committed helper that runs LibreOffice headless over the reference
  workbooks and dumps target cells, so the oracle is reproducible, not hand-typed. Fixtures:
  `csl_mt_v4.json`, `csl_scenarios_v2.json`, `wbc_mt_v4.json`, `dnl_mt_v5.json`.
- `tests/dcf/` — `test_fcf_engine_csl_mt.py` (134.52 + line-level), `test_fcf_engine_csl_scenarios.py`
  (six + asymmetry ~1.31x + validator fires), `test_fcf_engine_dnl_mt.py` (3.59, single-segment),
  `test_bank_engine_wbc_mt.py` (30.03 AND 30.28), `test_bank_engine_wbc_scenarios.py`,
  `test_terminal_fixes.py` (binding terminal margin; terminal capex == D&A — encodes the v1 and v3->v4
  corrections), `test_market_implied.py` (implied beta ~1.71, margin ~13.5%, g ~ -4.1%).
- `tests/linkage/` — `test_matrix_application.py`, `test_overrides.py`, `test_matrix_write_validators.py`.
- `tests/assumptions/` — `test_translation_rules.py`, `test_time_profiles.py` (n/6 reproduces CSL phasing;
  override vector reproduces the J-curve), `test_chain_traceability.py` (industry + offset as distinct
  rows summing to derived), `test_derivations.py` (CSL Re 8.75%; WBC Re 8.05%), `test_consistency_checks.py`.
- End-to-end: `tests/test_e2e_csl_mt.py`, `tests/test_e2e_wbc_mt.py`, `tests/test_e2e_dnl_mt.py`.

---

## 4. Sequencing and milestones

Smallest end-to-end vertical slice = DNL x Muddle Through (single-segment, existing matrix + financials,
oracle AUD 3.59). Prove that first, then generalise to segments (CSL) and the bank fork (WBC).

- **M0 — De-risk decisions (no code).** Lock R1/R3/R4/R5. ~½ session. *(Owner sign-off gate.)*
- **M1 — DNL MT vertical slice.** `linkage/` + minimal `assumptions/` + single-segment `fcf_engine.py`;
  `test_e2e_dnl_mt.py` to 3.59. ~1-1.5 sessions.
- **M2 — Full `assumptions/` layer.** `data/translation_rules/`; full time-profile library; derivations;
  consistency + terminal-continuity; segment aggregation; retire `SmokeAssumptionSet`. ~1.5 sessions.
- **M3 — Segment FCFF + CSL.** Generalise to segments; binding terminal margin; terminal capex=D&A;
  reconcile CSL MT + six. BLOCKER: CSL needs an impact matrix + financials.yaml (R1). ~1.5 sessions.
- **M4 — Bank engine + WBC.** NII=AIEA x NIM, credit primary, CET1-binding payout, ROE-fade terminal,
  §15.7 bridge; reconcile WBC MT + six. ~1.5 sessions.
- **M5 — §16/§3.5.7 cross-check + outputs.** `market_implied.py`; closest-scenario diagnostic; write
  `output/{driver_movements,assumption_sets}/`; `docs/dcf_engine.md`; wire engine to the UI prototype
  sliders. ~1 session.

Dependencies: M1 -> M2 -> {M3, M4} (M3 better next, exercises segment aggregation) -> M5.

---

## 5. Risks and open decisions (for owner sign-off)

- **R1 — CSL has no impact matrix and no `financials.yaml`.** Before M3, either (a) author CSL impact
  matrices + financials.yaml by reverse-engineering the workbook columns (principled; real authoring
  work), or (b) feed the engine from a CSL fixture to get the test green and defer authoring.
  Recommend (a), scoped explicitly.
- **R2 — Multi-archetype company.** The loader must resolve per-segment archetype -> per-segment matrix
  for CSL. Low technical risk; a loader generalisation to confirm.
- **R3 — Terminal-share validator fires structurally on long-duration compounders. DECIDED 25 June 2026 (Stephen): keep it a NON-BLOCKING warning that triggers a sensitivity pass; do not auto-suppress.** (CSL 73-77%, DNL
  72-80%). Keep it a NON-blocking warning triggering a sensitivity pass; do NOT auto-extend horizon or
  auto-fade ROIC to suppress it (that would silently change the documented numbers). The phase-3.5
  10-year / explicit-fade mitigations stay OPTIONAL modes, not defaults.
- **R4 — Segment detail: encode vs parameterise.** Encode segments and per-year vectors as DATA
  (`AssumptionCell.mid` is already a per-year list); phasing is a time-profile selection, not hardcoded
  `/6`; the corporate line growth is a parameterised driver, not a constant.
- **R5 — WBC payout oracle: 30.03 (flat 0.75) vs 30.28 (CET1-solved). DECIDED 25 June 2026 (Stephen): the CET1-binding mechanic is the sounder methodology for financial institutions; 30.28 is the canonical bank-engine acceptance number. The flat-0.75 MT valuation workbook (30.03) is a superseded artefact — to be noted as such, and optionally refreshed to a v5 binding-payout build.** The engine should implement the
  CET1 constraint (§15.5), so its natural oracle is 30.28; the 30.03 workbook is a simplified earlier
  artefact. Confirm 30.28 as the acceptance number, and whether to refresh the MT valuation workbook to
  match or keep both with a documented ~0.8% reconciliation.
- **R6 — β / market-implied tension is a retained §16 output, not a bug to tune away.** Engine must NOT
  auto-adjust β toward the market-implied figure; §3.5.7 is reporting only. Restate in `docs/dcf_engine.md`.
- **R7 — v0.7 dependency.** The §3.5.7 market-implied check and §11.6 terminal-continuity discipline are
  assumed accepted (now folded into architecture.md v0.7). M2/M5 shift if revised.
- **R8 — Currency discipline.** CSL USD-throughout, AUD only at the per-share line; DNL per-entity
  functional currency (parent AUD, US sub USD). Confirm whether the production engine needs segment-level
  FX now or whether single-currency treatment suffices for the test companies.

---

## Critical files for implementation

- `src/vcc_valuations/translator.py` — the stub to decompose into `linkage/` + `assumptions/`.
- `src/vcc_valuations/dcf/fcf_stub.py` — the stub `fcf_engine.py` replaces; `WaccBuild` relocates to `assumptions/wacc.py`.
- `src/vcc_valuations/schemas/assumption.py` — the `AssumptionSet` contract the translator emits and both engines consume.
- `analyses/csl/valuations/csl_scenarios_comparison_v2.xlsx` — segment-FCFF + scenario-overlay + §3.5.7 oracle.
- `analyses/wbc/valuations/wbc_muddle_through_valuation_v4_formulas.xlsx` (+ `wbc_scenarios_comparison_v2.xlsx`) — bank-fork oracle.
- `design/methodology/equity_bridge_and_valuation_mechanics.md` — governing methodology for both engines.
