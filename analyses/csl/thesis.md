# CSL — Cross-scenario investment thesis

**Company:** CSL Limited (ASX:CSL)
**Version:** 2026-Q2-v1 (25 June 2026). First cross-scenario thesis for CSL; third test company after DNL and WBC.
**Type:** Cross-scenario investment thesis per §16.1 item 6. Segment-level industrial valuation (§11) with peer-triangulated β per §3.5.3 and the §16 market-vs-framework gap treatment.
**Anchor period:** FY25 actuals (year ended 30 June 2025). USD functional currency throughout; AUD translation at spot 1.5152 only at the per-share line.
**Companion workbooks:** `csl_muddle_through_valuation_v4.xlsx` (Muddle Through, terminal-capex-consistent), `csl_scenarios_comparison_v2.xlsx` (six scenarios + §3.5.7 market-implied tab).

---

## One-paragraph thesis

CSL is three businesses sharing a balance sheet: CSL Behring, the largest plasma-derived therapies franchise in the world (about 72 per cent of group revenue, anchored on immunoglobulin for chronic, life-sustaining indications); Seqirus, a top-tier influenza-vaccine business with pandemic optionality; and Vifor, the iron-deficiency and nephrology franchise acquired in 2022. The economic character that matters for scenario work is that the demand is essentially price-inelastic in volume terms — patients on immunoglobulin do not stop because the macro turns — so the franchise does not behave like a cyclical. The consequence runs through the whole analysis: scenarios reach CSL through *margins and policy*, not through volumes. Donor-collection wage costs (CSL runs the largest plasma-collection network itself), energy and cold-chain costs, and what payors will permit CSL to price — chiefly US Medicare Part D — are the live channels; the plasma keeps flowing in all six states of the world. That produces a deliberately narrow, only mildly downward-skewed distribution: a downside/upside asymmetry of 1.31×, far below DNL's cyclical 4.05× and below WBC's 1.83×, which is exactly what one should expect of a defensive staple. The uncomfortable feature of the result is not the shape but the level. Every scenario, including the Stagflation downside boundary, sits *above* the market price — Muddle Through by 93 per cent. The central question this thesis has to answer honestly is therefore not "what is CSL worth" in the usual sense, but "why does a rules-based framework, applied without intervention, land so far above where the stock trades, and which of us is wrong".

## Calibration anchors

Per `data/companies/csl.yaml` and `csl_muddle_through_valuation_v4.xlsx`:

| Anchor | Value | Source / note |
| --- | ---: | --- |
| Anchor year | FY25 (ended 30 June 2025) | Disclosed segment accounts |
| Group revenue FY25 | USD 15,558m | Behring 11,158 / Seqirus 2,166 / Vifor 2,234 |
| Group EBIT margin FY25 | ~27.5% | Segment operating result less corporate / R&D |
| Cost of equity (selected) | 8.75% | Re = 4.50% + 0.85 × 5.00% |
| β measured (EODHD) | 0.094 | Unreliable — USD revenue base vs AUD index; discarded per §3.5.3 |
| β selected | 0.85 | Peer triangulation: Grifols / Takeda / Sanofi 0.7–0.9; defensive healthcare |
| Terminal EBIT margin | 30.0% | Binding in v3+; scale + peer-gap closure held into perpetuity |
| Terminal growth g | 3.0% | US nominal-GDP-adjacent |
| Terminal capex / revenue | 6.0% (= D&A) | v4 steady-state reinvestment consistency |
| Net debt at anchor | USD 9,100m | 1H26 close; ~1.8× EBITDA |
| Restructuring cash to come | USD 507m | FY26–27, PV at Re; §4.4 cost-of-closure consistency |
| Shares outstanding | 478.9m | — |
| Market reference price | AUD 105.53 (≈ USD 69.65) | ~61% below the 52-week high of AUD 269 |
| Sell-side 12m target | USD 96.75 (≈ AUD 136) | 16-analyst mean; cutting hard (15 down, 0 up over 90 days) |
| Consensus normalised EPS FY26 | USD 6.28 | Implies a market forward P/E of ~11× |

## Where the value sits — cross-scenario distribution

Calibrating each scenario as a driver overlay on the Muddle Through base (terminal-capex-consistent), the six-scenario per-share distribution is:

