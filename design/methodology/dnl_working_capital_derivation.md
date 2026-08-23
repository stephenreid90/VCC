# DNL working capital — derivation and the case for changing it

**Status: CLOSED and implemented, 23 August 2026.** Superseded in two places by
what was actually ratified, and kept because the reasoning is still the record of how
we got there.

1. **The definition moved.** This paper derives a TRADE working-capital intensity of
   16.87%. D-09 subsequently adopted the BROAD definition, and the ratified DNL figure
   is **13.76%** (D-31) — see `working_capital_treatment.md` §6.4 for why the trade
   measure was rejected (it gives three different answers across three DNL documents).
   Every 16.87% in this paper should be read as superseded arithmetic, not as the live
   input.
2. **Section 6's tables are therefore stale.** The implemented outcome across the six
   scenarios is in `WORKING_NOTES.md`; the mechanism is
   `working_capital_intensity_from_data()` and the wiring is
   `build_engine_inputs_from_data`.

What survives unchanged is section 4 (why constant intensity), section 5 (the evidence
is one observation), and section 8's core argument — that zero was never a considered
view. Written 20 August 2026 at Stephen's request, before touching anything.

Context: the engine currently books **zero** working-capital investment in every
explicit year and in the terminal. This document sets out what the balance sheet
actually says, which lines belong in the measure, what the alternatives imply, and
where the honest uncertainty sits.

---

## 1. What the engine does today

`build_engine_inputs_from_data` returns `delta_wc = [0.0] × 5` and
`delta_wc_stub = 0.0`, so `fcf_engine.py:354` books nothing. DNL's revenue compounds
at 6.15% a year in Muddle Through, from AUD 3,609m in Y1 to AUD 4,583m in Y5 — a 27%
increase over the horizon, funded by no incremental investment in receivables or
inventory. The terminal likewise grows at 2.5% in perpetuity with no working-capital
drag.

The engine matches the audited workbook exactly, so this is a *workbook* assumption,
not an engine bug. Changing it retires the current 3.073 tie.

## 2. What the balance sheet says

From `data/financials/dnl.yaml`, balance sheet at **30 September 2025** (AUD m):

| Line | Value | In the measure? |
|---|---|---|
| Net receivables | 840.5 | **Yes** |
| Inventory | 519.1 | **Yes** |
| Accounts payable | 733.7 | **Yes** (negative) |
| Other current assets | 115.9 | No |
| Other current liabilities | 231.3 | No |
| Cash and short-term investments | 647.2 | No |
| Short-term debt | 626.3 | No |

**Trade working capital = 840.5 + 519.1 − 733.7 = AUD 625.9m.**

### Why those inclusions and exclusions

1. **Receivables, inventory and payables** are the three lines that scale mechanically
   with trading volume. They are the operating working capital a growing manufacturer
   must fund. This is the standard definition and the one CSL's own
   `working_capital_change_pct_revenue_change` uses.
2. **Cash and short-term debt are excluded** because they are financing items, already
   captured in the net-debt bridge. Including them would double-count.
3. **"Other current assets" and "other current liabilities" are excluded** because
   they are not disclosed at a level that lets us see what is in them. For an
   industrial they typically hold current tax, provisions, accruals and prepayments —
   items that either do not scale with revenue or are already in the tax and EBIT
   lines. Including them would move the measure to
   (115.9 − 231.3) = −115.4m, i.e. a *reduction* of 3.1pp in intensity. I have left
   them out because I cannot justify what is in them, not because I know they do not
   belong. **This is the single largest judgement in the derivation.**

## 3. The intensity, and why the denominator matters

Working-capital intensity = trade WC ÷ revenue. Three defensible denominators exist
in the register and they do not agree:

| Denominator | Revenue | Intensity |
|---|---|---|
| FY25 statutory (year to 30 Sep 2025) | 3,710.1 | **16.87%** |
| TTM to 31 Mar 2026 | 3,905.4 | 16.03% |
| Engine base-year revenue | 3,400.0 | 18.41% |

**I would use 16.87%.** It is the only pairing where the balance sheet and the revenue
cover the same period — a stock measured at 30 Sep 2025 against the flow of the year
ending 30 Sep 2025. The TTM figure is cleaner as a *trading* baseline (the register
itself calls it "the first full 12 months post-demerger") but it runs to 31 March 2026,
six months past the balance-sheet date, so pairing them mismatches the periods. The
engine base-year of 3,400 is a normalised figure, not a reported one.

The spread across the three is 16.0% to 18.4%, so the denominator choice is worth
about ±1.2pp of intensity — small relative to the decision being made (0% versus
roughly 17%).

## 4. Why constant intensity is the right assumption — and when it isn't

The proposal is that incremental working capital equals the intensity multiplied by
the *change* in revenue: ΔWC = 16.87% × ΔRevenue. This is the constant-intensity
assumption, and it is the default for a reason:

1. Receivables scale with sales at constant payment terms; inventory scales with
   volume at constant turns; payables scale with purchases at constant terms. Absent
   a reason for any of those three to change, the ratio holds.
2. It is what the engine already does for CSL
   (`working_capital_change_pct_revenue_change: 0.10`), so adopting it for DNL makes
   the two companies methodologically comparable rather than differently silent.

