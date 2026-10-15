# Bridge item (e): bank retained equity earns nothing until the terminal (draft for approval, 16 Oct 2026)

Status: APPROVED AND BUILT 16 Oct 2026 as D-83 (option 1b).

## 1. The problem

The bank engine (`src/vcc_valuations/dcf/bank_engine.py`) works like this:

1. Dividends are paid out of profit (NPAT). Each year, dividends are discounted at the cost of equity (Ke).
2. Profit that is not paid out is retained. It adds to book equity.
3. Retained equity earns nothing in the explicit years. Profit comes from assets (interest-earning assets times the margin). It does not come from the equity balance.
4. Retained equity only gets value in the terminal. The terminal value is closing equity times (ROE minus g) divided by (Ke minus g). It is discounted from the end of the explicit period.

Result: when the payout falls, the withheld cash sits idle. The model pays for that only through the terminal. This is why the D-60 payout cut (which holds CET1 capital at its target) lowers value in Disorderly Climate and Stagflation Persists. Those are the two scenarios where the cut binds.

## 2. Options

1. **Retained equity earns Ke during the explicit years.** The retained balance compounds at Ke, and the terminal is applied to that compounded balance. Retention then counts at its time value, consistent with the terminal. Effect: retention is worth more than it is now. The sign of the D-60 effect can reverse in scenarios where ROE is above Ke. No new number is needed.
2. **Retained equity earns the bank's own ROE.** This is the most generous option. It assumes all retained capital is deployed at full ROE. I do not recommend it.
3. **Surplus equity above the CET1 target is paid out.** Under D-60, retention is already held to the target. This option changes the D-60 rule itself, so it is a bigger change. It is not needed to fix the idle-cash problem.

## 3. Recommendation (revised after sizing)

Option 1b, the cash version (section 6). Option 1 as first written grows book equity at Ke, but
that income never reaches shareholders in the explicit years. It counts the same income twice.
Option 1b pays the income out as cash, so it appears in NPAT and in dividends. It is the
consistent version.

Sizing shows option 1b raises WBC's value by about 4 to 6% in every scenario. Option 1 as first
written raised it by 4 to 11%, which was overstated.

## 4. What I need from you

1. Choose option 1b (recommended), 1, 2 or 3.
2. Accept a 4 to 6% rise in WBC's value in every scenario. This is a serious change. It moves WBC's levels in all six scenarios.
3. Accept that the payout cut's effect turns positive in Disorderly Climate and Stagflation, and is positive in every scenario. The comparison with no cut is itself a simplification (no cut overpays capital), so state it that way in the decision record.

## 5. What is not changed

Dividends, CET1 path and terminal form stay as they are. Only the treatment of retained equity in the explicit years changes, under option 1.

## 6. Sizing (16 Oct 2026)

Script: `scripts/size_bank_retained_equity.py`. It reproduces the WBC base values in the goldens.
The "D-60 effect" is the value with the payout cut minus the value without it.

| Scenario | Base | Option 1 (as first written) | Option 1b (cash, recommended) | D-60 effect base | D-60 effect 1b |
|---|---:|---:|---:|---:|---:|
| Orderly Convergence | 45.39 | 50.20 (+10.6%) | 47.91 (+5.5%) | +1.73 | +2.41 |
| Muddle Through | 32.40 | 34.80 (+7.4%) | 33.93 (+4.7%) | +0.34 | +0.47 |
| AI Productivity Lag | 32.73 | 35.15 (+7.4%) | 34.27 (+4.7%) | +0.33 | +0.45 |
| Fragmentation | 28.23 | 30.09 (+6.6%) | 29.58 (+4.8%) | +0.12 | +0.17 |
| Disorderly Climate | 23.08 | 24.58 (+6.5%) | 24.39 (+5.7%) | -0.06 | +0.12 |
| Stagflation Persists | 15.73 | 16.42 (+4.4%) | 16.35 (+4.0%) | -0.01 | +0.02 |

Values are AUD per share for WBC.

Option 1b, in plain terms: each year, the retained balance earns Ke. That income is paid to shareholders as extra dividends. The principal stays in book equity. The terminal value is unchanged.

Simplifications: annual periods; the stub period is handled as a fraction of a year; the terminal is unchanged in 1b. The payout rule itself is not changed.
