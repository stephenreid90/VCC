# Decay-horizon checklist (the short Five Forces interview)

**Purpose.** Produce, for ONE company x scenario, exactly the four fields of
`excess_return_defence` (schema `ExcessReturnDefence`, `schemas/linkage.py`) that the
terminal form reads (D-71): the headline terminal converges the return on the closing
capital base to the cost of capital over the declared decay horizon, then Gordon. Until
these four fields exist for a pair, the assembler falls back to Gordon and the pair sits
in `tests/terminal_form_baseline.json`. The long question bank
(`five_forces_questions.md`) is where the ratings come from; this page is only the last
step, from ratings to the four fields. Written 14 October 2026 (bridge note step 3).

**Where the answer goes.** `data/impact_matrix/by_industry/<archetype>.yaml`, under the
scenario's `terminal_roic` driver (create the driver if the scenario has none), as
`excess_return_defence:`. For a segment-valued company (CSL) the matrix file for each
segment archetype carries it.

**Rule to hold throughout (D-43a).** A RENT is a cash advantage with an end date (a gas
contract, an offtake contract, a patent on one product). It lives in the explicit period
and is never a `moat_source`. A BARRIER is what stops a rival taking the business (scale,
switching costs, a network, a licence, a rolling patent estate). Only barriers go in
`moat_sources`, and the horizon is set by the longest-lived barrier.

## The six questions

1. **Which way is the excess?** Read the D-42 diagnostic for the pair (terminal return on
   the whole capital base vs the cost of capital; `scripts/size_terminal_returns.py`).
   Above: the horizon is how long the excess lasts. Below: the horizon is how long the
   shortfall lasts before the return recovers to the cost of capital (D-71 is symmetric).
   If exactly at: write the defence anyway with the band the barriers support, so the
   pair is declared rather than absent.

2. **Which barriers hold the business, and which "defences" are really rents?** List the
   company's moat sources (`Moat.source_roles` in the company file) and the scenario
   write-up's "what defends" section. Strike every rent. What remains is `moat_sources`
   (snake_case names already used in the matrix: `scale`, `switching_cost`,
   `regulatory`, `network`, `brand`, `patent_estate`).

3. **Which band?** Read the archetype's three ratings per `terminal_value.md` §12: threat
   of new entrants sets the barrier height, rivalry sets the speed the excess is competed
   away, substitutes set the ceiling. Then place the pair:
   - **Short 5-10:** advantage visible but contestable; a named threat already moving.
   - **Medium 10-20:** structural advantage (scale, switching costs) with an identifiable
     erosion path.
   - **Long 20-30:** rooted in something rivals cannot readily replicate (licence,
     network, rolling patent estate plus brand).
   - **Indefinite:** oligopoly protected by regulation or systemic scale, no credible
     erosion path. Admissible for any barrier (D-58) but NEVER by omission, and always
     paired with `finite_horizon_sensitivity` and with a declared terminal return BELOW
     the one currently earned (`terminal_value.md` §12: "indefinite moats need a second
     lever, not a longer first one").
   Archetype ratings do not move by scenario, so the band is usually the same across a
   company's six scenarios. A scenario that shortens or lengthens it must say why in the
   `basis` (Disorderly Climate on DNL carries the risk in the sensitivity, not the band).
   Write the band as `years_low` / `years_high` (or `indefinite: true`) plus `basis`.

4. **What is the named threat?** One competitor, policy or substitution path that would
   compete the excess away (or, below the cost of capital, that would prevent the
   recovery). A named actor, not "competition".

5. **What is the sensitivity?** What the terminal does at the two band ends (D-63: the
   midpoint is the headline, the ends are the disclosure). State it in words; the sizing
   scripts carry the numbers.

6. **Is a terminal return declared?** Only if the scenario has actually formed the view
   (`declared_terminal_return` + `basis`). Absence is honest; a number copied off the
   engine makes the D-42 reconciliation vacuous.

## After the answer lands (every time, in this order)

1. Declare it on the matrix; run `pytest tests/test_ssot_lint.py tests/dcf/test_terminal_form.py`.
2. Remove the pair from `tests/terminal_form_baseline.json` and, if it was there,
   `tests/terminal_defence_baseline.json`.
3. Re-pin the golden in `tests/dcf/test_scenario_goldens.py` with the reason (the level
   moves: convergence replaces Gordon for that pair).
4. Regenerate the three sizing sets (`scripts/size_terminal_options.py`,
   `size_terminal_returns.py`, `size_two_stage_disclosure.py`) and the workbook oracles
   (`python tests/dcf/golden/_recalc_generated_workbooks.py`).
5. Record the ruling in `DECISIONS.md` if it changes a stated view; otherwise the matrix
   comment is the record.

## Worked example

DNL Muddle Through (`industrial_explosives.yaml`, `terminal_roic.excess_return_defence`):
above the WACC (1); `scale`, `switching_cost` -- the gas contracts struck as a rent (2);
medium band 10-15 from entrants low / rivalry high / substitutes low (3); Orica
competitive response (4); band ends as the disclosure (5); no declared return yet (6).
