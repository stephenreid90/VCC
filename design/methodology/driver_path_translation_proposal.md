# Driver paths inside the explicit period — translation proposal (D-72 implementation)

**Status: RULED 2 Oct 2026 (Stephen: §0 equilibrium chain capped at nominal GDP; §2 spread; §3 yes; §4 as proposed) and IMPLEMENTED the same sitting -- see D-72 in DECISIONS.md. Kept as the record of the reasoning and the tables.**
Companion to D-71 (fixed ten-year horizon, convergence terminal) and D-72 (growth inside
the explicit period is the chain evaluated per year on the scenario's own paths; terminal
`g` is the chain at the scenario's equilibrium, not a typed overlay). Nothing in this file
is wired; the goldens are unchanged by it.

## 0. The finding that reframes the job

The revenue-growth chain, evaluated on today's flat scalars, gives DNL a through-cycle
NOMINAL growth of **5.6% to 7.6%** depending on scenario (volume = 1.15 × mining real
growth + 0.4pp ore-grade pickup; pricing = 0.7 × DM inflation + 0.3 × gas + 0.5pp
productivity). The typed terminal `g` is **1.75% to 2.75%**. The scenario files' own
year-10 world nominal GDP is **~5%**.

| Scenario | Chain nominal growth (today) | Typed terminal g | Scenario yr-10 world nominal GDP |
|---|---:|---:|---:|
| Muddle Through | 6.2% | 2.50% | ~5.3% |
| Orderly Convergence | 7.5% | 2.75% | ~5.3% |
| AI Productivity Lag | 5.6% | 2.25% | ~4.8% |
| Fragmentation | 6.4% | 2.25% | ~5.3% |
| Disorderly Climate | 7.6% | 1.75% | ~5.2% |
| Stagflation Persists | (chain) | 2.25% | (series ends yr 5) |

So D-36's two-year fade is currently bridging a **~4pp gap** between the chain and the
terminal with no economics behind it — that is the flat-growth problem Stephen named, in
numbers. Two things follow, and both are decisions rather than data:

1. **The chain as written is a current-cycle model, not an equilibrium one.** Its
   above-GDP terms (mining beta 1.15, the 0.4pp ore-grade pickup, the 0.5pp productivity
   sharing) cannot hold forever — a mature explosives company does not outgrow world
   nominal GDP in perpetuity. D-72 ("terminal g = the chain at equilibrium") therefore
   needs an **equilibrium reading of the chain**: which coefficients persist in the
   scenario's equilibrium phase and which are cyclical. Proposed: in equilibrium the
   mining beta is 1.0, the ore-grade pickup and productivity sharing are zero, and the
   company offset is zero (the Five Forces offsets are time-limited by their own
   description) — so terminal g = mining real growth at equilibrium + 0.7 × equilibrium
   DM inflation + 0.3 × equilibrium gas growth. On Muddle Through that is roughly 2.3%
   real-ish + 2.7% pricing ≈ 5.0% nominal, i.e. world nominal GDP, not 2.5%.
2. **Or the typed g stands and the chain's above-GDP terms are declared to decay inside
   the explicit period** — which is what the fade does today, just without saying so.

Stephen to rule: (1) equilibrium chain (my recommendation — it is the only reading
under which "growth is driven by the scenario and the industry" is literally true at
every year including the terminal), or (2) keep a typed g and make the decay explicit.
Note (1) moves every DNL level materially upward (a ~5% terminal g against an 8.9%
WACC is a far larger terminal than 2.5%) — which is precisely why it has to be a ruling
and not a quiet fix. A terminal g at world nominal GDP is standard practice; a chain
that says 6% forever is not.

## 1. `dm_inflation` — wire to the scenario's own `cpi_inflation_advanced` (agreed 25 Sep)

Mechanical. Interpolated at years 1/3/5/7/10 from the scenario series; held after its
last point.

| Scenario | yr1 | yr3 | yr5 | yr7 | yr10 | flat today |
|---|---:|---:|---:|---:|---:|---:|
| Muddle Through | 3.0 | 3.0 | 3.0 | 3.0 | 3.0 | 2.5 |
| Orderly Convergence | 2.8 | 2.4 | 2.3 | 2.3 | 2.3 | 2.0 |
| AI Productivity Lag | 3.0 | 3.0 | 3.0 | 2.9 | 2.8 | 2.5 |
| Fragmentation | 3.2 | 3.5 | 3.5 | 3.4 | 3.3 | 3.5 |
| Disorderly Climate | 3.5 | 4.5 | 4.0 | 3.6 | 3.0 | 3.5 |
| Stagflation Persists | 5.0 | 5.0 | 4.0 | 3.5 | 3.5 | 4.5 |

Consequence to disclose: the scenario headline CPI sits ~0.5pp above the flat
"through-cycle pricing" value on the central scenarios, so pricing growth rises ~0.35pp
on Muddle Through. The 12 Aug 2026 note in `dnl.yaml` deferring exactly this is closed
by it.

## 2. `global_mining_real_growth` — shape from `real_gdp_growth_world`, level from the flat value

Mining growth is a function of world growth plus a scenario-specific story (supercycle
premium in Orderly Convergence, bloc-disruption drag in Fragmentation, stall in
Stagflation), which is what the existing flat values encode. Proposal: keep the
scenario's own level as an **additive spread** to the world real-GDP path, calibrated so
the path's average reproduces the flat value.

| Scenario | spread | yr1 | yr3 | yr5 | yr7 | yr10 |
|---|---:|---:|---:|---:|---:|---:|
| Muddle Through | +0.20 | 2.5 | 2.5 | 2.5 | 2.5 | 2.5 |
| Orderly Convergence | +0.96 | 3.8 | 4.1 | 4.2 | 4.1 | 4.0 |
| AI Productivity Lag | +0.06 | 2.1 | 2.0 | 2.0 | 2.0 | 2.1 |
| Fragmentation | −0.50 | 1.7 | 1.3 | 1.5 | 1.5 | 1.5 |
| Disorderly Climate | −0.02 | 2.0 | 1.8 | 2.0 | 2.1 | 2.2 |
| Stagflation Persists | −1.86 | 0.1 | −0.4 | −0.1 | 0.1 | 0.1 |

Spread, not multiple: a multiple of zero (Stagflation's flat 0.0%) would hold mining at
exactly zero in every year regardless of the world, which is not a model of anything.
Honest caveat: the scenario files' world-GDP series are themselves nearly flat, so the
within-scenario variation this produces is small. The transition dynamics the scenarios
describe live mostly in margin and gas, not volume — §3 and §4 are where the shape is.

## 3. `gas_price_growth` — level from the flat value, shape from the scenario's `time_profile`

No series exists anywhere. Proposal: the existing flat value is the scenario's
TRANSITION-phase gas price growth; it applies through the scenario's transition phases
and reverts to the baseline (Muddle Through's 2.0%) from the equilibrium year. Elevated
price GROWTH during a transition leaves a structurally higher price LEVEL in equilibrium
with normal growth thereafter, which is what "new equilibrium" means.

| Scenario | transition value | equilibrium year | yr1 | yr3 | yr5 | yr7 | yr10 |
|---|---:|---:|---:|---:|---:|---:|---:|
| Muddle Through | 2.0 | 1 | 2.0 | 2.0 | 2.0 | 2.0 | 2.0 |
| Orderly Convergence | 1.5 | 5 | 1.5 | 1.5 | 2.0 | 2.0 | 2.0 |
| AI Productivity Lag | (none assessed) | 8 | 2.0 | 2.0 | 2.0 | 2.0 | 2.0 |
| Fragmentation | 4.0 | 10 | 4.0 | 4.0 | 4.0 | 4.0 | 2.0 |
| Disorderly Climate | 6.0 | 6 | 6.0 | 6.0 | 6.0 | 2.0 | 2.0 |
| Stagflation Persists | 5.0 | 5 | 5.0 | 5.0 | 2.0 | 2.0 | 2.0 |

(Interpolation between anchors makes the hand-off to baseline a ramp, not a step.)
AI Lag is set to baseline because its own write-up never assessed gas — the genuine gap
the audit lists; it is a placeholder with that label, not a view.

## 4. `margin_delta_pp` — level from the stated ranges, shape from the `time_profile`

Each scenario write-up already states a pp range; the overlay carries a point inside or
at the edge of it (Fragmentation −3.0pp vs "−200 to −300bp"; Disorderly Climate −3.0pp
vs "−200 to −400bp"; Stagflation −7.5pp vs EBIT "14% to 8–10%" plus the gross-margin
range). Proposal: ramp in over the first phase, hold through the transition, then at the
equilibrium year either PERSIST (structural — Fragmentation's duplication costs,
Disorderly Climate's carbon cost) or REVERT (cyclical — Stagflation's resolution phase).
Stephen to confirm persist/revert per scenario; the magnitudes stay as typed.

## 5. What this does to D-36

Once §1–§4 land and D-72's equilibrium chain is ruled, the chain lands on the terminal
g by construction at year 10 and D-36's fade becomes a safety net that never fires.
Retire it then, not before.

## 6. What this needs from Stephen

1. §0: equilibrium chain (recommended) or typed g with explicit decay.
2. §2: spread (recommended) or multiple.
3. §3: the transition-then-baseline shape for gas, and whether AI Lag stays at baseline.
4. §4: persist vs revert per scenario for the margin shift.
