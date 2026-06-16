# WBC — Cross-scenario investment thesis (initial sketch)

**Company:** Westpac Banking Corporation (ASX:WBC)
**Version:** 2026-Q2-v1 (initial framework view, 16 June 2026 — workbook to follow)
**Type:** Cross-scenario investment thesis per §16.1 item 6. First worked example under methodology §15 (bank-specific valuation conventions).
**Anchor period:** 1H26 results, 31 March 2026.

---

## One-paragraph thesis

Westpac Banking Corporation is the second-largest Australian bank by mortgage book scale (#2 in system housing share at ~20%) and the second-largest by total assets, with a franchise anchored on the consumer banking and mortgage core supported by a solid retail deposit franchise (#2 household deposits, AUD 615bn Australian retail base including AUD 149bn non-interest-bearing transaction balances). The defining investment question is whether the **transformation program (UNITE technology re-platforming, FY26-FY29 cost-out plan)** closes the ~10pp cost-to-income gap to CBA (51.7% vs ~42%) and the ~4pp ROE gap (9.8% vs 13.6%) — a closure that would drive a meaningful re-rating from the current 1.69× price-to-book — or whether execution risk locks WBC in the mid-tier oligopoly position. Across our six scenarios, WBC's outcome is **structurally asymmetric**: the downside scenarios (Stagflation Persists, Disorderly Climate) materially compress value through credit-loss cycle stress combined with NIM compression and operating leverage in cost growth; the upside scenario (Orderly Convergence) lifts value modestly via benign credit and incremental NIM expansion plus loan-growth tailwind. The framework's distinguishing inputs versus conventional sell-side views: (a) peer-triangulated β of 0.75 vs mechanical use of WBC's measured 0.73 per methodology §3.5.3, (b) through-cycle NIM anchor 1.94% calibrated against four years of disclosed FY history rather than long-term spot, (c) credit losses as a **primary scenario driver** rather than a residual under methodology §15.4, (d) explicit CET1 capital constraint binding dividend payout under stress per §15.5, (e) Five Forces decomposition for the bank archetype — +8bps NIM advantage on supplier power (deposit franchise) less ~−10bps revenue growth on rivalry (cost-to-income gap).

## Calibration anchors

Per `data/companies/wbc.yaml/bank_specifics`:

| Anchor | Value | Source |
| --- | --- | --- |
| Anchor date | 31 March 2026 | 1H26 results announcement |
| Cost of equity (selected) | 8.05% | Re = 4.30% + 0.75 × 5.00%; β selected via peer triangulation §3.5.3 |
| β measured (WBC) | 0.73 | EODHD feed, 15 June 2026 |
| β selected | 0.75 | CBA / NAB / WBC peer-cluster midpoint; ANZ excluded as outlier |
| Through-cycle NIM | 1.94% | FY22-FY25 disclosed range midpoint |
| Current 1H26 NIM | 1.89% | Front-book mortgage compression at low end of historic range |
| AIEA (1H26 average) | AUD 1,035bn | Of which loans AUD 799bn, liquid assets AUD 212bn |
| Through-cycle credit loss | 18bps | Low end of Big Four 15-25bps anchor; mortgage-heavy book |
| Current credit loss (1H26 annualised) | ~10bps | Benign cycle |
| Cost-to-income (1H26 ex notable) | 51.7% | Mid-pack Big Four; CBA ~42% / NAB ~43% set the pace |
| CET1 (Level 2) | 12.42% | 92bps above management's 11.0-11.5% operating target |
| AT1 hybrid outstanding | AUD 8,522m | Deducted from per-share ordinary equity |
| Shares outstanding | 3,414.9m | EODHD-verified |
| Market reference price | AUD 35.32 | 15 June 2026; implied market cap AUD 120.6bn |
| Sell-side consensus 12m target | AUD 33.45 | ~5% below current trading |
| Book value per share | AUD 21.31 | Price-to-book 1.69× |
| ROE TTM (statutory) | 9.8% | Slightly below 10-12% Big Four anchor |

## Where the asymmetry sits (qualitative, pre-workbook)

The workbook is not yet built, so the per-share numbers are not finalised. The qualitative directional view, applying the impact matrix at
`data/impact_matrix/by_industry/australian_major_banks.yaml`:

| Scenario | Expected direction vs market | Dominant driver |
| --- | --- | --- |
| Orderly Convergence | Modest upside | Healthy loan growth + NIM ~5-10bps positive + benign credit cycle |
| Muddle Through (central) | At or near market | Status-quo NIM at anchor; cost glide net of inflation; through-cycle credit losses |
| AI Productivity Lag | Mild downside | Modest cost benefit insufficient to offset weaker macro demand |
| Fragmentation | Moderate downside | Institutional/markets income pressure; modest credit losses on business book; rate path uncertain |
| Disorderly Climate | Material downside | Climate-RWA uplift compresses ROE; transition stress raises credit losses; terminal-growth dampened by capital intensity |
| Stagflation Persists | Material downside | NIM compression -20 to -40bps + credit losses peak-cycle 60-80bps + operating leverage in cost growth |

Stagflation Persists is expected to be the worst outcome for WBC — the bank-archetype equivalent of "supplier-power blocks cost pass-through" plays out across three channels simultaneously: NIM compresses on deposit competition and slow front-book repricing; cost growth lifts on wage inflation while transformation glide insufficient; and credit losses lift to peak-cycle territory. The combination compresses both numerator (cash earnings) and the terminal-value multiplier (ROE fade).

Disorderly Climate is the second-worst outcome. The mortgage book scale (#2 system) is asymmetric in a climate scenario where APRA RWA models are climate-adjusted upward for vulnerable zones — WBC has more absolute climate-vulnerable mortgage exposure than NAB or ANZ.

Orderly Convergence is the upside scenario but the lift is modest — banks are not torque to upside in the way cyclical industrials are; ROE expansion is capped by the oligopolistic structure that constrains both pricing and downside.

## Three transmission channels that distinguish WBC's scenario exposures (mapped to Five Forces)

### 1. NIM compression under sustained competition or rate stress — Supplier Power × Rivalry interaction

This channel sits at the *intersection* of the supplier-power force (deposit funding) and the rivalry force (front-book mortgage competition). The bank archetype's `supplier_power: moderate` rating means deposit competition (term-deposit rate wars, at-call rate moves) directly pressures NIM. Under Stagflation, elevated cash rates intensify deposit rate competition AND borrower refinancing pressure simultaneously compresses front-book mortgage margins. The supplier-power-blocks-pass-through dynamic at WBC manifests as: deposit costs rise faster than the bank can pass through to asset yields, and front-book mortgage pricing lags asset-yield improvement on the way down. Net NIM compression −20 to −40bps from the 1.94% anchor under Stagflation.

WBC has a partial structural defence here: the AUD 149bn non-interest-bearing transaction deposit balance provides a structural funding-cost floor (deposits with zero or near-zero interest rate cost). The framework captures this as the +8bps NIM advantage on supplier-power decomposition. Under Stagflation, however, the advantage shrinks as customers move balances from transaction accounts to term deposits to chase higher rates — a defensive moat that erodes precisely when it would matter most.

Watchable signals:

1. RBA cash-rate decisions and forward guidance (most directly relevant).
2. Big Four term-deposit rate moves (industry-rivalry signal — when one bank breaks discipline, NIM compresses across the sector).
3. Westpac NIM disclosures at half-yearly results — Core NIM trend separated from Treasury & Markets contribution.
4. Non-interest-bearing deposit balance trajectory (the defensive moat measurement).

### 2. Credit cycle stress — the primary scenario driver, not a residual

Credit losses are the bank-archetype equivalent of "gross margin shock under stress" — they sit as a **primary scenario driver** in the impact matrix per methodology §15.4, not as a residual to be absorbed. WBC's mortgage-heavy book (~68% of gross loans) places its through-cycle anchor at the low end of Big Four range (18bps vs 15-25bps), but the cyclical amplification is real: peak-cycle anchor 75-80bps; benign-cycle anchor 5bps. The dispersion across the cycle is 70bps+.

Under Stagflation Persists: cycle stress accelerates Stage 2/3 migration in both housing (serviceability pressure on high-LVR cohorts) and business book (demand stress combined with rate-cost pressure). Estimated 60-80bps of average loans — adding ~AUD 600-800m to the impairment line annually vs the through-cycle anchor.

Under Disorderly Climate: targeted stress in transition-vulnerable mortgage zones (high-flood, high-bushfire) and managed run-off of coal/oil-gas business lending. Lower aggregate impact than Stagflation but more permanent (RWA uplift is structural).

Under Orderly Convergence: benign cycle persists; losses 10-15bps; CET1 generation strong, supporting capital management.

Watchable signals:

1. 90+ day delinquency rate trajectory (currently 0.45% mortgage; troughed below trough-cycle level).
2. Stage 2 migration in Pillar 3 disclosures.
3. Mortgage stress and serviceability tests under RBA hiking cycle dynamics.
4. Business book impairment trend at FY26 / 1H27 results.

### 3. CET1 capital constraint binding payout under stress — Capital regime, methodology §15.5

The bank-archetype-distinguishing transmission channel. Under benign conditions WBC's CET1 (currently 12.42%, against an 11.0-11.5% management target) provides 92bps of buffer above target — supporting capital management (buyback in progress, AUD 581m executed FY25 of AUD 1.5bn announced). Under stress conditions the buffer is constrained — and the methodology §15.5 mechanic kicks in: if CET1 generation falls below the requirement to maintain target post-stress, payout ratio must drop to retain earnings. This is the canonical "banks cut dividends in recession" pattern.

Translation to value: under Stagflation Persists, payout ratio is forced from 75% down to 50-55% as CET1 is rebuilt. This is not a structural value loss (retained capital compounds the next year) but it does delay the cash distribution to shareholders, reducing present value materially over a 5-year explicit horizon.

Under Disorderly Climate: climate-RWA uplift directly compresses CET1 (without bank action), forcing the same payout-rebuild mechanic. Structurally permanent.

Watchable signals:

1. CET1 trajectory at half-year results — the most direct payout-capacity read.
2. APRA capital framework consultations (any movement on D-SIB surcharge, IRB models, climate adjustments).
3. Pillar 3 RWA composition — particularly housing RWA density and climate-related additions.
4. Buyback completion pace (early signal of CET1 surplus / shortfall).

## What the framework will add vs the conventional view

Conventional analyst views of WBC typically focus on next-period earnings, NIM trajectory, and cost-to-income glide path — the same drivers the framework captures, but presented as a single point-estimate Muddle-Through equivalent. The framework's additions:

1. **Peer-triangulated β selection per §3.5.3** — measured β 0.73 sits at the bottom of the comparable-peer cluster (CBA 0.80 / NAB 0.72 / WBC 0.73); selected β 0.75 lifts Ke from 7.95% to 8.05% with documented rationale. ANZ excluded as institutional-dilution outlier.

2. **Through-cycle NIM anchor calibrated to 4-year FY history** rather than long-term spot. Anchor 1.94% (FY22-FY25 disclosed range midpoint); current 1H26 1.89% sits at the historic low end — informative for scenario stress range.

3. **Credit losses as primary scenario driver** per §15.4, not a residual. Through-cycle 18bps anchor for WBC's mortgage-heavy book; peak-cycle 75bps. Six-scenario dispersion captured.

4. **CET1 capital constraint binding payout under stress** per §15.5. Explicit mechanic in the workbook: cash earnings retained = CET1 generation; ΔRWA × CET1 ratio = required capital; payout ratio is the residual.

5. **Five Forces decomposition for the bank archetype** per §15.6, applied to WBC vs Big Four average: +8bps NIM advantage on supplier-power (retail deposit franchise) — visible in NIM trajectory; −10bps revenue growth on rivalry (cost-to-income gap) — captured as transformation overlay glide rather than structural offset; −5bps growth on business-banking rebuild sub-force.

6. **AT1 hybrid AUD 8.5bn deduction** from per-share ordinary equity per §15.7 — frequently missed in price-to-book valuations.

7. **Terminal value via ROE-fade-to-Ke** per §15.8 with sustainable-growth identity (g = ROE × (1 − payout)). For WBC: terminal ROE 10.5% (Big Four anchor) > Ke 8.05% so positive terminal value generation; sensitivity to terminal ROE assumption is material.

## What's NOT in this thesis yet

The workbook is to come. Once built:

1. Per-scenario per-share value (six values).
2. Per-share asymmetry quantification (analogous to DNL's 4.05× downside / upside ratio).
3. Sensitivity to β-selection range (0.72-0.80 = ±5% on Ke).
4. Sensitivity to through-cycle NIM anchor (1.88-2.00% = ±AUD 3-4 per share).
5. Sensitivity to terminal ROE assumption (10-12% = ±AUD 5-7 per share).
6. Bridge from Muddle Through cash-earnings forecast to per-share value via the §15.7 equity bridge.
7. Market check vs sell-side consensus target (AUD 33.45) and current price (AUD 35.32).