It would be wrong if DNL were expected to *improve* working-capital efficiency — a
deliberate inventory reduction, tighter collection, extended supplier terms. Nothing
in `dnl.yaml` claims any such programme. If you believe one exists, the honest
treatment is a declining intensity path with a stated reason, not zero.

**The current assumption of zero is not a conservative version of this. It is the
claim that DNL can grow revenue 27% over five years while funding no incremental
receivables or inventory at all** — which is only true if the business is shrinking
its working capital by exactly the amount growth requires, every year, forever.

## 5. The evidence is thinner than I would like

1. **One real observation.** FY25 is the only reported balance sheet in the register.
   FY21–FY24 in `build_cfgs.py` are explicitly labelled mock placeholders pending
   Ben's EODHD export, so there is no trend to test whether 16.87% is representative
   or a point-in-time distortion.
2. **FY25 is a transition year.** The demerger completed March 2025 and the register
   notes EBIT is shaped by roughly AUD 200m of significant items. Those are P&L
   effects rather than balance-sheet ones, so the working-capital lines should be
   less affected — but a balance sheet six months after a demerger may still carry
   separation artefacts.
3. **The cash flow statement is not usable as a cross-check.** FY25 operating cash
   flow of 574.7 against net income 145.5 plus D&A 284.1 implies roughly +145m from
   working capital and other items — a release, not a build. But that year contains
   demerger flows, so it cannot separate a genuine working-capital release from
   separation mechanics.

**Recommendation on the evidence:** proceed with 16.87%, and flag in the decision
record that it rests on a single post-demerger observation and should be re-tested
when Ben's feed provides FY21–FY24 actuals. That is a better position than zero,
which rests on nothing.

## 6. What each choice is worth

Muddle Through, with terminal capex also set equal to D&A (the two changes are
naturally taken together — both are reinvestment-consistency fixes):

| Assumption | Value per share | vs market (3.61) | Change |
|---|---|---|---|
| Current: 0% WC, terminal capex 7.0% | **3.073** | −14.9% | — |
| Terminal capex = D&A only | 2.994 | −17.1% | −2.6% |
| + WC at 10% of Δrevenue (CSL parity) | 2.722 | −24.6% | −11.4% |
| + WC at 16.87% (data-derived) | **2.535** | **−29.8%** | **−17.5%** |

Across all six scenarios at 16.87% + terminal capex = D&A:

| Scenario | Current | Revised | Change |
|---|---|---|---|
| Orderly Convergence | 3.5619 | 2.8863 | −19.0% |
| Muddle Through | 3.0730 | 2.5351 | −17.5% |
| AI Productivity Lag | 2.9850 | 2.5200 | −15.6% |
| Fragmentation | 2.2224 | 1.7022 | −23.4% |
| Disorderly Climate | 1.1768 | 1.3702 | **+16.4%** |
| Stagflation Persists | 1.0194 | 0.5586 | −45.2% |

Two consequences worth understanding before deciding:

1. **Asymmetry widens from 4.05× to 5.6×.** The downside worlds fall further than the
   upside because working capital is a fixed claim on growth regardless of margin —
   in Stagflation, where the EBIT margin is 7.1%, the working-capital build consumes
   a far larger share of a thin cash flow. Arguably this is the *more* honest picture
   of DNL's operating leverage, but it is a material change to the framework's
   headline claim about the company.
2. **Disorderly Climate rises 16.4%, against the trend.** Because capex assumptions
   are scenario-specific, that world currently runs terminal capex *above* D&A, so
   normalising it releases value. The review characterised the terminal-capex wedge as
   uniformly flattering; it is not — it cuts both ways depending on the scenario.

## 7. What changing this actually costs

1. The audited Muddle Through workbook
   (`analyses/dnl/valuations/`) must be rebuilt with the working-capital rows added
   and re-tied, because the 3.073 oracle retires with the change.
2. The 18 scenario goldens pinned in Batch 1 all move and must be consciously
   re-pinned — which is precisely the change-detection they were built for.
3. `dnl.yaml` needs a `working_capital_change_pct_revenue_change` entry with its
   rationale, mirroring the CSL block.
4. The comparison workbook's driver ties (`test_dnl_all_scenarios.py`) are unaffected
   — they pin revenue growth, Y5 margin and terminal growth, none of which move.
5. Every DNL narrative claim citing "15% below market" needs restating at roughly 30%.

Estimated effort: half a day including the workbook rebuild and re-tie.

## 8. Recommendation

**Adopt 16.87%, and set terminal capex equal to D&A at the same time**, with the
evidence limitation in section 5 written into the decision record.

The reason is not that the new number is better. It is that the current number is a
claim nobody has made deliberately: zero working capital was almost certainly a
simplification carried forward from an early build rather than a considered view, and
it is not conservative — it inflates the valuation by 17.5%. A framework whose stated
purpose is traceability should not have its second-largest DNL assumption be an
unstated one.

If the −30% discount to market feels too strong to publish, that is a signal worth
attending to rather than a reason to keep zero. It would mean either the revenue
growth or the margin glide is carrying more optimism than the reinvestment side can
support — which is exactly the kind of internal inconsistency the §11.4.2 sensitivity
discipline exists to surface.

**Fallback if you want to move in one step rather than two:** take terminal capex = D&A
now (−2.6%, small workbook change) and hold working capital until Ben's feed provides
FY21–FY24 balance sheets to test the 16.87%. That is defensible sequencing. It is not
defensible to leave both indefinitely.
