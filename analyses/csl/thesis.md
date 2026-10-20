# CSL — Cross-scenario investment thesis

**Company:** CSL Limited (ASX:CSL)
**Version:** 2026-Q4-v3 (rewritten 20 October 2026 on the WACC, the ten-year explicit period and the excess-return terminal; supersedes v2 of 23 August 2026, which discounted at an 8.75 per cent cost of equity over five years to a Gordon terminal). Third test company after DNL and WBC.
**Type:** Cross-scenario investment thesis per §16.1 item 6. Segment-level industrial valuation (§11) with peer-triangulated β per §3.5.3 and the §16.3 market-gap treatment under D-92.
**Anchor period:** FY25 actuals (year ended 30 June 2025); net debt and issued capital anchored at the 1H26 close and rolled to the valuation date (D-87). USD functional currency throughout; AUD translation at 1.5152 only at the per-share line.
**Numbers:** every figure below is in `design/methodology/csl_thesis_set.yaml`, written by `scripts/size_csl_thesis.py` from the segment engine and asserted by `tests/dcf/test_csl_thesis_set.py`. The gap and fade-band figures repeat `csl_market_gap_set.yaml` (D-92); the terminal-return figures repeat `csl_terminal_return_sets.yaml` (D-86). The live workbook is the generated CSL workbook, recalculated in LibreOffice and pinned across the six scenarios in `tests/dcf/test_csl_workbook_tie.py`.

---

## One-paragraph thesis

CSL is three businesses sharing a balance sheet: CSL Behring, the largest plasma-derived therapies franchise in the world (about 72 per cent of group revenue, anchored on immunoglobulin for chronic, life-sustaining indications); Seqirus, a top-tier influenza-vaccine business with pandemic optionality; and Vifor, the iron-deficiency and nephrology franchise acquired in 2022. The economic character that matters for scenario work is that demand is essentially price-inelastic in volume terms — patients on immunoglobulin do not stop because the macro turns — so the franchise does not behave like a cyclical. Scenarios reach CSL through *margins, policy and the durability of its return on capital*, not through volumes. Donor-collection wage costs (CSL runs the largest plasma-collection network itself), energy and cold-chain costs, and what payors will permit CSL to price — chiefly US Medicare Part D — are the live channels; the plasma keeps flowing in all six states of the world. The result is a distribution that is narrower than DNL's and wider than we first thought: a downside-to-upside asymmetry of 1.91×, between the bank's near-symmetry and the explosives maker's cyclical skew. The uncomfortable feature is the level. Every scenario, including the Stagflation downside boundary, sits above the 15 June 2026 market price — Muddle Through by 100 per cent. We do not reconcile that gap. Under D-92 we state the assumptions that produce it, show what each is worth, and leave the reader to change the ones they disagree with.

## Calibration anchors

Per `data/companies/csl.yaml`, `data/financials/csl.yaml` and the engine:

| Anchor | Value | Source / note |
| --- | ---: | --- |
| Anchor year | FY25 (ended 30 June 2025) | Disclosed segment accounts |
| Group revenue FY25 | USD 15,558m | Behring 11,158 / Seqirus 2,166 / Vifor 2,234 |
| Group EBIT margin FY25 | 27.5% | Segment operating result less corporate and R&D |
| Explicit period | ten years, FY26–FY36 | D-71; mid-period discounting |
| Discount rate | WACC 8.12% | D-84: Re 8.75% (4.50% + 0.85 × 5.00%) at 87.1%, after-tax kd 3.85% at 12.9% |
| Target capital structure | net debt 1.8× EBITDA over EV 14× EBITDA | D-06, still provisional: the 14× has no independent support |
| β selected | 0.85 | Peer triangulation (Grifols, Takeda, Sanofi cluster 0.7–0.9); the measured 0.094 is an AUD price on an AUD index for a USD business, and is discarded per §3.5.3 |
| Terminal form | excess-return convergence, 20-year fade | D-62/D-71: the return earned on capital fades to the WACC over the moat decay band's midpoint (D-93: 15–25 years), then growth continues at the scenario rate |
| Invested capital, end of forecast (Muddle Through) | USD 23,494m excluding goodwill | D-44/D-67: net PP&E including right-of-use, intangibles excluding goodwill, non-cash working capital |
| Working capital | 35% of the change in revenue | Derived from six years of balance sheets (23 August 2026) |
| Capex / D&A | 4.5% / 6.0% of revenue | Explicit period |
| Net debt at valuation date (Muddle Through) | USD 7,881m | D-87: 9,100 at 31 December 2025, less operating cash flow, plus half a year of capex and the declared interim dividend |
| Restructuring cash to come | USD 507m | FY26–27 |
| Issued shares | 482.13m | 1H26 statutory accounts, Note 6(c) |
| Market reference price | AUD 105.53 on 15 June 2026 | D-92: not refreshed; 61 per cent below the 52-week high of AUD 269.15 |
| Sell-side 12-month target | USD 96.75 (AUD 146.60) | 16-analyst mean at the June read |

