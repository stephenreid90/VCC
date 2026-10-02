# VCC VALUATIONS — bridge note for a new chat, 2 October 2026

Supersedes the note of 22 September 2026.

**WHAT THIS IS.** A travelling snapshot. `WORKING_NOTES.md` is the live layer; **where the
two disagree, `WORKING_NOTES.md` wins.**

**HOW TO WRITE TO STEPHEN.** Plain, simple, professional English. Short sentences.
Problem first, then recommendation, then what you need from him. Numbered lists. Define a
term in a few words the first time you use it. Don't assume he remembers decision numbers;
say in a few words what each one means. (`notes/claude_writing_style_instruction.md`.)

## READ IN, IN THIS ORDER

1. `session_start.cmd`. If it is not green, stop and read why. Expected base ties:
   **DNL 2.138, WBC 30.03, CSL 195.78**; suite 498 passed, 2 deselected; SSOT lint 14/14.
2. `CLAUDE.md`. Standing rule 4 (every number comes from committed code, asserted by a
   test) and standing rule 5 (land once per sitting, at the end).
3. `WORKING_NOTES.md`, the HANDOVER block at the top (sitting of 2 October).
4. `DECISIONS.md` rows **D-71 and D-72** — the framework the whole model now sits on.
5. `analyses/dnl/five_forces_driver_gap_audit_2026-09-25.md` — the worklist for this chat.

## STATE — what the model does now (D-71, D-72, both landed and pushed)

1. **The explicit forecast period is a fixed ten years** for every company and scenario.
   It is declared (`data/companies/dnl.yaml` `horizon_years: 10`), not computed.
2. **Growth inside the ten years comes from each scenario's own year-by-year inputs.**
   The revenue chain (`translator.revenue_growth_chain_from_data`) reads, for each year,
   the scenario file's series for mining real growth, DM inflation (= the scenario's
   `cpi_inflation_advanced`) and gas price growth, interpolated between the anchor years
   1/3/5/7/10. Mining and gas are DERIVED series: mining = world real GDP plus a fixed gap;
   gas = the scenario's level until its equilibrium year, then the baseline. They are
   written by `scripts/derive_macro_driver_paths.py` and asserted by
   `tests/test_macro_driver_paths.py`. The old flat scalars in `dnl.yaml` are now the
   level anchors those derivations are calibrated to.
3. **Terminal growth is derived per scenario** (`terminal_growth_from_data`): the chain in
   equilibrium at year 10 (volume beta, ore-grade pickup, productivity, geo-mix and
   company offsets all switched off), capped at the scenario's nominal GDP. Today:
   MT 5.27%, OC 5.37% (capped), AI Lag 4.67%, Frag 4.45%, DCC 4.94%, Stag 3.19%.
   Stephen has ruled this settled. Nothing is typed.
