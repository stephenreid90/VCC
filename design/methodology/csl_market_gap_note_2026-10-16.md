# CSL gap to market (16 Oct 2026)

Status: disclosure only. No model input has changed and no price has been refreshed.

Source: set `csl_market_gap_set.yaml`, written by `scripts/size_csl_market_gap.py` and checked by `tests/dcf/test_csl_market_gap_set.py`. Every number below comes from that set.

## What this is

Section 16.3 asks for a written treatment where the central case sits above market. CSL's does. Stephen's ruling (D-92) is that the 15 June 2026 price stands and the gap is disclosed, not reconciled. This note states the assumptions that differ and the sensitivity band. It does not explain the gap away, propose a haircut or refresh the price.

## The gap

Market price: AUD 105.53 per share, struck on 2026-06-15 (read from `data/companies/csl.yaml`). Gap is model value divided by price, less one.

| Scenario | AUD per share | Gap to market |
|---|---|---|
| Orderly convergence | 246.47 | +134% |
| Muddle through | 211.15 | +100% |
| AI productivity lag | 203.32 | +93% |
| Fragmentation | 164.23 | +56% |
| Disorderly climate | 173.43 | +64% |
| Stagflation persists | 143.71 | +36% |

All six scenarios sit above the market price. The closest is Stagflation persists at 143.71, +36% above. Following section 16.3, the market is implicitly pricing closer to that scenario's terminal assumptions than to Muddle through (211.15, +100%).

## The assumptions that differ

- Discount rate (D-84, D-06): a WACC of 8.12% on a target capital structure. Cost of equity 8.75%, after-tax cost of debt 3.85%, debt weight 12.86%. The debt weight is 1.8 times net debt to EBITDA over a 14 times through-cycle EV/EBITDA. D-06 is still provisional because that multiple has no independent support.
- Terminal form (D-62, D-71, D-93): the return earned on capital at the end of the forecast fades to the cost of capital over 20 years, then growth continues at the terminal rate. 20 years is the midpoint of a 15-25 year decay band.
- Earned starting returns (D-44, D-86): the return on capital excluding goodwill, which the fade starts from. Orderly convergence 31.22%, Muddle through 27.56%, AI productivity lag 27.03%, Fragmentation 22.91%, Disorderly climate 23.81%, Stagflation persists 20.52%.
- Terminal growth: set by scenario. Orderly convergence 5.06%, Muddle through 4.86%, AI productivity lag 4.55%, Fragmentation 3.48%, Disorderly climate 3.49%, Stagflation persists 2.69%.
- Price date (D-92): 2026-06-15. The model is not marked to a later price.

## The band

Value per share if the fade runs 15, 20 or 25 years (D-63 band ends and the D-93 midpoint). Everything else is as in the model.

| Scenario | 15 years | 20 years | 25 years |
|---|---|---|---|
| Orderly convergence | 223.54 | 246.47 | 266.33 |
| Muddle through | 193.08 | 211.15 | 226.66 |
| AI productivity lag | 186.76 | 203.32 | 217.32 |
| Fragmentation | 153.63 | 164.23 | 172.73 |
| Disorderly climate | 162.06 | 173.43 | 182.56 |
| Stagflation persists | 136.06 | 143.71 | 149.62 |

Even the lowest value in the band (136.06) is above the market price of 105.53. The band does not close the gap.

## Closing

The gap is an output of the assumptions above. A reader who disagrees with any of them can change it and rerun the model. No reconciliation to the market is made.