## Where the value sits — cross-scenario distribution

| Scenario | Per share USD | Per share AUD | vs market | vs Muddle Through | Terminal share of EV | Dominant channel |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| Orderly Convergence | 162.67 | 246.47 | +134% | +16.7% | 55% | Faster trough exit; full +250bps Behring closure; collection-cost relief |
| **Muddle Through (central)** | **139.36** | **211.15** | **+100%** | baseline | 53% | Secular plasma growth after the FY26 trough; +150bps closure |
| AI Productivity Lag | 134.19 | 203.32 | +93% | −3.7% | 52% | White-collar cost relief offset by a softer macro and lower terminal growth |
| Disorderly Climate | 114.46 | 173.43 | +64% | −17.9% | 49% | Carbon-cost margin compression; partial Seqirus pandemic offset |
| Fragmentation | 108.39 | 164.23 | +56% | −22.2% | 49% | China Ig access and localisation; closure stalls; tax to 20% |
| Stagflation Persists | 94.85 | 143.71 | +36% | −31.9% | 46% | Donor-wage and payor squeeze; closure reverses |

Upside (Orderly less Muddle Through) is AUD 35.32; downside (Muddle Through less Stagflation) is AUD 67.44; the ratio is **1.91×**. The v2 thesis put it at 1.33×. Our view of CSL's demand has not changed; the widening is what the ten-year explicit period and the excess-return terminal do to a margin story. Under the old five-year Gordon build, each scenario's margin difference was capitalised once, at year five. Now the scenario runs for ten years, and the return it leaves the capital base earning at year ten is what the terminal fades from. A scenario that erodes margin therefore erodes the starting point of the fade as well, and a 32 per cent fall in Stagflation is the result. The terminal is 46 to 55 per cent of enterprise value across the set, down from about three-quarters in v2, because ten explicit years carry more of the value — but the judgement that moves the number most is still the one about the terminal: how high a return CSL earns at the end of the forecast, and how long it takes to fade.

What follows is the intuitive reading of each scenario — the macro story, the channels through which it reaches CSL, and why the number lands where it does. The thread to hold throughout: the revenue line moves less than the margin line, and the margin line moves less than the terminal return.

**Muddle Through (USD 139.36 / AUD 211.15) — the central case.** Post-2022 friction persists without crushing demand; US inflation stays sticky and growth continues at 2 to 2.5 per cent. Segment growth runs on US real GDP plus advanced-economy CPI (D-82), with no healthcare price premium over CPI (D-89): the price and volume split is a reporting line and moves no value. Behring starts FY26 at −0.8 per cent as the Medicare Part D redesign and the China access soft patch annualise out, then climbs to 5.0 per cent by FY36; Seqirus runs to 1.5 per cent and Vifor to 6.5 per cent. The peer-gap closure overlay delivers +150bps to Behring over six years (the full +250bps is reserved for the upside), and group EBIT margin rises from 27.5 to 34.7 per cent at FY36 before the terminal normalises it to 30 per cent. That leaves the capital base earning 27.6 per cent at the end of the forecast, against an 8.12 per cent WACC, and the fade takes twenty years to close the difference. The number lands at double the market price for one reason: the engine treats a 27.6 per cent return on USD 23.5bn of capital as a franchise that takes two decades to become ordinary. The market, at AUD 105.53, plainly does not.