| Scenario | Per share USD | Per share AUD | vs Market | vs Muddle Through | Dominant channel |
| --- | ---: | ---: | ---: | ---: | --- |
| Orderly Convergence | 156.61 | 237.29 | +125% | +16.4% | Faster trough recovery; full +250bps Behring closure; collection-cost relief |
| **Muddle Through (central)** | **134.52** | **203.83** | **+93%** | baseline | Secular plasma growth after the near-term trough; +150bps closure; 30% terminal margin |
| AI Productivity Lag | 131.03 | 198.53 | +88% | −2.6% | Mild white-collar cost relief offset by softer macro and lower terminal g |
| Disorderly Climate | 115.36 | 174.79 | +66% | −14.2% | Carbon-cost margin compression; partial Seqirus pandemic offset |
| Fragmentation | 111.03 | 168.23 | +59% | −17.5% | China Ig access + supply-chain localisation; closure stalls; tax to 20% |
| Stagflation Persists | 105.53 | 159.90 | +52% | −21.5% | Donor-wage and payor squeeze; closure reverses; terminal margin 26.5% |

The per-share asymmetry: upside (Orderly minus Muddle Through) is USD 22.08; downside (Muddle Through minus Stagflation) is USD 28.99; the ratio is **1.31×**. Terminal value is 73–77 per cent of enterprise value across the set — CSL is a long-duration compounder, and the sensitivity therefore concentrates in the terminal margin and growth rate rather than in the explicit five-year path.

What follows is the intuitive reading of each scenario — the macro story, the channels through which it reaches CSL, and why the number lands where it does. The thread to hold throughout: the revenue line barely moves between scenarios; the work is all done by margin and by the durability of that margin into the terminal.

**Muddle Through (USD 134.52 / AUD 203.83) — the central case.** Post-2022 friction persists without crushing demand; US inflation stays sticky, growth continues at 2–2.5 per cent. For CSL this is a benign-enough world that the plasma franchise resumes its secular path — immunoglobulin demand compounding at 5–7 per cent — once the near-term Behring trough (the Medicare Part D redesign and the China access soft patch) annualises out across FY26–27. Vertical integration of plasma collection and fractionation scale hold the margin advantage, and the peer-gap closure overlay delivers +150bps to Behring by FY31 (the full +250bps is reserved for the upside). Terminal margin settles at 30 per cent, growth at 3 per cent. The number lands at +93 per cent above market not because the cash-flow path is heroic — near-term lines sit on top of consensus — but because the terminal capitalises a high-quality compounder at roughly 22× forward earnings, while the market trades CSL at about 11×. The entire gap is a disagreement about the terminal, not the next two years.

**Orderly Convergence (USD 156.61 / AUD 237.29, +16.4 per cent) — the upside boundary.** Inflation re-anchors to target, real rates normalise, a productivity surprise lifts real growth and eases cost pressure at the same time. The two things this buys CSL are a faster exit from the Behring trough and genuine relief on donor-collection wages, which is what makes the *full* +250bps peer-gap closure credible rather than aspirational. Terminal margin lifts to 31.5 per cent, growth to 3.25 per cent. The instructive point is how *modest* the upside is — +16 per cent. A defensive staple cannot accelerate the way a cyclical recovers off a trough; there is no operating-leverage explosion waiting in plasma. The upside is the quiet compounding of a good franchise in a kind world, nothing more.

**AI Productivity Lag (USD 131.03 / AUD 198.53, −2.6 per cent).** Foundation models advance and agents proliferate, but the gains concentrate in platform owners and show up mainly as white-collar wage containment. CSL has a meaningful professional cost base — roughly USD 1bn of G&A and USD 1.4bn of R&D — so the wage-containment channel is a mild margin tailwind. But the same scenario carries softer macro growth and compressing growth-equity multiples, which pulls the terminal growth rate down to 2.875 per cent. The two roughly offset, and CSL lands a touch below Muddle Through. The honest reading is that the technology axis barely touches a plasma franchise: this scenario is close to neutral by construction, and that is the right answer.

**Disorderly Climate (USD 115.36 / AUD 174.79, −14.2 per cent).** The climate transition crystallises disorderly — carbon-cost pass-through runs inflation at 3–5 per cent and disrupts across sectors. CSL is exposed through cost, not demand: fractionation is energy-intensive and the distribution chain is cold-chain dependent, so carbon-cost pass-through compresses margins. The one genuine offset in the portfolio sits here — Seqirus carries pandemic and health-disruption optionality, so a disorderly world lifts vaccine demand even as it raises everyone's costs. Terminal margin 28 per cent, growth 2.75 per cent. The Seqirus cushion is precisely why this scenario lands *better* than Fragmentation despite a larger headline cost shock.

