# The 6–7% capex anchor, tested against the accounts

*Working note, 7 September 2026. Series and sources in `analyses/dnl_capex_history.yaml`,
extracted from the reports in `data/financials/historical/dnl/`. Valuation effects computed
on the current assumption set.*

---

`data/companies/dnl.yaml` carries `capex_pct_revenue: 0.07`, justified as the "pre-demerger
historical pattern (6–7%)", with FY25's reported 12.8% "rejected as the steady-state anchor".
The claim had no evidence reference and no series behind it. It does now, and the short
version is that the pattern is real but the range is wrong, the 12.8% it rejects was
mis-struck, and neither of those is the problem worth caring about.

## The series

Two definitions are in play and the file mixes them. The five-year statistics table reports
"net capital expenditure on plant and equipment (cash flow)" — narrow, excludes intangibles,
struck net of proceeds. The consolidated cash flow statement reports "payments for property,
plant and equipment and intangibles" — broader, gross. The FY25 figure of 12.8% is computed
on the second. The 6–7% pattern, if it comes from anywhere, comes from the first.

On the narrow definition, group capex as a percentage of group revenue ran 8.61%, 6.87%,
8.03%, 6.78% and 6.97% across FY19 to FY23 — 7.36% in aggregate. On the broad definition,
FY21 to FY25 ran 8.16%, 6.87%, 8.24%, 7.06% and 8.87%, aggregating to 7.80%.

So "6–7%" is the bottom of the range rather than the range, and it is reachable only on the
narrow definition and only in the years the fertiliser price spike inflated the denominator.
FY22 and FY23 group revenue was $6.3bn and $6.0bn against $4.3bn in FY21; a capex ratio
struck on that denominator is not a capital intensity, it is a commodity price.

The cleaner ratio, immune to the denominator problem, is capex to depreciation. On the narrow
definition FY19–FY23 gives 1.04×. On the broad definition FY21–FY25 gives 1.24×. Either way
the group was spending more than it depreciated, not less.

## What is wrong with the 12.8%

Three things, and the first is arithmetic rather than judgement.

The numerator is the whole group and the denominator is not. FY25 payments for property,
plant and equipment and intangibles were $474.2m, of which $52.3m was the discontinued
fertiliser operations. Revenue of $3,710.1m is continuing operations only. So 12.8% divides
a group numerator by a continuing-operations denominator. Struck consistently, FY25 is 8.87%
group-on-group, 11.37% continuing-on-continuing, or 10.78% for the Dyno Nobel segments alone.
The figure the file rejects as an outlier is not the figure the accounts support, and
correcting it does not produce 6–7% — it produces something between 8.9% and 11.4%.

FY25 was nonetheless a heavy year, and for a reason the file does not name. Turnaround capex
was $143.0m against $31.3m in FY24 — the scheduled turnarounds at Moranbah, Cheyenne, LOMO
and Mount Isa. That is a genuine cyclical spike and a good reason to normalise. It argues for
a mid-cycle number, not for the bottom of a historical range.

And the pattern being extrapolated is Incitec Pivot's. Denali is the explosives residual.
The relevant series exists — the FY25 report discloses capital expenditure by business unit —
and it says something different. Excluding Fertilisers, the Dyno Nobel segments spent $241.7m
in FY24 and $346.4m in FY25 against revenue of $3,194.1m and $3,212.3m: **7.57% and 10.78%,
or 9.18% across the two years**. Their depreciation over the same two years was 8.24% of
revenue, so the explosives business ran capex at **1.11× depreciation**.

## What the company expects to spend

The FY25 annual report guided total Dyno Nobel capital expenditure of $280m to $330m in FY26.
The 1H26 result, six months later, revised that to $250m to $300m for continuing operations.
On the model's base-year revenue of $3,400m that is **7.35% to 8.82%**, midpoint 8.09%.