**Orderly Convergence (USD 162.67 / AUD 246.47, +16.7 per cent) — the upside boundary.** Inflation re-anchors, real rates normalise, a productivity surprise lifts growth and eases cost pressure at once. This buys CSL a faster exit from the Behring trough (flat in FY26 rather than down, 6.0 per cent by FY36) and genuine relief on donor-collection wages, which is what makes the *full* +250bps closure credible rather than aspirational. Terminal margin lifts to 31.5 per cent; the earned return at year ten is 31.2 per cent. The instructive point is how modest the upside is. A defensive staple cannot accelerate the way a cyclical recovers off a trough; there is no operating leverage waiting in plasma. The upside is the quiet compounding of a good franchise in a kind world, and it is worth about a sixth.

**AI Productivity Lag (USD 134.19 / AUD 203.32, −3.7 per cent).** Foundation models advance and agents proliferate, but the gains concentrate in platform owners and show up mainly as white-collar wage containment. CSL has a meaningful professional cost base — roughly USD 1bn of G&A and USD 1.4bn of R&D — so the channel is a mild margin tailwind: Behring closure of +175bps rather than +150bps. The same scenario carries softer growth, so US real GDP runs only 0.2 points above the world path (D-90) and terminal growth drops to 4.55 per cent. The two nearly offset; the earned return is 27.0 per cent and CSL lands a touch below the central case. The technology axis barely touches a plasma franchise, and a near-neutral answer is the right one.

**Disorderly Climate (USD 114.46 / AUD 173.43, −17.9 per cent).** The climate transition crystallises disorderly: carbon-cost pass-through runs inflation at 3 to 5 per cent and disrupts across sectors. CSL is exposed through cost, not demand. Fractionation is energy-intensive and the distribution chain is cold-chain dependent, so the Behring closure goes to −50bps. The one genuine offset in the portfolio sits here — Seqirus carries pandemic and health-disruption optionality, so its growth runs at 2.1 per cent against 1.5 in the central case and it gains 50bps of margin. Terminal margin 28 per cent, earned return 23.8 per cent. The Seqirus cushion is why this scenario lands *better* than Fragmentation despite a larger headline cost shock.

**Fragmentation and Resource Nationalism (USD 108.39 / AUD 164.23, −22.2 per cent) — the second-worst.** Trade barriers harden, supply chains localise, and China market access becomes a geopolitical instrument. CSL's model — collect in the US, fractionate and distribute globally — is structurally awkward in a fragmenting world, and Behring's China immunoglobulin line is the most exposed revenue in the group: Behring starts FY26 at −1.4 per cent and reaches only 3.5 per cent by FY36. Peer-gap closure stalls at zero across all three segments as the cost of operating across blocs erodes the efficiencies it depended on, and the effective tax rate drifts to 20 per cent. With no offsetting segment, the channels compound: terminal margin 28.2 per cent, earned return 22.9 per cent, and Fragmentation becomes the binding downside short of outright stagflation.

**Stagflation Persists (USD 94.85 / AUD 143.71, −31.9 per cent) — the downside boundary.** Inflation un-anchors above 4 per cent, growth recesses, an energy shock lands. This is the worst case and the clearest illustration of the thesis, because plasma demand still holds — these are essential therapies — so the stress arrives as margin and as the return the franchise is left earning. Donor-collection wages surge (supplier power at full stretch), payors press on price in a fiscally strained state (Part D with no relief), and closure does not merely stall but reverses: Behring runs 150bps below the FY25 base, Seqirus and Vifor 50bps below. Terminal margin falls to 26.5 per cent and terminal growth to 2.69 per cent. The earned return at year ten is 20.5 per cent — still well above the WACC, which is why even this scenario sits 36 per cent above the market and why the market, on the §16.3 reading, is pricing closer to Stagflation's terminal than to anyone else's.