**Fragmentation and Resource Nationalism (USD 111.03 / AUD 168.23, −17.5 per cent) — the second-worst.** Trade barriers harden, supply chains localise, and China market access becomes a geopolitical instrument. CSL's plasma model — collect in the US, fractionate and distribute globally — is structurally awkward in a fragmenting world, and Behring's China immunoglobulin access is the most exposed revenue line in the group. Peer-gap closure stalls (the uplift goes to zero) as the cost of operating across blocs erodes the efficiencies the closure depended on, and the effective tax rate drifts to 20 per cent as cross-border structuring loses its edge. With no offsetting segment — unlike the Seqirus cushion in the climate case — the channels compound, and Fragmentation becomes the binding downside short of outright stagflation.

**Stagflation Persists (USD 105.53 / AUD 159.90, −21.5 per cent) — the downside boundary.** Inflation un-anchors above 4 per cent, growth recesses, an energy shock lands. This is the worst case *and the clearest illustration of the thesis*, because the plasma demand still holds — these are essential therapies — so the entire stress arrives as margin. US donor-collection wages surge (the supplier-power channel at full stretch), payors press hard on price in a fiscally-strained state (Medicare Part D with no relief), and peer-gap closure does not merely stall but reverses, with Behring margin running 150bps *below* the FY25 base. Terminal margin falls to 26.5 per cent. The revenue line is almost indistinguishable from Muddle Through; the whole 21 per cent fall is the squeeze between what CSL pays its donors and what payors let it charge. Even here, the number sits 52 per cent above market — which is the puzzle this thesis turns to next.

## The central puzzle — why the framework sits above the market

The striking feature of the distribution is not its shape but that all of it, including the downside boundary, sits well above where CSL trades. Muddle Through is +93 per cent; even Stagflation is +52 per cent. The disciplined response is not to re-tune assumptions until the gap closes — that would convert the framework from an analytical instrument into an expensive way of reproducing the share price — but to ask what the market price *implies*, lay those implied numbers beside ours, and decide each on its merits. That is the §3.5.7 market-implied cross-check, and for CSL it is unusually clarifying.

Reverse the discounted cash flow onto the market price of AUD 105.53 (USD 69.65), holding everything at Muddle Through and solving one lever at a time. To justify the price on the discount rate alone, the market would need a cost of equity of about 13 per cent — a β of roughly 1.7, for a defensive healthcare staple whose peers cluster at 0.7–0.9. To justify it on the terminal margin alone, that margin would have to fall to about 13.5 per cent — roughly half CSL's actual FY25 group margin of 27.5 per cent, a level that would imply the franchise economics have been structurally destroyed rather than merely pressured. To justify it on growth alone, CSL would have to contract at around 4 per cent in perpetuity — an essential-therapies business shrinking forever. None of these is plausible standing alone. The market price can only be reached by stacking pessimism across all three axes at once.

There are two honest interpretations, and the thesis declines to collapse them prematurely. The first is that the framework is too generous, and the candidates are identifiable: the most defensible single move is the discount rate, since a β of 0.85 sits awkwardly below market for a stock that has fallen some 60 per cent from its high — though we have deliberately *held* β at 0.85 to keep the framework rules-based and repeatable, and to let the gap remain visible rather than assumed away. (A stressed β of 1.2, lifting Re to 10.5 per cent, would on its own take Muddle Through to roughly AUD 155 and close about half the residual — a move to be made on its merits, if at all, not to chase the price.) The second interpretation is that the market is genuinely pricing a permanent de-rating of CSL's franchise — Part D, China, plasma-collection economics, the end of the high-growth era — and the framework, by pricing CSL as a still-premium compounder, simply disagrees. The multiples frame the disagreement cleanly: the framework values CSL at about 22× forward earnings, the market at about 11×, against a franchise that historically traded in the high-20s to 30×. The truth sits between, and per §16 that gap is an informative output of the framework, not a calibration error to be engineered away.

## Three transmission channels, mapped to Five Forces

CSL's scenario exposures resolve into three channels, each tied to a force in the segment-level Five Forces decomposition. Together they explain why the distribution is a margin story end to end.

**1. Plasma-collection economics — supplier power.** The "suppliers" in the plasma business are individual donors at CSL's collection centres, and CSL runs the largest such network in the world. Vertical integration is a structural advantage in normal times — it is the source of the +5bps supplier-power margin offset in the Behring decomposition, and the closure of 22 underperforming centres in FY26 is exactly the variable-cost management this affords. But the same integration makes the margin sensitive to US frontline wage inflation, because the donor-facing cost base is labour. This is the channel that does the damage in Stagflation: when wages surge, the collection cost rises faster than CSL can recover it, and the franchise's defining strength becomes the route through which the stress arrives. Watch the gap between US wage growth and CSL's disclosed gross-margin trajectory; watch centre productivity (litres per centre) as the management lever.