The half itself is worth a second look. Continuing-operations capex was $95.1m against
revenue of $1,609.8m — 5.9%, and the lowest half in the series. But turnaround spend was
$1.8m against $56.8m in the prior corresponding half, and revenue was up 11.4% while capex
fell 42%. That is a business deferring spend in a transition year, not one demonstrating a
structurally lower capital requirement. Reading 5.9% as evidence for a 7% steady state would
be making the same mistake as reading 12.8%, in the other direction.

## The depreciation rate is the load-bearing number, not the capex rate

`da_pct_revenue` is 7.3%, and its rationale says it "matches assumed capex/revenue ratio of
7%". It cross-checks against FY25 depreciation of 7.66% of revenue — but that is depreciation
for continuing operations divided by continuing-operations revenue, and continuing operations
still include Phosphate Hill. For the Dyno Nobel segments alone, FY25 depreciation was $269.1m
on $3,212.3m of revenue: **8.38%**, and FY24 was 8.11%.

This matters more than the capex figure because D-38 converges the explicit capex path onto
the depreciation rate and D-39 strikes the terminal from the final explicit year. The
depreciation rate is not an input to the build so much as the destination of it.

## What any of this does to the valuation — and the answer is: less than you would think

Re-anchoring both rates together barely moves anything. Holding the EBIT margin and lifting
depreciation and the capex convergence target in step:

| | Value per share | Terminal capex |
|---|---|---|
| As built — D&A 7.30%, capex converging to 7.30% | $2.6956 | 8.77% |
| D&A 7.66%, capex converging to 7.66% | $2.6984 | 9.13% |
| D&A 8.38%, capex converging to 8.38% | $2.7040 | 9.85% |

Three tenths of one per cent across a full percentage point of capital intensity. The reason
is mechanical: depreciation is added back to cash flow and capex is subtracted from it, so
moving both by the same amount nets to nothing. **The level of the anchor is very nearly
irrelevant to the answer. Only its position relative to depreciation matters.**

Which is item 11 again, and it puts the company's own guidance directly into that argument.
Take the guidance midpoint as the converged capex rate and leave depreciation at 7.30%:

| | Value per share | Terminal ROIC | Invested capital ÷ revenue, Y10 |
|---|---|---|---|
| Capex converging to 7.30% (as built) | $2.6956 | 14.94% | 72.6% |
| Capex converging to 8.10% (guidance midpoint) | $2.5719 | 13.92% | 77.9% |
| Capex holding capital intensity flat | $1.7676 | 10.02% | 108.3% |

So the guidance moves the ruled build by 4.6% and closes about an eighth of the distance to
holding intensity flat. Denali is guiding, for FY26, to capex roughly equal to its own
depreciation while revenue grows — which is the ruled build's assumption, not the alternative's.

## What follows

The anchor should be restated rather than defended. On the evidence the standalone explosives
business runs capex at 9.2% of revenue and depreciation at 8.2%, and guides to 7.4%–8.8% for
the coming year. "6–7% per pre-demerger historical pattern" is not what the accounts say, is
struck on the wrong entity, and cites a range it cannot support. Restating it costs almost
nothing in valuation terms — three tenths of a per cent — and buys a defensible input where
there is currently an undocumented one. The series and sources are now in
`analyses/dnl_capex_history.yaml` and should become the `evidence_refs` that
`capex_pct_revenue` and `da_pct_revenue` both lack.

The FY26 guidance cuts against the alternatives on item 11, and the note should say so
plainly rather than bury it. A company guiding to capex at its depreciation rate while growing
revenue is behaving as the ruled build assumes. What that single year cannot tell you is
whether the behaviour persists for ten — a business in a transition year, selling Phosphate
Hill and deferring turnarounds, is not evidence about the steady state. The two-year actual of
1.11× depreciation is the better guide, and it sits between the ruled build's 1.00× and the
1.7× falling to 1.3× that holding intensity flat would require.

The one number in this whole chain that has moved on evidence is the depreciation rate: 8.38%
on the business being valued against 7.30% in the file. That is worth correcting on its own
merits, and it should be corrected before D-38 is ruled on, because D-38's convergence target
is precisely that number.
