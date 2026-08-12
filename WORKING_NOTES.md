# VCC Valuations — Working Notes

A living scratchpad for conversational decisions, current preoccupations, and session
handoffs — the *volatile* layer. Durable facts and standing rules live in `CLAUDE.md`
(the front door, read first every session). **Maintained by Stephen + Claude.**

---

## Read order

See `CLAUDE.md` for the canonical session read order. In short: `CLAUDE.md` → this file
→ `design/architecture.md` → `design/build_plan.html` → (optional) `design/frameworks/`.


---

## CHAT HANDOVER — 12 August 2026 (f) (DNL UI headline wired to the engine — one source of truth, replicable)

The DNL scenario-interface HTML now shows the PRODUCTION ENGINE's numbers, not the old hand-calibrated
set. `ui_prototypes/_generator/build_cfgs.py` computes the six DNL per-share values from the engine at
generation time via a reusable `engine_pack(company_id, archetype_id, scen, broker_price)` — the same call
will drive WBC/CSL. Pushed. (Generator-only change; test suite unaffected, still 99; ratchet green.)

1. **`engine_pack()`** (new, company-agnostic) runs `build_engine_inputs_from_data` per scenario and returns
   base, scenario bars (with the broker bar spliced after the upside), asymmetry (down/up), discount-to-market
   and the per-scenario per-share. Applied to DNL: **base 3.48 → 3.073**, re0 0.0868 → **0.088772**, the six
   bars → engine values (OC 3.562 / MT 3.073 / AIPL 2.985 / Frag 2.222 / DClim 1.177 / Stag 1.019), asymmetry
   **4.2×**, discount-rate slider default → 8.88 (keeps the reduced-form base tie: computeVals(defaults)=3.072).
2. **Narrative re-anchored (Stephen's Direction 2 — measured), numbers engine-sourced.** MT now reads "below
   market (AUD 3.61, ~15%)… emphasis is the scenario asymmetry, not the central level" (was "~4% … agrees
   with consensus" — that framing was FALSE at 3.073). Per-scenario deltas recomputed (+AUD 0.49 / −AUD 2.05 /
   the % vs MT). Footnote + topnote flipped from "calibrated" to "engine-computed". WACC text 8.68%→8.88%,
   weights 79/21→83.5/16.5.
3. **Verified:** `node --check` OK on all three inlined scripts; base tie holds; **WBC/CSL untouched (base
   30.15 / 203.83)**; regenerated HTMLs written to `ui_prototypes/`.

**Left deliberately (visible inconsistency to close next):** the **"Valuation build-up" drill-down** and the
**financials tab** still show the OLD hardcoded bridge — EV **8,064** (→ engine 7,009), per-share **3.48**
(→ 3.073), shares **1,884** (→ 1,770), net debt **1,512**, leases **212** (→ 194.3). These are a different
construction (the generator's lease-inclusive steady-state anchor vs the engine's Period-A walk).
`translator.equity_bridge_from_data` already produces the full engine bridge (EV 7,009 → nd@val 1,224 →
adj 151.65 → leases 194.3 → equity 5,439 → 3.073), so the next slice is mapping that derivation into the
generator's DCF-bridge + net-debt table so the build-up matches the headline. Until then the headline is
engine-sourced but the build-up drill-down lags.

**Replicable pattern established:** `engine_pack` + inject into cp.base/re0/scenarios/metric4/slider-def +
engine-sourced narrative numbers. Roll the SAME onto WBC and CSL once their scenarios resolve (WBC bank fork,
CSL segment FCFF/M3).

**UPDATE (same session): the "Valuation build-up" gap is now CLOSED.** The DCF bridge, dcfRows, the lease
panel, the net-debt table and the per-year operating build are all wired to the engine via
`equity_bridge_from_data` + the central-case `FcfDcfResult`. The build-up now shows: EV **7,009** → net debt
at valuation **(1,224)** (Period-A walk from the 1,261 anchor, §7) → **equity-bridge adjustments (152)** now
shown as their OWN line (§4.2, previously hidden in the anchor) → leases **(194)** → equity **5,439** ÷
**1,770** → **3.07** — matches the headline. Operating build re-based to the ratified **3,400** continuing-ops
base (revenue [3609,3831,4067,4318,4583]; the stale 3,905 note dropped). Net-debt table rebuilt to the
Period-A walk; leaseMat/richbook/multiples anchors updated (shares 1,770, nd-incl 1,418, leases 194.3);
discount drill-down gearing text → E/V 83.5/16.5 off 1,770m. `node --check` OK on all three; WBC/CSL base
30.15/203.83 unchanged; suite 99. **DNL is now single-sourced end to end — headline AND build-up.** Remaining
UI item: WBC/CSL still hand-calibrated (roll the same pattern).

DNL now values end-to-end from data across ALL SIX scenarios (was MT only). Restructured the
scenario-specific blocks into the methodology's baseline + overlay shape and added the five non-MT
scenarios from `dnl_scenarios_comparison_v4`. Pushed. **Suite 90 → 99.**

**Per-share (ratified WACC 8.877%, β 1.10):** Orderly Convergence 3.562 > Muddle Through 3.073 >
AI Productivity Lag 2.985 > Fragmentation 2.222 > Disorderly Climate 1.177 > Stagflation 1.019. Downside
skew ~4.2× (v4 workbook 4.05×). These supersede the v4 comparison's per-share (which were at a stale
β-0.95 WACC 0.0828), exactly as MT's 3.073 superseded 3.484.

1. **`revenue_growth_chain` restructured** to `shared` (industry_structure coeffs + company_offset — both
   scenario-invariant) + `by_scenario.{id}.macro` (DM inflation, global mining real growth, gas price
   growth, + DM-GDP context memo). De-duplicates the shared coefficients across the six. The chain
   reproduces the workbook's per-scenario revenue growth (row 26) to the cent for all six.
2. **`engine_overlays` restructured** to `baseline` (the MT v6 operating build) + `by_scenario.{id}` deltas
   (`margin_delta_pp`, `capex_delta_pp`, `terminal_growth`). **Owner decision (12 Aug): scenario margin/capex
   deltas apply as a PARALLEL SHIFT across the five explicit years** (regime is persistent from Y1; the stub
   is unshifted). `translator.engine_overlays_from_data` now RESOLVES baseline+deltas and returns the same
   keys consumers expect — so MT (zero deltas) is unchanged and still ties 3.073. Y5 EBIT margin ties the
   workbook (row 27) for all six.
3. **Scenario data source:** `dnl_scenarios_comparison_v4.xlsx` Inputs sheet (macros rows 6-9; deltas rows
   12-14). Net company-position offset is scenario-invariant (row 23). Rationale for the margin deltas:
   the cost-pass-through channel (upside = margin protected/lifted; Stagflation = input inflation can't be
   passed through, −7.5pp the binding downside). WACC + equity bridge + tax bridge are all shared.
4. **Tests +9** (`test_dnl_all_scenarios.py`): parametrized driver-ties-workbook for all six, MT==3.073,
   asymmetry downside-skewed, single-WACC-across-scenarios. **Ratchet 136 → 137** (one coincidental collision:
   0.04 = OC mining growth vs a beta_data.py literal). Regenerated + verified.

**Where DNL stands: DONE for the engine path.** All five derived sheets trace at V6 granularity (revenue
chain, WACC, Equity Bridge, Tax Bridge) AND all six scenarios produce per-share from data with zero
hand-typed constants. `dnl_mt_inputs.py` remains oracle-only.

**Next — roll across the other two (Stephen's plan: get happy with one, then the other two).** WBC (bank
archetype — Ke discipline, no WACC/EV bridge, different operating build: NIM / cost-to-income / credit
losses, methodology §15) and CSL (segment FCFF, Ke, M3 — and the pre-existing 76-error
`CompanyPositionFile` schema mismatch to clear first). WBC and CSL each have a `_scenarios_comparison`
workbook to source the six scenarios from, same as DNL. The DNL scenario structure (shared + by_scenario,
parallel-shift overlay) is the template. Also still open: per-year P&L margin `Derivation` (parity item);
the human-readable workings view (deferred); the DM-inflation basis reconciliation.

Rolled the traceability pattern onto the Tax Bridge, which doubled as a genuine single-source-of-truth
fix: the per-year `tax_rate_glide` was a STORED derived value in `engine_overlays` (the effective rate
gliding to blended statutory) — exactly the "stored answer" the protocol targets. Now derived. Pushed.
**Suite 88 → 90.**

1. **`data/companies/dnl.yaml`** — new `normalised_baseline.tax_bridge` block, INPUTS ONLY: `effective_tax_rate`
   0.225 (B59), `statutory_rate_by_region` (US 0.26 / Australia 0.30 / Rest of World 0.27, keyed to the
   geographic_concentration region names so the revenue WEIGHTS are derived, not restated), and
   `glide_fractions` [0, .25, .5, .75, 1] (E12-E16). **Removed `stub_tax_rate` and `tax_rate_glide` from
   `engine_overlays.muddle_through`** — both were derived, now sourced from the bridge.
2. **`translator.tax_bridge_from_data(inputs) -> Derivation`** exposes the V6 rows: per-region contributions
   D5-D7 (revenue_weight x statutory_rate), blended statutory **D8 = 0.275** (0.55x0.26 + 0.35x0.30 +
   0.10x0.27), and the applied-tax glide B12-B16 = effective + (blended − effective) x fraction =
   [0.225, 0.2375, 0.25, 0.2625, 0.275] — reproducing the value that used to be hardcoded.
   `build_engine_inputs_from_data` now sources stub + glide from here; the ratified overlays test updated
   to match. **DNL MT still 3.073 / EV 7,009.2.**
3. **Tests +2** (`test_dnl_mt_from_data.py`): D8 + glide pinned and shown derived (nine steps D5-B16); and a
   guard that `tax_rate_glide`/`stub_tax_rate` are GONE from the stored overlays. Fixed the field-by-field
   test to compare the glide with tolerance (float artifact 0.2375 vs 0.23750000000000002).
