# CSL terminal return sensitivity (16 Oct 2026)

Status: sensitivity only. No model input has changed. Decision D-85 records why.

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
- Fade: the model's 25 years, or 10 years.
- Value: AUD per share, from the segment engine.
- Source: every figure below is in `design/methodology/csl_terminal_return_sets.yaml`,
  written by `scripts/size_csl_terminal_return.py` and pinned by
  `tests/dcf/test_csl_terminal_return_sets.py` (which also checks this table cell by cell).

## Results (AUD per share)

| Scenario | Model start return | Fade | Model (earned start) | Start 20% | Start 15% | Start 12% |
|---|---|---|---|---|---|---|
| Orderly convergence | 31.2% | 25 yrs | 266.33 | 200.73 | 171.49 | 153.94 |
| Orderly convergence | 31.2% | 10 yrs | 197.07 | 165.11 | 150.86 | 142.31 |
| Muddle through | 27.6% | 25 yrs | 226.66 | 184.73 | 157.00 | 140.35 |
| Muddle through | 27.6% | 10 yrs | 172.01 | 151.33 | 137.65 | 129.44 |
| AI productivity lag | 27.0% | 25 yrs | 217.32 | 179.86 | 153.23 | 137.25 |
| AI productivity lag | 27.0% | 10 yrs | 167.17 | 148.36 | 134.98 | 126.96 |
| Fragmentation | 22.9% | 25 yrs | 172.73 | 159.12 | 135.75 | 121.73 |
| Fragmentation | 22.9% | 10 yrs | 140.45 | 133.19 | 120.74 | 113.27 |
| Disorderly climate | 23.8% | 25 yrs | 182.56 | 164.53 | 140.90 | 126.72 |
| Disorderly climate | 23.8% | 10 yrs | 147.91 | 138.30 | 125.71 | 118.15 |
| Stagflation persists | 20.5% | 25 yrs | 149.62 | 147.42 | 126.12 | 113.34 |
| Stagflation persists | 20.5% | 10 yrs | 126.17 | 124.95 | 113.11 | 106.01 |

The "Model (earned start)" column is the current model. It ties to the
six base values: 266.33, 226.66, 217.32, 172.73, 182.56, 149.62.
These values reflect D-87 as refined (net debt on the agreed convention, and issued capital
of 482.13m shares at 31 December 2025).

## Reading the table

1. The starting return and the fade both matter a lot. A 10-year fade cuts
   orderly convergence from 266.33 to 197.07.
2. A starting return of 20% cuts orderly convergence by about a quarter
   (266.33 to 200.73), and stagflation by almost nothing (149.62 to 147.42).
3. The fade and the starting return interact. The gap between the models is
   widest in the strongest scenarios.

## What this note does not do

- It does not say which starting return or fade is right. That is a judgement
  for Stephen, and the same question applies to DNL's terminal return.
- It does not change the terminal capex line. D-85 explains why that line
  does not feed the headline value.
