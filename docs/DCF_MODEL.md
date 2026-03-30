# DCF Model — Technical Reference

## Overview

The DCF engine in `models/dcf.py` implements a standard unlevered DCF with terminal value.

## Methodology

### 1. FCF Projection
```
FCF_t = FCF_base × (1 + g)^t   for t = 1 … n
```

### 2. Present Value of Explicit Period
```
PV_explicit = Σ FCF_t / (1 + WACC)^t
```

### 3. Terminal Value (Gordon Growth)
```
TV = FCF_n × (1 + g_terminal) / (WACC - g_terminal)
PV_terminal = TV / (1 + WACC)^n
```

### 4. Enterprise & Equity Value
```
EV = PV_explicit + PV_terminal
Equity Value = EV - Net Debt
Price/Share = Equity Value / Shares Outstanding
```

## Key Assumptions

| Parameter | Typical Range | Notes |
|-----------|--------------|-------|
| WACC | 7–12% | Higher for miners/EM, lower for defensives |
| Terminal Growth | 1.5–3% | Anchored to long-run GDP/inflation |
| Explicit Period | 5–10 years | 5 is standard; 10 for high-growth |
| FCF Growth | Company-specific | Match to revenue/margin outlook |

## Sensitivity Analysis

The model auto-generates a 5-scenario sensitivity:
- Base case
- WACC +1% / -1%
- Terminal growth +0.5% / -0.5%

## Sector Adjustments

- **Mining:** Apply `models/adjustments/mining.py` to adjust FCF for commodity prices and reserve depletion
- **Banking:** Use DDM or residual income; see `models/adjustments/banking.py`
- **Corporates:** Standard DCF; apply leverage adjustments from `models/adjustments/corporate.py`