4. **Ratchet 138 → 136** — the diff is instructive: three `0.275` entries *removed* (wacc/beta_data/build_cfgs)
   because 0.275 is no longer a stored data value (it's derived D8), so those code copies stopped being
   duplicates; one `0.26` added (US statutory rate coincidentally in gen_ui.py). Regenerated + verified.

**Traceability status — all five derived sheets now at V6 granularity:** revenue-growth chain (b), WACC
Build (c), Equity Bridge (c), **Tax Bridge (this block)**. The `Derivation` primitive now has four worked
examples (translator-built: revenue chain, tax bridge; dataclass-method: WaccBuild, EquityBridge). The
only remaining parity item is surfacing the **per-year P&L margin build** (base + transformation +
gas-rolloff, and the applied-tax glide as it lands per year) as a `Derivation` — but those values already
appear in the engine's per-period `FcfDcfResult`, so it's presentation, not new logic.

**Next.** (1) The other five DNL scenarios (each needs `engine_overlays[scenario]` +
`revenue_growth_chain[scenario]`; tax_bridge is company-level and shared unless a scenario overrides).
(2) M3 segment FCFF for CSL. (3) Deferred: the human-readable workings view from `Derivation.as_rows()`.
(4) The inflation-basis note (workbook DM inflation 2.5% normalising vs scenario CPI 3.0% sticky).

Continued rolling the full-V6-traceability pattern (from block (b)) onto two more sheets. Same discipline:
inputs are the yellow cells (data); every workbook *derived row* is a named `DerivationStep` computed in
code — never stored. Pushed. **Suite 86 → 88.**

1. **WACC Build** — `WaccBuild.derivation()` (method, co-located with the build; reusable for any
   WACC-discipline company) exposes the six V6 rows: B8 cost of equity (Rf + β×ERP), B13 after-tax cost
   of debt, B18 EV (E+D), B19 E/V, B20 D/V, B23 WACC. `translator.wacc_build_from_data(inputs)` returns
   it from data (`None` for banks/CSL). **Values reflect the RATIFIED inputs (β 1.10, tax 0.30) — they
   deliberately SUPERSEDE the v6 WACC sheet's cached β 0.95 / tax 0.275; row structure matches V6, numbers
   are the production discount rate.** B8 0.098, B13 0.042, B18 7,650.8, B23 0.088772.
2. **Equity Bridge** — `EquityBridge` now RETAINS its Period-A walk inputs (added optional fields
   `net_debt_anchor`/`period_a_years`/`operating_cash_flow_run_rate`/`capex_run_rate`, populated by
   `from_anchor`), so `EquityBridge.derivation(enterprise_value)` can trace the whole sheet: the walk
   (B6 anchor → B7 less OCF → B8 plus capex → B10 subtotal → B11 net debt at valuation) and the per-share
   chain (B27 EV → B28 net debt → B29 adjustments → B30 leases → B31 equity → B33 VPS → B37 discount).
   `translator.equity_bridge_from_data(inputs, scenario)` assembles inputs, runs the DCF for EV, and
   returns the trace. Ties the golden walk (B11 1,224.03) and the engine headline (B33 3.073, B37 −14.9%).
3. **Tests +2** (`test_dnl_mt_from_data.py`): WACC six rows pinned at ratified inputs; equity-bridge twelve
   rows pinned incl. B33 == engine `value_per_share` to 1e-9. **Ratchet:** no baseline change; one transient
   docstring trip again (scanner read "1.10"/"0.30" out of the WACC docstring prose) — reworded to words.
   Lesson holding: keep domain numbers out of `.py` prose (docstrings/comments), the regex scan is literal.

**Traceability status.** Now at full V6 granularity: the **revenue-growth chain** (b), the **WACC Build**,
and the **Equity Bridge**. Remaining sheets for the same treatment: the **Tax Bridge** (effective→statutory
glide, B12-B16 + D8), and the **per-year P&L build** (the margin = base + transformation + gas-rolloff
glide and the applied-tax glide already live in the engine's per-period result, but surfacing them as a
`Derivation` would complete parity). The `Derivation` primitive + the three worked examples are the template.

**Reminder for next session:** `WaccBuild` and `EquityBridge` now have `.derivation(...)`; the pattern is
"retain inputs on the dataclass, expose a `.derivation()`" (WaccBuild/EquityBridge) or "build in the
translator from data" (revenue chain). A human-readable workings view rendered from `Derivation.as_rows()`
is still deferred (Stephen took code-traceability first).

---

## CHAT HANDOVER — 12 August 2026 (b) (revenue-growth chain to FULL V6 traceability; the reference pattern for the whole model)

Stephen's steer (important, model-wide): the model must be **at least as granular as the V6 workbook**, and
Excel must NOT be the source of truth — it's an incidental scratchpad for eyeballing, not a driver/source.
Today's commit removed the last workbook-sourced constants from the DNL-MT production path (block below);
this one makes the revenue-growth chain's *derivation* as granular and auditable as V6, as the reference
pattern to roll across the other derived sheets (Tax Bridge, WACC Build, margin/gas glide, Equity Bridge).
Pushed. **Suite 80 → 86.**

1. **New `src/vcc_valuations/derivation.py`** — the model-wide primitive. `DerivationStep` (key, label,
   value, formula, inputs, workbook `cell`, units) + `Derivation` (ordered steps, lookup by key/cell,
   `.result`, `.as_rows()`) + a `DerivationBuilder`. The code-side equivalent of a workbook's labelled
   derived rows: inputs are the yellow cells (data); every *formula* row is computed here and exposed as a
   named, self-describing step — never stored back into the data. Generic on purpose (5 tests).
2. **`data/companies/dnl.yaml` revenue_growth_chain relabelled to V6 nomenclature, INPUTS ONLY** — DM
   inflation (B18), global mining real growth (B19), gas price growth (B20), volume coefficient a / constant
   b (B23/B24), pricing weights (B26/B27), productivity sharing (B28), em_growth_premium (B35), the named
   Five-Forces sub-offsets (B37-B40), plus the B17 DM real GDP growth carried as a `macro_context` memo
   (explicitly NOT consumed — the chain keys off B19 + B18). `developed_market_regions` [US, Australia]
   classifies the geo split. No derived value is stored.
3. **`translator.revenue_growth_chain_from_data(inputs, scenario_id) -> Derivation`** exposes all eight V6
   derived rows: B25 industry volume, B29 industry pricing, B30 industry nominal, **B33 DM weighting /
   B34 EM weighting (now DERIVED from the segment `geographic_concentration` — finer than V6, which hardcoded
   0.9/0.1)**, B36 geo-mix multiplier, B41 net company offset, B42 company nominal — each with formula + cell
   + the inputs it consumed. `revenue_growth_from_data` is now a thin wrapper returning `.result` for the
   engine assembler. Ties V6 row-by-row (B25 .03275, B29 .0285, B30 .062183375, B33 .9, B34 .1, B36 1.03,
   B41 −.0025, B42 .06154887625) and the golden to 1e-12; **DNL MT still 3.073 / EV 7,009.2**.
4. **Tests:** `test_derivation.py` (5, the primitive); `test_dnl_mt_from_data.py` +2 — every intermediate
   pinned to its V6 value, and each step asserted to carry formula + inputs + cell provenance (incl. that
   DM/EM weighting names the regions it summed, proving it's derived not stored).
5. **Ratchet:** no baseline change (relabel kept values identical). One transient trip — the regex scanner
   read the numerals "0.9/0.1" out of a **docstring**; reworded the prose to "DM/EM weighting" (the scan is
   comment-blind to intent, so keep domain numbers out of `.py` prose). Baseline stays 138.

**The pattern to reuse (Stephen wants full V6 traceability model-wide, one sheet at a time).** Inputs → data
(yellow cells); each workbook *derived row* → a `DerivationStep` computed in code (formula + cell + inputs),
never stored. Next candidates, same treatment: the **Tax Bridge** (effective→statutory glide), the **WACC
Build** (Rf/ERP/β → Ke → WACC with E/V weights), the **margin/gas glide** (base + transformation + roll-off
per year, already data but the derived per-year EBIT margin should surface as steps), and the **Equity
Bridge** (EV → net-debt walk → adjustments → leases → per-share). A human-readable "workings" view rendered
from `Derivation.as_rows()` (the inverted, byproduct-not-source relationship) was **deferred** — Stephen
picked the code-traceability pattern first.

**Next.** (1) Roll the derivation pattern across the sheets above. (2) The other five DNL scenarios (each
needs `engine_overlays[scenario]` + `revenue_growth_chain[scenario]`). (3) M3 segment FCFF for CSL. (4) The
inflation basis note: workbook DM inflation 2.5% (normalising) vs scenario `cpi_inflation_advanced` 3.0%
(sticky) — same concept, different assumed value; reconcile when the macro layer is formalised.

---

## CHAT HANDOVER — 12 August 2026 (M2 — full engine input assembled from data; DNL MT reproduces 3.073 with ZERO hand-typed constants)

The M2 assembly milestone for DNL Muddle Through: `translator.build_engine_inputs_from_data(inputs, scenario_id)`
composes the WHOLE `FcfEngineInputs` from the YAML files, so the ratified β-1.10 valuation
(**3.073/share, EV 7,009.2, WACC 8.8772%**) now reproduces with no hand-typed constant anywhere.
Every field traces to a data file. Pushed. **Suite 76 → 80.**

1. **`data/companies/dnl.yaml` `normalised_baseline`** gained the last three hand-typed groups
   (migrated from `tests/dcf/golden/dnl_mt_inputs.py`, all with workbook cell refs):
   (a) valuation base / timing — `base_year_revenue` 3400 (B9, normalised continuing-ops base, ≠ the
   3,905 TTM), `horizon_years` 5 (B78), `stub_years` 0.351 (B6);
   (b) `equity_bridge_run_rates` — `period_a_days` 55 (B84), `operating_cash_flow_run_rate` 500 (B86),
   `capex_run_rate` 256 (B87), `lease_liabilities` 194.3 (B108, a later date than the 211.5 FY25-close
   in financials), `market_reference_price` 3.61 (B110). Net-debt anchor 1,260.8 and shares 1,770m are
   NOT duplicated — they come from the §5.3-anchored `data/financials/dnl.yaml`;
   (c) `revenue_growth_chain.muddle_through` (§11) — split into SEPARATE rows per standing rule 1:
   `industry_baseline` (volume: mining_beta 1.15 / mining_real 0.025 / intercept 0.004; pricing:
   infl 0.025 ×0.7 + gas 0.02 ×0.3 + productivity 0.005) and `company_offset` (em_premium 1.3,
   `developed_market_regions` [US, Australia], the net Five-Forces offset −0.003/−0.001/+0.0015/0).
2. **`translator.revenue_growth_from_data(inputs, scenario_id)`** reproduces workbook B42 as a
   DERIVATION (industry_nominal × geo_mix + net_offset), not a stored scalar. Geo-mix is derived from
   the segment's `geographic_concentration` (US+AU = DM ~90%, RoW = EM ~10%) × em_premium — a change to
   the concentration data moves the chain (test pins this). **`build_engine_inputs_from_data`** then
   assembles the full input from the four data-driven pieces (WACC, overlays, revenue chain, bridge
   adjustments) + the migrated scalars/run-rates. Ties the golden bit-for-bit: revenue_growth
   0.061548876…, net_debt_at_valuation 1,224.03, adjustments 151.65.
3. **New `tests/dcf/test_dnl_mt_from_data.py` (4 tests):** end-to-end 3.073/EV/WACC from data;
   revenue-chain derivation ties `_revenue_growth_chain()` to 1e-12; field-by-field match to the golden
   (β excepted — data 1.10, golden 0.95); geo-mix responds to a concentration perturbation.
4. **Ratchet:** 15 new coincidental collisions (500, 1.3, 0.7, 1.15, 256 vs generic literals in the
   generator / estimate_emrp / stub — NOT the engine reading a migrated value). Baseline regenerated
   123 → 138 via `scripts/ssot_lint_baseline.py`; diff verified to be exactly those 15 additions.

**Layering note / follow-up.** The `revenue_growth_chain.industry_baseline` coefficients are in
principle archetype-level and the two macro drivers scenario-level, but they sit in `dnl.yaml` for now
because (a) `IndustryArchetypeFile` is `extra="forbid"` (strict), so promoting them needs a schema
field, and (b) the workbook's MT macro values (mining_real 2.5%, infl 2.5%, gas 2.0%) DIFFER from
`data/scenarios/muddle_through.yaml` (world GDP 2.3%, CPI 3.0%) — reconciling the workbook basis to the
published scenario macros is separate, later work. Promoting `industry_baseline` to the archetype file
(with a schema field) is the clean follow-up. Stephen approved keeping the block in the loosely-typed
company layer this slice (option 1-alt).

**`dnl_mt_inputs.py` is now oracle-only.** Nothing in the production path imports it: it survives as the
cross-check in `test_dnl_mt_from_data.py` and as the β-0.95 engine-mechanics oracle in
`test_e2e_dnl_mt.py` (3.484). The whole DNL-MT production number is now data-driven end to end.

**Next.** (1) The OTHER FIVE DNL scenarios — each needs its own `engine_overlays[scenario]` +
`revenue_growth_chain[scenario]` block, then `build_engine_inputs_from_data` produces all six from data;
worth a shared derivation check against the generator's calibrated per-share set. (2) Then M3 — segment
FCFF for CSL (a separate assembler; `build_engine_inputs_from_data` is single-segment / WACC-discipline
only, raises for banks / CSL). (3) Aside still open (pre-existing): CSL `company_position` doesn't
validate against `CompanyPositionFile` (76 schema mismatches) — worth a pass before CSL hits the engine.
(4) Follow-up: promote `industry_baseline` to the archetype schema and reconcile the workbook macro
basis to the scenario file.

---

## CHAT HANDOVER — 11 August 2026 (f) (M2 — per-year engine overlays data-driven)

Final M2 slice this session: migrated the Muddle Through per-year overlays out of the hand-typed
`dnl_mt_inputs.py` into a scenario-keyed data block. Pushed.

1. **`data/companies/dnl.yaml` `normalised_baseline.engine_overlays.muddle_through`** — the per-year
   glides: `margin_transformation` [0.006,0.018,0.02,0.02,0.02], `margin_gas_rolloff`
   [0,0,−0.005,−0.01,−0.015], `tax_rate_glide` [0.225…0.275], `capex_pct` [0.08,0.08,0.07,0.07,0.07],
   plus `base_ebit_margin` 0.141, `stub_tax_rate` 0.225, `capex_pct_stub` 0.08, `da_pct_revenue` 0.073,
   `terminal_growth` 0.025 — all tie the workbook cell refs.
2. **`translator.engine_overlays_from_data(company_raw, scenario_id)`** returns the scenario overlay
   mapping. New test builds FcfEngineInputs from the DATA overlays + DATA WACC and reproduces the
   ratified **3.073** (fidelity check — drift in any overlay would move it). **Suite 75 → 76.**
3. **Ratchet:** `tax_rate_glide` re-introduced 0.275 (27.5% tax); the three code hardcodes (wacc.py,
   beta_data.py, build_cfgs.py) re-collide — real duplicates, baselined 120 → 123 (they were baselined
   pre-CSL-deletion too).

**M2 data-driven surface now:** discount rate (β 1.10 WACC), equity-bridge adjustments (§4.2/§4.3), and
the per-year overlays — all from data, all reproducing 3.073. **Still hand-typed** in
`tests/dcf/golden/dnl_mt_inputs.py`: `base_year_revenue` 3400, the revenue-growth chain (industry ×
geo-mix + FF offset), `stub_years` 0.351, horizon 5, and the equity-bridge RUN-RATES (OCF 500, capex
256, period_a 55/365, leases 194.3, market ref 3.61; net_debt_anchor 1260.8 and shares 1770 are already
in data). **Next milestone:** `build_engine_inputs_from_data(inputs, scenario)` assembling the whole
FcfEngineInputs from data + the revenue-chain derivation (§11) → zero hand-typed constants; then the
other five scenarios; then M3 (segment FCFF for CSL).

---

## CHAT HANDOVER — 11 August 2026 (e) (M2 — equity-bridge adjustments data-driven, §4.2/§4.3)

Continued the M2 assumptions-layer build: migrated DNL's Fertilisers-separation equity-bridge
adjustments out of the hand-typed `_equity_bridge_adjustments_net()` into a structured data block
(methodology §4.2) and implemented the §4.3 validator. Pushed.

1. **`data/companies/dnl.yaml` `normalised_baseline.equity_bridge_adjustments`** — the ten separation
   items as a structured list (id, description, amount_aud_m, direction, on_balance_sheet_at_anchor,
   treatment, + provided_for / probability): declared dividend 81.4, PH ARO gap 44 (126−82), PH
   inventory 80, transformation cost 12, Geelong 35, Gibson Island 97, transaction 11; receivables
   Perdaman 145×0.5, IPF 125×0.85, PH contingent 100×0.3. **Net 151.65** = workbook Equity Bridge B24.
2. **`translator.equity_bridge_adjustments_net_from_data(company_raw)`** — sums the block (in_full /
   gap_only / probability_weighted, signed by direction) and enforces the **§4.3 validator** (ValueError
   if any line lacks `on_balance_sheet_at_anchor`). Two new tests: net == 151.65 == the hand-typed
   golden; validator fires on a missing flag. **Suite 73 → 75.**
3. **Ratchet:** the block surfaced a faithful pre-existing generator hardcode — `build_cfgs.py` prints
   "IPF distribution +125" — so 125 gained a data home and the copy became visible debt. Baseline
   regenerated 119 → 120 (only `build_cfgs.py:125` added), tracked like the other generator hardcodes
   (clears when the generator consumes engine output at M5).

**M2 status:** WACC half wired (β 1.10 → 3.073); equity-bridge adjustments now data-driven (§4.2/§4.3).
Still hand-typed in `tests/dcf/golden/dnl_mt_inputs.py`: the per-year margin / gas / tax / capex glides,
stub timing, the revenue-growth chain, and the bridge run-rates (OCF 500 / capex 256 / period-A). Next
slice: a per-year-overlay schema (`margin_transformation`, `margin_gas_rolloff`, `tax_rate_glide`,
`capex_pct`), then a full `build_engine_inputs_from_data` assembling FcfEngineInputs end-to-end and
reproducing 3.073 with NO hand-typed constants.

---

## CHAT HANDOVER — 11 August 2026 (d) (M2 — WACC wired data→engine; DNL re-anchored to β 1.10)

Stephen's call (option 1): adopt the ratified β **1.10** and drive the discount rate from the data.
First end-to-end slice of M2 (`AssumptionSet → FcfEngineInputs`) — the WACC half. Pushed.

1. **`translator.build_wacc_from_inputs(inputs)`** — assembles a `WaccBuild` from the resolved
   layer-1/layer-2 data: β and ERP from the joined `wacc_build`, E/V weights from the §5.3-anchored
   equity/debt market values (6,390 / 1,260.8). Returns `None` for Ke companies (banks / CSL). The
   discount rate is now DATA-DRIVEN, not a hand-typed constant.
2. **DNL Muddle Through re-anchored to β 1.10.** Data-driven WACC = **8.877%** (β 1.10, E/V 83.5%,
   tax 0.30) → per-share **3.073** (EV 7,009, terminal 72.6%, −14.9% to market). This SUPERSEDES the
   β-0.95 workbook headline **3.484** as the production number. Two new tests in
   `tests/dcf/test_dnl_mt_ratified.py`: one pins the data-driven WACC (non-circular — ties the YAML);
   one pins the end-to-end ratified per-share 3.073.
3. **The β-0.95 workbook golden is KEPT** (`test_e2e_dnl_mt.py`, 20 assertions, 3.484) — its role is
   now the **engine-mechanics oracle**: it proves the engine faithfully reproduces the audited v6
   workbook when fed the workbook's own (β-stale) inputs, validating the mechanics independently of
   any figure the engine itself emits. Not the production headline. (Workbook v6 lives at
   `analyses/dnl/valuations/`; a β-1.10 workbook re-run could later give an INDEPENDENT oracle for
   3.073 — today 3.073 is the engine's own output under the ratified β.)
4. **Suite 71 → 73 green.**

**Scope honesty — wired vs still hand-typed.** Only the WACC/discount half is data-driven. The
per-year structural overlays still come from the hand-typed `tests/dcf/golden/dnl_mt_inputs.py`:
`margin_transformation` + `margin_gas_rolloff` glides, `tax_rate_glide`, capex step, stub timing,
the revenue-growth chain, and the whole Fertilisers-separation equity bridge (PH ARO/inventory,
Perdaman, Gibson Island…). Migrating those into a data-driven assumptions/linkage layer — a new
schema for per-year overlays + the equity-bridge adjustments, none of which exist in the YAML yet —
is the remaining (large) M2 build.

**Minor to reconcile later:** the workbook's WACC used blended statutory tax 0.275 on the debt leg;
the data's `normalised_baseline.tax_rate` is 0.30, so the data-driven WACC (8.877%) is a hair below a
0.275 build (8.90%). Reconcile when the tax layer is formalised.

---

## CHAT HANDOVER — 11 August 2026 (c) (CSL layer-1 circularity broken — M2 track, step 2)

Second M2-track step: broke the circularity in `data/financials/csl.yaml` (was
`base_year_status: workbook_reverse_engineered` — its "observed" layer-1 had been transcribed from
the very model it feeds). Structural fix, not a re-computation; **numbers unchanged**. Pushed.

1. **Layer-2 leak removed.** The `segments` block carried per-segment SCENARIO assumptions
   (`muddle_through_growth_path`, `growth_shape`, `growth_rationale`, `margin_uplift_cum_fy31`,
   `margin_uplift_rationale`, `muddle_through_cagr`) — pure judgment sitting in the observed file.
   Moved to `data/companies/csl.yaml` `normalised_baseline.segment_baseline` (layer 2, one entry per
   segment, verbatim). Layer-1 `segments` now holds observed only: `fy25_revenue`, `fy25_or_margin`,
   `revenue_share`, `industry_archetype`.
2. **Provenance re-attributed.** `base_year_status` flipped `workbook_reverse_engineered` →
   `disclosed_accounts_hand_curated`; `data_source` + `last_updated_note` rewritten to cite primary
   disclosures/feeds (FY25 disclosed segment accounts, 1H26 balance sheet, MarketScreener / Yahoo
   market data, EODHD / US Treasury) rather than `csl_muddle_through_valuation_v4.xlsx`.
3. **No schema change, no consumer impact.** `normalised_baseline` is a loosely-typed `dict` on
   `CompanyPositionFile`, so `segment_baseline` slots in with no model edit; nothing in
   src/scripts/generator reads the growth-path fields yet (M3/engine is where they get consumed). New
   test `test_csl_segment_assumptions_live_in_layer2_not_layer1` pins the split. **Suite 70 → 71.**

**Honest caveat.** This removes the *structural* circularity (assumptions out of the observed file)
and the *citation* circularity (workbook → primary sources). It does NOT independently machine-verify
the observed values against the filings — that stays pending Ben's EODHD pipeline; the file is now
primary-cited but still hand-curated (stated in the header).

**Aside found (NOT touched).** `data/companies/csl.yaml` `company_position` does not currently
validate against `CompanyPositionFile` (76 schema mismatches — `functional_currency_rationale`
missing, `industry_type` / `share_statistics` / `operating_result_share` extra, etc.). Pre-existing
and latent (no test runs CSL through `load_inputs`). Worth a dedicated pass before CSL is wired to
the engine (M3). My change is unrelated (0 of the 76 errors touch `normalised_baseline`).

**M2 track remaining:** the engine wiring proper — `AssumptionSet` → `FcfEngineInputs` (`linkage/`,
`assumptions/`, time profiles, derivations, segment aggregation). That is the large milestone; the
SSOT hygiene that gated it (DNL §5.3, WBC split, CSL circularity) is now **done**.

---

## CHAT HANDOVER — 11 August 2026 (b) (WBC layer split — M2 track, step 1)

First step of the M2 track: WBC split into layer 1 / layer 2, mirroring DNL and CSL. Clears the
last `KNOWN_STORED_DERIVED` offender, so **no company now stores a computed discount rate**. Pushed.

1. **New `data/financials/wbc.yaml`** (layer 1, LF): `coe_observed_inputs` — `risk_free_rate` +
   source, `beta_measured` 0.73 + source, and the 5-name `beta_peer_dataset` (CBA/NAB/WBC/ANZ/MQG;
   ANZ excluded-outlier, MQG informative-not-comparable). Hand-curated from Ben's 15 Jun 2026 EODHD
   feed; not yet machine-fed.
2. **`data/companies/wbc.yaml`** gained a top-level `normalised_baseline.coe_method` (layer 2): ERP
   0.05, `beta_selected` 0.75 + the full peer-triangulation rationale (carried verbatim), cluster
   0.72/0.75/0.80, active `beta` 0.75, `single_ke_discipline`, `discount_rate_basis`. As a bank it
   carries *only* the Ke method — no FCFF margin/capex/terminal fields (correct for the archetype).
   The old `company_position.bank_specifics.cost_of_equity_build` block is gone; layer-1 parts moved
   to financials, layer-2 to `coe_method`, and the stored **`cost_of_equity: 0.0805` deleted** (engine
   computes Re = 4.30% + 0.75 × 5.00% = 8.05%).
3. **Translator unchanged** — the generic coe path (`coe_observed_inputs` + `coe_method` →
   `cost_of_equity_build`) reconstructs WBC automatically; verified Re 8.05%, no `wacc_build`.
4. **Lint:** `KNOWN_STORED_DERIVED` now empty; new
   `test_wbc_split_reconstructs_cost_of_equity_build` pins the join. Value-keyed baseline regenerated
   **downward 120 → 119** (only `build_cfgs.py:0.0805` dropped — that hardcoded generator copy is no
   longer a stored-value duplicate; it is now a pure derived constant awaiting the M2 feed). **Suite
   69 → 70 green.** CRLF preserved on wbc.yaml (targeted diff 59/81).

**M2 track remaining:** (i) CSL layer-1 circularity — `data/financials/csl.yaml` is
`workbook_reverse_engineered`, so its "layer 1" is hand-curated from an export; break that so it is a
genuine observed feed. (ii) The engine wiring proper (`AssumptionSet` → `FcfEngineInputs`: `linkage/`,
`assumptions/`, time profiles, derivations, segment aggregation). The generator still hardcodes
`re0:0.0805` for the WBC UI (base tie 30.15); that gets consumed from the engine at M2/M5, not
hand-patched now.

---

## CHAT HANDOVER — 11 August 2026 (β free-input · DNL §5.3 share-count fix EXECUTED)

Two things shipped this session; both pushed.

**1. β is now a free input in the workbench (commit `1a28b1b`, pushed).** In "The rate you built",
the subject β was display-only (peer median, or Hamada-relevered median). Stephen's methodology is
that peers *triangulate* β and the owner *chooses* an appropriate value — not necessarily the
average/median. So β is now an editable field defaulting to the peer-derived value, overridable to
any number, flowing straight into Re. Peer median / relevered / documented judgment stay on screen
as reference, with a "↺ use peer-triangulated" reset when overridden. Generator-only change
(`gen_ui.py`: `bs.betaOv`, `effBeta()`, apply routes through `effBeta`). Default unchanged, so the
base tie held (DNL 3.48 / WBC 30.15 / CSL 203.83), netDebt 1512, `node --check` clean on all three.

**2. DNL §5.3 share-count fix EXECUTED in the data layer (this session's data-fix commit, pushed).**
This is the half that was decided-and-documented on 25 Jul but never applied to the source-of-truth
file. The *valuation* already used 1,770m (golden inputs, M1 engine and workbook all tie 3.484), but
`data/financials/dnl.yaml` still carried the stale EODHD feed (1,875.9m / phantom equity 6,802),
which the translator reads for the per-share divisor and the WACC weight — so M2 (yaml → engine)
would have silently reintroduced the ~6% equity-weight error. Now closed:

1. `share_statistics` — §5.3-compliant: `shares_outstanding: 1,770,000,000`,
   `shares_outstanding_at: 2026-03-31`, `shares_outstanding_source` note; the stale feed value kept
   as `shares_outstanding_feed_stale` for provenance.
2. `wacc_observed_inputs` — `equity_market_value` 6,802 → **6,390** (1,770m × 3.6061),
   `debt_market_value` 1,810 → **1,260.8** (31 Mar 2026 anchor, workbook B74). E/V now 83.5% (was
   79.0%), matching the golden. Rationale comment rewritten.
3. `derived_metrics` — anchor `net_debt: 1,260.8` @ `net_debt_at: 2026-03-31`; the FY25-reported
   1,809.8 (30 Sep 2025) preserved as `net_debt_fy25_reported`.
4. **§5.4 validator implemented** (`tests/test_ssot_lint.py::test_share_and_netdebt_anchor_dates_paired`):
   for any company declaring a §5.3 share anchor, `shares_outstanding_at` must equal
   `derived_metrics.net_debt_at` and a source note must be present. Generalised across
   `data/financials/*.yaml`.
5. Join test updated (now pins 6,390 / 1,260.8). **Full suite 68 → 69 green; M1 golden still ties
   3.484 (20 assertions); smoke-test WACC now E/V 83.5% off the 1,770m anchor.**

**One judgment call (flag for veto).** `derived_metrics.net_debt` moved from the FY25-reported
1,809.8 (30 Sep 2025) to the 31 Mar 2026 H1 anchor 1,260.8 — necessary because §5.4 needs
`net_debt_at` to be a real date matching the 31 Mar share anchor; stamping 2026-03-31 on a 30-Sep
figure would be false. FY25 preserved as `net_debt_fy25_reported`. **Valuation unaffected:** the
translator uses the companies-yaml *normalised* override (1,300 steady-state) for `base_net_debt`,
not `derived_metrics.net_debt`.

**Still open / next.** The generator/UI scenario re-anchor stays engine-driven and waits on M2 (the
six scenario values were calibrated on the old set, can't be hand-re-derived). M2 track: WBC split
(clear stored `cost_of_equity`), CSL layer-1 circularity, then wire `AssumptionSet` →
`FcfEngineInputs`. Ben still owes real peer gearings/tax + optionally the exact reported 31 Mar 2026
issued count (1,770m is currently back-solved).

---

## CHAT HANDOVER — 9 August 2026 (UI Workstreams A+C, C9, B — all shipped & pushed)

**Commit state (all pushed to origin/main; HEAD `107ef59`).** The five commits from the prior
session (`aafa878`…`408a2bb`) were already on origin — a stale local `origin/main` ref made them
look unpushed; a `git fetch` confirmed. Always fetch before trusting "ahead by N". This session then
added, in order:

1. `0ed7546` — **A+C content.** C6: richer world-scenario descriptions (lead paragraph + *Macro
   picture* + *What would move the world elsewhere*, from `data/scenarios/*.md`, shared across all
   three). C7: an industry-level snapshot (concentration / lifecycle / excess-return durability, from
   `data/industries/`) prepended to each Five-Forces `intro`. C8: position bullets regrouped under
   `thytag` sub-heads (content verbatim, reordered only). A1: **verified, no change** — detail already
   renders in place below the tabs (`openDetail`→`#detail`, `scrollIntoView({block:'nearest'})`,
   `skipScroll` on load).
2. `e4c0ea5` — **C9: discount-rate theory → global best practice.** Rewritten jurisdiction-neutral,
   **six** components, collapsed to **two strands** (Best practice / What we did). Dropped the
   Australia-centric IER framing (Stephen: the tool must read globally). Rf notes the **zero-coupon
   (spot) sovereign** as theoretically correct, 10y coupon benchmark as the proxy. **Gamma dropped
   from the default and gated** (`GAMMA_COMPONENT` in build_cfgs, appended only via
   `drtheory(did, gamma_did=...)`; dormant for DNL/WBC/CSL) — it's Australia- *and*
   infrastructure-specific. Mirrors the `multiples.leaseNeutral` gating pattern.
3. `ae503a5` — **`sandbox_cleanup.cmd`** (repo root) + CLAUDE.md operational-quirks note. Mount is
   create-but-not-delete → sessions orphan `*.bak` and `.git/*.lock.dead*`; the script clears them.
   Standing rule added: always surface the exact cleanup CMD as a copy-widget.
4. `107ef59` — **Workstream B: Five-Forces overrides now flow into the number.** Were saved to
   localStorage but disconnected. Now routed **generically by driver key**, **delta-from-assessed**
   (so the base tie is preserved), transitory forces as **FY27–31 year-paths PV-collapsed** for the
   reduced-form and **forward-compatible with M2** (the engine will consume the path natively).
   New: `_forces.impacts[]` data model; `forcesOffsets`/`valsWithForces`→`scVal` compute; numeric
   matrix cells + a "Routes to" column + a per-year path editor for transitory forces.

**Design decisions locked (Stephen):**
1. Discount-rate theory is global/jurisdiction-neutral; per-company "What we did" stays specific
   (DNL/WBC AUD, CSL USD) — legitimate, not Australia-centric.
2. Gamma is a gated optional component, not in the global default; reintroduce via the gate when an
   Australian-infrastructure archetype exists (don't build more machinery until then).
3. **Forces→driver routing is generic by driver key.** Principle: *if a company's Porter's-5-forces
   work implies it needs a driver its reduced-form lacks, add that driver.* Today's routing: DNL
   supplier→**gas** x-driver (path from the `gasRolloff` overlay `[0,0,−50,−100,−150]`); DNL
   new-entrants/rivalry→**g**; WBC supplier→ROE (**m**), rivalry→**g**; CSL supplier/rivalry→**m**;
   buyer/substitutes neutral everywhere.
4. Reduced-form stays an approximation; the faithful year-by-year flow-through is **M2**. The forces
   year-paths already live in the data model (`_forces.impacts[i].path`) for M2 to consume — no re-keying.

**Where things stand.** Workstreams **A and C are complete** (A1, C6–C9). **Workstream B** — the
Five-Forces wiring is done; the workbench spine (user scenarios, per-input overrides, global/
per-scenario toggle, live recompute, localStorage) was already built in prior sessions.

**Open / next (pick by appetite):**
1. **Workstream D** — β-workbench depth (add/deselect comparables, estimation-window toggle, index
   selection). Most data-dependent; leans on the mock `beta_data.py`.
2. **dnl.yaml §5.3 share-count fix** — `shares_outstanding_at` 2026-03-31, shares 1,770m + source;
   `equity_market_value` 6,802 → ~6,390. Moves E/V → WACC → valuations, so needs an **engine re-run**,
   NOT a hand-patch. β settled (1.10), so unblocked.
3. **WBC split** (clear stored `cost_of_equity` — last `KNOWN_STORED_DERIVED` offender); CSL layer-1
   circularity; §5.4 validator (`shares_outstanding_at == net_debt_at`). Then **M2** (wire
   `AssumptionSet` → `FcfEngineInputs`).
4. Ben still owes real peer gearings/tax (mock in `beta_data.py`) + optionally the exact reported
   31 Mar 2026 issued share count.

**Generator mechanics (unchanged, critical).** Edit `ui_prototypes/_generator/*.py` **sandbox-side**
via Python string replacement (the Edit tool corrupts these large files); `python3 build_cfgs.py &&
python3 gen_ui.py`; verify **node --check** on all three inlined scripts + base tie (**DNL 3.48 /
WBC 30.15 / CSL 203.83**) + **netDebt 1512**. Never hand-edit the generated HTML. Commit sandbox-side
(`mv .git/*.lock` aside; push with the `x-access-token` URL). Run `sandbox_cleanup.cmd` to clear
orphaned files. Stephen's UI drops AskUserQuestion prompts — use plain-text numbered questions.

---

## CHAT HANDOVER — 25 July 2026 (d) (UI: single WACC presented in the scenario interface)

**Committed + pushed `ed7e756`.** First UI-workstream slice on the DNL scenario interface, driven by
Stephen's "the UI defines what needs to be true" plan. Generator-only change (`gen_ui.py`) + the three
regenerated HTMLs; reduced-form base still ties (DNL 3.48), `node --check` clean for all three.

**Key finding (corrects an earlier read):** the workbench spine is ALREADY built and functional — user
scenarios (+ add), per-input overrides on all five drivers (sliders + editable number fields), a
global-vs-per-scenario "apply to all" toggle, live recompute (`setInput → scVal → computeVals`), and
localStorage persistence. So "make a driver live" was mostly done; the remaining work is presentation,
compute fidelity, and aligning with the settled conventions.

**What shipped this slice (all in the discount-rate / β area):**
1. Always-visible **"Discount rate" metric card** showing the single WACC (cost of equity for WBC/CSL),
   kept in sync on every recompute — the single rate is now *presented*, not buried.
2. The Discount-rate tab **auto-opens the β workbench** (was behind a second button), laid out in **two
   columns**: component inputs (Rf/ERP/α, index, window, unlever toggle) on the left; **"The rate you
   built"** + **"Apply this rate"** on the right.
3. Apply scope is two explicit **radios** — "to all scenarios" (single WACC, default) or "to this
   scenario only" (per-scenario override, flagged with a "· r X%" marker on that scenario's bar).
   Encodes the single-WACC ruling while keeping the per-scenario what-if Stephen wanted.
4. Clearer **unlever label** ("use asset betas: unlever peers, re-lever at DNL gearing D/E") + explainer.
5. **β-regression plots expand inline** under each comparable (toggle open/close, "slope = β" caption);
   removed the scroll-to-bottom scatter.
6. **Excel-export wording** aligned to the single-WACC discipline.

**Generator mechanics (critical):** edit `ui_prototypes/_generator/{build_cfgs.py, beta_data.py,
gen_ui.py}` SANDBOX-SIDE (the Edit tool corrupts these large files on this mount), then
`python3 build_cfgs.py && python3 gen_ui.py`. Verify every regen: extract the inlined `<script>` and
`node --check` it; confirm the reduced-form base ties (`computeVals(defaults)==cp.base`, DNL 3.48);
confirm WBC/CSL untouched. Never hand-edit the generated HTML. Stephen eyeballs the render (file:// won't
open in the sandbox), and his UI has shown disappearing AskUserQuestion prompts — prefer plain-text
numbered questions.

**Compute honesty (unchanged):** the browser reduced-form (`computeVals`) is a multiplicative sensitivity
model around the base case, NOT the real FCFF engine; the six scenario per-share values remain
generator-hand-calibrated. The real-engine swap is M2.

**Next on the UI (Stephen wants all three; A→C→B→D is the brief's suggested order):**
1. Workstream A + C — layout/content richness (longer scenario descriptions from `data/scenarios/*.md`,
   richer Five-Forces drill-down, discount-rate theory click-throughs from
   `design/reference/discount_rate_iers/`, detail-renders-below). Low compute risk.
2. Workstream B (rest) — extend the global/override + recompute pattern to other high-impact drivers; wire
   the Five-Forces overrides into the number (currently saved/displayed but disconnected).
3. Workstream D — β workbench depth (mostly built). Most data-dependent (mock `beta_data.py`).
Full 10-point brief: `design/ui_design_brief.md`.

---

## CHAT HANDOVER — 25 July 2026 (c) (β DECIDED = 1.10 · share-count fix still pending)

**β is settled.** Stephen ratified **β = 1.10** on 25 Jul 2026, on a *real-gearing* peer triangulation
(not the mock). Recorded in `data/companies/dnl.yaml` `wacc_method.beta_selection_decision`
(+ `beta_selected_decided_on` / `beta_selected_status: decided_owner_ratified`). **Value unchanged**
(was already 1.10) → value-neutral, 68 tests green, no re-run.

**The analysis (corrects the record).** Unlevering the comparable equity betas at *real* gearings
(Orica D/E 0.18, Yara 0.36, ICL 0.30) gives asset β ~0.93 (ASX) / ~0.98 (World); re-levering at DNL's
D/E 0.28 gives **1.11 (ASX) to 1.17 (World)** — at/above the raw peer median because DNL sits
mid-to-upper on leverage. Shaded to the top of a 1.05–1.10 range for DNL's lowest-in-set operating
leverage (~78% contracted book + long US gas contract) and dampened cyclicality → 1.10. **This
supersedes** the old "triangulation → 0.96–1.05, excludes 1.10" claim, which was a MOCK-gearing
artefact (`beta_data.py` gearings 0.45/0.35/0.40 overstated peer leverage and are internally
inconsistent with their own mfin). So 1.10 is defensible, not stale. Peer gearings are public estimates
(Orica net debt / Yara market cap to firm); Ben's rigorous EODHD pull still wanted but the call is
robust to sensitivity.

**STILL PENDING — the §5.3 share-count fix (the other half of the re-anchor pass).** `dnl.yaml` still
carries `share_statistics.shares_outstanding: 1,875.9m` and `equity_market_value: 6,802` (off the
phantom 1,884m). §5.3-compliant = 1,770m @ 31 Mar 2026 and equity ~6,390. Unlike β, this **does** move
the E/V weight → WACC → valuations, so it needs an engine re-run and is its own step (do NOT hand-patch
scenario values). β being locked unblocks it. Then WBC, remaining §8 items, M2.

---

## CHAT HANDOVER — 25 July 2026 (b) (share-count convention: already in methodology §5, now surfaced · β still open)

**Read this, then the CSL-split block below it.** After the CSL split (below), this session went deep on
DNL's β / share-count tangle and **landed the share-count half**. Key realisation: the anchoring
convention was *already written* — methodology §5 "Share-count discipline" — we simply hadn't surfaced
or enforced it, and I wasted several turns chasing a live figure the spec tells us to ignore.

**The convention (methodology §5).**
1. §5.1 — latest *reported* issued share count, paired with net debt at the *same* balance-sheet date;
   do not project the buyback forward.
2. §5.2 — rationale: an on-market buyback at fair value is value-neutral per share, so projecting it
   into the denominator (without walking net debt forward by the cash spent) double-counts.
3. §5.3 — practical: `share_statistics.shares_outstanding_at: 2026-03-31`, `shares_outstanding ≈ 1,770m`
   (back-solved from H1 NPAT ex-IMIs / EPS ex-IMIs, net of H1 buybacks); the `as_at` must match the
   net-debt anchor date.
4. §5.4 — validator: error if `shares_outstanding_at ≠ net_debt_at` (NOT yet implemented).

**So the answer to "what's DNL's share count" is ~1,770m at 31 Mar 2026** — the H1 anchor the workbook
already uses. The four rival numbers reconcile: **1,770m** (workbook / §5 anchor — correct); **1,772m**
(feed market cap 6,390.4 ÷ price 3.6061 — agrees, the feed's market-cap field was current); **1,875.9m**
(EODHD `shares_outstanding` in dnl.yaml — STALE); **1,884m** (behind `equity_market_value: 6,802` —
phantom, wrong). The live public count is **1,754.1m at 3 Jul 2026** (ASX Appendix 3G) — *post-anchor*
buyback, deliberately NOT used. DNL has an active buyback (expanded Dec 2025 to ≤250m shares / ~A$740m
through late 2026), which is exactly why §5 says anchor and don't chase.

**What shipped this session on this thread (documentation only — no numbers moved).**
1. **CLAUDE.md** — added cross-cutting convention 6 (share-count / net-debt anchoring, pointer to §5), so
   it sits in the "never violate" list read every session.
2. **design/single_source_of_truth.md §8 item 5** — annotated that §5 governs the anchoring date; the
   residual is enforcement (validator + missing fields + the non-compliant dnl.yaml numbers).

**NOT done — DNL data still violates §5 (belongs in the β re-anchor pass, NOT piecemeal).**
`data/financials/dnl.yaml` still carries `share_statistics.shares_outstanding: 1,875,912,826` (no
`shares_outstanding_at`, no source) and `wacc_observed_inputs.equity_market_value: 6,802.0` (off the
phantom 1,884m). The §5.3-compliant values are shares **1,770m @ 31 Mar 2026** and equity market value
**~6,390** (= 1,770 × 3.61, which equals the feed's own market cap). Left unchanged here because it moves
E/V → WACC → every scenario, and the standing rule is: don't hand-patch, or we create yet another
inconsistent set. It rides with the β decision.

**β itself — STILL OPEN, STILL STEPHEN'S CALL** (unchanged): proper triangulation ~0.96–1.05, excluding
both 0.95 and 1.10. Ben's residual is narrow: (1) real peer gearings/tax for the triangulation (mock in
`ui_prototypes/_generator/beta_data.py`); (2) optionally confirm the *exact* reported 31 Mar 2026 issued
count from the 1H26 half-year PDF — secondary sources (openbriefing, kalkine, marketscreener) didn't
yield it cleanly this session; the filing PDF is the place.

**The clean next action — the "DNL β re-anchor pass" (one focused chat).**
1. Stephen picks β.
2. Bring dnl.yaml into §5.3 compliance: `shares_outstanding_at: 2026-03-31`, `shares_outstanding: 1,770m`
   + source; recompute/retire `equity_market_value` (→ ~6,390, or derive rather than store).
3. Add `derived_metrics.net_debt_at` and implement the §5.4 validator (`shares_at == net_debt_at`).
4. Re-run; then re-anchor the generator/UI engine-driven (do NOT hand-patch scenario values).
Then WBC (clear its stored `cost_of_equity`), then the remaining §8 items, then M2.

---

## CHAT HANDOVER — 25 July 2026 (CSL layer split · lint tightened)

**Read this first.** This session (1) committed and pushed the DNL layer split + lint that was
left uncommitted at the 22 July (c) handoff, and (2) executed the **CSL layer split**, mirroring
DNL. Both are pushed. 68 tests green throughout.

**Commit state (all pushed to origin/main).**

1. `aafa878` — *SSOT: execute DNL layer split + add hardcoded-value lint*. This is the 22 July (c)
   work, finally in history. Committed and pushed sandbox-side (the PAT in `.github-token` was used
   for the push; `git push origin main` alone fails in the sandbox with no stored credential —
   inject the token URL).
2. `<this session's CSL commit>` — the CSL split below.

**THE CSL SPLIT — what shipped.** Proven value-neutral by the same adversarial audit as DNL:
**95 numeric leaves in, 93 out — only `computed_cost_of_equity` (0.0875) and `group_ebit_margin_fy25`
(0.275) removed, zero added, zero changed.** Translator rejoin faithful (all `cost_of_equity_build`
keys present, none extra, computed value absent).

1. **`data/financials/csl.yaml` (layer 1).** `normalised_baseline` block GONE. Replaced by observed
   blocks: `group_financials` (group_revenue 15,558 — Stephen's call: layer 1, observed disclosed
   accounts), `balance_sheet` (net_debt 9,100), `market_data` (price/fx/consensus), `share_statistics`
   (shares 478.9), and `coe_observed_inputs` (risk_free_rate, beta_measured + source, beta_peer_dataset).
   Header `last_updated` bumped to 2026-07-25 with a note that this file is `workbook_reverse_engineered`
   (still hand-curated from the v4 workbook, not yet machine-fed — refresh-safety aspirational, the
   circularity the protocol §3 flags).
2. **`data/companies/csl.yaml` (layer 2).** Gained a top-level `normalised_baseline` (sibling of
   `company_position`, same placement as DNL): corporate_unallocated, capex/da/terminal_capex pct,
   working_capital_change, tax_rate, restructuring_cash_to_come, terminal_ebit_margin, terminal_growth,
   plus a nested **`coe_method`** (ERP, beta_selected + rationale, market-implied note, active beta,
   discount_rate_basis). CSL discounts FCFF at the **cost of equity**, not WACC — hence `coe_method`
   / `cost_of_equity_build`, the mirror of DNL's `wacc_method` / `wacc_build`. (Stephen's call:
   full mirror of DNL, not the minimal delete-only variant.)
3. **Deleted `computed_cost_of_equity: 0.0875`** (stored layer-3 value; engine computes Re). Also
   **dropped `group_ebit_margin_fy25: 0.275`** (a self-described derived memo; concept survives in
   the group_revenue rationale prose). Removed the hand-typed "(8.75%)" from `discount_rate_basis`.
4. **`src/vcc_valuations/translator.py`.** `resolve_normalised_baseline` now also joins
   `coe_observed_inputs` (layer 1) + `coe_method` (layer 2) into `cost_of_equity_build`, alongside
   the existing wacc join. DNL path unchanged (no coe_* keys).
5. **Lint (`tests/test_ssot_lint.py`).** Removed CSL's `computed_cost_of_equity` from
   `KNOWN_STORED_DERIVED` (now only WBC's `cost_of_equity` remains as visible debt); emptied
   `known_unmigrated` in check 2 (CSL is split, so no company should carry a layer-2 block in layer
   1 now); replaced the old CSL-fallback test with `test_csl_split_reconstructs_cost_of_equity_build`.
6. **Baseline ratchet tightened 124 → 120.** Deleting 0.0875 and 0.275 from the register made four
   code copies stale (`wacc.py:0.275`, `beta_data.py:0.275`, `build_cfgs.py:0.0875` +`:0.275`) —
   the GOOD case (register source removed, not value drift), so regenerated **downward** via
   `scripts/ssot_lint_baseline.py`.

**PICK THIS UP NEXT (unchanged from 22 July (c), minus the now-done CSL split).**

1. **β decision + share count** — STILL OPEN, STILL STEPHEN'S CALL, and now the highest-value item.
   Live problem persists on DNL: `equity_market_value: 6802.0` is blessed as layer-1 observed but
   derives from 1,884 shares, contradicting `share_statistics: 1,875.9` — ~6.4% error in the equity
   weight. Blocked on Ben's reconciliation (feed's own market cap 6,390.4 ÷ 3.6061 = 1,772) and the
   real EODHD peer pull. Proper triangulation → ~0.96–1.05, excluding both 0.95 and 1.10.
2. **WBC** — clear its stored `cost_of_equity` (the remaining `KNOWN_STORED_DERIVED` offender) when
   WBC work comes up. No `data/financials/wbc.yaml` exists yet.
3. **Remaining §8 items** — layer-2 schema, valuation-date stamping, basis labels, supersession log,
   export proliferation, peer-data home.
4. **Then M2** (wire AssumptionSet → FcfEngineInputs). This protocol is adjacent to M2, not its
   front half.

---

## CHAT HANDOVER — 22 July 2026 (c) (SSOT protocol EXECUTED for DNL · CI fixed)

**Read this first, then (b) below it, then the spec.** This session committed M1, fixed CI, and
**executed the layer split for DNL** — the protocol in `design/single_source_of_truth.md` is no
longer just drafted, it is in force for one company with a lint guarding it.

**Commit state (all pushed unless noted).**
- `0acab99` — M1 engine + golden master + SSOT protocol draft.
- `009616a` — CI fix (root `conftest.py` puts `src/` on `sys.path`).
- **Uncommitted at handoff:** the DNL layer split + lint. Commit message drafted; `git add -A` is
  safe (`.github-token` is gitignored). Commit from Stephen's terminal.

**CI was failing — now fixed.** Two GitHub Actions emails after the M1 push ("Deploy Web
Playground: all jobs failed" + a Tests failure). Cause was **not** the push: neither workflow
installs the package and nothing put `src/` on the path, so every `import vcc_valuations` failed at
collection. Reproduced in a clean checkout (2 errors, 0 tests), fixed with a root `conftest.py`,
re-verified 63 → green. Two things still worth doing (not done): (1) `.github/workflows/deploy-web.yml`
doesn't deploy — its deploy step is a placeholder `echo`, so it just reruns tests under a misleading
name; (2) `test.yml` runs `--cov=models`, so all of `src/vcc_valuations` (i.e. M1) reports zero
coverage. Cosmetic: `setup.py` still says `author='Ben Watson'`.

**THE DNL LAYER SPLIT — what shipped this session.** Executed §3 of the protocol, proven value-neutral
by adversarial audit (50 leaves in, 49 out, only `computed_wacc` deleted, no value or rationale
changed; smoke-test output byte-identical bar one label line; 63 → **68 tests green**).

1. `data/financials/dnl.yaml` — the `normalised_baseline` block (was lines 42–199) is gone. What
   remains is `wacc_observed_inputs` (layer 1: `risk_free_rate`, `beta_measured`,
   `beta_peer_dataset_v0_6_backport`, `equity_market_value`, `debt_market_value`). Header comment +
   `last_updated` bumped to 2026-07-22 with a note that the file is *not yet* truly machine-refreshable.
2. `data/companies/dnl.yaml` — gained `normalised_baseline` (layer 2: margin, net debt, capex, tax,
   D&A, terminal growth) with a nested `wacc_method` (ERP, `beta_selected` + rationale + refresh
   action, active `beta`, cost of debt). Hand-authored; never machine-written.
3. `computed_wacc: 0.0882` **DELETED** — it was a stored layer-3 value derived from a twice-superseded
   β 1.15. (The engine computes WACC; nothing should store it.)
4. `src/vcc_valuations/translator.py` — new `resolve_normalised_baseline(inputs)` joins layer 2 +
   layer 1 back into the legacy `wacc_build` shape, so consumers are unaffected. `load_inputs` now
   passes `company_raw` and parses the company YAML once (was twice). CSL fallback: if
   `data/companies/<id>` has no `normalised_baseline`, it reads the old financials location.
5. `scripts/run_smoke_test.py` — repointed to `resolve_normalised_baseline`; docstring + header
   updated.
6. `src/vcc_valuations/schemas/company.py` — `CompanyPositionFile` gained
   `normalised_baseline: dict | None` (loosely typed; consumers reach it via the translator, not this
   model). Left loose until the layer-2 schema is specified (protocol §8 item 9).

**THE LINT (`tests/test_ssot_lint.py`, 5 tests + `scripts/ssot_lint_baseline.py` + baseline JSON).**
- **Check 1** — no stored derived value in *either* data layer (widened after audit: `computed_wacc`
  lived in layer 1, so a layer-2-only scan would have missed the very defect it targets). Excludes
  `market_data.*`/`share_statistics.*` (feed snapshots are layer 1 by definition). **Found two
  pre-existing offenders, recorded as visible debt in `KNOWN_STORED_DERIVED`:**
  `csl.yaml::…cost_of_equity_build.computed_cost_of_equity` and
  `wbc.yaml::…cost_of_equity_build.cost_of_equity` — clear each during that company's split.
- **Check 2** — no `normalised_baseline` left in a layer-1 financials file (csl.yaml exempt until split).
- **Check 3** — value-keyed ratchet: register scalars must not appear as literals in `src/`, `scripts/`,
  `ui_prototypes/_generator/*.py`; 124 pre-existing duplicates baselined, anything NEW fails.
  Regenerate downward only via `scripts/ssot_lint_baseline.py`.
- **Two join tests** pin the rejoined `wacc_build` and the CSL fallback.
- **Known lint limits (documented in-file):** value-keyed not path-keyed, so updating `beta` while
  leaving `beta_selected`/a peer's `beta_indicative` behind is invisible (needs the layer-2 schema to
  name the authoritative key). Scan scope is `.py` only — **not** the UI `.html`, `tests/`, `models/`,
  `.md`, `.xlsx`. `_is_scannable` skips 1900–2100 (years), <0.02, and integer-valued <100 — so β=1.0,
  g=1.5%, netdebt=1,950 are invisible. Several of the 124 baseline entries are coincidental collisions
  with generic constants (0.1/0.3/0.5), so routine edits can trip the stale-baseline assertion.

**Open, deliberately NOT done this session (each needs a call, none blocks the others).**
1. **CSL split** — mirrors DNL, but two judgement calls: is `group_revenue` layer 1 or 2, and how to
   split `cost_of_equity_build` (csl.yaml declares itself `workbook_reverse_engineered`, so its
   "layer 1" is hand-curated from an export — circularity to break). Clearing
   `computed_cost_of_equity` is part of this.
2. **WBC** — no `data/financials/wbc.yaml` exists at all; only `data/companies/wbc.yaml`. Clear its
   stored `cost_of_equity` during whatever WBC work comes next.
3. **β decision + share count** — STILL OPEN, STILL STEPHEN'S CALL. Now cheaper: method is registered,
   so a decision propagates via `resolve_normalised_baseline` instead of being retyped. Corrected
   analysis stands: proper triangulation → ~0.96–1.05, excluding BOTH 0.95 and 1.10. **Live problem:**
   `equity_market_value: 6802.0` is now blessed as layer-1 observed data but derives from 1,884 shares,
   contradicting `share_statistics` (1,875.9) in the same file — a ~6.4% error in the equity weight
   until the share count is settled.
4. **Peer-exclusion reasons + `capital_structure_rationale`** currently sit in layer 1 with the peer
   data; §2 arguably makes exclusion reasons layer 2. Left pending the §8 "where does peer data live"
   decision rather than pre-judged.
5. The other §8 items unchanged: workbook generator scope, valuation-date stamping, basis labels,
   supersession log, export proliferation, layer-2 schema.

**Then M2** (unchanged): wire driver-keyed `AssumptionSet` → `FcfEngineInputs`. Honest scoping from
(b): this protocol is *adjacent* to M2, not its front half. Computing β on demand needs a new
peer-triangulation derivation + a layer-1 peer feed (gearings/tax live only in the MOCK
`beta_data.py`).

---

## CHAT HANDOVER — 22 July 2026 (b) (single-source-of-truth protocol · β claim withdrawn)

**Read this before the block below it.** This session did **not** decide β. It re-diagnosed the
re-anchor problem as an *architecture* problem and drafted the protocol to fix it:
**`design/single_source_of_truth.md`** (draft, not in force, awaiting Stephen's review of §3 and §8).

**Stephen's reframing that started it.** The issue is not which number wins — it is that building
the UI produced multiple different calculations doing the same thing. He wants one-source-of-truth
baked in before any further UI work: whenever a number is needed, check whether we already have it.

**Root cause identified.** We stored *answers*, not *methods*, in a format consumers cannot read.
β was settled — in cell B71 of an `.xlsx`. Nothing in the system can read a spreadsheet cell, so
every consumer made its own copy. The coupling that proves the point: β depends on gearing, gearing
on equity market value, equity market value on the share count — so under a stored-method regime,
settling the share count *recomputes* β; under ours it silently leaves β wrong.

### ⚠ CORRECTIONS TO EARLIER BLOCKS — the notes below this one contain claims now known false

1. **The β re-levering claim made this session is WITHDRAWN.** An interim finding that re-levering
   the peer cluster vindicates the workbook's 0.95 and retires 1.10 as an error was **cherry-picked**
   (it quoted the lowest cell of a grid). Across both index bases and both candidate gearings the
   re-levered cluster median runs ~**0.96–1.05**, which **excludes both stored answers**. On the
   world index — the workbook's own stated convention for >30% non-AU revenue — it returns 1.01–1.05.
   **β remains open and remains Stephen's call**, exactly as the block below records.
2. **The drift is 4 quantities, not 8.** Genuine drift: β, share count, WACC, base EBIT margin.
   *Not* drift: revenue 3,400 vs 3,905 (continuing-ops vs incl. Phosphate Hill — already ruled on;
   4,139 is FY27, not a base); net debt 1,260.8/1,300/1,512/1,810 (four definitions); EV
   7,736.6/8,064/7,681.5 (DCF / reduced-form / market); leases 194.3 vs 211.5 (two dates).
   **Basis mixing, not stale copying, is the more persistent failure.**
3. **`dnl.yaml` is internally inconsistent.** `beta: 1.10` (:163) but `computed_wacc: 0.0882` (:189),
   whose own comment derives it from `4.30% + 1.15 × 5.00%` — a twice-superseded β. Also
   `beta_measured: 0.36` (:105) duplicates `market_data.beta: 0.359` (:341).
4. **1,884 is not generator-only** — `dnl.yaml:179` derives `equity_market_value: 6802.0` from it,
   working shown at `:182`. Retiring 1,884 means recomputing that.
5. **The feed contradicts itself on shares.** Market cap 6,390.4 at price 3.6061 implies **1,772m**,
   two lines from a stated `shares_outstanding: 1875.9`. Ben to reconcile.

### Decisions made this session

1. **One β and one WACC per company per valuation date.** Scenarios differ in cash flows, not in
   discount rate. Strict reading of cross-cutting convention 1; removes the β/gearing circularity.
   *Consequence:* the UI's per-scenario "assessed rate" behaviour (`dnl_scenario_interface.html:418`)
   is retired — note it already contradicts the same file's single-WACC claim (`build_cfgs.py:72,142`).
2. **Three-layer taxonomy:** observed data (layer 1) / method and selection (layer 2) / derived
   values (layer 3). Store the method, never the answer.
3. **The register needs no new file.** An earlier proposal for `data/method/` is **withdrawn** — the
   split already exists: `data/financials/` is machine-written (it holds the EODHD CSVs), and
   `data/companies/` is hand-written judgement. Judgement merely leaked into the wrong one.
4. **The workbook is an export, not a repository** (Stephen's ruling). It stays downloadable and
   formula-driven; `golden/dnl_mt_v6.json` becomes the pinned oracle in its own right.

### The one concrete migration (a split, not a move)

`data/financials/dnl.yaml` lines **42–199** (`normalised_baseline`) contain all three layers at once:
layer 2 (margin, net debt, capex, tax, D&A, terminal growth, β rationale) → move to
`data/companies/dnl.yaml`; layer 1 (risk-free rate, measured β, peer dataset, equity/debt market
values) → stays; layer 3 (`computed_wacc`) → **delete**. Consumers to repoint:
`src/vcc_valuations/translator.py:225`, `scripts/run_smoke_test.py:45,74`. `csl.yaml` same
(its block includes observed `shares_outstanding: 478.9`). **No `data/financials/wbc.yaml` exists.**
Caveat: `csl.yaml` declares itself `workbook_reverse_engineered`, hand-curated from an export — so
layer-1 purity is aspirational there and that circularity must be broken separately.

### Also found

- **`.github-token` was NOT gitignored** (untracked, never committed, but one `git add -A` from
  disaster). **Fixed this session.** Stephen has a new fine-grained PAT; old one should be revoked.
- `scripts/export_excel.py` writes EV/equity/per-share as literal values — breaches standing rule 1.
- A formula-driven workbook writer **partly exists**: `VCCXLSX` inside `dnl_scenario_interface.html`,
  with an `Ff()` formula constructor and Hamada formulas. Move it server-side rather than rebuild.
- `scripts/workbook_lint.py` already does orphan-input and terminal-continuity checks — the §5 lint
  extends an existing surface.
- `src/vcc_valuations/dcf/fcf_engine.py` carries no company data, only dataclass defaults
  (`wacc=0.085`, `terminal_growth=0.025`) which should arguably be removed so a missing input fails loudly.

### Next

1. **Commit M1 + the `.gitignore` fix** from Stephen's terminal. Still uncommitted, 63 tests green.
2. **Stephen reviews `design/single_source_of_truth.md`** — especially §3 (the split) and §8 (twelve
   open items, several needing his call).
3. **Execute the `normalised_baseline` split** + repoint the two consumers + the lint.
4. **Then** β and the share count — with the method registered, so the decision propagates instead of
   being typed into three places.
5. Then M2. Note the honest scoping: this protocol is *adjacent* to M2, not "the front half" of it —
   an earlier framing that was overstated. Computing β on demand needs a new peer-triangulation
   derivation and a layer-1 peer feed (gearings and tax rates live only in the MOCK `beta_data.py`).

---

## CHAT HANDOVER — 22 July 2026 (M1 engine · re-anchor decisions · IronCorp note)

**Read this first.** Built the **real per-year DCF engine** (build-plan step 10 / engine plan
milestone **M1**), engine-first slice: a single-segment industrial FCFF engine that reproduces the
audited DNL Muddle Through workbook **to the cent**. **NOT committed** (commit from Stephen's
terminal — delete `.git/index.lock` first if present). Supersedes nothing below; adds the engine.

**What shipped (all new files; `src/` had only Phase-3.5 stubs before):**

1. `src/vcc_valuations/assumptions/wacc.py` — `WaccBuild` relocated from `dcf/fcf_stub.py` per the
   engine plan §1.3 (single-discipline WACC, component build-up; `fcf_stub.py` left untouched so its
   tests still pass). New `src/vcc_valuations/assumptions/__init__.py` package.
2. `src/vcc_valuations/dcf/fcf_engine.py` — `FcfEngine.run(FcfEngineInputs) -> FcfDcfResult`. Real
   mechanics, not the reduced-form solve: fractional **stub** period (val date → first FY-end),
   **mid-period discounting from the valuation date**, per-year **margin glide** (base + transformation
   overlay + gas-roll-off overlay as separate rows, methodology §11), per-year **tax glide**, a **capex
   step** (transition→steady), **Gordon terminal** on the grown last-year FCFF, and a **granular equity
   bridge** (`EquityBridge`, incl. a `from_anchor` Period-A net-debt walk). Terminal-share >70% fires a
   **non-blocking** warning (owner decision R3). Single-WACC discipline is structural.
3. `tests/dcf/golden/_recalc.py` — reproducible oracle extractor (forces LibreOffice "always recalc
   OOXML" via a throwaway profile, dumps target cells → `golden/dnl_mt_v6.json`). The committed JSON is
   the oracle; the test needs no spreadsheet tooling. `tests/dcf/golden/dnl_mt_inputs.py` hand-resolves
   the DNL MT inputs from the workbook Assumptions sheet (each scalar cell-referenced; revenue-growth
   chain reproduced explicitly) — the M1 stand-in for the linkage/assumptions layers.
4. `tests/dcf/test_e2e_dnl_mt.py` — golden-master, **20 assertions, all pass**; line-level FCFF vectors +
   headline. **Full suite 63 passed, no regressions.**

**Golden result (ties audited `dnl_muddle_through_valuation_v6_2026-06-25.xlsx`):** revenue
1193.4/3609.3/3831.4/4067.2/4317.6/4583.3 · margin glide 14.7/15.9/15.6/15.1/14.6 · WACC 8.2755% ·
g 2.5% · PV explicit 1,950.7 + PV terminal 5,785.9 → **EV 7,736.6** · terminal share 74.8% · bridge
EV − netdebt@val 1,224.0 − sep-adj 151.6 − leases 194.3 = equity 6,166.6 ÷ 1,770 sh = **3.484** (−3.5%
vs market 3.61).

**⚠ KEY FINDING — workbook↔UI drift (decision needed).** The engine reproduces the **audited v6
workbook** (the plan's designated oracle): base revenue **3,400**→FY27 **3,609**, shares **1,770**,
granular bridge (1,224 + 151.6 + 194.3), **EV 7,736.6**. The **generator/UI MT block has diverged**:
re-based revenue (FY27 **4,139**), shares **1,884**, netDebt **1,512** lumped, leases **212**, EV
**~8,064** — solved so the reduced-form stream reproduces the 8,068 headline at ~3.48. **Both land at
~3.48 by construction, via materially different inputs.** So "EV 8,068" (reduced-form) ≠ the honest
bottom-up DCF EV 7,736.6. Wiring the engine to the UI (M5) forces a reconciliation: either (a) re-anchor
the workbook to the re-based revenue / 1,884 sh / 1,512 ND, or (b) pull the UI back to the workbook.
**Stephen's methodology call — not made.**

**Also (note 3.59 vs 3.48):** 3.59 was the *model's* pre-lease MT output (vs market 3.61), not a share
price; the lease re-anchor moved it to 3.484. The engine targets 3.484.

**Housekeeping:** `CLAUDE.md` "Tara Reid" git-author note **fixed** (verified author = Stephen Reid /
stephenreid90; `build_plan.html` header still cosmetically shows "Owner: Tara Reid"). Test-run quirk:
the mount desyncs file-tool writes from the bash/python view — `test_e2e_dnl_mt.py` had to be written
**sandbox-side** (Edit-tool write looked right to `sed` but Python compiled a stale copy). Prefer
sandbox-side overwrites for test/source files, as noted for the generator. Nothing committed from the
sandbox.

---

### Re-anchor: what was decided this session (and what is still blocked)

**Stephen's rulings.** (1) The **workbook is the single source of truth**; the UI/generator and
`dnl.yaml` derive from it. (2) The **revenue basis is LOCKED at the workbook's FY26 3,400
continuing-ops figure** (→ FY27 3,609). The multiples-tab re-base to ~3,905 from the 12–13 July
chat is to be **reverted**.

**Why — the Phosphate Hill reconciliation (the finding that settled it).** Reported and TTM
revenue *include* Phosphate Hill, which is being divested (sale to Mayfair, completion Q3 FY26);
the workbook's continuing-ops build *excludes* it. Evidence: FY25 reported 3,710.1 vs workbook
continuing 3,220 (gap 490); TTM-Mar-26 reported 3,905.4 vs workbook FY26 3,400 (gap 505). Both
gaps ≈ Phosphate Hill. So ~3,905 and 3,400 are **not comparable**, and last chat's "3,400 sits
~13% below the accounts" drew the wrong conclusion. Keeping PH revenue in the forward build while
the bridge *also* takes PH sale proceeds/ARO/inventory would double-count the same business.

**⚠ BLOCKED — the β fork gates the rest.** The generator re-anchor was deliberately **NOT
executed**, because EV depends on WACC, which depends on a genuine methodology fork:

- **Workbook:** β **0.95** (world-index MSCI World, Hamada re-levered; convention = world index
  for >30% non-AU revenue) → Re 9.05%, **WACC 8.2755%**, EV 7,736.6, MT 3.484.
- **`dnl.yaml` + the β-workbench:** β **1.10** (peer cluster Orica/ICL/Yara, v0.6 §3.5.3
  peer-triangulation, 17 June) → Re 9.80%, WACC ~8.68–8.82%.

Both are documented and separately built into artefacts (the β workbench is built around 1.10), so
this is Stephen's call, not a mechanical "workbook wins". **Pick β first**, then re-anchor
everything in one consistent pass. Also unresolved and riding along: **share count 1,770**
(workbook, paired to the 31 Mar 2026 net-debt anchor; ties to E = 6,390 = 1,770 × 3.61) **vs
1,884** (generator/`dnl.yaml`).

**Scale of the drift found (do not underestimate).** The generator carries a whole older
parameter set — β 1.10, WACC ~8.7%, "normalised EBIT margin 13.5%" (workbook base is 14.1%),
shares 1,884, netDebt 1,512 lumped, leases 212, EV 8,064 — plus last chat's re-based revenue.
`dnl.yaml` carries a *third* set (β 1.10, WACC 8.82%, E 6,802, D 1,810, shares 1,884). The five
non-MT scenario values and the `cp` slider model were calibrated on the old set and **cannot be
re-derived by hand** — they need the scenario engine (M2/M3). Deliberate decision: **do not
hand-patch**, or we simply create a fourth inconsistent set.

**Target once β is locked** (workbook basis, for reference): EV 7,736.6 · net debt @ val 1,224.0 ·
separation adjustments 151.65 · leases 194.3 · single bridge figure **1,570** · equity 6,166.6 ÷
1,770 sh = **3.484**.

**Process fix agreed (the durable answer to the drift).** The engine is the one calculator; the
workbook is the human-auditable oracle it reproduces (the `_recalc.py` golden master); the
generator and `dnl.yaml` should **consume engine output** rather than keep hand-typed copies, with
a lint for stray hardcoded valuation numbers and one recorded house pick per methodology choice.

### Also this session (non-VCC)

- **`note_to_ben_ironcorp_critique.md`** (repo root) — critique of Ben's 50-page IronCorp/deecalc
  brief, developed in staged parts and rewritten to the house voice. Core argument: being exact
  and re-runnable doesn't *find* a model's error, but deecalc is unusually well-placed to help
  find it — five concrete mechanisms. Stephen sent an edited, shorter version.
- **`design/writing_style.md` updated** — new "Register: notes to colleagues vs published prose"
  section (plain bullets, no heading scaffolding, no summary recap, don't justify the
  self-evident, warm sign-off, err simpler) and a refinement to pattern 6: cut a blunting caveat
  rather than appending it.

### Next

1. **Decide β (0.95 world-index vs 1.10 peer-cluster) and the share count** — this gates everything.
2. Then re-anchor the generator **and** `dnl.yaml` to the workbook in one pass, engine-driven.
3. Then M2: wire the driver-keyed `AssumptionSet` → `FcfEngineInputs` (`linkage/` + `assumptions/`:
   translation rules, time profiles, derivations, consistency, segment aggregation).
4. Then M3 (segment FCFF + CSL) — needs the binding-terminal-margin + terminal-capex=D&A path,
   already stubbed as a seam in `fcf_engine._terminal`.

---

## CHAT HANDOVER — 13 July 2026 (cash-flow tie + forward-multiples re-base)

**Read this first.** Two DNL pieces this chat, both verified, **NOT committed** (commit from Stephen's
terminal — delete `.git/index.lock` first; the sandbox can't unlink it). Supersedes nothing below; adds to it.

1. **Summary Financials — cash flow now articulates** (`build_cfgs.py` `_financials['cf']` rebuilt). Operating
   cash flow builds from net profit after tax + D&A + non-cash significant items + a working-capital line (the
   WC line ties to the balance-sheet current assets/liabilities); free cash flow = OCF − capex; then dividends
   + a combined financing line; **cash at end of year equals the balance-sheet cash line every year, incl. real
   FY25 = 647**. FY25 WC-&-other and financing lines are condensed (fold in non-cash demerger items, buybacks,
   net borrowings, STI movements) so it still ties. Foot note updated. Verified numerically (tie-check PASS) and
   in the rendered table.

2. **Multiples tab — three-basis toggle + revenue re-base.** Replaced the mislabelled "Forward / normalised" +
   "Reported FY25" with **FY25 underlying · FY26 forward · FY27 forward** (default FY26).
   - **FY25 underlying** = ex the ~AUD 200m demerger one-offs (operating-income basis: EBIT 484 not reported
     344; EBITDA 768), so the trailing multiple is meaningful.
   - **FY26 / FY27** show **our-build and consensus side by side** (consensus = invented mock, flagged pending
     the EODHD/broker feed); implied multiples compute on our-build so they tie to the DCF.
   - **Re-base = revenue LEVEL only.** Lifted the operating build to the clean post-demerger run-rate
     (FY26 ~3,905 = TTM to 31 Mar 26; FY27 ~4,139 at the established ~6% growth), replacing the old ~3,405
     reduced-form base that sat ~13% below the accounts. **The established margin glide is UNCHANGED**
     (baseMargin 14.1 + peerGap − gasRolloff → 14.7/15.9/15.6/15.1/14.6). *Stephen corrected an earlier draft
     where Claude invented a NEW 12.5%→14.5% margin — do not reintroduce a second margin assumption; only the
     revenue level moves.*
   - **Numbers:** FY25u 768/484/322 · FY26 836/551/372 · FY27 910/608/409 (EBITDA/EBIT/NI). Forward
     EV/EBITDA **FY26 9.65×, FY27 8.87×** (peers ~6.6–7.0×). **Headline UNCHANGED: MT 3.48, EV 8,068.**
   - **Mechanics:** peers are keyed `ttm`/`fwd` in `beta_data.py` and were **not** touched — instead each
     subject basis carries a `peerKey` (+ `peerGrow` on FY27) and `_earn` maps fy25u→ttm, fy26→fwd,
     fy27→fwd×1.055. build_cfgs `multiples.bases` + `dcfDetail.mt` re-based; `gen_ui` `_earn` + base box (consensus
     side-by-side) changed. All three CFGs valid JSON; `node --check` clean; WBC/CSL untouched.

**Context / diagnosis worth keeping.** DNL FYE = **30 September**; valuation anchor ~21 May 2026, so FY26 is the
current/stub year (mostly elapsed) and FY27 is the first full forward year — which is why the DCF starts its
explicit period at FY27. The old "Forward/normalised" basis was really underlying-FY25 mislabelled; the mt
operating build separately sat ~13% below the reported revenue baseline. Both now reconciled to the accounts
(`data/financials/dnl.yaml`, which designates TTM-Mar-26 ~3,905 the "cleanest post-demerger baseline").

**Git state.** Identity is **already Stephen Reid** — the CLAUDE.md "Tara Reid" note is **STALE** (worth
fixing in CLAUDE.md). Commit `87cf8dc` (lease workstream: §4.6 + v0.8 + gated EV/EBITDAR) is committed **and
pushed**. A mount glitch had truncated `WORKING_NOTES.md`, `architecture.md` and the methodology doc in the
working tree; **restored this chat by overwriting with HEAD content** (sandbox-side, since `.git/index.lock`
blocks `git restore`). Uncommitted now = this chat's cash-flow + re-base changes (`build_cfgs.py`, `gen_ui.py`,
`dnl_scenario_interface.html`) plus this WORKING_NOTES block. **Don't `git restore WORKING_NOTES.md`** — it now
carries this new block; just delete the lock and commit.

**Open / next.** Consensus figures are placeholders (replace when EODHD returns). FY26/FY27 our-build earnings
use only established assumptions but Stephen may refine. The reduced-form-to-EV reconciliation at the re-based
revenue is illustrative (real per-year engine = M1, still pending). Earlier threads still open: WBC/CSL rich
templates (bank + FX archetypes), real EODHD behind the β workbench, the lease data-contract fields.

---

## CHAT HANDOVER — 12 July 2026 (lease accounting, part 2: #2 + #6 DONE)

**Read this first.** Fresh chat picked up the two remaining lease items from the block below; **both now
shipped and verified, NOT committed** (commit from Stephen's terminal). Nothing else in the earlier blocks
changed.

1. **#2 methodology convention — DONE.** New **§4.6 Lease-normalisation convention (AASB 16 / IFRS 16)** written
   into `design/methodology/equity_bridge_and_valuation_mechanics.md` (§4.6.1 Approach A default · §4.6.2
   subject-consistency invariant · §4.6.3 two-ratio materiality gate shown on screen · §4.6.4 why cross-company
   is a multiples not a DCF problem · §4.6.5 house re-capitalisation → lease-neutral EV/EBITDAR, three knobs,
   gated to lease-heavy archetypes · §4.6.6 AASB 16 vs US GAAP ASC 842 · §4.6.7 DNL lease-light worked example
   3.59→3.48 · §4.6.8 data contract + auditor discipline test). Matched the doc's own technical register (not the
   Valuation Matters reader voice — this is an internal spec). **`architecture.md` bumped v0.7 → v0.8** with a
   full "Migration from v0.7 → v0.8" block (a/b/c) referencing §4.6; Version/Date/Status lines updated.

2. **#6 lease-neutral EV/EBITDAR peer basis — DONE, gated + dormant.** Generator now supports an EV/EBITDAR
   multiple on the multiples toggle, **gated on `MU.leaseNeutral`** (present only for lease-heavy archetypes).
   DNL/WBC/CSL carry **no** leaseNeutral block, so it's dormant for them (confirmed: `grep leaseNeutral
   cfgs_gen.json` = 0; the only hits are the schema-doc comment in build_cfgs.py). Mechanics: EBITDAR =
   EBITDA + rent; EV re-capitalised on a house rule (strip reported lease liability, add uniform rent ×
   `capMult`), applied identically to subject + every peer — neutralises tenure judgment and the
   AASB 16-vs-US GAAP EBITDA gap. Schema documented in a `build_cfgs.py` comment:
   `multiples.leaseNeutral = { capMult, peer, peerNote, note, subject:{ rent, leaseLiabInND } }` + each peer
   `mfin` gains `{ rent, leaseLiab }`.
   - **Implementation** (`gen_ui.py`, 7 string-replace patches, sandbox-side python + `ast.parse`, NOT the Edit
     tool): added `muMetrics()` (appends the gated EV/EBITDAR metric), `muEbitdar/muAdjBridge/muIsEV/muDen/
     muEVof/muBridge` helpers; unified `muImplied`/`muValue` through them (ev + evr + eq all one path);
     `muComp` computes peer `evebitdar`; comps workbench gains a Rent input row + EV/EBITDAR derived row + a
     house-rule note; base box shows EBITDAR; implied-by-scenario table + cross-check show Adj. EV / adjusted
     net obligations for the evr kind.

**Verified:** all three CFGs parse as valid JSON; none carry leaseNeutral (untouched); all three app scripts
`node --check` clean; DNL netDebt still 1512 (re-anchor intact). **EV/EBITDAR math proven on a synthetic
lease-heavy fixture** (`/outputs/fixture_ebitdar.js`, 13/13 pass): peer EV/EBITDAR by hand, peer median,
subject adjBridge/EBITDAR, implied@price, `muValue(muImplied(v))==v` round-trip at four values, cross-check
equity, and a no-regression check that the ev-kind metrics are unchanged. Not browser-eyeballed (file://
limitation) — Stephen to view; the evr toggle only appears once a lease-heavy company config exists.

**Quirks:** nothing committed from sandbox. Scratch files the mount won't let the sandbox delete —
`ui_prototypes/_generator/apply_r6.py`, `gen_ui.prelease6.bak`, `build_cfgs.prelease6.bak` — delete from
Stephen's cmd window. Confirmed again: **prefer sandbox-side python overwrite for gen_ui.py/build_cfgs.py**
(used 7 guarded replacements; no truncation).

**Lease workstream now COMPLETE** (tasks #1–#8 all done across the two chats). Next natural threads: the
WBC/CSL rich-template roll-out (bank + FX archetypes) and real EODHD data behind the β workbench + the lease
data-contract — but nothing lease-specific outstanding. Discuss before starting.

---

## CHAT HANDOVER — 12 July 2026 (lease accounting; swap at iter ~18)

**Read this first.** This chat scoped and largely built **lease accounting** (the parked-twice item). The
11 July block below still describes the broader UI state; this block supersedes it for leases. Detail lives in
the "Lease accounting — approach agreed, scope locked (12 July 2026)" section further down.

**What shipped — all DNL, verified, NOT committed (commit from Stephen's terminal):**

1. **Treatment agreed = Approach A** (leases are debt): reported post-AASB 16 earnings + lease liability in
   net debt. Materiality gate (two ratios, 10-15%), Moody's/S&P peer re-capitalisation for lease-heavy names,
   AASB 16 vs US GAAP divergence, and the data contract are all written up in the scope section below.
2. **DNL re-anchored** — leases folded into net debt; headline ~11c lower. New six:
   **MT 3.48 / Orderly 4.05 / AI Lag 3.37 / Fragmentation 2.52 / Disorderly 1.33 / Stagflation 1.17**
   (asymmetry unchanged 4.09). Touched: `dnl_scenarios_comparison_v4.xlsx` (explicit lease row; equity/
   per-share/deltas converted from literals to formulas), audited `dnl_muddle_through_valuation_v6_...xlsx`
   (explicit lease line from a new Assumptions input; misleading BS net-debt note fixed; 3.594 -> 3.484), and
   the generator (`netDebt` 1300->1512, both DCF bridges, net-debt drill-down, MT narrative; rich Excel + DCF
   table auto-follow `CFG.netDebt`). LibreOffice recalc + JSON parse + node --check all pass.
3. **Lease-materiality panel** in DNL's net-debt drill-down (ratios + on-screen 10-15% threshold +
   "Lease-light" verdict). **`workbook_lint.py` lease-basis check** (WARNs when leases are orphaned from the
   bridge; passes re-anchored v6, warns the pre-fix backup). **`_leaseContract`** mock data-contract block in
   the DNL CFG + a note for Ben in the scope section.

**Next in this workstream (fresh chat): #2 methodology write-up** (lease-normalisation convention into
`equity_bridge_and_valuation_mechanics.md` + architecture ref) **and #6 lease-neutral EV/EBITDAR peer basis**
(gated to a lease-heavy archetype flag; DNL/WBC/CSL untouched). Both fully scoped below.

**Housekeeping / quirks:** nothing committed from the sandbox. A stale git lock was moved aside to
`.git/index.lock.dead1` — delete it from cmd. The Edit tool truncated `workbook_lint.py` once mid-write
(restored via `git show HEAD:` + in-place overwrite, since the mount blocks unlink so `git checkout` can't
replace a file) — **prefer sandbox-side python overwrite for any source file bigger than a few KB.**

**Mechanics unchanged:** edit `ui_prototypes/_generator/` then `python3 build_cfgs.py && python3 gen_ui.py`;
DNL-only features gate on data presence (leaseMat / _leaseContract / richbook); verify JSON + node --check +
reduced-form/DCF ties on every regen; Chrome/file:// won't open locally, Stephen eyeballs.

---

## CHAT HANDOVER — 11 July 2026 (UI build-out chat, swap point ~iter 19)

Read this first for the current UI state. The dated entries further down hold the detail; the older
"Next session focus (25 June)" section below is now background.

**Where we are.** This chat built out the **DNL** scenario-interface prototype substantially, all through the
shared generator. Everything new is **DNL-first**; WBC and CSL are deliberately untouched for the new features
(gated — see below) and await their pass. Nothing was committed from the sandbox this session — commits
finalise from Stephen's terminal (the `.git` lock quirk); the generated HTML and generator sources are saved
on the mount.

**Shipped this chat** (edit `ui_prototypes/_generator/`, regenerate; mock-now/real-later where data is absent):

1. β-workbench opener moved to sit under "Beta — peer triangulation" (all three prototypes).
2. **Beta determinants** in the β workbench — financial leverage / operational leverage / cyclicality, with
   numbered method footnotes (¹–⁴) and asset β via Hamada. DNL only.
3. **Summary financials tab** (5-yr P&L / balance sheet / cash flow) — real FY25 as-reported, mock FY21–24. DNL only.
4. **Multiples tab** — implied-by-DCF + cross-check; EV/EBITDA · EV/EBIT · P/E; forward/normalised + reported
   FY25 basis. DNL only.
5. **Comparable-company multiples workbench** — editable, transposed comps sheet (replaced the old expander),
   multiples derived from underlying peer financials, median tied to the β peer selection. Basis now drives
   **peers and subject together** (like-for-like) — this was the last fix.
6. **DCF tab Narrative/Table toggle** — traditional per-scenario DCF that reconstructs the headline EV exactly
   (Δ 0), with drill-downs: real §11 operating build (revenue × margin → EBIT → NOPAT), net-debt breakdown,
   terminal-value calc. DNL only (richbook-gated).

**Next, in order:**

1. **Lease accounting** — Stephen's explicitly-flagged next issue, parked twice. Not yet scoped. Do this first.
2. **Roll the new DNL features to WBC and CSL** — statements, multiples tab + peer workbench, DCF table,
   determinants. Archetype-aware: WBC (bank) uses P/E + P/B and a dividend/excess-return build (no EV bridge);
   CSL is FCFF at Ke with USD→AUD 0.66. Needs the WBC/CSL rich templates (the older pending item).
3. **Real EODHD data** — replace the mocks (`beta_data.py` det/mfin + peer betas; statements FY21–24) once
   Ben's feed returns (currently down). The mock JSON shapes are the contract the real feed must reproduce.

**How to work in here (critical):**

1. **Never hand-edit the generated HTML.** Edit `_generator/` — `build_cfgs.py` (per-company data), `beta_data.py`
   (mock feed), `gen_ui.py` (scaffold + inlined JS) — then `python3 build_cfgs.py && python3 gen_ui.py`.
2. **Large-file edits corrupt via the Edit/Write tools** (`gen_ui.py` ~100KB, `build_cfgs.py` ~60KB). Edit them
   sandbox-side with python string-replace + `ast.parse` checks + `cp`; keep /tmp backups (this session's are
   `/tmp/*.bak*.py`).
3. **DNL-only features are gated by data presence**, not by code branches: `CFG.richbook` (DCF table),
   `CFG.beta.subject.det` (determinants), `CFG.multiples` + titles (multiples/workbench tab), `CFG.dcfDetail`
   (DCF drill-downs), `_financials` + titles (statements). Shared JS is inlined in all three HTML but stays
   dormant without the data/title. **Extending a feature to WBC/CSL = add the data + title, not new code.**
4. **Verify every regen**: extract each embedded `CFG`, JSON-parse it; confirm the reduced-form still
   reproduces each Muddle Through (DNL 3.59) and the DCF cascade ties (Δ 0); `node --check` the inlined app
   script. Chrome/`file://` won't open locally — Stephen eyeballs visually.
5. Mock data is always flagged in-UI and lives in the JSON shape the real feed must reproduce.

---

## Lease accounting — approach agreed, scope locked (12 July 2026)

The parked-twice lease issue, scoped with Stephen this chat. **Approach agreed; build not started
(pending the one open decision below).** Read this before touching leases.

**The problem in one line.** Leases touch the number in three places — the operating build
(EBIT/EBITDA/FCFF), the net-debt/equity bridge, and the multiples tab — and one convention must hold
across all three. DNL is in a latent *mixed* state today: reported post-AASB 16 earnings (rent already
replaced by right-of-use depreciation + lease interest) but net debt **excludes** the 212 lease liability
(the "narrow, AASB16 excl" definition). Numerator sits in the leases-are-debt world; bridge sits in the
leases-are-operating world.

**Agreed treatment:**

1. **Default convention — Approach A (leases as debt).** Keep reported post-AASB 16 earnings and add the
   lease liability into net debt so both sides agree. Chosen over de-capitalising (Approach B) because it
   uses reported numbers with least estimation and scales to lease-heavy names.
2. **Materiality gate — two ratios.** Liability ÷ EV (or lease-inclusive net debt); lease cost
   (ROU dep + lease interest ≈ cash lease payment) ÷ EBITDA. Threshold ~10–15% on *either* flips a company
   from "apply convention, show calc, move on" to "lease-sensitive". **Both ratios AND the threshold must be
   shown on screen**, per Stephen (not asserted). DNL is lease-light (liability ~2.6% of EV).
3. **DNL fix.** Fold the 212 into net debt so numerator/bridge agree — a ~11c / ~3% one-directional
   correction. Stephen pushed back on calling that immaterial: it's a *consistency* fix (not judgment), so
   we take it. No heavy machinery for DNL.
4. **Cross-company = a multiples problem, not a DCF problem.** In the subject's own DCF, earnings and the
   lease liability come from the same accounts under the same tenure assumption, so a longer/shorter term
   moves EV and the liability together and they offset at the equity line — the DCF discounts the real rent
   stream, so the accounting carve-up nets out. A multiple can't net it out (EBITDA is tenure-invariant but
   the liability that adjusts EV is tenure-dependent), so the distortion passes straight through.
5. **Aligning peers — Moody's/S&P house re-capitalisation (Stephen liked this).** Don't consume reported
   lease liabilities cross-company; rebuild from the underlying rent commitments on one house rule with three
   fixed knobs: (a) capitalisation method (uniform multiple, e.g. rent × 8, or uniform rate+term);
   (b) tenure definition (e.g. committed-to-first-break, or committed + standard renewal); (c) rent definition
   (incl. variable/turnover rent). Applied identically to subject and every peer. Surfaced as a lease-neutral
   **EV/EBITDAR** basis on the multiples toggle, **gated to lease-heavy archetypes** (DNL/WBC/CSL never see it).
   Same fix also neutralises the AASB 16 vs US GAAP divergence (see 6).
6. **AASB 16 vs US GAAP (ASC 842).** Balance sheet broadly aligned (both capitalise ROU asset + lease
   liability). Income statement / cash flow **not** aligned: AASB 16 is single-model (all leases → dep +
   interest, so all lease cost leaves EBITDA and operating cash flow); ASC 842 keeps operating leases as a
   single straight-line operating expense that stays *in* EBIT/EBITDA and operating cash flow. So identical
   economics report different EBITDA/OCF across standards. The uniform EBITDAR basis strips this out too.
7. **Subject-consistency rule.** Whatever tenure assumption sets the liability in net debt must be the same
   assumption behind the earnings figure — automatic on reported numbers; the trap is normalising one side
   without the other.
8. **Data contract (flag to Ben for EODHD).** Need three fields we can't do without: whether "total debt"
   includes lease liabilities, the rent / lease-cost line, the lease **maturity table** (to re-discount/
   re-capitalise on our own rule), and an IFRS-vs-US-GAAP flag per company.

**Build plan (tasks #1–#8):** lock notes (this) → methodology convention → lint consistency check → DNL
materiality panel + corrected bridge → [DNL headline re-anchor: OPEN DECISION] → gated EBITDAR basis →
mock lease data-contract fields → verify. Same generator mechanics as always (edit `_generator/`, regen,
verify; large edits sandbox-side + cp).

**DECISION (task #5) — RESOLVED: re-anchor everything now** (Stephen, 12 July). Headline moves down.

**Accounts check (Stephen asked "look in the accounts").** DNL's own statutory accounts aren't in the repo
(only our briefing/discussion PDFs). But `data/financials/dnl.yaml` (parsed FY25 statutory BS) lists
`capital_lease_obligations: 211.5` as a **separate** line from short-term (626.3) / long-term (1,238.9)
borrowings; the valuation's net-debt anchor is borrowings−cash = 1,218 (ex that lease line) + 82 = 1,300.
So the operative 3.59 **excluded** leases — re-anchor confirmed correct, no double-count. The v6 workbook's
Balance Sheet note claiming net debt "includes capital leases" was the misleading outlier (now fixed).

**Wiring reality found:** the three artefacts carried three different net-debt/share decompositions that all
reproduce 3.59 — `comparison_v4` (net debt −1,224 val-date + bridge −151.65, shares 1,770, a **hard-coded
values dump**), audited `v6` (D 1,260.8, shares 1,770, **formula** model), and the UI (EV 8,064, net debt
1,300, shares 1,884, reduced-form). Period-consistent lease figures: 194.3 (H1 val-date, workbooks) / 212
(FY25, UI). Both bases round to the SAME re-anchored set.

### Re-anchor DONE + verified (12 July) — tasks #4, #5 complete

Re-anchored six DNL scenarios (constant −~0.11 shift; **asymmetry ratio unchanged 4.09**):
**MT 3.48 · Orderly 4.05 · AI Lag 3.37 · Fragmentation 2.52 · Disorderly 1.33 · Stagflation 1.17.**

1. **`dnl_scenarios_comparison_v4.xlsx`** (operative source): added explicit `Less: AASB 16 lease liabilities
   (−194.3)` row to DCF Outputs; **converted equity-value + per-share + vs-market/vs-MT cells to formulas**
   (were literals); Asymmetry per-share now references DCF Outputs. LibreOffice recalc: 3.48/4.05/3.37/2.52/
   1.33/1.17, asymmetry 4.09. Backup `/tmp/lease_bak`.
2. **`dnl_muddle_through_valuation_v6_...xlsx`** (audited formula model): added explicit lease line from a new
   Assumptions input (B108 = 194.3) into the Equity Bridge (per-share 3.594 → **3.484**); **fixed the
   misleading BS!C20 net-debt note** (now: borrowings less cash, ex-leases; leases deducted explicitly per
   Approach A). LibreOffice recalc clean (the two DCF Build-up (v5) error cells are pre-existing, unrelated).
3. **Generator** (`build_cfgs.py`, 20 ASCII-anchored patches, `ast.parse` OK): scenario bars, `cp.base` 3.48,
   `netDebt` 1300→**1512** (+ `netDebtExLeases` 1300, `leaseLiab` 212); compact + detailed DCF bridges gain an
   explicit lease line (equity 6,764→**6,552**, /share 3.48); net-debt drill-down array gains
   `Add: AASB 16 lease liabilities 212` and note flips "excluded" → Approach A / included; MT narrative "Why
   AUD 3.48? … modestly below market (~4%)".
4. **Materiality panel (task #4)** — `dcfDetail.leaseMat` data + a renderer in `gen_ui.py`'s net-debt
   drill-down: shows liability, ÷EV (2.6%), per-share impact (AUD 0.11, ~3% of value), lease cost ÷EBITDA
   (~7%/6% rep/fwd), the **10-15% threshold on screen**, and the verdict **Lease-light → Approach A, no
   lease-neutral peer basis needed**. Gated on `dd.leaseMat` (DNL only).
5. **Rich Excel + DCF table** read `CFG.netDebt` → auto-use 1,512 → 3.48 (no hard-coded 1,300 anywhere).

**Verified:** all three CFGs parse as valid JSON; DNL scenarios/base/netDebt/leaseMat correct; WBC/CSL carry
no leaseMat/netDebt (gated, untouched); UI bridge (8064−1512)/1884 = 3.48; workbook recalcs tie; `node
--check` passes all three app scripts. Not browser-eyeballed (file:// limitation) — Stephen to view.

### #3 (lint) + #7 (data contract) also DONE this session (12 July)

- **#3** — `scripts/workbook_lint.py` gained `check_lease_basis()`: flags lease liabilities sitting on the
  balance sheet but not wired into net debt / the equity bridge (the pre-fix mixed-basis state). Verified:
  new v6 -> INFO "basis consistent" (Assumptions!B108); pre-fix backup -> WARN. **Quirk hit:** the Edit tool
  truncated this file mid-write; restored via `git show HEAD:scripts/workbook_lint.py` + in-place overwrite
  (the mount blocks unlink, so `git checkout` can't replace a file). Left `.git/index.lock.dead1` (moved
  aside per the standing lock workaround) - Stephen can delete it from his own cmd window.
- **#7** — `_leaseContract` mock block added to the DNL CFG (dormant, DNL-only): accountingStandard,
  totalDebtIncludesLeases, leaseLiability, annualLeaseCost, incrementalBorrowingRate, leaseMaturityUndisc
  (year bands), contractNote. All three CFGs still parse; WBC/CSL carry none.

**Note for Ben (EODHD feed) — carry per company:** (1) whether reported total debt includes AASB 16 lease
liabilities; (2) the annual rent / lease-cost line (RoU depreciation + lease interest); (3) the undiscounted
lease-maturity table (to re-capitalise peers on a uniform house rule); (4) the accounting-standard flag
(AASB 16 / IFRS 16 vs US GAAP ASC 842).

**Remaining (fresh chat): #2 methodology convention** (equity-bridge doc + architecture ref) **and #6
lease-neutral EV/EBITDAR multiples basis** (gated to lease-heavy archetype). Both scoped above; safe to hand off.

**Nothing committed from the sandbox** — workbooks + generator + lint changes saved on the mount; commit
finalises from Stephen's terminal.

---

## Next session focus (fresh chat — opened after 25 June 2026)

Two workstreams, in order:

1. **Build out the user interface.** Stephen has many ideas for the scenario-valuation
   interface. Start from the three prototypes in `ui_prototypes/`
   (`csl_`/`dnl_`/`wbc_scenario_interface.html`) and the locked concept in the "Interface
   prototypes" section below. **Stephen's full 10-point UI brief + all design decisions are captured in
   `design/ui_design_brief.md` (25 June 2026) — read that first for this workstream.** It turns the
   interface from an illustrative viewer into a live modelling workbench (user-defined scenarios,
   per-input overrides, faithful browser-side reduced-form, Excel formula-workbook download, a
   cost-of-capital/beta workbench, deeper content from data/scenarios|industries|companies, and
   discount-rate theory from the IERs now in `design/reference/discount_rate_iers/`). First move:
   iterate the prototypes live against the brief. Note: CSL now has a full six-scenario set (`csl_scenarios_comparison_v2.xlsx` +
   thesis + discussion doc), so its interface bars can be made real like DNL/WBC (the
   csl_ prototype still shows only Muddle Through calibrated with placeholders).

2. **Decide the programming boundary — where AI/analyst judgment enters vs where it is
   mechanical.** After the UI, work through `design/engine_implementation_plan.md` (steps
   6+10) and mark each part as deterministic code or human/AI judgment. Rough seed:
   *mechanical* = derivations/identities, discounting, segment aggregation, consistency
   checks, the workbook lint; *judgment/AI* = scenario calibration, Five Forces positioning,
   driver direction×magnitude×confidence, the narratives. This decision shapes how the
   `linkage/` + `assumptions/` layers get built.

**State at handoff (main f9d2b02, all pushed):** CSL finished to WBC parity; methodology
at **v0.7** (accepted, folded into architecture.md); engine implementation plan written and
**M0 settled** (R1 done — CSL `financials.yaml` + 3 impact matrices authored; R5 — CET1-binding
payout, canonical WBC MT oracle **30.28**; R3 — terminal-share validator stays a non-blocking
warning). Engine **not yet coded** — M1 (DNL Muddle Through vertical slice, oracle AUD 3.59) is
the first build when chosen. β held at 0.85 for CSL by decision (repeatable framework).

---

## UI build — Workstreams A + C done (10 July 2026)

First live iteration of the modelling-workbench brief (`design/ui_design_brief.md`). Did the two
low-risk workstreams (A layout + C content) and folded CSL into the generator; **B and D not started**
(next). Everything runs through the shared generator now.

### Architecture decision (Claude's call, Stephen delegated it)
**Evolved the shared generator and folded CSL in** — rejected hand-editing three HTML files. The brief's
trajectory (shared reduced-form calculator, user scenarios, beta workbench) is mostly *shared engine* +
*per-company data*, which is exactly what `_generator/` separates. "HTML is the contract" still holds:
the generated HTML is the self-contained spec; the generator keeps three instances in sync. CSL was the
last hand-built divergence — now gone.

### What changed
1. **A — detail renders inline.** The dark full-page modal (`#overlay` at top) is removed. "Learn more →"
   and the explore tabs now expand the full detail in a `.detailcard` **directly below the panel, in
   place** (`#detail`), scrolling gently (`block:'nearest'`). This is the editing-surface pattern for B.
2. **C6 — longer world-scenario descriptions.** Shared `WORLD_DESC` (6 scenarios, from `data/scenarios/*.md`)
   now heads the world detail as "The world", with the company transmission narrative under "What it means
   for X".
3. **C7 — richer Five Forces.** Each force now shows the **industry-level rating + one-line rationale**
   (from `data/industries/*.yaml`) alongside the company-vs-industry position and impact. `forces_table`
   rows are now 6-element: `[force, ind_rating, ind_rationale, position, impact, mechanism]`.
4. **C9 — discount-rate theory click-throughs (the flagship of C).** Seven native `<details>` panels
   (Rf, ERP, beta, cost of debt, gearing, gamma, WACC-vs-CoE), each with **proper approach / what the IERs
   show / what we did (VCC)**. Grounded in the four IERs in `design/reference/discount_rate_iers/`
   (Oil Search/Santos, Woodside/BHP Petroleum, Universal Coal — real concluded WACCs quoted; Realm is a
   *supplementary* IER with no CAPM build-up, so used only for method/control-premium points).
5. **CSL bars made real.** CSL's six scenarios are now live from v4 / comparison v2 (AUD, USD-functional
   model at 0.66): Orderly 237.29 / **MT 203.83** / AI Lag 198.53 / Disorderly 174.79 / Fragmentation
   168.23 / Stagflation 159.90; broker bar 136 sits **below all six** (the §16 puzzle, on purpose).
   Market 105.53; terminal-% 75%; asymmetry 1.31×. Replaces the stale v3 placeholders (141.78/214.82).
   CSL discounts FCFF at cost-of-equity 8.75% (not a WACC) — flagged in its theory panels as a simplification.

### Verification (all pass)
Each generated HTML's embedded `CFG` parses as valid JSON (so the browser parses it); the browser-side
reduced-form reproduces each Muddle Through base **exactly** at default sliders (DNL 3.59, WBC 30.15,
CSL 203.83); 7 theory panels + 6 world descriptions + industry-forces column + all-real narratives present
in all three; inline `#detail` present, dark modal gone. Numbers traced to the workbooks/thesis by two
research subagents. (Browser visual check not done — the Chrome tool forces https:// and won't open local
file:// paths; Stephen to eyeball on review.)

### Mount-truncation quirk bit hard this session
The Cowork file-write tool truncated **both** `build_cfgs.py` and `gen_ui.py` mid-write (at ~18KB / line
119 and line 163 respectively) — the WORKING_NOTES 25-June quirk. Recovered by keeping the clean disk head
and appending the remainder via a quoted bash heredoc to `/tmp`, compile-checking, then `cp`-ing onto the
mount. **Lesson for large source edits: build sandbox-side + cp, don't trust large mount writes.**

### Next on the UI (unchanged order): B then D
- **B** — user-defined scenarios ("+" bar), per-input overrides everywhere (global value + per-scenario
  override), editable Impact column on forces, editable assumptions, faithful browser-side reduced-form,
  Excel formula-workbook download, localStorage persistence. The `#detail` panels are now the editing surface.
- **D** — the beta/cost-of-capital workbench (the flagship; EODHD JSON data-contract; the AI-vs-mechanical
  boundary decision). The discount-theory panels + CSL's correct-currency-index point set this up.

## UI feedback + Workstream B increment 1 (10 July 2026, same session)

### Feedback applied
**Discount-rate theory panels degeneralised.** Stephen: the IERs were his private good-practice
reference, not to be cited in the UI. Middle panel relabelled "In market practice" (was "What the IERs
show"); all report/firm/deal names removed (Grant Samuel, KPMG, Deloitte, Oil Search/Santos, Woodside/BHP,
Universal Coal, Realm) — substance and representative ranges kept. Verified zero proper-noun leaks in all
three HTML. Commit `534f4d5`.

### B increment 1 — user-defined scenarios (the workbench spine)
**"+ add your scenario"** now works: clones Muddle Through's inputs, user names it, a new **user-coloured
bar** appears, and the top-5 value drivers flex it live via the browser-side reduced-form. Selecting a user
bar loads its inputs into the sliders and the metric cards; a "×" deletes it. **Persisted in localStorage**
per company (`vcc_userscen_<TICKER>`). Built-in scenarios stay read-only (their values are workbook figures,
not reduced-form) — selecting one greys the sliders with an "exploring … read-only" note. The world-detail
for a user scenario shows a live overrides-vs-MT table.

Model: `target` = 'live' | user-id | null; sliders always drive the current editable target; `liveVals`
holds Muddle Through so switching targets preserves each scenario's edits. Verified in node: CFG parses as
valid JSON, reduced-form reproduces each base exactly, and moves correctly (+1% Re lowers, +0.5% g raises).

**B increment 2 done (10 July 2026):** the value-material inputs are now editable from the
**Assumptions** tab as typed number fields (two-way synced with the sliders and the live value); the
**Five Forces Impact column is editable** for user scenarios (stored per scenario as an annotation — flagged
as not-yet-feeding-the-number until the engine lands); and a **"apply to all editable scenarios (global)"**
toggle lets an input change hit every reduced-form scenario at once or just the selected one (points 3, 4-at-Re-level,
5). Verified in node: global propagation hits all editable scenarios, per-scenario overrides stay isolated,
directions correct. Structured `forcesData` now shipped in each CFG so the interactive forces table can rebuild client-side.

**Still on B (increment 3, next):** the Excel formula-workbook download; component-level discount-rate overrides + the "advanced / show all
inputs" long tail; then **D** (beta workbench).

### Iteration tracking
Stephen wants to swap chats ~every 20 iterations. Rough count this session: ~6 exchanges in.

## Workstream D — beta / cost-of-capital workbench (10 July 2026, MOCK data)

Built the flagship module against a **mocked EODHD-shaped JSON contract** (Stephen: mock for now, source
from Ben's pipeline in time). The contract lives in `ui_prototypes/_generator/beta_data.py` and ships inside
each CFG as `cfg.beta`; the synthetic scatter points are rescaled so each point cloud's OLS slope equals the
stored beta exactly, so scatter and beta are mutually consistent. **This JSON shape is the spec the real
pipeline must reproduce.**

Opened from the Discount-rate detail ("β / cost-of-capital workbench →"). Covers Stephen's 8(a)–(k):
Rf/ERP/alpha inputs (a,j); per-comparable levered+unlevered betas and the subject (b,k); "why comparable"
expanders (c); add from a candidate pool (d) and "find more comparables" with rationale-to-accept (e, the
AI/judgment step); select/deselect checkboxes (f); index selector — ASX 200 / MSCI World, or S&P 500 / World
for CSL (g); a scatterplot with regression line per comparable (h); weekly·2y vs monthly·4y estimation-window
toggle (i); unlever→relever at a target D/E (k, hidden for banks). Aggregates selected peers → median levered
(or relevered) β → Re = Rf + β×ERP + α → implied WACC (DNL) or cost of equity (WBC/CSL), with an **"apply to
the discount-rate slider"** button that closes the loop into the reduced-form value. Prominent **MOCK DATA**
banner throughout.

This is the tangible place the **AI-vs-mechanical boundary** lands: the regression, unlever/relever and
aggregation are *mechanical*; comparable selection + "find more comparables" rationales are *judgment/AI*.
CSL's subject row carries the measured-β 0.094 note with the steer to switch the index to S&P 500 / MSCI World
— the correct-currency point, made visible.

Verified in node: full CFG (incl. beta + all scatter points) parses as valid JSON; peer-median → Re → implied
discount math correct (DNL median β 1.10 → WACC 8.62%; WBC 0.76 → Re 8.10%; CSL 0.80 → Re 8.50%, each shown
against the documented judgment β); scatter slopes equal stored betas. DOM interactions reviewed, not
browser-tested (the Chrome tool here won't open local file:// paths — Stephen to eyeball).

**Outstanding on the UI:** the **Excel formula-workbook download** (B increment 3 — still a stub button;
needs an inlined xlsx writer to stay self-contained, or the Python side) and the "advanced / show all inputs"
long tail. Then the real EODHD data behind D. Iteration count ~9 this session.

## UI — points 2, 3, 4 reworked per Stephen's feedback (10 July 2026)

Stephen's clarifications drove a core-engine unification (commit follows).

**Point 4 "take it all the way" — every scenario is now editable, anchored at its assessed value.**
Rebuilt the model: each scenario (our six world cases *and* user scenarios) carries its own editable input
set (`vals`) and an `anchor` = its assessed value; its bar = `anchor × reduced-form-ratio(vals)`, where
ratio = 1 at the assessed defaults. So you can override *anything* on a per-scenario basis, or globally via
the "apply to all editable scenarios" toggle; **↻ reset restores the assessed case**. Overridden scenarios
get a ✎ marker on their bar and an "you've adjusted this case — value now X vs assessed Y" note. Built-in
scenarios are no longer read-only — the assessed cases are just the defaults. Broker stays a reference line.
World-case overrides + user scenarios persist per company in localStorage (`vcc_ws_<TICKER>`).

**Point 2 — per-scenario cost of capital.** The β workbench's "apply to the discount-rate slider" now writes
to the *active* scenario's discount rate (Re/WACC), so each scenario can carry its own cost-of-capital build.

**Point 3 — Five Forces impact restated honestly.** Replaced the single editable "Impact (yours)" column
(which confusingly implied a flow it didn't have) with: the **assessed** impact column, plus a **per-scenario
override matrix** (a column per editable scenario, each cell editable, defaulting to the assessed impact).
Explicit note that the company-vs-industry position is structural (same across world cases) and that in this
prototype the bars come from the calibrated/reduced-form cases — a future engine will make these impacts flow.

Verified in node: valid JSON; ratio(defaults)=1 so every assessed anchor is preserved (MT 3.59 / Stagflation
1.28 etc.); per-scenario edit moves only that scenario (Stagflation +1% Re → 1.28→1.13); global propagates;
no leftover state vars; 51 functions/file, consistent. DOM reviewed, not browser-tested here.

**Still open (Stephen's list):** 8(e) free-text "add any comparable" + "search wider" (he couldn't find the
existing add-behind-find-more; wants free-text + broader search); deepen DNL/WBC **company position** from
data/companies (point 9); the **Excel formula-workbook download**; real EODHD data behind the β workbench.
Iteration count ~11 — a chat swap is due within a couple more exchanges.

## UI — 8(e) free-text/wider comparables + 9 deepened positions (10 July 2026)

**8(e).** β workbench now lets you **add any company you name** (free-text name / ticker / estimated β → synthetic
scatter, selected) — addressing "I couldn't find where to just add a company". Plus a **"search wider"** button
revealing a second, broader candidate tier (`candidates2` in beta_data, ~3 adjacent names per company with weaker
rationales) alongside the original "find more comparables". `addCand` generalised to `addCandObj(cd)`; shared
`candRow` renderer. Still mock data.

**9.** DNL and WBC **company position** deepened from data/companies (9 sourced bullets each, was 4/3): DNL adds the
switching-cost moat (200+ on-site units, ~78% contracted), Orica peer-gap arithmetic, product/customer mix,
Louisiana execution weakness, and full balance sheet (2.12x ND/EBITDA, liquidity, payout); WBC adds segment mix
(consumer/business/institutional/NZ), the +8bps deposit edge, ROE-drag decomposition, full capital stack (Total
Capital 21.5%, AT1 8.5bn, RWA 458bn), credit anchors and dividend/buyback specifics. CSL position already deep (6).

Verified: valid JSON, positions render 9/9/6 bullets, candidates2 + free-text + wider all wired, files close.

**Remaining UI:** the **Excel formula-workbook download** (still a stub); real **EODHD data** behind the β workbench
(replace beta_data mock). Iteration ~12 — swap chats now / next exchange.

## UI — pre-swap polish: build-up drill-downs, open-all, no-snapshot, beta stats (10 July 2026)

Four asks from Stephen before the chat swap:
1. **Valuation build-up drill-downs.** Each line of the DCF/valuation build-up is now a click-to-expand
   `<details>` showing its make-up: EV → PV explicit FCFF + PV terminal (+ the driver inputs); net debt →
   the balance-sheet items and equity-bridge adjustments; equity value → the arithmetic; etc. Structured
   `dcfRows`/`dcfIntro` per company in build_cfgs (DNL 5 rows, WBC 7, CSL 9), rendered as disclosure rows.
2. **"⊕ open all" tab** in Explore the Build-up — renders every section stacked (each in its own card) and
   wires all the interactive bits (editable assumptions, forces matrix, β workbench opener).
3. **Snapshot removed.** Clicking an Explore tab now goes straight to the detailed content (no brief
   overview first); `#panel` slimmed to a bare div; `setPanel` is now just markExplore+openDetail; init and
   bar-select open detail directly (init without auto-scroll via a skipScroll arg on openDetail).
4. **Beta regression stats.** Under each scatterplot: n, R², SE(β), t(β vs 0), and — the one Stephen wanted —
   **t(β vs 1)** with a verdict ("significantly above/below 1" vs "not distinguishable from 1" at ~95%).
   Computed live from the stored points. Sample reads: Orica β 1.05 / R² 0.62 / t(β vs 1) 0.3 (not distinct
   from 1); CBA 0.80 / R² 0.37 / t −0.9; Grifols 0.85 / R² 0.37 / t −0.7. Realistic beta-regression numbers.

Verified in node across all three: valid JSON, dcfRows render as drill-downs, open-all + betaStats + skipScroll
wired, snapshot no longer referenced. DOM reviewed, not browser-tested here (Chrome tool won't open file://).

**Still outstanding (post-swap):** Excel formula-workbook download (stub); real EODHD data behind the β
workbench (replace beta_data mock). Iteration ~13 — swapping chats now.

## UI — DNL rich formula-workbook: DCF + discount build + comps/β/stats + charts (10 July 2026)

Stephen's brief: the Excel download should show *all* the numeric analysis, formula-driven — a DCF to
equity per scenario, discount-rate build-ups, comparables/betas/stats/charts. Decisions (via
AskUserQuestion): **hybrid** fidelity, **all four** sheet types, **DNL first**. WBC/CSL keep the simple
book until their bank/FX templates are built (gated on a new `richbook` cfg flag; only DNL has it).

**What the DNL download now contains** (`DNL_scenarios.xlsx`, all formula-driven, yellow/blue inputs):
1. **Assumptions** — global inputs (Rf/ERP/α, shares 1884, net debt 1300, reduced-form calibration, WACC
   weights, market/broker).
2. **Comparables & Beta** — peers from `cfg.beta` (mock): levered β, tax, D/E → **Hamada unlever/relever**
   (formula) columns; **subject β = median of selected levered** betas (1.10, matches the UI default,
   relever-off); a **regression block** (26 points) with native **SLOPE / RSQ / STEYX-based SE(β) / t(β vs 1)**
   formulas; and a **native scatter chart with linear trendline**.
3. **Discount rate** — Re = Rf + β×ERP + α (β links to the comps median) → **Re 9.80%**, then
   WACC = Re×wE + after-tax Kd×(1−wE) → **WACC 8.624%** (matches the notes). Scenarios discount at their
   assessed rate by default; this β-driven WACC is the labelled alternative.
4. **DCF to equity per scenario** (one tab each) — explicit 5-year FCFF cascade (solve-F1 construction) →
   PV explicit + PV terminal → **EV → net-debt bridge → equity → ÷ shares → per share**, plus an implied
   P&L block. Built **reduced-form-consistent**: it **reconstructs EV and ties EXACTLY to the UI headline**
   (Muddle Through EV 8,064 → 3.59; all six scenarios tie, EV-check Δ = 0.0000).
5. **Summary** — every scenario value linked to its DCF tab, + β/Re/WACC/market/broker.

**Engine additions.** The inline writer gained **native scatter-chart support** (chart/drawing parts, rels,
content-types, linear trendline). New shared module `dnl_rich.js` (→ `DNLRICH`) alongside `vcc_book.js`
(simple, → `VCCBOOK`) and the chart-capable `xlsx_writer.js` (→ `VCCXLSX`). `vccDownload` branches:
`CFG.richbook && CFG.beta` → DNLRICH, else the simple book.

**Verification (strong).** LibreOffice headless recalc: all 6 DCF tabs reconstruct EV and tie to the UI
numbers (Δ 0.0000); β 1.10 / Re 9.80 / WACC 8.624; regression stats compute (n26, β1.051, R²0.618,
SE0.169, t(βvs1)0.303 — "not distinguishable from 1", matching the UI); Hamada unlever/relever correct
(Orica 1.05→βu 0.798→relever 0.955); no error cells; all XML well-formed; scatter chart survives LO;
apostrophe/edge-char safe. **End-to-end re-run from the shipped `dnl_scenario_interface.html` CFG** (not just
the /tmp source) reproduces the tie-out. (Not opened in real Excel here — Stephen to eyeball the download.)

**Hybrid design note (how it upgrades).** The DCF path is a reduced-form-consistent reconstruction (F1 solved
so the explicit stream reproduces the anchor×ratio EV), *not* the audited 3-statement model. The sheet
**layout** mirrors the real `dnl_muddle_through_valuation_v4.xlsx` (Assumptions → WACC → DCF → Equity bridge),
so when the DCF engine (M1+) lands, its per-scenario projection lines swap into the same cells without
changing structure — same mock-now/real-later pattern as the β workbench.

**Also fixed:** the recurring `/tmp/cfgs.json` permission collision — `build_cfgs.py` now dumps, and
`gen_ui.py` reads, a **script-local `cfgs_gen.json`** (cwd-independent, falls back to /tmp), so a
prior session's file can no longer block regeneration.

**Next (WBC/CSL rich templates):** bank archetype (cost of equity, ROE fade to Ke, CET1-binding payout, no
EV bridge — a dividend/excess-return build, not FCFF→EV) and CSL (FCFF at CoE with USD→AUD 0.66). Then real
EODHD data behind the β workbench. Iteration ~19 this chat — **swap chats now.**

## UI — Excel formula-workbook download shipped (10 July 2026, fresh chat)


The stub `#dlbtn` now downloads a **real, self-contained formula workbook** — no libraries, works offline
from the single HTML file (chose the inline browser writer over the Python side, per Stephen: keeps "HTML is
the contract").

**What it produces.** `<TICKER>_scenarios.xlsx`, built live from the current in-browser state (so it
**captures your edits** — overridden world cases and user scenarios included). Structure:
1. **Assumptions** sheet — the reduced-form baseline (base value, reference Re/g/margin/tax/x0, wTerm, x
   sensitivity, market & broker), all in **yellow-fill / blue-font input cells**.
2. **One tab per editable scenario** — the five value-material inputs + anchor as yellow inputs; then
   term / margin / tax / x factors → reduced-form ratio → **value per share, all by formula** linking back
   to Assumptions (`=$B$3*B17`, cross-sheet `'Assumptions'!$B$12`, etc.). Honours workbook-discipline
   (formulas not hard-coded values; baseline separate from scenario inputs; value derived).
3. **Summary** — every scenario value linked to its tab by formula, + market/broker reference lines.

**How it's built.** Two shared JS modules inlined into the generator's SCAFFOLD: `VCCXLSX` (CRC32 +
store-only ZIP + minimal OOXML — inlineStr text, number/formula cells, 5-style sheet incl. yellow/blue
input style, `fullCalcOnLoad`) and `VCCBOOK` (maps live CFG state → sheets, mirrors gen_ui's reduced-form
for cached values). Both live in `_generator/xlsx_writer.js` + `vcc_book.js` conceptually but are inlined
verbatim into `gen_ui.py` (byte-parity verified against the node-tested source).

**Verification (strong — actually recalculated).** Built workbooks from all three real CFGs; opened in
**openpyxl** (structurally valid, value cells are formulas not constants, inputs carry FFFFF2CC fill /
FF0000CC font); then **LibreOffice headless recalc** (`--calc`, fullCalcOnLoad) reproduced **every one of
the 18 scenario tabs to the exact UI number** (DNL 4.16/3.59/3.48/2.63/1.44/1.28; WBC 35.46/30.15/…/20.09;
CSL 237.29/203.83/…/159.90). Override test: MT +1% Re → 3.59→3.16 (down, correct); a user "bull case" +0.5%
g → 3.86 (up); Summary cross-sheet links (incl. a spaced sheet name) resolve. All three HTML: CFG still
parses as valid JSON; stub/alert gone; `vccDownload` wired to `#dlbtn` in both openDetail and openAll.
(Browser click-to-save not exercised — Chrome tool won't open file://; Stephen to eyeball the actual
download.)

**Sandbox quirk noted:** `/tmp/cfgs.json` is owned by a prior session's uid (nobody) and sticky `/tmp`
blocks overwrite/rm, so `build_cfgs.py` errors on its `json.dump`. Existing file is current and valid, so
`gen_ui.py` runs fine against it — but a future sandbox session may need to dump cfgs to a fresh path. Edits
built sandbox-side + `cp`'d to the mount (truncation quirk avoided).

**Excel-repair fix (same session):** Excel (stricter than LibreOffice) stripped the Summary's
cross-sheet formula when a user-scenario name contained an apostrophe — the quote in
`'Bob's case'!$B$18` closes early. Fixed in `vcc_book.js`: `refName()` doubles apostrophes
(`'Bob''s case'!`), and `sanitize()` strips edge apostrophes plus the illegal `[]:*?/\` set from
tab names. Re-verified via LibreOffice recalc across all three + a torture-test of names (`&`,
quotes, brackets, edge/inner apostrophes): every Summary link resolves and all XML parts are
well-formed. Also relabelled the explore heading → "Explore the build-up for the selected
scenario". gen_ui.py rebuilt deterministically from the pristine original (xlsx + fix + label).
Iteration ~9.

**Remaining UI:**
 real **EODHD data** behind the β workbench (replace `beta_data.py` mock — needs Ben's
feed/sample); the "advanced / show all inputs" long tail. Local main still needs `git push origin main`
from Stephen's terminal. Iteration ~7 this fresh chat.

## Who and what

Owner, people, repo, and test companies now live in `CLAUDE.md`. Volatile note kept here:

- **Strategist friend** has independently completed an IPL/DNL scenario valuation; that's
  the calibration benchmark for step 8.

---

## Working preferences

Now codified in `CLAUDE.md` — house style plus the two standing rules (workbook discipline,
write-up discipline). Not duplicated here.

---

## Interface prototypes (25 June 2026) — CSL, DNL, WBC shareable HTML

**What.** Designed an interactive end-user interface for the scenario valuations and
delivered three self-contained, offline HTML prototypes in `ui_prototypes/`
(`csl_`, `dnl_`, `wbc_scenario_interface.html`). For sharing with Ben and iterating.
Iterated v1→v3 live as inline mockups before locking the design.

**The interface concept (locked with Stephen):**
1. Headline metric cards: per-share value, vs market, vs average broker, plus a
   company stat (CSL terminal-% of value; DNL/WBC asymmetry ratio).
2. "Top 5 value drivers" sliders — the five biggest movers only (not Behring-style
   near-term growth, which barely moves value), stated as such. Discount rate is a
   single slider (not beta). Responses are an **illustrative** approximation, not the
   live DCF engine.
3. Scenario outcomes bar chart — clickable scenarios that drive the build-up views;
   an **average broker** bar (Stephen's preferred term over "consensus"); market line.
4. "Explore the build-up" drill-downs, each with a short snapshot + "learn more" →
   full view: world-scenario write-up (discussion-doc depth), **company-vs-industry
   Five Forces** (per-force industry rating vs company position + impact), company
   position, **discount-rate build-up** (Rf+β×ERP, peer triangulation, §3.5.7 check),
   **assumptions & rationale** (each input with §14.5.1 [disclosed]/[derived]/[judgment]
   tag), and a valuation build-up with an **all-scenario Excel download** (one tab per
   scenario).

**Per company:**
- CSL — only Muddle Through calibrated (USD 141.78 / AUD 214.82); other five scenarios
  are placeholders. Hand-built file.
- DNL — all six scenarios real (Orderly 4.16 → Stagflation 1.28; MT 3.59 at market 3.61;
  4.05× asymmetry). Industrial: WACC/EV bridge, gas-roll-off lever, −25bps Five Forces.
- WBC — all six real (Orderly 35.46 → Stagflation 20.09; MT 30.15 vs market 35.32; 1.90×).
  Bank fork §15: cost-of-equity only, NIM/credit/CET1 build-up. Key story: market is
  implicitly pricing Orderly Convergence (35.46), not the status-quo base.

**Generator.** `ui_prototypes/_generator/` (`build_cfgs.py` real-data configs +
`gen_ui.py` common scaffold) reproduces the DNL/WBC files. See its README.

**Open / next on the interface:**
1. Slider responses are illustrative — wire to the real engine for production.
2. CSL's other five scenarios need calibrating to make its bars real like DNL/WBC.
3. Optional: side-drawer instead of inline-overlay for detail views; PPTX export.
4. The all-scenario Excel download is a real build item (DNL/WBC scenario comparison
   workbooks already exist; CSL's needs its scenario set first).

---

## Current state of play (as of 25 June 2026 — CSL consensus + v3 reforecast)

**Session focus.** CSL consensus comparison, an industry-grounded re-challenge of
the Muddle Through assumptions, a v3 reforecast, and a process-discipline pass
(v0.7 proposal + a reusable workbook lint).

### What happened

1. **FMP free tier can't cover CSL.** Stephen's free FMP key works for analyst
   estimates on whitelisted (mainly large-cap US) symbols only; both CSL.AX and
   the CSLLY ADR return `402 Premium / symbol not available`. The sandbox also
   blocks the FMP domain directly. Consensus was therefore pulled via the
   Claude-in-Chrome browser from MarketScreener + Yahoo Finance (16 analysts).
   For future consensus pulls: use the browser route, not FMP free.

2. **Consensus (16 analysts, USD).** FY26–28 revenue 15,390 / 15,670 / 16,278;
   normalised EPS FY26 6.28, FY27 6.40. Notably consensus has FY26 revenue −1.1%
   and EPS −5%, and has been cutting hard (FY26 EPS 6.90 → 6.28 over 90 days; 15
   downward revisions, 0 up). 12-month target ≈ USD 96.75 (~AUD 136).

3. **v1 vs consensus.** Framework was above consensus on revenue (+6/+9/+10%) and
   EBIT (+4/+13/+17%), widening through FY28 — divergence in *direction*, not just
   degree. Added a formula-linked **Consensus comparison** tab (workbook **v2**;
   consensus figures are yellow inputs on Assumptions, model lines link to
   Segment Forecasts / Per-Share, diffs are formulas).

4. **Industry-grounded challenge → three fixes (not a re-tune to market).** Going
   back to the three archetypes and CSL's five-forces position: the long-run
   thesis is defensible (plasma secular 5–7%, scale-margin edge), but three things
   were mis-specified — (i) Behring entered as a flat 5% CAGR with no near-term
   J-curve for the high-certainty Medicare Part D / China trough; (ii) full
   +250bps peer-gap margin uplift banked alongside the growth the reinvested
   US$525m funds (double-count); (iii) a hidden terminal inconsistency — the
   Assumptions sheet stated a 30% terminal EBIT margin but no formula used it, so
   the model capitalised FY31's ~33.3% peak into perpetuity.

5. **Workbook v3.** Implemented all three: Behring J-curve (FY26 −1% → 5.5% by
   FY29, as yellow per-year inputs), Behring margin uplift cut to +150bps (full
   +250 reserved for Orderly Convergence), terminal value rebuilt to bind to the
   30% margin. **Result: USD 141.78 / AUD 214.82** (was 164.97 / 249.96). Premium
   to market AUD 105.53 falls from +137% to **+104%**; premium to consensus target
   from +70.5% to +46.5%. Near-term lines now sit on top of consensus (FY26 EBIT
   slightly below). **~84% of the USD 23/share fall came from the terminal fix
   alone** — most of v1's over-valuation was the orphaned terminal margin, not an
   aggressive growth view. The residual ~+100% premium to market is now genuine
   through-cycle framework disagreement.

6. **Process discipline (Stephen asked how to do this better generally).**
   - **v0.7 proposal** at `design/reviews/methodology_v0_7_proposal_2026-06-25.md`
     — six refinements: §3.7 forecast-trajectory discipline; §16.5 consensus as a
     calibration input; §11.6 workbook-integrity checks; §4.4.1 benefit-funding
     consistency; §3.5.7 market-implied cost-of-capital check; §14.5.2 aggression
     flag. PROPOSAL — pending Stephen's approval; not yet in architecture.md.
   - **Reusable lint** at `scripts/workbook_lint.py` — orphan-input + terminal-
     continuity checks. Catches CSL v1 (exit 1: B55 orphan; effective terminal
     margin 33.3% vs stated 30%); CSL v3 passes (exit 0). Documentation-only
     anchors (measured beta, FY25 memos) downgraded to warnings.

### Workbook files (analyses/csl/valuations/)

1. `csl_muddle_through_valuation_v1.xlsx` — original (USD 164.97).
2. `csl_muddle_through_valuation_v2.xlsx` — v1 + Consensus comparison tab.
3. `csl_muddle_through_valuation_v3.xlsx` — reforecast (USD 141.78 / AUD 214.82).

### Open / Stephen's call

1. **J-curve shape** (FY26 −1% recovering to 5.5%) — Stephen to confirm or flex.
2. **Whether v3 becomes the working CSL version** or stays a candidate.
3. **β 0.85 reality check** (sanity-check #1 in earlier notes) — still open; v3
   leaves Re at 8.75%. A market-implied cross-check would be the §3.5.7 move.
4. **v0.7 approval** — if accepted, fold into architecture.md as the v0.6 → v0.7
   migration note and backport the lint to DNL / WBC workbooks.

### Operational notes

1. **Mount write quirk.** The Cowork file-write tool truncated large new files
   (~8.9KB) mid-write this session; writing sandbox-side and `cp`-ing onto the
   mount was reliable. Worth knowing for future large script/doc writes.
2. **Chat-swap protocol agreed.** Swap chats roughly every 20 exchanges; do a
   full WORKING_NOTES handoff update at the swap (and at every natural milestone).

### Workbook-lint backport + DNL restyle (25 June 2026, later session)

1. **Lint made palette-aware.** `scripts/workbook_lint.py` previously recognised
   only the CSL/WBC input palette (`FFF2CC`/`0066CC`); on DNL (older `FFFF00`/`0000FF`
   palette) it detected *zero* inputs and false-passed. Now recognises both palettes.
   Regression-checked: CSL v1 still trips its terminal-margin ERROR, CSL v3 / WBC pass,
   DNL now actually inspects its 63 inputs.
2. **Lint sweep of latest workbooks.** No CSL-style value-distorting orphan in DNL v5
   or WBC v4 — that bug was unique to CSL v1. WBC's flagged cells are benign (1H26
   reconciliation anchors + the through-cycle credit-loss anchor B30; credit losses
   are wired via the per-year path at Assumptions row 50).
3. **DNL restyled to canonical palette → `dnl_muddle_through_valuation_v6_2026-06-25.xlsx`.**
   Styling-only (63 inputs recoloured to `FFF2CC`+`0066CC` per standing rule 1); zero
   value/formula changes vs v5. No analytical content changed.
4. **OPEN — Stephen's call.** DNL `Assumptions!B17` "DM real GDP growth" (2.0%) is a
   genuine orphan: the growth chain keys off mining growth + inflation and never uses it.
   Parked — either wire it in (changes the valuation; methodology call), recolour as
   non-input context, or annotate and accept. Lint flags it ERROR until resolved.

### CSL — five scenarios calibrated + comparison workbook (25 June 2026, later session)

1. **All six CSL scenarios now real** (were placeholders). Calibrated off the v3
   base as driver overlays. CSL is defensive — scenarios transmit through margins
   (donor-collection wages, energy/carbon cost, payor pricing) and policy, not
   volumes — so the spread is narrow: **asymmetry ~1.31x** (vs DNL 4.05x, WBC 1.83x).
2. **Two corrections this session.** (a) §3.5.7 market-implied reverse-DCF: to justify
   AUD 105.53 the market needs β≈1.7 / terminal margin ~13% / g negative — none plausible
   alone, so the gap is a blend (or genuine under-pricing). (b) **Terminal capex = D&A**
   reinvestment-consistency fix (v1 ran terminal capex 4.5% < D&A 6%, inflating perpetual
   FCFF). Trims every scenario ~5%.
3. **Post-fix distribution (USD / AUD):** Orderly 156.61/237.29; **MT 134.52/203.83**
   (premium to market +104% → **+93%**); AI Lag 131.03/198.53; Disorderly 115.36/174.79;
   Fragmentation 111.03/168.23; Stagflation 105.53/159.90. All formula-based, lint-clean,
   reconciled to an independent Python engine.
4. **Decision (Stephen, 25 June):** hold β 0.85 — wants a *repeatable* framework, not one
   that needs intervention; the residual premium stands as an informative §16 output ("a
   cause for curiosity"), to be explained in the thesis, not tuned away.
5. **Files (analyses/csl/valuations/):** `csl_scenarios_comparison_v1.xlsx` (pre-capex-fix),
   `csl_scenarios_comparison_v2.xlsx` (terminal capex=D&A + Market-Implied §3.5.7 tab),
   `csl_muddle_through_valuation_v4.xlsx` (v3 + terminal-capex fix; MT 134.52). v2 + v4 are
   the working versions.
6. **Next:** CSL thesis (cross-scenario, per-scenario narratives, §16 premium framing) +
   discussion document — DONE (analyses/csl/thesis.md; csl_discussion_v1_2026-06-25.docx + .pdf).

### v0.7 accepted + DNL B17 + engine plan (25 June 2026, later)

1. **Methodology v0.7 ACCEPTED and folded into architecture.md** (now v0.7). Six
   process-discipline refinements from the CSL build: §3.7 forecast-trajectory,
   §16.5 consensus-as-calibration, §11.6 workbook-integrity lint, §4.4.1
   benefit-funding consistency, §3.5.7 market-implied check, §14.5.2 aggression flag.
   Proposal file marked ACCEPTED. All additive; no schema breaks.
2. **Lint (c) backported.** DNL v6 + WBC v4 both lint-clean (exit 0).
3. **DNL B17 resolved** — "DM real GDP growth" annotated as a context memo (not used
   in the growth chain, which keys off mining growth B19 + inflation B18); lint now
   downgrades it to WARN. No valuation change. β decision precedent: keep the framework
   repeatable, annotate rather than wire-in.
4. **Engine implementation plan** for steps 6 + 10 written to
   `design/engine_implementation_plan.md` — FOR APPROVAL. Linkage + assumptions layers,
   fcf_engine + bank_engine, golden-master tests pinned to the workbook numbers
   (CSL MT 134.52, WBC 30.03/30.28, DNL 3.59), milestones M0–M5, risks R1–R8. Key open
   calls: CSL has no impact matrix / financials.yaml (R1); WBC payout oracle 30.03 vs
   30.28 (R5); terminal-share validator fires structurally on compounders (R3).

### CSL is now a first-class data-driven company (25 June 2026, R1 done)

1. **`data/financials/csl.yaml`** authored — USD-functional, segment-level base-year
   snapshot reverse-engineered from csl_muddle_through_valuation_v4 (group + Behring/
   Seqirus/Vifor revenue & margins, corporate, capex/D&A/WC, tax, net debt, restructuring,
   shares, FX, cost-of-equity build with β 0.85 held, terminal margin 30% / g 3% /
   terminal capex = D&A). Valid YAML.
2. **Three impact matrices** in `data/impact_matrix/by_industry/`:
   `plasma_derived_therapies.yaml` (Behring; 21 non-neutral cells), `vaccines.yaml`
   (Seqirus; 8), `specialty_pharmaceuticals.yaml` (Vifor; 11). Sparse per §10.2;
   consistent with the csl_scenarios_comparison_v2 driver overrides + thesis channels
   (margins/policy, not volumes). All three VALIDATE against schemas.linkage.ImpactMatrix.
3. **Pre-existing discrepancy noted (parked):** `australian_major_banks.yaml` carries extra
   top-level keys (`archetype_class`, `version`) the strict ImpactMatrix model forbids — it
   does NOT conform, while industrial_explosives and the three new CSL matrices do. Worth a
   one-line cleanup later (either relax the schema or strip the keys). Schema test suite: 22 pass.
4. **Unblocks engine milestone M3** (CSL no longer needs a workbook fixture; it has matrices +
   financials). Remaining engine open calls: R5 (WBC payout oracle 30.03 vs 30.28), R3
   (terminal-share validator).

5. **M0 engine decisions settled (25 June 2026, Stephen):** R5 — CET1-binding payout
   is the sounder methodology for financial institutions; **30.28 is the canonical WBC
   MT bank-engine oracle**; the flat-0.75 MT workbook (30.03) is superseded — documented note placed on its
   Cover sheet (rows 16-20); optional v5 binding-payout refresh later. R3 — terminal-share validator stays a **non-blocking warning**
   (do not auto-suppress; would silently change documented numbers). With R1 done, M0 is
   settled — the engine is ready to start at M1 (DNL Muddle Through vertical slice).



---

## Current state of play (as of 18 June 2026 — end of long session)

**Session handoff notes.** This session has covered methodology v0.6 consolidation, DNL v5 backport, WBC v3/v4 (workbook + discussion document + scenarios comparison + standing rules), and started CSL v1 (foundation + Muddle Through workbook). If continuing in a new chat, see the "Carrying into next chat" section at the bottom of this file.

### Where everything stands

**Methodology**: v0.6 stable. Six refinements lifted from review-question pattern (peer-gap closure framing, cost-of-closure consistency P&L-vs-bridge distinction, workbook construction discipline §11, assumption-strength tagging §14.5.1, market-vs-framework gap interpretive output §16, acronym sweep discipline §16.4). Architecture spec at v0.6 with full migration note.

**Standing rules now in force** (lines 32-33 in this file):
1. **Workbook discipline** — all Excel spreadsheets use formulas; inputs on Assumptions sheet in yellow-shaded cells with blue text; output cells link via formulas
2. **Write-up discipline** — intuitive narrative per scenario in every company write-up; macro story → key channels → why the number is what it is; plus mental short-cut

**DNL (industrial — first test company)**: v5 backport complete (commit `6d060e5`).
- v0.6 framing applied: "transformation overlay" → "peer-gap closure" in thesis.md and dnl.md
- β peer-triangulation discipline applied: peer set Orica (~1.05) / Yara (~1.20) / ICL (~1.10) / Sasol excluded (~1.45) / DNL measured 0.36 unreliable; β selected 1.10 (cluster midpoint)
- Workbook v5 with new "DCF Build-up (v5)" sheet showing explicit Step 2 → Step 3 decomposition (industry growth + company offset; base margin + peer-gap closure + gas roll-off)
- v4_5forces workbook preserved as audit trail
- **Outstanding**: discussion document refresh with peer-gap closure framing (cosmetic, only worth doing if Tara re-shares with Sunil); actual EODHD pulls for ORI/YAR/ICL when Ben has time

**WBC (bank — second test company)**: v3/v4 complete (commits `c47c420`, `cfbfdd6`, `939fba3`).
- All v0.6 standing rules applied
- Methodology §15 bank fork stable
- β peer-triangulation: 0.75 selected (CBA/NAB/WBC midpoint); ANZ excluded; MQG informative-not-comparable
- Discussion v3 includes intuitive narrative per scenario (the example for the standing rule)
- Workbook v4 is formula-based per standing rule (133 valid formula cells, zero errors)
- Headline: Muddle Through AUD 30.03 vs market AUD 35.32 (−15%); Orderly AUD 35.84 essentially at market (market is implicitly pricing closer to upside)
- Asymmetry ratio 1.83× (materially less than DNL's 4.05× — bank capital-constraint payout flex + oligopolistic structure cap both sides)
- **Outstanding**: nothing critical

**CSL (industrial — third test company, IN PROGRESS)**: foundation + workbook v1 done (commits `f1f3652`, `4fa068b`).
- Documents register, 3 industry archetypes (plasma_derived_therapies, vaccines, specialty_pharmaceuticals), CSL company position YAML with 3 segments + Five Forces all built
- Workbook v1 formula-based per standing rule, segment-level forecasts (Behring + Seqirus + Vifor + corporate) aggregating to consolidated NPATA → FCFF → per share
- USD throughout; AUD translation only at per-share output line
- β selected 0.85 (peer triangulation: Grifols / Takeda / Sanofi 0.7-0.9 range); measured 0.094 from EODHD unreliable per §3.5.3
- Peer-gap closure overlay: USD 525m annual savings target by FY27; +250bps Behring margin uplift / +100bps each Seqirus, Vifor by FY31
- §4.4(b) restructuring cost USD 507m PV deducted in equity bridge
- FY25 NPATA reconciliation: computed USD 3,130m vs disclosed USD 3,219m (3% gap — sound)
- **Headline result**: Muddle Through per share USD 164.97 = AUD 249.96 vs market AUD 105.53 = **+137% premium**
- **This needs review.** Market currently 61% below 52-week high AUD 269. Framework Muddle Through implies the market reset is overdone — but the gap is striking. Per v0.6 §16, market is implicitly pricing a scenario closer to a stress case than to status quo. Sanity-checks worth running:
  1. Beta — 0.85 may be too low given CSL's 60% drawdown; β = 1.0 → Re = 9.5% → ~USD 145 / AUD 220 still well above market
  2. Peer-gap closure aggressiveness — +250bps Behring may need a more cautious Muddle Through (closer to +150bps?) with full +250bps in Orderly Convergence
  3. Beyond v1: assess whether market is pricing a "Stagflation / Disorderly Policy" scenario more like AUD 80-110
- **Outstanding for CSL v2+**: per-scenario impact matrix; scenarios comparison; thesis (with intuitive narrative per scenario per standing rule); discussion document; **decision on whether to re-anchor v2 with more cautious peer-gap closure for Muddle Through**

### Open methodology questions / decisions pending

1. **CSL peer-gap closure aggressiveness**: is +250bps Behring margin uplift correct for Muddle Through, or should it be more cautious (with full closure as Orderly Convergence)?
2. **CSL Seqirus demerger**: v1 values pre-demerger consolidated. Post-demerger value-of-stub treatment deferred to v2 sensitivity.
3. **DNL peer-triangulation refresh**: indicative β values used (Orica 1.05 / Yara 1.20 / ICL 1.10). EODHD pulls on those tickers pending from Ben.
4. **CSL peer EODHD pulls**: requested from Ben — Grifols, Takeda, Sanofi for triangulation refresh.

### Pending Ben asks (data workstream)

1. EODHD fundamentals exports for DNL peers: Orica (ASX:ORI), Yara (OSLO:YAR), ICL (NYSE:ICL)
2. EODHD fundamentals exports for CSL peers: Grifols (BME:GRF), Takeda (TSE:4502), Sanofi (Paris:SAN), GSK (LSE:GSK)
3. WBC NIM half-year-cadence history from FY22 onward (multi-year time series) — deferred from earlier
4. Macquarie Banking & Financial Services segment carve-out for bank peer set

---

## Carrying into next chat

If this chat session needs to end and you're starting a fresh one, here's how to bring the new Claude up to speed efficiently:

### Opening message for the new chat

A short message like this should be enough — the new Claude reads WORKING_NOTES (which is the bootstrap document) and gets oriented:

> "We're working on the VCC scenario-based equity valuation framework. Read WORKING_NOTES.md first — the 'Current state of play (18 June 2026)' section at the top has the latest. Methodology is at v0.6; DNL backport done; WBC v3 stable; CSL v1 workbook just built and needs sanity-check review (Muddle Through AUD 250 vs market AUD 105, +137% premium — the gap is too large; want to refine Muddle Through assumptions). Standing rules at lines 32-33 of WORKING_NOTES — formula-based workbooks, intuitive narrative per scenario. Push to git happens at cmd in `C:\Users\steph\vcc-valuations` using `git push origin main`."

### Specific tips for continuity

1. **The bootstrap pattern works.** WORKING_NOTES is the authoritative single source for state. Architecture spec is at v0.6; methodology doc is comprehensive. New Claude will pick up the framework conventions by reading those.

2. **Git pushes happen from your cmd, not from Claude.** The sandbox can stage and commit but can't reach github.com. Whenever Claude says "N commits ahead", run `git push origin main` from your terminal.

3. **Use the document discipline you've established.** When Claude proposes a new build, expect: documents register update per §14, source-document key-insights extraction, then YAML + workbook + thesis + discussion document, in that order.

4. **Standing rules are binding.** Any workbook Claude produces should be formula-based with the Assumptions sheet input pattern. Any write-up should include the intuitive per-scenario narrative. Push back if Claude forgets — both rules surfaced from your review feedback and are in WORKING_NOTES.

5. **The "framework vs market" gap is a feature.** For each company, the framework's Muddle Through may sit at market (DNL), below market (WBC), or well above market (CSL v1). Each tells a different analytical story per methodology §16. Be careful: don't reflexively re-tune assumptions to match market. The framework's job is to give a defensible base case; gaps to market are informative outputs, not calibration errors.

6. **What to do next session**: the natural priorities are (a) review CSL v1 Muddle Through assumptions — particularly Behring growth rate and peer-gap closure aggressiveness; (b) build CSL scenarios comparison once Muddle Through is finalised; (c) CSL thesis + discussion document (with intuitive narratives); (d) at some point, the DNL discussion document refresh with peer-gap closure framing if you want to re-share with Sunil.

7. **The repo has 37+ commits ahead of origin.** Push them all before you finish to ensure github mirror is current. Recovery from a lost local will then be straightforward.

---

## Current state of play (as of 12 June 2026)

**17 June 2026 (evening) — Methodology v0.6 consolidation: six review-derived refinements lifted.**

Tara asked a meta-question: from her review questions during DNL and WBC, are there methodology questions worth raising. Yes, six surfaced. All six are discipline / explicit-articulation refinements rather than analytical-substance changes; no per-share numbers move. v0.6 (additive only) lands them:

1. **§3.2 renamed to "Peer-gap closure overlay"** (from "Transformation overlay"). Reframed so the methodology view does not depend on any specific announced programme succeeding; the assumption is the closure trajectory, with a specific programme (UNITE for WBC, post-demerger glide for DNL) treated as the most credible stated mechanism. YAML field name `peer_gap_closure_overlay` (new) coexists with `margin_glide_path` (existing) for backward compatibility.

2. **§4.4 renamed to "Cost-of-closure consistency rule"** (from "Restructuring-cost consistency rule") and now distinguishes (a) P&L-absorbed (WBC's UNITE expensed through P&L, time-profile mechanic) versus (b) upfront one-off equity-bridge line (DNL's AUD 12m execution cash). Both worked examples in methodology. Auditor discipline test added.

3. **New §11 Workbook construction discipline** — Step 2 → Step 3 traceability requirement. Every workbook MUST show industry baseline AND company offset as separate rows, with the company-specific assumption derived. Replaces the implicit assumption that the analyst would mentally combine the two layers. DNL backport required (current DNL workbooks collapsed the chain).

4. **§14.5.1 Assumption-strength tagging.** Each calibration anchor tagged `[disclosed]`, `[derived]`, `[judgment]`, or `[default]`. Makes audit transparent — reviewer identifies at a glance which assumptions are hard-data-grounded.

5. **New §16 Interpretive output discipline — market-vs-framework gap.** Codifies the diagnostic the framework has been using implicitly. Where Muddle Through sits at market (DNL) the value-add is asymmetry exposure; where it doesn't (WBC), the closest-to-market scenario is the market's implied pricing, and the analyst articulates which assumptions differ.

6. **§16.4 External-facing artefact discipline — acronym sweep.** Internal workbooks may use shorthand (TTM, AIEA, NIM, CET1); external artefacts spell out all but the canonical commonly-recognised set. Standard expansions table for consistency.

Architecture spec bumped 0.5 → 0.6 with migration note covering all six refinements.

**DNL backports outstanding** (to be done on next DNL refresh):
- Rename "transformation overlay" → "peer-gap closure" in DNL company YAML, thesis, briefing pack, discussion document where appropriate
- Rebuild DNL workbook to show industry growth + company offset decomposition explicitly (similar to WBC v3 pattern)
- Apply β peer-triangulation discipline (already noted earlier)

These would constitute a "DNL v5" pass — methodology-discipline refresh, not analytical-substance change.

**Meta-observation:** Tara's review questions on the first two test companies surfaced these six refinements systematically. The hypothesis is that the third (CSL) and beyond will produce fewer refinements as the methodology hardens — but each new company should be expected to surface at least one or two before the framework is stable.

---

**17 June 2026 — WBC v3 reframe: "peer-gap closure" not "transformation"; UNITE evidence; industry+WBC growth decomposition explicit in workbook.**

Tara raised four substantive questions on the v2 WBC discussion document. Three of them surfaced methodology refinements that v3 addresses:

1. **Framing change (semantic but important).** "Transformation" implies a specific announced program. Westpac's UNITE update (26 March 2026 presentation) lists three stated outcomes of which the third is "CLOSE CTI RATIO GAP TO PEERS" — peer-gap framing is Westpac's own language. v3 reframes throughout: framework assumes WBC management will progressively close the cost-to-income / return-on-equity gap to peers; UNITE is the most credible disclosed mechanism but the framework does not depend on the specific program succeeding.

2. **Cost-to-income glide rebuild around UNITE evidence.** UNITE investment trajectory is FY24 AUD 147m → FY25 AUD 660m → FY26 AUD 850-950m → FY27-28 c.40% of total → FY29 lower. ~75% of spend expensed. Direct annual benefits disclosed AUD 190m (Mortgage Simplification 70 + One Commercial Bank 40 + One Collections 40 + One Wealth 40), plus undisclosed Digital Banker + further initiatives. Implied steady-state benefit FY30-31 ~AUD 300-400m p.a. Glide is now back-loaded: FY27-28 keep elevated UNITE spend (flat CTI), FY29-31 benefits emerge (CTI drops from 51.7% to 48.0%). Half of the gap to NAB (43%) and CBA (42%).

3. **Industry growth + WBC offset decomposition NOW EXPLICIT in workbook.** Previously workbook collapsed industry AIEA growth + WBC company offset into a single number. v3 P&L Forecast sheet shows: industry AIEA growth 4.5% (from §3 of discussion doc) less WBC company offset -15bps (Five Forces: rivalry -10bps + business-banking-rebuild -5bps) = WBC AIEA growth 4.35%. Same explicit decomposition for NIM: industry NIM 1.86% + WBC supplier-power offset +8bps (deposit franchise) = WBC NIM anchor 1.94%.

4. **(Deferred to a separate pass)** — Tara also noted the v2 model had no explicit transformation execution cost line. v3 acknowledges the UNITE spend is already in 1H26 base opex. FY27-28 maintaining UNITE spend = no additional execution overlay needed at the equity bridge level (it shows up in higher opex during those years). Methodologically this is "cost in P&L during execution years, benefits in P&L during reaping years" — consistent with §3.2 transformation overlay framing.

Workbook v3 result: AUD 30.08 per share (essentially same as v2 AUD 29.98; 10c uplift). Y1 EPS AUD 2.17 matches consensus FY27 AUD 2.18.

Documents register updated with UNITE presentation. wbc_unite_update_presentation_2026-03-26.pdf saved to data/financials/historical/wbc/.

---

**16 June 2026 (evening) — WBC NIM YE history FY22-FY25 extracted; historical results pack ingested.**

Tara provided WBC half-year and full-year results announcements covering FY22 through FY25 (plus FY23 via annual report) and MQG FY26 annual report + presentation. Saved to `data/financials/historical/{wbc,mqg}/` and registered in `wbc_documents.yaml` (wbc_historical_results_pack and mqg_fy26_results_pack).

WBC NIM YE history added to `bank_specifics.historical_anchors.nim_history_annual`:

| FY | Group NIM | AIEA avg (AUDm) | Basis |
| FY22 | 1.93% | 886,971 | Statutory (disclosed) |
| FY23 | 1.95% | 941,356 | AIEA-weighted half-year average |
| FY24 | 1.95% | 970,594 | Ex Notable Items (disclosed in FY25 comparative) |
| FY25 | 1.94% | 1,002,839 | Ex Notable Items (disclosed) |

Through-cycle anchor 1.94% (midpoint of FY22-FY25 range). Current 1H26 NIM 1.89% sits at lower end — front-book mortgage competition. Pre-2022 NIM regime materially higher (1H21 2.06%) — RBA-rate-cycle effect.

Synthesised `nim_anchors` block also added: through-cycle anchor, recent peak (1.97% 2H24), recent trough (1.88% 1H25), long-term pre-2022 baseline (2.06%), with scenario calibration commentary on how NIM should move under Muddle Through, Stagflation, Disorderly Climate.

MQG FY26 results saved for future MQG-Banking segment peer-comp work (currently excluded from peer set as "different archetype" at group level; segment carve-out from these reports addresses the "option 2" Tara discussed).

---

**16 June 2026 (afternoon) — Peer-triangulation principle promoted to general methodology (§3.5.3).**

Following Tara's question on whether the principle should be addressed in the overall methodology, peer-triangulation is now a general discipline at **§3.5.3**, applying to both industrials and banks. The bank-specific statement at §15.2(c) was slimmed to a pointer; §15.2(b) now references §3.5.3 for the procedure. Existing §3.5.3 (User override) and successors renumbered to §3.5.4 / §3.5.5 / §3.5.6. Schema implications updated: company YAMLs MUST carry a `beta_selection_rationale` block per §3.5.3.

DNL's measured β = 0.95 (sourced from world-index AUD-MSCI) was applied without peer triangulation against Orica / MAXAM / Austin Powder. To be back-applied on the next DNL refresh — Australian-listed peer set is thin (Orica is the only ASX-listed direct peer; world-listed peer set adds Yara, ICL, Sasol-explosives flank).

Architecture spec v0.5 migration note (c) records the §3.5.3 addition and the renumbering.

---

**16 June 2026 — Beta-selection principle landed; peer EODHD feeds for CBA / NAB / ANZ / MQG ingested.**

Tara articulated a key methodological principle: measured β carries material statistical noise and should not be used mechanically. The framework should select β via reasoned peer triangulation, in the same spirit as a Five Forces decomposition — catalogue peers, identify outliers, reason about where the subject company should sit relative to peers given franchise mix, then select. The principle is general (applies to industrials at §3.5.2 too) but landed first in methodology **§15.2(c)** as part of the bank-specific cost-of-equity discipline. Both the measured and selected β are documented for transparency.

Peer feeds applied for WBC:

1. Peer beta dataset: CBA 0.80, NAB 0.72, ANZ 0.57, MQG 0.88, WBC 0.73.
2. ANZ excluded as outlier (institutional / international revenue dilution; Suncorp integration period). MQG excluded as informative-not-comparable (different archetype).
3. Comparable cluster CBA / NAB / WBC: β 0.72-0.80, midpoint 0.75.
4. **β_selected for WBC = 0.75** (cluster midpoint); measured 0.73 documented alongside. Re = 4.30% + 0.75 × 5.00% = **8.05%** (vs 7.95% under mechanical use of measured β).
5. Peer ROE / P/B / forward PE rankings validate franchise hierarchy: CBA > MQG > NAB ≈ WBC > ANZ on ROE; market valuation multiples track this exactly.

Archetype `cost_of_equity_anchor` revised to: measured peer range 0.57-0.88; comparable cluster range 0.72-0.80; anchor selected β 0.75; Re anchor 8.05%. The initial 0.85-1.00 range based on global-diversified-financials default was too high — Australian Big Four oligopoly produces meaningfully lower systematic risk than the global default.

NIM time series: Tara accepted YE basis (5 data points: FY21-FY25) over half-yearly (9 data points). Deferred to next pass — requires AIEA history not in the EODHD feed.

---

**15 June 2026 — Ben's WBC financial feed arrived; key calibrations applied.**

Ben's EODHD fundamentals export landed (`data/financials/wbc_eodhd_fundamentals_2026-06-15.csv`). Material calibrations applied to WBC YAMLs and bank archetype:

1. **Equity beta 0.73** — below initial archetype range 0.85-1.00. Cost of equity revised to Re = 4.30% + 0.73 × 5.00% = **7.95%** (vs initial archetype mid-point ~8.93%). 100bps reduction; meaningful upward pressure on Muddle Through fair value. Archetype `cost_of_equity_anchor` beta_range extended to 0.73-1.00 to accommodate.
2. **Shares outstanding 3,414.9m** verified (was 3,380m placeholder).
3. **Market reference price AUD 35.32** at feed date 15 June 2026 (was AUD 38.50 placeholder). Sell-side consensus 12-month target AUD 33.45 (~5% below current trading).
4. **Multi-year net income history** added to `bank_specifics.historical_anchors`: peak FY18 AUD 8.09bn; trough FY20 (COVID) AUD 2.29bn; FY25 AUD 6.91bn; through-cycle 5-yr average AUD 6.45bn.
5. **FY26 / FY27 consensus** captured: FY26 EPS AUD 2.06 / FY27 EPS AUD 2.18 — usable as Muddle Through market check.
6. **Book value per share AUD 21.31** (book equity ~AUD 72.8bn).

Outstanding feed requests: peer comp (CBA/NAB/ANZ + Macquarie banking on same metrics) and NIM time series at half-yearly cadence — for next pass.

---

**12 June 2026 — Westpac build kicked off; bank-methodology fork landed first.**

Ben sent the WBC source pack (11 files: 1H26 financial results announcement, 1H26 IDP presentation, 1H26 key financial information xlsx, 1H26 quantitative information xlsx (Pillar 3), 1H26 risk factors, items-impacting-1H26 PDF, 1Q26 Update + IDP, December and March Pillar 3 reports, FY25 annual report). Ben's financial feed (multi-year time series, beta, peer comp) still to come — not blocking.

Before starting the WBC company build, added **methodology §15 "Bank-specific valuation conventions"** as a fork. Industrials methodology (§§2–7) unchanged; banks invoke §15 in place of §§2–4. Key conventions: cost of equity not WACC (no EV→equity bridge); NII = average interest-earning assets × NIM; credit losses are a scenario-conditional primary driver, not a residual; CET1 ratio binds dividend payout and asset growth; ROE fade to Ke for terminal. Schema additions: `bank_specifics.*` on company YAMLs, `bank_archetype.*` on industry YAMLs, `macro_baseline.credit_cycle / cash_rate_path / swap_spreads / housing_market / regulatory` on scenario YAMLs. Architecture spec bumped v0.4 → v0.5 (additive only).

WBC v1 baseline committed 12 June 2026 (commit d568262): `data/industries/australian_major_banks.{yaml,md}`, `data/companies/wbc.{yaml,md}`, `data/companies/wbc_documents.yaml`. Calibrated against 1H26 results (anchor date 31 March 2026): CET1 12.42%, NIM 1.89%, AIEA AUD 1,035bn, gross loans AUD 890bn, customer deposits AUD 745bn.

Next: per-scenario impact matrix `data/impact_matrix/by_industry/australian_major_banks.yaml`, then Muddle Through valuation workbook applying §15 conventions.

---

## Previous state of play (as of 16 May 2026)

- Architecture spec **v0.1 frozen** (`design/architecture.md`), tagged in git as `architecture-v0.1`. Sections 1–17 reviewed and updated. Ben's-bot platform-side review (5 May 2026) absorbed; Group 1 changes committed. Plus a new §9.7 review item (#9) added 16 May 2026 capturing the terminal-growth-from-demographic-trajectory principle.
- Build plan wall chart at `design/build_plan.html` (currently v3).
- Response document to Ben's `vcc_valuations` rev1 design committed at `design/reviews/vcc_valuations_rev1_response_2026-05-16.md`.
- **Step 1** (close out design hardening): **done.** Editorial sweep applied; v0.1 freeze and git tag in place.
- **Step 2** (Draft analytical methodology): **done.**
  - `design/frameworks/five_forces_questions.md` — all five forces, Porter-2008-aligned.
  - `design/frameworks/payor_and_regulator.md` — v1 draft. Two-axis (regulatory + payor) framework.
- **Step 3** (Scenarios workshop): **done.** Six scenarios selected via interactive workshop (16 May 2026): Muddle Through (interior, most-likely), Orderly Convergence (upside boundary), Stagflation Persists (macro-downside boundary), Fragmentation and Resource Nationalism (geopolitical boundary), Disorderly Climate Crystallisation (climate boundary), AI Productivity Lag (technology boundary). All six scenarios drafted into `data/scenarios/<id>.yaml` (structured per §6.4) and `data/scenarios/<id>.md` (narrative per §16.1). Workshop output at `design/scenarios_workshop.md` includes institutional comparison (IMF / OECD / World Bank / IEA / NGFS mapping).
- **Step 4** (Formalise data schemas): **done.** pydantic v2 models for all eight layer schemas live under `src/vcc_valuations/schemas/` (scenario, industry, company + corporate-action overlay, driver, linkage, assumption, frameworks, plus common enums). JSON Schema exports generated under `design/schemas/`. Round-trip tests under `tests/schemas/` validate each scenario YAML against the model — all six pass; 22/22 tests pass overall.
- **Step 5** (Populate first archetype — DNL, formerly IPL): **substantively done.** Five phases completed.
- **IPL → DNL rename (22 May 2026):** Ben's data dump revealed the company was renamed from Incitec Pivot Limited (IPL) to **Dyno Nobel Limited (DNL.AU)** in March 2025 following the demerger of the fertilisers business. ISIN AU0000390544. Two passes:
  - **First pass (commit `f21fb1e`):** Renamed company / financial / analyses files (`data/companies/dnl.{yaml,md}`, `data/financials/dnl.yaml`, `analyses/dnl/`), bulk-replaced IPL → DNL in those files' prose, replaced indicative financials with real EODHD-sourced data (FY2025 + TTM Mar 2026), refined functional-currency treatment to per-entity (parent AUD, US subsidiary USD per IAS 21 / AASB 121).
  - **Editorial sweep (commit `_pending_`):** swept IPL → DNL across `design/architecture.md` (now v0.2.1), `design/build_plan.html`, `design/frameworks/five_forces_questions.md`, `design/scenarios_workshop.md` and `..._prep.md`, `design/reviews/vcc_valuations_rev1_response_2026-05-16.md`, `data/industries/industrial_explosives.{yaml,md}`, `data/impact_matrix/by_industry/industrial_explosives.yaml`, and the six `data/scenarios/*.md` files. The single remaining "IPL" reference is the legitimate "DNL, formerly IPL" historical pointer in architecture spec §2 item 4. YAMLs still validate against pydantic schemas. Architecture spec bumped v0.2 → v0.2.1 (editorial only; no schema or analytical content changes).
  - **Phase A:** industrial_explosives archetype YAML + narrative, validates against schema. Multi-tier competitive landscape (Tier 1: Orica + Dyno + MAXAM + EPC; Tier 2: Austin Powder + AECI + Solar Industries + Sasol/BME + Yara; Tier 3: country-specific).
  - **Phase B:** IPL company position YAML + narrative + indicative base-year financials. **USD functional currency** (Ben's-bot review point). Single segment post-demerger. Five franchise assets, archetype-specific positioning block, two company-level scenario sensitivity overrides (high operational carbon, moderate supply-chain concentration).
  - **Phase C:** industrial_explosives impact matrix across all six scenarios. 46 driver movements populated; sparse per §10.2; two defended-exception terminal-state entries per §10.6 rule 2.
  - **Phase D:** six per-scenario impact narratives + cross-scenario thesis. Each scenario sketch covers IPL-specific transmission channels and divergences from archetype baseline. Thesis identifies negative asymmetry: downside scenarios compress value more than upside lifts it.
  - **Phase E (valuations):** deferred to Phase 3.5 smoke-test DCF (Step 7).
- **Phase 3.5 smoke-test DCF (24 May 2026): done, including calibration pass.** First-pass end-to-end pipeline (commit `86233ca`) confirmed the framework works: comparative directional ranking matches the per-scenario narratives; framework discriminating power is real. First-pass calibration issues (baseline AUD 1.87/share vs market AUD 3.61; two scenarios negative-equity; four trip the >70% terminal-share validator) addressed by an incremental calibration pass: normalised EBIT margin (11.2% → 13.5%), steady-state net debt (AUD 1,810m → AUD 1,300m), rigorous component-build WACC (8.5% round-number → 8.82% from Rf 4.30% + β 1.15 × ERP 5.00% with market-value weights). Calibrated Muddle Through baseline AUD 2.53/share (30% below market, down from 50% below); negative-equity outcomes disappeared; terminal-share validator still fires on 3 of 6 (structural; needs §11.4.2 rule 5 fade period in Step 7). Calibration captured in `data/financials/dnl.yaml` `normalised_baseline` block and `docs/phase_3_5_findings.md` Calibration-pass section. No architecture spec changes required.
- **Next: Step 6** — production translator informed by Phase 3.5 findings (calibrated baseline, §11.3 time profiles, §11.4.2 consistency rules), then either re-run smoke test or proceed straight to **Step 9** (populate CSL + WBC) once the engine is solid.

---

## Conversationally-decided things worth holding in working memory

- IPL is post-demerger single-segment industrial explosives. Working assumption pending Ben's data workstream confirmation when populating `data/companies/ipl.yaml`.
- UI is **embedded in the existing VCC dashboard** (not standalone FastAPI + Vue). Locked Decision §2.1 was re-decided after Ben's-bot review.
- Industry archetype location **parked** — stays in `vcc-valuations` for now; may relocate to a platform-level repo when other archetype consumers (NAB / ANZ / CBA VCCs) materialise.
- Time budget for step 5 (populate IPL): provisional **3-week** working anchor pre-narrative-deliverables; bumped to roughly **4 weeks** (320–800 chat-min) once narrative deliverables were added in v3 of the build plan.
- Complementary-framework approach: **defined enum** (`payor_and_regulator | network_effect | resource_lifecycle | none`) chosen but **open-to-revisit** after first non-Porter archetype (banking / WBC) is populated.
- Probability-weighting of scenarios: **comparative output is canonical**; mode (a) blended expected value is *not* supported under §6.2 boundary-cases commitment. Optional per-scenario probability supported only for analyst-side indicative blends. Scenarios workshop chose not to populate the probability field in YAMLs at this stage.
- Narrative deliverables: six per company (scenario, industry view, company positioning, scenario impact, valuation note, thesis) — see §16.1.
- **Workshop refinement on §6.2 framing:** scenarios are boundary cases except for the most-likely interior (Muddle Through). The set spans the plausible range; it doesn't aim for exhaustive coverage. (§6.2 with workshop refinement.)
- **US powerhouse as cross-cutting assumption.** Tara's view — the US economy is structurally stronger than consensus credits. Handled implicitly in each scenario's narrative rather than as a structured regime tag.
- **Climate posture and demographic response also cross-cutting**, addressed in each scenario's narrative, not as structured regime tags. Tara's preference.
- **Terminal-growth-from-demographic-trajectory.** Scenario × company × geography-conditional. Even when the 2040s skilled-migration cliff sits beyond the explicit forecast horizon, terminal growth must reflect the demographic-adaptation trajectory. Captured as §9.7 review item 9 in architecture spec (added 16 May 2026).
- **AI Productivity Lag insight (workshop):** AI doesn't need to deliver economy-wide TFP gains to be useful for labour substitution. Rents capture asymmetric — platform owners win; labour-cost containment in white-collar work is the working channel. China's bipedal-robotics is uniquely advantaged in physical-substitution domains.
- **DNL Q1-Q8 review + Five Forces spine + tax-rate consistency (9 June 2026).** Substantive day of methodology refinement. (a) Q1-Q8 review fixes: base EBIT corrected to AUD 480m (corporate already in segment guidance per slides 27-28); margin glide reconciled to FY27 exit run rate; OCF run rate AUD 500m (was AUD 290m, depressed by H1 TWC unwind); full Fertilisers separation map per slide 29 added to equity bridge (IPF Distribution +AUD 125m face, Geelong remediation -AUD 35m, Gibson Island -AUD 97m, transaction costs -AUD 11m, PH contingent +AUD 100m face); Period A buyback adjustment removed (value-neutral). (b) WACC discipline: Hamada formula confirmed; world-index basis for beta (DNL beta 0.95 vs 1.15 ASX200); RFR convention is 10Y on-the-run CGS YTM. (c) Tax discipline (methodology section 3.6 new): effective rate (FY26 22.5%) glides linearly to blended statutory (27.5%, computed from jurisdictional weights x statutory rates) over the explicit horizon. Single rate consistency principle: same blended statutory used for terminal operating tax, WACC debt-tax-shield, and Hamada re-levering. (d) Five Forces spine for Step 3 company position (methodology section 3.3 new): per-force traversal (buyer, supplier, new entrants, substitutes, rivalry) with industry rating vs company-relative + mechanism + quantified delta + where_captured. Replaces earlier catch-all 'company offset.' DNL net: -25bps (rivalry/competitive position -30, rivalry/product-mix -10, new entrants/DNEL pipeline +15). (e) Source-document ingestion discipline (methodology section 14 new): standing checklist (investor pres, half-year results, statutory accounts, continuous disclosure, transcripts, sustainability); per-company documents register; refresh cadence; handoff spec for Ben's data workstream. Headline: Muddle Through per share AUD 2.90 (v3) -> AUD 3.59 (v4 with full discipline), essentially at market AUD 3.61. Framework discriminating power now in scenario asymmetry, not in disagreement with consensus on central case. Architecture spec bumped v0.3.1 -> v0.4 (additive only).
- **Gas-contract roll-off overlay added (29 May 2026).** Tara flagged that the US gas-contract roll-off (2028-2030 window) was narrative-only and the margin glide path actually moved the wrong way (transformation drove margins up through FY31 — exactly when the gas-cost advantage erodes). Resolution: added a structural-headwind overlay to the margin glide of -50/-100/-150bps cumulative in Y3/Y4/Y5, partially offsetting the transformation tailwind. Methodology §3.2.1 captures the concept (sister to transformation overlay). Applied flat across scenarios for this iteration — future refinement could make scenario-conditional (bigger drag under high-gas scenarios like Stagflation/Disorderly Climate). Headline DNL per-share moves: MT AUD 3.22 → AUD 2.90 (vs market AUD 3.61, -20%); Orderly AUD 3.72 → AUD 3.36 (-7%); Stagflation AUD 1.12 → AUD 0.82; all scenarios drop AUD 0.31-0.36/share. Workbooks v3 in analyses/dnl/valuations/. Aligns with substack discipline of building structural risk into cash flows, not hand-waving to terminal state or adjusting WACC.
- **Reference texts and style anchors (28 May 2026).** Tara's go-to references: (a) Damodaran (Stern website, blog, books — particularly Investment Valuation, Narrative and Numbers, and the 2005 "Value of Control" paper); (b) Mercer's Business Valuation: An Integrated Theory, 3rd Edition (Mercer + Harms, 2021); (c) Clifford Ang's Applied Valuation; (d) Valuation Matters substack at valuationmatters1.substack.com (co-authored Stephen Reid + Tony Carlton). Style of thinking absorbed from KISS principle + control-premium-fallacy posts: (i) build risk and economic content into the cash flows, not into ad-hoc premia or discounts; (ii) "standard" adjustments applied rotely are suspect — case-specific mechanism is required; (iii) KISS / market efficiency / historical premia get arbitraged away; (iv) distinguish measurable from abstract (e.g. takeover premium != control premium); (v) double-counting check is the recurring red flag. The single-WACC discipline (methodology §3.5) is a direct application of (i) and (v).
- **Single-WACC discipline across scenarios (28 May 2026).** Resolution of the parked §9.7 review item 4 ("WACC scenario behaviour"). WACC is set at the valuation date and held constant across all scenarios. Rationale: each scenario already prices its risk through the cash-flow path; using a higher discount rate in a stress scenario double-counts risk. The marginal investor's required return is set by today's market conditions; it does not change conditional on which future state realises. Scenario rate-driver deltas (Rf, ERP, country risk) are retained in the impact matrix for narrative context but do NOT flow into the DCF discount rate. Terminal growth REMAINS scenario-conditional (it represents a structural economic state, not risk re-prici
## UI — β-workbench button relocation + beta-determinants comps (11 July 2026, new chat)

Stephen's UI asks (DNL-first, real-statements/hybrid-betas per AskUserQuestion):
1. **Button moved.** The "β / cost-of-capital workbench →" opener now sits **directly under the
   "Beta — peer triangulation" block** in the Discount-rate detail (was at the very bottom, below all
   seven theory panels). Done with a `<!--BWSLOT-->` marker inserted in the `detail.discount` assembly
   (gen_ui.py line ~806, between `_discount` and `dr_theory_html`); the discount branch replaces the
   marker with the button, falling back to append if absent. Applies to all three (shared render).
2. **Beta determinants comps (DNL only this pass).** New "Beta determinants — why these asset betas"
   disclosure table in the β workbench (below the peer table): per subject + selected peer, the three
   drivers — **financial leverage** (D/E · ND/EBITDA, from reported gearing), **operational leverage**
   (DOL, estimated), **revenue/cash-flow cyclicality** (cycle corr., estimated) — with low/med/high
   chips and the resulting **asset β**. Framing: financial leverage = the Hamada levered-vs-unlevered
   gap; opLev + cyclicality set the asset beta itself. Closing `detNote` reads the set (Sasol high on
   all three → top β, excluded; DNL's ~78% contracted book dampens cyclicality). Hybrid data in
   `beta_data.py` (`det` dict on DNL subject + 4 comps + `detNote`); render **gated on `BW.subject.det`**
   so WBC/CSL are untouched until their pass.

**Edits done sandbox-side + cp** (the large-file truncation quirk) via python patch scripts with
assertions; backups in /tmp/gen_ui.bak.py, /tmp/beta_data.bak.py. **Verified:** build_cfgs + gen_ui
regen clean; all three CFGs parse as valid JSON; BWSLOT lands exactly after the peer-triangulation `<p>`;
DNL carries det on subject+4 comps+detNote, WBC/CSL carry none; DNL MT still 3.59 / scenarios intact;
all three app scripts pass `node --check`. Not browser-eyeballed (file:// limitation) — Stephen to view.

**Task 3 (5-yr statements tab) — BLOCKED on data.** DNL only has FY24/FY25/H1-FY26 clean in-repo;
pre-FY25 = IPL incl. the demerged fertiliser business (Phosphate Hill visible in the v6 workbook BS).
Stephen wants actual reported financials, not segment carve-outs. Awaiting his call: reconstruct a real
5-yr as-reported series from an EODHD DNL/IPL pull (Ben's feed), show the ~2 clean years we have now,
or build the tab on WBC/CSL first (clean multi-year EODHD CSVs) then adapt DNL.

**Next issue after the above (Stephen flagged, not started): lease accounting.**
Iteration ~4 this chat.

## UI — determinants footnotes + DNL 5-yr statements tab (11 July 2026, cont.)

Follow-ups on the same chat:
- **Determinants footnoted.** The β-workbench determinants table now has superscripts ¹–⁴ on the column
  headers and a numbered footnote block: ¹ financial leverage = reported gearing (ND/EBITDA, D/E, mocked);
  ² operational leverage = DOL = %ΔEBIT/%ΔRevenue ≈ 1+FC/EBIT (mocked estimate); ³ cyclicality = corr of
  real revenue growth vs GDP/industrial production (mocked estimate); ⁴ asset β = Hamada βu = βl/(1+(1−t)·D/E),
  computed live. Long inline caveat shortened to a one-line mock banner pointing at the footnotes.
  Mock values live in `beta_data.py` `det` dicts (ndeb/dol/cyc) + `gearingDE` + `detNote` — DNL only.
- **Task 3 built (DNL, real FY25 + mock prior 4y).** New **"Summary financials"** tab under Explore the
  build-up: Income statement / Balance sheet / Cash flow, FY21–FY25. **FY25 is real as-reported** from
  `data/financials/dnl.yaml` (P&L bridged with an "other opex" + "non-operating & significant items" line so
  it articulates; BS from the 30 Sep 2025 snapshot; CF = OCF/capex/FCF/dividends). **FY21–FY24 are mock**
  placeholders (continuing-ops basis), greyed with a "mock" badge per column, internally consistent (P&L
  articulates, BS balances exactly) and footnoted as pending the EODHD DNL/IPL pull. Pre-demerger IPL group
  (incl. fertilisers) deliberately NOT shown, per Stephen. Structured `_financials` in build_cfgs; new
  `financials_html()` renderer in gen_ui; tab gated to DNL (WBC/CSL unchanged).

All edits sandbox-side + regen; verified: 3× valid JSON, DNL tabs now include `financials` (WBC/CSL don't),
statements render with real FY25 (rev 3,710) + mock badges, all app scripts pass `node --check`. Backups in
/tmp/*.bak*.py. Not browser-eyeballed (file://).

**Next: lease accounting** (Stephen's flagged next issue). Iteration ~8 this chat.

## UI — Multiples tab: implied-by-DCF + cross-check (11 July 2026, cont.)

New **"Multiples"** tab (DNL only), per Stephen's design AskUserQuestion: both directions, forward/normalised
base (reported FY25 as reference), dedicated tab.
- **Metric selector:** EV/EBITDA · EV/EBIT · P/E (ar