**2. US healthcare policy — buyer power.** CSL's buyers are payors — Medicare, private insurers, national health systems — and the force is rated moderate because plasma therapies are essential and largely price-inelastic in volume, which limits how far payors can push. The live pressure is the Medicare Part D redesign, which cost roughly USD 100m on immunoglobulin in 1H26 and is the dominant policy risk in the company's own framing. It sits behind the near-term Behring trough in every scenario and behind the deeper price squeeze in Stagflation and Fragmentation. The structural question for the terminal is whether Part D is a one-off reset (re-based and then resumed growth, the framework's view) or the first move in extending price negotiation to plasma therapies (the bearish view embedded in the market price). Watch the scope of Part D negotiation lists and any signal of plasma-derived therapies entering the frame.

**3. Scale-margin durability — rivalry, and the terminal.** The plasma industry is a global oligopoly — CSL Behring, Grifols, Takeda, Octapharma, Kedrion — in which CSL is typically the largest by revenue, and that scale converts into lower marginal cost through fractionation efficiency. This is the +10bps rivalry offset, and more importantly it is the assumption underwriting the 30 per cent terminal margin: that CSL's scale advantage persists into perpetuity. Because terminal value is roughly three-quarters of enterprise value, this single judgement — whether the scale-margin edge is durable or erodes as biosimilar and recombinant alternatives advance over a long horizon — moves the valuation more than any near-term line. It is, in the end, the assumption on which the framework and the market most fundamentally disagree.

## What the framework adds versus the conventional view

Sell-side coverage of CSL is, at present, a study in momentum: the 16-analyst mean target has been cut from the high USD 90s with fifteen downward revisions and none up over ninety days, tracking the share price down. The framework's contribution is not a better point estimate but a different object — a scenario distribution that separates what is cyclical and policy-driven from what would have to be permanent for the market to be right. Three specific additions:

1. **A defensive asymmetry, quantified.** At 1.31× the distribution is narrow and only mildly downward-skewed, which is the correct signature for a price-inelastic franchise and a useful corrective to coverage that extrapolates the current downgrade cycle. The scenarios that matter are margin scenarios, and the framework names them.
2. **The market-vs-framework gap made explicit and reversible.** Rather than asserting a target, the §3.5.7 cross-check states precisely what the market must believe — β ~1.7, or a terminal margin near half the current level, or perpetual contraction — and shows that no single one is plausible. That reframes the debate from "is CSL cheap" to "is CSL's franchise permanently impaired", which is the question actually worth arguing.
3. **Reinvestment and terminal discipline.** The v4 correction (terminal capex set equal to D&A) removes a perpetual cash inflation that a growing business cannot sustain, and the terminal-margin fix from v3 binds the stated 30 per cent rather than capitalising a peak. Both are housekeeping in the Damodaran sense — growth must be funded, and a terminal must be a steady state — and both pull the number toward defensibility on their own merits.

## Mental short-cut

CSL is a margin story, not a volume story. In every scenario the plasma keeps flowing, so do not watch the revenue line — watch the gap between what CSL pays US plasma donors and what payors, chiefly Medicare, will let it charge. The six scenarios are essentially six settings of that one dial, and they all cash out in the terminal margin, which is where three-quarters of the value lives. And keep the framing question in view: the framework prices CSL at about 22× forward earnings, the market at about 11×, for a business that used to trade in the high-20s. The whole investment debate is whether that de-rating is permanent impairment or a policy-and-cost trough — and this framework, applied without intervention, takes the second view while showing exactly what you would have to believe to take the first.

## Implications — what to watch

1. **Medicare Part D scope.** Whether the redesign re-bases immunoglobulin once and growth resumes, or extends toward plasma therapies. This single policy line is the swing between the framework's terminal and the market's.
2. **US donor-collection wages versus gross margin.** The supplier-power channel; the clearest read on whether the margin thesis is holding through the cycle.
3. **Behring trough shape.** Confirmation that FY26–27 is the bottom of the Part D and China soft patch and that the secular 5–7 per cent path resumes — the load-bearing assumption of Muddle Through.
4. **β / cost of equity.** Held at 0.85 by choice for repeatability; the most defensible candidate for a merit-based correction if the de-rating proves structural. Revisit only on evidence, not to match the price.
5. **Scale-margin durability.** Long-horizon signals on biosimilar and recombinant substitution for plasma therapies — the assumption underwriting the terminal margin, and the deepest point of disagreement with the market.

*Status: calibration and thesis draft, 25 June 2026. Per-scenario narratives per standing rule 2; market-vs-framework gap per §16; β held at 0.85 per Stephen's decision (repeatable framework). Companion discussion document to follow.*
