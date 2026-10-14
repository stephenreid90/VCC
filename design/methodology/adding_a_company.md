# Adding a company — the process, on one page

**Status: written 14 October 2026 (bridge note step 5, D-78 sitting).** This is the only
document a new company needs. It lists the steps, in order, from the archetype's declared
drivers to "every company x scenario has a decay horizon or a baselined reason", and ends
with the seven terminal disclosures every write-up carries. Where a step has a longer
paper behind it, the paper is named; nothing here repeats it.

**The rule that runs through every step (D-73, D-78):** the process is the same for every
company. Company and driver names live in data files under `data/`; code reads
declarations. If a step seems to need a company's name in `src/`, the step is wrong.

## Before you start

1. Run `python scripts/session_start.py`. It must be green before anything is added.
2. Read `DECISIONS.md` (one line per ruling) before proposing a method. If the method
   exists, use it. If not, write the proposal in `design/methodology/` and get it ruled
   before building.
3. Pick the engine. Industrial (FCFF on invested capital, `dcf/fcf_engine.py`, DNL);
   bank (ROE on book equity, `dcf/bank_engine.py`, WBC); segment-valued (FCFF per
   segment, discounted at the cost of equity, `dcf/segment_engine.py`, CSL). A company
   that fits none needs a ruling before a line of code.

## The steps, in order

1. **Archetype.** Write or reuse `data/industries/<archetype>.yaml` (schema:
   `IndustryArchetype` in `schemas/industry.py`). It carries the Five Forces view, the
   scenario sensitivities, and three declarations the engine reads:
   `required_macro_drivers` (step 2), `growth_chain_terms` (step 4) and, for a bank, the
   `bank_archetype` block. A segment-valued company has one archetype per segment and
   declares `company_position.segment_level_valuation: true` (SSOT check 11: the fallback
   is declared, never inferred from a missing file).
2. **Macro drivers and their paths (D-37, D-72, D-73).** For each macro driver the
   archetype's growth chain reads, declare it under `required_macro_drivers` with a
   `derivation`: `scenario_series` (the scenario file carries it natively), `spread` (a
   scenario series plus a fixed gap, calibrated to a level anchor in the company file) or
   `transition_then_baseline` (the anchor until the scenario's equilibrium year, then the
   baseline scenario's). Run `python scripts/derive_macro_driver_paths.py`; it writes the
   paths into all six `data/scenarios/*.yaml` between BEGIN/END markers.
   `tests/test_macro_driver_paths.py` and SSOT check 14 assert them. A driver the
   scenarios do not carry is a scenario-development item, not a new company series
   (D-73 ruling 1: proxies from existing series, not new ones).
3. **Company file and financials.** `data/companies/<id>.yaml` holds the judgement layer
   (`normalised_baseline`: margins, the growth chain's typed coefficients, the beta
   selection, overlays per scenario) and `company_position` (moat sources with D-43a
   roles: a RENT has an end date and lives in the explicit period; a BARRIER is what the
   decay horizon measures). `data/financials/<id>.yaml` holds observed inputs only
   (statements, market data, share count and net debt anchored at a dated balance). The
   SSOT lint (`tests/test_ssot_lint.py`, 14 checks) enforces the split: no derived value
   stored, no judgement in layer 1, every rate declares the basis it was struck on, the
   anchor dates pair up. Run it after every edit.
4. **Equilibrium chain terms (D-72, D-78).** Where the company's terminal growth is
   DERIVED from its growth chain, the archetype must classify every numeric term of the
   chain's `shared` block in `growth_chain_terms`: `current_cycle` (switched off at the
   end of the explicit period; give the `equilibrium_value` and a `basis`) or
   `equilibrium` (keeps its typed value). `translator.equilibrium_chain_terms` raises on
   an unclassified term. Terminal growth is then the chain in equilibrium at year ten,
   capped at the scenario's nominal GDP. Where terminal growth is still typed per
   scenario (WBC and CSL today), declare `growth_chain_terms: []` and record that
   deriving it is open.
5. **Ten years and the terminal form (D-71, D-74).** The explicit period is a fixed ten
   years for every company (`horizon_years: 10`). Typed glides hold their last value to
   year ten. The headline terminal is convergence over the declared decay horizon, then
   Gordon; where no horizon is declared the assembler falls back to Gordon and the pair
   sits in `tests/terminal_form_baseline.json` with a reason. Paper:
   `design/methodology/horizon_and_terminal_convergence.md`.
6. **Decay horizons, all six scenarios (D-63, D-75).** Run the short Five Forces
   interview in `design/frameworks/decay_horizon_checklist.md` for each company x
   scenario. It produces exactly the four `excess_return_defence` fields on
   `data/impact_matrix/by_industry/<archetype>.yaml`: `moat_sources` (barriers only),
   `decay_horizon` (band + basis; indefinite only with a finite sensitivity beside it,
   D-58), `named_threat`, `sensitivity`. Each answer that lands removes the pair from
   `terminal_form_baseline.json` and `terminal_defence_baseline.json`. Done when both
   baselines list only pairs with no Five Forces answer yet.
7. **Declared terminal return (D-76), if a view exists.** A declared
   `declared_terminal_return` is the rate the convergence starts from; absent, the earned
   return is. It moves the level, so size it first (`scripts/size_terminal_returns.py`,
   checklist question 6) and never copy it off the engine's own output.
8. **Pin the numbers (standing rule 4).** Every figure that reaches a document comes from
   committed code asserted by a test. Add the company to `tests/dcf/test_scenario_goldens.py`
   (six levels and six terminal shares; the 70% terminal-share line is read, not assumed),
   to `scripts/session_start.py` `EXPECTED_BASES`, and to `ui_prototypes/_generator/build_cfgs.py`.
   Regenerate the three sizing sets (`size_terminal_options.py`, `size_terminal_returns.py`,
   `size_two_stage_disclosure.py`). If the company gets a generated workbook, it must be
   formulas only (standing rule 1) and tie the engine in LibreOffice
   (`tests/dcf/golden/_recalc_generated_workbooks.py`).
9. **Write-up (standing rule 2).** One intuitive narrative per scenario, the terminal
   section carrying the seven disclosures below, and a line in `DECISIONS.md` for every
   ruling the company needed. Land once, at the end of the sitting (standing rule 5).

**Done when:** the company runs through steps 1 to 8 with no company-specific code; both
terminal baselines list only pairs that genuinely lack a Five Forces answer; the suite,
the SSOT lint and the base ties are green in `session_start.py`.

## The seven terminal disclosures (D-66; `terminal_value.md` §8)

Every terminal, whatever its basis, is reported with the same set, in this order:

1. **Terminal value as a share of total value.** How much of the answer rests on it.
2. **TV / capital.** The implied terminal price-to-book; 1.00 is convergence. The only
   measure that reads the same for an industrial and a bank.
3. **Implied perpetual return.** The single return on all capital, held forever, that
   reproduces the TV.
4. **Implied return on new capital** (single-stage bases only).
5. **Implied forward multiples.** EV/EBIT and EV/EBITDA for industrials; P/E and P/B for
   banks, on year T+1.
6. **Implied moat.** Years from the valuation date, "perpetual or more", or "other side of
   capital" where the TV assumes a recovery or collapse the forecast does not show.
7. **Value per share under each basis.** So the cost of the choice is in the reader's
   currency.

Where a market price exists, add the line: what the market price needs the terminal to be,
on the same forecast.