4. **The headline terminal is excess-return convergence, then Gordon**
   (`FcfEngineInputs.terminal_form = "excess_return_convergence"`): the return on the
   closing capital base converges to the WACC over the declared decay horizon (12.5
   years, the 10–15 band's midpoint), symmetric — below-WACC converges up. Gordon stays
   selectable. Where no decay horizon is declared the assembler falls back to Gordon and
   says so; that fallback is ratcheted in `tests/terminal_form_baseline.json`.
5. **The margin shift is shaped by the scenario's phases** (`margin_shift_shape`): ramps in
   over the first phase, holds, then persists (structural: Fragmentation, Disorderly
   Climate) or reverts to zero by year 10 (cyclical: Stagflation only).
6. **D-36's growth fade still exists** but now only glides the chain's temporary extras
   onto g over the last 1–2 years. Leave it. Follow-up, not this chat: give those extras
   their own expiry years and retire the fade.
7. The standalone Excel workbook (`ui_prototypes/_generator/engine_workbook.py`) carries
   all of the above in formulas and ties to the engine on all six scenarios
   (`tests/dcf/test_dnl_workbook_tie.py`).

## RESULTS — read before quoting a level

| Scenario | 25 Sep | Now | Terminal form |
|---|---:|---:|---|
| Orderly Convergence | 2.16 | 2.49 | convergence |
| Muddle Through | 1.85 | 2.14 | convergence |
| AI Productivity Lag | 1.88 | 2.11 | convergence |
| Fragmentation | 1.09 | 1.58 | Gordon fallback (no decay horizon) |
| Stagflation Persists | −0.07 | 1.39 | Gordon fallback (no decay horizon) |
| Disorderly Climate | 0.82 | 1.08 | convergence |

Two story changes, both ruled SETTLED by Stephen on 2 October:

1. **Stagflation is no longer the worst case.** It is a cyclical scenario — its gas spike
   ends and its margin hit recovers at its own resolution phase (year 5). Disorderly
   Climate, whose carbon cost persists, is the floor.
2. **Terminal g of 3–5% replaces the typed 1.75–2.75%.** Under the convergence terminal g
   matters little once the excess return is gone (sized in the 2 Oct chat: 2.5% → 5% moved
   the MT terminal by ~3%, not 24%).

## THE PLAN FOR THIS CHAT — make the process repeatable; DNL is instance one, not the job

**Stephen's instruction (2 Oct, 15:55): the focus is a repeatable process, not a solution
for DNL.** Everything landed so far is correct for DNL but three pieces are still
DNL-shaped. Generalise each, prove it on DNL (no golden should move), then run it for WBC
and CSL. Order:

1. **Driver paths for any archetype, not just explosives.** Today
   `scripts/derive_macro_driver_paths.py` hard-codes DNL's two drivers and reads DNL's
   anchors. Make the archetype YAML declare, for each entry in `required_macro_drivers`,
   HOW it is derived from the world scenario — e.g.
   `derivation: {from: real_gdp_growth_world, method: spread, anchor: <company field>}` or
   `{method: transition_then_baseline, anchor: ..., baseline_scenario: muddle_through}` or
   `{method: scenario_series, series: cpi_inflation_advanced}` — and have one script
   derive every archetype's paths from those declarations. Add the derivation methods
   as a small enum with a test each. Schema: `IndustryArchetype` in
   `src/vcc_valuations/schemas/industry.py`; SSOT check 14 already reads the result.
   WBC and CSL declare no required drivers today; decide with Stephen which world-series
   each of their chains should read (bank: rates, credit cycle; CSL: plasma demand /
   healthcare inflation) and declare them.
2. **Terminal form in all three engines.** `terminal_form` / `convergence_years` exist
   only on `FcfEngineInputs`. Add the same two fields to `BankInputs` (ROE converging
   to Ke on book equity — same two-stage algebra, D-62 already states it in bank terms)
   and `SegmentInputs` (CSL's capital base exists, D-67). The assembler rule is the one
   D-71 already states: convergence where a decay horizon is declared, Gordon fallback
   otherwise, ratcheted in `tests/terminal_form_baseline.json` — extend that baseline to
   all eighteen pairs so the gap is visible.
3. **Decay horizons as a process, not a per-scenario favour.** The Five Forces question
   bank (`design/frameworks/five_forces_questions.md`) already defines the interview.
   Write the SHORT version that produces exactly the four `excess_return_defence` fields
   (moat_sources — barrier-bearing only, D-43a; decay_horizon band + basis;
   named_threat; sensitivity) for one company x scenario, as a checklist in
   `design/frameworks/`. Then run it: DNL Fragmentation and Stagflation (nothing exists
   for either), then WBC x6, CSL x6. Each one that lands shrinks two baselines.
4. **Terminal g for any company** — `terminal_growth_from_data` is generic in shape (chain
   in equilibrium, capped at scenario nominal GDP) but the "equilibrium = extras off"
   rule names explosives-chain coefficients. Make the archetype declare which of its
   chain terms are current-cycle (switched off at equilibrium) and which persist. WBC and
   CSL need the same declaration once their chains are declared (step 1).
5. **Write the process down as one page**: `design/methodology/adding_a_company.md` —
   the steps, in order, from "declare the archetype's required drivers and their
   derivations" to "every company x scenario has a decay horizon or a baselined reason".
   The seven §8 disclosures (build order item 6) belong at the end of that page.

**Done-when:** WBC and CSL run through the same four steps as DNL with no company-specific
code; both terminal-form baselines list only pairs that genuinely lack a Five Forces
answer; `adding_a_company.md` is the only document a new company needs.

**DNL loose ends, folded into the above:** Fragmentation and Stagflation decay horizons
(step 3); AI Lag gas assessed rather than baseline-by-absence (step 3, same interview);
`margin_delta_pp` as a company-level shaped path with its own check (step 1 — it is
company-specific, so it does NOT go in `required_macro_drivers`, which reads scenario
files); retiring D-36's fade once the chain extras have expiry years (step 4).

## TRAPS

1. **Stale git locks.** `.git/index.lock` / `.git/HEAD.lock` appear; ask for delete
   permission on the repo folder, then `rm -f` them. Push needs the token:
   `git push https://stephenreid90:$(cat .github-token)@github.com/stephenreid90/VCC main`.
2. **Standing rule 4 bites on every number.** Goldens: `tests/dcf/test_scenario_goldens.py`
   (`DNL_GOLDEN`, `TERMINAL_BREACH`, `dnl_shares`), `test_dnl_all_scenarios.py`,
   `test_dnl_mt_from_data.py`, `test_dnl_mt_ratified.py`, `test_terminal_form.py`,
   `test_terminal_option_sets.py`, `test_terminal_return_sets.py`,
   `test_two_stage_disclosure.py`, `scripts/session_start.py` `EXPECTED_BASES`.
3. **The workbook tie.** After any engine or data change: `python
   tests/dcf/golden/_recalc_generated_workbooks.py` (needs LibreOffice), then
   `test_dnl_workbook_tie.py`.
4. **The horizon-variant harness** (`scripts/size_horizon_variants.py`) reproduces
   PUBLISHED tables on frozen pre-D-72 inputs (`frozen_pre_d72_inputs` in its YAML). It is
   not the live build. Run with `PYTHONPATH=src:.`.
5. **D-43a:** gas contracts are a rent, not a barrier. Never list `resource` in
   `moat_sources` for a decay-horizon defence. The Disorderly Climate prose says
   "resource + scale"; the structured block correctly says `scale` only.
6. **Scenario series are percent_yoy; the engine works in decimals.** `macro_series_at`
   divides by `PERCENT`.

## COMMITS THIS SITTING (all on origin/main)

`14ba58a` D-71 (ten-year horizon, convergence terminal) · `1302575` D-72 principle +
translation proposal · `6590be5` writing-style note · `300fea4` D-72 implemented.