## The gap to market — disclosed, not reconciled

The striking feature of the distribution is not its shape but that all of it sits well above where CSL trades. The v2 thesis responded with a reverse DCF: what β, what terminal margin, what growth would the market have to believe. Those figures were struck at the 8.75 per cent cost of equity and have not been rerun under the WACC, so we do not repeat them. Stephen's ruling (D-92) changed the question anyway. The 15 June 2026 price stands; the gap is an output of the framework's assumptions; the thesis states them and what each is worth, and does not re-tune the model until the gap closes — which would turn an analytical instrument into an expensive way of reproducing the share price.

Four assumptions do the work.

**The discount rate.** A WACC of 8.12 per cent on a target structure (D-84), built from a 0.85 β. The β is the single most contestable input for a stock that has fallen some 60 per cent from its high, and we have held it at 0.85 on purpose, so the gap stays visible rather than assumed away. The 12.9 per cent debt weight rests on a 14× through-cycle EV/EBITDA that D-06 records as provisional. Both are open to the reader.

**The terminal return and its fade.** CSL ends the central forecast earning 27.6 per cent on invested capital excluding goodwill (D-44), and the fade to the WACC runs twenty years (D-93). D-86 records the known weakness: a long fade on a high starting return is generous, and the fade evidence only supports it where a named barrier exists. Two disclosures follow. Including goodwill in the capital base — about 45 per cent of it — the starting return is 20.5 per cent and Muddle Through is AUD 209.53, so the goodwill treatment is not where the gap lives. And the fade band:

| Scenario | 15 years | 20 years | 25 years |
| --- | ---: | ---: | ---: |
| Orderly Convergence | 223.54 | 246.47 | 266.33 |
| Muddle Through | 193.08 | 211.15 | 226.66 |
| AI Productivity Lag | 186.76 | 203.32 | 217.32 |
| Fragmentation | 153.63 | 164.23 | 172.73 |
| Disorderly Climate | 162.06 | 173.43 | 182.56 |
| Stagflation Persists | 136.06 | 143.71 | 149.62 |

The lowest value in the band, AUD 136.06, is still above the price. The band does not close the gap, and neither does any single assumption above; the price can only be reached by stacking pessimism across several at once.

**Terminal growth.** Set by scenario from the growth the explicit period ends on, 4.86 per cent in the central case. That is a nominal rate, and a high one to carry in perpetuity; it is the one of the four we would look at first.

**The price date.** 15 June 2026, with no refresh scheduled. The sell-side mean target of USD 96.75 (AUD 146.60) at that date sits between the market and our Stagflation case, and was being cut hard.

There are two honest readings, and we decline to collapse them. The first is that the framework is too generous, and the candidates are the four above. The second is that the market is pricing a permanent de-rating of CSL's franchise — Part D, China, plasma-collection economics, the end of the high-growth era — and the framework, by letting a 27.6 per cent return take twenty years to fade, simply disagrees. Per §16 the gap is an informative output, not a calibration error to be engineered away.

## Three transmission channels, mapped to Five Forces

CSL's scenario exposures resolve into three channels, each tied to a force in the segment-level Five Forces decomposition.

**1. Plasma-collection economics — supplier power.** The "suppliers" in the plasma business are individual donors at CSL's collection centres, and CSL runs the largest such network in the world. Vertical integration is a structural advantage in normal times — the closure of 22 underperforming centres in FY26 is exactly the variable-cost management it affords — but the same integration makes the margin sensitive to US frontline wage inflation, because the donor-facing cost base is labour. This is the channel that does the damage in Stagflation. Watch the gap between US wage growth and CSL's disclosed gross-margin trajectory, and litres per centre as the management lever.

