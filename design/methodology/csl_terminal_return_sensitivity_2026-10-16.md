# CSL terminal return sensitivity (16 Oct 2026)

Status: sensitivity only. No model input has changed. Decision D-85 records why.

Note (16 Oct 2026, D-93): the model fade is now 20 years, the midpoint of CSL's
15-25 year decay band. It was 25 years (band 20-30) when this note was first
written. The "Model (earned start)" column at 20 years is the current model.
The 25-year and 15-year rows are the band ends (D-63); the 10-year row is the
short line kept from the first version.

## What this shows

CSL's headline value uses the excess-return convergence terminal in all six
scenarios (D-62, D-71). That terminal starts from a return on the capital
base, then fades it to the cost of capital (8.12%) over a set number of years.
This note shows how the per-share value moves when the starting return or the
fade length changes. Each row reruns the segment engine with only those two
inputs overridden. Everything else is as in the model.

## Method

- Starting return: the model's own earned return for each scenario, or a
  fixed 20%, 15% or 12%.
- Fade: the model's 20 years, the band ends of 25 and 15 years, or 10 years.
- Value: AUD per share, from the segment engine.
- Source: every figure below is in `design/methodology/csl_terminal_return_sets.yaml`,
  written by `scripts/size_csl_terminal_return.py` and pinned by
  `tests/dcf/test_csl_terminal_return_sets.py` (which also checks this table cell by cell).

## Results (AUD per share)

| Scenario | Model start return | Fade | Model (earned start) | Start 20% | Start 15% | Start 12% |
|---|---|---|---|---|---|---|
| Orderly convergence | 31.2% | 20 yrs | 246.47 | 190.52 | 165.57 | 150.61 |
| Orderly convergence | 31.2% | 25 yrs | 266.33 | 200.73 | 171.49 | 153.94 |
| Orderly convergence | 31.2% | 15 yrs | 223.54 | 178.72 | 158.74 | 146.75 |
| Orderly convergence | 31.2% | 10 yrs | 197.07 | 165.11 | 150.86 | 142.31 |
| Muddle through | 27.6% | 20 yrs | 211.15 | 175.26 | 151.51 | 137.26 |
| Muddle through | 27.6% | 25 yrs | 226.66 | 184.73 | 157.00 | 140.35 |
| Muddle through | 27.6% | 15 yrs | 193.08 | 164.21 | 145.11 | 133.65 |
| Muddle through | 27.6% | 10 yrs | 172.01 | 151.33 | 137.65 | 129.44 |
| AI productivity lag | 27.0% | 20 yrs | 203.32 | 171.06 | 148.14 | 134.38 |
| AI productivity lag | 27.0% | 25 yrs | 217.32 | 179.86 | 153.23 | 137.25 |
| AI productivity lag | 27.0% | 15 yrs | 186.76 | 160.66 | 142.11 | 130.98 |
| AI productivity lag | 27.0% | 10 yrs | 167.17 | 148.36 | 134.98 | 126.96 |
| Fragmentation | 22.9% | 20 yrs | 164.23 | 152.28 | 131.79 | 119.50 |
| Fragmentation | 22.9% | 25 yrs | 172.73 | 159.12 | 135.75 | 121.73 |
| Fragmentation | 22.9% | 15 yrs | 153.63 | 143.78 | 126.87 | 116.72 |
| Fragmentation | 22.9% | 10 yrs | 140.45 | 133.19 | 120.74 | 113.27 |
| Disorderly climate | 23.8% | 20 yrs | 173.43 | 157.62 | 136.90 | 124.46 |
| Disorderly climate | 23.8% | 25 yrs | 182.56 | 164.53 | 140.90 | 126.72 |
| Disorderly climate | 23.8% | 15 yrs | 162.06 | 149.01 | 131.91 | 121.65 |
| Disorderly climate | 23.8% | 10 yrs | 147.91 | 138.30 | 125.71 | 118.15 |
| Stagflation persists | 20.5% | 20 yrs | 143.71 | 141.75 | 122.84 | 111.49 |
| Stagflation persists | 20.5% | 25 yrs | 149.62 | 147.42 | 126.12 | 113.34 |
| Stagflation persists | 20.5% | 15 yrs | 136.06 | 134.43 | 118.60 | 109.10 |
| Stagflation persists | 20.5% | 10 yrs | 126.17 | 124.95 | 113.11 | 106.01 |

The "Model (earned start)" column at 20 years is the current model. It ties to the
six base values: 246.47, 211.15, 203.32, 164.23, 173.43, 143.71. The 25-year rows are the model before
D-93 (266.33, 226.66, 217.32, 172.73, 182.56, 149.62).
These values reflect D-87 as refined (net debt on the agreed convention, and issued capital
of 482.13m shares at 31 December 2025).

## Reading the table

1. The starting return and the fade both matter a lot. A 10-year fade cuts
   orderly convergence from 246.47 to 197.07. The band ends move it to 266.33
   (25 years) and 223.54 (15 years).
2. A starting return of 20% cuts orderly convergence by about a fifth
   (246.47 to 190.52), and stagflation by almost nothing (143.71 to 141.75).
3. The fade and the starting return interact. The gap between the models is
   widest in the strongest scenarios.

## What this note does not do

- It does not say which starting return is right. The fade was set to 20 years by
  Stephen on 16 Oct 2026 (D-93). The starting return stays the earned return (D-86).
- It does not change the terminal capex line. D-85 explains why that line
  does not feed the headline value.
