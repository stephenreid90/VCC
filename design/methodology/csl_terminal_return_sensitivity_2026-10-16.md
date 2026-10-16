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

## Results (AUD per share)

| Scenario | Model start return | Fade | Model (earned start) | Start 20% | Start 15% | Start 12% |
|---|---|---|---|---|---|---|
| Orderly convergence | 31.2% | 25 yrs | 264.30 | 198.26 | 168.82 | 151.15 |
| Orderly convergence | 31.2% | 10 yrs | 194.57 | 162.39 | 148.05 | 139.44 |
| Muddle through | 27.6% | 25 yrs | 224.34 | 182.13 | 154.20 | 137.44 |
| Muddle through | 27.6% | 10 yrs | 169.31 | 148.50 | 134.72 | 126.46 |
| AI productivity lag | 27.0% | 25 yrs | 214.93 | 177.22 | 150.41 | 134.32 |
| AI productivity lag | 27.0% | 10 yrs | 164.43 | 145.50 | 132.04 | 123.96 |
| Fragmentation | 22.9% | 25 yrs | 170.02 | 156.31 | 132.79 | 118.68 |
| Fragmentation | 22.9% | 10 yrs | 137.52 | 130.21 | 117.68 | 110.15 |
| Disorderly climate | 23.8% | 25 yrs | 179.93 | 161.78 | 137.98 | 123.71 |
| Disorderly climate | 23.8% | 10 yrs | 145.04 | 135.37 | 122.69 | 115.08 |
| Stagflation persists | 20.5% | 25 yrs | 146.75 | 144.53 | 123.09 | 110.23 |
| Stagflation persists | 20.5% | 10 yrs | 123.15 | 121.91 | 109.99 | 102.84 |

The "Model (earned start)" column is the current model. It ties to the
six base values: 264.30, 224.34, 214.93, 170.02, 179.93 and 146.75.

## Reading the table

1. The starting return and the fade both matter a lot. A 10-year fade cuts
   orderly convergence from 264.30 to 194.57.
2. A starting return of 20% cuts orderly convergence by about a quarter
   (264.30 to 198.26), and stagflation by almost nothing (146.75 to 144.53).
3. The fade and the starting return interact. The gap between the models is
   widest in the strongest scenarios.

## What this note does not do

- It does not say which starting return or fade is right. That is a judgement
  for Stephen, and the same question applies to DNL's terminal return.
- It does not change the terminal capex line. D-85 explains why that line
  does not feed the headline value.