**2. US healthcare policy — buyer power.** CSL's buyers are payors — Medicare, private insurers, national health systems — and the force is moderate because plasma therapies are essential and largely price-inelastic in volume. The live pressure is the Medicare Part D redesign, roughly USD 100m on immunoglobulin in 1H26 and the dominant policy risk in the company's own framing. It sits behind the FY26 Behring trough in every scenario and behind the deeper squeeze in Stagflation and Fragmentation. The structural question for the terminal is whether Part D is a one-off reset or the first move in extending price negotiation to plasma therapies — the bearish view embedded in the market price. Watch the scope of Part D negotiation lists.

**3. Return durability — rivalry, and the terminal.** The plasma industry is a global oligopoly — CSL Behring, Grifols, Takeda, Octapharma, Kedrion — in which CSL is typically the largest, and scale converts into lower marginal cost through fractionation efficiency. In the v2 build this underwrote a 30 per cent terminal margin held forever. In the current build it underwrites something more specific and more contestable: that the 27.6 per cent return CSL earns at year ten takes twenty years to fade to its cost of capital. Whether biosimilar and recombinant alternatives shorten that, and by how much, is the assumption on which the framework and the market most fundamentally disagree.

## What the framework adds versus the conventional view

Sell-side coverage of CSL at the June read was a study in momentum: the 16-analyst mean target tracking the share price down. The framework's contribution is not a better point estimate but a different object — a scenario distribution that separates what is cyclical and policy-driven from what would have to be permanent for the market to be right. Three additions:

1. **An asymmetry, quantified and explained.** At 1.91× the distribution is wider than the defensive signature we expected, and the reason is instructive: a ten-year explicit period lets margin scenarios compound into the return the terminal starts from. The scenarios that matter are margin scenarios, and the framework names them.
2. **The gap made explicit and reversible.** Rather than asserting a target, the thesis states the four assumptions that produce the gap, shows the fade band, and leaves each to the reader. That reframes the debate from "is CSL cheap" to "how long does a 27 per cent return last", which is the question actually worth arguing.
3. **One rule for the terminal.** The starting return is the earned return and the fade length is the moat band (D-86), the same rule for every company. Nothing is hand-set for CSL. The price of that discipline is a generous answer where the earned return is high; the benefit is that the generosity is visible and sized.

## Mental short-cut

CSL is a margin story that ends in a return story. In every scenario the plasma keeps flowing, so do not watch the revenue line — watch the gap between what CSL pays US plasma donors and what payors, chiefly Medicare, will let it charge. The six scenarios are six settings of that one dial, and they cash out in the return CSL is left earning at year ten (20 to 31 per cent) and the twenty years the engine gives it to fade. Half the value is in that terminal. The whole investment debate is whether the market's de-rating is permanent impairment or a policy-and-cost trough — and this framework, applied without intervention, takes the second view while showing exactly what you would have to believe to take the first.

## Implications — what to watch

1. **Medicare Part D scope.** Whether the redesign re-bases immunoglobulin once and growth resumes, or extends toward plasma therapies. This is the swing between the framework's terminal and the market's.
2. **US donor-collection wages versus gross margin.** The supplier-power channel; the clearest read on whether the margin thesis is holding.
3. **Behring trough shape.** Confirmation that FY26 is the bottom and the secular path resumes — the load-bearing assumption of Muddle Through.
4. **β and the target structure.** Held at 0.85 and 14× by choice for repeatability; the most defensible candidates for a merit-based correction if the de-rating proves structural. Revisit on evidence, not to match the price.
5. **Fade length.** Long-horizon signals on biosimilar and recombinant substitution — the assumption underwriting half the value, and the deepest point of disagreement with the market.

*Status: thesis v3, 20 October 2026. Per-scenario narratives per standing rule 2; gap treatment per §16.3 and D-92; β held at 0.85 per Stephen's decision. The v2 reverse-DCF figures are withdrawn until rerun under the WACC.*
